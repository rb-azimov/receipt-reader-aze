from src.low_level_processors.application_properties import ApplicationProperties
from src.low_level_processors.receipt_builder import ReceiptBuilder
from src.low_level_processors.receipt_util import ReceiptUtil
from src.models.product import Product
from src.models.receipt import Receipt
from src.models.receipt_general_info import ReceiptGeneralInfo
from src.models.receipt_payment_info import ReceiptPaymentInfo
from src.models.receipt_product_list import ReceiptProductList


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

  def __init__(self, app_props):
    self.app_props = app_props

  def mine_receipt(self, fiscal_code: str):
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
    image_ekassa_gray = ReceiptUtil.read_image_from_ekassa(fiscal_code)
    image_general, image_products, image_payment = ReceiptBuilder.split_receipt_logical_parts(image_ekassa_gray)

    general_info = self.perform_ner_on_general_part(image_general)
    products = self.perform_ner_on_products_part(image_products)
    payment_info = self.perform_ner_on_payment_details_part(image_payment)

    receipt = Receipt(general_info, products, payment_info)
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

    for key, value in cashier_value_dict.items():
      results_dict[key] = value
    for key, value in date_time_value_dict.items():
      results_dict[key] = value

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

  def perform_ner_on_products_part(self, image_products):
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
    vertical_hist_normalized, horizontal_hist_normalized = ReceiptUtil.calculate_histograms(image_products)
    splitting_property = ApplicationProperties.splitting_properties.products_part_splitting_properties
    rect_xs_list = ReceiptUtil.determine_horizontal_splitting_rectangles(image_products, vertical_hist_normalized,
                   threshold_scale = splitting_property.threshold_scale, min_diff = splitting_property.min_difference)
    clear_products_part, clear_quantities_part, clear_prices_part, clear_amounts_part = ReceiptBuilder.segment_products_part(image_products, rect_xs_list)

    ocr_property = ApplicationProperties.ocr_properties.quantities_ocr_property
    quantities, df_quantities = ReceiptUtil.perform_ocr_obtain_values(image=clear_quantities_part,
                ocr_config=ocr_property.config, return_type = float, lang = ocr_property.lang)

    product_line_margin = ApplicationProperties.margin_properties.product_line_margin
    product_images = ReceiptUtil.prepare_product_images(clear_products_part, df_quantities,
                     quantities_image_height = clear_quantities_part.shape[0], product_line_margin = product_line_margin)
    product_names = ReceiptBuilder.extract_product_names(product_images)

    ocr_property = ApplicationProperties.ocr_properties.prices_ocr_property
    prices, _ = ReceiptUtil.perform_ocr_obtain_values(image=clear_prices_part,
                ocr_config=ocr_property.config, return_type = float, lang = ocr_property.lang)
    ocr_property = ApplicationProperties.ocr_properties.amounts_ocr_property
    amounts, _ = ReceiptUtil.perform_ocr_obtain_values(image=clear_amounts_part,
                ocr_config=ocr_property.config, return_type = float, lang = ocr_property.lang)

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