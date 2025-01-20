import math
import os
import time

import cv2
from matplotlib import pyplot as plt
from matplotlib.scale import scale_factory

from src.logger import LowLevelReceiptMinerLogger
from src.low_level_processors.util import Util
from src.low_level_processors.application_properties_service import ApplicationPropertiesService
from src.low_level_processors.receipt_builder import ReceiptBuilder
from src.low_level_processors.receipt_util import ReceiptUtil
from src.models.product import Product
from src.models.receipt import Receipt
from src.models.receipt_general_info import ReceiptGeneralInfo
from src.models.receipt_payment_info import ReceiptPaymentInfo
from src.models.receipt_product_list import ReceiptProductList
import warnings

warnings.simplefilter("always", UserWarning)

class ReceiptService:
  """
    Class for taking a fiscal code,
    calling the methods of ReceiptBuilder
    performing OCR and NER in high level.

    Attributes:
        app_props (ApplicationProperties): includes global properties for using in OCR and NER (e.g. threshold scale)

    Methods:
        mine_receipt(fiscal_code) -> Receipt instance
        perform_ner_on_general_part(image_general) -> ReceiptGeneralInfo instance
        perform_ner_on_products_part(image_products) -> ReceiptProductList instance
        perform_ner_on_payment_details_part(image_total) -> ReceiptPaymentInfo instance

  """

  def mine_receipt(self, image_ekassa_gray = None, fiscal_code = None):
    """
    Acquires receipt image from E-kassa using the fiscal code.
    Splits receipt image into general, products, payments parts.
    Gathers mined data from the receipts parts to a single Receipt instance.

    Args:
        fiscal_code (str): unique tax identifier of a receipt
        ...

    Returns:
        return_type: Receipt instance
    """
    start_time = time.time()
    if image_ekassa_gray is None:
      image_ekassa_gray = ReceiptUtil.read_image_from_ekassa(fiscal_code)
      receipt_images_folder = os.path.join('logs', 'receipts')
      image_name = LowLevelReceiptMinerLogger.sanitize_string(f"receipt_{fiscal_code}.jpg")
      if image_name not in os.listdir(receipt_images_folder):
        image_file = os.path.join(receipt_images_folder, image_name)
        # image_ekassa_gray = ReceiptUtil.read_image_from_ekassa(fiscal_code)
        cv2.imwrite(image_file, image_ekassa_gray)

    ApplicationPropertiesService.current_receipt_fiscal_code = fiscal_code
    ApplicationPropertiesService.current_receipt_processing_start_date_time = Util.prepare_current_datetime()
    image_general, image_products, image_payment, product_part_rect_xs_list = ReceiptBuilder.split_receipt_logical_parts(image_ekassa_gray)

    if ApplicationPropertiesService.is_debug_on:
      ApplicationPropertiesService.logger.log_image('Ekassa image (gray)', image_ekassa_gray)
      ApplicationPropertiesService.logger.log_image('general part of receipt', image_general)
      ApplicationPropertiesService.logger.log_image('products part of receipt', image_products)
      ApplicationPropertiesService.logger.log_image('payments part of receipt', image_payment)

    general_info = self.perform_ner_on_general_part(image_general)
    products = self.perform_ner_on_products_part(image_products, product_part_rect_xs_list)
    payment_info = self.perform_ner_on_payment_details_part(image_payment)

    receipt = Receipt(general_info, products, payment_info)
    processing_time = time.time() - start_time
    if ApplicationPropertiesService.is_debug_on:
      ApplicationPropertiesService.logger.log_text('device properties', Util.prepare_device_properties())
      ApplicationPropertiesService.logger.log_text('general results',
                                                   f'Processed in {math.ceil(processing_time)} seconds!\n\n' +
                                                   receipt.__str__())
      ApplicationPropertiesService.logger.log_receipt('extracted receipt text', receipt.__str__())
      ApplicationPropertiesService.logger.log_receipt_image('receipt image', image_ekassa_gray)
    receipt._fiscal_code = fiscal_code
    return receipt

  def perform_ner_on_general_part(self, image_general):
    """
    Determine roughly general properties of the receipt.
    Adjusts cashier name, date, time if necessary.

    Args:
        image_general (numpy array): general part of the receipt image
        ...

    Returns:
        return_type: ReceiptGeneralInfo instance
    """
    multi_token_keywords = ['Object name', 'Object address:', 'Object code:', 'Taxpayer name:', 'Sale receipt №']
    one_token_keywords = ['TIN:', 'Cashier:', 'Date:', 'Time:']
    results_dict, df, selected_df = ReceiptUtil.rule_based_text_extraction(image_general, multi_token_keywords, one_token_keywords)

    cashier_part_image, date_time_part_image = ReceiptBuilder.segment_cashier_date_time_part(image_general, df, selected_df)
    cashier_value_dict, _, _ = ReceiptUtil.rule_based_text_extraction(cashier_part_image, multi_token_keywords = None, one_token_keywords = ['Cashier:',])
    date_time_value_dict, _, _ = ReceiptUtil.rule_based_text_extraction(date_time_part_image, multi_token_keywords = None, one_token_keywords = ['Date:', 'Time:'])

    if ApplicationPropertiesService.is_debug_on:
      ApplicationPropertiesService.logger.log_image('general-cashier part image', cashier_part_image)
      ApplicationPropertiesService.logger.log_image('general-datetime part image', date_time_part_image)

    for key, value in cashier_value_dict.items():
      results_dict[key] = value
    for key, value in date_time_value_dict.items():
      results_dict[key] = value

    if 'Object name' not in results_dict:
      results_dict['Object name'] = '-'
      warnings.warn('Object name was not found!', UserWarning)

    if 'Object address' not in results_dict:
      results_dict['Object address'] = '-'
      warnings.warn('Object address was not found!', UserWarning)

    general_info = ReceiptGeneralInfo(
      name = results_dict['Object name'],
      address = results_dict['Object address'],
      code = results_dict['Object code'],
      tax_payer_name = results_dict['Taxpayer name'],
      TIN = results_dict['TIN'],
      sale_receipt_num = results_dict['Sale receipt №'],
      cashier_name = results_dict['Cashier'],
      date = results_dict['Date'],
      time = results_dict['Time']
    )
    return general_info

  def perform_ner_on_products_part(self, image_products, product_part_rect_xs_list):
    """
    Splits products part of the receipt image into
    product names, quantities, prices, amounts.
    Uses quantities vertical locations to determine
    locations of seperate product names.

    Args:
        image_products (numpy array): products part of the receipt image
        ...

    Returns:
        return_type: ReceiptProductsList instance
    """
    rect_xs_list = product_part_rect_xs_list
    clear_products_part, clear_quantities_part, clear_prices_part, clear_amounts_part = ReceiptBuilder.segment_products_part(image_products, rect_xs_list)

    if ApplicationPropertiesService.is_debug_on:
      ApplicationPropertiesService.logger.log_image('Products', clear_products_part)
      ApplicationPropertiesService.logger.log_image('Quantities', clear_quantities_part)
      ApplicationPropertiesService.logger.log_image('Prices', clear_prices_part)
      ApplicationPropertiesService.logger.log_image('Amounts', clear_amounts_part)

    ocr_property = ApplicationPropertiesService.ocr_properties.quantities_ocr_property
    quantities, df_quantities = ReceiptUtil.perform_ocr_obtain_values(image=clear_quantities_part,
                ocr_config=ocr_property.config, return_type = float, lang = ocr_property.lang)

    # Handle very small number segments when there is one number
    if df_quantities.shape[0] == 0:
      quantities, df_quantities = ReceiptUtil.perform_ocr_on_small_image(clear_quantities_part)

    product_line_margin = ApplicationPropertiesService.margin_properties.product_line_margin
    product_images = ReceiptUtil.prepare_product_images(clear_products_part, df_quantities,
                     quantities_image_height = clear_quantities_part.shape[0], product_line_margin = product_line_margin)
    product_names = ReceiptBuilder.extract_product_names(product_images)

    price_images = ReceiptUtil.prepare_price_images(clear_prices_part, df_quantities,
                                                        price_line_margin=product_line_margin)
    amount_images = ReceiptUtil.prepare_amount_images(clear_amounts_part, df_quantities,
                                                      amount_line_margin=product_line_margin)

    prices = ReceiptBuilder.extract_prices(price_images)
    amounts = ReceiptBuilder.extract_amounts(amount_images)

    # print('Quantities:', quantities)
    # print('Prices:', prices)
    # print('Amounts:', amounts)
    # ocr_property = ApplicationPropertiesService.ocr_properties.prices_ocr_property
    # prices, _ = ReceiptUtil.perform_ocr_obtain_values(image=clear_prices_part,
    #             ocr_config=ocr_property.config, return_type = float, lang = ocr_property.lang)
    # ocr_property = ApplicationPropertiesService.ocr_properties.amounts_ocr_property
    # amounts, _ = ReceiptUtil.perform_ocr_obtain_values(image=clear_amounts_part,
    #             ocr_config=ocr_property.config, return_type = float, lang = ocr_property.lang)

    products = [Product(product_names[i], quantities[i], prices[i], amounts[i]) for i in range(len(product_names))]
    return ReceiptProductList(products)

  def perform_ner_on_payment_details_part(self, image_payment):
    """
    Splits payments part of the receipt image into
    payment amounts, payment type details.

    Args:
        image_payment (numpy array): payment details part of the receipt image
        ...

    Returns:
        return_type: ReceiptPaymentInfo instance
    """
    payment_part_image, payment_type_part_image = ReceiptBuilder.segment_payment_details_part(image_payment)

    total_amount_standalone, non_tax_amount, tax_amount = ReceiptBuilder.extract_values_from_payment_part(payment_part_image)
    cashless, cash, paid_cash, change, bonus, prepayment, credit = ReceiptBuilder.extract_values_from_payment_type_part(payment_type_part_image)

    payment_info = ReceiptPaymentInfo(total_amount_standalone, non_tax_amount, tax_amount, cashless, cash, paid_cash, change, bonus, prepayment, credit)
    return payment_info