# Repo for Group 17 MDP Project
The project is to be done and submitted to 
Nanyang Technological University, School of Computer Science 
and Engineering for the assessing of the module 
CZ3004, Multi-Disciplinary Project.

## Objective
The objective of this project is to build and program a robot to
do the following:
* Autonomously explore an unknown fixed size area of 15x20 grids,
each grid having a size of 10cm x 10cm
* While exploring
    * Send the updated map to the connected tablet
    * Find and recognise images on any found obstacles
    * Stream live feed from camera to PC
* Once the robot completes exploring and returns a completed map
    * The robot is to find a shortest path to a goal
    * Move to the goal using the found shortest path
* Manually control the robot when desired

## Checklist
This section is for tracking requirements for the various teams.

##### Android
* [ ] Transmit and receive text strings over Bluetooth
* [ ] Functional GUI to initiate exploration
* [ ] Functional GUI to provide interactive control of robot
* [ ] Functional GUI to indicate current status of robot
* [ ] Functional GUI to select fastest path and robot start 
co-ordinates
* [ ] 2D display of maze environment
* [ ] Functional GUI that provides selection of Manual or Auto 
updating of graphical display of maze environment
* [ ] Functional GUI that provides 2 buttons that supports
persistent user reconfigurable stirng commands to robot
* [ ] Robust connectivity with Pi through Bluetooth
* [ ] Display Number ID blocks in the Grid Map
* [ ] (Extension) Novel robot movement control
* [ ] (Extension) Provide button-activated toggle between 2D grid map and 3D
first person view 
* [ ] (Extension) 2.5D view of current known map and robot
* [ ] Testing code

##### Algorithms
* [ ] Detect and recognise images
* [x] Obstacle avoidance and position recovery (straight line)
* [ ] Arena exploration simulator
* [ ] Fastest path computation simulator
* [x] Generate map descriptor
* [ ] Time and coverage-limited exploration simulation
* [ ] (Extension) Obstacle avoidance and position recovery (obstacle)
* [ ] (Extension) Generate and display map on PC
* [ ] Testing code

##### Raspberry Pi
* [x] Accessed by PC through Wifi
* [x] Accessed by Tablet through Bluetooth
* [x] Communicate with Arduino through USB Serial
* [x] Pass information among devices (Tablet to send character to
Arduino, Arduino to increase by 1, send back to Pi, send to PC and 
display)
* [ ] Testing code

##### Arduino
* [ ] Sensors calibrated to correctly return distance to obstacle
(Error tolerance: -6% to 6% of target distance)
* [ ] Accurate straight line motion
* [ ] Accurate rotation
* [ ] Testing code

## Pre-requisite
The repository requires (but is not limited to) the 
following libraries to execute on a Linux, Windows and Darwin 
environment:
* Python 3
* Numpy
* Matplotlib
* PyBluez 0.23
* OpenCV 4.2.0
* PySerial 3.4

## Installing

PlBluez requires additional dependencies to install. Get it from 
`https://visualstudio.microsoft.com/visual-cpp-build-tools/`

Execute the following command to install the libraries\
`pip3 install -r requirements.txt`

## Data Standards
The following table shows the type of data sent/received in 
each connection.

| Connection Type | Data Type |
| :---: | :---: |
| Bluetooth | Arrays |
| Wifi | Arrays | 
| Serial | Strings | 

## System architecture
A simplified system architecture diagram is as follows:

![](config/Images/System%20Architecture.png)

The Raspberry Pi uses a total of 5 Sockets:
1. Bluetooth socket
2. Serial "Socket"
3. Wifi Socket x 3

### Bluetooth Socket
The bluetooth socket is used for connecting with the tablet. It 
uses RFCOMM protocol for connection. The socket binds a MAC 
address before listening to devices for connection. 

Upon successful connection, Raspberry Pi creates 2 queues and 
2 threads. 1 queue to handle data receiving, 1 queue to handle 
data sending and 1 thread for each queue. As mentioned in the 
Data Standards table, this connection uses Arrays to 
send/receive data.

### Serial Connection
The Serial class is used for interfacing with the Arduino board.
Raspberry Pi creates an instance of Serial object using the name 
of the port connected to the Arduino board. Like the Bluetooth 
socket, the Serial Connection creates 2 queues and 2 threads; 1
 queue for sending, 1 queue for receiving and 1 thread for each 
 queue. This method of implementation is done as Serial.read()
 is a blocking function.

For the recv function, it checks the buffer size for the size 
of the data in there before reading all the data in the buffer 
and returns it to the function calling recv. 

For the send function, the msg to be sent is directly written
to the Serial Connection. As mentioned in the Data Standards table,
 this connection uses String to send/receive data.

### Wifi Socket
The Wifi Socket is used to connect to the PC. It starts a queue 
and thread for each instantiation of the Server class. This way
of implementing was done as there were concerns regarding latency.
As mentioned in the Data Standards table, this connection uses 
Arrays to send/receive data.

For the first Wifi Socket instantiation, it binds the port 7777 to
a socket before listening for requests to connect on this port. 
This connection would then be used for sending data to the PC.

For the second Wifi Socket instantiation, it binds the port 8888 to
a socket before listening for requests to connect on this port. 
This connection would then be used for receiving data from the PC.

For the last Wifi Socket instantiation, it binds the port 9999 to
a socket before listening for requests to connect on this port. 
This connection would then be used for sending stream data from
 the Pi Camera to the PC.

## To Run
Execute the command `python3 main.py` to start.

## Contributors
The project is done by the following teams:

##### Android
* Wong Chun Foong
* Goh Yong Wei
##### Algorithms
* Satya Gupta
* Wong Chun Foong
* Sin Chong Wen Bryan
##### Raspberry Pi
* Cao Shiqi
* Neo Kian Hao
* Sin Chong Wen Bryan
##### Arduino
* Pereddy Vijai Krishna Reddy
* Nguyen Le Hoang

## References
* [Comparing 2 images](https://www.pyimagesearch.com/2014/09/15/python-compare-two-images/)
