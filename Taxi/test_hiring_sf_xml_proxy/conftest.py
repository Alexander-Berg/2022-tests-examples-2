# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import functools
import logging

import pytest

import hiring_sf_xml_proxy.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['hiring_sf_xml_proxy.generated.service.pytest_plugins']


logger = logging.getLogger(__name__)


@pytest.fixture  # noqa: F405
def replication(mockserver):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/replication/data/test')
    def put_data_into_queue(request):
        data = [{'id': '13123', 'status': 'ok'}]
        return data


@pytest.fixture
def personal(mockserver, response_mock, load_json):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _store_phone(request):
        assert request.json['value']
        return {
            'id': 'eb79288c2399407c8f1319ed6ba5f873',
            'value': '+79859594523',
        }

    @mockserver.json_handler('/personal/v1/driver_licenses/store')
    def _store_license(request):
        return {'id': 'eb79288c2399407c8f1319ed6ba5f874', 'value': '0011ABCDE'}


def main_configuration(func):
    @pytest.mark.config(  # noqa: F405
        TVM_RULES=[
            {'dst': 'replication', 'src': 'hiring-sf-xml-proxy'},
            {'dst': 'personal', 'src': 'hiring-sf-xml-proxy'},
        ],
        HIRING_SF_XML_PROXY_PERSONAL_FIELD_TYPES={
            'test/Phone': 'phones',
            'test/License': 'driver_licenses',
            'test/NewPhone': 'phones',
            'test/PhoneNumber': 'phones',
        },
    )
    @pytest.mark.usefixtures('replication', 'personal')  # noqa: F405
    @functools.wraps(func)
    async def patched(*args, **kwargs):
        await func(*args, **kwargs)

    return patched
