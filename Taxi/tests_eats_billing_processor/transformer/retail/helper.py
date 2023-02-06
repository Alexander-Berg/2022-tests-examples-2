# pylint: disable=import-only-modules
from tests_eats_billing_processor.transformer.helper import TransformerTest


class TransformerRetailTest(TransformerTest):
    def __init__(self):
        super().__init__('retail')
