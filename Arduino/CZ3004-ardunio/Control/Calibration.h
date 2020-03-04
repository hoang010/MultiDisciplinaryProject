#ifndef Calibration_h
#define Calibration_h

#include "Sensors.h"

/* Class to control all calibration related functionalities of the bot*/
class Calibration {
  private :
    float calibrationSetSpeed1;
    float calibrationSetSpeed2;
    DualVNH5019MotorShield md;
    void CalibrateSpin(SharpIR sensor1, int sensorOffset1, SharpIR sensor2, int sensorOffset2, long difference);
    void CalibrateDistance(SharpIR sensor1, int sensorOffset1, long dist1, SharpIR sensor2,int sensorOffset2,  long dist2, long difference);
  public:
    Calibration(float _calibrateSetSpeed1, float _calibrationSetSpeed2, DualVNH5019MotorShield _md);
    void CalibrateFront();
    void CalibrateRight();
    void CalibrateStep();
};

/* Constructor for initialising class variables include motor control*/
Calibration::Calibration(float _calibrationSetSpeed1, float _calibrationSetSpeed2, DualVNH5019MotorShield _md) {
  calibrationSetSpeed1 = _calibrationSetSpeed1;
  calibrationSetSpeed2 = _calibrationSetSpeed2;
  md = _md;
}

/* Function to determine rotate the bot depending on required offsets. 
eg           sensor 1  |  sensor 2  |  Difference
    current     10     |     15     |      5
    required    12     |     12     |      0
bot will turn until reuired difference between sensor values are obtained. */

void Calibration::CalibrateSpin(SharpIR sensor1,int sensorOffset1, SharpIR sensor2,int sensorOffset2, long difference) {
  float rightDistance = sensor1.getDistance(false) + sensorOffset1;
  float leftDistance = sensor2.getDistance(false) + sensorOffset2;
  while (fabs(rightDistance - leftDistance) != difference) {
    Serial.print(rightDistance );
    Serial.print(" | ");
    Serial.println(leftDistance);
    if (rightDistance - leftDistance > difference) {
      md.setSpeeds(-calibrationSetSpeed1, calibrationSetSpeed2);
      delay(10);
      md.setM1Brake(400);
      md.setM2Brake(400);
      delay(15);
    }
    if (rightDistance - leftDistance < difference) {
      md.setSpeeds(calibrationSetSpeed1, -calibrationSetSpeed2);
      delay(10);
      md.setM2Brake(400);
      md.setM1Brake(400);
      delay(15);
    }
    rightDistance = sensor1.getDistance(false) + sensorOffset1;
    leftDistance = sensor2.getDistance(false) + sensorOffset2;
  }
}

/* Function to determine Forward movement the bot depending on required offsets. (Done after rotate Calibration)
eg           sensor 1  |  sensor 2  (front sensors)
    current     15     |     15     
    required    12     |     12     
bot will move forward until reuired sensor values are obtained. */

void Calibration::CalibrateDistance(SharpIR sensor1,int sensorOffset1, long dist1, SharpIR sensor2,int sensorOffset2,  long dist2, long difference) {
  //first calibrate the angle
  //take only 1 sample to improve timings
  float rightDistance = sensor1.getDistance(false) + sensorOffset1;
  float leftDistance = sensor2.getDistance(false) + sensorOffset2;
    Serial.print(rightDistance );
    Serial.print(" | ");
    Serial.println(leftDistance);
  if (fabs(rightDistance - leftDistance) != difference) {
    CalibrateSpin(sensor1, sensorOffset1, sensor2, sensorOffset2, difference);
  }

  rightDistance = sensor1.getDistance(false) + sensorOffset1;
  leftDistance = sensor2.getDistance(false) + sensorOffset2;
  
  //calibrate the distance
  float setM1, setM2;

  do {

    if (leftDistance < dist2)
      setM2 = -calibrationSetSpeed2;
    else if (leftDistance > dist2)
      setM2 = calibrationSetSpeed2;
    else
      setM2 = 0;

    if (rightDistance < dist1)
      setM1 = -calibrationSetSpeed1;
    else if (rightDistance > dist1)
      setM1 = calibrationSetSpeed1;
    else
      setM1 = 0;

    md.setSpeeds(setM1, setM2);
    delay(10);
    md.setM2Brake(400);
    md.setM1Brake(400);
    delay(15);

    rightDistance = sensor1.getDistance(false) + sensorOffset1;
    leftDistance = sensor2.getDistance(false) + sensorOffset2;

  }  while (!(rightDistance == dist1 && leftDistance == dist2));
}

/* Calibrate using front-right and front-left sensors to a distance of 12 from boundry 
and difference of 0 between both sensors */
void Calibration::CalibrateFront() {
  CalibrateDistance(SR1, 0, 14, SR2, 0, 14, 0);
  //SR1 is right
  //SR2 is left
}

/* Calibrate using left-front and left-back sensors until required offset between sensors is achieved*/
void Calibration::CalibrateRight() {
  CalibrateSpin(SR4, 0, SR3, 0, 0);
}

/* calibrate using front-middle and front-left  or front-middle and front-right sensors at maze steps
|_|_|_|                           |_|_|_|
|_|      left Stair | right Stair     |_|
{ bot }                           { bot }*/
/*
void Calibration::CalibrateStep() {
  float frontLeftDistance = SR1.getDistance(false) + 2;
  float frontMiddleDistance = SR2.getDistance(false) + 2;
  float frontRightDistance = SR3.getDistance(false) + 2;

  if ( frontLeftDistance >= 11 && frontLeftDistance <= 14 && frontMiddleDistance >= 17 && frontMiddleDistance <= 21)
    CalibrateDistance( SR1, 12, SR2,  19, 7);
  else if (frontRightDistance >= 11 && frontRightDistance <= 14 && frontMiddleDistance >= 17 && frontMiddleDistance <= 21)
    CalibrateDistance(SR2, 19, SR3,  12, 7);
}*/


//void calibrateRightSide() {
//  float distance[3] = {0, 0, 0};
//  distance[1] = LR1.getDistance(false) + 10;
//  md.setSpeeds(350, -350);
//  delay(25);
//  md.setBrakes(400);
//  delay(50);
//  float distance[0] = LR1.getDistance(false) + 10;
//  md.setSpeeds(350, -350);
//  delay(25);
//  md.setBrakes(400);
//  delay(50);
//  float distance[3] = LR1.getDistance(false) + 10;
//  while (fabs(frontSensor - backDistance) != 6) {
//    if (frontSensor - backDistance > 6) {
//      md.setSpeeds(350, -350);
//      delay(25);
//      md.setBrakes(400);
//      delay(50);
//    }
//    if (frontSensor - backDistance < 6) {
//      md.setSpeeds(-350, 350);
//      delay(25);
//      md.setM2Brake(400);
//      md.setM1Brake(400);
//      delay(50);
//    }
//    frontSensor = SR4.getDistance(false) + 2;
//    backDistance = SR5.getDistance(false) + 2;
//  }
//}

#endif