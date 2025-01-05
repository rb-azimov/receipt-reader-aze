from src.low_level_processors.properties import OCRProperties, OCRProperty, SplittingProperties, SplittingProperty, \
    MarginProperties, TextSimilarityThresholdProperties


class ApplicationPropertiesService:
    ocr_properties = None
    splitting_properties = None
    margin_properties = None
    text_similarity_threshold_properties = None
    version = None

    @staticmethod
    def load_properties(application_properties):
        ApplicationPropertiesService.ocr_properties = application_properties.ocr_properties
        ApplicationPropertiesService.splitting_properties = application_properties.splitting_properties
        ApplicationPropertiesService.margin_properties = application_properties.margin_properties
        ApplicationPropertiesService.text_similarity_threshold_properties = application_properties.text_similarity_threshold_properties
        ApplicationPropertiesService.version = application_properties.version

class ApplicationProperties:
    version = 0
    def __init__(self,
                 ocr_properties,
                 splitting_properties,
                 margin_properties,
                 text_similarity_threshold_properties):

        self.ocr_properties = ocr_properties
        self.splitting_properties = splitting_properties
        self.margin_properties = margin_properties
        self.text_similarity_threshold_properties = text_similarity_threshold_properties

        ApplicationProperties.version += 1
        self.version = ApplicationProperties.version
