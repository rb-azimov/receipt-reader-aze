from src.logger import LowLevelReceiptMinerLogger

class ApplicationProperties:
    version = 0
    def __init__(self,
                 ocr_properties,
                 splitting_properties,
                 margin_properties,
                 text_similarity_threshold_properties,
                 is_debug_on = False):

        self.ocr_properties = ocr_properties
        self.splitting_properties = splitting_properties
        self.margin_properties = margin_properties
        self.text_similarity_threshold_properties = text_similarity_threshold_properties
        self.is_debug_on = is_debug_on
        self.logger = LowLevelReceiptMinerLogger()

        ApplicationProperties.version += 1
        self.version = ApplicationProperties.version
