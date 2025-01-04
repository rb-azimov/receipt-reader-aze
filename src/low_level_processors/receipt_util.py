import cv2
import numpy as np
import pytesseract
from pytesseract import Output
import requests
import pandas as pd
from rapidfuzz import fuzz, process

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
    df = ReceiptUtil.perform_ocr(image, ocr_config, lang = None)
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

    product_lines_ys = []
    for i in range(1, df_quantities.shape[0]):
      y1, y2 = df_quantities.iloc[i-1].top, df_quantities.iloc[i].top
      product_lines_ys.append((y1-product_line_margin,y2))

    y1, y2 = df_quantities.iloc[-1].top, quantities_image_height
    product_lines_ys.append((y1-product_line_margin,y2))

    product_images = []
    for product_line_ys in product_lines_ys:
      y1, y2 = product_line_ys
      product_images.append(products_part[y1:y2,:])
    return product_images

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
        similiarity = fuzz.ratio(keyword, value)
        if similiarity >= similiarity_thresh:
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

    # Basic characteristics for OCR
    upper_letters = 'ABCÇDEƏFGĞHXIİJKQLMNOÖPRSŞTUÜVYZ'
    lower_letters = 'abcçdeəfgğhxıijkqlmnoöprsştuüvyz'
    azerbaijani_alphabet = upper_letters + lower_letters
    chartset = ' ' + '%_-№' + azerbaijani_alphabet + '.0123456789'

    # Extract text from the given image (image -> recognition df)
    df_general = ReceiptUtil.perform_ocr(image, ocr_config = f'--psm 6 -c tessedit_char_whitelist={chartset}', lang = 'eng+aze').reset_index(drop=True)

    df_general['MergedStrings'] = df_general['text'] + ' ' + df_general['text'].shift(-1)
    df_last_content = df_general.iloc[-1:]
    df = df_general.iloc[:-1]  # Drop the last row as it will contain NaN due to shifting

    # Focus on the rows searching keywords exist (recognition df -> selected rows)
    selected_rows_multi_token, keyword_token_counts_multi_token = ReceiptUtil.select_keyword_existed_rows(df = df, searched_col_name = 'MergedStrings',
                                                                                          keywords = multi_token_keywords, similiarity_thresh = 80)
    selected_rows_one_token, keyword_token_counts_one_token = ReceiptUtil.select_keyword_existed_rows(df = df, searched_col_name = 'text',
                                                                                          keywords = one_token_keywords, similiarity_thresh = 80)
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
  def is_payment_cash(texts, similiarity_thresh = 70):
    """
    Checks whether {texts} include keywords of cash type payment.

    Args:
        texts: str[]
        similiarity_thresh: int
        ...

    Returns:
        return: flag to determine payment type
    """
    keyword1, keyword2 = 'Paid cash:', 'Change:'
    is_keyword1_exist = False
    is_keyword2_exist = False
    for text in texts:
      if fuzz.ratio(keyword1, text) >= similiarity_thresh:
        is_keyword1_exist = True
      if fuzz.ratio(keyword2, text) >= similiarity_thresh:
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