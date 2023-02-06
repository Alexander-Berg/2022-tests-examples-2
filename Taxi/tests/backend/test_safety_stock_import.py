import base64

from odoo.modules.module import get_resource_path
from odoo.tests import tagged
from odoo.tests.common import SavepointCase
from odoo.tools import file_open


@tagged('lavka', 'autoorder', 'autoorder_imports', 'safety_stock', 'safety_stock_import')
class TestSafetyStockImport(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with file_open(
                get_resource_path('lavka', 'frontend/static/xlsx_templates/import_safety_stock.xls'), 'rb'
        ) as f:
            cls.safety_stock_file = base64.b64encode(f.read())

        cls.wh_tag1 = cls.env['stock.warehouse.tag'].create(
            {
                'type': 'geo',
                'name': 'Paris 1',
            }
        )

        cls.wh_tag2 = cls.env['stock.warehouse.tag'].create(
            {
                'type': 'geo',
                'name': 'Paris 2',
            }
        )

        cls.p_tag1 = cls.env['product.tag'].create(
            {
                'type': 'assortment',
                'name': 'Category 1',
            }
        )

        cls.p_tag2 = cls.env['product.tag'].create(
            {
                'type': 'assortment',
                'name': 'Category 2',
            }
        )

        cls.wh1 = cls.env['stock.warehouse'].create(
            {
                'name': 'wh-1',
                'code': '1',
                'active': True,
                'warehouse_tag_ids': [cls.wh_tag1.id, cls.wh_tag2.id],
                'product_tag_ids': [cls.p_tag1.id, cls.p_tag2.id],
            }
        )

        cls.wh2 = cls.env['stock.warehouse'].create(
            {
                'name': 'wh-2',
                'code': '2',
                'active': True,
                'warehouse_tag_ids': [cls.wh_tag1.id, cls.wh_tag2.id],
                'product_tag_ids': [cls.p_tag1.id, cls.p_tag2.id],
            }
        )

        cls.p1 = cls.env['product.product'].create(
            {
                'name': 'p-1',
                'default_code': '1',
                'wms_id': '1',
                'product_tag_ids': [cls.p_tag1.id],
            }
        )

        cls.p2 = cls.env['product.product'].create(
            {
                'name': 'p-2',
                'default_code': '2',
                'wms_id': '2',
                'product_tag_ids': [cls.p_tag1.id],
            }
        )

        cls.s_stock1 = cls.env['autoorder.safety.stock'].create({
            'product_id': cls.p1.id,
            'warehouse_ids': [cls.wh1.id, cls.wh2.id],
            'warehouse_product_tag_ids': [],
            'warehouse_tag_ids': [],
            'value': 1.0,
        })

    def test_safety_stock_import(self):
        ssi = self.env['autoorder.safety.stock.import']
        safety_stock_import = ssi.create({
            'file': self.safety_stock_file
        })
        safety_stock_import.import_data()

        obj1 = ssi.get_object({
            'product_id': self.p1.id,
            'warehouse_ids': [self.wh1.id, self.wh2.id],
            'warehouse_tag_ids': [],
            'warehouse_product_tag_ids': [],
        })

        self.assertEqual(len(obj1), 1, 'Обновление объекта, а не его создание')
        self.assertEqual(obj1.value, 1.2, 'Обновление уже существущего safety_stock')

        obj2 = ssi.get_object({
            'product_id': self.p1.id,
            'warehouse_ids': [],
            'warehouse_tag_ids': [self.wh_tag1.id, self.wh_tag2.id],
            'warehouse_product_tag_ids': [],
        })

        self.assertEqual(len(obj2), 1)

        obj3 = ssi.get_object({
            'product_id': self.p2.id,
            'warehouse_ids': [],
            'warehouse_tag_ids': [],
            'warehouse_product_tag_ids': [self.p_tag1.id, self.p_tag2.id],
        })

        self.assertEqual(len(obj3), 1)
