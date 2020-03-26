from picamera import PiCamera
from picamera.array import PiRGBArray
import cv2 as cv

class Camera:

	def __init__(self , resolution=(640, 480), framerate = 32):
		self.filepath = "/home/pi/src/main/G17/Algo/images/"
		self.camera = PiCamera()
		self.camera.resolution = resolution
		self.camera.framerate = framerate
		self.rawCapture = PiRGBArray(self.camera)
		self.camera.rotation = 90

		#self.camera.vflip = False
		#self.camera.hflip = False

		self.counter = 1

	def capture(self):
		"""
		A function to capture the image and stored it at an assigned directory
		with its respective number count.
		"""
		filename = "{}img{}.jpg".format(self.filepath, str(self.counter))
		# filename = F"{filepath}img{self.counter}.jpg".
		self.camera.capture(self.rawCapture, format="bgr")
		image = self.rawCapture.array
		cv.imwrite(filename, image)
		self.counter += 1
		self.rawCapture.truncate(0)

	def close(self):
		"""
		A function to close the camera and release the resources.
		"""
		self.camera.close()
		print("Picamera closed successfully!")