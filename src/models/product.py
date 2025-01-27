class Product:
    def __init__(self, name: str, quantity: float, price: float, amount: float):
        self._name = name
        self._quantity = quantity
        self._price = price
        self._amount = amount

    # Getters and Setters for name
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    # Getters and Setters for quantity
    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value: float):
        self._quantity = value

    # Getters and Setters for price
    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value: float):
        self._price = value

    # Getters and Setters for amount
    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value: float):
        self._amount = value

    # Method to check if amount equals quantity * price
    def check_amount_coherence(self) -> bool:
        return self._amount == self._quantity * self._price

    def copy(self):
        return Product(
            self._name,
            self._quantity,
            self._price,
            self._amount
        )
    # Override __str__ method
    def __str__(self):
        return str({
            "name": self._name,
            "quantity": self._quantity,
            "price": self._price,
            "amount": self._amount
        })