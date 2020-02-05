# picamera library should be installed on the Pi by default
import picamera


class Recorder:
    def __init__(self):
        self.camera = picamera.PiCamera()
        self.camera.resolution = (640, 480)
        self.io = picamera.CircularIO(size=10)

    def start(self):
        self.camera.start_recording(self.io)

    def stop(self):
        self.camera.stop_recording()
        self.camera.close()