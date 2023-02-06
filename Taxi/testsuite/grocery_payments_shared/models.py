import enum


class InvoiceOriginator(enum.Enum):
    grocery = ('grocery', '', 'order')
    helping_hand = ('persey_donation', 'hh:', 'helping_hand')
    tips = ('tips', 'tips:', 'tips')

    def __init__(self, request_name, prefix, receipt_data_type):
        self._request_name = request_name
        self._prefix = prefix
        self._receipt_data_type = receipt_data_type

    @property
    def request_name(self):
        return self._request_name

    @property
    def prefix(self):
        return self._prefix

    @property
    def receipt_data_type(self):
        return self._receipt_data_type
