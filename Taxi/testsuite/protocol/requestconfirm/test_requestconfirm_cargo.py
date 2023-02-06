import datetime

import pytest


@pytest.mark.parametrize(
    'target_service',
    [
        pytest.param('cargo-claims', id='target_service_cargo_claims'),
        pytest.param(
            'api-proxy',
            marks=(pytest.mark.config(CARGO_PROTOCOL_API_PROXY=True)),
            id='target_service_api_proxy',
        ),
    ],
)
@pytest.mark.parametrize(
    'action_disabled, reason, response_code',
    [(False, None, 200), (True, 'Some reason', 406)],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.driver_experiments('dont_trust_position')
@pytest.mark.driver_experiments('waiting_coord_providers_check')
@pytest.mark.fixture_now(datetime.timedelta(minutes=5))
def test_requestconfirm_cancel_cargo(
        taxi_protocol,
        mockserver,
        db,
        action_disabled,
        reason,
        response_code,
        target_service: str,
):
    @mockserver.json_handler(f'/{target_service}/v1/claims/driver-changes')
    def _mock_cargo_claims(request):
        response = {'action_disabled': action_disabled}
        if reason:
            response['reason'] = reason
        return response

    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {
            '$set': {
                'order.request.cargo_ref_id': (
                    'f7793a14a2e94cd78dbdb2831476aafc'
                ),
                'order.taxi_status': 'driving',
            },
        },
    )

    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
        'latitude': '55.733410768',
        'longitude': '37.589179973',
        'status': 'cancelled',
        'db_id': 'some park_id',
    }
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'

    response = taxi_protocol.post(
        '1.x/requestconfirm?clid=999012&apikey=' + apikey, request_params,
    )

    assert response.status_code == response_code
    assert _mock_cargo_claims.times_called == 1
    if response_code != 200:
        assert response.json() == {'error': {'text': reason}}


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.fixture_now(datetime.timedelta(minutes=5))
@pytest.mark.parametrize(
    'driver_changes,error_expected',
    [
        pytest.param(
            {'action_disabled': False},
            None,
            marks=pytest.mark.config(
                CARGO_REQUESTCONFIRM_VALIDATION_DISABLED=True,
            ),
        ),
        pytest.param(
            {'action_disabled': False},
            {
                'error': {
                    'text': 'Distance checks failed for destination point',
                },
            },
            marks=pytest.mark.config(
                CARGO_REQUESTCONFIRM_VALIDATION_DISABLED=False,
            ),
        ),
        pytest.param(
            {'action_disabled': True, 'reason': 'testsuite'},
            {'error': {'text': 'testsuite'}},
            marks=pytest.mark.config(
                CARGO_REQUESTCONFIRM_VALIDATION_DISABLED=False,
            ),
        ),
    ],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='requestconfirm_complete_status_checks',
    consumers=['protocol/requestconfirm'],
    clauses=[
        {
            'value': {
                'max_distance_auto': 100,
                'max_distance_pedestrian': 100,
                'check_all_coord_providers': False,
                'allow_no_position': True,
                'use_captcha': False,
            },
            'predicate': {'type': 'true'},
        },
    ],
)
def test_complete(
        taxi_protocol,
        mockserver,
        db,
        load_binary,
        driver_changes,
        error_expected,
):
    @mockserver.handler('/maps-router/route_jams/')
    def route_jams(request):
        return mockserver.make_response('Not implemented', 500)

    @mockserver.handler('/router-yamaps-masstransit/pedestrian/route')
    def yarouter_dummy(request):
        return mockserver.make_response('Not implemented', 500)

    @mockserver.json_handler(f'/cargo-claims/v1/claims/driver-changes')
    def _mock_cargo_claims(request):
        return driver_changes

    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {
            '$set': {
                'order.request.cargo_ref_id': (
                    'f7793a14a2e94cd78dbdb2831476aafc'
                ),
                'order.taxi_status': 'driving',
            },
        },
    )

    request_params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'uuid': 'a5709ce56c2740d9a536650f5390de0b',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'status_change_time': '20161215T083000',
        'time': '20161215T083000',
        'avg_speed': '0',
        'direction': '0',
        'latitude': '50.733410768',
        'longitude': '30.589179973',
        'status': 'complete',
        'db_id': 'some park_id',
    }
    apikey = 'd19a9b3b59424881b57adf5b0f367a2c'

    response = taxi_protocol.post(
        '1.x/requestconfirm?clid=999012&apikey=' + apikey, request_params,
    )

    if not error_expected:
        assert response.status_code == 200
    else:
        assert response.status_code == 406
        assert response.json() == error_expected
