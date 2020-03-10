import cv2
import time
import numpy as np
import matplotlib.pyplot as plt
from os import listdir


class ImageRecognition:
    def __init__(self, text_color, threshold=1):
        """
        Function to initialise an instance of ImageRecognition class
        :param text_color: Class
                Class for colourised print statements
        :param threshold: float
                Float to be used as threshold for comparing images
        """
        self.threshold = threshold
        self.text_color = text_color
        self.true_images = []
        self.log_string = self.text_color.OKBLUE + \
                          '{} | ImageRecognition Algo: '.format(time.asctime()) \
                          + self.text_color.ENDC
        directory = './Signs'

        # Save all file names if they are an image (.jpg extension)
        image_folder = [file for file in listdir(directory) if '.png' in file]

        for image in image_folder:
            # Convert image into bgr array of type float before saving it
            self.true_images.append(cv2.imread(directory + image).astype('float'))

    def compare(self, captured_image_path):
        """
        Function to compare captured image to known images
        :param captured_image_path: String
                String containing path to recently captured image
        :return: ID
                Returns Image ID of closest known image to captured image
                Returns -1 otherwise
        """
        # Convert captured image into bgr array of type float
        captured_image_array = cv2.imread(captured_image_path).astype('float')

        # For every bgr array stored in true_images
        for image in self.true_images:

            # This formula is retrieved from https://www.pyimagesearch.com/2014/09/15/python-compare-two-images/
            # Need to check validity
            diff = np.sum((captured_image_array - image) ** 2)
            diff /= float(captured_image_array.shape[0] * image.shape[1])

            # If the difference is lower than declared threshold, image is more or less similar
            # Hence return image ID
            if diff <= self.threshold:
                print(self.log_string + self.text_color.OKGREEN +
                      'Similar image found! ID: {}'.format(self.true_images.index(image) + 1)
                      + self.text_color.ENDC)
                return True

        # If all images does not conform within threshold, image is not similar.
        # Hence return -1
        print(self.log_string + self.text_color.FAIL +
              'No similar images found.'
              + self.text_color.ENDC)
        return False

    @staticmethod
    def display_image(captured_image):
        """
        Function to display captured image
        :param captured_image: String
                String containing path to recently captured image
        :return:
        """
        plt.imshow(captured_image)
        plt.show()
