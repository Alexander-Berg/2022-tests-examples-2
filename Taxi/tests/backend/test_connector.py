# pylint: disable=relative-beyond-top-level,import-error,no-name-in-module

from unittest.mock import patch
from odoo import exceptions
from odoo.tests.common import SavepointCase, tagged

from common.client.wms import WMSConnector
from .test_orders import Fixtures


def mocked_path(*args, **kwargs):
    return args[1]


def mocked_requests_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            self.text = 'code not 200!'

        def json(self):
            return self.json_data

    fixtures = Fixtures()
    path = args[0].rsplit('/', 1)[1]
    if path == 'products':
        return MockResponse({"products": []}, 200)
    elif path == 'list':
        return MockResponse({"orders": []}, 200)
    elif path == 'log':
        return MockResponse({"stocks_log": fixtures.check_product_on_shelf_log_data}, 200)
    return MockResponse(None, 404)


def mocked_requests_post_raise_exception(*args, **kwargs):
    raise ConnectionError("no connection")


@tagged('lavka', 'wms_integration', 'connector')
class TestWMSConnector(SavepointCase):
    @patch('common.client.wms.WMSConnector.smart_url_join',
           side_effect=mocked_path)
    @patch('common.client.wms._session.post',
           side_effect=mocked_requests_post)
    def test_get_wms_data_products(self, url, post):
        test_wms_handler = WMSConnector()
        test_data, test_cursor = test_wms_handler.get_wms_data('/api/external/products/v1/products',
                                                               'products',
                                                               None)
        self.assertEqual(test_data, [])

    @patch('common.client.wms.WMSConnector.smart_url_join',
           side_effect=mocked_path)
    @patch('common.client.wms._session.post',
           side_effect=mocked_requests_post)
    def test_get_wms_data_wrong_path(self, requests, url):
        test_wms_handler = WMSConnector()
        with self.assertRaises(exceptions.UserError):
            test_data, test_cursor = test_wms_handler.get_wms_data('ftp/xxx', 'xxx', None)

    @patch('common.client.wms.WMSConnector.smart_url_join',
           side_effect=mocked_path)
    @patch('common.client.wms._session.post',
           side_effect=mocked_requests_post_raise_exception)
    def test_get_wms_data_exception(self, requests, url):
        test_wms_handler = WMSConnector()
        with self.assertRaises(exceptions.UserError):
            test_data, test_cursor = test_wms_handler.get_wms_data('/api/external/products/v1/products',
                                                                   'products', None)
        self.assertEqual(requests.call_count, 3)
