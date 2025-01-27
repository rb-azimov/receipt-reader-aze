from statistics import quantiles

from src.models.receipt import Receipt

class ReceiptValidator:
    """
    Class for checking consistencies
    and validating if needed.

    validate_receipt(receipt) -> error statements
    """
    threshold = 1

    @staticmethod
    def check_equality(value1, value2):
        return True if abs(value1 - value2) < ReceiptValidator.threshold else False

    @staticmethod
    def validate_receipt(receipt: Receipt, update: bool = True):
        product_list_errors = ReceiptValidator.validate_product_list(receipt, update)
        tax_details_errors = ReceiptValidator.validate_tax_details(receipt, update)
        payment_types_errors = ReceiptValidator.validate_payment_types(receipt, update)
        total_amount_errors = ReceiptValidator.validate_total_amount(receipt, update)

        errors_all = product_list_errors \
            + tax_details_errors \
            + payment_types_errors \
            + total_amount_errors

        return errors_all

    @staticmethod
    def validate_product_list(receipt: Receipt, update: bool):
        errors = []
        products = receipt.product_list.products
        for i in range(len(products)):
            product = products[i]
            if not ReceiptValidator.check_equality(product.quantity * product.price, product.amount):
                # Character 1 may have been recognized as 7
                if product.quantity == 7 and product.price == product.amount:
                    if update:
                        product.quantity = 1
                else:
                    errors.append('Inconsistent Product {0}: quantity={1}, price={2}, amount={3}'.format(
                        i+1, product.quantity, product.price, product.amount
                    ))
                    if update:
                        product.amount = product.quantity * product.price
        return errors

    @staticmethod
    def validate_tax_details(receipt: Receipt, update: bool):
        errors = []
        payment_info = receipt.payment_info

        if not ReceiptValidator.check_equality(payment_info.tax_amount + payment_info.non_tax_amount,
                                               payment_info.total_amount):
            errors.append('Inconsistent Tax Details: tax={0}, non-tax={1}, total={2}'.format(
                payment_info.tax_amount,
                payment_info.non_tax_amount,
                payment_info.total_amount
            ))
            if update:
                payment_info.non_tax_amount = payment_info.total_amount - payment_info.tax_amount
        return errors

    @staticmethod
    def validate_payment_types(receipt: Receipt, update: bool):
        errors = []
        payment_info = receipt.payment_info
        if (payment_info.paid_cash_amount == 0
                and payment_info.change_cash_amount == 0
                and (payment_info.cash_payment_amount + payment_info.cashless_payment_amount) != 0):
            return errors
        if not ReceiptValidator.check_equality(payment_info.cash_payment_amount + payment_info.change_cash_amount,
                                               payment_info.paid_cash_amount):
            errors.append('Inconsistent Cash Change: cash={0}, change={1}, paid={2}'.format(
                payment_info.cash_payment_amount,
                payment_info.change_cash_amount,
                payment_info.paid_cash_amount
            ))
            if update:
                payment_info.change_cash_amount = payment_info.paid_cash_amount - payment_info.cash_payment_amount

        if not ReceiptValidator.check_equality(
            payment_info.cashless_payment_amount + payment_info.cash_payment_amount
                + payment_info.bonus + payment_info.prepayment + payment_info.credit,
            payment_info.total_amount
        ):
            errors.append('Inconsistent payment parts: '
                          + 'cashless={0}, cash={1}, '.format(payment_info.cashless_payment_amount,
                                                            payment_info.cash_payment_amount)
                          + 'bonus={0}, prepayment={1}, '.format(payment_info.bonus, payment_info.prepayment)
                          + 'credit={0}, total={1}'.format(payment_info.credit, payment_info.total_amount)
            )
            if update:
                payment_info.total_amount = payment_info.cashless_payment_amount + payment_info.cash_payment_amount
                + payment_info.bonus + payment_info.prepayment + payment_info.credit
        return errors

    @staticmethod
    def validate_total_amount(receipt: Receipt, update: bool):
        errors = []
        expected_total_amount = sum(product.amount for product in receipt.product_list.products)
        real_total_amount = receipt.payment_info.total_amount
        if not ReceiptValidator.check_equality(expected_total_amount, real_total_amount):
            errors.append('Inconsistent Total Amount: '
                          + 'calculated={0}, real={1}'.format(expected_total_amount, real_total_amount))
            if update:
                receipt.payment_info.total_amount = expected_total_amount
        return errors