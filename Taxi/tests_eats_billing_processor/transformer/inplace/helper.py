# pylint: disable=import-only-modules

from tests_eats_billing_processor.transformer.helper import TransformerTest

INPLACE_CLIENT_ID = '12345'
INPLACE_PLACE_ID = '54321'


class TransformerInplaceTest(TransformerTest):
    def __init__(self):
        super().__init__('inplace')
