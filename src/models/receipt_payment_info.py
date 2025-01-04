class ReceiptPaymentInfo:
    def __init__(
        self,
        total_amount: float,
        tax_amount: float,
        non_tax_amount: float,
        cashless_payment_amount: float,
        cash_payment_amount: float,
        paid_cash_amount: float,
        change_cash_amount: float,
        bonus: float,
        prepayment: float,
        credit: float
    ):
        self._total_amount = total_amount
        self._tax_amount = tax_amount
        self._non_tax_amount = non_tax_amount
        self._cashless_payment_amount = cashless_payment_amount
        self._cash_payment_amount = cash_payment_amount
        self._paid_cash_amount = paid_cash_amount
        self._change_cash_amount = change_cash_amount
        self._bonus = bonus
        self._prepayment = prepayment
        self._credit = credit

    # Getter and Setter for total_amount
    @property
    def total_amount(self):
        return self._total_amount

    @total_amount.setter
    def total_amount(self, value: float):
        self._total_amount = value

    # Getter and Setter for tax_amount
    @property
    def tax_amount(self):
        return self._tax_amount

    @tax_amount.setter
    def tax_amount(self, value: float):
        self._tax_amount = value

    # Getter and Setter for non_tax_amount
    @property
    def non_tax_amount(self):
        return self._non_tax_amount

    @non_tax_amount.setter
    def non_tax_amount(self, value: float):
        self._non_tax_amount = value

    # Getter and Setter for cashless_payment_amount
    @property
    def cashless_payment_amount(self):
        return self._cashless_payment_amount

    @cashless_payment_amount.setter
    def cashless_payment_amount(self, value: float):
        self._cashless_payment_amount = value

    # Getter and Setter for cash_payment_amount
    @property
    def cash_payment_amount(self):
        return self._cash_payment_amount

    @cash_payment_amount.setter
    def cash_payment_amount(self, value: float):
        self._cash_payment_amount = value

    # Getter and Setter for paid_cash_amount
    @property
    def paid_cash_amount(self):
        return self._paid_cash_amount

    @paid_cash_amount.setter
    def paid_cash_amount(self, value: float):
        self._paid_cash_amount = value

    # Getter and Setter for change_cash_amount
    @property
    def change_cash_amount(self):
        return self._change_cash_amount

    @change_cash_amount.setter
    def change_cash_amount(self, value: float):
        self._change_cash_amount = value

    # Getter and Setter for bonus
    @property
    def bonus(self):
        return self._bonus

    @bonus.setter
    def bonus(self, value: float):
        self._bonus = value

    # Getter and Setter for prepayment
    @property
    def prepayment(self):
        return self._prepayment

    @prepayment.setter
    def prepayment(self, value: float):
        self._prepayment = value

    # Getter and Setter for credit
    @property
    def credit(self):
        return self._credit

    @credit.setter
    def credit(self, value: float):
        self._credit = value

    # Override __str__ method
    def __str__(self):
        return str({
            "total_amount": self._total_amount,
            "tax_amount": self._tax_amount,
            "non_tax_amount": self._non_tax_amount,
            "cashless_payment_amount": self._cashless_payment_amount,
            "cash_payment_amount": self._cash_payment_amount,
            "paid_cash_amount": self._paid_cash_amount,
            "change_cash_amount": self._change_cash_amount,
            "bonus": self._bonus,
            "prepayment": self._prepayment,
            "credit": self._credit
        })