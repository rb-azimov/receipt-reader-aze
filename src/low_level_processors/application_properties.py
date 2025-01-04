class Property:
    pass

class OCRProperty(Property):
    def __init__(self, config, lang):
        self.config = config
        self.lang = lang

class SplittingProperty(Property):
    pass

class OCRProperties:
    def __init__(self,
                 general_part_ocr_properties,
                 product_names_ocr_properties,
                 quantities_ocr_properties,
                 prices_ocr_properties,
                 amounts_ocr_properties,
                 payment_amount_part_ocr_properties,
                 payment_type_part_names_ocr_properties,
                 payment_type_part_numbers_ocr_properties):
        self.general_part_ocr_properties = general_part_ocr_properties
        self.product_names_ocr_properties = product_names_ocr_properties
        self.quantities_ocr_properties = quantities_ocr_properties
        self.prices_ocr_properties = prices_ocr_properties
        self.amounts_ocr_properties = amounts_ocr_properties
        self.payment_amount_part_ocr_properties = payment_amount_part_ocr_properties
        self.payment_type_part_names_ocr_properties = payment_type_part_names_ocr_properties
        self.payment_type_part_numbers_ocr_properties = payment_type_part_numbers_ocr_properties

class ApplicationProperties:
    ocr_properties = OCRProperties(
        general_part_ocr_properties = OCRProperty(config = '', lang = ''),
        product_names_ocr_properties = OCRProperty(config = '', lang = ''),
        quantities_ocr_properties = OCRProperty(config = '', lang = ''),
        prices_ocr_properties = OCRProperty(config = '', lang = ''),
        amounts_ocr_properties = OCRProperty(config = '', lang = ''),
        payment_amount_part_ocr_properties = OCRProperty(config = '', lang = ''),
        payment_type_part_names_ocr_properties = OCRProperty(config = '', lang = ''),
        payment_type_part_numbers_ocr_properties = OCRProperty(config = '', lang = '')
    )




