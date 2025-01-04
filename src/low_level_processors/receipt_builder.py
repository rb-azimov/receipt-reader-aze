from src.low_level_processors.receipt_util import ReceiptUtil


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
    rect_ys_list = ReceiptUtil.determine_vertical_splitting_rectangles(image, horizontal_hist_normalized, threshold_scale = 0.3, min_diff = 30)

    rect_ys_list = rect_ys_list[-2:] # Bypass useless, incorrect splits
    rect_ys_prod = rect_ys_list[0]
    rect_ys_total = rect_ys_list[1]

    image_general = image[:rect_ys_prod[0]-50, :] #[:-50,:]
    image_products = image[rect_ys_prod[0]:rect_ys_prod[1], :]
    image_total = image[rect_ys_total[0]:rect_ys_total[1]-160, :]

    return image_general, image_products, image_total

  @staticmethod
  def segment_cashier_date_time_part(image, df, selected_df):
    """
    Since general (upper) part of a receipt image has some inconsistencies
    in terms of line counts of values would differ, lower part of the upper one
    must be considered seperately.


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

    y_start = df.iloc[index].top - 2
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
        rects_xs_list: list of horizontal splitting rectangles
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
    rect_ys_list = ReceiptUtil.determine_vertical_splitting_rectangles(image_payment_details, horizontal_hist_normalized, threshold_scale = 0.5, min_diff = 30) # WARNING! 0.3

    index1, index2 = rect_ys_list[0][:2]
    payment_part = image_payment_details[:index1-5,:]
    payment_type_part = image_payment_details[index1+5:index2,:]

    return payment_part, payment_type_part
  # def segment_totals_part(image_total):
  # vertical_hist_normalized, horizontal_hist_normalized = calculate_histograms(image_total)
  # rect_ys_list = determine_vertical_splitting_rectangles(image_total, horizontal_hist_normalized, threshold_scale = 0.03, min_diff = 30)

  # index1, index2 = rect_ys_list[0][:2]

  # payment_part = image_total[:index1-5,:]
  # payment_type_part = image_total[index1+5:index2,:]

  # return payment_part, payment_type_part
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
    upper_letters = 'ABCÇDEƏFGĞHXIİJKQLMNOÖPRSŞTUÜVYZ'
    lower_letters = 'abcçdeəfgğhxıijkqlmnoöprsştuüvyz'
    azerbaijani_alphabet = upper_letters + lower_letters
    chartset = ' ' + '%_-' + azerbaijani_alphabet + '.0123456789'

    product_names = []
    for i in range(len(product_images)):
      product_image = product_images[i]

      # Perform OCR on {product_image}
      df_product = ReceiptUtil.perform_ocr(product_image, ocr_config = f'--psm 4 -c tessedit_char_whitelist={chartset}', lang = 'eng+aze')
      product_name = ' '.join(df_product.iloc[:-2].text.to_list())

      product_names.append(product_name)
    return product_names

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
    rect_xs_list = ReceiptUtil.determine_horizontal_splitting_rectangles(payment_part, vertical_hist_normalized, threshold_scale = 0.03, min_diff = 30)

    index1, index2 = rect_xs_list[0][1], rect_xs_list[-1][0]
    names_part = payment_part[:,:index1]
    values_part = payment_part[:,index2:]

    # Perform OCR on values part of the payment amount details
    df_values = ReceiptUtil.perform_ocr(values_part, ocr_config = '--psm 6 -c tessedit_char_whitelist=.0123456789')

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
    rect_xs_list = ReceiptUtil.determine_horizontal_splitting_rectangles(payment_type_part, vertical_hist_normalized, threshold_scale = 0.03, min_diff = 30)

    index1, index2 = rect_xs_list[0][1], rect_xs_list[-1][0]
    index1, index2 = index1 - 50, index2 - 50
    names_part = payment_type_part[:,:index1]
    values_part = payment_type_part[:,index2:]

    # charset = ':* '
    charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxvz'
    df_names = ReceiptUtil.perform_ocr(names_part, ocr_config = f'--psm 4 -c tessedit_char_whitelist={charset}', lang = 'eng')
    is_paid_cash = ReceiptUtil.is_payment_cash(df_names.text.to_list())

    values, _ = ReceiptUtil.perform_ocr_obtain_values(values_part, ocr_config = '--psm 6 -c tessedit_char_whitelist=.0123456789', return_type = float)
    cashless, cash, paid_cash, change, bonus, prepayment, credit = ReceiptUtil.distribute_values_in_payment_type(values, is_paid_cash)
    return cashless, cash, paid_cash, change, bonus, prepayment, credit