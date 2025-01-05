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