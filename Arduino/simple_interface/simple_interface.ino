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
  Serial.println("Going straight...");
  while(Serial.available() == 0){
    int spd = 200;
    md.setM1Speed(spd);
    md.setM2Speed(-spd);
    }
  }

void turnLeft(){
  Serial.println("Turning Left...");
  int spd = 200;
  md.setM1Speed(spd);
  md.setM2Speed(spd);
  delay(1000);
  }


void turnRight(){
  Serial.println("Turning Right...");
  int spd = 200;
  md.setM1Speed(-spd);
  md.setM2Speed(-spd);
  delay(1000);
  }

void stopRobot(){
  md.setM1Speed(0);
  md.setM2Speed(0);
  }
String result;
void reportSensors(){
  result = "";
  int val = analogRead(analogPin);
  result += String("{") + "right front:"+ val;
  val = analogRead(analogPin2);
  result += String("; left front:") + val;
  val = analogRead(analogPin3);
  result += String("; right side:") + val;
  val = analogRead(analogPin4);
  result += String("; left side:")+ val + "}"; 
  Serial.println(result);
  }

void setup() {
  Serial.begin(9600); 
  Serial.println("Welcome Pi! Alduino here!");
  md.init();
}

void loop() {
  static String cmd = "";
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
    default:
      stopRobot();
      reportSensors();
      break;
    }
  cmd = "";
}
