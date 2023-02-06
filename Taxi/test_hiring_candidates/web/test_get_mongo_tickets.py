# pylint: disable=redefined-outer-name

import pytest

from test_hiring_candidates import conftest


ROUTE = '/v1/infranaim-mongo/tickets'


@pytest.mark.usefixtures('fill_initial_data')
@pytest.mark.parametrize(
    'request_name',
    ['default', 'wrong_params', 'empty', 'fallback_default_settings'],
)
@conftest.main_configuration
async def test_get_mongo_tickets(
        taxi_hiring_candidates_web, load_json, request_name,
):
    async def make_request(params, consumer, code):
        response = await taxi_hiring_candidates_web.get(
            ROUTE, params=params, headers={'X-Consumer-Id': consumer},
        )
        assert response.status == code
        return response

    request = load_json('requests.json')[request_name]

    response = await make_request(
        params=request['params'],
        code=request['code'],
        consumer=request['consumer'],
    )
    body = await response.json()
    if request_name == 'empty':
        assert body['tickets'] == []
        return
    if request['code'] != 200:
        return

    assert body['tickets']
    if request_name == 'fallback_default_settings':
        return
    for ticket in body['tickets']:
        source_park_db_id = next(
            (
                field_obj['value']
                for field_obj in ticket['fields']
                if field_obj['name'] == 'source_park_db_id'
            ),
            None,
        )
        assert source_park_db_id == request['params']['source_park_db_id']
