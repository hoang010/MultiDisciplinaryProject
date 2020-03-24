#include "SharpIR.h"

uint8_t SharpIR::getDistance( bool avoidBurstRead )
  {
    uint8_t distance ;

    if( !avoidBurstRead ) while( millis() <= lastTime + 20 ) {} //wait for sensor's sampling time

    lastTime = millis();

    switch( sensorType )
    {
      case GP2Y0A21YK0F_rightHug :
        distance = 112070* pow(analogRead(pin),-1.599);

        if(distance > 80) return 81;
        //else if(distance < 10) return 9;
        else return distance;

        break;
      
      case GP2Y0A21YK0F :
        distance = 21950* pow(analogRead(pin),-1.244);

        if(distance > 80) return 81;
        else if(distance < 10) return 9;
        else return distance;

        break;
      case GP2Y0A21YK0F_centerFront :
        distance = 21950* pow(analogRead(pin),-1.244);

        if(distance > 37) return 81;
        else if(distance > 34 ) return 40;
        else return distance;

        break;
      case GP2Y0A21YK0F_rightFront :
        distance = 60606*pow(analogRead(pin),-1.46);
        //distance = 680255 * pow(analogRead(pin),-1.903);

        if(distance > 80) return 81;
        //else if(distance < 10) return 9;
        else return distance;

        break;

      case GP2Y0A21YK0F_frontRight :
        //distance = 21186* pow(analogRead(pin),-1.254);
        distance = 9981.7* pow(analogRead(pin),-1.13);


        if(distance > 39) return 81;
        else return distance;

        break;
      case GP2Y0A21YK0F_frontLeft :
        distance = 21186* pow(analogRead(pin),-1.254);


        if(distance > 45) return 81;
        //else if(distance < 10) return 9;
        else return distance;

        break;
      case GP2Y0A02YK0F :
        distance = 42822*pow(analogRead(pin),-1.204);
        //distance = 28875* pow(analogRead(pin),-1.139);

        if(distance > 85) return 151;
        else if(distance < 20) return 19;
        else return distance;
    }
  }
