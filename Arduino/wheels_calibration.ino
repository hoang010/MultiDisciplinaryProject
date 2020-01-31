#include "DualVNH5019MotorShield.h"

DualVNH5019MotorShield md;

//set up pin for the encoder
int E2B = 13;  
int E2A = 11;
int E1B = 5;
int E1A = 3;

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


float calculateRPM(int side)
{
  unsigned long period;
  float rpm;

  //calculate the period of the square wave
  //right side
  if(side == 0)
  {
    period = pulseIn(E2A, HIGH) *2; //return the time for the signal to go low high low (1 period);
  }
  //left side
  else
  {
    period = pulseIn(E1A, HIGH) *2; //return the time for the signal to go low high low (1 period);
  }
  //find time required to have 565.25 revolutions
  rpm = 60.0/(period * 565.25 /1000000);
  return period;
}

void setup()
{
  Serial.begin(115200);
  Serial.println("Dual VNH5019 Motor Shield");
  
  //set modes for the encoder pins
  pinMode(E2B, INPUT);  
  pinMode(E2A, INPUT);
  pinMode(E1B, INPUT);
  pinMode(E1A, INPUT);

  md.init();
}

double rpm_ave_l = 0;
double rpm_ave_r = 0;

void loop()
{
  //this is because once loop runs too high, the number reversed back to negative and ruined the calibration
  static long loop_count = 0;
  static int count = 0;
  //for left and right wheel

  double rpm_l;
  double rpm_r;
  //only enter every 1000 loop counts
  if(loop_count%1000 == 0){
    Serial.print("The current loop count is: ");
    Serial.println(loop_count);

    rpm_l = calculateRPM(1);
    rpm_r = calculateRPM(0);
    
    //until we have 10 counts of readings
    if(loop_count > 0 && count != 10)
    {
      Serial.println("Entered");
      rpm_ave_l= rpm_ave_l + rpm_l;
      rpm_ave_r= rpm_ave_r + rpm_r;
      Serial.println(rpm_l);
      Serial.println(rpm_r);
      count = count +1;
    }
    //start calculating average after 10 readings of rpm
    if (count == 10){
      Serial.print("The current rotation per minute(rpm) for left wheel is: ");
      Serial.println(rpm_ave_l/10);
          
      Serial.print("The current rotation per minute(rpm) for right wheel is: ");
      Serial.println(rpm_ave_r/10);
    }
    }
  else{
    md.setM1Speed(-254);
    md.setM2Speed(289);
    stopIfFault();
    }
  loop_count = loop_count + 1;
}
