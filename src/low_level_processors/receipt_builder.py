import warnings

import cv2

from src.low_level_processors.application_properties_service import ApplicationPropertiesService
from src.low_level_processors.receipt_util import ReceiptUtil
from src.low_level_processors.util import Util


class ReceiptBuilder:
  """
    Class for building high level architecture in receipt OCR and NER
    between ReceiptService and ReceiptUtil classes.

    Methods:
        split_receipt_logical_parts(image) -> splits receipt image into general, products, payments parts.
        segment_products_part(image, rect_xs_list) -> splits products part of the receipt image
                                                      into names, quantities, prices, amounts parts.
        segment_payment_details_part(image_payment_details) -> splits payment details part of the receipt image
                                                               into payment amount and payment type parts.
        extract_product_names(product_images) -> performs OCR on each of the images to obtain product_names.
        extract_values_from_payment_part(payment_part) -> processes payment part of the lower (payments and payment type details)
                                                            of the receipt image to obtain total payment amounts.
        extract_values_from_payment_type_part(payment_type_part) -> processes payment type part of the lower (payments and payment type details)
                                                                  of the receipt image to obtain cashless, cash, paid_cash, change, bonus, prepayment, credit values.
  """

  warnings.simplefilter("always", UserWarning)

  @staticmethod
  def split_receipt_logical_parts(image):
    """
    Takes receipt image and splits it
    into general, products, payments parts.
    Calls calculation of horizontal histograms,
    determining vertical splitting rectangles.

    Args:
        image (numpy array): image of a receipt
        ...

    Returns:
        return: image_general, image_products, image_total
    """

    _, horizontal_hist_normalized = ReceiptUtil.calculate_histograms(image, is_cleaning_applied = False)
    splitting_property = ApplicationPropertiesService.splitting_properties.receipt_logical_splitting_property
    rect_ys_list = ReceiptUtil.determine_vertical_splitting_rectangles(image, horizontal_hist_normalized,
                    threshold_scale = splitting_property.threshold_scale, min_diff = splitting_property.min_difference)

    rect_ys_list = rect_ys_list[-2:] # Bypass useless, incorrect splits
    rect_ys_prod = rect_ys_list[0]
    rect_ys_total = rect_ys_list[1]

    general_part_bottom_margin = ApplicationPropertiesService.margin_properties.general_part_bottom_margin
    payment_part_bottom_margin = ApplicationPropertiesService.margin_properties.payment_part_bottom_margin
    image_general = image[:rect_ys_prod[0] - general_part_bottom_margin, :]
    image_products = image[rect_ys_prod[0]:rect_ys_prod[1], :]
    image_total = image[rect_ys_total[0]:rect_ys_total[1] - payment_part_bottom_margin, :]

    # Print part between general info and products for debug
    index1 = rect_ys_prod[0] - general_part_bottom_margin + 25
    index2 = rect_ys_prod[0]
    product_column_names_part = image[index1:index2,:]
    ApplicationPropertiesService.logger.log_image_for_debug(
      'product_column_names_part', product_column_names_part
    )
    # charset = "ProductQinycealT "
    # config = f'--psm 7 -c tessedit_char_whitelist={charset}'
    config = f'--psm 7'
    values, df = ReceiptUtil.perform_ocr_obtain_values(product_column_names_part,
                                          ocr_config = config, return_type=str, lang=None)
    # print(values)
    # print(df[['left', 'top', 'width', 'height', 'text']])
    PRODUCT, QUANTITY, PRICE, TOTAL = 'Product', 'Quantity', 'Price', 'Total'

    left_product = df[df.text == PRODUCT].iloc[0].left
    width_product = df[df.text == PRODUCT].iloc[0].width
    left_quantity = df[df.text == QUANTITY].iloc[0].left
    width_quantity = df[df.text == QUANTITY].iloc[0].width
    left_price = df[df.text == PRICE].iloc[0].left
    width_price = df[df.text == PRICE].iloc[0].width
    left_total = df[df.text == TOTAL].iloc[0].left
    width_total = df[df.text == TOTAL].iloc[0].width

    product_part_rect_xs_list = [
      (0, left_quantity),
      (left_quantity, left_price),
      (left_price, left_total),
      (left_total, image.shape[1]),
    ]
    # top_left = (left_quantity, 0)  # (x1, y1) coordinates
    # bottom_right = (left_price, product_column_names_part.shape[0])  # (x2, y2) coordinates
    # color = (0, 0, 255)  # Red color
    # thickness = 1  # Thickness of the rectangle border
    # cv2.rectangle(product_column_names_part, top_left, bottom_right, color, thickness)
    # ApplicationPropertiesService.logger.log_image_for_debug(
    #   'labeled_product_column_names_part', product_column_names_part
    # )
    return image_general, image_products, image_total, product_part_rect_xs_list

  @staticmethod
  def segment_cashier_date_time_part(image, df, selected_df):
    """
    Since general (upper) part of a receipt image has some inconsistencies
    in terms of line counts of values would differ, lower part of the upper one
    must be considered separately.


    Args:
        image (numpy array): image of the general (upper) part of a receipt
        df: raw OCR results data frame of the general part
        selected_df: selected rows of focus in terms of searched keywords
        ...

    Returns:
        return: cashier_part_image, date_time_part_image
                of the lower part of the receipt image
    """

    cashier_keyword = 'Cashier:' # Used to note the splitting location of the general part
    index, keyword, matched_string, keyword_token_count = selected_df[selected_df.Keyword == cashier_keyword].iloc[0]

    cashier_date_time_top_margin = ApplicationPropertiesService.margin_properties.cashier_date_time_top_margin
    y_start = df.iloc[index].top - cashier_date_time_top_margin
    cashier_part_image = image[y_start:,:image.shape[1] // 2]
    date_time_part_image = image[y_start:,image.shape[1] // 2:]

    return cashier_part_image, date_time_part_image

  @staticmethod
  def segment_products_part(image, rect_xs_list):
    """
    Takes product part of the receipt image and horizontally
    splits into product names, quantities, prices, amounts parts.

    Args:
        image (numpy array): image of the products (middle) part of a receipt
        rect_xs_list: list of horizontal splitting rectangles
        ...

    Returns:
        return: cashier_part_image, date_time_part_image
                of the lower part of the receipt image
    """
    horizontal_parts = []
    y_start, y_end = 0, image.shape[0]
    for rect_xs in rect_xs_list: # WARNING!
      x_start, x_end = rect_xs
      horizontal_parts.append(image[y_start:y_end, x_start:x_end])

    product_names_part = horizontal_parts[0]
    quantities_part = horizontal_parts[-3]
    prices_part = horizontal_parts[-2]
    amounts_part = horizontal_parts[-1]
    return product_names_part, quantities_part, prices_part, amounts_part

  @staticmethod
  def segment_payment_details_part(image_payment_details):
    """
    Splits payment details part into payment amount and payment type parts.

    Args:
        image_payment_details (numpy array): payment details (lower) part of the receipt image
        ...

    Returns:
        return: payment_part, payment_type_part
    """
    vertical_hist_normalized, horizontal_hist_normalized = ReceiptUtil.calculate_histograms(image_payment_details)
    splitting_property = ApplicationPropertiesService.splitting_properties.payment_to_amount_type_splitting_property
    rect_ys_list = ReceiptUtil.determine_vertical_splitting_rectangles(image_payment_details, horizontal_hist_normalized,
                   threshold_scale = splitting_property.threshold_scale, min_diff = splitting_property.min_difference) # WARNING! 0.3

    index1, index2 = rect_ys_list[0][:2]
    payment_amount_part_margin = ApplicationPropertiesService.margin_properties.payment_amount_part_margin
    payment_part = image_payment_details[:index1 - payment_amount_part_margin,:]
    payment_type_part = image_payment_details[index1 + payment_amount_part_margin:index2,:]

    return payment_part, payment_type_part

  @staticmethod
  def extract_product_names(product_images):
    """
    Performs OCR on each of the images to obtain
    product_names.

    Args:
        product_images (list): list of product images
        ...

    Returns:
        return: product_names
    """

    product_names = []
    for i in range(len(product_images)):
      product_image = product_images[i]
      ocr_property = ApplicationPropertiesService.ocr_properties.product_names_ocr_property
      df_product = ReceiptUtil.perform_ocr(product_image, ocr_config = ocr_property.config, lang = ocr_property.lang)
      product_name = ' '.join(df_product.iloc[:-2].text.to_list())

      # Remove redundant (pc) like things
      product_name = product_name.replace(' (pc)', '')
      product_names.append(product_name)
    return product_names

  @staticmethod
  def extract_prices(price_images):
    """
    Performs OCR on each of the images to obtain
    price_names.

    Args:
        price_images (list): list of price images
        ...

    Returns:
        return: price_names
    """

    prices = []
    for i in range(len(price_images)):
      price_image = price_images[i]
      ocr_property = ApplicationPropertiesService.ocr_properties.prices_ocr_property
      df_price = ReceiptUtil.perform_ocr(price_image, ocr_config='--psm 8 -c tessedit_char_whitelist=.0123456789', lang=None)
      price = ''.join(df_price.iloc[:].text.to_list())
      price = ReceiptUtil.preprocess_to_real_number(price)
      try:
        price = Util.clean_and_convert_to_float(price)
      except ValueError:
        text = ReceiptUtil.perform_ocr_on_single_item_image(price_image)
        if len(text) != 0:
          price = float(text)
        else:
          price = -1
          warnings.warn('Non-float value error supressed with `-1` {price}', UserWarning)
      prices.append(price)
    return prices

  @staticmethod
  def extract_amounts(amount_images):
    """
    Performs OCR on each of the images to obtain
    amount_images.

    Args:
        amount_images (list): list of price images
        ...

    Returns:
        return: amount_names
    """

    amounts = []
    for i in range(len(amount_images)):
      amount_image = amount_images[i]
      ocr_property = ApplicationPropertiesService.ocr_properties.prices_ocr_property
      df_amount = ReceiptUtil.perform_ocr(amount_image, ocr_config='--psm 8 -c tessedit_char_whitelist=.0123456789',
                                         lang=None)
      amount = ''.join(df_amount.iloc[:].text.to_list())
      amount = ReceiptUtil.preprocess_to_real_number(amount)
      try:
        amount = Util.clean_and_convert_to_float(amount)
      except ValueError:
        text = ReceiptUtil.perform_ocr_on_single_item_image(amount_image)
        if len(text) != 0:
          amount = float(text)
        else:
          amount = -1
          warnings.warn('Non-float value error supressed with `-1` {amount}', UserWarning)
      amounts.append(amount)
    return amounts

  @staticmethod
  def extract_values_from_payment_part(payment_part):
    """
    Processes payment part of the lower (payments and payment type details)
    of the receipt image to obtain total payment amounts.

    Args:
        payment_part (numpy array): payment part of the receipt image
        ...

    Returns:
        return: total_amount_standalone, non_tax_amount, tax_amount
    """
    # Split {payment_part} into names and values images (totally 2)
    vertical_hist_normalized, horizontal_hist_normalized = ReceiptUtil.calculate_histograms(payment_part)
    splitting_property = ApplicationPropertiesService.splitting_properties.payment_amount_to_name_value_splitting_property
    rect_xs_list = ReceiptUtil.determine_horizontal_splitting_rectangles(payment_part, vertical_hist_normalized,
                    threshold_scale = splitting_property.threshold_scale, min_diff = splitting_property.min_difference)

    index1, index2 = rect_xs_list[0][1], rect_xs_list[-1][0]
    # Remained for possible need for usage: names_part = payment_part[:,:index1]
    values_part = payment_part[:,index2:]

    # Perform OCR on values part of the payment amount details
    ocr_property = ApplicationPropertiesService.ocr_properties.payment_amount_part_ocr_property
    df_values = ReceiptUtil.perform_ocr(values_part, ocr_config = ocr_property.config, lang = ocr_property.lang)

    # Extract the needed total payment numbers
    total_amount_standalone = float(df_values.iloc[0].text)
    non_tax_amount = float(df_values.iloc[1].text)
    tax_amount = total_amount_standalone - non_tax_amount
    return total_amount_standalone, non_tax_amount, tax_amount

  @staticmethod
  def extract_values_from_payment_type_part(payment_type_part):
    """
    Processes payment type part of the lower (payments and payment type details)
    of the receipt image to obtain cashless, cash, paid_cash, change, bonus, prepayment, credit values.

    Args:
        payment_type_part (numpy array): payment type part of the receipt image
        ...

    Returns:
        return: cashless, cash, paid_cash, change, bonus, prepayment, credit
    """
    vertical_hist_normalized, horizontal_hist_normalized = ReceiptUtil.calculate_histograms(payment_type_part)
    splitting_property = ApplicationPropertiesService.splitting_properties.payment_type_to_name_value_splitting_property
    rect_xs_list = ReceiptUtil.determine_horizontal_splitting_rectangles(payment_type_part, vertical_hist_normalized,
                   threshold_scale = splitting_property.threshold_scale, min_diff = splitting_property.min_difference)

    payment_type_name_value_margin = ApplicationPropertiesService.margin_properties.payment_type_name_value_margin
    index1, index2 = rect_xs_list[0][1], rect_xs_list[-1][0]
    index1, index2 = index1 - payment_type_name_value_margin, index2 - payment_type_name_value_margin
    names_part = payment_type_part[:,:index1]
    values_part = payment_type_part[:,index2:]

    ocr_property = ApplicationPropertiesService.ocr_properties.payment_type_part_names_ocr_property
    df_names = ReceiptUtil.perform_ocr(names_part, ocr_config = ocr_property.config, lang = ocr_property.lang)

    payment_type_checking_text_similarity_threshold = ApplicationPropertiesService.text_similarity_threshold_properties.payment_type_checking_text_similarity_threshold
    is_paid_cash = ReceiptUtil.is_payment_cash(df_names.text.to_list(), similarity_thresh=payment_type_checking_text_similarity_threshold)

    ocr_property = ApplicationPropertiesService.ocr_properties.payment_type_part_numbers_ocr_property
    values, _ = ReceiptUtil.perform_ocr_obtain_values(values_part, ocr_config = ocr_property.config, return_type = float, lang = ocr_property.lang)
    cashless, cash, paid_cash, change, bonus, prepayment, credit = ReceiptUtil.distribute_values_in_payment_type(values, is_paid_cash)
    return cashless, cash, paid_cash, change, bonus, prepayment, credit