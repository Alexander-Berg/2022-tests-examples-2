import pytest

from tests_driver_work_modes import utils


ENDPOINT_URL = 'v1/parks/driver-profiles/retrieve-by-clid'
TAG = 'retrieve_by_clid'
METRIC_NAMES = [
    'park_not_found',
    'several_parks_by_clid',
    'invalid_driver_partner_source',
    'drivers_not_found',
]


@pytest.mark.parametrize(
    'request_params, fleet_parks_response,'
    'driver_profiles_list_response,handler_response',
    [
        (
            {'at': '2021-02-19T22:46:00+00:00', 'clid': 'clid1'},
            {'parks': [utils.NICE_PARK]},
            {
                'driver_profiles': [
                    {'driver_profile': {'id': 'driver1'}},
                    {'driver_profile': {'id': 'driver2'}},
                ],
                'parks': [{'id': 'park1', 'country_id': 'rus', 'tz': 3}],
                'offset': 0,
                'total': 1,
                'limit': 1,
            },
            {
                'at': '2021-02-19T22:46:00+00:00',
                'clid': 'clid1',
                'park_id': 'park1',
                'driver_profile_id': 'driver2',
            },
        ),
        (
            {'at': '2016-07-19T22:46:00+00:00', 'clid': 'clid1'},
            {'parks': [utils.NICE_PARK]},
            {
                'driver_profiles': [
                    {'driver_profile': {'id': 'driver1'}},
                    {'driver_profile': {'id': 'driver2'}},
                    {'driver_profile': {'id': 'driver3'}},
                ],
                'parks': [{'id': 'park1', 'country_id': 'rus', 'tz': 3}],
                'offset': 0,
                'total': 1,
                'limit': 1,
            },
            {
                'at': '2016-07-19T22:46:00+00:00',
                'clid': 'clid1',
                'park_id': 'park1',
                'driver_profile_id': 'driver3',
            },
        ),
        (
            {'at': '2022-12-19T22:46:00+00:00', 'clid': 'clid1'},
            {'parks': [utils.NICE_PARK]},
            {
                'driver_profiles': [
                    {'driver_profile': {'id': 'driver1'}},
                    {'driver_profile': {'id': 'driver2'}},
                    {'driver_profile': {'id': 'driver3'}},
                    {'driver_profile': {'id': 'driver4'}},
                ],
                'parks': [{'id': 'park1', 'country_id': 'rus', 'tz': 3}],
                'offset': 0,
                'total': 1,
                'limit': 1,
            },
            {
                'at': '2022-12-19T22:46:00+00:00',
                'clid': 'clid1',
                'park_id': 'park1',
                'driver_profile_id': 'driver4',
            },
        ),
        (
            {'at': '2022-12-19T22:46:00+00:00', 'clid': 'clid1'},
            {
                'parks': [
                    utils.NICE_PARK,
                    utils.make_park(park_id='park2', is_active=False),
                ],
            },
            {
                'driver_profiles': [
                    {'driver_profile': {'id': 'driver1'}},
                    {'driver_profile': {'id': 'driver2'}},
                    {'driver_profile': {'id': 'driver3'}},
                    {'driver_profile': {'id': 'driver4'}},
                ],
                'parks': [{'id': 'park1', 'country_id': 'rus', 'tz': 3}],
                'offset': 0,
                'total': 1,
                'limit': 1,
            },
            {
                'at': '2022-12-19T22:46:00+00:00',
                'clid': 'clid1',
                'park_id': 'park1',
                'driver_profile_id': 'driver4',
            },
        ),
    ],
)
async def test_ok(
        taxi_driver_work_modes,
        taxi_driver_work_modes_monitor,
        mockserver,
        driver_orders,
        request_params,
        fleet_parks_response,
        driver_profiles_list_response,
        handler_response,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list-by-clids')
    def mock_fleet_parks(request):
        assert request.json['query']['park']['clids'] == ['clid1']

        return fleet_parks_response

    @mockserver.json_handler('/parks/driver-profiles/list')
    def mock_driver_profiles_list(request):
        assert request.json['query']['park']['id'] == 'park1'
        assert request.json['limit'] > 0

        return driver_profiles_list_response

    response = await taxi_driver_work_modes.get(
        ENDPOINT_URL, params=request_params,
    )

    assert mock_driver_profiles_list.times_called == 1
    assert mock_fleet_parks.times_called == 1
    assert driver_orders.times_called == len(
        driver_profiles_list_response['driver_profiles'],
    )

    metrics = await taxi_driver_work_modes_monitor.get_metrics()
    assert not metrics.get(TAG)

    assert response.status_code == 200, response.text

    assert response.json() == handler_response


@pytest.mark.parametrize(
    'fleet_parks_response,handler_code,handler_response',
    [
        (
            {'parks': []},
            404,
            {'code': 'park_not_found', 'message': 'Park not found'},
        ),
        (
            {'parks': [utils.NICE_PARK, utils.make_park(park_id='park2')]},
            404,
            {
                'code': 'several_parks_by_clid',
                'message': 'Several parks were found by request clid',
            },
        ),
        (
            {
                'parks': [
                    utils.make_park(
                        park_id='park2', driver_partner_source=None,
                    ),
                ],
            },
            404,
            {
                'code': 'invalid_driver_partner_source',
                'message': 'Park doesnt have driver partner source',
            },
        ),
    ],
)
async def test_bad_park(
        taxi_driver_work_modes,
        taxi_driver_work_modes_monitor,
        mockserver,
        fleet_parks_response,
        handler_code,
        handler_response,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list-by-clids')
    def mock_fleet_parks(request):
        return fleet_parks_response

    @mockserver.json_handler('/parks/driver-profiles/list')
    def mock_driver_profiles_list(request):
        return {}

    @mockserver.json_handler('/driver-orders/v1/parks/orders/list')
    def mock_parks_orders_list(request):
        return {}

    await taxi_driver_work_modes.tests_control(reset_metrics=True)
    response = await taxi_driver_work_modes.get(
        ENDPOINT_URL,
        params={'at': '2021-02-19T22:46:00+00:00', 'clid': 'clid1'},
    )

    assert mock_driver_profiles_list.times_called == 0
    assert mock_fleet_parks.times_called == 1
    assert mock_parks_orders_list.times_called == 0

    metrics = await taxi_driver_work_modes_monitor.get_metrics(TAG)
    for metric_name in METRIC_NAMES:
        if metric_name == handler_response.get('code'):
            assert metrics.get(TAG, {}).get(metric_name) == 1
        else:
            assert not metrics.get(TAG, {}).get(metric_name)

    assert response.status_code == handler_code, response.text

    assert response.json() == handler_response


@pytest.mark.parametrize(
    'drivers_list_response,handler_code,handler_response',
    [
        (
            {
                'driver_profiles': [],
                'parks': [{'id': 'park1', 'country_id': 'rus', 'tz': 3}],
                'offset': 0,
                'total': 1,
                'limit': 1,
            },
            404,
            {
                'code': 'drivers_not_found',
                'message': 'Park has no any drivers',
            },
        ),
    ],
)
async def test_bad_drivers(
        taxi_driver_work_modes,
        taxi_driver_work_modes_monitor,
        mockserver,
        drivers_list_response,
        handler_code,
        handler_response,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list-by-clids')
    def mock_fleet_parks(request):
        assert request.json['query']['park']['clids'] == ['clid1']

        return {'parks': [utils.NICE_PARK]}

    @mockserver.json_handler('/parks/driver-profiles/list')
    def mock_driver_profiles_list(request):
        assert request.json['limit'] > 0
        return drivers_list_response

    @mockserver.json_handler('/driver-orders/v1/parks/orders/list')
    def mock_parks_orders_list(request):
        return {}

    await taxi_driver_work_modes.tests_control(reset_metrics=True)
    response = await taxi_driver_work_modes.get(
        ENDPOINT_URL,
        params={'at': '2021-02-19T22:46:00+00:00', 'clid': 'clid1'},
    )

    assert mock_driver_profiles_list.times_called == 1
    assert mock_fleet_parks.times_called == 1
    assert mock_parks_orders_list.times_called == 0

    metrics = await taxi_driver_work_modes_monitor.get_metrics(TAG)
    for metric_name in METRIC_NAMES:
        if metric_name == handler_response.get('code'):
            assert metrics.get(TAG, {}).get(metric_name) == 1
        else:
            assert not metrics.get(TAG, {}).get(metric_name)

    assert response.status_code == handler_code, response.text

    assert response.json() == handler_response


@pytest.mark.parametrize(
    'drivers_list_response,orders_list_response,'
    'handler_code,handler_response',
    [
        (
            {
                'driver_profiles': [
                    {'driver_profile': {'id': 'driver1'}},
                    {'driver_profile': {'id': 'driver2'}},
                ],
                'parks': [{'id': 'park1', 'country_id': 'rus', 'tz': 3}],
                'offset': 0,
                'total': 1,
                'limit': 1,
            },
            {'orders': [utils.RESULT_ORDERS[6]], 'limit': 1},
            500,
            {'code': '500', 'message': 'Internal Server Error'},
        ),
    ],
)
async def test_bad_driver_orders(
        taxi_driver_work_modes,
        mockserver,
        drivers_list_response,
        orders_list_response,
        handler_code,
        handler_response,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list-by-clids')
    def mock_fleet_parks(request):
        assert request.json['query']['park']['clids'] == ['clid1']

        return {'parks': [utils.NICE_PARK]}

    @mockserver.json_handler('/parks/driver-profiles/list')
    def mock_driver_profiles_list(request):
        assert request.json['limit'] > 0
        return drivers_list_response

    @mockserver.json_handler('/driver-orders/v1/parks/orders/list')
    def mock_parks_orders_list(request):
        return orders_list_response

    response = await taxi_driver_work_modes.get(
        ENDPOINT_URL,
        params={'at': '2021-02-19T22:46:00+00:00', 'clid': 'clid1'},
    )

    assert mock_driver_profiles_list.times_called == 1
    assert mock_fleet_parks.times_called == 1
    assert mock_parks_orders_list.times_called == len(
        drivers_list_response['driver_profiles'],
    )

    assert response.status_code == handler_code, response.text

    assert response.json() == handler_response
