from datetime import date, timedelta, datetime
from random import randrange, shuffle
from freezegun import freeze_time

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import SavepointCase


@tagged('lavka', 'autoorder', 'delivery_schedule', 'delivery_schedule_old')
class TestDeliverySchedule(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.p_tag_assort_base = cls.env['product.tag'].create(
            {
                'type': 'assortment',
                'name': 'base',
            }
        )
        cls.p_tag_assort_lux = cls.env['product.tag'].create(
            {
                'type': 'assortment',
                'name': 'lux',
            }
        )
        cls.p_tag_assort_budget = cls.env['product.tag'].create(
            {
                'type': 'assortment',
                'name': 'budget',
            }
        )

        cls.p_tag_abc_group_a = cls.env['product.tag'].create(
            {
                'type': 'abc_group',
                'name': 'a',
            }
        )
        cls.p_tag_abc_group_b = cls.env['product.tag'].create(
            {
                'type': 'abc_group',
                'name': 'b',
            }
        )

        cls.p_tag_storage_type_warm = cls.env['product.tag'].create(
            {
                'type': 'storage_type',
                'name': 'test_warm',
            }
        )
        cls.p_tag_storage_type_chem = cls.env['product.tag'].create(
            {
                'type': 'storage_type',
                'name': 'chem',
            }
        )

        cls.p_tag_nonfood_food = cls.env['product.tag'].create(
            {
                'type': 'nonfood',
                'name': 'food300',
            }
        )

        cls.p_tag_nonfood_nonfood = cls.env['product.tag'].create(
            {
                'type': 'nonfood',
                'name': 'nonfood300',
            }
        )

        cls.p_base_water = cls.env['product.product'].create(
            {
                'name': 'water',
                'default_code': '100',
                'wms_id': '100',
                'product_tag_ids': [
                    cls.p_tag_assort_base.id,
                    cls.p_tag_abc_group_a.id,
                    cls.p_tag_storage_type_warm.id,
                    cls.p_tag_nonfood_food.id,
                ]
            },
        )
        cls.p_base_soap = cls.env['product.product'].create(
            {
                'name': 'soap',
                'default_code': '200',
                'wms_id': '200',
                'product_tag_ids': [
                    cls.p_tag_assort_base.id,
                    cls.p_tag_abc_group_b.id,
                    cls.p_tag_storage_type_chem.id,
                    cls.p_tag_nonfood_nonfood.id,
                ]
            },
        )
        cls.p_lux_water = cls.env['product.product'].create(
            {
                'name': 'lux water',
                'default_code': '110',
                'wms_id': '110',
                'product_tag_ids': [
                    cls.p_tag_assort_lux.id,
                    cls.p_tag_storage_type_warm.id,
                    cls.p_tag_nonfood_food.id,
                ]
            },
        )
        cls.p_budget_water = cls.env['product.product'].create(
            {
                'name': 'budget water',
                'default_code': '120',
                'wms_id': '120',
                'product_tag_ids': [
                    cls.p_tag_assort_budget.id,
                    cls.p_tag_storage_type_warm.id,
                    cls.p_tag_nonfood_food.id,
                ]
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
                'product_tag_ids': [
                    cls.p_tag_assort_base.id,
                    cls.p_tag_assort_lux.id,
                    cls.p_tag_assort_budget.id,
                ],
            }
        )
        cls.wh2_geo1 = cls.env['stock.warehouse'].create(
            {
                'name': 'l-002',
                'code': 'l-002',
                'warehouse_tag_ids': [
                    cls.wh_tag_geo1.id,
                ],
                'product_tag_ids': [
                    cls.p_tag_assort_base.id,
                    cls.p_tag_assort_lux.id,
                ],
            }
        )
        cls.wh3_geo2 = cls.env['stock.warehouse'].create(
            {
                'name': 'l-003',
                'code': 'l-003',
                'warehouse_tag_ids': [
                    cls.wh_tag_geo2.id,
                ],
                'product_tag_ids': [
                    cls.p_tag_assort_base.id,
                    cls.p_tag_assort_budget.id,
                ],
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

        cls.v1 = cls.env['res.partner'].create(
            {
                'name': 'v-001: assort_base',
                'is_company': True,
                'supplier_rank': 1,
            }
        )
        cls.v1_contract1 = cls.env['purchase.requisition'].create(
            {
                'vendor_id': cls.v1.id,
                'state': 'open',
                'warehouse_tag_ids': [
                    cls.wh_tag_geo1.id,
                ],
            }
        )
        with freeze_time('1970-01-01 00:00:00'):
            cls.env['purchase.requisition.line'].create(
                [
                    {
                        'requisition_id': cls.v1_contract1.id,
                        'product_id': p.id,
                        'start_date': fields.Datetime.today(),
                        'tax_id': p.supplier_taxes_id.id,
                        'product_uom_id': p.uom_id.id,
                        'price_unit': 300 + randrange(1, 3),
                        'product_qty': 1,
                        'product_code': f'code-{p.id}',
                        'product_name': 'vendor product name',
                        'qty_multiple': 1,
                        'approve': True,
                        'approve_price': True,
                        'approve_tax': True,
                        'active': True,
                    }
                    for p in [cls.p_base_water, cls.p_base_soap]
                ]
            )

            cls.v2 = cls.env['res.partner'].create(
                {
                    'name': 'v-002',
                    'is_company': True,
                    'supplier_rank': 1,
                }
            )
            cls.v2_contract1 = cls.env['purchase.requisition'].create(
                {
                    'vendor_id': cls.v2.id,
                    'state': 'open',
                    'warehouse_tag_ids': [
                        cls.wh_tag_geo1.id,
                        cls.wh_tag_geo2.id,
                        cls.wh_tag_geo3.id,
                    ],
                }
            )
            cls.env['purchase.requisition.line'].create(
                [
                    {
                        'requisition_id': cls.v2_contract1.id,
                        'product_id': p.id,
                        'start_date': fields.Datetime.today(),
                        'tax_id': p.supplier_taxes_id.id,
                        'product_uom_id': p.uom_id.id,
                        'price_unit': 300 + randrange(1, 3),
                        'product_qty': 1,
                        'product_code': f'code-{p.id}',
                        'product_name': 'vendor product name',
                        'qty_multiple': 1,
                        'approve': True,
                        'approve_price': True,
                        'approve_tax': True,
                        'active': True,
                    }
                    for p in [cls.p_base_water, cls.p_base_soap]
                ]
            )

            cls.v3 = cls.env['res.partner'].create(
                {
                    'name': 'v-003',
                    'is_company': True,
                    'supplier_rank': 1,
                }
            )
            cls.v3_contract1 = cls.env['purchase.requisition'].create(
                {
                    'vendor_id': cls.v3.id,
                    'state': 'open',
                    'warehouse_tag_ids': [
                        cls.wh_tag_geo1.id,
                        cls.wh_tag_geo2.id,
                        cls.wh_tag_geo3.id,
                    ],
                }
            )
            cls.env['purchase.requisition.line'].create(
                [
                    {
                        'requisition_id': cls.v3_contract1.id,
                        'product_id': p.id,
                        'start_date': fields.Datetime.today(),
                        'tax_id': p.supplier_taxes_id.id,
                        'product_uom_id': p.uom_id.id,
                        'price_unit': 300 + randrange(1, 3),
                        'product_qty': 1,
                        'product_code': f'code-{p.id}',
                        'product_name': 'vendor product name',
                        'qty_multiple': 1,
                        'approve': True,
                        'approve_price': True,
                        'approve_tax': True,
                        'active': True,
                    }
                    for p in [cls.p_lux_water]
                ]
            )

            cls.v4 = cls.env['res.partner'].create(
                {
                    'name': 'v-004',
                    'is_company': True,
                    'supplier_rank': 1,
                }
            )
            cls.v4_contract1 = cls.env['purchase.requisition'].create(
                {
                    'vendor_id': cls.v4.id,
                    'state': 'open',
                    'warehouse_tag_ids': [
                        cls.wh_tag_geo1.id,
                        cls.wh_tag_geo2.id,
                        cls.wh_tag_geo3.id,
                    ],
                }
            )
            cls.env['purchase.requisition.line'].create(
                [
                    {
                        'requisition_id': cls.v4_contract1.id,
                        'product_id': p.id,
                        'start_date': fields.Datetime.today(),
                        'tax_id': p.supplier_taxes_id.id,
                        'product_uom_id': p.uom_id.id,
                        'price_unit': 300 + randrange(1, 3),
                        'product_qty': 1,
                        'product_code': f'code-{p.id}',
                        'product_name': 'vendor product name',
                        'qty_multiple': 1,
                        'approve': True,
                        'approve_price': True,
                        'approve_tax': True,
                        'active': True,
                    }
                    for p in [cls.p_budget_water]
                ]
            )
            for line in cls.env['purchase.requisition.line'].search([]):
                line._compute_approve()

    def test_01_products(self):
        assort_base = self.env['product.product'].search(
            [
                ('product_tag_ids', 'in', self.p_tag_assort_base.ids),
            ]
        )
        self.assertIn(self.p_base_water, assort_base)
        self.assertIn(self.p_base_soap, assort_base)

        assort_lux = self.env['product.product'].search(
            [
                ('product_tag_ids', 'in', self.p_tag_assort_lux.ids),
            ]
        )
        self.assertIn(self.p_lux_water, assort_lux)

        assort_budget = self.env['product.product'].search(
            [
                ('product_tag_ids', 'in', self.p_tag_assort_budget.ids),
            ]
        )
        self.assertIn(self.p_budget_water, assort_budget)

    def test_001_x_weekdays(self):
        sch = self.env['autoorder.delivery.schedule'].create(
            [
                {
                    'vendor_id': self.v1.id,
                    'days_before_order': 1,
                    'delivery_weekday_0': True,
                    'delivery_weekday_6': True,
                    'order_weekday_0': False,
                    'order_weekday_6': False,
                    'week_type': '',
                    'warehouse_ids': [self.wh1_geo1.id],
                }
            ]
        )

        self.assertEqual(
            sch.delivery_weekdays(),
            (True, False, False, False, False, False, True),
            'correct delivery weekdays',
        )
        self.assertEqual(
            sch.order_weekdays(),
            (False, True, True, True, True, True, False),
            'correct order weekdays',
        )

    def test_001_get_delivery_dates(self):
        wd = {
            date(1970, 1, i).weekday(): date(1970, 1, i)
            for i in range(1, 8)
        }

        sch1 = self.env['autoorder.delivery.schedule'].create(
            [
                {
                    'vendor_id': self.v1.id,
                    'days_before_order': 1,
                    'warehouse_ids': [self.wh1_geo1.id],
                }
            ]
        )
        self.assertEqual(
            [sch1.get_delivery_dates(i) for i in wd.values()],
            [[]] * 7,
            'дни поставок не заданы',
        )

        sch2 = self.env['autoorder.delivery.schedule'].create(
            [
                {
                    'vendor_id': self.v1.id,
                    'days_before_order': 1,
                    'order_weekday_0': False,
                    'delivery_weekday_0': True,
                    'delivery_weekday_1': True,
                    'delivery_weekday_2': True,
                    'delivery_weekday_3': True,
                    'delivery_weekday_4': True,
                    'delivery_weekday_5': True,
                    'delivery_weekday_6': True,
                    'warehouse_ids': [self.wh1_geo1.id],
                }
            ]
        )
        self.assertEqual(
            sch2.get_delivery_dates(wd[0]),
            [],
            'по понедельникам заказы не принимаются',
        )
        self.assertTrue(
            all([sch2.get_delivery_dates(v) for k, v in wd.items() if k > 0]),
            'со вторника по субботу заказы принимаются',
        )

        sch3 = self.env['autoorder.delivery.schedule'].create(
            [
                {
                    'vendor_id': self.v1.id,
                    'days_before_order': 1,
                    'delivery_weekday_0': True,
                    'delivery_weekday_2': True,
                    'delivery_weekday_4': True,
                    'warehouse_ids': [self.wh1_geo1.id],
                }
            ]
        )
        self.assertEqual(
            sch3.get_delivery_dates(wd[0]),
            [],
            'если заказ в понедельник, то доставки на вторник нет (+1 день)',
        )
        self.assertEqual(
            sch3.get_delivery_dates(wd[1]),
            [(wd[2], wd[2] + timedelta(days=2))],
            'если заказ во вторник, то есть доставка на среду и следующая доставка на пятницу (+2 дня)',
        )
        self.assertEqual(
            sch3.get_delivery_dates(wd[3]),
            [(wd[4], wd[4] + timedelta(days=3))],
            'если заказ в четверг, то есть доставка на пятницу и следующая доставка на понедельник (+3 дня)',
        )

        sch4 = self.env['autoorder.delivery.schedule'].create(
            [
                {
                    'vendor_id': self.v1.id,
                    'days_before_order': 7,
                    'delivery_weekday_0': True,
                    'warehouse_ids': [self.wh1_geo1.id],
                }
            ]
        )
        self.assertEqual(
            sch4.get_delivery_dates(wd[0]),
            [(wd[0] + timedelta(days=7), wd[0] + timedelta(days=14))],
            'если заказ в понедельник, то доставка на след понедельник',
        )
        self.assertEqual(
            sch4.get_delivery_dates(wd[1]),
            [],
            'если заказ во вторник, то уже нет доставки',
        )

        sch5 = self.env['autoorder.delivery.schedule'].create(
            [
                {
                    'vendor_id': self.v1.id,
                    'days_before_order': 3,
                    'delivery_weekday_0': True,
                    'delivery_weekday_1': True,
                    'order_weekday_5': False,
                    'order_weekday_6': False,
                    'warehouse_ids': [self.wh1_geo1.id],
                }
            ]
        )

        self.assertEqual(
            sch5.get_delivery_dates(wd[4]),
            [
                (wd[0], wd[1]),
                (wd[1], wd[0] + timedelta(days=7)),
            ],
            'если заказ в пт, то делаем заказ на пн (+3 дня) и '
            'на вт, так как сб и вс не принимают заказы'
        )

    def _sheds(self, vendor):
        return [
            # базовый график
            {
                'vendor_id': vendor.id,
                'days_before_order': 1,
                'delivery_weekday_0': True,
                'delivery_weekday_1': True,
                'delivery_weekday_2': True,
                'delivery_weekday_3': True,
                'delivery_weekday_4': True,
                'delivery_weekday_5': True,
                'delivery_weekday_6': True,
                'warehouse_ids': [self.wh1_geo1.id],
            },
            # график на товарную группу
            {
                'vendor_id': vendor.id,
                'days_before_order': 1,
                'delivery_weekday_0': True,
                'delivery_weekday_1': True,
                'delivery_weekday_2': True,
                'delivery_weekday_3': True,
                'delivery_weekday_4': True,
                'delivery_weekday_5': True,
                'delivery_weekday_6': True,
                'product_tag_ids': [self.p_tag_abc_group_a.id],
                'warehouse_ids': [self.wh1_geo1.id],
            },
            # график на несколько товарных групп
            {
                'vendor_id': vendor.id,
                'days_before_order': 1,
                'delivery_weekday_0': True,
                'delivery_weekday_1': True,
                'delivery_weekday_2': True,
                'delivery_weekday_3': True,
                'delivery_weekday_4': True,
                'delivery_weekday_5': True,
                'delivery_weekday_6': True,
                'product_tag_ids': [
                    self.p_tag_abc_group_a.id,
                    self.p_tag_storage_type_warm.id,
                    self.p_tag_nonfood_nonfood.id,
                ],
                'warehouse_ids': [self.wh1_geo1.id],
            },
            # график на группу складов
            {
                'vendor_id': vendor.id,
                'days_before_order': 1,
                'delivery_weekday_0': True,
                'delivery_weekday_1': True,
                'delivery_weekday_2': True,
                'delivery_weekday_3': True,
                'delivery_weekday_4': True,
                'delivery_weekday_5': True,
                'delivery_weekday_6': True,
                'warehouse_tag_ids': [
                    self.wh_tag_geo1.id,
                    self.wh_tag_geo2.id,
                    self.wh_tag_geo3.id,
                ],
            },
            # график на группу складов + товарную группу
            {
                'vendor_id': vendor.id,
                'days_before_order': 1,
                'delivery_weekday_0': True,
                'delivery_weekday_1': True,
                'delivery_weekday_2': True,
                'delivery_weekday_3': True,
                'delivery_weekday_4': True,
                'delivery_weekday_5': True,
                'delivery_weekday_6': True,
                'warehouse_tag_ids': [self.wh_tag_geo1.id],
                'product_tag_ids': [self.p_tag_nonfood_nonfood.id],
            },
            # график на группу складов + несколько товарных групп
            {
                'vendor_id': vendor.id,
                'days_before_order': 1,
                'delivery_weekday_0': True,
                'delivery_weekday_1': True,
                'delivery_weekday_2': True,
                'delivery_weekday_3': True,
                'delivery_weekday_4': True,
                'delivery_weekday_5': True,
                'delivery_weekday_6': True,
                'warehouse_tag_ids': [self.wh_tag_geo1.id],
                'product_tag_ids': [
                    self.p_tag_abc_group_a.id,
                    self.p_tag_storage_type_chem.id,
                ],
            },
            # график на склад
            {
                'vendor_id': vendor.id,
                'days_before_order': 1,
                'delivery_weekday_0': True,
                'delivery_weekday_1': True,
                'delivery_weekday_2': True,
                'delivery_weekday_3': True,
                'delivery_weekday_4': True,
                'delivery_weekday_5': True,
                'delivery_weekday_6': True,
                'warehouse_ids': [self.wh1_geo1.id],
            },
            # график на склад + товарную группу
            {
                'vendor_id': vendor.id,
                'days_before_order': 1,
                'delivery_weekday_0': True,
                'delivery_weekday_1': True,
                'delivery_weekday_2': True,
                'delivery_weekday_3': True,
                'delivery_weekday_4': True,
                'delivery_weekday_5': True,
                'delivery_weekday_6': True,
                'warehouse_ids': [self.wh1_geo1.id],
                'product_tag_ids': [self.p_tag_abc_group_a.id],
            },
            # график на склад + несколько товарных групп + чёт
            {
                'vendor_id': vendor.id,
                'days_before_order': 1,
                'delivery_weekday_0': False,
                'delivery_weekday_1': True,
                'delivery_weekday_2': False,
                'delivery_weekday_3': True,
                'delivery_weekday_4': False,
                'delivery_weekday_5': True,
                'delivery_weekday_6': False,
                'week_type': 'even',
                'warehouse_ids': [self.wh1_geo1.id],
                'product_tag_ids': [
                    self.p_tag_abc_group_a.id,
                    self.p_tag_nonfood_food.id,
                ],
            },
            # график на склад + несколько товарных групп + нечет
            {
                'vendor_id': vendor.id,
                'days_before_order': 1,
                'delivery_weekday_0': True,
                'delivery_weekday_1': False,
                'delivery_weekday_2': True,
                'delivery_weekday_3': False,
                'delivery_weekday_4': True,
                'delivery_weekday_5': False,
                'delivery_weekday_6': True,
                'week_type': 'odd',
                'warehouse_ids': [self.wh1_geo1.id],
                'product_tag_ids': [
                    self.p_tag_abc_group_a.id,
                    self.p_tag_nonfood_food.id,
                ],
            },
            # график на склад + несколько товарных групп + только нечет
            {
                'vendor_id': vendor.id,
                'days_before_order': 1,
                'delivery_weekday_0': True,
                'delivery_weekday_1': False,
                'delivery_weekday_2': True,
                'delivery_weekday_3': False,
                'delivery_weekday_4': True,
                'delivery_weekday_5': False,
                'delivery_weekday_6': True,
                'week_type': 'odd',
                'warehouse_ids': [self.wh1_geo1.id],
                'product_tag_ids': [
                    self.p_tag_abc_group_a.id,
                    self.p_tag_nonfood_food.id,
                ],
            },
        ]

    def test_002_schedules_sort_by_rank(self):
        ds = self.env['autoorder.delivery.schedule']

        _scheds = self._sheds(self.v1)

        # для надежности
        shuffle(_scheds)
        shuffle(_scheds)
        shuffle(_scheds)

        scheds = ds.create(_scheds)

        r = ds.schedules_sort_by_rank(scheds)

        self.assertEqual(r[0].rank, 3001000)
        self.assertFalse(r[0].product_tag_ids)
        self.assertTrue(r[0].warehouse_tag_ids)
        self.assertFalse(r[0].warehouse_ids)

        self.assertEqual(r[1].rank, 4001001)
        self.assertTrue(r[1].product_tag_ids)
        self.assertTrue(r[1].warehouse_tag_ids)
        self.assertFalse(r[1].warehouse_ids)

        self.assertEqual(r[2].rank, 4001110)
        self.assertEqual(len(r[2].product_tag_ids), 2)
        self.assertTrue(r[2].warehouse_tag_ids)
        self.assertFalse(r[2].warehouse_ids)

        self.assertEqual(r[3].rank, 5010000)
        self.assertFalse(r[3].product_tag_ids)
        self.assertFalse(r[3].warehouse_tag_ids)
        self.assertTrue(r[3].warehouse_ids)

        self.assertEqual(r[4].rank, 5010000)
        self.assertFalse(r[4].product_tag_ids)
        self.assertFalse(r[4].warehouse_tag_ids)
        self.assertTrue(r[4].warehouse_ids)

        self.assertEqual(r[5].rank, 6010100)
        self.assertEqual(len(r[5].product_tag_ids), 1)
        self.assertFalse(r[5].warehouse_tag_ids)
        self.assertTrue(r[5].warehouse_ids)

        self.assertEqual(r[6].rank, 6010100)
        self.assertTrue(r[6].product_tag_ids)
        self.assertFalse(r[6].warehouse_tag_ids)
        self.assertTrue(r[6].warehouse_ids)

        self.assertEqual(r[7].rank, 6010111)
        self.assertTrue(r[7].product_tag_ids)
        self.assertFalse(r[7].warehouse_tag_ids)
        self.assertTrue(r[7].warehouse_ids)

        self.assertEqual(r[8].rank, 6110101)
        self.assertEqual(len(r[8].product_tag_ids), 2)
        self.assertFalse(r[8].warehouse_tag_ids)
        self.assertTrue(r[8].warehouse_ids)

    def test_003_fixtures(self):
        ds = self.env['autoorder.delivery.schedule']

        v1_contracts = self.env['purchase.requisition'].search([('vendor_id', '=', self.v1.id)])

        self.assertEqual(len(v1_contracts), 1, 'один контракт')

        v1_contract1 = v1_contracts[0]
        v1_contract1_whs = self.env['stock.warehouse'].search(
            [
                ('warehouse_tag_ids', 'in', v1_contract1.warehouse_tag_ids.ids),
            ]
        )
        v1_contract1_products = v1_contract1.line_ids.product_id

        self.assertEqual(
            set(v1_contract1_whs), set([self.wh1_geo1, self.wh2_geo1]), '2 лавки',
        )
        self.assertEqual(
            set(v1_contract1_products), set([self.p_base_water, self.p_base_soap]), '2 товара',
        )

        scheds = ds.schedules_sort_by_rank(ds.create(self._sheds(self.v1)))

        self.assertEqual(scheds[0].rank, 3001000)

        # график на все лавки/товары поставщика

        f3 = scheds[3].get_fixtures(date(1970, 1, 1))

        self.assertEqual(len(f3), 2, '1 лавка x 2 товара')
        self.assertIn(
            (self.wh1_geo1.code, self.p_base_water.default_code, self.v1.external_id), f3,
        )
        self.assertIn(
            (self.wh1_geo1.code, self.p_base_soap.default_code, self.v1.external_id), f3,
        )

        # график на все лавки + сужение до товарной группы

        f1 = scheds[1].get_fixtures(date(1970, 1, 1))

        self.assertEqual(len(f1), 2, '2 лавки x 1 товар в группе а -- вода')
        self.assertIn(
            (self.wh1_geo1.code, self.p_base_soap.default_code, self.v1.external_id), f1,
        )

        # график с набором товарных групп для которых товаров не найдется

        f2 = scheds[2].get_fixtures(date(1970, 1, 1))

        self.assertEqual(len(f2), 0, 'нет товаров подходящих')

        # график на группы лавок без указания товарных групп

        f0 = scheds[0].get_fixtures(date(1970, 1, 1))

        self.assertEqual(len(f0), 4, '2 лавки x 2 товара')

        # график на группы лавок с сужением по товарным группам

        f4 = scheds[4].get_fixtures(date(1970, 1, 1))

        self.assertEqual(len(f4), 2, '2 лавки x 1 товар')
        self.assertIn(
            (self.wh1_geo1.code, self.p_base_soap.default_code, self.v1.external_id), f4,
        )
        self.assertIn(
            (self.wh1_geo1.code, self.p_base_water.default_code, self.v1.external_id), f4,
        )

        # график на группы лавок и товарные группы для которых нет товаров

        f7 = scheds[7].get_fixtures(date(1970, 1, 1))

        self.assertEqual(len(f7), 0, 'нет товаров подходящих')

        # график на конкретную лавку

        f4 = scheds[4].get_fixtures(date(1970, 1, 1))

        self.assertEqual(len(f4), 2, '1 лавка x 2 товара')
        self.assertIn(
            (self.wh1_geo1.code, self.p_base_water.default_code, self.v1.external_id), f4,
        )
        self.assertIn(
            (self.wh1_geo1.code, self.p_base_soap.default_code, self.v1.external_id), f4,
        )

        # график на конкретную лавку + товарную группу

        f5 = scheds[5].get_fixtures(date(1970, 1, 1))

        self.assertEqual(len(f5), 1, '1 лавка x 1 товар')
        self.assertIn(
            (self.wh1_geo1.code, self.p_base_water.default_code, self.v1.external_id), f5,
        )

    def test_004_vendor_fixtures(self):
        ds = self.env['autoorder.delivery.schedule']

        scheds = ds.schedules_sort_by_rank(ds.create(self._sheds(self.v1)))
        self.assertEqual(len(scheds), 11, '11 графиков')

        f = self.v1.get_delivery_schedule_fixtures(date(1970, 1, 1))

        self.assertEqual(len(f), 4, '2 лавки x 2 товара')
        self.assertIn(
            (self.wh1_geo1.code, self.p_base_water.default_code, self.v1.external_id), f,
        )
        self.assertIn(
            (self.wh1_geo1.code, self.p_base_soap.default_code, self.v1.external_id), f,
        )
        self.assertIn(
            (self.wh2_geo1.code, self.p_base_water.default_code, self.v1.external_id), f,
        )
        self.assertIn(
            (self.wh2_geo1.code, self.p_base_soap.default_code, self.v1.external_id), f,
        )

    def test_005_vendor_fixtures(self):
        ds = self.env['autoorder.delivery.schedule']
        dsf = self.env['autoorder.delivery.schedule.fixture']

        scheds = ds.create(self._sheds(self.v1)[0])
        self.assertEqual(len(scheds), 1, '1 график')

        f = self.v1.get_delivery_schedule_fixtures(date(1970, 1, 1))

        self.assertEqual(len(f), 2, '1 лавка x 2 товара')
        self.assertEqual(
            f[(self.wh1_geo1.code, self.p_base_water.default_code, self.v1.external_id)],
            [(date(1970, 1, 1), date(1970, 1, 2), date(1970, 1, 3))],
            'order_date,delivery_date,next_delivery_date',
        )

        scheds[0].update({
                'fixture_start_date': date(1970, 1, 1),
                'fixture_end_date': date(1970, 1, 3),
        })

        dsf.create(
            [
                {
                    'delivery_schedule_id': scheds[0].id,
                    'order_date': date(1970, 1, 1),
                    'delivery_date': date(1970, 1, 3),
                },
            ]
        )

        self.assertEqual(
            dsf.search_count(
                [
                    ('delivery_schedule_id', '=', scheds[0].id),
                    ('order_date', '=', date(1970, 1, 1)),
                ]
            ),
            1,
            'одно исключение создалось',
        )

        f = self.v1.get_delivery_schedule_fixtures(date(1970, 1, 1))
        self.assertEqual(len(f), 2, '1 лавка x 2 товара')
        self.assertEqual(
            [i for i in f.values()],
            [[(date(1970, 1, 1), date(1970, 1, 3), date(1970, 1, 4))]] * 2,
            'даты доставки забиты гвоздями',
        )

    def test_weeks(self):
        ds = self.env['autoorder.delivery.schedule']

        scheds = ds.create(self._sheds(self.v1)[8:10])
        self.assertEqual(len(scheds), 2, '2 графика')

        # четверг, нечетная неделя, работает второй график
        # поставка в пятницу и воскресенье
        f = self.v1.get_delivery_schedule_fixtures(date(1970, 1, 1))

        self.assertEqual(len(f), 1, '1 лавка x 1 товар')
        self.assertEqual(
            [i for i in f.values()],
            [[(date(1970, 1, 1), date(1970, 1, 2), date(1970, 1, 4))]],
            'дата второй поставки на этой же неделе графика с четностью',
        )

        # суббота, нечетная неделя, работает второй график
        # поставка в воскресенье, следующая во вторник на четной неделе.
        f = self.v1.get_delivery_schedule_fixtures(date(1970, 1, 3))

        self.assertEqual(len(f), 1, '1 лавка x 1 товар')
        self.assertEqual(
            [i for i in f.values()],
            [[(date(1970, 1, 3), date(1970, 1, 4), date(1970, 1, 6))]],
            'дата второй поставки на сл. неделе графика с четностью',
        )


        scheds = ds.create(self._sheds(self.v2)[10])
        self.assertEqual(len(scheds), 1, '1 график')

        # суббота, нечетная неделя, работает второй график
        # поставка в воскресенье, следующая во вторник на четной неделе.
        f = self.v2.get_delivery_schedule_fixtures(date(1970, 1, 3))

        self.assertEqual(len(f), 1, '1 лавка x 1 товар')
        self.assertEqual(
            [i for i in f.values()],
            [[(date(1970, 1, 3), date(1970, 1, 4), date(1970, 1, 12))]],
            'дата второй поставки через неделю графика только с четностью',
        )

@tagged('lavka', 'autoorder', 'delivery_schedule', 'delivery_schedule_modern')
class TestDeliveryScheduleModern(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.p_tag_assort_base = cls.env['product.tag'].create(
            {
                'type': 'assortment',
                'name': 'base',
            }
        )
        cls.p_tag_assort_lux = cls.env['product.tag'].create(
            {
                'type': 'assortment',
                'name': 'lux',
            }
        )
        cls.p_tag_assort_budget = cls.env['product.tag'].create(
            {
                'type': 'assortment',
                'name': 'budget',
            }
        )

        cls.p_tag_abc_group_a = cls.env['product.tag'].create(
            {
                'type': 'abc_group',
                'name': 'a',
            }
        )
        cls.p_tag_abc_group_b = cls.env['product.tag'].create(
            {
                'type': 'abc_group',
                'name': 'b',
            }
        )

        cls.p_tag_storage_type_warm = cls.env['product.tag'].create(
            {
                'type': 'storage_type',
                'name': 'test_warm',
            }
        )
        cls.p_tag_storage_type_chem = cls.env['product.tag'].create(
            {
                'type': 'storage_type',
                'name': 'chem',
            }
        )

        cls.p_tag_nonfood_food = cls.env['product.tag'].create(
            {
                'type': 'nonfood',
                'name': 'food300',
            }
        )

        cls.p_tag_nonfood_nonfood = cls.env['product.tag'].create(
            {
                'type': 'nonfood',
                'name': 'nonfood300',
            }
        )

        cls.p_base_water = cls.env['product.product'].create(
            {
                'name': 'water',
                'default_code': '100',
                'wms_id': '100',
                'product_tag_ids': [
                    cls.p_tag_assort_base.id,
                    cls.p_tag_abc_group_a.id,
                    cls.p_tag_storage_type_warm.id,
                    cls.p_tag_nonfood_food.id,
                ]
            },
        )
        cls.p_base_soap = cls.env['product.product'].create(
            {
                'name': 'soap',
                'default_code': '200',
                'wms_id': '200',
                'product_tag_ids': [
                    cls.p_tag_assort_base.id,
                    cls.p_tag_abc_group_b.id,
                    cls.p_tag_storage_type_chem.id,
                    cls.p_tag_nonfood_nonfood.id,
                ]
            },
        )
        cls.p_lux_water = cls.env['product.product'].create(
            {
                'name': 'lux water',
                'default_code': '110',
                'wms_id': '110',
                'product_tag_ids': [
                    cls.p_tag_assort_lux.id,
                    cls.p_tag_storage_type_warm.id,
                    cls.p_tag_nonfood_food.id,
                ]
            },
        )
        cls.p_budget_water = cls.env['product.product'].create(
            {
                'name': 'budget water',
                'default_code': '120',
                'wms_id': '120',
                'product_tag_ids': [
                    cls.p_tag_assort_budget.id,
                    cls.p_tag_storage_type_warm.id,
                    cls.p_tag_nonfood_food.id,
                ]
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
                'product_tag_ids': [
                    cls.p_tag_assort_base.id,
                    cls.p_tag_assort_lux.id,
                    cls.p_tag_assort_budget.id,
                ],
            }
        )
        cls.wh2_geo1 = cls.env['stock.warehouse'].create(
            {
                'name': 'l-002',
                'code': 'l-002',
                'warehouse_tag_ids': [
                    cls.wh_tag_geo1.id,
                ],
                'product_tag_ids': [
                    cls.p_tag_assort_base.id,
                    cls.p_tag_assort_lux.id,
                ],
            }
        )
        cls.wh3_geo2 = cls.env['stock.warehouse'].create(
            {
                'name': 'l-003',
                'code': 'l-003',
                'warehouse_tag_ids': [
                    cls.wh_tag_geo2.id,
                ],
                'product_tag_ids': [
                    cls.p_tag_assort_base.id,
                    cls.p_tag_assort_budget.id,
                ],
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

        cls.v1 = cls.env['res.partner'].create(
            {
                'name': 'v-001: assort_base',
                'is_company': True,
                'supplier_rank': 1,
            }
        )
        cls.v1_contract1 = cls.env['purchase.requisition'].create(
            {
                'vendor_id': cls.v1.id,
                'state': 'open',
                'warehouse_tag_ids': [
                    cls.wh_tag_geo1.id,
                ],
            }
        )
        with freeze_time('1970-01-01 00:00:00'):
            cls.env['purchase.requisition.line'].create(
                [
                    {
                        'requisition_id': cls.v1_contract1.id,
                        'product_id': p.id,
                        'start_date': fields.Datetime.today(),
                        'tax_id': p.supplier_taxes_id.id,
                        'product_uom_id': p.uom_id.id,
                        'price_unit': 300 + randrange(1, 3),
                        'product_qty': 1,
                        'product_code': f'code-{p.id}',
                        'product_name': 'vendor product name',
                        'qty_multiple': 1,
                        'approve': True,
                        'approve_price': True,
                        'approve_tax': True,
                        'active': True,
                    }
                    for p in [cls.p_base_water, cls.p_base_soap]
                ]
            )

            cls.v2 = cls.env['res.partner'].create(
                {
                    'name': 'v-002',
                    'is_company': True,
                    'supplier_rank': 1,
                }
            )
            cls.v2_contract1 = cls.env['purchase.requisition'].create(
                {
                    'vendor_id': cls.v2.id,
                    'state': 'open',
                    'warehouse_tag_ids': [
                        cls.wh_tag_geo1.id,
                        cls.wh_tag_geo2.id,
                        cls.wh_tag_geo3.id,
                    ],
                }
            )
            cls.env['purchase.requisition.line'].create(
                [
                    {
                        'requisition_id': cls.v2_contract1.id,
                        'product_id': p.id,
                        'start_date': fields.Datetime.today(),
                        'tax_id': p.supplier_taxes_id.id,
                        'product_uom_id': p.uom_id.id,
                        'price_unit': 300 + randrange(1, 3),
                        'product_qty': 1,
                        'product_code': f'code-{p.id}',
                        'product_name': 'vendor product name',
                        'qty_multiple': 1,
                        'approve': True,
                        'approve_price': True,
                        'approve_tax': True,
                        'active': True,
                    }
                    for p in [cls.p_base_water, cls.p_base_soap]
                ]
            )

            cls.v3 = cls.env['res.partner'].create(
                {
                    'name': 'v-003',
                    'is_company': True,
                    'supplier_rank': 1,
                }
            )
            cls.v3_contract1 = cls.env['purchase.requisition'].create(
                {
                    'vendor_id': cls.v3.id,
                    'state': 'open',
                    'warehouse_tag_ids': [
                        cls.wh_tag_geo1.id,
                        cls.wh_tag_geo2.id,
                        cls.wh_tag_geo3.id,
                    ],
                }
            )
            cls.env['purchase.requisition.line'].create(
                [
                    {
                        'requisition_id': cls.v3_contract1.id,
                        'product_id': p.id,
                        'start_date': fields.Datetime.today(),
                        'tax_id': p.supplier_taxes_id.id,
                        'product_uom_id': p.uom_id.id,
                        'price_unit': 300 + randrange(1, 3),
                        'product_qty': 1,
                        'product_code': f'code-{p.id}',
                        'product_name': 'vendor product name',
                        'qty_multiple': 1,
                        'approve': True,
                        'approve_price': True,
                        'approve_tax': True,
                        'active': True,
                    }
                    for p in [cls.p_lux_water]
                ]
            )

            cls.v4 = cls.env['res.partner'].create(
                {
                    'name': 'v-004',
                    'is_company': True,
                    'supplier_rank': 1,
                }
            )
            cls.v4_contract1 = cls.env['purchase.requisition'].create(
                {
                    'vendor_id': cls.v4.id,
                    'state': 'open',
                    'warehouse_tag_ids': [
                        cls.wh_tag_geo1.id,
                        cls.wh_tag_geo2.id,
                        cls.wh_tag_geo3.id,
                    ],
                }
            )
            cls.env['purchase.requisition.line'].create(
                [
                    {
                        'requisition_id': cls.v4_contract1.id,
                        'product_id': p.id,
                        'start_date': fields.Datetime.today(),
                        'tax_id': p.supplier_taxes_id.id,
                        'product_uom_id': p.uom_id.id,
                        'price_unit': 300 + randrange(1, 3),
                        'product_qty': 1,
                        'product_code': f'code-{p.id}',
                        'product_name': 'vendor product name',
                        'qty_multiple': 1,
                        'approve': True,
                        'approve_price': True,
                        'approve_tax': True,
                        'active': True,
                    }
                    for p in [cls.p_budget_water]
                ]
            )
            for line in cls.env['purchase.requisition.line'].search([]):
                line._compute_approve()

    def test_01_products(self):
        assort_base = self.env['product.product'].search(
            [
                ('product_tag_ids', 'in', self.p_tag_assort_base.ids),
            ]
        )
        self.assertIn(self.p_base_water, assort_base)
        self.assertIn(self.p_base_soap, assort_base)

        assort_lux = self.env['product.product'].search(
            [
                ('product_tag_ids', 'in', self.p_tag_assort_lux.ids),
            ]
        )
        self.assertIn(self.p_lux_water, assort_lux)

        assort_budget = self.env['product.product'].search(
            [
                ('product_tag_ids', 'in', self.p_tag_assort_budget.ids),
            ]
        )
        self.assertIn(self.p_budget_water, assort_budget)

    def test_001_x_weekdays(self):
        sch = self.env['autoorder.delivery.schedule'].create(
            [
                {
                    'vendor_id': self.v1.id,
                    'days_before_order': 1,
                    'delivery_weekday_0': True,
                    'delivery_weekday_6': True,
                    'order_weekday_0': False,
                    'order_weekday_6': False,
                    'week_type': '',
                    'warehouse_ids': [self.wh1_geo1.id],
                }
            ]
        )

        self.assertEqual(
            sch.delivery_weekdays(),
            (True, False, False, False, False, False, True),
            'correct delivery weekdays',
        )
        self.assertEqual(
            sch.order_weekdays(),
            (False, True, True, True, True, True, False),
            'correct order weekdays',
        )

    def test_001_get_delivery_dates(self):
        wd = {
            date(1970, 1, i).weekday(): date(1970, 1, i)
            for i in range(1, 8)
        }

        sch1 = self.env['autoorder.delivery.schedule'].create(
            [
                {
                    'vendor_id': self.v1.id,
                    'days_before_order': 1,
                    'warehouse_ids': [self.wh1_geo1.id],
                }
            ]
        )
        self.assertEqual(
            [sch1.get_delivery_dates(i) for i in wd.values()],
            [[]] * 7,
            'дни поставок не заданы',
        )

        sch2 = self.env['autoorder.delivery.schedule'].create(
            [
                {
                    'vendor_id': self.v1.id,
                    'days_before_order': 1,
                    'order_weekday_0': False,
                    'delivery_weekday_0': True,
                    'delivery_weekday_1': True,
                    'delivery_weekday_2': True,
                    'delivery_weekday_3': True,
                    'delivery_weekday_4': True,
                    'delivery_weekday_5': True,
                    'delivery_weekday_6': True,
                    'warehouse_ids': [self.wh1_geo1.id],
                }
            ]
        )
        self.assertEqual(
            sch2.get_delivery_dates(wd[0]),
            [],
            'по понедельникам заказы не принимаются',
        )
        self.assertTrue(
            all([sch2.get_delivery_dates(v) for k, v in wd.items() if k > 0]),
            'со вторника по субботу заказы принимаются',
        )

        sch3 = self.env['autoorder.delivery.schedule'].create(
            [
                {
                    'vendor_id': self.v1.id,
                    'days_before_order': 1,
                    'delivery_weekday_0': True,
                    'delivery_weekday_2': True,
                    'delivery_weekday_4': True,
                    'warehouse_ids': [self.wh1_geo1.id],
                }
            ]
        )
        self.assertEqual(
            sch3.get_delivery_dates(wd[0]),
            [],
            'если заказ в понедельник, то доставки на вторник нет (+1 день)',
        )
        self.assertEqual(
            sch3.get_delivery_dates(wd[1]),
            [(wd[2], wd[2] + timedelta(days=2))],
            'если заказ во вторник, то есть доставка на среду и следующая доставка на пятницу (+2 дня)',
        )
        self.assertEqual(
            sch3.get_delivery_dates(wd[3]),
            [(wd[4], wd[4] + timedelta(days=3))],
            'если заказ в четверг, то есть доставка на пятницу и следующая доставка на понедельник (+3 дня)',
        )

        sch4 = self.env['autoorder.delivery.schedule'].create(
            [
                {
                    'vendor_id': self.v1.id,
                    'days_before_order': 7,
                    'delivery_weekday_0': True,
                    'warehouse_ids': [self.wh1_geo1.id],
                }
            ]
        )
        self.assertEqual(
            sch4.get_delivery_dates(wd[0]),
            [(wd[0] + timedelta(days=7), wd[0] + timedelta(days=14))],
            'если заказ в понедельник, то доставка на след понедельник',
        )
        self.assertEqual(
            sch4.get_delivery_dates(wd[1]),
            [],
            'если заказ во вторник, то уже нет доставки',
        )

        sch5 = self.env['autoorder.delivery.schedule'].create(
            [
                {
                    'vendor_id': self.v1.id,
                    'days_before_order': 3,
                    'delivery_weekday_0': True,
                    'delivery_weekday_1': True,
                    'order_weekday_5': False,
                    'order_weekday_6': False,
                    'warehouse_ids': [self.wh1_geo1.id],
                }
            ]
        )

        self.assertEqual(
            sch5.get_delivery_dates(wd[4]),
            [
                (wd[0], wd[1]),
                (wd[1], wd[0] + timedelta(days=7)),
            ],
            'если заказ в пт, то делаем заказ на пн (+3 дня) и '
            'на вт, так как сб и вс не принимают заказы'
        )

    def _sheds(self, vendor):
        return [
            # базовый график
            {
                'vendor_id': vendor.id,
                'days_before_order': 1,
                'delivery_weekday_0': True,
                'delivery_weekday_1': True,
                'delivery_weekday_2': True,
                'delivery_weekday_3': True,
                'delivery_weekday_4': True,
                'delivery_weekday_5': True,
                'delivery_weekday_6': True,
                'warehouse_ids': [self.wh1_geo1.id],
            },
            # график на товарную группу
            {
                'vendor_id': vendor.id,
                'days_before_order': 1,
                'delivery_weekday_0': True,
                'delivery_weekday_1': True,
                'delivery_weekday_2': True,
                'delivery_weekday_3': True,
                'delivery_weekday_4': True,
                'delivery_weekday_5': True,
                'delivery_weekday_6': True,
                'product_tag_ids': [self.p_tag_abc_group_a.id],
                'warehouse_ids': [self.wh1_geo1.id],
            },
            # график на несколько товарных групп
            {
                'vendor_id': vendor.id,
                'days_before_order': 1,
                'delivery_weekday_0': True,
                'delivery_weekday_1': True,
                'delivery_weekday_2': True,
                'delivery_weekday_3': True,
                'delivery_weekday_4': True,
                'delivery_weekday_5': True,
                'delivery_weekday_6': True,
                'product_tag_ids': [
                    self.p_tag_abc_group_a.id,
                    self.p_tag_storage_type_warm.id,
                    self.p_tag_nonfood_nonfood.id,
                ],
                'warehouse_ids': [self.wh1_geo1.id],
            },
            # график на группу складов
            {
                'vendor_id': vendor.id,
                'days_before_order': 1,
                'delivery_weekday_0': True,
                'delivery_weekday_1': True,
                'delivery_weekday_2': True,
                'delivery_weekday_3': True,
                'delivery_weekday_4': True,
                'delivery_weekday_5': True,
                'delivery_weekday_6': True,
                'warehouse_tag_ids': [
                    self.wh_tag_geo1.id,
                    self.wh_tag_geo2.id,
                    self.wh_tag_geo3.id,
                ],
            },
            # график на группу складов + товарную группу
            {
                'vendor_id': vendor.id,
                'days_before_order': 1,
                'delivery_weekday_0': True,
                'delivery_weekday_1': True,
                'delivery_weekday_2': True,
                'delivery_weekday_3': True,
                'delivery_weekday_4': True,
                'delivery_weekday_5': True,
                'delivery_weekday_6': True,
                'warehouse_tag_ids': [self.wh_tag_geo1.id],
                'product_tag_ids': [self.p_tag_nonfood_nonfood.id],
            },
            # график на группу складов + несколько товарных групп
            {
                'vendor_id': vendor.id,
                'days_before_order': 1,
                'delivery_weekday_0': True,
                'delivery_weekday_1': True,
                'delivery_weekday_2': True,
                'delivery_weekday_3': True,
                'delivery_weekday_4': True,
                'delivery_weekday_5': True,
                'delivery_weekday_6': True,
                'warehouse_tag_ids': [self.wh_tag_geo1.id],
                'product_tag_ids': [
                    self.p_tag_abc_group_a.id,
                    self.p_tag_storage_type_chem.id,
                ],
            },
            # график на склад
            {
                'vendor_id': vendor.id,
                'days_before_order': 1,
                'delivery_weekday_0': True,
                'delivery_weekday_1': True,
                'delivery_weekday_2': True,
                'delivery_weekday_3': True,
                'delivery_weekday_4': True,
                'delivery_weekday_5': True,
                'delivery_weekday_6': True,
                'warehouse_ids': [self.wh1_geo1.id],
            },
            # график на склад + товарную группу
            {
                'vendor_id': vendor.id,
                'days_before_order': 1,
                'delivery_weekday_0': True,
                'delivery_weekday_1': True,
                'delivery_weekday_2': True,
                'delivery_weekday_3': True,
                'delivery_weekday_4': True,
                'delivery_weekday_5': True,
                'delivery_weekday_6': True,
                'warehouse_ids': [self.wh1_geo1.id],
                'product_tag_ids': [self.p_tag_abc_group_a.id],
            },
            # график на склад + несколько товарных групп + чёт
            {
                'vendor_id': vendor.id,
                'days_before_order': 1,
                'delivery_weekday_0': False,
                'delivery_weekday_1': True,
                'delivery_weekday_2': False,
                'delivery_weekday_3': True,
                'delivery_weekday_4': False,
                'delivery_weekday_5': True,
                'delivery_weekday_6': False,
                'week_type': 'even',
                'warehouse_ids': [self.wh1_geo1.id],
                'product_tag_ids': [
                    self.p_tag_abc_group_a.id,
                    self.p_tag_nonfood_food.id,
                ],
            },
            # график на склад + несколько товарных групп + нечет
            {
                'vendor_id': vendor.id,
                'days_before_order': 1,
                'delivery_weekday_0': True,
                'delivery_weekday_1': False,
                'delivery_weekday_2': True,
                'delivery_weekday_3': False,
                'delivery_weekday_4': True,
                'delivery_weekday_5': False,
                'delivery_weekday_6': True,
                'week_type': 'odd',
                'warehouse_ids': [self.wh1_geo1.id],
                'product_tag_ids': [
                    self.p_tag_abc_group_a.id,
                    self.p_tag_nonfood_food.id,
                ],
            },
            # график на склад + несколько товарных групп + только нечет
            {
                'vendor_id': vendor.id,
                'days_before_order': 1,
                'delivery_weekday_0': True,
                'delivery_weekday_1': False,
                'delivery_weekday_2': True,
                'delivery_weekday_3': False,
                'delivery_weekday_4': True,
                'delivery_weekday_5': False,
                'delivery_weekday_6': True,
                'week_type': 'odd',
                'warehouse_ids': [self.wh1_geo1.id],
                'product_tag_ids': [
                    self.p_tag_abc_group_a.id,
                    self.p_tag_nonfood_food.id,
                ],
            },
        ]

    def test_003_fixtures(self):
        ds = self.env['autoorder.delivery.schedule']

        v1_contracts = self.env['purchase.requisition'].search([('vendor_id', '=', self.v1.id)])

        self.assertEqual(len(v1_contracts), 1, 'один контракт')

        v1_contract1 = v1_contracts[0]
        v1_contract1_whs = self.env['stock.warehouse'].search(
            [
                ('warehouse_tag_ids', 'in', v1_contract1.warehouse_tag_ids.ids),
            ]
        )
        v1_contract1_products = v1_contract1.line_ids.product_id

        self.assertEqual(
            set(v1_contract1_whs), set([self.wh1_geo1, self.wh2_geo1]), '2 лавки',
        )
        self.assertEqual(
            set(v1_contract1_products), set([self.p_base_water, self.p_base_soap]), '2 товара',
        )

        scheds = ds.schedules_sort_by_rank(ds.create(self._sheds(self.v1)))

        self.assertEqual(scheds[0].rank, 3001000)

        # график на все лавки/товары поставщика

        f3 = scheds[3].get_schedules(date(1970, 1, 1))

        self.assertEqual(len(f3), 2, '1 лавка x 2 товара')
        self.assertIn(
            (self.wh1_geo1.code, self.p_base_water.default_code, self.v1.external_id, '', 0, 'direct'), f3,
        )
        self.assertIn(
            (self.wh1_geo1.code, self.p_base_soap.default_code, self.v1.external_id, '', 0, 'direct'), f3,
        )

        # график на все лавки + сужение до товарной группы

        f1 = scheds[1].get_schedules(date(1970, 1, 1))

        self.assertEqual(len(f1), 2, '2 лавки x 1 товар в группе а -- вода')
        self.assertIn(
            (self.wh1_geo1.code, self.p_base_soap.default_code, self.v1.external_id, '', 0, 'direct'), f1,
        )

        # график с набором товарных групп для которых товаров не найдется

        f2 = scheds[2].get_schedules(date(1970, 1, 1))

        self.assertEqual(len(f2), 0, 'нет товаров подходящих')

        # график на группы лавок без указания товарных групп

        f0 = scheds[0].get_schedules(date(1970, 1, 1))

        self.assertEqual(len(f0), 6, '3 лавки x 2 товара')

        # график на группы лавок с сужением по товарным группам

        f4 = scheds[4].get_schedules(date(1970, 1, 1))

        self.assertEqual(len(f4), 2, '2 лавки x 1 товар')
        self.assertIn(
            (self.wh1_geo1.code, self.p_base_soap.default_code, self.v1.external_id, '', 0, 'direct'), f4,
        )
        self.assertIn(
            (self.wh1_geo1.code, self.p_base_water.default_code, self.v1.external_id, '', 0, 'direct'), f4,
        )

        # график на группы лавок и товарные группы для которых нет товаров

        f7 = scheds[7].get_schedules(date(1970, 1, 1))

        self.assertEqual(len(f7), 0, 'нет товаров подходящих')

        # график на конкретную лавку

        f6 = scheds[6].get_schedules(date(1970, 1, 1))

        self.assertEqual(len(f6), 1, '1 лавка x 1 товар')
        self.assertIn(
            (self.wh1_geo1.code, self.p_base_water.default_code, self.v1.external_id, '', 0, 'direct'), f6,
        )

        # график на конкретную лавку + товарную группу

        f5 = scheds[5].get_schedules(date(1970, 1, 1))

        self.assertEqual(len(f5), 1, '1 лавка x 1 товар')
        self.assertIn(
            (self.wh1_geo1.code, self.p_base_water.default_code, self.v1.external_id, '', 0, 'direct'), f5,
        )

@tagged('lavka', 'autoorder', 'delivery_schedule', 'delivery_schedule_delivery_type')
class TestDeliveryScheduleDeliveryType(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.p_tag_assort_base = cls.env['product.tag'].create(
            {
                'type': 'assortment',
                'name': 'base',
            }
        )
        cls.p_tag_assort_lux = cls.env['product.tag'].create(
            {
                'type': 'assortment',
                'name': 'lux',
            }
        )
        cls.p_tag_assort_budget = cls.env['product.tag'].create(
            {
                'type': 'assortment',
                'name': 'budget',
            }
        )

        cls.p_tag_abc_group_a = cls.env['product.tag'].create(
            {
                'type': 'abc_group',
                'name': 'a',
            }
        )
        cls.p_tag_abc_group_b = cls.env['product.tag'].create(
            {
                'type': 'abc_group',
                'name': 'b',
            }
        )

        cls.p_tag_storage_type_warm = cls.env['product.tag'].create(
            {
                'type': 'storage_type',
                'name': 'test_warm',
            }
        )
        cls.p_tag_storage_type_chem = cls.env['product.tag'].create(
            {
                'type': 'storage_type',
                'name': 'chem',
            }
        )

        cls.p_tag_nonfood_food = cls.env['product.tag'].create(
            {
                'type': 'nonfood',
                'name': 'food300',
            }
        )

        cls.p_tag_nonfood_nonfood = cls.env['product.tag'].create(
            {
                'type': 'nonfood',
                'name': 'nonfood300',
            }
        )

        cls.p_base_water = cls.env['product.product'].create(
            {
                'name': 'water',
                'default_code': '100',
                'wms_id': '100',
                'product_tag_ids': [
                    cls.p_tag_assort_base.id,
                    cls.p_tag_abc_group_a.id,
                    cls.p_tag_storage_type_warm.id,
                    cls.p_tag_nonfood_food.id,
                ]
            },
        )
        cls.p_base_soap = cls.env['product.product'].create(
            {
                'name': 'soap',
                'default_code': '200',
                'wms_id': '200',
                'product_tag_ids': [
                    cls.p_tag_assort_base.id,
                    cls.p_tag_abc_group_b.id,
                    cls.p_tag_storage_type_chem.id,
                    cls.p_tag_nonfood_nonfood.id,
                ]
            },
        )
        cls.p_lux_water = cls.env['product.product'].create(
            {
                'name': 'lux water',
                'default_code': '110',
                'wms_id': '110',
                'product_tag_ids': [
                    cls.p_tag_assort_lux.id,
                    cls.p_tag_storage_type_warm.id,
                    cls.p_tag_nonfood_food.id,
                ]
            },
        )
        cls.p_budget_water = cls.env['product.product'].create(
            {
                'name': 'budget water',
                'default_code': '120',
                'wms_id': '120',
                'product_tag_ids': [
                    cls.p_tag_assort_budget.id,
                    cls.p_tag_storage_type_warm.id,
                    cls.p_tag_nonfood_food.id,
                ]
            },
        )

        cls.wh_tag_dc = cls.env['stock.warehouse.tag'].create(
            {
                'type': 'geo',
                'name': 'dc',
            }
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

        cls.wh_dc = cls.env['stock.warehouse'].create(
            {
                'name': 'dc',
                'code': '123',
                'warehouse_tag_ids': [
                    cls.wh_tag_dc.id,
                ],
                'type': 'dc',
            }
        )
        cls.wh1_geo1 = cls.env['stock.warehouse'].create(
            {
                'name': 'l-001',
                'code': '100',
                'warehouse_tag_ids': [
                    cls.wh_tag_geo1.id,
                ],
                'product_tag_ids': [
                    cls.p_tag_assort_base.id,
                    cls.p_tag_assort_lux.id,
                    cls.p_tag_assort_budget.id,
                ],
            }
        )
        cls.wh2_geo1 = cls.env['stock.warehouse'].create(
            {
                'name': 'l-002',
                'code': '200',
                'warehouse_tag_ids': [
                    cls.wh_tag_geo1.id,
                ],
                'product_tag_ids': [
                    cls.p_tag_assort_base.id,
                    cls.p_tag_assort_lux.id,
                ],
            }
        )
        cls.wh3_geo3 = cls.env['stock.warehouse'].create(
            {
                'name': 'l-003',
                'code': '300',
                'warehouse_tag_ids': [
                    cls.wh_tag_geo3.id,
                ],
                'product_tag_ids': [
                    cls.p_tag_assort_base.id,
                    cls.p_tag_assort_budget.id,
                ],
            }
        )

        cls.v1 = cls.env['res.partner'].create(
            {
                'name': 'v-001: assort_base',
                'is_company': True,
                'supplier_rank': 1,
            }
        )
        cls.v1_contract1 = cls.env['purchase.requisition'].create(
            {
                'vendor_id': cls.v1.id,
                'state': 'open',
                'warehouse_tag_ids': [
                    cls.wh_tag_geo1.id,
                ],
            }
        )
        with freeze_time('1970-01-01 00:00:00'):
            cls.env['purchase.requisition.line'].create(
                [
                    {
                        'requisition_id': cls.v1_contract1.id,
                        'product_id': p.id,
                        'start_date': fields.Datetime.today(),
                        'tax_id': p.supplier_taxes_id.id,
                        'product_uom_id': p.uom_id.id,
                        'price_unit': 300 + randrange(1, 3),
                        'product_qty': 1,
                        'product_code': f'code-{p.id}',
                        'product_name': 'vendor product name',
                        'qty_multiple': 1,
                        'approve': True,
                        'approve_price': True,
                        'approve_tax': True,
                        'active': True,
                    }
                    for p in [cls.p_base_water, cls.p_base_soap]
                ]
            )

            cls.v2 = cls.env['res.partner'].create(
                {
                    'name': 'v-002',
                    'is_company': True,
                    'supplier_rank': 1,
                }
            )
            cls.v2_contract1 = cls.env['purchase.requisition'].create(
                {
                    'vendor_id': cls.v2.id,
                    'state': 'open',
                    'warehouse_tag_ids': [
                        cls.wh_tag_geo1.id,
                        cls.wh_tag_geo2.id,
                        cls.wh_tag_geo3.id,
                    ],
                }
            )
            cls.env['purchase.requisition.line'].create(
                [
                    {
                        'requisition_id': cls.v2_contract1.id,
                        'product_id': p.id,
                        'start_date': fields.Datetime.today(),
                        'tax_id': p.supplier_taxes_id.id,
                        'product_uom_id': p.uom_id.id,
                        'price_unit': 300 + randrange(1, 3),
                        'product_qty': 1,
                        'product_code': f'code-{p.id}',
                        'product_name': 'vendor product name',
                        'qty_multiple': 1,
                        'approve': True,
                        'approve_price': True,
                        'approve_tax': True,
                        'active': True,
                    }
                    for p in [cls.p_base_water, cls.p_base_soap]
                ]
            )

        # storage
        supply = cls.env['supply.chain'].create({
            'type_supplier': 'vendor',
            'vendor_id': cls.v1.id,
            'type_destination': 'warehouse',
            'destination_warehouse': cls.wh_dc.id,
            'product_id': cls.p_base_soap.id,
            'changed': True,
        })

        # PBL
        cross = cls.env['cross.dock.pbl'].create({
            'vendor_id': cls.v2.id,
            'type_destination': 'geo',
            'destination_geo':cls.wh_tag_geo1.id,
            'transit_warehouse': cls.wh_dc.id,
            'line_ids': [
                (0, 0, {'day': 'thursday', 'transit_time': 1}),
                (0, 0, {'day': 'thursday', 'transit_time': 2}),
                (0, 0, {'day': 'thursday', 'transit_time': 3}),
                (0, 0, {'day': 'monday', 'transit_time': 1}),
                (0, 0, {'day': 'general', 'transit_time': 1}),
            ],
            'delivery_type': 'dc_pbl',
        })

        supply = cls.env['supply.chain'].create({  # pbl
            'type_supplier': 'vendor',
            'vendor_id': cls.v2.id,
            'type_destination': 'geo',
            'destination_geo':cls.wh_tag_geo1.id,
            'product_id': cls.p_base_soap.id,
            'changed': True,
        })

        cls.schedules = [
            # график direct
            {
                'vendor_id': cls.v1.id,
                'type_supplier': 'vendor',
                'days_before_order': 1,
                'delivery_weekday_0': True,
                'delivery_weekday_1': True,
                'delivery_weekday_2': True,
                'delivery_weekday_3': True,
                'delivery_weekday_4': True,
                'delivery_weekday_5': True,
                'delivery_weekday_6': True,
                'product_tag_ids': [
                    cls.p_tag_abc_group_a.id,
                    cls.p_tag_storage_type_warm.id,
                    cls.p_tag_nonfood_food.id,
                ],
                'warehouse_ids': [cls.wh1_geo1.id],
            },
            # график на DC хранение
            {
                'vendor_id': cls.v1.id,
                'type_supplier': 'vendor',
                'days_before_order': 1,
                'delivery_weekday_0': True,
                'delivery_weekday_1': True,
                'delivery_weekday_2': True,
                'delivery_weekday_3': True,
                'delivery_weekday_4': True,
                'delivery_weekday_5': True,
                'delivery_weekday_6': True,
                'product_tag_ids': [
                    cls.p_tag_abc_group_b.id,
                    cls.p_tag_storage_type_chem.id,
                    cls.p_tag_nonfood_nonfood.id,
                ],
                'warehouse_tag_ids': [cls.wh_tag_dc.id],
            },
            # график развозки с DC
            {
                'distribution_center_id': cls.wh_dc.id,
                'type_supplier': 'dc',
                'days_before_order': 1,
                'delivery_weekday_0': True,
                'delivery_weekday_1': False,
                'delivery_weekday_2': True,
                'delivery_weekday_3': True,
                'delivery_weekday_4': True,
                'delivery_weekday_5': True,
                'delivery_weekday_6': True,
                'warehouse_tag_ids': [
                    cls.wh_tag_geo1.id,
                    cls.wh_tag_geo2.id,
                    cls.wh_tag_geo3.id,
                ],
            },
            # график на DC pbl
            {
                'vendor_id': cls.v2.id,
                'type_supplier': 'vendor',
                'days_before_order': 1,
                'order_weekday_0': True,
                'order_weekday_1': False,
                'order_weekday_2': True,
                'order_weekday_3': False,
                'order_weekday_4': False,
                'order_weekday_5': False,
                'order_weekday_6': False,
                'delivery_weekday_0': True,
                'delivery_weekday_1': False,
                'delivery_weekday_2': False,
                'delivery_weekday_3': True,
                'delivery_weekday_4': False,
                'delivery_weekday_5': False,
                'delivery_weekday_6': False,
                'product_tag_ids': [
                    cls.p_tag_abc_group_b.id,
                    cls.p_tag_storage_type_chem.id,
                    cls.p_tag_nonfood_nonfood.id,
                ],
                'warehouse_tag_ids': [cls.wh_tag_dc.id],
            },
        ]

        cls.result = [
            {'warehouse_id': 123, 'supplier_id': cls.v1.external_id, 'lavka_id': 200, 'order_date': '2022-05-04', 'supply_date': '2022-05-05', 'next_supply_date': '2022-05-06', 'date_of_delivery_to_dc': '', 'lag': 0, 'delivery_type': 'dc_storage'},
            {'warehouse_id': 100, 'supplier_id': cls.v1.external_id, 'lavka_id': 100, 'order_date': '2022-05-04', 'supply_date': '2022-05-05', 'next_supply_date': '2022-05-06', 'date_of_delivery_to_dc': '', 'lag': 0, 'delivery_type': 'direct'},
            {'warehouse_id': 100, 'supplier_id': 123, 'lavka_id': 100, 'order_date': '2022-05-04', 'supply_date': '2022-05-05', 'next_supply_date': '2022-05-06', 'date_of_delivery_to_dc': '', 'lag': 0, 'delivery_type': 'from_dc'},
            {'warehouse_id': 100, 'supplier_id': 123, 'lavka_id': 110, 'order_date': '2022-05-04', 'supply_date': '2022-05-05', 'next_supply_date': '2022-05-06', 'date_of_delivery_to_dc': '', 'lag': 0, 'delivery_type': 'from_dc'},
            {'warehouse_id': 100, 'supplier_id': 123, 'lavka_id': 120, 'order_date': '2022-05-04', 'supply_date': '2022-05-05', 'next_supply_date': '2022-05-06', 'date_of_delivery_to_dc': '', 'lag': 0, 'delivery_type': 'from_dc'},
            {'warehouse_id': 100, 'supplier_id': 123, 'lavka_id': 200, 'order_date': '2022-05-04', 'supply_date': '2022-05-05', 'next_supply_date': '2022-05-06', 'date_of_delivery_to_dc': '', 'lag': 0, 'delivery_type': 'from_dc'},
            {'warehouse_id': 200, 'supplier_id': 123, 'lavka_id': 100, 'order_date': '2022-05-04', 'supply_date': '2022-05-05', 'next_supply_date': '2022-05-06', 'date_of_delivery_to_dc': '', 'lag': 0, 'delivery_type': 'from_dc'},
            {'warehouse_id': 200, 'supplier_id': 123, 'lavka_id': 110, 'order_date': '2022-05-04', 'supply_date': '2022-05-05', 'next_supply_date': '2022-05-06', 'date_of_delivery_to_dc': '', 'lag': 0, 'delivery_type': 'from_dc'},
            {'warehouse_id': 200, 'supplier_id': 123, 'lavka_id': 200, 'order_date': '2022-05-04', 'supply_date': '2022-05-05', 'next_supply_date': '2022-05-06', 'date_of_delivery_to_dc': '', 'lag': 0, 'delivery_type': 'from_dc'},
            {'warehouse_id': 300, 'supplier_id': 123, 'lavka_id': 100, 'order_date': '2022-05-04', 'supply_date': '2022-05-05', 'next_supply_date': '2022-05-06', 'date_of_delivery_to_dc': '', 'lag': 0, 'delivery_type': 'from_dc'},
            {'warehouse_id': 300, 'supplier_id': 123, 'lavka_id': 120, 'order_date': '2022-05-04', 'supply_date': '2022-05-05', 'next_supply_date': '2022-05-06', 'date_of_delivery_to_dc': '', 'lag': 0, 'delivery_type': 'from_dc'},
            {'warehouse_id': 300, 'supplier_id': 123, 'lavka_id': 200, 'order_date': '2022-05-04', 'supply_date': '2022-05-05', 'next_supply_date': '2022-05-06', 'date_of_delivery_to_dc': '', 'lag': 0, 'delivery_type': 'from_dc'},
            {'warehouse_id': 100, 'supplier_id': cls.v2.external_id, 'lavka_id': 200, 'order_date': '2022-05-04', 'supply_date': '2022-05-08', 'next_supply_date': '2022-05-10', 'date_of_delivery_to_dc': '2022-05-05', 'lag': 3, 'delivery_type': 'dc_pbl'},
            {'warehouse_id': 200, 'supplier_id': cls.v2.external_id, 'lavka_id': 200, 'order_date': '2022-05-04', 'supply_date': '2022-05-08', 'next_supply_date': '2022-05-10', 'date_of_delivery_to_dc': '2022-05-05', 'lag': 3, 'delivery_type': 'dc_pbl'},
            {'warehouse_id': 100, 'supplier_id': cls.v2.external_id, 'lavka_id': 200, 'order_date': '2022-05-04', 'supply_date': '2022-05-07', 'next_supply_date': '2022-05-08', 'date_of_delivery_to_dc': '2022-05-05', 'lag': 2, 'delivery_type': 'dc_pbl'},
            {'warehouse_id': 200, 'supplier_id': cls.v2.external_id, 'lavka_id': 200, 'order_date': '2022-05-04', 'supply_date': '2022-05-07', 'next_supply_date': '2022-05-08', 'date_of_delivery_to_dc': '2022-05-05', 'lag': 2, 'delivery_type': 'dc_pbl'},
            {'warehouse_id': 100, 'supplier_id': cls.v2.external_id, 'lavka_id': 200, 'order_date': '2022-05-04', 'supply_date': '2022-05-06', 'next_supply_date': '2022-05-07', 'date_of_delivery_to_dc': '2022-05-05', 'lag': 1, 'delivery_type': 'dc_pbl'},
            {'warehouse_id': 200, 'supplier_id': cls.v2.external_id, 'lavka_id': 200, 'order_date': '2022-05-04', 'supply_date': '2022-05-06', 'next_supply_date': '2022-05-07', 'date_of_delivery_to_dc': '2022-05-05', 'lag': 1, 'delivery_type': 'dc_pbl'}
        ]

    def test_export_schedule(self):
        ds = self.env['autoorder.delivery.schedule']
        scheds_data = self.schedules
        scheds = ds.create(scheds_data)
        export_data = ds.gen_today_schedule(date(2022, 5, 4), True)
        for schedule in export_data:
            schedule.pop('schedule_id', False)

        self.assertEqual(export_data, self.result)

