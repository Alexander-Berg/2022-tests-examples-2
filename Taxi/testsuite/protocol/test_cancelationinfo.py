import datetime

import pytest


@pytest.mark.parametrize(
    'params, expected_status',
    [
        ({'origin': 'dispatch'}, 200),
        ({'latitude': '55.733410768', 'longitude': '37.589179973'}, 200),
        ({}, 400),
    ],
)
@pytest.mark.config(ENABLE_PAID_CANCEL_TAXIMETER=False)
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_reason_disabled(
        taxi_protocol,
        experiments3,
        load_json,
        recalc_order,
        params,
        expected_status,
):
    request_params = {
        'clid': '999012',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
    }
    request_params.update(params)

    response = taxi_protocol.get('1.x/cancelationinfo', params=request_params)
    assert response.status_code == expected_status

    if expected_status == 200:
        data = response.json()
        assert data == {'type': 'free', 'reason': 'disabled'}

    assert not recalc_order.calls


@pytest.mark.parametrize(
    'params, expected_result',
    [
        (
            {'origin': 'dispatch'},
            {
                'type': 'free',
                'reason': 'time',
                'paid_since': '2016-12-15T08:38:29+0000',
                'max_distance': 300,
                'min_waiting_time': 600,
            },
        ),
        (
            {'latitude': '55.733448', 'longitude': '37.587476'},
            {
                'type': 'free',
                'reason': 'time',
                'paid_since': '2016-12-15T08:38:29+0000',
                'max_distance': 300,
                'min_waiting_time': 600,
                'distance': 106,
            },
        ),
        (
            {'latitude': '55.733917', 'longitude': '37.589879'},
            {
                'type': 'free',
                'reason': 'time',
                'paid_since': '2016-12-15T08:38:29+0000',
                'max_distance': 300,
                'min_waiting_time': 600,
                'distance': 71,
            },
        ),
        (
            {'latitude': '55.734948', 'longitude': '37.557476'},
            {
                'type': 'free',
                'reason': 'time',
                'paid_since': '2016-12-15T08:38:29+0000',
                'max_distance': 300,
                'min_waiting_time': 600,
                'distance': 1992,
            },
        ),
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.fixture_now(datetime.timedelta(minutes=5))
def test_before_min_waiting(
        taxi_protocol,
        experiments3,
        load_json,
        recalc_order,
        params,
        expected_result,
):
    request_params = {
        'clid': '999012',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
    }
    request_params.update(params)

    response = taxi_protocol.get('1.x/cancelationinfo', params=request_params)
    assert response.status_code == 200

    data = response.json()
    assert data == expected_result
    assert isinstance(data['max_distance'], int)

    assert recalc_order.calls


@pytest.mark.parametrize(
    'params, expected_result',
    [
        (
            {'origin': 'dispatch'},
            {
                'type': 'paid',
                'max_distance': 300,
                'min_waiting_time': 600,
                'cost': 126.0,
            },
        ),
        (
            {'latitude': '55.733448', 'longitude': '37.587476'},
            {
                'type': 'paid',
                'max_distance': 300,
                'min_waiting_time': 600,
                'cost': 126.0,
            },
        ),
        (
            {'latitude': '55.734948', 'longitude': '37.557476'},
            {
                'type': 'free',
                'reason': 'distance',
                'paid_since': '2016-12-15T08:28:29+0000',
                'distance': 1992,
                'max_distance': 300,
                'min_waiting_time': 600,
            },
        ),
    ],
)
@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.fixture_now(datetime.timedelta(minutes=15))
@pytest.mark.parametrize(
    'new_pricing_error_code',
    [400, 500, None],
    ids=['new_pricing_400', 'new_pricing_500', 'new_pricing_ok'],
)
def test_after_min_waiting(
        taxi_protocol,
        experiments3,
        load_json,
        recalc_order,
        new_pricing_error_code,
        params,
        expected_result,
):
    new_pricing_cost = 127.0 if new_pricing_error_code else 128.0
    recalc_order.set_recalc_result(new_pricing_cost, new_pricing_cost)

    if expected_result['type'] == 'paid':
        expected_result['cost'] = new_pricing_cost

    if new_pricing_error_code:
        recalc_order.set_error_code(new_pricing_error_code)

    request_params = {
        'clid': '999012',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
    }
    request_params.update(params)

    response = taxi_protocol.get('1.x/cancelationinfo', params=request_params)
    assert response.status_code == 200

    data = response.json()
    assert data == expected_result
    assert isinstance(data['max_distance'], int)

    assert recalc_order.calls
