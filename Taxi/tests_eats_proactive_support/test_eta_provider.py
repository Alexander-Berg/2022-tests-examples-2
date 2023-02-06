import pytest

TRACKING_URL = (
    '/eats-orders-tracking/internal/'
    'eats-orders-tracking/v1/get-claim-by-order-nr'
)
CARGO_POINTS_ETA_URL = '/cargo-claims/api/integration/v1/claims/points-eta'
CARGO_EXTERNAL_PERFORMER_URL = '/cargo-claims/internal/external-performer'
EATS_ETA_URL = '/eats-eta/v1/eta/orders/estimate'

ORDER_NR = '128'

DETECTORS_CONFIG = {
    'lateness': {
        'events_settings': [
            {'enabled': True, 'delay_sec': 0, 'order_event': 'lateness'},
        ],
    },
}

MAP_CARGO_ALIAS_TO_CLIENT_ID = {'124': {'client_id': '123'}}

LATENESS_SETTINGS = {
    'enabled': True,
    'first_interval_before_promise_sec': 600,
    'second_interval_before_promise_sec': 300,
    'maximal_courier_eta_delay_sec': 180,
    'maximal_fast_orders_lifetime_sec': 1260,  # 21 minutes
}

CONFIG_LATENESS_ON = pytest.mark.experiments3(
    name='eats_proactive_support_lateness_detector',
    consumers=['eats_proactive_support/lateness_detector'],
    default_value={'enabled': True},
    is_config=True,
)

POINTS_ETA_RESPONSE_WITH_NO_LATENESS = {
    'id': 'temp_id',
    'route_points': [
        {
            'id': 1,
            'address': {
                'fullname': '3',
                'coordinates': [40.8, 50.4],
                'country': '3',
                'city': '3',
                'street': '3',
                'building': '3',
            },
            'type': 'destination',
            'visit_order': 3,
            'visit_status': 'pending',
            'visited_at': {
                'expected': '2020-04-28T12:02:00+03:00',
            },  # 2 minutes - is no lateness
        },
    ],
    'performer_position': [37.8, 55.4],
}


def assert_db_problems(psql, expected_db_problems_count):
    cursor = psql.cursor()
    cursor.execute('SELECT * FROM eats_proactive_support.problems;')
    db_problems = cursor.fetchall()
    assert len(db_problems) == expected_db_problems_count


@pytest.fixture(name='mock_cargo_claims_external_performer')
def _mock_cargo_claims_external_performer(mockserver):
    @mockserver.json_handler(CARGO_EXTERNAL_PERFORMER_URL)
    def mock(request):
        return mockserver.make_response(
            status=200,
            json={
                'car_info': {'model': 'car_model_1', 'number': 'car_number_1'},
                'eats_profile_id': '123',
                'name': 'Kostya',
                'first_name': 'some first name',
                'legal_name': 'park_name_1',
                'driver_id': 'driver_id1',
                'park_id': 'park_id1',
                'taxi_alias_id': 'order_alias_id_1',
            },
        )

    return mock


@pytest.fixture(name='mock_cargo_eta')
def _mock_pointseta(mockserver):
    @mockserver.json_handler(CARGO_POINTS_ETA_URL)
    def mock(request):
        return mockserver.make_response(
            status=200, json=POINTS_ETA_RESPONSE_WITH_NO_LATENESS,
        )

    return mock


@pytest.fixture(name='mock_eats_eta')
def _mock_eats_eta(mockserver):
    @mockserver.json_handler(EATS_ETA_URL)
    def _handler(request):
        mock_response = {
            'orders': [
                {
                    'order_nr': '129',
                    'estimations': [
                        {
                            'name': 'courier_arrival_at',
                            'calculated_at': '2020-10-28T18:30:00.00+00:00',
                            'status': 'in_progress',
                        },
                        {
                            'name': 'delivery_at',
                            'calculated_at': '2020-04-28T12:00:00+03:00',
                            'expected_at': '2020-04-28T12:02:00+03:00',
                        },
                    ],
                },
            ],
            'not_found_orders': [],
        }
        return mockserver.make_response(json=mock_response, status=200)

    return _handler


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(EATS_PROACTIVE_SUPPORT_PROBLEM_LATENESS=LATENESS_SETTINGS)
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.parametrize(
    """order_nr, expected_cargo_eta_called, expected_eats_eta_called""",
    [
        pytest.param('128', 1, 0, id='cargo_eta'),
        pytest.param('129', 0, 1, id='eats_eta'),
    ],
)
@CONFIG_LATENESS_ON
@pytest.mark.experiments3(filename='eta_provider_exp.json')
@pytest.mark.now(
    '2020-04-28T11:50:00+03:00',
)  # - 10 min below promise_at from fill_orders.sql
async def test_lateness_detector_cargo_eta(
        stq_runner,
        pgsql,
        stq,
        order_nr,
        expected_cargo_eta_called,
        expected_eats_eta_called,
        mock_cargo_claims_external_performer,
        mock_cargo_eta,
        mock_eats_eta,
        load_json,
        mockserver,
):
    @mockserver.json_handler(TRACKING_URL)
    def mock_eats_orders_tracking(request):
        return mockserver.make_response(
            status=200,
            json={
                'order_nr': order_nr,
                'claim_id': '123',
                'claim_alias': '124',
            },
        )

    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'lateness',
            'detector_name': 'lateness',
            'promised_at_for_lateness_detector': '2020-04-28T12:00:00+03:00',
        },
    )

    assert mock_eats_orders_tracking.times_called == 1
    assert mock_cargo_claims_external_performer.times_called == 1
    assert mock_cargo_eta.times_called == expected_cargo_eta_called
    assert mock_eats_eta.times_called == expected_eats_eta_called
    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert stq.eats_proactive_support_detections.times_called == 1

    task = stq.eats_proactive_support_detections.next_call()
    assert task['queue'] == 'eats_proactive_support_detections'
    assert task['kwargs']['order_nr'] == order_nr
    assert task['kwargs']['detector_name'] == 'lateness'
    assert task['kwargs']['event_name'] == 'additional_lateness'


@pytest.fixture(name='mock_eats_eta_failed')
def _mock_eats_eta_failed(mockserver):
    @mockserver.json_handler(EATS_ETA_URL)
    def mock(request):
        return mockserver.make_response(status=500)

    return mock


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(EATS_PROACTIVE_SUPPORT_PROBLEM_LATENESS=LATENESS_SETTINGS)
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@CONFIG_LATENESS_ON
@pytest.mark.experiments3(filename='eta_provider_exp.json')
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.now(
    '2020-04-28T11:50:00+03:00',
)  # - 10 min below promise_at from fill_orders.sql
async def test_lateness_detector_eats_eta_failed(
        stq_runner,
        stq,
        pgsql,
        mockserver,
        mock_cargo_claims_external_performer,
        mock_cargo_eta,
        mock_eats_eta_failed,
):
    @mockserver.json_handler(TRACKING_URL)
    def mock_eats_orders_tracking(request):
        return mockserver.make_response(
            status=200,
            json={'order_nr': '129', 'claim_id': '123', 'claim_alias': '124'},
        )

    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': '129',
            'event_name': 'lateness',
            'detector_name': 'lateness',
            'promised_at_for_lateness_detector': '2020-04-28T12:00:00+03:00',
        },
    )

    assert mock_eats_orders_tracking.times_called == 1
    assert mock_cargo_eta.times_called == 0
    assert mock_cargo_claims_external_performer.times_called == 1
    assert mock_eats_eta_failed.times_called == 1
    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert stq.eats_proactive_support_detections.times_called == 0
