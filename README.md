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

## Pre-requisite
The repository requires (but is not limited to) the 
following libraries to execute on a Linux, Windows and Darwin 
environment:
* Python 3
* Numpy
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
| Bluetooth | Byte |
| Wifi | Byte | 
| Serial | Byte | 

## System architecture
A simplified system architecture diagram is as follows:

![](config/Images/System%20Architecture.png)

In the system architecture, the PC will be running the algorithms. 
The Raspberry Pi will be routing data to their respective destinations. 
Tablet will control the function to be run, whereas the Arduino connection 
will facilitate movement as dictated by PC. The Pi Camera input will only be
used for Image Recognition. 

## Raspberry Pi
The Raspberry Pi uses a total of 3 connections:
1. Bluetooth Connection
2. Serial Connection
3. Wifi Connection

### Bluetooth Connection
The bluetooth socket is used for connecting with the tablet. It 
uses RFCOMM protocol for connection. The socket binds a MAC 
address before listening to devices for connection. 

Upon successful connection, Raspberry Pi creates 2 queues and 
2 threads. 1 queue to handle data receiving, 1 queue to handle 
data sending and 1 thread for each queue. This method of implementation
 is done as Socket.recv() is a blocking function. As mentioned in the 
Data Standards table, this connection uses Bytes to 
send/receive data.

### Serial Connection
The Serial class is used for interfacing with the Arduino board.
Raspberry Pi creates an instance of Serial object using the name 
of the port connected to the Arduino board. Like the Bluetooth 
socket, the Serial Connection creates 2 queues and 2 threads; 1
 queue for sending, 1 queue for receiving and 1 thread for each 
 queue. This method of implementation is done as Serial.readline()
 is a blocking function.

For the recv function, it checks the buffer size for the size 
of the data in there before reading all the data in the buffer 
and returns it to the function calling recv. 

For the send function, the msg to be sent is directly written
to the Serial Connection. As mentioned in the Data Standards table,
 this connection uses Bytes to send/receive data.

#### Wifi Socket
The Wifi Socket is used to connect to the PC. It starts a queue 
and thread for each instantiation of the Server class. This way
of implementing was done as there were concerns regarding latency.
As mentioned in the Data Standards table, this connection uses 
Bytes to send/receive data.

The Wifi Socket instantiation binds the port 7777 to
a socket before listening for requests to connect on this port. 
This connection would then be used for sending data to the PC.

## Algorithm

### Exploration
For exploring the given arena, right wall hugging is used.

During exploration, the following packet structure is used for information 
sending between the entities.

##### From PC to Raspberry Pi:
```
{
    "dest": destination entity,
    "param": For arduino,
    "explored": For tablet,
    "obstacle": For tablet,
    "movement": For tablet,
    "direction": For tablet,
}
```

##### From Raspberry Pi to tablet:
```
 {
    "explored": contains hex of explored map,
    "obstacle": contains hex of real map,
    "movement": contains String of movement("l", "r", "f"),
    "direction": contains direction of robot,
}
```

##### From Raspberry Pi to Arduino: 
* movement in Bytes

The above packet structures are converted into string and then encoded into 
Bytes before being sent.

#### Conditions to turn right
One of the following conditions must be fulfilled:
* Coordinates on right side are within map and unexplored
* No obstacle on right (The variable check_right_empty is used as there is
a blind spot on the right side of the robot.)

Once the robot turns right, update the direction of the robot.

#### Conditions to turn left
The following conditions must be fulfilled:
* Obstacle/wall on right
* Obstacle in front

Once the robot turns left, get the coordinates of the front of the robot 
and add them to the list of obstacle coordinates if the obstacle is in 
front of the robot. Update the direction of the robot thereafter.

#### Conditions to advance
The following condition must be fulfilled:
* No obstacle in front and obstacle/wall on right

If the right obstacle is within the map, add them to the list of obstacle
coordinates. Update position of the robot thereafter.

#### After movement

Once a movement is decided, the robot will use the sensor on the left to 
check for obstacle. 

If distance is lower than range of sensor, there must be an obstacle on the 
left. Hence, get the last set of coordinate of obstacle and add to list of
obstacle coordinates. For the rest of the coordinates, add them to list of 
explored coordinates. 

With the list of explored and obstacle coordinates, update the explored map
and real map accordingly.

### Fastest Path

A star search algorithm is used to find the fastest path from start point to 
waypoint, and then from waypoint to goal point.

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

## Note
In explore.py, the coordinates declared for the position of the 
robot on the map are done with respect to the numpy array initialised
with size (15, 20). Visualisation of the array is as follows:

[[0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]

 [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
 
 [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
 
 [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
 
 [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
 
 [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
 
 [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
 
 [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
 
 [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
 
 [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
 
 [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
 
 [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
 
 [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
 
 [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
 
 [0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0. 0.]]
 
 and self.start_pos is declared to be top left and self.goal
 is declared to be bottom right of the array.