int analogPin = A0;  // right upper
int analogPin2 = A1; //left upper
int analogPin3 = A2; //right lower
int analogPin4 = A3; //left lower
int val = 0;
int temp = 0;
#include "DualVNH5019MotorShield.h"

DualVNH5019MotorShield md;

void stopIfFault()
{
  if (md.getM1Fault())
  {
    Serial.println("M1 fault");
    while(1);
  }
  if (md.getM2Fault())
  {
    Serial.println("M2 fault");
    while(1);
  }
}

void goStraight(){
  while(Serial.available() == 0){
    int spd = 200;
    md.setM1Speed(spd);
    md.setM2Speed(-spd);
    }
  }

void turnLeft(){
  int spd = 200;
  md.setM1Speed(spd);
  md.setM2Speed(spd);
  delay(10000);
  }


void turnRight(){
  int spd = 200;
  md.setM1Speed(-spd);
  md.setM2Speed(-spd);
  delay(10000);
  }

void stopRobot(){
  md.setM1Speed(0);
  md.setM2Speed(0);
  }
void setup() {
  Serial.begin(9600); 
  md.init();
}

void loop() {
  /*
  val = analogRead(analogPin);  // read the input pin
  Serial.println("Pin 1, right front");
  Serial.println(val); 
  val = analogRead(analogPin2);  // read the input pin
  Serial.println("Pin 2, left front");
  Serial.println(val); 
  val = analogRead(analogPin3);  // read the input pin
  Serial.println("Pin 3, right side");
  Serial.println(val); 
  val = analogRead(analogPin4);  // read the input pin
  Serial.println("Pin 4, left side");
  Serial.println(val); 
*/
  String cmd = "";
  int spd = 0;
  Serial.println("Hello this is ardunio uno!");
  if (Serial.available()>0){
    delay(2);
    char ch = Serial.read();
    cmd += ch;
    }

  switch (cmd.toInt()){
    case 1:
      goStraight();
      break;
    case 2:
      turnLeft();
      break;
    case 3:
      turnRight();
      break;
    case 0:
      stopRobot();
      break;
    }
  
  
  Serial.println("This is what i see: ");
  Serial.println(spd);
  delay(1000);
}
