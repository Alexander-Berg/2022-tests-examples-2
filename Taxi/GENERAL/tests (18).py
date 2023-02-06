import json
from unittest.mock import patch

import requests
from django.test import TestCase
from requests import Response

from common.authentication import get_user_data_by_barcode


def get_response(data, status_code=200):
    resp = Response()
    resp.code = "expired"
    resp.error_type = "expired"
    resp.status_code = status_code
    resp._content = json.dumps(data).encode()
    return resp


class BarcodeAuth(TestCase):
    def test_get_user_data(self):
        resp_data = {
            'code': 'OK',
            'user': 'urpewrpweu',
            'store': 'rupupoopod;jl',
            'fullname': 'Vasiliy Zadov',
            'token': ';j;oioei34980fs',
            'mode': 'wms',
            'permits': [],
        }
        with patch.object(requests, 'post',
                          return_value=get_response(resp_data)):
            user_data = get_user_data_by_barcode('some_devicew',
                                                 'some_barcode')

        self.assertTrue(user_data.get('user'))
        self.assertTrue(user_data.get('store'))
        self.assertTrue(user_data.get('fullname'))
