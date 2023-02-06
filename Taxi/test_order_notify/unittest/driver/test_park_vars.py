import json

import pytest

from order_notify.generated.stq3 import stq_context
from order_notify.repositories.driver import park_vars


PARK_DATA: dict = {
    'inn': 'inn',
    'ogrn': 'ogrn',
    'short_name': 'short_name',
    'legal_address': 'legal_address',
    'name': 'name',
}


@pytest.fixture(name='mock_server')
def mock_server_fixture(mockserver):
    @mockserver.handler('/parks-replica/v1/parks/retrieve')
    def _get_parks_info(request):
        request_json = json.loads(request.get_data())
        park_id = request_json['id_in_set'][0]
        assert park_id in ('0', '1', '2', '3')
        if park_id == '0':
            return mockserver.make_response(
                json={'parks': [{'park_id': park_id, 'data': PARK_DATA}]},
            )
        if park_id == '1':
            return mockserver.make_response(
                json={'parks': [{'park_id': park_id}]},
            )
        if park_id == '3':
            PARK_DATA['short_name'] = None
            return mockserver.make_response(
                json={'parks': [{'park_id': park_id, 'data': PARK_DATA}]},
            )
        return mockserver.make_response(json={'parks': []})


@pytest.mark.parametrize(
    'park_id, expected_vars',
    [
        pytest.param(
            '0',
            {
                'park_inn': PARK_DATA['inn'],
                'park_ogrn': PARK_DATA['ogrn'],
                'park_legal_name': PARK_DATA['short_name'],
                'park_legal_address': PARK_DATA['legal_address'],
            },
            id='park_exists',
        ),
        pytest.param('1', {}, id='no_park_data'),
        pytest.param('2', {}, id='no_park'),
        pytest.param(
            '3',
            {
                'park_inn': PARK_DATA['inn'],
                'park_ogrn': PARK_DATA['ogrn'],
                'park_legal_name': PARK_DATA['name'],
                'park_legal_address': PARK_DATA['legal_address'],
            },
            id='no_short_name',
        ),
    ],
)
async def test_get_park_vars(
        stq3_context: stq_context.Context, mock_server, park_id, expected_vars,
):
    p_vars = await park_vars.get_park_vars(
        context=stq3_context, park_id=park_id, locale='ru',
    )
    assert p_vars == expected_vars
