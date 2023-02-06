# -*- coding: utf-8 -*-
# pylint: disable=import-error, unused-argument, too-many-locals, protected-access
import json
import os
from collections import defaultdict
from datetime import datetime
from unittest.mock import patch
import xml.etree.ElementTree as ET
from common.client.wms import WMSConnector
from freezegun import freeze_time
from odoo import exceptions
from odoo.tests import tagged
from odoo.tests.common import Form
from .test_common import TestVeluationCommon
from .test_orders import Fixtures
from odoo.addons.lavka.tests.utils import save_xlsx_report, get_stock_loc, read_json_data

FIXTURES_PATH = 'transfer_test'

def _get_shipment_response(transfer):
    shipment_tmpl = {
        'order_id': '',
        'type': 'shipment',
        'doc_number': f'{datetime.now()}',
        'request_type': 'shipment',
    }
    req = []
    for line in transfer.transfer_lines:
        req.append({
            'product_id': line.product_id.wms_id,
            'count': line.qty_plan,
        })
    shipment_tmpl.update({'required': req})
    return shipment_tmpl


# TODO заменить на метод Андрея
def _create_delta(transfer_lines, shipment_required):
    shipment_delta = defaultdict(int)
    for required in shipment_required:
        shipment_delta[required['product_id']] = required['result_count']
    return shipment_delta


def mocked_requests_for_order(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    fixtures = Fixtures()
    path = args[0].rsplit('/', 1)[1]
    if path == 'log':
        return MockResponse({"stocks_log": fixtures.order_log_data}, 200)
    return MockResponse(None, 404)


def mocked_path(*args, **kwargs):
    return args[1]


# pylint: disable=invalid-name,too-many-statements
@tagged('lavka', 'transfer')
class TestTransfer(TestVeluationCommon):
    wms_connector = WMSConnector()

    # pylint: disable=unused-variable, attribute-defined-outside-init
    def _create_transfer(self, params):
        self.transfer = self.env['transfer.lavka'].create(params)
        return self.transfer.id

    def _create_lines(self, transfer_id=None):
        if transfer_id is None:
            transfer_id = self.transfer.id
        lines = [
            {
                'transfer_id': transfer_id,
                'product_id': self.products[0].id,
                'qty_plan': 5,
            },
            {
                'transfer_id': transfer_id,
                'product_id': self.products[1].id,
                'qty_plan': 10,
            },
        ]
        self.env['transfer.lavka.line'].create(lines)

    def test_transfer_create_lines(self):
        params = {
            'warehouse_out': self.warehouse_1.id,
            'warehouse_in': self.warehouse_4.id,
            'date_planned': datetime.now()
        }
        self._create_transfer(params)
        self._create_lines()
        self.assertEqual(len(self.transfer.transfer_lines), 2, 'Длина совпала')

    def test_import_stocks_for_line(self):
        params = {
            'warehouse_out': self.warehouse_1.id,
            'warehouse_in': self.warehouse_4.id,
            'state': 'draft',
            'date_planned': datetime.now()
        }
        self._create_transfer(params)
        self._create_lines()

        with patch(
                'common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
            get_wms_data_mock.return_value = read_json_data(
                folder=FIXTURES_PATH,
                filename='stocks',
            ), None
            self.transfer.check_transfer_lines(self.transfer.state)

        self.assertEqual(len(self.transfer.transfer_lines), 2,
                         'Длина не изменилась')

        result_dict = {
            self.products[0].id: 5,
            self.products[1].id: 7,
        }

        from_transfer_lines = {
            line.product_id.id: line.qty_plan
            for line in self.transfer.transfer_lines
        }

        self.assertEqual(
            from_transfer_lines, result_dict,
            'значения изменились'
        )

    def test_import_stocks_all(self):
        params = {
            'warehouse_out': self.warehouse_1.id,
            'warehouse_in': self.warehouse_4.id,
            'date_planned': datetime.now()
        }
        self._create_transfer(params)
        self.assertEqual(len(self.transfer.transfer_lines), 0,
                         'Линий нет')

        with patch(
                'common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
            get_wms_data_mock.return_value = read_json_data(
                folder=FIXTURES_PATH,
                filename='stocks',
            ), None
            self.transfer.fill_transfer_lines_from_wms(self.transfer.state)

        self.assertEqual(len(self.transfer.transfer_lines), 4,
                         'Длина изменилась')

    def test_approve(self):
        params = {
            'warehouse_out': self.warehouse_1.id,
            'warehouse_in': self.warehouse_4.id,
            'source': 'user',
            'date_planned': datetime.now()
        }
        self._create_transfer(params)
        self._create_lines()

        self.assertEqual(self.transfer.source, 'user',
                         'source есть')
        self.assertEqual(self.transfer.state, 'draft',
                         'статус draft')

        self.env.user.groups_id = [(4, self.env.ref('lavka.group_catman').id)]
        self.transfer.button_approved()
        self.assertEqual(self.transfer.state, 'approved',
                         'статус approved')
        self.assertEqual(
            self.transfer.user_approved,
            self.env.user,
            'юзер прсотавлен'
        )

    def test_shipment(self):
        params = {
            'warehouse_out': self.warehouse_1.id,
            'warehouse_in': self.warehouse_4.id,
            'source': 'user',
            'date_planned': datetime.now(),
            'external_id': 'transf2343',
            'state': 'draft',
        }
        self._create_transfer(params)
        self._create_lines()

        with self.assertRaises(exceptions.UserError):
            self.transfer.button_send_shipment()

        self.transfer.state = 'approved'

        with patch(
                'common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
            data = {}
            get_wms_data_mock.return_value = data, None
            with self.assertRaises(exceptions.UserError):
                self.transfer.button_send_shipment()
        with patch('odoo.addons.lavka.backend.models.transfer.Transfer._get_products_by_stock') as _get_products_by_stock_mock:
            _get_products_by_stock_mock.return_value = {'126903': 10, '11909': 12},\
                                                       {('126903', 'store'): 10, ('11909', 'store'): 12}
            with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
                data = _get_shipment_response(self.transfer)
                data.update({'order_id': 'dd3bc1144ce545c48c104bf6646976b6000200010001'})
                get_wms_data_mock.return_value = data, None
                self.transfer.button_send_shipment()

        self.assertEqual(self.transfer.state, 'sent', 'статус изменился')
        self.assertEqual(self.transfer.shipment_id, data['order_id'],
                         'shipment_id появился')

    def test_acceptance(self):
        params = {
            'warehouse_out': self.warehouse_1.id,
            'warehouse_in': self.warehouse_4.id,
            'source': 'user',
            'date_planned': datetime.now(),
            'external_id': 'transf2343',
            'state': 'sent',
        }
        self._create_transfer(params)
        self._create_lines()

        with patch(
                'common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
            data = {'order_id': 'dd3bc1144ce545c48c104bf6646976b6000200010001'}
            get_wms_data_mock.return_value = data, None
            self.transfer.acceptance_jobs(external_id=self.transfer.external_id)

        self.assertEqual(self.transfer.state, 'in_transfer', 'статус изменился')
        self.assertEqual(self.transfer.acceptance_id, data['order_id'],
                         'acceptance появился')

    @patch('common.client.wms.WMSConnector.smart_url_join',
           side_effect=mocked_path)
    @patch('common.client.wms._session.post',
           side_effect=mocked_requests_for_order)
    def test_move(self, request, url):
        shipment_imported = read_json_data(
                folder=FIXTURES_PATH,
                filename='shipment',
            )

        with patch(
                'common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
            data = read_json_data(
                folder=FIXTURES_PATH,
                filename='stocks_shipment',
            )
            get_wms_data_mock.return_value = data, None

            fixtures = Fixtures()
            with freeze_time('2021-03-15 12:00:00'):
                self.env['wms_integration.order'].create_wms_order(
                    [shipment_imported], self.wms_connector)
            shipment = self.env['wms_integration.order'].search(
                [('order_id', '=', 'shipment')])

        acceptance_imported = read_json_data(
            folder=FIXTURES_PATH,
            filename='acceptance',
        )
        with patch(
                'common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
            data = read_json_data(
                folder=FIXTURES_PATH,
                filename='stocks_acceptance',
            )
            get_wms_data_mock.return_value = data, None

            fixtures = Fixtures()
            with freeze_time('2021-03-15 12:00:00'):
                self.env['wms_integration.order'].create_wms_order(
                    [acceptance_imported], self.wms_connector)
                acceptance = self.env['wms_integration.order'].search(
                    [('order_id', '=', 'acceptance')])

        params = {
            'warehouse_out': self.warehouse_1.id,
            'warehouse_in': self.warehouse_4.id,
            'source': 'user',
            'date_planned': datetime.now(),
            'external_id': 'transf2343',
            'shipment_id': shipment.order_id,
            'acceptance_id': acceptance.order_id,
            'state': 'sent',
            'date_shipment': datetime.now(),
        }
        self._create_transfer(params)
        with patch(
                'common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
            get_wms_data_mock.return_value = read_json_data(
                folder=FIXTURES_PATH,
                filename='stocks',
            ), None
            self.transfer.fill_transfer_lines_from_wms(self.transfer.state)

        #TODO change to Andrew method
        shipment_delta = _create_delta(
            self.transfer.transfer_lines,
            shipment_imported['required']
        )

        self.transfer._create_shipment_move(
            shipment,
            shipment_delta
        )

        self.transfer.transfer_lines._compute_qty()
        # проверяем qty_in_transfer
        result_dict = {
            self.products[0].id: 9,
            self.products[1].id: 7,
            self.products[2].id: 10,
            self.products[3].id: 5,
            self.products[4].id: 1,
        }
        from_transfer_lines = {
            line.product_id.id: line.qty_in_transfer
            for line in self.transfer.transfer_lines
        }

        self.assertEqual(result_dict, from_transfer_lines,
                         'qty_in_transfer изменен')

        # проверяем транзакции
        # должен быть уход с OPER warehouse_out
        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.transfer.warehouse_out.lot_stock_id)

        self.assertEqual(qty, -32)
        self.assertEqual(valuation_qty, -32)
        self.assertEqual(value, -168)
        self.assertEqual(rem_qty, -32)
        self.assertEqual(rem_value, -168)

        # приход на GIT warehouse_in
        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.transfer.warehouse_in.wh_stock_git)

        self.assertEqual(qty, 32)
        self.assertEqual(valuation_qty, 32)
        self.assertEqual(value, 168)
        self.assertEqual(rem_qty, 32)
        self.assertEqual(rem_value, 168)


        # TODO change to Andrew method
        acceptance_delta = _create_delta(
            self.transfer.transfer_lines,
            acceptance_imported['required']
        )
        self.transfer._receiving_moves(
            acceptance,
            acceptance_delta
        )

        self.transfer.transfer_lines._compute_qty()
        # проверяем qty_received
        result_dict = {
            self.products[0].id: 9,
            self.products[1].id: 7,
            self.products[2].id: 11,
            self.products[3].id: 6,
            self.products[4].id: 1,
        }
        from_transfer_lines = {
            line.product_id.id: line.qty_received
            for line in self.transfer.transfer_lines
        }

        self.assertEqual(result_dict, from_transfer_lines,
                         'qty_received изменен')

        # git warehouse_in
        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.transfer.warehouse_in.wh_stock_git)

        self.assertEqual(qty, 0)
        self.assertEqual(valuation_qty, 0)
        self.assertEqual(value, 0)
        self.assertEqual(rem_qty, 0)
        self.assertEqual(rem_value, 0)

        # stock warehouse_in
        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.transfer.warehouse_in.lot_stock_id)

        self.assertEqual(qty, 34)
        self.assertEqual(valuation_qty, 34)
        self.assertEqual(value, 178.5)
        self.assertEqual(rem_qty, 34)
        self.assertEqual(rem_value, 178.5)

        result_dict = {
            self.products[0].id: 0,
            self.products[1].id: 0,
            self.products[2].id: 0,
            self.products[3].id: 0,
            self.products[4].id: 0,
        }
        from_transfer_lines = {
            line.product_id.id: line.qty_diff
            for line in self.transfer.transfer_lines
        }
        self.assertEqual(result_dict, from_transfer_lines, 'qty_diff 0')

        # приход на warehouse_out
        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.transfer.warehouse_out.wh_stock_diff)

        self.assertEqual(qty, 0)
        self.assertEqual(valuation_qty, 0)
        self.assertEqual(value, 0)
        self.assertEqual(rem_qty, 0)
        self.assertEqual(rem_value, 0)

        # recount 1
        recount_delta = {
            self.products[0].wms_id: 1,
            self.products[1].wms_id: -1,
            self.products[2].wms_id: 1,
            self.products[3].wms_id: -1,
            self.products[4].wms_id: 1,
        }

        recount_imported = read_json_data(
            folder=FIXTURES_PATH,
            filename='recount',
        )
        with patch(
                'common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
            data = read_json_data(
                folder=FIXTURES_PATH,
                filename='stocks_recount',
            )
            get_wms_data_mock.return_value = data, None

            fixtures = Fixtures()
            with freeze_time('2021-03-15 12:00:00'):
                self.env['wms_integration.order'].create_wms_order(
                    [recount_imported], self.wms_connector)
                recount = self.env['wms_integration.order'].search(
                    [('order_id', '=', 'recount')])

        self.transfer._receiving_moves(
            recount,
            recount_delta
        )

        # приход на warehouse_in git
        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.transfer.warehouse_in.wh_stock_git)

        self.assertEqual(qty, 0)
        self.assertEqual(valuation_qty, 0)
        self.assertEqual(value, 0)
        self.assertEqual(rem_qty, 0)
        self.assertEqual(rem_value, 0)

        # приход на warehouse_in diff
        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.transfer.warehouse_in.wh_stock_diff)

        self.assertEqual(qty, -3)
        self.assertEqual(valuation_qty, -3)
        self.assertEqual(value, -15.75)
        self.assertEqual(rem_qty, -3)
        self.assertEqual(rem_value, -15.75)

        # recount 2
        recount_imported = read_json_data(
                folder=FIXTURES_PATH,
                filename='recount2',
            )
        with patch(
                'common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
            data = read_json_data(
                folder=FIXTURES_PATH,
                filename='stocks_recount',
            )
            get_wms_data_mock.return_value = data, None

            fixtures = Fixtures()
            with freeze_time('2021-03-15 12:00:00'):
                self.env['wms_integration.order'].create_wms_order(
                    [recount_imported], self.wms_connector)
                recount = self.env['wms_integration.order'].search(
                    [('order_id', '=', 'recount2')])

        recount_delta = {
            self.products[0].wms_id: -1,
            self.products[1].wms_id: 1,
            self.products[2].wms_id: -1,
            self.products[3].wms_id: 1,
            self.products[4].wms_id: -1,
        }

        self.transfer._receiving_moves(
            recount,
            recount_delta
        )

        # приход на warehouse_in git
        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.transfer.warehouse_in.wh_stock_git)

        self.assertEqual(qty, 0)
        self.assertEqual(valuation_qty, 0)
        self.assertEqual(value, 0)
        self.assertEqual(rem_qty, 0)
        self.assertEqual(rem_value, 0)

        # приход на warehouse_in diff
        qty, valuation_qty, value, rem_qty, rem_value = get_stock_loc(
            self,
            self.transfer.warehouse_in.wh_stock_diff)

        self.assertEqual(qty, -2)
        self.assertEqual(valuation_qty, -2)
        self.assertEqual(value, -10.5)
        self.assertEqual(rem_qty, -2)
        self.assertEqual(rem_value, -10.5)

        if os.environ.get('EXPORT_TEST_TO_XLS'):
            save_xlsx_report(
                self,
                locations=[self.transfer.warehouse_in.wh_stock_diff.id,
                           self.transfer.warehouse_in.wh_stock_git.id,
                           self.transfer.warehouse_in.lot_stock_id.id,
                           ],
                report_name='transfer_result',
            )

        if os.environ.get('EXPORT_TEST_TO_XLS'):
            save_xlsx_report(
                self,
                locations=[
                           self.transfer.warehouse_out.lot_stock_id.id,
                           ],
                report_name='transfer_result_out',
            )


@tagged('lavka', 'transfer1')
class TestUserRights(TestVeluationCommon):

    def test_visibility(self):
        params = {
            'warehouse_out': self.warehouse_1.id,
            'warehouse_in': self.warehouse_4.id,
            'date_planned': datetime.now()
        }
        self.transfer0 = self.env['transfer.lavka'].create([params])
        self.transfer1 = self.env['transfer.lavka'].create([params])
        _user = self.env['res.users'].create([{
            'login': 'test',
            'password': 'test',
            'partner_id': self.env['res.partner'].create([{
                'name': 'Test'
            }]).id,
            'groups_id': self.env.ref('lavka.group_catman').ids
        }])
        # в данном тесте криво проверяется что кнопка невидима
        # нужны фронтовые тесты
        form = Form(self.env['transfer.lavka'].with_user(_user.id), view='lavka.transfer_tree_view')
        xml = ET.fromstring(form._view['arch'])
        for obj in xml.iter('header'):
            for button in obj:
                if button.attrib['name'] == 'acceptance_jobs':
                    self.assertEqual(button.attrib['invisible'], '1')
