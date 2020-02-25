#include "DualVNH5019MotorShield.h"
#include "math.h"
#include "Sensors.h"
#include "Movements.h"
//#include "Calibration.h"

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
#define initialSetSpeed1 210
#define initialSetSpeed2 210
#define calibrationSetSpeed1 315
#define calibrationSetSpeed2 350

String sensorData;

Motion* bot;  // Motion object to control bot movements such as "Move Forward", "Turn Right", etc.
//Calibration* calibrateBot; // Calibration object to control calibration techniques such as "Calibrate with Front sensors", "Calibrate with Left sensors", etc.


void setup() {
  Serial.begin(115200);

  pinMode(E1A, INPUT);
  pinMode(E1B, INPUT);
  pinMode(E2A, INPUT);
  pinMode(E2B, INPUT);

  md.init();                                                                            //Initialisation of motor shield
  bot = new Motion(targetRPM, initialSetSpeed1, E1B, initialSetSpeed2, E2A, md);        //Construction of Motion object
  //calibrateBot = new Calibration(calibrationSetSpeed1, calibrationSetSpeed2, md);       //Construction of Calibration object
  //Serial.println("Hi. I am Ardunio!");
}


void loop() {
  
  int secondVal = 10; // Offset of 10 to let bot travel by 10 cm in forward and backward movement by default
  delay(2000);
  controlBot(3,120);
  if (Serial.available())
  {
    int instructions = Serial.parseInt();       //Integer parsing is more efficient and has a faster response time than string reading i.e Serial.read(), Serial.readStringUntil(), etc.
    controlBot(instructions, secondVal);
  }
  delay(2000);
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

void controlBot (int instruction, int secondVal) {  

  switch (instruction) {
    case 1:  // Check If arduino is responding 
      Serial.println("X_BOTREADY");
      break;
    case 2:  // Return Sensor data
      sensorData = returnSensorData(12);
      Serial.println("X_SENDDATA: " + sensorData);
      break;
    case 3:  // Move Forward
      bot->moveForward(secondVal);
      Serial.println("X_BOTDONE");
      break;
    case 4:  // Turn Left
      bot->turnLeft(360);
      Serial.println("X_BOTDONE");
      break;
    case 5:  // Turn Right
      bot->turnRight(90);
      Serial.println("X_BOTDONE");
      break;
    case 6:  // Move Backward
      bot->moveBackward(secondVal);
      Serial.println("X_BOTDONE");
      break;
    case 7:  // Turn left 180 degrees
      bot->turnLeft(180);
      Serial.println("X_BOTDONE");
      break;
    case 8:  // Turn right 180 degrees
      bot->turnRight(180);
      Serial.println("X_BOTDONE");
      break;
    case 9:  // Unbreak wheels
      md.setM1Speed(0);
      md.setM2Speed(0);
      Serial.println("X_BOTDONE");
      break;
  }
}
