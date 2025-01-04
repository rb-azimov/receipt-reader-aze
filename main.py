import pytesseract
from src.low_level_processors.receipt_service import ReceiptService

pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def main():
    fiscal_codes = [
        'wPeLM3wvuBUCQn4TMN5ZQZvheV7XuQg97meruVsqRVT',
        'Dh8hsAoFVGFcyEzwYdmmykoZZZPhm5LeVe9r9VZQy9AH',
        'JDbiy1aCSKJn',
        'BaLH4264TYtf',
        '8ofcmJhYPcaZ',
        '4tFLVnqE1gbT',
        'ER9s8qbNzEsyVcj2vhRi7yJGxsUgKkVvE7fydNX2Mz7y',
    ]
    fiscal_code = fiscal_codes[0]

    receipt_service = ReceiptService(app_props=None)
    receipt = receipt_service.mine_receipt(fiscal_code)
    print(receipt.__str__())

if __name__ == '__main__':
    main()
