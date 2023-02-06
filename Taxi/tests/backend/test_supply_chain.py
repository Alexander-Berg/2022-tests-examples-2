from datetime import datetime

from freezegun import freeze_time
from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import SavepointCase, Form
from psycopg2 import errors
import logging

_logger = logging.getLogger(__name__)


@tagged('lavka', 'supply_chain')
class TestSupplyChain(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(SavepointCase, cls).setUpClass()
        cls.factory = cls.env['factory_common']

        cls.dc, *cls.warehouse_list = cls.factory.create_warehouses(qty=3)
        cls.dc.warehouse_tag_ids = False
        cls.dc.type = 'dc_external'

        cls.geo_tags = cls.warehouse_list[0].warehouse_tag_ids

        cls.products = cls.factory.create_products(cls.warehouse_list, qty=3)
        cls.vendor = cls.env['res.partner'].create({'name': 'Bow-Bow'})

    def test_supply_direct(self):
        with Form(self.env['supply.chain']) as form:

            form.type_supplier = 'vendor'
            form.vendor_id = self.vendor

            form.product_id = self.products[0]

            form.type_destination = 'geo'
            form.destination_geo = self.geo_tags[0]

            self.assertEqual(form.delivery_type, 'direct')

        chain = form.save()
        #excess fields
        self.assertFalse(chain.warehouse_id.id)
        self.assertFalse(chain.destination_warehouse.id)
        self.assertFalse(chain.transit_warehouse.id)
        self.assertEqual(chain.line_ids.ids, [])

        self.assertEqual(len(chain.arc_warehouse_warehouse_ids), 0)

        self.assertEqual(len(chain.display_arc_vendor_warehouse_ids), 2)
        for arc, wh in zip(chain.display_arc_vendor_warehouse_ids, self.warehouse_list):
            self.assertEqual(arc.end_, wh)
            self.assertEqual(arc.begin, self.vendor)
            self.assertEqual(arc.res_model, chain._name)
            self.assertEqual(arc.product_id, chain.product_id)



    def test_dc_storage(self):
        with Form(self.env['supply.chain']) as form:
            form.type_supplier = 'vendor'
            form.vendor_id = self.vendor

            form.product_id = self.products[0]

            form.type_destination = 'warehouse'
            form.destination_warehouse = self.dc

            self.assertEqual(form.delivery_type, 'dc_storage')

        chain = form.save()
        # excess fields
        self.assertFalse(chain.warehouse_id.id)
        self.assertFalse(chain.destination_geo.id)
        self.assertFalse(chain.transit_warehouse.id)
        self.assertEqual(chain.line_ids.ids, [])

        self.assertEqual(len(chain.arc_warehouse_warehouse_ids), 0)

        self.assertEqual(len(chain.display_arc_vendor_warehouse_ids), 1)
        arc = chain.display_arc_vendor_warehouse_ids
        self.assertEqual(arc.begin, self.vendor)
        self.assertEqual(arc.end_, self.dc)
        self.assertEqual(arc.end_, self.dc)
        self.assertEqual(arc.res_model, chain._name)

        with Form(self.env['supply.chain']) as form:
            form.type_supplier = 'warehouse'
            form.warehouse_id = self.dc

            form.product_id = self.products[1]

            form.type_destination = 'geo'
            form.destination_geo = self.geo_tags[0]

            self.assertEqual(form.delivery_type, 'dc_storage')

        chain = form.save()

        self.assertFalse(chain.vendor_id.id)
        self.assertFalse(chain.destination_warehouse.id)
        self.assertFalse(chain.transit_warehouse.id)
        self.assertEqual(chain.line_ids.ids, [])

        self.assertEqual(len(chain.display_arc_vendor_warehouse_ids), 0)

        self.assertEqual(len(chain.arc_warehouse_warehouse_ids), 2)
        for arc, wh in zip(chain.display_arc_vendor_warehouse_ids, self.warehouse_list):
            self.assertEqual(arc.begin, self.dc)
            self.assertEqual(arc.product_id, chain.product_id)
            self.assertEqual(arc.end_, wh)

    def test_cross(self):
        cross = self.env['cross.dock.pbl'].create({
            'vendor_id': self.vendor.id,
            'type_destination': 'geo',
            'destination_geo': self.geo_tags[0].id,
            'transit_warehouse': self.dc.id,
            'delivery_type': 'dc_cross_docking',
            'line_ids': [(0, 0, {'day': 'general', 'transit_time': 3})],
        })

        for arc, wh in zip(cross.display_arc_vendor_warehouse_ids, self.warehouse_list):
            self.assertEqual(arc.end_, wh)
            self.assertEqual(arc.begin, self.vendor)
            self.assertEqual(arc.res_model, cross._name)

        with Form(self.env['supply.chain']) as form:
            form.type_supplier = 'vendor'
            form.vendor_id = self.vendor

            form.product_id = self.products[0]

            form.type_destination = 'warehouse'
            form.destination_warehouse = self.warehouse_list[0]

            self.assertEqual(form.delivery_type, 'dc_cross_docking')

        with Form(self.env['supply.chain']) as form:
            form.type_supplier = 'vendor'
            form.vendor_id = self.vendor

            form.product_id = self.products[0]

            form.type_destination = 'geo'
            form.destination_geo = self.geo_tags[0]

            self.assertEqual(form.delivery_type, 'dc_cross_docking')
            self.assertEqual(form.transit_warehouse, self.dc)
            self.assertEqual(form.line_ids._records[0]['transit_time'], 3)
            self.assertEqual(form.line_ids._records[0]['day'], 'general')

        chain = form.save()

        self.assertFalse(chain.warehouse_id.id)
        self.assertFalse(chain.destination_warehouse.id)

        self.assertEqual(len(chain.arc_warehouse_warehouse_ids), 0)

        self.assertEqual(len(chain.display_arc_vendor_warehouse_ids), 2)
        for arc, wh in zip(chain.display_arc_vendor_warehouse_ids, self.warehouse_list):
            self.assertEqual(arc.end_, wh)
            self.assertEqual(arc.begin, self.vendor)
            self.assertEqual(arc.res_model, chain._name)
            self.assertEqual(arc.product_id, chain.product_id)

    def test_forbidden_arcs(self):
        geotag = self.geo_tags[0]
        intersection_geotag = self.geo_tags.copy({'name': 'other_tag'})
        self.assertNotEqual(geotag.id, intersection_geotag.id)
        product = self.products[0]
        warehouse = self.warehouse_list[0]
        self.env['supply.chain'].create({
            'type_supplier': 'vendor',
            'vendor_id': self.vendor.id,
            'product_id': product.id,
            'type_destination': 'geo',
            'destination_geo': geotag.id
        })

        self.assertTrue(warehouse in self.geo_tags.warehouse_ids)

        with self.assertRaises(errors.UniqueViolation):
            self.env['supply.chain'].create({
                'type_supplier': 'vendor',
                'vendor_id': self.vendor.id,
                'product_id': product.id,
                'type_destination': 'geo',
                'destination_geo': intersection_geotag.id
            })

    def test_get_delivery_type(self):
        vals = self.env['supply.chain'].get_delivery_type_for_vendor(self.vendor, self.warehouse_list[0])
        self.assertEqual(vals['delivery_type'], 'direct')
        self.assertEqual(vals['transit_warehouse'], False)

        vals = self.env['supply.chain'].get_delivery_type_for_vendor(self.vendor, self.dc)
        self.assertEqual(vals['delivery_type'], 'dc_storage')
        self.assertEqual(vals['transit_warehouse'], False)

        cross = self.env['cross.dock.pbl'].create({
            'vendor_id': self.vendor.id,
            'type_destination': 'geo',
            'destination_geo': self.geo_tags[0].id,
            'transit_warehouse': self.dc.id,
            'line_ids': [(0, 0, {'day': 'general', 'transit_time': 3})],
            'delivery_type': 'dc_cross_docking',
        })

        supply = self.env['supply.chain'].create({
            'type_supplier': 'vendor',
            'vendor_id': self.vendor.id,
            'type_destination': 'geo',
            'destination_geo': self.geo_tags[0].id,
            'product_id': self.products[0].id,
            'changed': True,
        })

        vals = self.env['supply.chain'].get_delivery_type_for_vendor(self.vendor, self.warehouse_list[0])
        self.assertEqual(vals['delivery_type'], cross.delivery_type)
        self.assertEqual(vals['transit_warehouse'], cross.transit_warehouse)
        self.assertEqual(vals['product_ids'], supply.product_id)

        supply = self.env['supply.chain'].create({
            'type_supplier': 'warehouse',
            'warehouse_id': self.dc.id,
            'type_destination': 'geo',
            'destination_geo': self.geo_tags[0].id,
            'product_id': self.products[0].id,
            'changed': True,
        })

        vals = self.env['supply.chain'].get_delivery_type_for_vendor(self.dc, self.warehouse_list[0])
        self.assertEqual(vals['delivery_type'], 'dc_storage')
        self.assertEqual(vals['product_ids'], supply.product_id)

    def test_get_lag_del_schedule(self):
        cross = self.env['cross.dock.pbl'].create({
            'vendor_id': self.vendor.id,
            'type_destination': 'geo',
            'destination_geo': self.geo_tags[0].id,
            'transit_warehouse': self.dc.id,
            'line_ids': [(0, 0, {'day': 'general', 'transit_time': 3})],
            'delivery_type': 'dc_pbl',
        })

        with freeze_time('2022-06-22 12:00:00'):  # Wednesday
            params = {
                'vendor_id': self.vendor,
                'warehouse_id': self.geo_tags.warehouse_ids[0],
                'day': datetime.now(),
                'transit_warehouse': self.dc,
            }
            lags = self.env['cross.dock.pbl'].get_lag_del_schedule(params)
            self.assertEqual(lags, [3])

        cross = self.env['cross.dock.pbl'].create({
            'vendor_id': self.vendor.id,
            'type_destination': 'warehouse',
            'destination_warehouse': self.geo_tags[0].warehouse_ids[0].id,
            'transit_warehouse': self.dc.id,
            'line_ids': [
                        (0, 0, {'day': 'general', 'transit_time': 3}),
                        (0, 0, {'day': 'wednesday', 'transit_time': 7}),
                        (0, 0, {'day': 'wednesday', 'transit_time': 5}),
                         ],
            'delivery_type': 'dc_pbl',
        })


        with freeze_time('2022-06-22 12:00:00'):  # Wednesday
            params = {
                'vendor_id': self.vendor,
                'warehouse_id': self.geo_tags.warehouse_ids[0],
                'day': datetime.now(),
                'transit_warehouse': self.dc,
            }
            lags = self.env['cross.dock.pbl'].get_lag_del_schedule(params)
            self.assertEqual(lags, [7, 5])


    def test_get_lag_del_schedule(self):
        cross = self.env['cross.dock.pbl'].create({
            'vendor_id': self.vendor.id,
            'type_destination': 'geo',
            'destination_geo': self.geo_tags[0].id,
            'transit_warehouse': self.dc.id,
            'line_ids': [(0, 0, {'day': 'general', 'transit_time': 3})],
            'delivery_type': 'dc_pbl',
        })

        with freeze_time('2022-06-22 12:00:00'):  # Wednesday
            params = {
                'vendor_id': self.vendor,
                'warehouse_id': self.geo_tags.warehouse_ids[0],
                'day': datetime.now(),
                'transit_warehouse': self.dc,
            }
            lags = self.env['cross.dock.pbl'].get_lag_del_schedule(params)
            self.assertEqual(lags, [3])

        cross = self.env['cross.dock.pbl'].create({
            'vendor_id': self.vendor.id,
            'type_destination': 'warehouse',
            'destination_warehouse': self.geo_tags[0].warehouse_ids[0].id,
            'transit_warehouse': self.dc.id,
            'line_ids': [
                        (0, 0, {'day': 'general', 'transit_time': 3}),
                        (0, 0, {'day': 'wednesday', 'transit_time': 7}),
                        (0, 0, {'day': 'wednesday', 'transit_time': 5}),
                         ],
            'delivery_type': 'dc_pbl',
        })


        with freeze_time('2022-06-22 12:00:00'):  # Wednesday
            params = {
                'vendor_id': self.vendor,
                'warehouse_id': self.geo_tags.warehouse_ids[0],
                'day': datetime.now(),
                'transit_warehouse': self.dc,
            }
            lags = self.env['cross.dock.pbl'].get_lag_del_schedule(params)
            self.assertEqual(lags, [7, 5])


    def test_get_chains_info_by_vendor_rc(self):

        cross = self.env['cross.dock.pbl'].create({
            'vendor_id': self.vendor.id,
            'type_destination': 'warehouse',
            'destination_warehouse': self.warehouse_list[0].id,
            'transit_warehouse': self.dc.id,
            'line_ids': [(0, 0, {'day': 'general', 'transit_time': 3})],
            'delivery_type': 'dc_pbl',
        })

        supply = self.env['supply.chain'].create({  # pbl
            'type_supplier': 'vendor',
            'vendor_id': self.vendor.id,
            'type_destination': 'warehouse',
            'destination_warehouse': self.warehouse_list[0].id,
            'product_id': self.products[0].id,
            'changed': True,
        })

        supply_dc = self.env['supply.chain'].create({  # dc_storage
            'type_supplier': 'vendor',
            'vendor_id': self.vendor.id,
            'type_destination': 'warehouse',
            'destination_warehouse': self.dc.id,
            'product_id': self.products[1].id,
            'changed': True,
        })


        vals = self.env['cross.dock.pbl'].get_chains_info_by_vendor_rc(self.vendor, self.dc, datetime.today())

        expected_vals = (
            {
                'delivery_type': 'dc_storage',
                'product_ids': supply_dc.product_id,
            },
            {
                'delivery_type': 'dc_pbl',
                'lags': {
                    3: [(supply.destination_warehouse, supply.product_id)]
                }
            }
        )

        self.assertEqual(
            vals,
            expected_vals
        )

    @freeze_time('2022-06-22 12:00:00')  # wednesday
    def test_get_chains_info_by_vendor_rc_days(self):

        cross = self.env['cross.dock.pbl'].create({
            'vendor_id': self.vendor.id,
            'type_destination': 'warehouse',
            'destination_warehouse': self.warehouse_list[0].id,
            'transit_warehouse': self.dc.id,
            'line_ids': [(0, 0, {'day': 'general', 'transit_time': 3}),
                         (0, 0, {'day': 'wednesday', 'transit_time': 5}),
                         (0, 0, {'day': 'wednesday', 'transit_time': 7}),
                         ],
            'delivery_type': 'dc_pbl',
        })

        supply = self.env['supply.chain'].create({  # pbl
            'type_supplier': 'vendor',
            'vendor_id': self.vendor.id,
            'type_destination': 'warehouse',
            'destination_warehouse': self.warehouse_list[0].id,
            'product_id': self.products[0].id,
            'changed': True,
        })

        supply_dc = self.env['supply.chain'].create({  # dc_storage
            'type_supplier': 'vendor',
            'vendor_id': self.vendor.id,
            'type_destination': 'warehouse',
            'destination_warehouse': self.dc.id,
            'product_id': self.products[1].id,
            'changed': True,
        })


        vals = self.env['cross.dock.pbl'].get_chains_info_by_vendor_rc(self.vendor, self.dc, datetime.today())

        expected_vals = (
            {
                'delivery_type': 'dc_storage',
                'product_ids': supply_dc.product_id,
            },
            {
                'delivery_type': 'dc_pbl',
                'lags': {
                    5: [(supply.destination_warehouse, supply.product_id)],
                    7: [(supply.destination_warehouse, supply.product_id)],
                }
            }
        )

        self.assertEqual(
            vals,
            expected_vals
        )


    def test_recalculate_delicery_type(self):
        chain = self.env['supply.chain'].create({
            'type_supplier': 'vendor',
            'vendor_id': self.vendor.id,
            'type_destination': 'warehouse',
            'destination_warehouse': self.warehouse_list[0].id,
            'product_id': self.products[1].id,
            'changed': True,
        })
        self.assertEqual(chain.delivery_type, 'direct')

        cross = self.env['cross.dock.pbl'].create({
            'vendor_id': self.vendor.id,
            'type_destination': 'warehouse',
            'destination_warehouse': self.warehouse_list[0].id,
            'transit_warehouse': self.dc.id,
            'delivery_type': 'dc_cross_docking',
            'line_ids': [(0, 0, {'day': 'general', 'transit_time': 3})],
        })

        self.assertEqual(chain.delivery_type, 'dc_cross_docking')
