import logging
from odoo.tests.common import SavepointCase, tagged, Form

_logger = logging.getLogger(__name__)


@tagged('lavka', 'factory_backend')
class TestFactory(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestFactory, cls).setUpClass()
        cls.factory = cls.env['factory_common']
        cls.warehouses = cls.factory.create_warehouses(qty=5)
        assert cls.warehouses, 'Warehouses look empty'
        cls.products = cls.factory.create_products(cls.warehouses, qty=10)
        assert cls.products, 'Products look empty'

    def test_factory(self):
        pass
