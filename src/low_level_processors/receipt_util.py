import os

import cv2
import numpy as np
import pytesseract
from pytesseract import Output
import requests
import pandas as pd
from rapidfuzz import fuzz, process

from src.low_level_processors.application_properties_service import ApplicationPropertiesService
from src.low_level_processors.util import Util
from src.models.product import Product
from src.models.receipt import Receipt
from src.models.receipt_general_info import ReceiptGeneralInfo
from src.models.receipt_payment_info import ReceiptPaymentInfo
from src.models.receipt_product_list import ReceiptProductList
import os


class ReceiptUtil:
  """
  Class for utility/helper functions to
  acquire/preprocess image,
  prepare quantitative values for splitting images horizontally/vertically,
  perform OCR on images.

  Methods:
      read_image_from_ekassa(fiscal_code) -> obtains receipt image from ekassa.
      perform_ocr(image, ocr_config, lang = None) -> performs OCR on an image.
      perform_ocr_obtain_values(image, ocr_config, return_type, lang = None) -> performs OCR on an image and casts values to the given type.
      prepare_product_images(products_part, df_quantities, quantities_image_height, product_line_margin = 3) -> helps to segment
      product names image into images of seperate product names.
      select_keyword_existed_rows(df, searched_col_name, keywords, similiarity_thresh = 80) -> Helps to search for the keywords
          to obtain corresponding values in OCR results.
      extract_content_based_on_keywords(selected_df, df, df_last_content) -> Helps to find values among keywords.
      rule_based_text_extraction(image, multi_token_keywords, one_token_keywords) -> Searches one token and multi token keywords
          and the corresponding values.
      calculate_histograms(image, is_cleaning_applied = True) -> Calculates vertical and horizontal histograms.
      determine_horizontal_splitting_rectangles(image, vertical_hist_normalized,
          threshold_scale = 0.01, min_diff = 30) -> Determines horizontal splitting rectangles based on vertical histogram.
      determine_vertical_splitting_rectangles(image, horizontal_hist_normalized,
          threshold_scale = 0.03, min_diff = 30) -> Determines vertical splitting rectangles based on horizontal histogram.
      is_payment_cash(texts, similiarity_thresh = 70) -> Checks whether {texts} include keywords of cash type payment.
      distribute_values_in_payment_type(values, is_paid_cash) -> Distributes values based on payment type (cash vs cashless).

  """

  EXPORT_IMPORT_EXCEL = 3
  EXPORT_IMPORT_HTML = 4

  @staticmethod
  def read_image_from_ekassa(fiscal_code):
    """
    Obtains the receipt image corresponding to the given {fiscal_code}.

    Args:
        fiscal_code: str
        ...

    Returns:
        return: image_ekassa_gray
    """

    ekassa_image_url = f'https://monitoring.e-kassa.gov.az/pks-monitoring/2.0.0/documents/{fiscal_code}'
    response = requests.get(ekassa_image_url) # for EN: headers = {'user-lang': 'en'}
    image_data = np.frombuffer(response.content, np.uint8)
    image_ekassa = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
    image_ekassa_gray = cv2.cvtColor(image_ekassa, cv2.COLOR_BGR2GRAY)
    return image_ekassa_gray

  def perform_ocr(image, ocr_config, lang = None):
    """
    Reads text on an image using OCR.

    Args:
        image (numpy array)
        ocr_config (str)
        lang (str)
        ...

    Returns:
        return: data frame of OCR results

    """
    if lang is None:
      df = pd.DataFrame(pytesseract.image_to_data(image, config = ocr_config, output_type=Output.DICT))
    else:
      df = pd.DataFrame(pytesseract.image_to_data(image, lang = lang, config = ocr_config, output_type=Output.DICT))
    df = df[df.text.str.strip() != '']
    return df

  def perform_ocr_obtain_values(image, ocr_config, return_type, lang = None):
    """
    Reads text on an image using OCR.
    Casts values to the given type.

    Args:
        image (numpy array)
        ocr_config (str)
        return_type: type to cast values to
        lang (str)
        ...

    Returns:
        return: ready values,
                data frame of OCR results

    """
    df = ReceiptUtil.perform_ocr(image, ocr_config, lang = lang)
    values = [return_type(item) for item in df.text.to_list()]
    return values, df

  def prepare_product_images(products_part, df_quantities, quantities_image_height, product_line_margin = 3):
    """
    Helps to segment product names image into images of seperate product names.

    Args:
       products_part: image of the products part
       df_quantities: data frame that contains OCR results of quantities part
       quantities_image_height: height of the quantities part
       product_line_margin: int
       ...

    Returns:
        return: product_images
    """
    # print(df_quantities)
    product_lines_ys = []
    for i in range(1, df_quantities.shape[0]):
      y1, y2 = df_quantities.iloc[i-1].top, df_quantities.iloc[i].top
      # product_lines_ys.append((y1-product_line_margin,y2))
      product_lines_ys.append((max(y1-product_line_margin, 0),y2))

    y1, y2 = df_quantities.iloc[-1].top, quantities_image_height
    # product_lines_ys.append((y1-product_line_margin,y2))
    product_lines_ys.append((max(y1-product_line_margin, 0),y2))
    # print('Num lines:', len(product_lines_ys))
    # print(product_lines_ys)
    product_images = []
    for i in range(len(product_lines_ys)):
      product_line_ys = product_lines_ys[i]
      y1, y2 = product_line_ys
      product_image = products_part[y1:y2,:]
      product_images.append(product_image)
      if ApplicationPropertiesService.is_debug_on:
        ApplicationPropertiesService.logger.log_image(f'Product-{i + 1}', product_image)
    return product_images

  def prepare_price_images(prices_part, df_quantities, quantities_image_height, price_line_margin = 3):
    """
    Helps to segment price names image into images of seperate price names.

    Args:
       prices_part: image of the prices part
       df_quantities: data frame that contains OCR results of quantities part
       quantities_image_height: height of the quantities part
       price_line_margin: int
       ...

    Returns:
        return: price_images
    """

    price_lines_ys = []
    for i in range(1, df_quantities.shape[0]):
      y1, y2 = df_quantities.iloc[i-1].top, df_quantities.iloc[i].top
      # print(y1, y2)
      price_lines_ys.append((y1-price_line_margin,y2))

    y1, y2 = df_quantities.iloc[-1].top, quantities_image_height
    # print(y1, y2)
    price_lines_ys.append((y1-price_line_margin,y2))
    # print('Num lines:', len(price_lines_ys))
    price_images = []
    for i in range(len(price_lines_ys)):
      price_line_ys = price_lines_ys[i]
      y1, y2 = price_line_ys
      # print(y1, y2)
      price_image = prices_part[y1:y2,:]
      price_images.append(price_image)
      if ApplicationPropertiesService.is_debug_on:
        ApplicationPropertiesService.logger.log_image(f'price-{i + 1}', price_image)
    return price_images

  def prepare_amount_images(amounts_part, df_quantities, quantities_image_height, amount_line_margin = 3):
    """
    Helps to segment amount names image into images of seperate amount names.

    Args:
       amounts_part: image of the amounts part
       df_quantities: data frame that contains OCR results of quantities part
       quantities_image_height: height of the quantities part
       amount_line_margin: int
       ...

    Returns:
        return: amount_images
    """

    amount_lines_ys = []
    for i in range(1, df_quantities.shape[0]):
      y1, y2 = df_quantities.iloc[i-1].top, df_quantities.iloc[i].top
      # print(y1, y2)
      amount_lines_ys.append((y1-amount_line_margin,y2))

    y1, y2 = df_quantities.iloc[-1].top, quantities_image_height
    # print(y1, y2)
    amount_lines_ys.append((y1-amount_line_margin,y2))
    # print('Num lines:', len(amount_lines_ys))
    amount_images = []
    for i in range(len(amount_lines_ys)):
      amount_line_ys = amount_lines_ys[i]
      y1, y2 = amount_line_ys
      # print(y1, y2)
      amount_image = amounts_part[y1:y2,:]
      amount_images.append(amount_image)
      if ApplicationPropertiesService.is_debug_on:
        ApplicationPropertiesService.logger.log_image(f'amount-{i + 1}', amount_image)
    return amount_images

  @staticmethod
  def select_keyword_existed_rows(df, searched_col_name, keywords, similiarity_thresh = 80):
    """
    Helps to search for the keywords to obtain corresponding values in OCR results.

    Args:
        df: data frame that contains raw OCR results.
        searched_col_name: specifies one vs multitoken keyword search
        keywords: list of keywords
        similiarity_thresh: threshold value to determine whether a match is found
        ...

    Returns:
        return: selected_rows, keyword_token_counts

    """
    selected_rows = []
    keyword_token_counts = []
    for keyword in keywords:
      for index, value in df[searched_col_name].items():
        similarity_score = fuzz.ratio(keyword, value)
        if similarity_score >= similiarity_thresh:
            selected_rows.append((index, keyword, value))
            token_count = len(keyword.split(' '))
            keyword_token_counts.append(token_count)
    return selected_rows, keyword_token_counts

  @staticmethod
  def extract_content_based_on_keywords(selected_df, df, df_last_content):
    """
    Helps to find values among keywords.

    Args:
        selected_df: keyword searching results
        df: OCR results in the general part of the receipt image
        df_last_content: results of the last searched keyword
        ...

    Returns:
        return: results_dict (keyword : searched value)

    """
    results_dict = {}
    for i in range(selected_df.shape[0] - 1):
      index, keyword, matched_string, keyword_token_count = selected_df.iloc[i]
      next_index, next_keyword, next_matched_string, next_keyword_token_count = selected_df.iloc[i+1]

      temp = df.iloc[index + keyword_token_count:next_index]
      value = ' '.join(temp.text.to_list())
      results_dict[keyword.replace(':', '')] = value

    index, keyword, matched_string, keyword_token_count = selected_df.iloc[-1]
    temp = pd.concat([df, df_last_content], axis = 0).drop('MergedStrings', axis = 1).iloc[index + keyword_token_count:]
    value = ' '.join([str(item) for item in temp.text.to_list()])
    results_dict[keyword.replace(':', '')] = value
    return results_dict

  @staticmethod
  def rule_based_text_extraction(image, multi_token_keywords, one_token_keywords):
    """
    Searches one token and multi token keywords and the corresponding values.

    Args:
        image (numpy array): image that keywords are searched in
        multi_token_keywords
        one_token_keywords
        ...

    Returns:
        return: results_dict, df, selected_df

    """
    if multi_token_keywords is None:
      multi_token_keywords = []
    if one_token_keywords is None:
      one_token_keywords = []

    # Extract text from the given image (image -> recognition df)
    ocr_property = ApplicationPropertiesService.ocr_properties.general_part_ocr_property
    df_general = ReceiptUtil.perform_ocr(image, ocr_config = ocr_property.config , lang = ocr_property.lang).reset_index(drop=True)

    df_general['MergedStrings'] = df_general['text'] + ' ' + df_general['text'].shift(-1)
    df_last_content = df_general.iloc[-1:]
    df = df_general.iloc[:-1]  # Drop the last row as it will contain NaN due to shifting

    # Focus on the rows searching keywords exist (recognition df -> selected rows)
    multi_token_text_similarity_threshold = ApplicationPropertiesService.text_similarity_threshold_properties.multi_token_text_similarity_threshold
    selected_rows_multi_token, keyword_token_counts_multi_token = ReceiptUtil.select_keyword_existed_rows(df = df, searched_col_name = 'MergedStrings',
                                                                  keywords = multi_token_keywords, similiarity_thresh = multi_token_text_similarity_threshold)
    one_token_text_similarity_threshold = ApplicationPropertiesService.text_similarity_threshold_properties.one_token_text_similarity_threshold
    selected_rows_one_token, keyword_token_counts_one_token = ReceiptUtil.select_keyword_existed_rows(df = df, searched_col_name = 'text',
                                                              keywords = one_token_keywords, similiarity_thresh = one_token_text_similarity_threshold)
    selected_rows = selected_rows_multi_token + selected_rows_one_token
    keyword_token_counts = keyword_token_counts_multi_token + keyword_token_counts_one_token

    if len(selected_rows) == 0:
      return {}

    selected_df = pd.DataFrame(selected_rows, columns=['Index', 'Keyword', 'MatchedString'])
    selected_df['KeywordTokenCount'] = keyword_token_counts
    selected_df = selected_df.sort_values(by='Index').reset_index(drop=True)

    # Obtain values corresponding to the given keywords in the recognition results
    results_dict = ReceiptUtil.extract_content_based_on_keywords(selected_df, df, df_last_content)

    return results_dict, df, selected_df

  @staticmethod
  def calculate_histograms(image, is_cleaning_applied = True):
    """
    Calculates vertical and horizontal histograms.

    Args:
        image (numpy array): image of which vertical, horizontal histograms calculated
        is_cleaning_applied: flag to determine whether image preprocessing is to be applied
    """

    if is_cleaning_applied:
      sobel_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)  # Horizontal edges
      sobel_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)  # Vertical edges
      sobel_magnitude = cv2.magnitude(sobel_x, sobel_y)
      sobel_magnitude = cv2.convertScaleAbs(sobel_magnitude)
      image = 255-sobel_magnitude # extracted_num_part
      image = cv2.medianBlur(image, 5)

    vertical_hist = np.sum(image, axis=0)
    horizontal_hist = np.sum(image, axis=1)

    vertical_hist_normalized = vertical_hist / max(vertical_hist) * image.shape[0]
    horizontal_hist_normalized = horizontal_hist / max(horizontal_hist) * image.shape[1]
    return vertical_hist_normalized, horizontal_hist_normalized

  @staticmethod
  def determine_horizontal_splitting_rectangles(image, vertical_hist_normalized, threshold_scale = 0.01, min_diff = 30):
    """
    Determines horizontal splitting rectangles based on vertical histogram.

    Args:
        image (numpy array): image to be splitted
        vertical_hist_normalised: average values of non-white pixels along the width
        threshold_scale: scales the threshold to determine borders of the objects
        min_diff: parameter to filter useless small segments
        ...

    Returns:
        return: list of horizontal splitting rectangles

    """
    threshold = threshold_scale * image.shape[0]
    indices = np.where((image.shape[0] - vertical_hist_normalized) < threshold)[0]

    # IS_TO_BE_DELETED!
    # print('Threshold scale:', threshold_scale)
    # print('image.shape[0]:', image.shape[0])
    # print('Threshold:', threshold)
    # print('Vertical histogram (normalized):', vertical_hist_normalized)
    # print('Indices:', indices)

    result = [indices[i] for i in range(len(indices) - 1) if indices[i + 1] != indices[i] + 1]
    result.append(indices[-1])  # Add the last element since it always ends a sequence
    result = np.array(result)
    indices = result

    # Determine rectangle parameters
    y_start, y_end = 0, image.shape[0]
    img_height = image.shape[0]
    img_width = image.shape[1]
    n = len(indices)
    rect_height = image.shape[0]
    rect_xs_list = []
    for i in range(n - 1):
      rect_xs = (indices[i], indices[i+1])
      rect_xs_list.append(rect_xs)
    rect_xs_list = [pair for pair in rect_xs_list if abs(pair[1] - pair[0]) >= min_diff]
    return rect_xs_list

  @staticmethod
  def determine_vertical_splitting_rectangles(image, horizontal_hist_normalized, threshold_scale = 0.03, min_diff = 30):
    """
    Determines vertical splitting rectangles based on horizontal histogram.

    Args:
        image (numpy array): image to be splitted
        horizontal_hist_normalised: average values of non-white pixels along the height
        threshold_scale: scales the threshold to determine borders of the objects
        min_diff: parameter to filter useless small segments
        ...

    Returns:
        return: list of vertical splitting rectangles

    """
    threshold = threshold_scale * image.shape[1] # WARNING! 0.3
    indices = np.where(image.shape[1] - horizontal_hist_normalized > threshold)[0]

    x_start, x_end = 0, image.shape[1]
    img_height = image.shape[0]
    img_width = image.shape[1]

    n = len(indices)
    rect_width = image.shape[1]
    rect_ys_list = []
    for i in range(n - 1):
      rect_ys = (indices[i], indices[i+1])
      rect_ys_list.append(rect_ys)
    rect_ys_list = [pair for pair in rect_ys_list if abs(pair[1] - pair[0]) >= min_diff]

    return rect_ys_list

  @staticmethod
  def is_payment_cash(texts, similarity_thresh = 70):
    """
    Checks whether {texts} include keywords of cash type payment.

    Args:
        texts: str[]
        similarity_thresh: int
        ...

    Returns:
        return: flag to determine payment type
    """
    keyword1, keyword2 = 'Paid cash:', 'Change:'
    is_keyword1_exist = False
    is_keyword2_exist = False
    for text in texts:
      if fuzz.ratio(keyword1, text) >= similarity_thresh:
        is_keyword1_exist = True
      if fuzz.ratio(keyword2, text) >= similarity_thresh:
        is_keyword2_exist = True
    if is_keyword1_exist and is_keyword2_exist:
      return True
    return False

  def distribute_values_in_payment_type(values, is_paid_cash):
    """
    Distributes values based on payment type (cash vs cashless).

    Args:
        values: list of numbers
        is_paid_cash: flag to determine payment type
        ...

    Returns:
        return: cashless, cash, paid_cash, change, bonus, prepayment, credit
    """
    cashless = values[0]
    cash = values[1]
    if is_paid_cash:
      paid_cash = values[2]
      change = values[3]
      bonus = values[4]
      prepayment = values[5]
      credit = values[6]
    else:
      paid_cash = 0
      change = 0
      bonus = values[2]
      prepayment = values[3]
      credit = values[4]
    return cashless, cash, paid_cash, change, bonus, prepayment, credit

  # def preprocess_to_real_number(text):
  #   if text[-1] == '.':
  #     text = text[:-1]
  #   if text[0] == '.':
  #     text = text[1:]
  #   return text

  def preprocess_to_real_number(input_string):
    parts = input_string.split('.')
    parts = [part for part in parts if part]
    real_number = ''.join(parts[:1]) + '.' + ''.join(parts[1:])
    return real_number

  @staticmethod
  def export_receipts(receipts, receipt_image_paths = None, export_option=None):
    if export_option is None:
      export_option = ReceiptUtil.EXPORT_IMPORT_EXCEL
    if export_option == ReceiptUtil.EXPORT_IMPORT_EXCEL:
      return ReceiptUtil._export_receipts_to_excel(receipts)
    elif export_option == ReceiptUtil.EXPORT_IMPORT_HTML:
      return ReceiptUtil._export_receipts_to_HTML(receipts, receipt_image_paths)
    raise ValueError("No valid import/export option was selected!")

  @staticmethod
  def _export_receipts_to_excel(receipts):
    df_general_info_payments = pd.DataFrame(columns=[
      'FiscalCode', 'ObjName', 'Address', 'ObjCode',
      'TaxPayer', 'TIN', 'ReceiptID', 'Cashier',
      'Date', 'Time', 'TotalAmount', 'TaxAmount',
      'NonTaxAmount', 'Cashless', 'Cash', 'PaidCash',
      'Change', 'Bonus', 'PrePayment', 'Credit',
    ])
    df_products = pd.DataFrame(columns=[
      'FiscalCode', 'ProductName', 'Quantity', 'Price', 'Amount'
    ])

    for i in range(len(receipts)):
      receipt = receipts[i]
      general_info = receipt.general_info
      products = receipt.product_list.products
      payment_info = receipt.payment_info
      fiscal_code = receipt._fiscal_code
      print('Code:', fiscal_code)
      df_general_info_payments.loc[len(df_general_info_payments)] = [
        fiscal_code, general_info.name, general_info.address, general_info.code,
        general_info.tax_payer_name, general_info.TIN, general_info.sale_receipt_num, general_info.cashier_name,
        general_info.date, general_info.time, payment_info.total_amount, payment_info.tax_amount,
        payment_info.non_tax_amount, payment_info.cashless_payment_amount, payment_info.cash_payment_amount, payment_info.paid_cash_amount,
        payment_info.change_cash_amount, payment_info.bonus, payment_info.prepayment, payment_info.credit
      ]

      for product in products:
        df_products.loc[len(df_products)] = [
          fiscal_code, product.name, product.quantity, product.price, product.amount
        ]
    folder_name = os.path.join(
      ApplicationPropertiesService.logger.output_dir,
      'overal_data'
    )
    date_time = Util.prepare_current_datetime()
    file_general_payment = os.path.join(
      folder_name,
      f'{date_time}_general-info_payment.xlsx'
    )
    file_products = os.path.join(
      folder_name,
      f'{date_time}_products.xlsx'
    )
    df_general_info_payments.to_excel(file_general_payment, index=False)
    df_products.to_excel(file_products, index=False)

  def _export_receipts_to_HTML(receipts, receipt_image_paths):
    """
    Creates an HTML page with receipts displayed in tabular format, showing both the image and the corresponding content string.

    Args:
        receipt_images (list of str): List of file paths to receipt images.
        receipts (list of str): List of receipt content strings.
        pdf_file_path (str): Output PDF file path.
    """
    receipt_image_paths = [os.path.join(os.getcwd(), path) for path in receipt_image_paths]
    folder_name = os.path.join(
      ApplicationPropertiesService.logger.output_dir,
      'overal_data'
    )
    date_time = Util.prepare_current_datetime()
    html_file_path = os.path.join(
      folder_name,
      f'{date_time}_results.html'
    )

    if len(receipt_image_paths) != len(receipts):
      raise ValueError("The number of receipt images and receipt content strings must match.")

    html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Receipt OCR Report</title>
            <style>
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                    border-spacing: 0 10px;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    vertical-align: top;
                    text-align: left;
                }
                <!-- vertical-align: middle;-->
                th {
                    background-color: #f4f4f4;
                }
                img {
                    max-width: 300px;
                    height: auto;
                }
                .container {
                    margin: 20px;
                    font-family: Arial, sans-serif;
                }
                .heading {
                    text-align: center;
                    margin-bottom: 20px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="heading">Receipt OCR Report</h1>
                <table>
                    <thead>
                        <tr>
                            <th>Receipt Image</th>
                            <th>Extracted Text</th>
                        </tr>
                    </thead>
                    <tbody>
        """

    # Add rows for each image-text pair
    for image_path, text in zip(receipt_image_paths, receipts):
      html_content += f"""
            <tr>
                <td><img src="{image_path}" alt="Receipt Image"></td>
                <td><pre>{text}</pre></td>
            </tr>
            """

    # Close the HTML tags
    html_content += """
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
    # Write the content to the output file
    with open(html_file_path, "w", encoding="utf-8") as file:
      file.write(html_content)
    return html_file_path

  @staticmethod
  def import_receipts(date_time, import_option=None):
    if import_option is None:
      import_option = ReceiptUtil.EXPORT_IMPORT_EXCEL
    if import_option == ReceiptUtil.EXPORT_IMPORT_EXCEL:
      return ReceiptUtil._import_receipts_from_excel(date_time)

  @staticmethod
  def _import_receipts_from_excel(date_time):
    folder_name = os.path.join(
      ApplicationPropertiesService.logger.output_dir,
      'overal_data'
    )
    file_general_payment = os.path.join(
      folder_name,
      f'{date_time}_general-info_payment.xlsx'
    )
    file_products = os.path.join(
      folder_name,
      f'{date_time}_products.xlsx'
    )
    df_general_info_payments = pd.read_excel(file_general_payment)
    df_products = pd.read_excel(file_products)

    fiscal_codes = df_general_info_payments.FiscalCode.to_list()
    receipts = []

    for fiscal_code in fiscal_codes:
      row = df_general_info_payments[df_general_info_payments.FiscalCode == fiscal_code].iloc[0]
      general_info = ReceiptGeneralInfo(
        row.ObjName, row.Address, row.ObjCode,
        row.TaxPayer, row.TIN, row.ReceiptID, row.Cashier,
        row.Date, row.Time
      )
      payment_info = ReceiptPaymentInfo(
        row.TotalAmount, row.TaxAmount,
        row.NonTaxAmount, row.Cashless, row.Cash, row.PaidCash,
        row.Change, row.Bonus, row.PrePayment, row.Credit,
      )
      product_rows = df_products[df_products.FiscalCode == fiscal_code]
      products = []
      for index in range(len(df_products)):
        row = df_products.iloc[index]
        product = Product(
          row.ProductName, row.Quantity, row.Price, row.Amount
        )
        products.append(product)
      product_list = ReceiptProductList(products)

      receipt = Receipt(
        general_info, product_list, payment_info
      )
      receipt._fiscal_code = fiscal_code
      receipts.append(receipt)
    return receipts
