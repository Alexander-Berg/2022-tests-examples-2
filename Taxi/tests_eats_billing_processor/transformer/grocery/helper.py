# pylint: disable=import-only-modules
from tests_eats_billing_processor.transformer.helper import TransformerTest


GROCERY_FAKE_CLIENT_ID = '94062943'
GROCERY_CLIENT_ID = '87432897'
GROCERY_CONTRACT_ID = '1708265'


class TransformerGroceryTest(TransformerTest):
    def __init__(self):
        super().__init__('grocery')
