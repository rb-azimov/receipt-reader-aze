from src.models.receipt_general_info import ReceiptGeneralInfo
from src.models.receipt_product_list import ReceiptProductList
from src.models.receipt_payment_info import ReceiptPaymentInfo

class Receipt:
    def __init__(
        self,
        general_info: 'ReceiptGeneralInfo',
        product_list: 'ReceiptProductList',
        payment_info: 'ReceiptPaymentInfo'
    ):
        self._general_info = general_info
        self._product_list = product_list
        self._payment_info = payment_info

    # Getter and Setter for general_info
    @property
    def general_info(self):
        return self._general_info

    @general_info.setter
    def general_info(self, value: 'ReceiptGeneralInfo'):
        self._general_info = value

    # Getter and Setter for product_list
    @property
    def product_list(self):
        return self._product_list

    @product_list.setter
    def product_list(self, value: 'ReceiptProductList'):
        self._product_list = value

    # Getter and Setter for payment_info
    @property
    def payment_info(self):
        return self._payment_info

    @payment_info.setter
    def payment_info(self, value: 'ReceiptPaymentInfo'):
        self._payment_info = value

    # Override __str__ method
    def __str__(self):
        return Receipt.format_receipt_to_show(self)

    @staticmethod
    def format_receipt_to_show(receipt):
      # Header and general information
      def format_line(label, value):
          return f"{label:<20}: {value}\n"

      output = ""
      output += "-" * 50 + "\n"
      output += f"{'RECEIPT':^50}\n"
      output += "-" * 50 + "\n"

      general_info = receipt.general_info
      output += format_line("Store Name", general_info.name)
      output += format_line("Address", general_info.address)
      output += format_line("Code", general_info.code)
      output += format_line("Tax Payer", general_info.tax_payer_name)
      output += format_line("TIN", general_info.TIN)
      output += format_line("Receipt #", general_info.sale_receipt_num)
      output += format_line("Cashier", general_info.cashier_name)
      output += format_line("Date", general_info.date)
      output += format_line("Time", general_info.time)
      output += "-" * 50 + "\n"

      # Products part as a table
      output += f"{'Product':<20} {'Qty':<8} {'Price':<10} {'Amount':<10}\n"
      output += "_" * 50 + "\n"
      for product in receipt.product_list.products:
          output += f"{product.name:<20} {product.quantity:<8} {product.price:<10.2f} {product.amount:<10.2f}\n"
      output += "_" * 50 + "\n"

      # Payment information
      payment_info = receipt.payment_info
      output += format_line("Total Amount", f"{payment_info.total_amount:.2f}")
      output += format_line("Tax Amount", f"{payment_info.tax_amount:.2f}")
      output += format_line("Non-Tax Amount", f"{payment_info.non_tax_amount:.2f}")
      output += format_line("Cashless Payment", f"{payment_info.cashless_payment_amount:.2f}")
      output += format_line("Cash Payment", f"{payment_info.cash_payment_amount:.2f}")
      output += format_line("Paid Cash", f"{payment_info.paid_cash_amount:.2f}")
      output += format_line("Change", f"{payment_info.change_cash_amount:.2f}")
      output += format_line("Bonus", f"{payment_info.bonus:.2f}")
      output += format_line("Prepayment", f"{payment_info.prepayment:.2f}")
      output += format_line("Credit", f"{payment_info.credit:.2f}")
      output += "-" * 50 + "\n"
      output += f"{'THANK YOU!':^50}\n"
      output += "-" * 50 + "\n"

      return output