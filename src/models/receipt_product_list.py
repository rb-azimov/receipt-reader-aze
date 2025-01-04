class ReceiptProductList:
    def __init__(self, products: list):
        self._products = products

    # Getter and Setter for products
    @property
    def products(self):
        return self._products

    @products.setter
    def products(self, value: list):
        self._products = value

    # Method to get the number of products
    def get_num_products(self) -> int:
        return len(self._products)

    # Method to get the total amount
    def get_total_amount(self) -> float:
        return sum(product.amount for product in self._products)

    # Override __str__ method
    def __str__(self):
        return str([str(product) for product in self._products])