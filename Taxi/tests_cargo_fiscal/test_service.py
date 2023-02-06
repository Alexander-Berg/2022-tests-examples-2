import aiohttp
import pytest

# flake8: noqa
# pylint: disable=import-error,wildcard-import
from cargo_fiscal_plugins.generated_tests import *

# Feel free to provide your custom implementation to override generated tests.


@pytest.fixture(autouse=True)
def proxy_py2_delivery(mockserver):
    @mockserver.json_handler('/py2-delivery/fetch-fiscal-data')
    def _handler2(request):
        return mockserver.make_response(
            status=200,
            json={
                'inn_for_receipt': '085715582283',
                'inn_for_receipt_id': '1514a5c7d59247afa82489b273e45303',
                'nds_for_receipt': -1,
            },
        )


# @pytest.fixture(autouse=True)
# def proxy_ng_v2_invoice(mockserver, load_json):
#     @mockserver.json_handler('/transactions-ng/v2/invoice/retrieve')
#     def _handler2(request):
#         return mockserver.make_response(
#             status=200,
#             json=load_json('t-ng_v2_invoice_retrieve_response.json'),
#         )
