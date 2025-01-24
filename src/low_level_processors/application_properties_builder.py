from src.low_level_processors.application_properties import ApplicationProperties
from src.low_level_processors.properties import TextSimilarityThresholdProperties, MarginProperties, SplittingProperty, \
    SplittingProperties, OCRProperty, OCRProperties

class ApplicationPropertiesBuilder:
    # @staticmethod
    # def prepare_application_properties_v_core_1_logic_0_depend_0(is_debug_on=False):
    #     upper_letters = 'ABCÇDEƏFGĞHXIİJKQLMNOÖPRSŞTUÜVYZ'
    #     lower_letters = 'abcçdeəfgğhxıijkqlmnoöprsştuüvyz'
    #     azerbaijani_alphabet = upper_letters + lower_letters
    #     chartset = ' ' + '%_-№' + azerbaijani_alphabet + '.0123456789'
    #     general_part_config = f'--psm 6 -c tessedit_char_whitelist={chartset}'
    #
    #     upper_letters = 'ABCÇDEƏFGĞHXIİJKQLMNOÖPRSŞTUÜVYZ'
    #     lower_letters = 'abcçdeəfgğhxıijkqlmnoöprsştuüvyz'
    #     azerbaijani_alphabet = upper_letters + lower_letters
    #     chartset = ' ' + '%_-' + azerbaijani_alphabet + '.0123456789'
    #     product_names_config = f'--psm 4 -c tessedit_char_whitelist={chartset}'
    #
    #     charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxvz'
    #     payment_type_part_names_config = f'--psm 4 -c tessedit_char_whitelist={charset}'
    #
    #     ocr_properties = OCRProperties(
    #         general_part_ocr_property=OCRProperty(config=general_part_config, lang='eng+aze'),
    #         product_names_ocr_property=OCRProperty(config=product_names_config, lang='eng+aze'),
    #         quantities_ocr_property=OCRProperty(config='--psm 6 -c tessedit_char_whitelist=.0123456789', lang=None),
    #         prices_ocr_property=OCRProperty(config='--psm 6 -c tessedit_char_whitelist=.0123456789', lang=None),
    #         amounts_ocr_property=OCRProperty(config='--psm 6 -c tessedit_char_whitelist=.0123456789', lang=None),
    #         payment_amount_part_ocr_property=OCRProperty(config='--psm 6 -c tessedit_char_whitelist=.0123456789',
    #                                                      lang=None),
    #         payment_type_part_names_ocr_property=OCRProperty(config=payment_type_part_names_config, lang='eng'),
    #         payment_type_part_numbers_ocr_property=OCRProperty(config='--psm 6 -c tessedit_char_whitelist=.0123456789',
    #                                                            lang=None)
    #     )
    #
    #     splitting_properties = SplittingProperties(
    #         receipt_logical_splitting_property=SplittingProperty(threshold_scale=0.3, min_difference=30),
    #         payment_to_amount_type_splitting_property=SplittingProperty(threshold_scale=0.5, min_difference=30),
    #         payment_amount_to_name_value_splitting_property=SplittingProperty(threshold_scale=0.03, min_difference=30),
    #         payment_type_to_name_value_splitting_property=SplittingProperty(threshold_scale=0.03, min_difference=30),
    #         products_part_splitting_properties=SplittingProperty(threshold_scale=0.01, min_difference=30)
    #     )
    #
    #     margin_properties = MarginProperties(
    #         product_line_margin=3,
    #         general_part_bottom_margin=50,
    #         payment_part_bottom_margin=160,
    #         cashier_date_time_top_margin=2,
    #         payment_amount_part_margin=5,
    #         payment_type_name_value_margin=50
    #     )
    #
    #     text_similarity_threshold_properties = TextSimilarityThresholdProperties(
    #         payment_type_checking_text_similarity_threshold=70,
    #         one_token_text_similarity_threshold=80,
    #         multi_token_text_similarity_threshold=80
    #     )
    #
    #     return ApplicationProperties(
    #         ocr_properties,
    #         splitting_properties,
    #         margin_properties,
    #         text_similarity_threshold_properties,
    #         is_debug_on
    #     )

    @staticmethod
    def prepare_application_properties_v_core_1_logic_0_depend_1(is_debug_on=False):
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
                                                               lang=None),
            small_image_ocr_property=OCRProperty(config='--psm 8 -c tessedit_char_whitelist=.0123456789', lang=None),
        )

        splitting_properties = SplittingProperties(
            receipt_logical_splitting_property=SplittingProperty(threshold_scale=0.3, min_difference=30),
            payment_to_amount_type_splitting_property=SplittingProperty(threshold_scale=0.5, min_difference=30),
            payment_amount_to_name_value_splitting_property=SplittingProperty(threshold_scale=0.03, min_difference=30),
            payment_type_to_name_value_splitting_property=SplittingProperty(threshold_scale=0.03, min_difference=30),
            products_part_splitting_properties=SplittingProperty(threshold_scale=0.015, min_difference=30)
            # th_scale changed!
        )

        margin_properties = MarginProperties(
            product_line_margin=3,
            price_line_margin=5,
            amount_line_margin=5,
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