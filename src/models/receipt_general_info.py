class ReceiptGeneralInfo:
    def __init__(
        self,
        name: str,
        address: str,
        code: str,
        tax_payer_name: str,
        TIN: str,
        sale_receipt_num: int,
        cashier_name: str,
        date: str,
        time: str
    ):
        self._name = name
        self._address = address
        self._code = code
        self._tax_payer_name = tax_payer_name
        self._TIN = TIN
        self._sale_receipt_num = sale_receipt_num
        self._cashier_name = cashier_name
        self._date = date
        self._time = time

    # Getter and Setter for name
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    # Getter and Setter for address
    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value: str):
        self._address = value

    # Getter and Setter for code
    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, value: str):
        self._code = value

    # Getter and Setter for tax_payer_name
    @property
    def tax_payer_name(self):
        return self._tax_payer_name

    @tax_payer_name.setter
    def tax_payer_name(self, value: str):
        self._tax_payer_name = value

    # Getter and Setter for TIN
    @property
    def TIN(self):
        return self._TIN

    @TIN.setter
    def TIN(self, value: str):
        self._TIN = value

    # Getter and Setter for sale_receipt_num
    @property
    def sale_receipt_num(self):
        return self._sale_receipt_num

    @sale_receipt_num.setter
    def sale_receipt_num(self, value: int):
        self._sale_receipt_num = value

    # Getter and Setter for cashier_name
    @property
    def cashier_name(self):
        return self._cashier_name

    @cashier_name.setter
    def cashier_name(self, value: str):
        self._cashier_name = value

    # Getter and Setter for date
    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value: str):
        self._date = value

    # Getter and Setter for time
    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value: str):
        self._time = value

    # Override __str__ method
    def __str__(self):
        return str({
            "name": self._name,
            "address": self._address,
            "code": self._code,
            "tax_payer_name": self._tax_payer_name,
            "TIN": self._TIN,
            "sale_receipt_num": self._sale_receipt_num,
            "cashier_name": self._cashier_name,
            "date": self._date,
            "time": self._time
        })