#include "DualVNH5019MotorShield.h"
#include "math.h"
#include "Sensors.h"
#include "Movements.h"
#include "Calibration.h"
/* Object to control motor shield and in turn control the motors, additionaly information found at https://github.com/pololu/dual-vnh5019-motor-shield */
DualVNH5019MotorShield md;

/* Definition of A & B lines of Encoder 1 (right) and Encoder 2 (left) */
#define E2A  11
#define E2B  13
#define E1A  3
#define E1B  5

/*Definition of target or required RPM by motors, calibration speed and starting set Speed
  ~ Staring set Speed is set to a mid range value below 80 rpm in order to not allow the PID
  controlled to start from 0 rpm which tend to cause a delay in response time*/
#define targetRPM 80
#define initialSetSpeed1 170 // left
#define initialSetSpeed2 305
#define calibrationSetSpeed1 300
#define calibrationSetSpeed2 340

String sensorData;

Motion* bot;  // Motion object to control bot movements such as "Move Forward", "Turn Right", etc.
Calibration* calibrateBot; // Calibration object to control calibration techniques such as "Calibrate with Front sensors", "Calibrate with Left sensors", etc.



void setup() {
  Serial.begin(115200);

  pinMode(E1A, INPUT);
  pinMode(E1B, INPUT);
  pinMode(E2A, INPUT);
  pinMode(E2B, INPUT);

  md.init();                                                                            //Initialisation of motor shield
  bot = new Motion(targetRPM, initialSetSpeed1, E1B, initialSetSpeed2, E2A, md);        //Construction of Motion object
  calibrateBot = new Calibration(calibrationSetSpeed1, calibrationSetSpeed2, md);       //Construction of Calibration object
  //Serial.println("Hi. I am Ardunio!");
}


void loop() {
  delay(2);
  int gridMoveValueInt;
  String gridMoveValueString;
  int dummy;
  while (Serial.available() > 0) {

    dummy = Serial.peek();
    if (dummy > 90 || dummy < 49)
    {
      dummy = Serial.read();
      continue;
    }

    gridMoveValueString = "";
    char character = Serial.read();

    if (character == '|')
      continue;
    if (character == '\0' || character == '\n')
      break;
    char nextChar = Serial.read();
    gridMoveValueString += nextChar;
    gridMoveValueInt = gridMoveValueString.toInt();
    if (gridMoveValueInt == 0){
      gridMoveValueInt = 1;
      }

    controlBot(character, gridMoveValueInt, 1);
  }
}

//Fastest path format ends with }
//i.e: {3:10, 4:90, 5:90}
String getFastestPath() {
  String fastestPath = "";
  Serial.read();
  while (fastestPath.equals("")) {
    fastestPath = Serial.readStringUntil('}');
  }
  //ignore the first "{"
  return fastestPath.substring(1);
}


void fastestPath(String fastest_path_code) {

  String instructions = "";
  String instruction = "";
  bool getInstruction = true;
  bool getValue = true;
  int value = 0;
  do {
    //for each character in the code
    for (int i = 0; i <= fastest_path_code.length(); i++) {
      //if the substring for the index is : or if it is the last character
      if (fastest_path_code.substring(i, i + 1) == "," || fastest_path_code.length() == i) {
        instructions = fastest_path_code.substring(0, i);
        for (int j = 0; j <= instructions.length(); j++) {
          if (instructions.substring(j, j + 1) == ":" || instructions.length() == j) {
            instruction = instructions.substring(0, j);
            value = instructions.substring(j + 1).toInt();
            break;
          }
        }
        fastest_path_code =  fastest_path_code.substring(i + 1);
        break;
      }
    }
    int str_len = instruction.length() +1;
    char char_arr[str_len];
    instruction.toCharArray(char_arr, str_len);
    controlBot(char_arr[0], value, 0);
    delay(200);
    //fastestPathCalibration();
    //delay(100);

  } while (!fastest_path_code.equals(""));

}

void fastestPathCalibration() {
  float frontRightDistance = SR1.getDistance(false);
  float frontLeftDistance = SR2.getDistance(false);
  float rightFrontDistance = SR3.getDistance(false);
  float rightBackDistance = SR4.getDistance(false);
  //if only front have object then calibrate front
  if ((frontRightDistance < 15 && frontRightDistance > 5) || (frontLeftDistance < 15 && frontLeftDistance > 5)) {
    calibrateBot->CalibrateFront();
    //if sides also have object then calibrate side as well
    if ((rightFrontDistance < 10 && rightFrontDistance > 5) || (rightBackDistance < 10 && rightBackDistance > 5)) {
      controlBot(5, 10, 0);
      delay(200);
      calibrateBot->CalibrateFront();
      delay(200);
      controlBot(4, 10, 0);
    }
  }
}



/* Function to control bot functions such as return sensor data, turn left, calibrate front, etc.
  The function additionally passes a message back to RPI via serial port when required action is complete
  In order to see bot functionalities simply use serial monitor to input bot functionalities
  1. Check If arduino is responding (redundant)
  2. Return Sensor data
  3. Move Forward
  4. Turn Left
  5. Turn Right
  6. Move Backward
  7. Turn Left 180
  8. Turn Right 180
  9. Stop bot (helps unlock wheels after using break)
  10. Turn left, Calibrate with Front sensors, and turn back to original position (left wall hugging)
  11. Calibrate with Front sensors
  12. Calibrate with Left sensors
  13. Calibrate using front sensors at a staircase
  14. Get ready to receive fastest path string */

void controlBot (char instruction, int secondVal, int returnSensor) {
  switch (instruction) {
    case 'C':  // Check If arduino is responding
      Serial.println("X_BOTREADY");
      break;
    case 'E':  // Return Sensor data
      sensorData = returnSensorData(12);
      Serial.println(sensorData + "\"Instruction\":\"" + instruction+"\"}" );
      break;
    case 'W':  // Move Forward
      bot->moveForward(secondVal * 10);
      if(returnSensor == 1){
        sensorData = returnSensorData(5);
        Serial.println(sensorData + "\"Instruction\":\"" + instruction+"\"}" );
        }

      break;
    case 'A':  // Turn Left by value
      bot->turnLeft(secondVal * 90);
      if(returnSensor == 1){
        sensorData = returnSensorData(5);
        Serial.println(sensorData + "\"Instruction\":\"" + instruction+"\"}" );
        }
      break;
    case 'D':  // Turn Right
      bot->turnRight(secondVal * 90);
      if(returnSensor == 1){
        sensorData = returnSensorData(5);
        Serial.println(sensorData + "\"Instruction\":\"" + instruction+"\"}" );
        }
      break;
    case 'S':  // Move Backward
      bot->moveBackward(secondVal * 10);
      if(returnSensor == 1){
        sensorData = returnSensorData(5);
        Serial.println(sensorData + "\"Instruction\":\"" + instruction+"\"}" );
        }
      break;
    case 'U':  // Unbreak wheels
      md.setM1Speed(0);
      md.setM2Speed(0);
      //Serial.println("X_BOTDONE");
      break;
    case 'F' :  // Calibrate with front sensors
      calibrateBot->CalibrateFront();
      Serial.println("X_CALIBRATIONDONE");
      break;
    case 'R' :  // Calibrate with right sensors
      bot->turnRight(90);
      delay(200);
      calibrateBot->CalibrateFront();
      delay(200);
      bot->turnLeft(90);
      calibrateBot->CalibrateRight();
      Serial.println("X_CALIBRATIONDONE");
      break;
    case 'N' :  // Calibrate for wall on the right and front
      calibrateBot->CalibrateFront();
      delay(200);
      bot->turnRight(90);
      delay(200);
      calibrateBot->CalibrateFront();
      delay(200);
      bot->turnLeft(90);
      delay(200);
      calibrateBot->CalibrateFront();
      delay(200);
      Serial.println("X_CALIBRATIONDONE");
      break;
    case 'I': // Init
      bot->turnLeft(90);
      delay(200);
      calibrateBot->CalibrateFront();
      delay(200);
      bot->turnLeft(90);
      delay(200);
      calibrateBot->CalibrateFront();
      delay(200);
      bot->turnLeft(90);
      calibrateBot->CalibrateRight();
      delay(200);
      break;
    case 'Q':  // Move Forward
      calibrateBot->CalibrateRight();
      delay(200);
      bot->moveForward(secondVal * 10);
      sensorData = returnSensorData(5);
      Serial.println(sensorData + "\"Instruction\":\"" + instruction+"\"}" );
      break;
    case 'K':  // Move Forward
      calibrateBot->CalibrateStep();
      Serial.println("X_CALIBRATIONDONE");
      break;
    case 'Z': //Get fastest path and run
      //Serial.println("X_READYFASTESTPATH");
      String fastest_path = getFastestPath();
      //String fastest_path = "3:30,5:11,3:10,5:14,3:30,5:14,3:10,5:14";
      fastestPath(fastest_path);
      //Serial.println("X_FASTESTPATHDONE");
      break;
  }
}
