# picamera library should be installed on the Pi by default
import picamera
import cv2
import os


class Recorder:
    def __init__(self):
        self.camera = picamera.PiCamera()
        self.camera.resolution = (640, 480)
        self.io = picamera.CircularIO(size=10)

    def start(self):
        self.camera.start_recording(self.io)

    def draw_box(self):
        cv2.rectangle(self.io, (5, 15), (20, 5), (255, 0, 0), 2)
        self.capture()

    def capture(self):
        path = './RPi/Captured Images'
        num = len([name for name in os.listdir(path) if os.path.isfile(name)])
        self.camera.capture('Image {}.png'.format(num))
        return path + 'Image {}.png'.format(num)

    def remove_box(self):
        cv2.rectangle(self.io, (5, 10), (20, 10), (255, 0, 0), 0)

    def stop(self):
        self.camera.stop_recording()
        self.camera.close()