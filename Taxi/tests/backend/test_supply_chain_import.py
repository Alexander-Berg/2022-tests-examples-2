import copy

from odoo.tests import tagged
from odoo.tests.common import SavepointCase

@tagged('lavka', 'supply_chain', 'supply_chain_import')
class TestSupplyChainImport(SavepointCase):
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

        cls.wh1 = cls.env['stock.warehouse'].create(
            {
                'name': 'wh-1',
                'code': '1',
                'active': True,
                'warehouse_tag_ids': [cls.wh_tag1.id],
            }
        )

        cls.wh2 = cls.env['stock.warehouse'].create(
            {
                'name': 'wh-2',
                'code': '2',
                'active': True,
                'warehouse_tag_ids': [cls.wh_tag2.id],
                'type': 'dc_external',
            }
        )

        cls.v1 = cls.env['res.partner'].create(
            {
                'name': 'v-1',
                'is_company': True,
                'supplier_rank': 1,
                'external_id': 1,
            }
        )

        cls.v2 = cls.env['res.partner'].create(
            {
                'name': 'v-2',
                'is_company': True,
                'supplier_rank': 1,
                'external_id': 2,
            }
        )

        cls.p1 = cls.env['product.product'].create(
            {
                'name': 'p-1',
                'default_code': '1',
                'wms_id': '1',
            }
        )

        cls.p2 = cls.env['product.product'].create(
            {
                'name': 'p-2',
                'default_code': '2',
                'wms_id': '2',
            }
        )

    def test_supply_import(self):
        supply_import = self.env['autoorder.supply.chain.import']

        rows = [
            {
                'active': False,
                'supplier': str(self.v1.external_id),
                'product_id': str(self.p1.default_code),
                'destination': str(self.wh1.code),
            },
            {
                'active': True,
                'supplier': str(self.v1.external_id),
                'product_id': str(self.p1.default_code),
                'destination': str(self.wh_tag1.name),
            },
            {
                'active': True,
                'supplier': str(self.wh1.code),
                'product_id': str(self.p2.default_code),
                'destination': str(self.wh2.code),
            },
            {
               'active': False,
               'supplier': str(self.wh1.code),
               'product_id': str(self.p2.default_code),
               'destination': str(self.wh_tag2.name),
            },
        ]
        serialized_rows = supply_import.serialize(copy.deepcopy(rows))
        supply_import.save(serialized_rows)
        chains = self.env['supply.chain'].search([])

        self.assertEqual(len(chains), len(rows))

        self.assertEqual(chains[0].type_supplier, 'vendor')
        self.assertEqual(chains[0].type_destination, 'warehouse')
        self.assertEqual(chains[0].changed, rows[0]['active'])
        self.assertEqual(chains[0].vendor_id.external_id, int(rows[0]['supplier']))
        self.assertEqual(chains[0].product_id.default_code, rows[0]['product_id'])
        self.assertEqual(chains[0].destination_warehouse.code, rows[0]['destination'])

        self.assertEqual(chains[1].type_supplier, 'vendor')
        self.assertEqual(chains[1].type_destination, 'geo')
        self.assertEqual(chains[1].changed, rows[1]['active'])
        self.assertEqual(chains[1].vendor_id.external_id, int(rows[1]['supplier']))
        self.assertEqual(chains[1].product_id.default_code, rows[1]['product_id'])
        self.assertEqual(chains[1].destination_geo.name, rows[1]['destination'])

        self.assertEqual(chains[2].type_supplier, 'warehouse')
        self.assertEqual(chains[2].type_destination, 'warehouse')
        self.assertEqual(chains[2].changed, rows[2]['active'])
        self.assertEqual(chains[2].warehouse_id.code, rows[2]['supplier'])
        self.assertEqual(chains[2].product_id.default_code, rows[2]['product_id'])
        self.assertEqual(chains[2].destination_warehouse.code, rows[2]['destination'])

        self.assertEqual(chains[3].type_supplier, 'warehouse')
        self.assertEqual(chains[3].type_destination, 'geo')
        self.assertEqual(chains[3].changed, rows[3]['active'])
        self.assertEqual(chains[3].warehouse_id.code, rows[3]['supplier'])
        self.assertEqual(chains[3].product_id.default_code, rows[3]['product_id'])
        self.assertEqual(chains[3].destination_geo.name, rows[3]['destination'])

    def test_transit_settings(self):
        cross_import = self.env['autoorder.cross.dock.import']

        rows = [ #todo: упавший тест
            {
                'supplier': self.v1.external_id,
                'destination': str(self.wh1.code),
                'delivery_type': 'pbl',
                'transit_warehouse': self.wh2.code,
                'transit_time': 5,
                'day': 'general',
            },
            {
                'supplier': self.v1.external_id,
                'destination': str(self.wh_tag1.name),
                'delivery_type': 'dc_cross_docking',
                'transit_warehouse': self.wh2.code,
                'transit_time': 10,
                'day': 'general',
            },
        ]
        serialized_rows = cross_import.serialize(copy.deepcopy(rows))
        cross_import.save(serialized_rows)
        chains = self.env['cross.dock.pbl'].search([])

        self.assertEqual(len(chains), len(rows))

        self.assertEqual(chains[0].type_destination, 'warehouse')
        self.assertEqual(chains[0].delivery_type, 'dc_pbl')
        self.assertEqual(chains[0].vendor_id.external_id, rows[0]['supplier'])
        self.assertEqual(chains[0].destination_warehouse.code, rows[0]['destination'])
        self.assertEqual(chains[0].transit_warehouse.code, rows[0]['transit_warehouse'])
        self.assertEqual(chains[0].line_ids.transit_time, rows[0]['transit_time'])
        self.assertEqual(chains[0].line_ids.day, rows[0]['day'])

        self.assertEqual(chains[1].type_destination, 'geo')
        self.assertEqual(chains[1].delivery_type, 'dc_cross_docking')
        self.assertEqual(chains[1].vendor_id.external_id, rows[1]['supplier'])
        self.assertEqual(chains[1].destination_geo.name, rows[1]['destination'])
        self.assertEqual(chains[1].transit_warehouse.code, rows[1]['transit_warehouse'])
        self.assertEqual(chains[1].line_ids.transit_time, rows[1]['transit_time'])
        self.assertEqual(chains[1].line_ids.day, rows[1]['day'])
