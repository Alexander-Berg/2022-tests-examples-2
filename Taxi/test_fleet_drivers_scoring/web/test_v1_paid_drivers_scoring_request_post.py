import pytest

from testsuite.utils import matching

from test_fleet_drivers_scoring import utils as global_utils
from test_fleet_drivers_scoring.web import defaults
from test_fleet_drivers_scoring.web import utils


ENDPOINT = 'v1/paid/drivers/scoring/request'
HEADERS = {
    'X-Ya-User-Ticket': 'ut',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Login': 'ya-login',
    'X-Yandex-UID': 'ya-uid',
}


PAID_RATE_LIMIT_CONFIG1 = {
    'FLEET_DRIVERS_SCORING_PAID_RATE_LIMITS': {
        '__default__': {'day': 2},
        'clid1': {'day': 10, 'week': 30},
        'clid3': {'day': 4, 'week': 20},
    },
}


@pytest.mark.config(
    TVM_RULES=[{'src': 'fleet-drivers-scoring', 'dst': 'stq-agent'}],
    **defaults.RATE_LIMIT_CONFIG1,
    **PAID_RATE_LIMIT_CONFIG1,
    **defaults.SCORING_ENABLED_CONFIG1,
)
async def test_ok(
        taxi_fleet_drivers_scoring_web, _mock_fleet_parks, stq, pgsql,
):
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [defaults.RESPONSE_FLEET_PARKS1]}],
    )
    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers={
            **utils.TVM_HEADERS,
            **HEADERS,
            'X-Idempotency-Token': '100000000',
        },
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license1_pd'},
            },
            'offer': {
                'decision': {'can_buy': True},
                'price': {'amount': '10', 'currency': 'RUB'},
            },
        },
        params={'park_id': 'park1'},
    )

    assert _mock_fleet_parks.parks_list.times_called == 1

    assert response.status == 200, response.text
    response_json = await response.json()
    assert response_json == {'request_id': matching.uuid_string}
    request_id = response_json['request_id']

    all_checks = global_utils.fetch_all_checks(pgsql)
    assert len(all_checks) == 1
    all_checks[0].pop('created_at')
    all_checks[0].pop('updated_at')
    assert all_checks == [
        {
            'check_id': request_id,
            'idempotency_token': '100000000',
            'license_pd_id': 'extra_super_driver_license1_pd',
            'park_id': 'park1',
            'status': 'pending',
            'status_meta_info': None,
            'ratings_history_id': None,
            'is_ratings_history_calculated': False,
            'orders_statistics_id': None,
            'is_orders_statistics_calculated': False,
            'quality_metrics_id': None,
            'is_quality_metrics_calculated': False,
            'high_speed_driving_id': None,
            'is_high_speed_driving_calculated': False,
            'driving_style_id': None,
            'is_driving_style_calculated': False,
            'passenger_tags_id': None,
            'is_passenger_tags_calculated': False,
            'car_orders_history_id': None,
            'is_car_orders_history_calculated': False,
            'offer': {
                'decision': {'can_buy': True},
                'price': {'amount': '10', 'currency': 'RUB'},
            },
            'requested_by': {
                'uid': 'ya-uid',
                'provider': 'yandex',
                'remote_ip': None,
            },
            'billing_doc_id': None,
            'discount_type': None,
        },
    ]

    assert stq.fleet_drivers_scoring_checks.times_called == 1
    stq_task = stq.fleet_drivers_scoring_checks.next_call()
    assert stq_task['id'] == f'park1_{request_id}'
    stq_task['kwargs'].pop('log_extra')
    assert stq_task['kwargs'] == {'park_id': 'park1', 'check_id': request_id}

    day_rates = global_utils.fetch_rate_limit(
        pgsql=pgsql, clid='clid1', period='day', rate_type='paid',
    )
    assert len(day_rates) == 1
    assert day_rates[0]['rate_limit'] == 10

    week_rates = global_utils.fetch_rate_limit(
        pgsql=pgsql, clid='clid1', period='week', rate_type='paid',
    )
    assert len(week_rates) == 1
    assert week_rates[0]['rate_limit'] == 30


@pytest.mark.config(
    TVM_RULES=[{'src': 'fleet-drivers-scoring', 'dst': 'stq-agent'}],
    **PAID_RATE_LIMIT_CONFIG1,
    **defaults.SCORING_ENABLED_CONFIG2,
)
@pytest.mark.parametrize(
    'park_id, response_fleet_parks',
    [
        ('park1', defaults.RESPONSE_FLEET_PARKS1),
        ('park2', defaults.RESPONSE_FLEET_PARKS2),
    ],
)
async def test_scoring_enabled(
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        stq,
        park_id,
        response_fleet_parks,
):
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [response_fleet_parks]}],
    )
    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers={
            **utils.TVM_HEADERS,
            **HEADERS,
            'X-Idempotency-Token': '100000000',
        },
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license1_pd'},
            },
            'offer': {
                'decision': {'can_buy': True},
                'price': {'amount': '10', 'currency': 'RUB'},
            },
        },
        params={'park_id': park_id},
    )

    assert _mock_fleet_parks.parks_list.times_called == 1

    assert response.status == 200, response.text
    response_json = await response.json()
    assert response_json == {'request_id': matching.uuid_string}

    assert stq.fleet_drivers_scoring_checks.times_called == 1


@pytest.mark.parametrize(
    'config, park_id, response_fleet_parks, fleet_parks_call_number,'
    'expected_response',
    [
        (
            defaults.SCORING_ENABLED_CONFIG3,
            'park2',
            {'parks': [defaults.RESPONSE_FLEET_PARKS2]},
            0,
            {'code': '400', 'message': 'Scoring is disabled'},
        ),
        (
            defaults.SCORING_ENABLED_CONFIG2,
            'park4',
            {'parks': [defaults.RESPONSE_FLEET_PARKS3]},
            1,
            {'code': '400', 'message': 'Park park4 was not found'},
        ),
        (
            defaults.SCORING_ENABLED_CONFIG2,
            'park3',
            {'parks': [defaults.RESPONSE_FLEET_PARKS2]},
            0,
            {'code': '400', 'message': 'Scoring is disabled for park park3'},
        ),
    ],
)
async def test_scoring_disabled(
        taxi_fleet_drivers_scoring_web,
        taxi_config,
        _mock_fleet_parks,
        config,
        park_id,
        response_fleet_parks,
        fleet_parks_call_number,
        expected_response,
):
    taxi_config.set_values(config)
    _mock_fleet_parks.set_parks_list_responses([response_fleet_parks])

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers={
            **utils.TVM_HEADERS,
            **HEADERS,
            'X-Idempotency-Token': '100000000',
        },
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license1_pd'},
            },
            'offer': {
                'decision': {'can_buy': True},
                'price': {'amount': '10', 'currency': 'RUB'},
            },
        },
        params={'park_id': park_id},
    )

    assert _mock_fleet_parks.parks_list.times_called == fleet_parks_call_number

    assert response.status == 400, response.text
    response_json = await response.json()
    assert response_json == expected_response


@pytest.mark.config(**defaults.SCORING_ENABLED_CONFIG1)
@pytest.mark.parametrize(
    'parks_call_times, expected_response',
    [
        pytest.param(
            0,
            {'code': '400', 'message': 'Scoring is disabled'},
            marks=pytest.mark.config(
                FLEET_DRIVERS_SCORING_PAID_ENABLED={
                    'cities': [],
                    'countries': ['rus', 'kaz'],
                    'dbs': [],
                    'dbs_disable': [],
                    'enable': False,
                },
            ),
            id='paid disabled',
        ),
        pytest.param(
            1,
            {'code': '400', 'message': 'Scoring is disabled for park park2'},
            marks=pytest.mark.config(
                FLEET_DRIVERS_SCORING_PAID_ENABLED={
                    'cities': [],
                    'countries': [],
                    'dbs': [],
                    'dbs_disable': [],
                    'enable': True,
                },
            ),
            id='no paid scoring in country',
        ),
    ],
)
async def test_paid_disabled(
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        parks_call_times,
        expected_response,
):
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [defaults.RESPONSE_FLEET_PARKS2]}],
    )
    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers={
            **utils.TVM_HEADERS,
            **HEADERS,
            'X-Idempotency-Token': '100000000',
        },
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license1_pd'},
            },
            'offer': {
                'decision': {'can_buy': True},
                'price': {'amount': '10', 'currency': 'RUB'},
            },
        },
        params={'park_id': 'park2'},
    )
    assert response.status == 400, response.text
    response_json = await response.json()
    assert response_json == expected_response
    assert _mock_fleet_parks.parks_list.times_called == parks_call_times


@pytest.mark.pgsql('fleet_drivers_scoring', files=['test_rate_limits.sql'])
@pytest.mark.config(
    TVM_RULES=[{'src': 'fleet-drivers-scoring', 'dst': 'stq-agent'}],
    **PAID_RATE_LIMIT_CONFIG1,
    **defaults.SCORING_ENABLED_CONFIG1,
)
@pytest.mark.now(defaults.NOW2.isoformat())
@pytest.mark.parametrize(
    'park_id, flee_parks_response',
    [
        # test day rate limit
        ('park3', {'parks': [defaults.RESPONSE_FLEET_PARKS3]}),
        # test week rate limit
        ('park1', {'parks': [defaults.RESPONSE_FLEET_PARKS1]}),
    ],
)
async def test_rate_limits(
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        park_id,
        flee_parks_response,
):
    _mock_fleet_parks.set_parks_list_responses([flee_parks_response])

    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers={
            **utils.TVM_HEADERS,
            **HEADERS,
            'X-Idempotency-Token': '100000000',
        },
        json={
            'query': {
                'driver': {'license_pd_id': 'extra_super_driver_license1_pd'},
            },
            'offer': {
                'decision': {'can_buy': True},
                'price': {'amount': '10', 'currency': 'RUB'},
            },
        },
        params={'park_id': park_id},
    )
    assert _mock_fleet_parks.parks_list.times_called == 1
    assert response.status == 429, response.text

    response_json = await response.json()
    assert response_json == {
        'code': '429',
        'message': f'Rate limit achieved for park {park_id}',
    }


@pytest.mark.pgsql('fleet_drivers_scoring', files=['retry.sql'])
@pytest.mark.config(
    TVM_RULES=[{'src': 'fleet-drivers-scoring', 'dst': 'stq-agent'}],
    **defaults.RATE_LIMIT_CONFIG1,
    **PAID_RATE_LIMIT_CONFIG1,
    **defaults.SCORING_ENABLED_CONFIG1,
)
async def test_retry_ok(
        taxi_fleet_drivers_scoring_web, _mock_fleet_parks, stq, pgsql,
):
    all_checks_before = global_utils.fetch_all_checks(pgsql)

    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [defaults.RESPONSE_FLEET_PARKS1]}],
    )
    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers={
            **utils.TVM_HEADERS,
            **HEADERS,
            'X-Idempotency-Token': '100000000',
        },
        json={
            'query': {'driver': {'license_pd_id': 'license_pd_id'}},
            'offer': {
                'decision': {'can_buy': True},
                'price': {'amount': '10', 'currency': 'RUB'},
            },
        },
        params={'park_id': 'park1'},
    )

    assert response.status == 200, response.text
    response_json = await response.json()
    assert response_json == {'request_id': 'check_id'}

    all_checks_after = global_utils.fetch_all_checks(pgsql)
    assert all_checks_after == all_checks_before


@pytest.mark.pgsql('fleet_drivers_scoring', files=['retry.sql'])
@pytest.mark.config(
    TVM_RULES=[{'src': 'fleet-drivers-scoring', 'dst': 'stq-agent'}],
    **defaults.RATE_LIMIT_CONFIG1,
    **PAID_RATE_LIMIT_CONFIG1,
    **defaults.SCORING_ENABLED_CONFIG1,
)
@pytest.mark.parametrize(
    'offer, expected_response',
    [
        (
            {
                'decision': {'can_buy': True},
                'price': {'amount': '10', 'currency': 'RUB'},
            },
            {
                'code': '400',
                'message': 'License pd mismatch for same idempotency token',
            },
        ),
        (
            {
                'decision': {'can_buy': False},
                'price': {'amount': '10', 'currency': 'RUB'},
            },
            {'code': '400', 'message': 'You cannot buy if can_buy=False'},
        ),
    ],
)
async def test_retry_bad(
        taxi_fleet_drivers_scoring_web,
        _mock_fleet_parks,
        offer,
        expected_response,
        stq,
        pgsql,
):
    _mock_fleet_parks.set_parks_list_responses(
        [{'parks': [defaults.RESPONSE_FLEET_PARKS1]}],
    )
    response = await taxi_fleet_drivers_scoring_web.post(
        ENDPOINT,
        headers={
            **utils.TVM_HEADERS,
            **HEADERS,
            'X-Idempotency-Token': '100000000',
        },
        json={
            'query': {'driver': {'license_pd_id': 'license_pd_id_other'}},
            'offer': offer,
        },
        params={'park_id': 'park1'},
    )

    assert response.status == 400, response.text
    response_json = await response.json()
    assert response_json == expected_response
