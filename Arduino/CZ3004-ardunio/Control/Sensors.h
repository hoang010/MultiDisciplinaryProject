#ifndef Sensor_h
#define Sensor_h

#include "SharpIR.h"
#include "ArduinoSort.h"

//Initial Sensor declaration
SharpIR SR1(SharpIR::GP2Y0A21YK0F, A0); //top right
SharpIR SR2(SharpIR::GP2Y0A21YK0F, A1); //top left
SharpIR SR3(SharpIR::GP2Y0A21YK0F, A2); //below right looking right
SharpIR LR4(SharpIR::GP2Y0A02YK0F, A3); //top right side, looking left 
SharpIR LR5(SharpIR::GP2Y0A02YK0F, A5); //top right side, looking left 
//SharpIR SR5(SharpIR::GP2Y0A21YK0F, A4); //top center
//SharpIR SR5(SharpIR::GP2Y0A21YK0F, A0);

/*

*/
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

String returnSensorData(int count) {

  float SR1_distance = returnSrDist(count, SR1, 0);
  float SR2_distance = returnSrDist(count, SR2, -1);
  float SR3_distance = returnSrDist(count, SR3, 0);
  float LR4_distance = returnLrDist(count, LR4, 1);
  float LR5_distance = returnLrDist(count, LR5, -4);

  return "{TopRight:" + String(SR1_distance) + "; TopLeft:" + String(SR2_distance) + "; RightSide:" + String(SR3_distance) + "; LeftSide:" + String(LR4_distance) + "; TopCenter:" + String(LR5_distance)+'}';
}
#endif
