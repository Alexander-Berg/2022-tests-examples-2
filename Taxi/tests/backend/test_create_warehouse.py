# -*- coding: utf-8 -*-
# pylint: disable=protected-access,attribute-defined-outside-init,import-error
# pylint: disable=too-many-branches,no-member,too-many-locals,abstract-class-instantiated
import logging

from odoo.tests import tagged
from odoo.tests.common import SavepointCase

# pylint: disable=invalid-name
_logger = logging.getLogger(__name__)


@tagged('lavka', 'inventory', 'fast')
class TestWarehouseCommon(SavepointCase):
    """
    Тест Создания склада
    """

    @classmethod
    def setUpClass(cls):
        super(TestWarehouseCommon, cls).setUpClass()
        cls.warehouse = cls.env['stock.warehouse'].create({
            'name': 'Test `warehouse',
            'code': 'TT',
        })


# pylint: disable=abstract-class-instantiated
@tagged('lavka', 'inventory')
class TestStockInventoryStandard(TestWarehouseCommon):

    def test_create_warehouse(self):
        self.assertEqual(self.warehouse.wh_stock_diff.name, 'DIFF')
        self.assertEqual(self.warehouse.lot_stock_id.name, 'OPER')
        self.assertEqual(self.warehouse.wh_stock_git.name, 'GIT')
        self.assertTrue(bool(self.warehouse.wh_sequence))
