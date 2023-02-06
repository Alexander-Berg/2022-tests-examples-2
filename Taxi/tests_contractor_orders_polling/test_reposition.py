import pytest

from tests_contractor_orders_polling import utils


@pytest.mark.parametrize(
    (),
    (
        pytest.param(
            marks=pytest.mark.config(
                REPOSITION_IN_POLLING_ORDER=True, REPOSITION_ENABLED=False,
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(REPOSITION_IN_POLLING_ORDER=False),
        ),
        pytest.param(
            marks=pytest.mark.config(
                REPOSITION_IN_POLLING_ORDER=True,
                TAXIMETER_VERSION_SETTINGS_BY_BUILD={
                    '__default__': {
                        'feature_support': {
                            'reposition_v2_in_polling_order': '99.99',
                        },
                    },
                },
            ),
        ),
    ),
)
async def test_reposition_disabled(taxi_contractor_orders_polling, mockserver):
    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL, headers=utils.HEADERS,
    )

    assert response.status_code == 200
    data = response.json()
    assert data['reposition_modes_etag'] == '<disabled>'
    assert 'reposition_state_etag' not in data
    assert 'reposition_modes' not in data
    assert 'reposition_state' not in data


@pytest.mark.config(
    REPOSITION_IN_POLLING_ORDER=True,
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {'reposition_v2_in_polling_order': '9.07'},
        },
    },
)
async def test_reposition_failed(taxi_contractor_orders_polling, mockserver):
    @mockserver.handler('/reposition/v2/reposition', prefix=True)
    def _mock_reposition(request):
        return mockserver.make_response(json={}, status=500)

    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL, headers=utils.HEADERS,
    )

    assert response.status_code == 200
    data = response.json()
    assert 'reposition_state_etag' not in data
    assert 'reposition_modes_etag' not in data
    assert 'reposition_offered_modes_etag' not in data
    assert 'reposition_modes' not in data
    assert 'reposition_state' not in data
    assert 'reposition_offered_modes' not in data

    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        headers=utils.HEADERS,
        params={
            'reposition_state_etag': '1',
            'reposition_modes_etag': '2',
            'reposition_offered_modes_etag': '3',
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data['reposition_state_etag'] == '1'
    assert data['reposition_modes_etag'] == '2'
    assert data['reposition_offered_modes_etag'] == '3'
    assert 'reposition_modes' not in data
    assert 'reposition_state' not in data
    assert 'reposition_offered_modes' not in data


@pytest.mark.config(
    REPOSITION_IN_POLLING_ORDER=True,
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {'reposition_v2_in_polling_order': '9.07'},
        },
    },
)
@pytest.mark.parametrize(
    'modes_etag,state_etag,offered_modes_etag',
    [
        ('modes-etag', 'state-etag', 'offered-modes-etag'),
        ('modes-etag', False, False),
        (False, 'state-etag', False),
        (False, False, 'offered-modes-etag'),
        (False, False, False),
    ],
)
@pytest.mark.parametrize(
    'modes_ok,state_ok,offered_modes_ok',
    [(True, True, True), (True, False, False)],
)
@pytest.mark.parametrize('dry_run', [True, False])
@pytest.mark.parametrize('switch_enabled', [False, True])
async def test_reposition_v2_200(
        taxi_contractor_orders_polling,
        experiments3,
        dry_run,
        switch_enabled,
        mockserver,
        modes_etag,
        modes_ok,
        state_etag,
        state_ok,
        offered_modes_etag,
        offered_modes_ok,
):
    @mockserver.handler('/reposition/v2/reposition/user_modes')
    def _mock_user_modes(request):
        if modes_etag:
            assert request.headers['If-None-Match'] == modes_etag
        else:
            assert 'If-None-Match' not in request.headers

        response = {'reposition': 'user_modes'}
        headers = {}
        if modes_ok:
            headers = {'ETag': 'ans-modes-etag'}

        return mockserver.make_response(
            json=response, status=200 if modes_ok else 500, headers=headers,
        )

    @mockserver.handler('/reposition/v2/reposition/state')
    def _mock_state(request):
        if state_etag:
            assert request.headers['If-None-Match'] == state_etag
        else:
            assert 'If-None-Match' not in request.headers

        response = {'reposition': 'state'}
        headers = {}
        if state_ok:
            headers = {'ETag': 'ans-state-etag'}

        return mockserver.make_response(
            json=response, status=200 if state_ok else 500, headers=headers,
        )

    @mockserver.handler('/reposition/v2/reposition/offered_modes')
    def _mock_offered_modes(request):
        if offered_modes_etag:
            assert request.headers['If-None-Match'] == offered_modes_etag
        else:
            assert 'If-None-Match' not in request.headers

        response = {'reposition': 'offered_modes'}
        headers = {}
        if offered_modes_ok:
            headers = {'ETag': 'ans-offered-modes-etag'}

        return mockserver.make_response(
            json=response,
            status=200 if offered_modes_ok else 500,
            headers=headers,
        )

    @mockserver.handler(
        '/reposition-api/internal/reposition-api/v2/user_modes',
    )
    def _mock_reposition_api_user_modes(request):
        if modes_etag:
            assert request.headers['If-None-Match'] == modes_etag
        else:
            assert 'If-None-Match' not in request.headers

        response = {'reposition': 'user_modes'}
        headers = {}
        if modes_ok:
            headers = {'ETag': 'ans-modes-etag'}

        return mockserver.make_response(
            json=response, status=200 if modes_ok else 500, headers=headers,
        )

    @mockserver.handler('/reposition-api/internal/reposition-api/v2/state')
    def _mock_reposition_api_state(request):
        if state_etag:
            assert request.headers['If-None-Match'] == state_etag
        else:
            assert 'If-None-Match' not in request.headers

        response = {'reposition': 'state'}
        headers = {}
        if state_ok:
            headers = {'ETag': 'ans-state-etag'}

        return mockserver.make_response(
            json=response, status=200 if state_ok else 500, headers=headers,
        )

    @mockserver.handler(
        '/reposition-api/internal/reposition-api/v2/offered_modes',
    )
    def _mock_reposition_api_offered_modes(request):
        if offered_modes_etag:
            assert request.headers['If-None-Match'] == offered_modes_etag
        else:
            assert 'If-None-Match' not in request.headers

        response = {'reposition': 'offered_modes'}
        headers = {}
        if offered_modes_ok:
            headers = {'ETag': 'ans-offered-modes-etag'}

        return mockserver.make_response(
            json=response,
            status=200 if offered_modes_ok else 500,
            headers=headers,
        )

    experiments3.add_experiment(
        name='reposition_switch_to_reposition_api',
        match={'enabled': True, 'predicate': {'type': 'true'}},
        consumers=['contractor-orders-polling/reposition-api'],
        clauses=[],
        default_value={
            'dry_run': (
                ['state', 'user_modes', 'offered_modes'] if dry_run else []
            ),
            'switch_enabled': (
                ['state', 'user_modes', 'offered_modes']
                if switch_enabled
                else []
            ),
        },
    )

    params = {}

    if modes_etag:
        params.update({'reposition_modes_etag': modes_etag})

    if state_etag:
        params.update({'reposition_state_etag': state_etag})

    if offered_modes_etag:
        params.update({'reposition_offered_modes_etag': offered_modes_etag})

    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL, headers=utils.HEADERS, params=params,
    )

    if switch_enabled:
        assert _mock_reposition_api_offered_modes.times_called == 1
        assert _mock_reposition_api_state.times_called == 1
        assert _mock_reposition_api_user_modes.times_called == 1

        assert _mock_offered_modes.times_called == 0
        assert _mock_state.times_called == 0
        assert _mock_user_modes.times_called == 0
    elif dry_run:
        assert _mock_reposition_api_offered_modes.times_called == 1
        assert _mock_reposition_api_state.times_called == 1
        assert _mock_reposition_api_user_modes.times_called == 1

        assert _mock_offered_modes.times_called == 1 if offered_modes_ok else 3
        assert _mock_state.times_called == 1 if state_ok else 3
        assert _mock_user_modes.times_called == 1 if modes_ok else 3
    else:
        assert _mock_reposition_api_offered_modes.times_called == 0
        assert _mock_reposition_api_state.times_called == 0
        assert _mock_reposition_api_user_modes.times_called == 0

        assert _mock_offered_modes.times_called == 1 if offered_modes_ok else 3
        assert _mock_state.times_called == 1 if state_ok else 3
        assert _mock_user_modes.times_called == 1 if modes_ok else 3

    assert response.status_code == 200
    data = response.json()

    if modes_etag and not (modes_ok and offered_modes_ok and state_ok):
        assert data['reposition_modes_etag'] == 'modes-etag'
        assert 'reposition_modes' not in data
    elif modes_ok and offered_modes_ok and state_ok:
        assert data['reposition_modes_etag'] == 'ans-modes-etag'
        assert data['reposition_modes'] == {'reposition': 'user_modes'}
    else:
        assert 'reposition_modes_etag' not in data
        assert 'reposition_modes' not in data

    if state_etag and not (modes_ok and offered_modes_ok and state_ok):
        assert data['reposition_state_etag'] == 'state-etag'
        assert 'reposition_state' not in data
    elif modes_ok and offered_modes_ok and state_ok:
        assert data['reposition_state_etag'] == 'ans-state-etag'
        assert data['reposition_state'] == {'reposition': 'state'}
    else:
        assert 'reposition_state_etag' not in data
        assert 'reposition_state' not in data

    if offered_modes_etag and not (modes_ok and offered_modes_ok and state_ok):
        assert data['reposition_offered_modes_etag'] == 'offered-modes-etag'
        assert 'reposition_offered_modes' not in data
    elif modes_ok and offered_modes_ok and state_ok:
        assert (
            data['reposition_offered_modes_etag'] == 'ans-offered-modes-etag'
        )
        assert data['reposition_offered_modes'] == {
            'reposition': 'offered_modes',
        }
    else:
        assert 'reposition_offered_modes_etag' not in data
        assert 'reposition_offered_modes' not in data


@pytest.mark.config(
    REPOSITION_IN_POLLING_ORDER=True,
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {'reposition_v2_in_polling_order': '9.07'},
        },
    },
)
async def test_reposition_304(taxi_contractor_orders_polling, mockserver):
    @mockserver.handler('/reposition/v2/reposition', prefix=True)
    def _mock_reposition(request):
        return mockserver.make_response(json={}, status=304)

    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL,
        headers=utils.HEADERS,
        params={
            'reposition_state_etag': 'incoming_state_tag',
            'reposition_modes_etag': 'incoming_modes_tag',
            'reposition_offered_modes_etag': 'incoming_offered_modes_tag',
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data['reposition_state_etag'] == 'incoming_state_tag'
    assert data['reposition_modes_etag'] == 'incoming_modes_tag'
    assert (
        data['reposition_offered_modes_etag'] == 'incoming_offered_modes_tag'
    )
    assert 'reposition_modes' not in data
    assert 'reposition_state' not in data
    assert 'reposition_offered_modes' not in data
