# picamera library should be installed on the Pi by default
from picamera import PiCamera
from picamera.array import PiRGBArray


class Camera:
    def __init__(self):
        self.camera = PiCamera()
        self.camera.resolution = (640, 480)
