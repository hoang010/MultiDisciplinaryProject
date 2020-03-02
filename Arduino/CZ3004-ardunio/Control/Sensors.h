#ifndef Sensor_h
#define Sensor_h

#include "SharpIR.h"
#include "ArduinoSort.h"

//Initial Sensor declaration
SharpIR SR1(SharpIR::GP2Y0A21YK0F, A0); //front right
SharpIR SR2(SharpIR::GP2Y0A21YK0F, A1); //front left
SharpIR SR3(SharpIR::GP2Y0A21YK0F, A2); //looking right, front
SharpIR SR4(SharpIR::GP2Y0A21YK0F, A3); //looking right, back
SharpIR LR5(SharpIR::GP2Y0A02YK0F, A4); //looking right
SharpIR SR6(SharpIR::GP2Y0A21YK0F, A5); //looking right, back

class Sensor {
  private:
    void printArray(String msg, int* arraySR1);
  public:
    float returnLrDist (int count, SharpIR sensor) ;
    float returnSrDist (int count, SharpIR sensor);
    String returnSensorData(int count);
};

float returnSrDist (int count, SharpIR sensor, int offset) {
  int arraySR[count];

  for (int i = 0; i < count; i++) {
    arraySR[i] = sensor.getDistance(false) + offset;
  }
  //getting median values
  sortArray(arraySR, count);

  float final = arraySR[count / 2];
  return final;
}

float returnLrDist (int count, SharpIR sensor, int offset) {
  int arrayLR[count];

  for (int i = 0; i < count; i++) {
    arrayLR[i] = sensor.getDistance(false)+ offset; //When it comes to LR sensor, add a +10 due to unknown offset
  }
  
  sortArray(arrayLR, count);

  float final = round(arrayLR[count / 2]);
  return final;
}

bool avoidObstacles(int count){
    float SR1_distance = returnSrDist(count, SR1, -5);
    float SR2_distance = returnSrDist(count, SR2, -5);
    float SR6_distance = returnSrDist(count, SR6, -5);
    
    if (SR1_distance <= 25 and SR1_distance >= 15){
      return true;
      }
    if (SR2_distance <= 25 and SR2_distance >= 15){
      return true;
      }
    if (SR6_distance <= 25 and SR6_distance >= 15){
      return true;
      }
    return false;
  }

String returnSensorData(int count) {

  float SR1_distance = returnSrDist(count, SR1, -5);
  float SR2_distance = returnSrDist(count, SR2, -5);
  float SR3_distance = returnSrDist(count, SR3, -3);
  float SR4_distance = returnSrDist(count, SR4, -4);
  float LR5_distance = returnLrDist(count, LR5, -17);
  float SR6_distance = returnSrDist(count, SR6, -8);

  return "{FrontRight:" + String(SR1_distance) + "; FrontLeft:" + String(SR2_distance) + "; FrontCenter:" + String(SR6_distance)+ "; RightFront:" + String(SR3_distance) + "; RightBack:" + String(SR4_distance) + "; LeftSide:" + String(LR5_distance)+'}';
}
#endif
