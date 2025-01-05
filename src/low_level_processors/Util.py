from datetime import datetime

class Util:

    def obtain_current_datetime():
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
        return formatted_datetime