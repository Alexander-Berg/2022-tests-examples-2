import pytest

from . import utils


@pytest.mark.parametrize(
    'request_obj, expected_response, expected_maps_calls, expected_uapi_calls',
    [
        ({'phone_id': '123456789abcdef123456789'}, 'response_1.json', 0, 0),
        ({'phone_id': '1dcf5804abae14bb0d31d02d'}, 'response_2.json', 2, 0),
        ({'phone': '+79001234567'}, 'response_1.json', 0, 1),
    ],
)
async def test_admin_list(
        taxi_routehistory,
        pgsql,
        load_json,
        request_obj,
        expected_response,
        expected_maps_calls,
        expected_uapi_calls,
        mockserver,
        yamaps,
):
    utils.fill_db(pgsql['routehistory'].cursor(), load_json('db.json'))
    utils.fill_db(pgsql['routehistory_ph'].cursor(), load_json('db_ph.json'))

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        geo_objects = load_json('yamaps_geo_objects.json')
        if 'uri' in request.args:
            for addr in geo_objects:
                if addr['uri'] == request.args['uri']:
                    return [addr]
        return []

    @mockserver.json_handler('/user-api/user_phones/by_number/retrieve')
    def _uapi_mock(request):
        return load_json('uapi_response.json')

    response = await taxi_routehistory.post(
        'routehistory/admin/list', request_obj, headers={},
    )

    assert response.json() == load_json(expected_response)
    assert yamaps.times_called() == expected_maps_calls
    assert _uapi_mock.times_called == expected_uapi_calls


@pytest.mark.config(ROUTEHISTORY_ADMIN_LIST_LIMIT=2)
@pytest.mark.parametrize(
    'request_obj, expected_orders',
    [
        (
            {'phone_id': '1dcf5804abae14bb0d31d02d'},
            [
                '11111111000000000000000000000003',
                '11111111000000000000000000000002',
            ],
        ),
        (
            {
                'phone_id': '1dcf5804abae14bb0d31d02d',
                'older_than': '2019-04-01T00:00:00+0000',
            },
            [
                '11111111000000000000000000000001',
                '11111111000000000000000000000004',
            ],
        ),
        (
            {
                'phone_id': '1dcf5804abae14bb0d31d02d',
                'older_than': '2014-03-01T00:00:00+0000',
            },
            [],
        ),
    ],
)
async def test_admin_list_older(
        taxi_routehistory,
        pgsql,
        load_json,
        request_obj,
        expected_orders,
        yamaps,
):
    utils.fill_db(pgsql['routehistory'].cursor(), load_json('db.json'))
    utils.fill_db(pgsql['routehistory_ph'].cursor(), load_json('db_ph.json'))

    response = await taxi_routehistory.post(
        'routehistory/admin/list', request_obj, headers={},
    )
    response_orders = [x['order_id'] for x in response.json()['results']]
    assert response_orders == expected_orders
