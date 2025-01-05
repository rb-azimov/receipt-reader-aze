import pytesseract

from src.low_level_processors.application_properties import ApplicationProperties, ApplicationPropertiesService
from src.low_level_processors.properties import OCRProperties, OCRProperty, SplittingProperties, SplittingProperty, \
    MarginProperties, TextSimilarityThresholdProperties
from src.low_level_processors.receipt_service import ReceiptService
import time, math
import platform
import psutil
import matplotlib.pyplot as plt

from src.low_level_processors.receipt_util import ReceiptUtil

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def prepare_application_properties():
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
        general_part_ocr_property = OCRProperty(config = general_part_config, lang = 'eng+aze'),
        product_names_ocr_property = OCRProperty(config = product_names_config, lang = 'eng+aze'),
        quantities_ocr_property = OCRProperty(config = '--psm 6 -c tessedit_char_whitelist=.0123456789', lang = None),
        prices_ocr_property = OCRProperty(config = '--psm 6 -c tessedit_char_whitelist=.0123456789', lang = None),
        amounts_ocr_property = OCRProperty(config = '--psm 6 -c tessedit_char_whitelist=.0123456789', lang = None),
        payment_amount_part_ocr_property = OCRProperty(config = '--psm 6 -c tessedit_char_whitelist=.0123456789', lang = None),
        payment_type_part_names_ocr_property = OCRProperty(config = payment_type_part_names_config, lang = 'eng'),
        payment_type_part_numbers_ocr_property = OCRProperty(config = '--psm 6 -c tessedit_char_whitelist=.0123456789', lang = None)
    )

    splitting_properties = SplittingProperties(
        receipt_logical_splitting_property = SplittingProperty(threshold_scale = 0.3, min_difference = 30),
        payment_to_amount_type_splitting_property = SplittingProperty(threshold_scale = 0.5, min_difference = 30),
        payment_amount_to_name_value_splitting_property = SplittingProperty(threshold_scale = 0.03, min_difference = 30),
        payment_type_to_name_value_splitting_property = SplittingProperty(threshold_scale = 0.03, min_difference = 30),
        products_part_splitting_properties = SplittingProperty(threshold_scale = 0.01, min_difference = 30)
    )

    margin_properties = MarginProperties(
        product_line_margin=3,
        general_part_bottom_margin=50,
        payment_part_bottom_margin=160,
        cashier_date_time_top_margin=2,
        payment_amount_part_margin=5,
        payment_type_name_value_margin=50
    )

    text_similarity_threshold_properties = TextSimilarityThresholdProperties(
        payment_type_checking_text_similarity_threshold=70,
        one_token_text_similarity_threshold=80,
        multi_token_text_similarity_threshold=80
    )

    return ApplicationProperties(
        ocr_properties,
        splitting_properties,
        margin_properties,
        text_similarity_threshold_properties
    )

def main():
    print('<< Device Properties >>')
    print("System:", platform.system())
    print("Processor:", platform.processor())
    print("CPU Cores:", psutil.cpu_count(logical=False))  # Physical cores
    print("Logical CPUs:", psutil.cpu_count(logical=True))
    print("RAM Size (GB):", round(psutil.virtual_memory().total / (1024 ** 3), 2))
    print("CPU Frequency (GHz):", psutil.cpu_freq().current / 1000)
    print('\n')

    fiscal_codes = [
        'wPeLM3wvuBUCQn4TMN5ZQZvheV7XuQg97meruVsqRVT',
        'Dh8hsAoFVGFcyEzwYdmmykoZZZPhm5LeVe9r9VZQy9AH',
        'JDbiy1aCSKJn',
        'BaLH4264TYtf',
        '8ofcmJhYPcaZ',
        '4tFLVnqE1gbT',
        'ER9s8qbNzEsyVcj2vhRi7yJGxsUgKkVvE7fydNX2Mz7y',
        '97mG868j3tAdNn1AWwemUtt93B4F9ycDHvmoMdqFcqWy'
    ]
    fiscal_code = fiscal_codes[-1]

    application_properties = prepare_application_properties()
    ApplicationPropertiesService.load_properties(application_properties)
    
    receipt_service = ReceiptService(app_props=None)
    start_time = time.time()
    receipt = receipt_service.mine_receipt(fiscal_code)
    processing_time = time.time() - start_time
    print(receipt.__str__())
    print(f'\n\nProcessed in {math.ceil(processing_time)} seconds!')

    plt.imshow(ReceiptUtil.read_image_from_ekassa(fiscal_code), cmap='gray')
    plt.show()

if __name__ == '__main__':
    main()
