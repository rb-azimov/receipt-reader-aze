import os
import re
import cv2
import logging

from src.low_level_processors.application_properties_service import ApplicationPropertiesService

class LowLevelReceiptMinerLogger:
    def __init__(self, output_dir="logs"):
        """
        Class for saving needed logging images and texts in different processing phases.

        Parameters:
        - output_dir (str): Directory where logs (images and text) will be stored.
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def log_text(self, tag, text):
        """
        Logs the text results for a given phase of processing.

        Parameters:
        - tag (str): keyword as recognition phase definition.
        - text (str): Text to log.
        """
        image_id = ApplicationPropertiesService.current_receipt_fiscal_code
        receipt_processing_start_date_time = ApplicationPropertiesService.current_receipt_processing_start_date_time
        fiscal_code_dir = os.path.join(self.output_dir, f'{image_id}_{receipt_processing_start_date_time}')
        os.makedirs(fiscal_code_dir, exist_ok=True)
        log_file_name = LowLevelReceiptMinerLogger.sanitize_string(f"{tag}_text.log")
        log_file_path = os.path.join(fiscal_code_dir, log_file_name)
        with open(log_file_path, "w", encoding="utf-8") as f:
            f.write(text)
        logging.info(f"Logged text for {image_id} during {tag}")

    def log_image(self, tag, image):
        """
        Logs the image results for a given phase of processing.

        Parameters:
        - tag (str): keyword as recognition phase definition.
        - image (numpy.ndarray): Image to save.
        """
        image_id = ApplicationPropertiesService.current_receipt_fiscal_code
        receipt_processing_start_date_time = ApplicationPropertiesService.current_receipt_processing_start_date_time
        image_name = LowLevelReceiptMinerLogger.sanitize_string(f"{tag}.jpg")
        fiscal_code_dir = os.path.join(self.output_dir, f'{image_id}_{receipt_processing_start_date_time}')
        os.makedirs(fiscal_code_dir, exist_ok=True)
        image_file = os.path.join(fiscal_code_dir, image_name)
        cv2.imwrite(image_file, image)
        logging.info(f"Logged image for {image_id} during {tag}")
        return image_name

    def sanitize_string(input_string):
        """
        Replaces non-saveable characters in a string with safe alternatives.

        Parameters:
        - input_string (str): The string to sanitize.

        Returns:
        - str: The sanitized string.
        """
        # Define a pattern for unsafe characters (e.g., special characters that can't be in file names)
        unsafe_pattern = r'[<>:"/\\|?*]'

        # Replace unsafe characters with underscores or another safe character
        sanitized_string = re.sub(unsafe_pattern, '_', input_string)

        # Optionally, trim leading/trailing spaces and replace multiple underscores with a single one
        sanitized_string = re.sub(r'__+', '_', sanitized_string.strip('_ '))

        return sanitized_string
