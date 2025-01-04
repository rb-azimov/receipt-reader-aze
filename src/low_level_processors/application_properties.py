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
    upper_letters = 'ABCÇDEƏFGĞHXIİJKQLMNOÖPRSŞTUÜVYZ'
    lower_letters = 'abcçdeəfgğhxıijkqlmnoöprsştuüvyz'
    azerbaijani_alphabet = upper_letters + lower_letters
    chartset = ' ' + '%_-№' + azerbaijani_alphabet + '.0123456789'
    general_part_config = f'--psm 6 -c tessedit_char_whitelist={chartset}'

    upper_letters = 'ABCÇDEƏFGĞHXIİJKQLMNOÖPRSŞTUÜVYZ'
    lower_letters = 'abcçdeəfgğhxıijkqlmnoöprsştuüvyz'
    azerbaijani_alphabet = upper_letters + lower_letters
    chartset = ' ' + '%_-' + azerbaijani_alphabet + '.0123456789'
    product_names_config = f'--psm 4 -c tessedit_char_whitelist={chartset}'

    charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxvz'
    payment_type_part_names_config = f'--psm 4 -c tessedit_char_whitelist={charset}'

    ocr_properties = OCRProperties(
        general_part_ocr_properties = OCRProperty(config = general_part_config, lang = 'eng+aze'),
        product_names_ocr_properties = OCRProperty(config = product_names_config, lang = 'eng+aze'),
        quantities_ocr_properties = OCRProperty(config = '--psm 6 -c tessedit_char_whitelist=.0123456789', lang = None),
        prices_ocr_properties = OCRProperty(config = '--psm 6 -c tessedit_char_whitelist=.0123456789', lang = None),
        amounts_ocr_properties = OCRProperty(config = '--psm 6 -c tessedit_char_whitelist=.0123456789', lang = None),
        payment_amount_part_ocr_properties = OCRProperty(config = '--psm 6 -c tessedit_char_whitelist=.0123456789', lang = None),
        payment_type_part_names_ocr_properties = OCRProperty(config = payment_type_part_names_config, lang = 'eng'),
        payment_type_part_numbers_ocr_properties = OCRProperty(config = '--psm 6 -c tessedit_char_whitelist=.0123456789', lang = None)
    )

