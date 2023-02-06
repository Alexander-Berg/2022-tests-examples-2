import datetime

from freezegun import freeze_time
from odoo import fields
from odoo.tests import SavepointCase, tagged


@tagged('lavka', 'autoorder', 'yt_export')
class TestExportYT(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

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
                'wms_id': '1',
                'address': 'paris 1, 1, 1',
                'purchase_date': '2021-01-01',
                'open_date': '2021-01-01',
                'employee_start_date': '2021-01-01',
                'active': True,
                'warehouse_tag_ids': [cls.wh_tag1.id],
                'product_tag_ids': [cls.p_tag1.id],
            }
        )

        cls.wh2 = cls.env['stock.warehouse'].create(
            {
                'name': 'wh-2',
                'code': '2',
                'wms_id': '2',
                'address': 'paris 2, 2, 2',
                'purchase_date': '2021-02-02',
                'open_date': '2021-02-02',
                'employee_start_date': '2021-02-02',
                'active': True,
                'warehouse_tag_ids': [cls.wh_tag2.id],
                'product_tag_ids': [cls.p_tag1.id, cls.p_tag2.id],
                'warehouse_analog_id': cls.wh1.id,
                'analog_start_date': '2021-02-02',
                'analog_end_date': '2021-02-02',
            }
        )

        cls.wh3 = cls.env['stock.warehouse'].create(
            {
                'name': 'wh-3',
                'code': '3',
                'wms_id': '3',
                'address': 'paris 3, 3, 3',
                'purchase_date': '2021-03-03',
                'open_date': '2021-03-03',
                'employee_start_date': '2021-03-03',
                'active': True,
                'warehouse_tag_ids': [cls.wh_tag2.id],
                'product_tag_ids': [cls.p_tag2.id],
                'warehouse_analog_id': cls.wh1.id,
                'analog_start_date': '2021-03-03',
                'analog_end_date': '2021-03-03',
                'type': 'dc_external',
            }
        )

        cls.p1 = cls.env['product.product'].create(
            {
                'name': 'p-1',
                'default_code': '1',
                'product_tag_ids': [cls.p_tag1.id],
                'wms_id': '1',
            }
        )

        cls.p2 = cls.env['product.product'].create(
            {
                'name': 'p-2',
                'default_code': '2',
                'product_tag_ids': [cls.p_tag1.id],
                'wms_id': '2',
            }
        )

        cls.p3 = cls.env['product.product'].create(
            {
                'name': 'p-3',
                'default_code': '3',
                'product_tag_ids': [cls.p_tag2.id],
                'wms_id': '3',
            }
        )

        cls.p4 = cls.env['product.product'].create(
            {
                'name': 'p-4',
                'default_code': '4',
                'product_tag_ids': [cls.p_tag2.id],
                'wms_id': '4',
            }
        )

        cls.p5 = cls.env['product.product'].create(
            {
                'name': 'p-5',
                'default_code': '5',
                'product_tag_ids': [cls.p_tag2.id],
                'wms_id': '5',
            }
        )

        cls.v1 = cls.env['res.partner'].create(
            {
                'name': 'v-1',
                'is_company': True,
                'supplier_rank': 1,
                'days_before_filling': 1
            }
        )

        cls.v2 = cls.env['res.partner'].create(
            {
                'name': 'v-2',
                'is_company': True,
                'supplier_rank': 1,
                'days_before_filling': 2,
            }
        )

        cls.pr1 = cls.env['purchase.requisition'].create(
            {
                'vendor_id': cls.v1.id,
                'state': 'ongoing',
                'warehouse_tag_ids': [cls.wh_tag1.id],
                'order_min_amount': 0.0,
                'order_increase': False,
                'order_min_sum_lower_bound': 0,
            }
        )

        cls.pr2 = cls.env['purchase.requisition'].create(
            {
                'vendor_id': cls.v2.id,
                'state': 'ongoing',
                'warehouse_tag_ids': [cls.wh_tag2.id],
                'order_min_amount': 2.0,
                'order_increase': True,
                'order_min_sum_lower_bound': 10,
            }
        )

        products_lines_data = (
            (cls.pr1, cls.p1, 100, 1, 1, True, True, True, True,),
            (cls.pr1, cls.p2, 200, 2, 2, True, True, True, True,),
            (cls.pr2, cls.p3, 300, 3, 3, True, True, True, True,),
            (cls.pr2, cls.p4, 400, 4, 4, True, False, False, True,),
            (cls.pr2, cls.p5, 500, 5, 5, True, True, True, False,),
        )

        cls.env['purchase.requisition.line'].create(
            [
                {
                    'requisition_id': pr.id,
                    'product_id': p.id,
                    'start_date': fields.Datetime.today(),
                    'tax_id': p.supplier_taxes_id.id,
                    'product_uom_id': p.uom_id.id,
                    'price_unit': price,
                    'product_qty': qty,
                    'product_code': f'code-{p.id}',
                    'product_name': 'vendor product name',
                    'qty_multiple': qty_multiple,
                    'approve_price': approve_price,
                    'approve_tax': approve_tax,
                    'approve': approve,
                    'active': active,
                }
                for (pr, p, price, qty, qty_multiple,
                     approve_price, approve_tax, approve, active)
                in products_lines_data
            ]
        )

        cls.now = datetime.datetime.now()
        cls.first_date = cls.now + datetime.timedelta(weeks=1)
        cls.second_date = cls.now + datetime.timedelta(weeks=2)

        cls.po1 = cls.env['purchase.order'].create(
            {
                'requisition_id': cls.pr1.id,
                'partner_id': cls.v1.id,
                'picking_type_id': cls.wh1.in_type_id.id,
                'state': 'sent',
            }
        )

        cls.po2 = cls.env['purchase.order'].create(
            {
                'requisition_id': cls.pr2.id,
                'partner_id': cls.v2.id,
                'picking_type_id': cls.wh2.in_type_id.id,
                'state': 'purchase',
            }
        )

        cls.po3 = cls.env['purchase.order'].create(
            {
                'requisition_id': cls.pr2.id,
                'partner_id': cls.v2.id,
                'picking_type_id': cls.wh2.in_type_id.id,
                'state': 'purchase',
            }
        )

        purchase_order_data = (
            (cls.po1, cls.p1, 1, cls.first_date),
            (cls.po1, cls.p2, 2, cls.first_date),
            (cls.po2, cls.p3, 3, cls.second_date),
            (cls.po3, cls.p3, 3, cls.second_date),
        )

        cls.env['purchase.order.line'].create(
            [
                {
                    'order_id': order.id,
                    'product_id': p.id,
                    'product_init_qty': qty,
                    'date_planned': date,
                }
                for (order, p, qty, date) in purchase_order_data
            ]
        )

        cls.today = datetime.date.today()
        cls.start_date = cls.today - datetime.timedelta(weeks=1)
        cls.end_date = cls.today + datetime.timedelta(weeks=1)

        cls.e1 = cls.env['autoorder.correction.coefficient'].create(
            {
                'start_date': cls.start_date,
                'end_date': cls.end_date,
                'value': 1.0,
                'reason': 'reason 1',
                'product_id': cls.p1.id,
                'warehouse_id': cls.wh1.id,
            }
        )

        cls.e2 = cls.env['autoorder.correction.coefficient'].create(
            {
                'start_date': cls.start_date,
                'end_date': cls.end_date,
                'value': 2.0,
                'reason': 'reason 2',
                'product_tag_id': cls.p_tag2.id,
                'warehouse_tag_id': cls.wh_tag2.id,
            }
        )

        cls.e3 = cls.env['autoorder.correction.coefficient'].create(
            {
                'start_date': cls.start_date,
                'end_date': cls.end_date,
                'value': 3.0,
                'reason': 'reason 3',
                'vendor_id': cls.v1.id,
                'warehouse_tag_id': cls.wh_tag1.id,
            }
        )

        cls.s1 = cls.env['autoorder.fixed.order'].create(
            {
                'product_id': cls.p1.id,
                'warehouse_id': cls.wh1.id,
                'min_stock': 1,
                'max_stock': 10,
                'value': 0,
            }
        )

        cls.s2 = cls.env['autoorder.fixed.order'].create(
            {
                'product_id': cls.p3.id,
                'warehouse_tag_id': cls.wh_tag2.id,
                'min_stock': 0,
                'max_stock': 0,
                'value': 20,
            }
        )

        cls.wh2.type = 'dc_external'
        cls.dc_quants = cls.env['dc.quants'].create(
            {
                'product_id': cls.p1.id,
                'warehouse_tag_id': cls.wh_tag1.id,
                'distribution_center_id': cls.wh2.id,
                'quant': 15,
            }
        )

    def test_gen_suppliers(self):
        suppliers = [
            {
                'supplier_id': self.v1.external_id,
                'supplier_name': self.v1.name,
                'days_before_filling': self.v1.days_before_filling,
            },
            {
                'supplier_id': self.v2.external_id,
                'supplier_name': self.v2.name,
                'days_before_filling': self.v2.days_before_filling,
            },
        ]
        test_suppliers = list(self.env['autoorder.yt.export'].gen_suppliers())

        for supplier in suppliers:
            self.assertTrue(
                supplier in test_suppliers,
                'Поставщика нет в выгрузке'
            )

    def test_gen_supplier_relations(self):
        self.env['ir.config_parameter'].sudo().set_param('unload_chains_instead_aggrements', "True")

        self.chain0 = self.env['supply.chain'].create({
            'changed': True,
            'type_supplier': 'vendor',
            'vendor_id': self.v1.id,
            'product_id': self.p1.id,
            'type_destination': 'warehouse',
            'destination_warehouse': self.wh1.id
        })
        self.chain0.delivery_type = 'dc_cross_docking'

        self.chain1 = self.env['supply.chain'].create({
            'type_supplier': 'vendor',
            'changed': True,
            'vendor_id': self.v1.id,
            'product_id': self.p1.id,
            'type_destination': 'geo',
            'destination_geo': self.wh_tag1.id
        })
        self.chain2 = self.env['supply.chain'].create({
            'type_supplier': 'warehouse',
            'changed': False,
            'warehouse_id': self.wh1.id,
            'product_id': self.p2.id,
            'type_destination': 'warehouse',
            'destination_warehouse': self.wh2.id
        })

        self.assertEqual(len(self.chain0.arc_vendor_warehouse_ids), 1)

        self.assertTrue(self.wh1 in self.wh_tag1.warehouse_ids)

        self.assertEqual(len(self.wh_tag1.warehouse_ids), 1)
        self.assertEqual(len(self.chain1.arc_vendor_warehouse_ids), 1)

        supplier_relations = [
            {
                'warehouse_id': int(self.wh1.code),
                'lavka_id': int(self.p1.default_code),
                'supplier_id': self.v1.external_id,
            }
        ]

        test_supplier_relations = self.env['autoorder.yt.export'].gen_supplier_relations(
            datetime.datetime.now()
        )

        self.assertEqual(
            supplier_relations,
            list(test_supplier_relations),
            'Выгрзука связей поставщиков со складами и продуктами',
        )

        self.chain2.changed = True
        self.assertTrue(self.chain2.arc_warehouse_warehouse_ids.changed)

        supplier_relations = [{
                'warehouse_id': int(self.wh1.code),
                'lavka_id': int(self.p1.default_code),
                'supplier_id': self.v1.external_id,
            },
            {
                'warehouse_id': int(self.wh2.code),
                'lavka_id': int(self.p2.default_code),
                'supplier_id': int(self.wh1.code),
            }
        ]

        test_supplier_relations = self.env['autoorder.yt.export'].gen_supplier_relations(
            datetime.datetime.now()
        )

        self.assertEqual(
            supplier_relations,
            list(test_supplier_relations),
            'Выгрзука связей поставщики -> склады, склады -> склады с продуктами',
        )

    @freeze_time('2022-06-22 12:00:00') # wednesday
    def test_gen_pick_by_line(self):
        self.cross1 = self.env['cross.dock.pbl'].create({
            'vendor_id': self.v1.id,
            'type_destination': 'warehouse',
            'destination_warehouse': self.wh1.id,
            'transit_warehouse': self.wh3.id,
            'line_ids': [(0, 0, {'day': 'general', 'transit_time': 3})],
            'delivery_type': 'dc_pbl'
        })

        self.cross2 = self.env['cross.dock.pbl'].create({
            'vendor_id': self.v1.id,
            'type_destination': 'geo',
            'destination_geo': self.wh_tag1.id,
            'transit_warehouse': self.wh3.id,
            'line_ids': [(0, 0, {'day': 'general', 'transit_time': 5})],
            'delivery_type': 'dc_pbl'
        })

        pbl = [
            {
                'warehouse_id': int(self.wh1.code),
                'supplier_id': int(self.v1.external_id),
                'distribution_center_id': int(self.wh3.code),
                'lag': 3,
            },
            {
                'warehouse_id': int(self.wh1.code),
                'supplier_id': int(self.v2.external_id),
                'distribution_center_id': int(self.wh3.code),
                'lag': 7,
            }
        ]

        self.cross3 = self.env['cross.dock.pbl'].create({
            'vendor_id': self.v2.id,
            'type_destination': 'geo',
            'destination_geo': self.wh_tag1.id,
            'transit_warehouse': self.wh3.id,
            'line_ids': [(0, 0, {'day': 'general', 'transit_time': 5}),
                         (0, 0, {'day': 'wednesday', 'transit_time': 7})
                         ],
            'delivery_type': 'dc_pbl'
        })

        test_pbl = self.env['autoorder.yt.export'].gen_pick_by_line()

        self.assertEqual(
            pbl,
            list(test_pbl),
            'Выгрзука связей по pbl настройкам',
        )

    def test_gen_quants(self):
        quants = [
            {
                'warehouse_id': 1,
                'lavka_id': 1,
                'quant': 1,
                'supplier_id': self.v1.external_id,
            },
            {
                'warehouse_id': 1,
                'lavka_id': 2,
                'quant': 2,
                'supplier_id': self.v1.external_id,
            },
            {
                'warehouse_id': 2,
                'lavka_id': 3,
                'quant': 3,
                'supplier_id': self.v2.external_id,
            },
            {
                'warehouse_id': 3,
                'lavka_id': 3,
                'quant': 3,
                'supplier_id': self.v2.external_id,
            },
            {
                'warehouse_id': 1,
                'lavka_id': 1,
                'quant': 15,
                'supplier_id': int(self.wh2.code),
            },
        ]

        test_quants = self.env['autoorder.yt.export'].gen_quants(
            datetime.datetime.now()
        )

        self.assertEqual(
            quants,
            list(test_quants),
            'Выгрзука квантов на продукты',
        )

    def test_gen_price_list_of_suppliers(self):
        price_list = [
            {
                'warehouse_id': 1,
                'lavka_id': 1,
                'price_with_nds': 115,
                'supplier_id': self.v1.external_id,
            },
            {
                'warehouse_id': 1,
                'lavka_id': 2,
                'price_with_nds': 230,
                'supplier_id': self.v1.external_id,
            },
            {
                'warehouse_id': 2,
                'lavka_id': 3,
                'price_with_nds': 345,
                'supplier_id': self.v2.external_id,
            },
            {
                'warehouse_id': 3,
                'lavka_id': 3,
                'price_with_nds': 345,
                'supplier_id': self.v2.external_id,
            },
        ]

        test_price_list = self.env['autoorder.yt.export'].gen_price_list_of_suppliers(
            datetime.datetime.now()
        )

        self.assertEqual(
            price_list,
            list(test_price_list),
            'Выгрзука цен на продукты',
        )

    def test_purchasing_assortment(self):
        purchasing_assortment = [
            {
                'warehouse_id': 1,
                'lavka_id': 1,
                'supplier_purchase': 1,
            },
            {
                'warehouse_id': 1,
                'lavka_id': 2,
                'supplier_purchase': 1,
            },
            {
                'warehouse_id': 2,
                'lavka_id': 1,
                'supplier_purchase': 1,
            },
            {
                'warehouse_id': 2,
                'lavka_id': 2,
                'supplier_purchase': 1,
            },
            {
                'warehouse_id': 2,
                'lavka_id': 3,
                'supplier_purchase': 1,
            },
            {
                'warehouse_id': 2,
                'lavka_id': 4,
                'supplier_purchase': 1,
            },
            {
                'warehouse_id': 2,
                'lavka_id': 5,
                'supplier_purchase': 1,
            },
            {
                'warehouse_id': 3,
                'lavka_id': 3,
                'supplier_purchase': 1,
            },
            {
                'warehouse_id': 3,
                'lavka_id': 4,
                'supplier_purchase': 1,
            },
            {
                'warehouse_id': 3,
                'lavka_id': 5,
                'supplier_purchase': 1,
            },
        ]

        test_purchasing_assortment = self.env['autoorder.yt.export'].gen_purchasing_assortment()

        self.assertEqual(
            purchasing_assortment,
            list(test_purchasing_assortment),
            'Выгрузка ассортимента продуктов',
        )

    def test_orders_on_the_way(self):
        orders_on_the_way = [
            {
                'warehouse_id': 1,
                'supplier_id': self.v1.external_id,
                'lavka_id': int(self.p1.default_code),
                'date': self.first_date.date().isoformat(),
                'qty': 1,
            },
            {
                'warehouse_id': 1,
                'supplier_id': self.v1.external_id,
                'lavka_id': int(self.p2.default_code),
                'date': self.first_date.date().isoformat(),
                'qty': 2,
            },
            {
                'warehouse_id': 2,
                'supplier_id': self.v2.external_id,
                'lavka_id': int(self.p3.default_code),
                'date': self.second_date.date().isoformat(),
                'qty': 6,
            },
        ]

        test_orders_on_the_way = self.env['autoorder.yt.export'].gen_orders_on_the_way(self.now)

        self.assertEqual(
            orders_on_the_way,
            list(test_orders_on_the_way),
            'Выгрузка товаровв пути',
        )

    def test_min_order_sum(self):
        min_order_sum = [
            {
                'warehouse_id': 1,
                'supplier_id': self.v1.external_id,
                'min_order_amount': 0.0,
                'increase_order': False,
                'order_trigger': 0.0,
            },
            {
                'warehouse_id': 2,
                'supplier_id': self.v2.external_id,
                'min_order_amount': 2.0,
                'increase_order': True,
                'order_trigger': 10.0,
            },
            {
                'warehouse_id': 3,
                'supplier_id': self.v2.external_id,
                'min_order_amount': 2.0,
                'increase_order': True,
                'order_trigger': 10.0,
            },
        ]

        test_min_order_sum = self.env['autoorder.yt.export'].gen_min_order_sum()

        self.assertEqual(
            min_order_sum,
            list(test_min_order_sum),
            'Выгрузка минимальных сумм заказа',
        )

    def test_warehouses(self):
        warehouses = [
            {
                'store_id': 1,
                'store_name': 'wh-1',
                'address': 'paris 1, 1, 1',
                'group': 'Paris 1',
                'purchase_date': '2021-01-01',
                'open_date': '2021-01-01',
                'employee_start_date': '2021-01-01',
                'active': 1,
                'store_type': 'Лавка',
                'days_before_filling': 0,
            },
            {
                'store_id': 2,
                'store_name': 'wh-2',
                'address': 'paris 2, 2, 2',
                'group': 'Paris 2',
                'purchase_date': '2021-02-02',
                'open_date': '2021-02-02',
                'employee_start_date': '2021-02-02',
                'active': 1,
                'store_type': 'Лавка',
                'days_before_filling': 0,
            },
            {
                'store_id': 3,
                'store_name': 'wh-3',
                'address': 'paris 3, 3, 3',
                'group': 'Paris 2',
                'purchase_date': '2021-03-03',
                'open_date': '2021-03-03',
                'employee_start_date': '2021-03-03',
                'active': 1,
                'store_type': 'Лавка',
                'days_before_filling': 0,
            },
        ]

        test_warehouses = self.env['autoorder.yt.export'].gen_warehouses()

        self.assertEqual(
            warehouses,
            list(test_warehouses),
            'Выгрузка складов',
        )

    def test_events(self):
        events = [
            {
                'warehouse_id': 1,
                'lavka_id': 1,
                'start_date': self.start_date.isoformat(),
                'ending_date': self.end_date.isoformat(),
                'coef': 1.0,
                'event_name': 'reason 1',
            },
            {
                'warehouse_id': 1,
                'lavka_id': 1,
                'start_date': self.start_date.isoformat(),
                'ending_date': self.end_date.isoformat(),
                'coef': 3.0,
                'event_name': 'reason 3',
            },
            {
                'warehouse_id': 1,
                'lavka_id': 2,
                'start_date': self.start_date.isoformat(),
                'ending_date': self.end_date.isoformat(),
                'coef': 3.0,
                'event_name': 'reason 3',
            },
            {
                'warehouse_id': 2,
                'lavka_id': 3,
                'start_date': self.start_date.isoformat(),
                'ending_date': self.end_date.isoformat(),
                'coef': 2.0,
                'event_name': 'reason 2',
            },
            {
                'warehouse_id': 2,
                'lavka_id': 4,
                'start_date': self.start_date.isoformat(),
                'ending_date': self.end_date.isoformat(),
                'coef': 2.0,
                'event_name': 'reason 2',
            },
            {
                'warehouse_id': 2,
                'lavka_id': 5,
                'start_date': self.start_date.isoformat(),
                'ending_date': self.end_date.isoformat(),
                'coef': 2.0,
                'event_name': 'reason 2',
            },
            {
                'warehouse_id': 3,
                'lavka_id': 3,
                'start_date': self.start_date.isoformat(),
                'ending_date': self.end_date.isoformat(),
                'coef': 2.0,
                'event_name': 'reason 2',
            },
            {
                'warehouse_id': 3,
                'lavka_id': 4,
                'start_date': self.start_date.isoformat(),
                'ending_date': self.end_date.isoformat(),
                'coef': 2.0,
                'event_name': 'reason 2',
            },
            {
                'warehouse_id': 3,
                'lavka_id': 5,
                'start_date': self.start_date.isoformat(),
                'ending_date': self.end_date.isoformat(),
                'coef': 2.0,
                'event_name': 'reason 2',
            },
        ]

        test_events = list(self.env['autoorder.yt.export'].gen_events(self.today))
        test_events = sorted(test_events, key=lambda x: (x['warehouse_id'], x['lavka_id'], x['coef']))
        self.assertEqual(
            events,
            list(test_events),
            'Выгрузка корректирующих коэффициентов',
        )

    def test_fixed_orders(self):
        fixed_orders = [
            {
                'store_id': 1,
                'product_id': 1,
                'min_stock': 1,
                'max_stock': 10,
                'order': 0,
            },
            {
                'store_id': 2,
                'product_id': 3,
                'min_stock': 0,
                'max_stock': 0,
                'order': 20,
            },
            {
                'store_id': 3,
                'product_id': 3,
                'min_stock': 0,
                'max_stock': 0,
                'order': 20,
            },
        ]
        test_fixed_orders = list(self.env['autoorder.yt.export'].gen_fixed_orders())
        test_fixed_orders = sorted(test_fixed_orders, key=lambda x: (x['store_id'], x['product_id']))
        self.assertEqual(
            fixed_orders,
            list(test_fixed_orders),
            'Выгрузка мин/макс настроек заказа',
        )

    def test_warehouse_analogs(self):
        warehouse_analogs = [
            {
                'warehouse_id': 2,
                'warehouse_id_analog': 1,
                'start_date': '2021-02-02',
                'ending_date': '2021-02-02',
            },
            {
                'warehouse_id': 3,
                'warehouse_id_analog': 1,
                'start_date': '2021-03-03',
                'ending_date': '2021-03-03',
            },
        ]

        test_warehouse_analogs = list(self.env['autoorder.yt.export'].gen_warehouse_analogs())
        self.assertEqual(
            warehouse_analogs,
            list(test_warehouse_analogs),
            'Выгрузка аналогов складов',
        )

