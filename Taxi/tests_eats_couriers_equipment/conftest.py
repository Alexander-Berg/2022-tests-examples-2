# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from eats_couriers_equipment_plugins import *  # noqa: F403 F401

PERSONAL_BULK_STORE_URL = '/personal/v1/phones/bulk_store'
PERSONAL_FIND_URL = '/personal/v1/phones/find'
PHONES_MAP = {
    '+79999999999': '18d9c9ed14cf46538263a0a51f8a473a',
    '+78888888888': '28d9c9ed14cf46538263a0a51f8a473a',
    '+70000000001': '38d9c9ed14cf46538263a0a51f8a473a',
    '+70000000002': '48d9c9ed14cf46538263a0a51f8a473a',
    '+70000000003': '58d9c9ed14cf46538263a0a51f8a473a',
    '+70000000004': '68d9c9ed14cf46538263a0a51f8a473a',
}


@pytest.fixture()
def get_cursor(pgsql):
    def create_cursor():
        return pgsql['outsource-lavka-transport'].dict_cursor()

    return create_cursor


@pytest.fixture
async def personal_find(mockserver):
    @mockserver.json_handler(PERSONAL_FIND_URL)
    def _mock_personal_find(request):
        assert request.json.keys() == {'value', 'primary_replica'}
        phone = request.json['value']
        if phone in PHONES_MAP:
            return {'id': PHONES_MAP[phone], 'value': phone}
        return mockserver.make_response(
            json={'code': '404', 'message': 'Doc not found in mongo'},
            status=404,
        )

    return _mock_personal_find


@pytest.fixture
async def personal_bulk_store(mockserver):
    @mockserver.json_handler(PERSONAL_BULK_STORE_URL)
    def _mock_personal_bulk_store(request):
        assert 'items' in request.json, request.json
        result = []
        for item in request.json['items']:
            assert item.get('value')
            phone = item['value']
            if phone in PHONES_MAP:
                result.append({'value': phone, 'id': PHONES_MAP[phone]})
        return {'items': result}

    return _mock_personal_bulk_store


@pytest.fixture
async def personal_empty_bulk_store(mockserver):
    @mockserver.json_handler(PERSONAL_BULK_STORE_URL)
    def _mock_personal_bulk_store(request):
        return {'items': []}

    return _mock_personal_bulk_store
