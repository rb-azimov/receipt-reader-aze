import re
from datetime import datetime
import platform

import cv2
import numpy as np
import psutil

class Util:
    @staticmethod
    def prepare_current_datetime():
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
        return formatted_datetime

    @staticmethod
    def prepare_device_properties():
        text = ''
        text += f'<< Device Properties >>\n'
        text += f"System: {platform.system()}\n"
        text += f"Processor: {platform.processor()}\n"
        text += f"CPU Cores: {psutil.cpu_count(logical=False)}\n"
        text += f"Logical CPUs: {psutil.cpu_count(logical=True)}\n"
        text += f"RAM Size (GB): {round(psutil.virtual_memory().total / (1024 ** 3), 2)}\n"
        text += f"CPU Frequency (GHz): {psutil.cpu_freq().current / 1000}\n"
        return text

    @staticmethod
    def clean_and_convert_to_float(s):
        """
        Cleans a string and converts it to a float if possible.
        Handles common issues like trailing dots, commas, and non-numeric characters.
        """
        if s.endswith('.'):
            s = s.rstrip('.')
        return s

    @staticmethod
    def find_vertical_bounds(image, threshold=1):
        row_sums = np.sum(255-image, axis=1)
        content_rows = np.where(row_sums > threshold)[0]
        if len(content_rows) == 0:
            return None, None
        start_index = content_rows[0]
        end_index = content_rows[-1]
        return start_index, end_index

    @staticmethod
    def find_horizontal_bounds(image, threshold=1):
        row_sums = np.sum(255 - image, axis=0)
        content_rows = np.where(row_sums > threshold)[0]
        if len(content_rows) == 0:
            return None, None
        start_index = content_rows[0]
        end_index = content_rows[-1]
        return start_index, end_index

    @staticmethod
    def resize_image(image, scale_factor):
        """
        Resizes a grayscale image by a given scale factor.

        Parameters:
            image (numpy.ndarray): Input grayscale image.
            scale_factor (float): The factor by which to resize the image (e.g., 2 for 2x larger, 0.5 for half size).

        Returns:
            numpy.ndarray: Resized image.
        """
        # Get the current dimensions of the image
        height, width = image.shape[:2]

        # Calculate the new dimensions
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)

        # Resize the image
        resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_NEAREST)

        return resized_image
