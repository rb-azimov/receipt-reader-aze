import re
from datetime import datetime
import platform
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
        # try:
        #     # Remove leading/trailing whitespace
        #     s = s.strip()
        #
        #     # Replace commas with empty string (e.g., "1,234" -> "1234")
        #     s = s.replace(',', '')
        #
        #     # Remove non-numeric characters except for '.' and '-'
        #     s = re.sub(r'[^\d.-]', '', s)
        #
        #     # Remove trailing dots (e.g., "123." -> "123")
        #     if s.endswith('.'):
        #         s = s.rstrip('.')
        #
        #     # Check for empty or invalid strings after cleaning
        #     if not s or s in ['-', '.']:
        #         raise ValueError("String cannot be converted to float")
        #
        #     # Convert to float
        #     return float(s)
        # except ValueError:
        #     print(f"Error: Unable to convert '{s}' to float.")
        #     return None