from src.receipt_processors.util import Util


class ApplicationPropertiesService:
    ocr_properties = None
    splitting_properties = None
    margin_properties = None
    text_similarity_threshold_properties = None
    version = None
    is_debug_on = False
    current_receipt_fiscal_code = 'Undefined'
    current_receipt_processing_start_date_time = Util.prepare_current_datetime()
    logger = None

    @staticmethod
    def load_properties(application_properties):
        ApplicationPropertiesService.ocr_properties = application_properties.ocr_properties
        ApplicationPropertiesService.splitting_properties = application_properties.splitting_properties
        ApplicationPropertiesService.margin_properties = application_properties.margin_properties
        ApplicationPropertiesService.text_similarity_threshold_properties = application_properties.text_similarity_threshold_properties
        ApplicationPropertiesService.version = application_properties.version
        ApplicationPropertiesService.is_debug_on = application_properties.is_debug_on
        ApplicationPropertiesService.logger = application_properties.logger

