#include <Arduino.h>

class SharpIR
{
  public:

    using sensorCode = const uint8_t ;

    SharpIR( sensorCode _sensorType , uint8_t _sensorPin ) : sensorType( _sensorType ) , pin( _sensorPin ) {}

    uint8_t getDistance( bool avoidBurstRead = true ) ;

    static sensorCode GP2Y0A41SK0F = 0 ;
    static sensorCode GP2Y0A21YK0F_rightFront = 1;
    static sensorCode GP2Y0A21YK0F = 2 ;
    static sensorCode GP2Y0A21YK0F_rightHug = 3;
    static sensorCode GP2Y0A02YK0F = 4;

  protected:

    uint8_t sensorType, pin ;

  private:

    uint32_t lastTime = 0 ;
};
