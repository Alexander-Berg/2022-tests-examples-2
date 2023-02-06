# pylint: disable=import-only-modules

from tests_eats_billing_processor.transformer.helper import TransformerTest


class TransformerShopMarketplaceTest(TransformerTest):
    def __init__(self):
        super().__init__('shop_marketplace')
