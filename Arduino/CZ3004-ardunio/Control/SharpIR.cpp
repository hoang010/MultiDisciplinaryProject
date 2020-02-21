#include "SharpIR.h"

uint8_t SharpIR::getDistance( bool avoidBurstRead )
  {
    uint8_t distance ;

    if( !avoidBurstRead ) while( millis() <= lastTime + 20 ) {} //wait for sensor's sampling time

    lastTime = millis();

    switch( sensorType )
    {
      case GP2Y0A21YK0F :

        distance = 4800/(analogRead(pin)-20);

        if(distance > 80) return 81;
        else if(distance < 10) return 9;
        else return distance;

        break;

      case GP2Y0A02YK0F :
      
        distance = 28875* pow(analogRead(pin),-1.139);

        if(distance > 150) return 151;
        else if(distance < 20) return 19;
        else return distance;
    }
  }
