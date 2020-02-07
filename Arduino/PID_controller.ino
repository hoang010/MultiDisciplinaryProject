#include "DualVNH5019MotorShield.h"

DualVNH5019MotorShield md;
long E2A = 3;
long E2B = 5;
long E1A = 11;
long E1B = 13;


#define M1k  ?
#define M1ts  ?
#define M1td  ?

#define M2k  ?
#define M2ts  ?
#define M2td  ?

float M1k1, M1k2, M1k3;
float M2k1, M2k2, M2k3;
float error1[3] = {0, 0, 0};
float error2[3] = {0, 0, 0};
float setSpeed1, setSpeed2, rpm = 50;

void stopIfFault()
{
  if (md.getM1Fault())
  {
    Serial.println("M1 fault");
    while (1);
  }
  if (md.getM2Fault())
  {
    Serial.println("M2 fault");
    while (1);
  }
}

void setup()
{
  Serial.begin(115200);
  Serial.println("Dual VNH5019 Motor Shield");
  pinMode(E1A, INPUT);
  pinMode(E1B, INPUT);
  pinMode(E2A, INPUT);
  pinMode(E2B, INPUT);
  PIDGearController1();
  PIDGearController2();

  Serial.print("Speed set(in rpm): ");
  Serial.println(rpm);

  setSpeed1 = 210;
  setSpeed2 = 220;

  md.init();

  md.setM1Speed(setSpeed1);
  md.setM2Speed(setSpeed2);
}


void loop() {

  Serial.print("Set Speed 1 : ");
  Serial.print(setSpeed1);
  Serial.print(" Set Speed 2 : ");
  Serial.println(setSpeed2);
  delay(20);
  float motorSpeed1 = getSpeed (pulseIn(E1B, HIGH));
  float motorSpeed2 = getSpeed (pulseIn(E2A, HIGH));

  Serial.print(millis());
  Serial.print(" |Motor Speed1(in rpm): ");
  Serial.print(motorSpeed1);
  Serial.print(" |Motor Speed2(in rpm): ");
  Serial.print(motorSpeed2);
  

  errorUpdate(error1);
  error1[0] = rpm - motorSpeed1 ;
  errorUpdate(error2);
  error2[0] = rpm - motorSpeed2 ;

  setSpeed1 = correctedSpeed(setSpeed1, error1[0], error1[1], error1[2], 1);
  setSpeed2 = correctedSpeed(setSpeed2, error2[0], error2[1], error2[2], 2);

  md.setM1Speed(setSpeed1);
  md.setM2Speed(setSpeed2);
  Serial.print("New Set Speed 1 : ");
  Serial.println(setSpeed1);
  Serial.println();
  Serial.print(", New Set Speed 2 : ");
  Serial.println(setSpeed2);
}

void errorUpdate(float error[]) {
  error[2] = error[1];
  error[1] = error[0];
}

float getSpeed (long pulseInTime) {
  long timePeriod = pulseInTime * 2;
  float rps = 1000000 / (timePeriod * 562.25);
  float rpm = rps * 60;
  return rpm;
}

void PIDGearController1() {

  Serial.print("M1k : ");
  Serial.print(M1k);
  Serial.print(" M1ts : ");
  Serial.print(M1ts);
  Serial.print(" M1td : ");
  Serial.println(M1td);

  float Kc =  (1.2 * M1ts) / (M1k * M1td);
  float Ti =  2 * M1td;
  float Td = 0.5 * M1td;

  float Kp =  Kc;
  float Ki = Kc / Ti;
  float Kd =  Kc * Td;

  Serial.print("Kp : ");
  Serial.print(Kp);
  Serial.print(" Ki : ");
  Serial.print(Ki);
  Serial.print(" Kd : ");
  Serial.println(Kd);

  M1k1 = Kp + Ki + Kd;
  M1k2 = -Kp - 2 * Kd;
  M1k3 = Kd;

  Serial.print("K1 : ");
  Serial.print(M1k1);
  Serial.print(" K2 : ");
  Serial.print(M1k2);
  Serial.print(" K3 : ");
  Serial.println(M1k3);
}

void PIDGearController2() {
  float Kc =  (1.2 * M2ts) / (M2k * M2td);
  float Ti = 2 * M2td;
  float Td = 0.5 * M2td;

  float Kp =  Kc;
  float Ki = Kc / Ti;
  float Kd =  Kc * Td;

  Serial.print("Kp : ");
  Serial.print(Kp);
  Serial.print(" Ki : ");
  Serial.print(Ki);
  Serial.print(" Kd : ");
  Serial.println(Kd);

  M2k1 = Kp + Ki + Kd;
  M2k2 = -Kp - 2 * Kd;
  M2k3 = Kd;

  Serial.print("K1 : ");
  Serial.print(M2k1);
  Serial.print(" K2 : ");
  Serial.print(M2k2);
  Serial.print(" K3 : ");
  Serial.println(M2k3);
}

float correctedSpeed(float originalSpeed, float error1, float error2, float error3, int motor) {
    Serial.print(" original Speed : ");
    Serial.print(originalSpeed);
    Serial.print(" Error 1 : ");
    Serial.print(error1);
    Serial.print(" Error 2 : ");
    Serial.print(error2);
    Serial.print(" Error 3 : ");
    Serial.print(error3);
  if (motor == 1) {
        Serial.print(" Additional Speed : ");
        Serial.println(error1 * M1k1 + error2 * M1k2 + error3 * M1k3);
    float newSpeed = originalSpeed + error1 * M1k1 + error2 * M1k2 + error3 * M1k3;
    return newSpeed;
  }
  else {
        Serial.print(" Additional Speed : ");
        Serial.println(error1 * M1k1 + error2 * M1k2 + error3 * M1k3);
    float newSpeed = originalSpeed + error1 * M2k1 + error2 * M2k2 + error3 * M2k3;
    return newSpeed;
  }
}
