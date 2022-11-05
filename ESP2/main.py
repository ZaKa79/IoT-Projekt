from imu import MPU6050
from time import sleep
from machine import Pin, I2C
import tm1637

i2c = I2C(0, sda = Pin(21), scl = Pin(22), freq = 400000)
imu = MPU6050(i2c)
tm = tm1637.TM1637(clk=Pin(2), dio=Pin(0))

tackling = 0
status = False
tm.write([0x00, 0x00, 0x00, 0x00])

while True:
    acceleration = imu.accel
    print ("Acceleration x: ", round(acceleration.x,2), " y:", round(acceleration.y,2),
           "z: ", round(acceleration.z,2))
    sleep(0.4)
    tm.show(str(tackling))
    
    if acceleration.y < 0.1 and status == False:
        tackling = tackling + 1
        status = True
        print(tackling)
        
    elif acceleration.y > 0.1 and status == True:
        status = False
    sleep(0.4)
        
     