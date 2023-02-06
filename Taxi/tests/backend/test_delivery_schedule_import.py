import datetime as dt

from odoo.tests import tagged, SavepointCase


@tagged('lavka', 'autoorder', 'autoorder_imports', 'delivery_schedule', 'delivery_schedule_import')
class TestDeliveryScheduleImport(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.wh_tag1 = cls.env['stock.warehouse.tag'].create({
            'type': 'geo',
            'name': 'New York',
        })

        cls.wh_tag2 = cls.env['stock.warehouse.tag'].create({
            'type': 'geo',
            'name': 'London',
        })

        cls.p_tag1 = cls.env['product.tag'].create({
            'type': 'abc_group',
            'name': 'G1',
        })

        cls.p_tag2 = cls.env['product.tag'].create({
            'type': 'abc_group',
            'name': 'G2',
        })

        cls.p_tag3 = cls.env['product.tag'].create({
            'type': 'storage_type',
            'name': 'T1',
        })

        cls.p_tag4 = cls.env['product.tag'].create({
            'type': 'storage_type',
            'name': 'T2',
        })

        cls.p_tag5 = cls.env['product.tag'].create({
            'type': 'nonfood',
            'name': 'N1',
        })

        cls.p_tag6 = cls.env['product.tag'].create({
            'type': 'nonfood',
            'name': 'N2',
        })

        cls.wh1 = cls.env['stock.warehouse'].create({
            'name': 'wh-1',
            'code': '1',
        })

        cls.wh2 = cls.env['stock.warehouse'].create({
            'name': 'wh-2',
            'code': '2',
        })

        cls.v1 = cls.env['res.partner'].create(
            {
                'name': 'v-1',
                'is_company': True,
                'supplier_rank': 1,
            }
        )

        cls.v2 = cls.env['res.partner'].create(
            {
                'name': 'v-2',
                'is_company': True,
                'supplier_rank': 1,
            }
        )

    def test_serialize_and_process_rows(self):
        dsi = self.env['autoorder.delivery.schedule.import']
        ds = self.env['autoorder.delivery.schedule']

        start = dt.date(year=2021, month=5, day=1)
        end = dt.date(year=2021, month=5, day=31)
        order_1 = dt.date(year=2021, month=5, day=2)
        delivery_1 = dt.date(year=2021, month=5, day=30)
        order_2 = dt.date(year=2021, month=5, day=3)
        delivery_2 = dt.date(year=2021, month=5, day=29)

        weekdays = {
            'delivery_weekday_0': True,
            'delivery_weekday_1': False,
            'delivery_weekday_2': True,
            'delivery_weekday_3': False,
            'delivery_weekday_4': True,
            'delivery_weekday_5': False,
            'delivery_weekday_6': True,
            'order_weekday_0': False,
            'order_weekday_1': True,
            'order_weekday_2': False,
            'order_weekday_3': True,
            'order_weekday_4': False,
            'order_weekday_5': True,
            'order_weekday_6': False,
        }

        rows = [
            {
                'vendor_external_id': self.v1.external_id,
                'warehouse_ids': [],
                'warehouse_tag_ids': ['New York', 'London'],
                'abc_tags': [],
                'storage_tags': [],
                'nonfood_tags': [],
                'days_before_order': 1,
                'week_type': 'odd',
                'fixture_start_date': start,
                'fixture_end_date': end,
                'order_date': order_1,
                'delivery_date': delivery_1,
                **weekdays,
            },
            {
                'vendor_external_id': self.v1.external_id,
                'warehouse_ids': [],
                'warehouse_tag_ids': ['New York', 'London'],
                'abc_tags': [],
                'storage_tags': [],
                'nonfood_tags': [],
                'days_before_order': 1,
                'week_type': 'odd',
                'fixture_start_date': start,
                'fixture_end_date': end,
                'order_date': order_2,
                'delivery_date': delivery_2,
                **weekdays,
            },
            {
                'vendor_external_id': self.v1.external_id,
                'warehouse_ids': [],
                'warehouse_tag_ids': ['New York'],
                'abc_tags': [],
                'storage_tags': [],
                'nonfood_tags': [],
                'days_before_order': 2,
                'week_type': 'odd',
                'fixture_start_date': start,
                'fixture_end_date': end,
                'order_date': order_1,
                'delivery_date': delivery_1,
                **weekdays,
            },
            {
                'vendor_external_id': self.v2.external_id,
                'warehouse_ids': ['1', '2'],
                'warehouse_tag_ids': [],
                'abc_tags': ['G1', 'G2'],
                'storage_tags': ['T1', 'T2'],
                'nonfood_tags': [],
                'days_before_order': 3,
                'week_type': 'odd',
                'fixture_start_date': start,
                'fixture_end_date': end,
                'order_date': None,
                'delivery_date': None,
                **weekdays,
            },
            {
                'vendor_external_id': self.v2.external_id,
                'warehouse_ids': ['1'],
                'warehouse_tag_ids': [],
                'abc_tags': [],
                'storage_tags': [],
                'nonfood_tags': ['N1', 'N2'],
                'days_before_order': 4,
                'week_type': 'odd',
                'fixture_start_date': None,
                'fixture_end_date': None,
                'order_date': None,
                'delivery_date': None,
                **weekdays,
            },
        ]

        rows = dsi.serialize(rows)
        items = dsi.post_process(rows)

        keys = [
            (self.v1.id, (), (self.wh_tag1.id, self.wh_tag2.id), ()),
            (self.v1.id, (), (self.wh_tag1.id,), ()),
            (self.v2.id, (self.wh1.id, self.wh2.id), (), (self.p_tag1.id, self.p_tag2.id, self.p_tag3.id, self.p_tag4.id)),
            (self.v2.id, (self.wh1.id,), (), (self.p_tag5.id, self.p_tag6.id)),
        ]

        test_schedule_data = [
            {
                'vendor_id': self.v1.id,
                'warehouse_ids': (),
                'warehouse_tag_ids': (self.wh_tag1.id, self.wh_tag2.id),
                'product_tag_ids': (),
                'days_before_order': 1,
                'week_type': 'odd',
                'fixture_start_date': start,
                'fixture_end_date': end,
                'type_supplier': 'vendor',
                'distribution_center_id': False,
                **weekdays,
            },
            {
                'vendor_id': self.v1.id,
                'warehouse_ids': (),
                'warehouse_tag_ids': (self.wh_tag1.id,),
                'product_tag_ids': (),
                'days_before_order': 2,
                'week_type': 'odd',
                'fixture_start_date': start,
                'fixture_end_date': end,
                'type_supplier': 'vendor',
                'distribution_center_id': False,
                **weekdays,
            },
            {
                'vendor_id': self.v2.id,
                'warehouse_ids': (self.wh1.id, self.wh2.id),
                'warehouse_tag_ids': (),
                'product_tag_ids': (self.p_tag1.id, self.p_tag2.id, self.p_tag3.id, self.p_tag4.id),
                'days_before_order': 3,
                'week_type': 'odd',
                'fixture_start_date': start,
                'fixture_end_date': end,
                'type_supplier': 'vendor',
                'distribution_center_id': False,
                **weekdays,
            },
            {
                'vendor_id': self.v2.id,
                'warehouse_ids': (self.wh1.id,),
                'warehouse_tag_ids': (),
                'product_tag_ids': (self.p_tag5.id, self.p_tag6.id),
                'days_before_order': 4,
                'week_type': 'odd',
                'fixture_start_date': None,
                'fixture_end_date': None,
                'type_supplier': 'vendor',
                'distribution_center_id': False,
                **weekdays,
            },
        ]

        test_fixtures = [
            {
                order_1: {'order_date': order_1, 'delivery_date': delivery_1},
                order_2: {'order_date': order_2, 'delivery_date': delivery_2},
            },
            {
                order_1: {'order_date': order_1, 'delivery_date': delivery_1},
            },
            {},
            {},
        ]

        test_items = {
            keys[0]: {
                'schedule': ds,
                'schedule_data': test_schedule_data[0],
                'fixtures': test_fixtures[0],
            },
            keys[1]: {
                'schedule': ds,
                'schedule_data': test_schedule_data[1],
                'fixtures': test_fixtures[1],
            },
            keys[2]: {
                'schedule': ds,
                'schedule_data': test_schedule_data[2],
                'fixtures': test_fixtures[2],
            },
            keys[3]: {
                'schedule': ds,
                'schedule_data': test_schedule_data[3],
                'fixtures': test_fixtures[3],
            },
        }

        self.assertEqual(items, test_items)

        dsi.save(items)
        for key, fixtures in zip(keys, test_fixtures):
            schedule = dsi.get_object(test_items[key]['schedule_data'])
            self.assertEqual(len(schedule), 1)
            self.assertEqual(len(schedule.delivery_schedule_fixture_ids), len(fixtures))
