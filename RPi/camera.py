from picamera import PiCamera

class Camera:

	filepath = "/home/pi/src/images/"

	def __init__(self , resolution=(640, 480), framerate = 32):
		self.camera = PiCamera()
		self.camera.resolution = resolution
		self.camera.framerate = framerate

		#self.camera.vflip = False
		#self.camera.hflip = False

		self.counter = 1

	def capture(self):
		"""
		A function to capture the image and stored it at an assigned directory
		with its respective number count.
		"""
		img = F"{filepath}img{self.counter}.jpg"
		self.camera.capture(img)
		self.counter = self.counter + 1


	def close(self):
		"""
		A function to close the camera and release the resources.
		"""
		self.camera.close()
		print("Picamera closed successfully!")