import os
import traceback

import cv2
import pytesseract

from src.logger import LowLevelReceiptMinerLogger
from src.low_level_processors.application_properties_service import ApplicationPropertiesService
from src.low_level_processors.application_properties import ApplicationProperties
from src.low_level_processors.properties import OCRProperties, OCRProperty, SplittingProperties, SplittingProperty, \
    MarginProperties, TextSimilarityThresholdProperties
from src.low_level_processors.receipt_service import ReceiptService
import time, math

from src.low_level_processors.receipt_util import ReceiptUtil

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def prepare_application_properties_v1(is_debug_on = False):
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
        text_similarity_threshold_properties,
        is_debug_on
    )

def prepare_application_properties_v2(is_debug_on=False):
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
        general_part_ocr_property=OCRProperty(config=general_part_config, lang='eng+aze'),
        product_names_ocr_property=OCRProperty(config=product_names_config, lang='eng+aze'),
        quantities_ocr_property=OCRProperty(config='--psm 6 -c tessedit_char_whitelist=.0123456789', lang=None),
        prices_ocr_property=OCRProperty(config='--psm 6 -c tessedit_char_whitelist=.0123456789', lang=None),
        amounts_ocr_property=OCRProperty(config='--psm 6 -c tessedit_char_whitelist=.0123456789', lang=None),
        payment_amount_part_ocr_property=OCRProperty(config='--psm 6 -c tessedit_char_whitelist=.0123456789',
                                                     lang=None),
        payment_type_part_names_ocr_property=OCRProperty(config=payment_type_part_names_config, lang='eng'),
        payment_type_part_numbers_ocr_property=OCRProperty(config='--psm 6 -c tessedit_char_whitelist=.0123456789',
                                                           lang=None)
    )

    splitting_properties = SplittingProperties(
        receipt_logical_splitting_property=SplittingProperty(threshold_scale=0.3, min_difference=30),
        payment_to_amount_type_splitting_property=SplittingProperty(threshold_scale=0.5, min_difference=30),
        payment_amount_to_name_value_splitting_property=SplittingProperty(threshold_scale=0.03, min_difference=30),
        payment_type_to_name_value_splitting_property=SplittingProperty(threshold_scale=0.03, min_difference=30),
        products_part_splitting_properties=SplittingProperty(threshold_scale=0.015, min_difference=30) # th_scale changed!
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
        text_similarity_threshold_properties,
        is_debug_on
    )

def main():
    application_properties = prepare_application_properties_v2(is_debug_on = True)
    ApplicationPropertiesService.load_properties(application_properties)
    receipt_service = ReceiptService()

    with open(os.path.join('src','fiscal_codes_for_testing', 'ekassa_fiscal_codes.txt'), mode = 'r') as file:
        fiscal_codes = file.readlines()

    # fiscal_codes = fiscal_codes[4:7]
    fiscal_codes = [fiscal_code.strip() for fiscal_code in fiscal_codes]
    fiscal_codes = list(set(fiscal_codes))
    fiscal_codes.sort()

    # fiscal_codes_of_interest = []
    fiscal_codes_with_error, errors, error_tracebacks = [], [], []
    receipt_images_folder = os.path.join('logs', 'receipts')
    downloaded_receipt_images = os.listdir()
    receipts_dict = {}
    for i in range(len(fiscal_codes)):
        fiscal_code = fiscal_codes[i]
        print(f'{i+1}. {fiscal_code}')
        image_name = LowLevelReceiptMinerLogger.sanitize_string(f"receipt_{fiscal_code}.jpg")
        if image_name not in downloaded_receipt_images:
            image_ekassa_gray = ReceiptUtil.read_image_from_ekassa(fiscal_code)
            image_file = os.path.join(receipt_images_folder, image_name)
            cv2.imwrite(image_file, image_ekassa_gray)
        image_ekassa_gray = cv2.imread(os.path.join(receipt_images_folder, image_name), cv2.IMREAD_GRAYSCALE)

        try:
            receipt = receipt_service.mine_receipt(image_ekassa_gray=image_ekassa_gray,
                                                   fiscal_code=fiscal_code)
            receipt._fiscal_code = fiscal_code
        except Exception as e:
            print(f"An error occurred (on {fiscal_code}): {e}")
            # traceback.print_exc()
            errors.append(e)
            error_tracebacks.append(traceback.format_exc())
            fiscal_codes_with_error.append(fiscal_code)
        else:
            receipts_dict[fiscal_code] = receipt

    receipts = list(receipts_dict.values())
    ReceiptUtil.export_receipts(receipts)

    print()
    print('<< Receipts >>')
    for fiscal_code, receipt in receipts_dict.items():
        print(f'FISCAL CODE: {fiscal_code}')
        print((receipt.__str__()))

    receipt_images = []
    receipt_image_paths = []
    receipt_images_folder = os.path.join('logs', 'receipts')
    for fiscal_code in list(receipts_dict.keys()):
        image_name = LowLevelReceiptMinerLogger.sanitize_string(f"receipt_{fiscal_code}.jpg")
        receipt_image_path = os.path.join(receipt_images_folder, image_name)
        receipt_image_paths.append(receipt_image_path)
        receipt_image = cv2.imread(receipt_image_path, cv2.IMREAD_GRAYSCALE)
        receipt_images.append(receipt_image)
    ReceiptUtil.export_receipts(
        receipts=[receipt.__str__() for receipt in receipts],
        receipt_image_paths = receipt_image_paths,
        export_option=ReceiptUtil.EXPORT_IMPORT_HTML
    )

    print()
    print('<<Fiscal codes that error occured>>')
    for i in range(len(fiscal_codes_with_error)):
        print(f'{(i+1)}. {fiscal_codes_with_error[i]}'.strip())

    print('---------------')
    print()
    print('<<Errors>>')
    for i in range(len(fiscal_codes_with_error)):
        print(f'{(i+1)}. {errors[i]}'.strip())
        print('---------------')
    print()
    print('<<Traceback>>')
    for i in range(len(fiscal_codes_with_error)):
        print(f'{(i+1)}. {errors[i]}\n{error_tracebacks[i]}'.strip())
        print('---------------')

if __name__ == '__main__':
    main()
