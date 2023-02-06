from odoo.tests import tagged
from odoo.tests.common import SavepointCase


@tagged('lavka', 'autoorder', 'safety_stock')
class TestSafetyStock(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.p_base_water = cls.env['product.product'].create(
            {
                'name': 'water',
                'default_code': '100',
                'wms_id': '100',
                'product_tag_ids': []
            },
        )
        cls.p_base_soap = cls.env['product.product'].create(
            {
                'name': 'soap',
                'default_code': '200',
                'wms_id': '200',
                'product_tag_ids': []
            },
        )

        cls.wh_tag_geo1 = cls.env['stock.warehouse.tag'].create(
            {
                'type': 'geo',
                'name': 'geo1',
            }
        )
        cls.wh_tag_geo2 = cls.env['stock.warehouse.tag'].create(
            {
                'type': 'geo',
                'name': 'geo2',
            }
        )
        cls.wh_tag_geo3 = cls.env['stock.warehouse.tag'].create(
            {
                'type': 'geo',
                'name': 'geo3',
            }
        )

        cls.wh1_geo1 = cls.env['stock.warehouse'].create(
            {
                'name': 'l-001',
                'code': 'l-001',
                'warehouse_tag_ids': [
                    cls.wh_tag_geo1.id,
                ],
                'product_tag_ids': [],
            }
        )
        cls.wh2_geo1 = cls.env['stock.warehouse'].create(
            {
                'name': 'l-002',
                'code': 'l-002',
                'warehouse_tag_ids': [
                    cls.wh_tag_geo1.id,
                ],
                'product_tag_ids': [],
            }
        )
        cls.wh3_geo2 = cls.env['stock.warehouse'].create(
            {
                'name': 'l-003',
                'code': 'l-003',
                'warehouse_tag_ids': [
                    cls.wh_tag_geo2.id,
                ],
                'product_tag_ids': [],
            }
        )
        cls.wh4_geo3 = cls.env['stock.warehouse'].create(
            {
                'name': 'l-004',
                'code': 'l-004',
                'warehouse_tag_ids': [
                    cls.wh_tag_geo3.id,
                ],
            }
        )

    def test_001_wh_tag_ids(self):
        self.env['autoorder.safety.stock'].create(
            [
                {
                    'product_id': self.p_base_water.id,
                    'value': 300.0,
                    'warehouse_tag_ids': [
                        self.wh_tag_geo1.id,
                        self.wh_tag_geo2.id,
                    ],
                },
            ]
        )

        self.assertEqual(
            self.env['autoorder.safety.stock'].get_values(),
            {
                (self.p_base_water.default_code, self.wh1_geo1.code,): 300,
                (self.p_base_water.default_code, self.wh2_geo1.code): 300,
                (self.p_base_water.default_code, self.wh3_geo2.code): 300,
            }
        )

        self.env['autoorder.safety.stock'].create(
            [
                {
                    'product_id': self.p_base_soap.id,
                    'value': 301,
                    'warehouse_tag_ids': [
                        self.wh_tag_geo3.id,
                    ],
                },
            ]
        )

        self.assertEqual(
            self.env['autoorder.safety.stock'].get_values(),
            {
                (self.p_base_water.default_code, self.wh1_geo1.code,): 300,
                (self.p_base_water.default_code, self.wh2_geo1.code): 300,
                (self.p_base_water.default_code, self.wh3_geo2.code): 300,
                (self.p_base_soap.default_code, self.wh4_geo3.code): 301,
            }
        )

    def test_002_wh_ids(self):
        self.env['autoorder.safety.stock'].create(
            [
                {
                    'product_id': self.p_base_water.id,
                    'value': 300.0,
                    'warehouse_ids': [
                        self.wh1_geo1.id,
                        self.wh2_geo1.id,
                    ],
                },
                {
                    'product_id': self.p_base_water.id,
                    'value': 301.0,
                    'warehouse_ids': [
                        self.wh3_geo2.id,
                    ],
                },
            ]
        )

        self.assertEqual(
            self.env['autoorder.safety.stock'].get_values(),
            {
                (self.p_base_water.default_code, self.wh1_geo1.code): 300,
                (self.p_base_water.default_code, self.wh2_geo1.code): 300,
                (self.p_base_water.default_code, self.wh3_geo2.code): 301,
            }
        )

    def test_003_priority(self):
        self.env['autoorder.safety.stock'].create(
            [
                {
                    'product_id': self.p_base_water.id,
                    'value': 300,
                    'warehouse_ids': [
                        self.wh1_geo1.id,
                    ],
                },
                {
                    'product_id': self.p_base_water.id,
                    'value': 301,
                    'warehouse_tag_ids': [
                        self.wh_tag_geo1.id,
                        self.wh_tag_geo2.id,
                    ],
                },
                {
                    'product_id': self.p_base_water.id,
                    'value': 302.0,
                    'warehouse_tag_ids': [
                        self.wh_tag_geo2.id,
                    ],
                },
                {
                    'product_id': self.p_base_soap.id,
                    'value': 303.0,
                    'warehouse_ids': [
                        self.wh3_geo2.id,
                    ],
                },
            ]
        )

        self.assertEqual(
            self.env['autoorder.safety.stock'].get_values(),
            {
                (self.p_base_water.default_code, self.wh1_geo1.code): 300,
                (self.p_base_water.default_code, self.wh2_geo1.code): 301,
                (self.p_base_water.default_code, self.wh3_geo2.code): 302,
                (self.p_base_soap.default_code, self.wh3_geo2.code): 303,
            }
        )
