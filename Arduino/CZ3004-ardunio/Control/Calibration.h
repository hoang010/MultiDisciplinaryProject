#ifndef Calibration_h
#define Calibration_h

#include "Sensors.h"

/* Class to control all calibration related functionalities of the bot*/
class Calibration {
  private :
    float calibrationSetSpeed1;
    float calibrationSetSpeed2;
    DualVNH5019MotorShield md;
    void CalibrateSpin(SharpIR sensor1, SharpIR sensor2, long difference);
    void CalibrateDistance(SharpIR sensor1, long offset1, SharpIR sensor2,  long offset2, long difference);
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

void Calibration::CalibrateSpin(SharpIR sensor1, SharpIR sensor2, long difference) {
  float leftDistance = sensor1.getDistance(false) + 0;
  float rightDistance = sensor2.getDistance(false) + 0;
  while (fabs(rightDistance - leftDistance) != difference) {
    if (rightDistance - leftDistance > difference) {
      md.setSpeeds(calibrationSetSpeed1, -calibrationSetSpeed1);
      delay(10);
      md.setM1Brake(400);
      md.setM2Brake(400);
      delay(15);
    }
    if (rightDistance - leftDistance < difference) {
      md.setSpeeds(-calibrationSetSpeed1, calibrationSetSpeed2);
      delay(10);
      md.setM2Brake(400);
      md.setM1Brake(400);
      delay(15);
    }
    leftDistance = sensor1.getDistance(false) + 0;
    rightDistance = sensor2.getDistance(false) + 0;
  }
}


void Calibration::CalibrateDistance(SharpIR sensor1, long offset1, SharpIR sensor2,  long offset2, long difference) {

  float leftDistance = sensor1.getDistance(false) + 0;
  float rightDistance = sensor2.getDistance(false) + 0;

  if (fabs(rightDistance - leftDistance) != difference) {
    CalibrateSpin(sensor1, sensor2, difference);
  }

  leftDistance = sensor1.getDistance(false) + 0;
  rightDistance = sensor2.getDistance(false) + 0;

  float setM1, setM2;

  do {

    if (leftDistance < offset1)
      setM2 = -calibrationSetSpeed2;
    else if (leftDistance > offset1)
      setM2 = calibrationSetSpeed2;
    else
      setM2 = 0;

    if (rightDistance < offset2)
      setM1 = -calibrationSetSpeed1;
    else if (rightDistance > offset2)
      setM1 = calibrationSetSpeed1;
    else
      setM1 = 0;

    md.setSpeeds(setM1, setM2);
    delay(10);
    md.setM2Brake(400);
    md.setM1Brake(400);
    delay(15);

    leftDistance = sensor1.getDistance(false) + 0;
    rightDistance = sensor2.getDistance(false) + 0;

    Serial.print(rightDistance );
    Serial.print(" | ");
    Serial.println(leftDistance);

  }  while (!(rightDistance == offset2 && leftDistance == offset1));
}

void Calibration::CalibrateFront() {
  CalibrateDistance(SR1, 0, SR2, 1, 0);
}

void Calibration::CalibrateRight() {
  CalibrateSpin(SR3, SR4, 0);
}

void Calibration::CalibrateStep() {
  float frontLeftDistance = SR1.getDistance(false) + 0;
  float frontMiddleDistance = SR2.getDistance(false) + 1;
  float frontRightDistance = SR6.getDistance(false) + 0;

  if ( frontLeftDistance >= 11 && frontLeftDistance <= 14 && frontMiddleDistance >= 17 && frontMiddleDistance <= 21)
    CalibrateDistance( SR2, 12, SR6,  19, 7);
  else if (frontRightDistance >= 11 && frontRightDistance <= 14 && frontMiddleDistance >= 17 && frontMiddleDistance <= 21)
    CalibrateDistance(SR6, 19, SR1,  12, 7);
}

#endif
