import json
import os

import bson.json_util
import pytest

TRANSLATIONS_TARIFF_EDITOR = {
    'vgw.direction.onuser4driver': {'ru': 'водитель клиенту'},
    'vgw.direction.ondriver4user': {'ru': 'клиент водителю'},
    'vgw.direction.ondriver4sender': {'ru': 'отправитель водителю'},
    'vgw.direction.ondriver4recipient': {'ru': 'получатель водителю'},
    'vgw.direction.ondriver4unknown': {'ru': 'другой абонент водителю'},
    'vgw.direction.onuser4dispatch': {'ru': 'диспетчер клиенту'},
    'vgw.direction.ondispatch4user': {'ru': 'клиент диспетчеру'},
    'vgw.direction.onuser4qa': {'ru': 'контроль качества'},
}

RESPONSE_CACHE = {}
RESPONSES_DIR = os.path.join(
    os.path.dirname(__file__), 'static', 'test_get_talks', 'responses',
)
for root, _, filenames in os.walk(RESPONSES_DIR):
    for filename in filenames:
        full_filename = os.path.join(root, filename)
        if filename.endswith('.bson.json'):
            with open(full_filename) as f:
                RESPONSE_CACHE[filename[:-5]] = bson.json_util.loads(f.read())
        elif filename.endswith('.json'):
            with open(full_filename) as f:
                RESPONSE_CACHE[filename] = json.load(f)


@pytest.fixture
def taxi_admin_orders_mocks(mockserver, order_archive_mock):
    """Put your mocks here"""

    def _set_order_proc():
        for resp_filename, response in RESPONSE_CACHE.items():
            if resp_filename.startswith('order_archive-order_proc-retrieve'):
                order_archive_mock.set_order_proc(response['doc'])

    _set_order_proc()

    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def _v1_forwardings(request):
        order_id = request.query['external_ref_id']
        file_name = f'vgw-api_v1_forwardings_{order_id}.json'
        if file_name not in RESPONSE_CACHE:
            return mockserver.make_response(json=[])
        response = RESPONSE_CACHE[file_name]
        return mockserver.make_response(json=response)

    @mockserver.json_handler(
        '/user_api-api/user_phones/by_number/retrieve_bulk',
    )
    def _get_phone_docs(request):
        res = RESPONSE_CACHE[f'user-api_retrieve_bulk.json']
        return res

    @mockserver.json_handler('/user_api-api/user_phones/get_bulk')
    def _get_phone_docs_by_phone_id(request):
        res = RESPONSE_CACHE[f'user-api_retrieve_bulk.json']
        request_json = json.loads(request.get_data())
        phone_ids = request_json['ids']
        return {
            'items': [
                item for item in res['items'] if item['id'] in phone_ids
            ],
        }

    @mockserver.json_handler('/territories/v1/countries/list')
    def _get_countries_list(request):
        return RESPONSE_CACHE['territories_v1_countries_list.json']


@pytest.mark.config(
    VGW_TALKS_SOURCES_ENABLED='api_only',
    TVM_RULES=[{'dst': 'archive-api', 'src': 'admin-orders'}],
)
@pytest.mark.translations(tariff_editor=TRANSLATIONS_TARIFF_EDITOR)
@pytest.mark.usefixtures('taxi_admin_orders_mocks')
async def test_get_talks(taxi_admin_orders_web):

    response = await taxi_admin_orders_web.get('/v1/talks/?order_id=id3')
    content = await response.json()
    expected_response = RESPONSE_CACHE['admin-orders_talks_id3.json']
    assert content == expected_response

    response = await taxi_admin_orders_web.get(
        '/v1/talks/?order_id=id3&allow_raw_phones=true',
    )
    expected_filename = 'admin-orders_talks_id3_with_raw.json'
    expected_response = RESPONSE_CACHE[expected_filename]
    content = await response.json()
    assert content == expected_response


@pytest.mark.config(TVM_RULES=[{'dst': 'archive-api', 'src': 'admin-orders'}])
@pytest.mark.translations(tariff_editor=TRANSLATIONS_TARIFF_EDITOR)
@pytest.mark.usefixtures('taxi_admin_orders_mocks')
async def test_get_talks_no_callee(taxi_admin_orders_web):

    response = await taxi_admin_orders_web.get('/v1/talks/?order_id=id2')
    content = await response.json()
    expected_response = RESPONSE_CACHE['admin-orders_talks_id2.json']
    assert content == expected_response


@pytest.mark.config(TVM_RULES=[{'dst': 'archive-api', 'src': 'admin-orders'}])
@pytest.mark.translations(tariff_editor=TRANSLATIONS_TARIFF_EDITOR)
@pytest.mark.usefixtures('taxi_admin_orders_mocks')
async def test_get_talks_unknown_id(taxi_admin_orders_web):

    response = await taxi_admin_orders_web.get('/v1/talks/?order_id=id1')
    content = await response.json()
    expected_response = RESPONSE_CACHE['admin-orders_talks_empty.json']
    assert content == expected_response
