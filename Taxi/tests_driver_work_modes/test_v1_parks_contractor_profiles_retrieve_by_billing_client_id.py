import pytest


ENDPOINT_URL = 'v1/parks/contractor-profiles/retrieve-by-billing-client-id'
TAG = 'retrieve_by_billing_client_id'
METRIC_NAMES = [
    'clids_not_found',
    'parks_not_found',
    'only_regular_parks_found',
    'several_parks_including_individual_found',
    'several_active_profiles_in_park_found',
    'no_active_profiles_in_park_found',
]

BILLING_CLIENT_ID = '123'
NOW = '2021-02-19T22:46:00+00:00'

REQUEST_BODY = {'billing_client_id': BILLING_CLIENT_ID, 'actual_at': NOW}
RESPONSE_BODY = {'park_id': 'park1', 'contractor_profile_id': 'driver1'}


def _make_response_404(code):
    return {'code': code, 'message': code}


async def _make_request(
        taxi_driver_work_modes,
        mock_required_services,
        fleet_parks_has_calls=True,
        driver_profiles_has_calls=True,
):
    response = await taxi_driver_work_modes.post(
        ENDPOINT_URL, json=REQUEST_BODY,
    )
    assert mock_required_services.has_mock_parks_replica_calls
    assert (
        mock_required_services.has_mock_fleet_parks_calls
        == fleet_parks_has_calls
    )
    assert (
        mock_required_services.has_mock_driver_profiles_calls
        == driver_profiles_has_calls
    )
    return response


async def _check_metrics(taxi_driver_work_modes_monitor, metric=None):
    metrics = await taxi_driver_work_modes_monitor.get_metric(TAG)
    assert metrics == ({metric: 1} if metric else {})


@pytest.mark.parametrize(
    'clids, parks_params, driver_params',
    [
        (
            ['clid1'],
            [{'fleet_type': 'yandex'}],
            [{'driver_id': 'driver1', 'status': 'working'}],
        ),
        (
            ['clid1', 'clid2'],
            [
                {'park_id': 'park1'},
                {'park_id': 'park2', 'clid': 'clid2', 'is_active': False},
            ],
            [{'driver_id': 'driver1', 'status': 'fired'}],
        ),
        (
            ['clid1'],
            [{'park_id': 'park1'}],
            [
                {'driver_id': 'driver1', 'status': 'working'},
                {'driver_id': 'driver2', 'status': 'not_working'},
            ],
        ),
    ],
)
async def test_ok(
        taxi_driver_work_modes,
        taxi_driver_work_modes_monitor,
        mock_required_services,
        clids,
        parks_params,
        driver_params,
):
    await taxi_driver_work_modes.tests_control(reset_metrics=True)
    mock_required_services.set_data(
        clids=clids, parks_params=parks_params, driver_params=driver_params,
    )

    response = await _make_request(
        taxi_driver_work_modes, mock_required_services,
    )

    await _check_metrics(taxi_driver_work_modes_monitor)

    assert response.status_code == 200, response.text
    assert response.json() == RESPONSE_BODY


async def test_clids_not_found(
        taxi_driver_work_modes,
        taxi_driver_work_modes_monitor,
        mock_required_services,
):
    code = 'clids_not_found'
    await taxi_driver_work_modes.tests_control(reset_metrics=True)
    response = await _make_request(
        taxi_driver_work_modes,
        mock_required_services,
        fleet_parks_has_calls=False,
        driver_profiles_has_calls=False,
    )

    await _check_metrics(taxi_driver_work_modes_monitor, code)

    assert response.status_code == 404, response.text
    assert response.json() == _make_response_404(code)


@pytest.mark.parametrize(
    'clids, parks_params',
    [
        (['clid1'], []),
        (
            ['clid1', 'clid2'],
            [
                {'is_active': False},
                {'park_id': 'park2', 'clid': 'clid2', 'is_active': False},
            ],
        ),
    ],
)
async def test_parks_not_found(
        taxi_driver_work_modes,
        taxi_driver_work_modes_monitor,
        mock_required_services,
        clids,
        parks_params,
):
    code = 'parks_not_found'
    mock_required_services.set_data(clids=clids, parks_params=parks_params)
    await taxi_driver_work_modes.tests_control(reset_metrics=True)
    response = await _make_request(
        taxi_driver_work_modes,
        mock_required_services,
        driver_profiles_has_calls=False,
    )

    await _check_metrics(taxi_driver_work_modes_monitor, code)

    assert response.status_code == 404, response.text
    assert response.json() == _make_response_404(code)


@pytest.mark.parametrize(
    'clids, parks_params',
    [
        (
            ['clid1', 'clid2'],
            [{'park_id': 'park1'}, {'park_id': 'park2', 'clid': 'clid2'}],
        ),
        (
            ['clid1'],
            [
                {'driver_partner_source': None},
                {'park_id': 'park2'},
                {'park_id': 'park3', 'clid': 'clid2'},
            ],
        ),
    ],
)
async def test_several_parks_including_individual_found(
        taxi_driver_work_modes,
        taxi_driver_work_modes_monitor,
        mock_required_services,
        clids,
        parks_params,
):
    code = 'several_parks_including_individual_found'
    mock_required_services.set_data(clids=clids, parks_params=parks_params)
    await taxi_driver_work_modes.tests_control(reset_metrics=True)
    response = await _make_request(
        taxi_driver_work_modes,
        mock_required_services,
        driver_profiles_has_calls=False,
    )

    await _check_metrics(taxi_driver_work_modes_monitor, code)

    assert response.status_code == 404, response.text
    assert response.json() == _make_response_404(code)


@pytest.mark.parametrize(
    'clids, parks_params',
    [
        (['clid1'], [{'driver_partner_source': None}]),
        (
            ['clid1', 'clid2'],
            [
                {'driver_partner_source': None},
                {
                    'park_id': 'park2',
                    'clid': 'clid2',
                    'driver_partner_source': None,
                },
            ],
        ),
    ],
)
async def test_only_regular_parks_found(
        taxi_driver_work_modes,
        taxi_driver_work_modes_monitor,
        mock_required_services,
        clids,
        parks_params,
):
    code = 'only_regular_parks_found'
    mock_required_services.set_data(clids=clids, parks_params=parks_params)
    await taxi_driver_work_modes.tests_control(reset_metrics=True)
    response = await _make_request(
        taxi_driver_work_modes,
        mock_required_services,
        driver_profiles_has_calls=False,
    )

    await _check_metrics(taxi_driver_work_modes_monitor, code)

    assert response.status_code == 404, response.text
    assert response.json() == _make_response_404(code)


@pytest.mark.parametrize(
    'driver_params',
    [
        [],
        [
            {'driver_id': 'driver1', 'status': 'not_working'},
            {'driver_id': 'driver2', 'status': 'not_working'},
        ],
    ],
)
async def test_no_active_profiles_in_park_found(
        taxi_driver_work_modes,
        taxi_driver_work_modes_monitor,
        mock_required_services,
        driver_params,
):
    code = 'no_active_profiles_in_park_found'
    mock_required_services.set_data(
        clids=['clid1'],
        parks_params=[{'park_id': 'park1'}],
        driver_params=driver_params,
    )

    await taxi_driver_work_modes.tests_control(reset_metrics=True)
    response = await _make_request(
        taxi_driver_work_modes, mock_required_services,
    )

    await _check_metrics(taxi_driver_work_modes_monitor, code)

    assert response.status_code == 404, response.text
    assert response.json() == _make_response_404(code)


async def test_several_active_profiles_in_park_found(
        taxi_driver_work_modes,
        taxi_driver_work_modes_monitor,
        mock_required_services,
):
    code = 'several_active_profiles_in_park_found'
    driver_params = [
        {'driver_id': 'driver1', 'status': 'working'},
        {'driver_id': 'driver2', 'status': 'fired'},
    ]
    mock_required_services.set_data(
        clids=['clid1'],
        parks_params=[{'park_id': 'park1'}],
        driver_params=driver_params,
    )

    await taxi_driver_work_modes.tests_control(reset_metrics=True)
    response = await _make_request(
        taxi_driver_work_modes, mock_required_services,
    )

    await _check_metrics(taxi_driver_work_modes_monitor, code)

    assert response.status_code == 404, response.text
    assert response.json() == _make_response_404(code)
