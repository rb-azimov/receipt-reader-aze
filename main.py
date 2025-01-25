import os
import traceback

import cv2
import pytesseract

from src.logger import LowLevelReceiptMinerLogger
from src.props.application_properties_service import ApplicationPropertiesService
from src.receipt_processors.receipt_service import ReceiptService
from src.receipt_processors.receipt_util import ReceiptUtil
from src.props.application_properties_builder import ApplicationPropertiesBuilder

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


def main():
    application_properties = ApplicationPropertiesBuilder.prepare_application_properties_v_core_1_logic_0_depend_1(is_debug_on = True)
    ApplicationPropertiesService.load_properties(application_properties)
    receipt_service = ReceiptService()

    with open(os.path.join('src','fiscal_codes_for_testing', 'ekassa_fiscal_codes.txt'), mode = 'r') as file:
        fiscal_codes = file.readlines()

    # fiscal_codes = fiscal_codes[4:7]
    fiscal_codes_with_watermark = [
        '8ofcmJhYPcaZ',
        'A9DYFDeVJckLTHxcQmpxcJhT5N8TA7KJr12Vga1Qxi3v',
        'JDbiy1aCSKJn'
    ]
    fiscal_codes_with_error = [
        '5Q5zCTnUCtLBVzRv5zyLXjyL58kLv9a7NfL7gtqx6pSQ',
        '7W7ZLvJZSAgUmjKRaJKbga5HXb4WAzFANWqdFrqAGwkr',
        'EPszcWAvJNCGw3HwEYb8PE9Ap3ewAj2TxLN92cdTmLSo',
        'smCRKc7ECvCDtpvqCDAWnZz1NZGvLfdeGgPZXQxbQj3'
    ]

    # fiscal_codes = fiscal_codes_with_error
    fiscal_codes = [fiscal_code.strip() for fiscal_code in fiscal_codes]
    fiscal_codes = list(set(fiscal_codes))
    fiscal_codes.sort()

    fiscal_codes_with_error, errors, error_tracebacks = [], [], []
    receipt_images_folder = os.path.join('logs', 'receipts')
    downloaded_receipt_images = os.listdir(receipt_images_folder)
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
            print(f"! An error occurred (on {fiscal_code}): {e}")
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
