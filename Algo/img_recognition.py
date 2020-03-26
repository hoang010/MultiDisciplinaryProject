import cv2 as cv
import numpy as np
import glob


class ImageRecognition:
	def __init__(self):

		config = "./Algo/model/tinyv3.config"
		weights = "./Algo/model/tinyv3.weights"

		self.net = cv.dnn.readNet(weights, config)
		self.classes = None
		self.colors = None
		self.count = 1
		self.ids = []
		self.tracker = 1
		self.predicted_list = []

		self.switcher = {
	        0: 3,
	        1: 1,
	        2: 5,
	        3: 10,
	        4: 11,
	        5: 2,
	        6: 6,
	        7: 8,
	        8: 9,
	        9: 7,
	        10: 13,
	        11: 14,
	        12: 15,
	        13: 4,
	        14: 12
	    }

		self.load_classes()

	def load_classes(self):

		file = "./Algo/model/img_classes.txt"

		with open(file , 'r') as f:
			self.classes = [line.strip() for line in f.readlines()]

		self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))

	def load_image(self):

		file = "./Algo/images/image{}.jpg".format(str(self.tracker))
		self.tracker += 1
		return np.asarray(cv.imread(file))

	@staticmethod
	def load_images():

		return np.asarray([cv.imread(file) for file in glob.glob("./Algo/images/*.jpg")])

	def get_output_layers(self):

		layer_names = self.net.getLayerNames()

		output_layers = [layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

		return output_layers

	def draw_bounding_box(self, image, class_id, confidence, x, y, x_plus_w, y_plus_h):

		label = str(self.classes[class_id])

		color = self.colors[class_id]

		cv.rectangle(image, (x, y), (x_plus_w, y_plus_h), color, 2)

		cv.putText(image, label, (x_plus_w, y_plus_h), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

	def predict(self, image):

		class_ids = []
		confidences = []
		boxes = []
		conf_threshold = 0.2
		nms_threshold = 0.4

		width = image.shape[1]
		height = image.shape[0]
		scale = 0.00392
		isRecognised = False

		blob = cv.dnn.blobFromImage(image, scale, (416, 416), (0, 0, 0), True, crop=False)

		self.net.setInput(blob)

		layers = self.get_output_layers()
		outs = self.net.forward(layers)

		# for each detection from each output layer 
		# get the confidence, class id, bounding box params
		# and ignore weak detections (confidence < 0.2)
		for out in outs:
			for detection in out:

				scores = detection[5:]
				class_id = np.argmax(scores)
				confidence = scores[class_id]

				if confidence > 0.2:

					center_x = int(detection[0] * width)
					center_y = int(detection[1] * height)
					w = int(detection[2] * width)
					h = int(detection[3] * height)
					x = center_x - w / 2
					y = center_y - h / 2
					class_ids.append(class_id)
					confidences.append(float(confidence))
					boxes.append([x, y, w, h])

		# apply non-max suppression
		indices = cv.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

		# go through the detections remaining
		# after nms and draw bounding box
		for i in indices:
			isRecognised = True
			i = i[0]
			box = boxes[i]
			x = box[0]
			y = box[1]
			w = box[2]
			h = box[3]
			self.draw_bounding_box(image, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))

		if(isRecognised and class_ids[0] not in self.predicted_list):
			# save output image to disk
			cv.imwrite("./Algo/predicted_images/object-detection-{}.jpg".format(str(self.count)), image)
			self.count = self.count + 1
			mapped_id = self.switcher.get(class_ids[0], "Number not in range 0 to 15!")
			self.predicted_list.append(class_ids[0])
			self.ids.append(["","",mapped_id])

	def get_predicted_ids(self):

		packet = "{\"dest\": \"bt\",  \
                   \"images\": \
                   \"[" + "[" + str(self.ids[0][0]) + "," + str(self.ids[0][1]) + "," + str(self.ids[0][2]) + "]" + "," + "[" + str(self.ids[1][0]) + "," + str(self.ids[1][1]) + "," + str(self.ids[1][2]) + "]" + "," + "[" + str(self.ids[2][0]) + "," + str(self.ids[2][1]) + "," + str(self.ids[2][2]) + "]" + "," + "[" + str(self.ids[3][0]) + "," + str(self.ids[3][1]) + "," + str(self.ids[3][2]) + "]" + "," + "[" + str(self.ids[4][0]) + "," + str(self.ids[4][1]) + "," + str(self.ids[4][2]) + "]"  + "]\"}"

		print(self.ids)
		return packet
