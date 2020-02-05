# Repo for Group 17 MDP Project

## Pre-requisite
The repository requires (but is not limited to) the 
following libraries to execute:
* Python 3.7
* PyBluez 0.23
* OpenCV 4.0.1
* PySerial 3.4

## Installing
Execute the following command to install the libraries\
`pip3 install -r requirements.txt`

## Workings

This section will document the functions within main.py. For more 
information about the classes used, refer to the README.md in their
respective folders.
* [Algo](Algo/README.md)
* [Android](Android/README.md)
* [Arduino](Arduino/README.md)
* [RPi](RPi/README.md)

### main.py
This file contains the main function required to start the program. It starts a server/client 
depending on the OS in which the main function is run on. A server on the Raspberry Pi will be 
initialised if the OS is Linux, and a client will be initialised if the OS is Windows or Mac.

## Deployment
Execute the command `python3 main.py` to start.

## Contributors
The project is done by the following team members:
* Neo Kian Hao
* Sin Chong Wen Bryan
* Satya Gupta
* Goh Yong Wei
* Wong Chun Foong
* Cao Shiqi
* Nguyen Le Hoang
* Pereddy Vijai Krishna Reddy

## References
* [Comparing 2 images](https://www.pyimagesearch.com/2014/09/15/python-compare-two-images/)
