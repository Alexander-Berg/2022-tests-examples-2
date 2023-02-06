from odoo.tests.common import SavepointCase, tagged, json
import datetime as dt

@tagged('lavka', 'warehouses', 'wms_integration')
class TestWarehouseLavka(SavepointCase):
    def setUp(self):
        super().setUp()
        self.stores_data_form_wms_to_update = [
            # Store #1
            {
                "company_id": "123",
                "store_id": "store_id_00",
                "external_id": "TESTWH00",
                "status": "status",
                "title": "Existing_warehouse",
                "slug": "TESTWH00",
                "address": "KUKUEVO_0",
                "open_ts": None,
                "timezone": "Europe/Paris",
                "attr": {
                    "telephone": "telephone",
                    "telegram": "telegram",
                    "email": '',
                    "directions": "null"
                },
                "type": 'lavka',
                'source': 'wms'
            },
            # Store #2
            {
                "company_id": "123",
                "store_id": "store_id_11",
                "external_id": "TESTWH11",
                "status": "status",
                "title": "Warehouse_to_UPDATE",
                "slug": "TESTWH11",
                "address": "KUKUEVO_1",
                "open_ts": "2019-12-31T21:00:00+00:00",
                "timezone": "Europe/Paris",
                "attr": {
                    "telephone": "telephone11",
                    "telegram": "telegram11",
                    "email": "n@ya.ru",
                    "directions": ''
                },
                "type": 'lavka',
                'source': 'wms'
            },
            # DC #1
            {
                "company_id": "123",
                "store_id": "store_id_dc_11",
                "external_id": "TESTDC11",
                "status": "status",
                "title": "DC_to_UPDATE",
                "slug": "TESTDC11",
                "address": "KUKUEVO_1",
                "open_ts": "2019-12-31T21:00:00+00:00",
                "timezone": "Europe/Paris",
                "attr": {
                    "telephone": "telephone11",
                    "telegram": "telegram11",
                    "email": "n@ya.ru",
                    "directions": ''
                },
                "type": 'dc',
                'source': 'wms'
            },
        ]

        self.stores_data_form_wms = [
            # Store #1
            {
                "company_id": "123",
                "store_id": "store_id_00",
                "external_id": "TESTWH00",
                "status": "status",
                "title": "Existing_warehouse",
                "slug": "TESTWH00",
                "address": "KUKUEVO_0",
                "open_ts": None,
                "timetable": [],
                "timezone": "Europe/Paris",
                "attr": {
                    "telephone": "telephone",
                    "telegram": "telegram",
                    "email": '',
                    "directions": "null"
                },
                "type": 'lavka',
                'source': 'wms'
            },
            # Store #2
            {
                "company_id": "123",
                "store_id": "store_id_11",
                "external_id": "TESTWH11",
                "status": "status",
                "title": "Warehouse_to_UPDATE",
                "slug": "TESTWH11",
                "address": "KUKUEVO_1",
                "open_ts": "2019-12-31T21:00:00+00:00",
                "timetable": [
                    {
                        "begin": "07:30",
                        "end": "23:10",
                        "type": "everyday"
                    }
                ],
                "timezone": "Europe/Paris",
                "attr": {
                    "telephone": "telephone11",
                    "telegram": "telegram11",
                    "email": "n@ya.ru",
                    "directions": ''
                },
                "type": 'lavka',
                'source': 'wms'
            },
            # Store #3
            {
                "company_id": "123",
                "store_id": "store_id_22",
                "external_id": "TESTWH2",
                "status": "status",
                "title": "Warehouse_to_CREATE",
                "slug": "TESTWH2",
                "address": "KUKUEVO_2",
                "open_ts": "2019-12-31T21:00:00-03:00",
                "timezone": "Europe/Moscow",
                "timetable": [
                    {
                        "begin": "02:15",
                        "end": "23:45",
                        "type": "everyday"
                    }
                ],
                "attr": {
                    "telephone": "telephone2",
                    "telegram": "telegram12",
                    "email": "n2@ya.ru",
                    "directions": "kukuevo"
                },
                "type": 'lavka',
                'source': 'wms'
            },
            # Store #3
            {
                "company_id": "123",
                "store_id": "store_id_dc_22",
                "external_id": "TESTDC2",
                "status": "status",
                "title": "DC_to_CREATE",
                "slug": "TESTDC2",
                "address": "KUKUEVO_2",
                "open_ts": "2019-12-31T21:00:00-03:00",
                "timezone": "Europe/Moscow",
                "timetable": [
                    {
                        "begin": "02:15",
                        "end": "23:45",
                        "type": "everyday"
                    }
                ],
                "attr": {
                    "telephone": "telephone2",
                    "telegram": "telegram12",
                    "email": "n2@ya.ru",
                    "directions": "kukuevo"
                },
                "type": 'dc',
                'source': 'wms'
            },
        ]

        self.stores_data_form_wms_to_create = [
            {
                "company_id": "123",
                "store_id": "store_id_22",
                "external_id": "TESTWH2",
                "status": "status",
                "title": "Warehouse_to_CREATE",
                "slug": "TESTWH2",
                "address": "KUKUEVO_2",
                "open_ts": None,
                "timezone": "Europe/Paris",
                "timetable": [
                    {
                        "begin": "02:00",
                        "end": "23:45",
                        "type": "everyday"
                    }
                ],
                "attr": {
                    "telephone": "telephone2",
                    "telegram": "telegram12",
                    "email": "n2@ya.ru",
                    "directions": "kukuevo"
                },
                "type": 'lavka',
                'source': 'wms'
            },
            {
                "company_id": "123",
                "store_id": "store_id_33",
                "external_id": "TESTWH3",
                "status": "status",
                "title": "Warehouse_to_CREATE2",
                "slug": "TESTWH2",
                "address": "KUKUEVO_3",
                "open_ts": "2019-12-31T21:00:00+00:00",
                "timezone": "Europe/Moscow",
                "timetable": [
                    {
                        "begin": "03:10",
                        "end": "23:35",
                        "type": "everyday"
                    }
                ],
                "attr": {
                    "telephone": "telephone3",
                    "telegram": "telegram13",
                    "email": "n3@ya.ru",
                    "directions": "kukuevo3"
                },
                "type": 'lavka',
                'source': 'wms'
            },
            {
                "company_id": "123",
                "store_id": "store_id_dc_33",
                "external_id": "TESTDC3",
                "status": "status",
                "title": "DC_to_CREATE2",
                "slug": "TESTDC2",
                "address": "KUKUEVO_3",
                "open_ts": "2019-12-31T21:00:00+00:00",
                "timezone": "Europe/Moscow",
                "timetable": [
                    {
                        "begin": "03:10",
                        "end": "23:35",
                        "type": "everyday"
                    }
                ],
                "attr": {
                    "telephone": "telephone3",
                    "telegram": "telegram13",
                    "email": "n3@ya.ru",
                    "directions": "kukuevo3"
                },
                "type": 'dc_external',
                'source': 'wms'
            },
        ]

        self.warehouse = self.env['stock.warehouse']
        # no change should be done
        self.warehouse_1 = self.warehouse.create(
            {
                'wms_id': 'store_id_00',
                'company_id': self.env.company.id,
                # 'external_id': 'external_id_0',
                'status': 'status',
                'name': 'Existing_warehouse',
                'code': 'TESTWH00',
                "address": "KUKUEVO_0",
                "open_date": dt.date.today(),
                'attr': json.dumps({
                  "telephone": 'telephone',
                  "telegram": 'telegram',
                  "email": '',
                  "directions": 'null'
                }),
                "type": 'lavka',
                'source': 'wms'
            }
        )
        # to update
        self.warehouse_2 = self.warehouse.create(
            {
                'wms_id': 'store_id_11',
                'company_id': self.env.company.id,
                # 'external_id': 'external_id_1',
                'status': 'old_status',
                'name': 'Existing_warehouse_old_0',
                'code': 'TESTWH11',
                "address": "KUKUEVO_11",
                'attr': json.dumps({
                  "telephone": 'telephone1',
                  "telegram": 'telegram1',
                  "email": '',
                  "directions": 'null'
                }),
                "type": 'lavka',
                'source': 'wms'
            }
        )

    def test_create_update_warehouse(self):
        stores = self.stores_data_form_wms
        mapped_data = {store_data['store_id']: self.env['stock.warehouse'].match_row_to_store_fields(store_data) for store_data in stores}
        stores_to_create, stores_to_update = self.env['stock.warehouse'].check_stores_to_process(mapped_data)

        self.assertIsNotNone(stores_to_create['store_id_22'], 'No ids to create, expected store_id_22')
        self.assertIsNotNone(stores_to_update['store_id_11'], 'Wrong ids to update, expected store_id_11')
        self.assertIsNotNone(stores_to_update['store_id_00'], 'Wrong ids to update, expected store_id_00')

        result = self.env['stock.warehouse'].create_stores(stores_to_create, stores_to_update)

        created = self.warehouse.search([('wms_id', '=', stores[2].get('store_id'))])
        self.assertEqual(created.wms_id, stores[2].get('store_id'), 'Store #3 is not created!')
        self.assertIsNotNone(created.open_date, 'Open date is not imported')

        created_dc = self.warehouse.search([('wms_id', '=', stores[3].get('store_id'))])
        self.assertEqual(created_dc.wms_id, stores[3].get('store_id'), 'Store DC is not created!')
        self.assertEqual(created_dc.type, 'dc', 'Store DC has no type dc!')

        updated = {i.wms_id: i for i in self.warehouse.search([('wms_id', 'in', ['store_id_11', 'store_id_00'])])}
        store_id_11 = updated.get('store_id_11')
        store_id_00 = updated.get('store_id_00')
        self.assertIsNotNone(store_id_11.open_date, 'Open date is not imported')
        self.assertFalse(store_id_00.open_date, 'Open date not cleaned')
        self.assertEqual(len(updated), 2, 'Store store_id_11  and store_id_00 is not updated!')

    def test_update_only_warehouse(self):
        stores = self.stores_data_form_wms_to_update
        mapped_data = {store_data['store_id']: self.env['stock.warehouse'].match_row_to_store_fields(store_data) for store_data in stores}
        stores_to_create, stores_to_update = self.env['stock.warehouse'].check_stores_to_process(mapped_data)

        self.assertIsNotNone(stores_to_update['store_id_11'], 'Wrong ids to update, expected store_id_11')
        self.assertIsNotNone(stores_to_update['store_id_00'], 'Wrong ids to update, expected store_id_00')

        result = self.env['stock.warehouse'].create_stores(stores_to_create, stores_to_update)

        updated = {i.wms_id: i for i in self.warehouse.search([('wms_id', 'in', ['store_id_11', 'store_id_00'])])}
        store_id_11 = updated.get('store_id_11')
        store_id_00 = updated.get('store_id_00')
        self.assertIsNotNone(store_id_11.open_date, 'Open date is not imported')
        self.assertFalse(store_id_00.open_date, 'Open date not cleaned')
        self.assertEqual(len(updated), 2, 'Store store_id_11  and store_id_00 is not updated!')

    def test_create_only_warehouse(self):
        stores = self.stores_data_form_wms_to_create
        mapped_data = {store_data['store_id']: self.env['stock.warehouse'].match_row_to_store_fields(store_data) for store_data in stores}
        stores_to_create, stores_to_update = self.env['stock.warehouse'].check_stores_to_process(mapped_data)

        self.assertIsNotNone(stores_to_create['store_id_22'], 'No ids to create, expected store_id_22')

        result = self.env['stock.warehouse'].create_stores(stores_to_create, stores_to_update)

        created = self.warehouse.search([('wms_id', '=', stores[0].get('store_id'))])
        self.assertEqual(created.wms_id, stores[0].get('store_id'), 'Store #3 is not created!')
        self.assertIsNotNone(created.open_date, 'Open date is not imported')

        created1 = self.warehouse.search([('wms_id', '=', stores[1].get('store_id'))])
        self.assertEqual(created1.wms_id, stores[1].get('store_id'), 'Store #4 is not created!')
        self.assertIsNotNone(created1.open_date, 'Open date is not imported')

        created_dc = self.warehouse.search([('wms_id', '=', stores[2].get('store_id'))])
        self.assertEqual(created_dc.wms_id, stores[2].get('store_id'), 'Store dc is not created!')
        self.assertIsNotNone(created_dc.open_date, 'Open date is not imported')
        self.assertEqual(created_dc.type, 'dc_external', 'Store DC has no type dc!')


    def test_update_duplicate_only_warehouse(self):
        stores = self.stores_data_form_wms_to_update
        mapped_data = {store_data['store_id']: self.env['stock.warehouse'].match_row_to_store_fields(store_data) for store_data in stores}
        stores_to_create, stores_to_update = self.env['stock.warehouse'].check_stores_to_process(mapped_data)

        stores = self.env['stock.warehouse'].create_stores(stores_to_create, stores_to_update)

        updated = {i.wms_id: i for i in stores}
        store_id_11 = updated.get('store_id_11')
        store_id_00 = updated.get('store_id_00')
        self.assertIsNotNone(store_id_11)
        self.assertIsNotNone(store_id_00)

        # проверим проверку на update

        store_id_00.name = store_id_11.name
        store_id_00.write({'name': store_id_11.name})
        self.assertTrue(store_id_00.name.startswith('DUPLICATED'))
        # проверим, что сам себя записывает
        store_id_11.write({'name': store_id_11.name})

    def test_create_duplicate_warehouse(self):
        wh_data = [
            {'wms_id': 'store_id_00',
             'company_id': self.env.company.id,
             'status': 'status',
             'name': 'Existing_warehouse',
             'code': 'TESTWH00000002',
             "address": "KUKUEVO_00",
             "open_date": dt.date.today(),
             'attr': json.dumps({
                 "telephone": 'telephone',
                 "telegram": 'telegram',
                 "email": '',
                 "directions": 'null'
             })},
        ]

        self.env['stock.warehouse'].create(wh_data)

