class Property:
    pass

class OCRProperty(Property):
    def __init__(self, config, lang):
        self.config = config
        self.lang = lang

class SplittingProperty(Property):
    def __init__(self, threshold_scale, min_difference):
        self.threshold_scale = threshold_scale
        self.min_difference = min_difference

class Properties:
    pass

class OCRProperties(Properties):
    def __init__(self,
                 general_part_ocr_property,
                 product_names_ocr_property,
                 quantities_ocr_property,
                 prices_ocr_property,
                 amounts_ocr_property,
                 payment_amount_part_ocr_property,
                 payment_type_part_names_ocr_property,
                 payment_type_part_numbers_ocr_property):
        self.general_part_ocr_property = general_part_ocr_property
        self.product_names_ocr_property = product_names_ocr_property
        self.quantities_ocr_property = quantities_ocr_property
        self.prices_ocr_property = prices_ocr_property
        self.amounts_ocr_property = amounts_ocr_property
        self.payment_amount_part_ocr_property = payment_amount_part_ocr_property
        self.payment_type_part_names_ocr_property = payment_type_part_names_ocr_property
        self.payment_type_part_numbers_ocr_property = payment_type_part_numbers_ocr_property

class SplittingProperties(Properties):
    def __init__(self,
                 receipt_logical_splitting_property,
                 payment_to_amount_type_splitting_property,
                 payment_amount_to_name_value_splitting_property,
                 payment_type_to_name_value_splitting_property,
                 products_part_splitting_properties):
        self.receipt_logical_splitting_property = receipt_logical_splitting_property
        self.payment_to_amount_type_splitting_property = payment_to_amount_type_splitting_property
        self.payment_amount_to_name_value_splitting_property = payment_amount_to_name_value_splitting_property
        self.payment_type_to_name_value_splitting_property = payment_type_to_name_value_splitting_property
        self.products_part_splitting_properties = products_part_splitting_properties

class MarginProperties(Properties):
    def __init__(self,
                 product_line_margin,
                 general_part_bottom_margin,
                 payment_part_bottom_margin,
                 cashier_date_time_top_margin,
                 payment_amount_part_margin,
                 payment_type_name_value_margin):
        self.product_line_margin = product_line_margin
        self.general_part_bottom_margin = general_part_bottom_margin
        self.payment_part_bottom_margin = payment_part_bottom_margin
        self.cashier_date_time_top_margin = cashier_date_time_top_margin
        self.payment_amount_part_margin = payment_amount_part_margin
        self.payment_type_name_value_margin = payment_type_name_value_margin

class TextSimilarityThresholdProperties(Properties):
    def __init__(self,
                 payment_type_checking_text_similarity_threshold,
                 multi_token_text_similarity_threshold,
                 one_token_text_similarity_threshold):
        self.payment_type_checking_text_similarity_threshold = payment_type_checking_text_similarity_threshold
        self.multi_token_text_similarity_threshold = multi_token_text_similarity_threshold
        self.one_token_text_similarity_threshold = one_token_text_similarity_threshold