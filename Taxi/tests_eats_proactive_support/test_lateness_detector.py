import pytest


ORDERS_TRACKING_RESPONSE = {
    'order_nr': '123',
    'claim_id': '123',
    'claim_alias': '124',
}


POINTS_ETA_RESPONSE = {
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
            'visited_at': {'expected': '2020-04-28T12:20:00+03:00'},
        },
    ],
    'performer_position': [37.8, 55.4],
}


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
            },  # 2 minutes - is not lateness
        },
    ],
    'performer_position': [37.8, 55.4],
}


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

CONFIG_LATENESS_OFF = pytest.mark.experiments3(
    name='eats_proactive_support_lateness_detector',
    consumers=['eats_proactive_support/lateness_detector'],
    default_value={'enabled': False},
    is_config=True,
)

CONFIG_ETA_PROVIDER = pytest.mark.experiments3(
    name='eats_proactive_support_eta_provider',
    consumers=['eats_proactive_support/eta_provider'],
    default_value={'eta_provider': 'cargo_claims'},
    is_config=True,
)


def assert_db_problems(psql, expected_db_problems_count):
    cursor = psql.cursor()
    cursor.execute('SELECT * FROM eats_proactive_support.problems;')
    db_problems = cursor.fetchall()
    assert len(db_problems) == expected_db_problems_count


def assert_db_actions(psql, expected_db_actions_count):
    cursor = psql.cursor()
    cursor.execute('SELECT * FROM eats_proactive_support.actions;')
    db_actions = cursor.fetchall()
    assert len(db_actions) == expected_db_actions_count


TRACKING_URL = (
    '/eats-orders-tracking/internal/'
    'eats-orders-tracking/v1/get-claim-by-order-nr'
)
CARGO_POINTS_ETA_URL = '/cargo-claims/api/integration/v1/claims/points-eta'
CARGO_EXTERNAL_PERFORMER_URL = '/cargo-claims/internal/external-performer'


@pytest.fixture(name='mock_eats_orders_tracking')
def _mock_eats_orders_tracking(mockserver):
    @mockserver.json_handler(TRACKING_URL)
    def mock(request):
        return mockserver.make_response(
            status=200, json=ORDERS_TRACKING_RESPONSE,
        )

    return mock


@pytest.fixture(name='mock_cargo_claims_points_eta')
def _mock_cargo_claims_points_eta(mockserver):
    @mockserver.json_handler(CARGO_POINTS_ETA_URL)
    def mock(request):
        return mockserver.make_response(status=200, json=POINTS_ETA_RESPONSE)

    return mock


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


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(EATS_PROACTIVE_SUPPORT_PROBLEM_LATENESS=LATENESS_SETTINGS)
@CONFIG_LATENESS_OFF
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.experiments3(filename='lateness_exp.json')
@pytest.mark.now(
    '2020-04-28T11:50:00+03:00',
)  # - 10 min below promise_at from fill_orders.sql
async def test_lateness_detector_feat_flag_off(stq_runner, pgsql, stq):
    order_nr = '123'
    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'lateness',
            'detector_name': 'lateness',
            'promised_at_for_lateness_detector': '2020-04-28T12:00:00+03:00',
        },
    )

    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert_db_actions(pgsql['eats_proactive_support'], 0)
    assert stq.eats_proactive_support_actions.times_called == 0


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(EATS_PROACTIVE_SUPPORT_PROBLEM_LATENESS=LATENESS_SETTINGS)
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@CONFIG_LATENESS_ON
@CONFIG_ETA_PROVIDER
@pytest.mark.experiments3(filename='lateness_exp.json')
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.parametrize(
    """order_nr,expected_eats_orders_tracking_count,
    expected_cargo_claims_count,expected_db_problems_count,
    expected_stq_actions""",
    [
        ('123', 0, 0, 0, 'empty_actions.json'),  # finished_order
        ('124', 0, 0, 1, 'not_confirmed_actions.json'),  # created_order
        ('125', 0, 0, 0, 'empty_actions.json'),  # promise_changed
        ('126', 0, 0, 0, 'empty_actions.json'),  # pickup_shipping
        (
            '127',
            0,
            0,
            1,
            'courier_on_the_way_actions.json',
        ),  # marketplace_delivery
        ('128', 1, 1, 1, 'courier_on_the_way_actions.json'),  # taken_order
        (
            '129',
            1,
            1,
            1,
            'not_started_courier_actions.json',
        ),  # not_taken_order
        ('130', 0, 0, 0, 'empty_actions.json'),  # fast_order
    ],
    ids=[
        'finished_order',
        'created_order',
        'promise_changed',
        'pickup_shipping',
        'marketplace_delivery',
        'taken_order',
        'not_taken_order',
        'fast_order',
    ],
)
@pytest.mark.now(
    '2020-04-28T11:50:00+03:00',
)  # - 10 min below promise_at from fill_orders.sql
async def test_lateness_detector_common(
        stq_runner,
        pgsql,
        stq,
        order_nr,
        expected_eats_orders_tracking_count,
        expected_cargo_claims_count,
        expected_db_problems_count,
        expected_stq_actions,
        mock_eats_orders_tracking,
        mock_cargo_claims_external_performer,
        mock_cargo_claims_points_eta,
        load_json,
):
    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'lateness',
            'detector_name': 'lateness',
            'promised_at_for_lateness_detector': '2020-04-28T12:00:00+03:00',
        },
    )

    assert_db_problems(
        pgsql['eats_proactive_support'], expected_db_problems_count,
    )
    loaded_stq_actions = load_json(expected_stq_actions)['actions']
    assert_db_actions(pgsql['eats_proactive_support'], len(loaded_stq_actions))

    assert (
        mock_eats_orders_tracking.times_called
        == expected_eats_orders_tracking_count
    )
    assert (
        mock_cargo_claims_points_eta.times_called
        == expected_cargo_claims_count
    )
    assert (
        mock_cargo_claims_external_performer.times_called
        == expected_cargo_claims_count
    )
    assert stq.eats_proactive_support_actions.times_called == len(
        loaded_stq_actions,
    )

    for _, expected_stq_action in enumerate(loaded_stq_actions):
        action_task = stq.eats_proactive_support_actions.next_call()
        assert action_task['queue'] == 'eats_proactive_support_actions'
        assert action_task['kwargs']['order_nr'] == order_nr
        assert (
            action_task['kwargs']['action_type'] == expected_stq_action['type']
        )


@pytest.fixture(name='mock_eats_orders_tracking_failed')
def _mock_eats_orders_tracking_failed(mockserver):
    @mockserver.json_handler(TRACKING_URL)
    def mock(request):
        return mockserver.make_response(
            status=400,
            json={
                'code': 'NOT_FOUND_COURIER_DATA',
                'message': 'not found courier data',
            },
        )

    return mock


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(EATS_PROACTIVE_SUPPORT_PROBLEM_LATENESS=LATENESS_SETTINGS)
@CONFIG_LATENESS_ON
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.parametrize(
    """order_nr,expected_eats_orders_tracking_count,
    expected_db_problems_count,expected_stq_actions""",
    [
        (
            '129',
            1,
            1,
            'not_confirmed_actions.json',
        ),  # no_tracking_claims_data_for_confirmed
        ('128', 1, 0, 'empty_actions.json'),
    ],  # no_tracking_claims_data_for_taken
    ids=[
        'no_tracking_claims_data_for_confirmed',
        'no_tracking_claims_data_for_taken',
    ],
)
@pytest.mark.experiments3(filename='lateness_exp.json')
@pytest.mark.now(
    '2020-04-28T11:50:00+03:00',
)  # - 10 min below promise_at from fill_orders.sql
async def test_lateness_detector_no_tracking_claims_data(
        stq_runner,
        pgsql,
        stq,
        order_nr,
        expected_eats_orders_tracking_count,
        expected_db_problems_count,
        expected_stq_actions,
        mock_eats_orders_tracking_failed,
        load_json,
):
    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'lateness',
            'detector_name': 'lateness',
            'promised_at_for_lateness_detector': '2020-04-28T12:00:00+03:00',
        },
    )

    assert_db_problems(
        pgsql['eats_proactive_support'], expected_db_problems_count,
    )
    loaded_stq_actions = load_json(expected_stq_actions)['actions']
    assert_db_actions(pgsql['eats_proactive_support'], len(loaded_stq_actions))

    assert (
        mock_eats_orders_tracking_failed.times_called
        == expected_eats_orders_tracking_count
    )
    assert stq.eats_proactive_support_actions.times_called == len(
        loaded_stq_actions,
    )

    for _, expected_stq_action in enumerate(loaded_stq_actions):
        action_task = stq.eats_proactive_support_actions.next_call()
        assert action_task['queue'] == 'eats_proactive_support_actions'
        assert action_task['kwargs']['order_nr'] == order_nr
        assert (
            action_task['kwargs']['action_type'] == expected_stq_action['type']
        )


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(EATS_PROACTIVE_SUPPORT_PROBLEM_LATENESS=LATENESS_SETTINGS)
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@CONFIG_LATENESS_ON
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.now(
    '2020-04-28T11:50:00+03:00',
)  # - 10 min below promise_at from fill_orders.sql
async def test_lateness_detector_no_extperformer_data(
        stq_runner, pgsql, stq, mock_eats_orders_tracking, mockserver,
):
    order_nr = '128'

    @mockserver.json_handler(CARGO_EXTERNAL_PERFORMER_URL)
    def mock_extperformer_not_found(request):
        return mockserver.make_response(
            status=404,
            json={'code': 'no_performer_info', 'message': 'not found'},
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

    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert_db_actions(pgsql['eats_proactive_support'], 0)

    assert mock_eats_orders_tracking.times_called == 1
    assert mock_extperformer_not_found.times_called == 1
    assert stq.eats_proactive_support_actions.times_called == 0


@pytest.fixture(name='mock_cargo_claims_points_eta_failed')
def _mock_cargo_claims_points_eta_failed(mockserver):
    @mockserver.json_handler(CARGO_POINTS_ETA_URL)
    def mock(request):
        return mockserver.make_response(status=400, json={})

    return mock


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(EATS_PROACTIVE_SUPPORT_PROBLEM_LATENESS=LATENESS_SETTINGS)
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@CONFIG_LATENESS_ON
@CONFIG_ETA_PROVIDER
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.parametrize(
    """order_nr,expected_eats_orders_tracking_count,expected_cargo_claims_count,
    expected_db_problems_count,expected_stq_actions_count""",
    [('128', 1, 1, 0, 0)],  # no_points_eta_data
    ids=['no_cargo_claims_data'],
)
@pytest.mark.now(
    '2020-04-28T11:50:00+03:00',
)  # - 10 min below promise_at from fill_orders.sql
async def test_lateness_detector_no_points_eta_data(
        stq_runner,
        pgsql,
        stq,
        order_nr,
        expected_eats_orders_tracking_count,
        expected_cargo_claims_count,
        expected_db_problems_count,
        expected_stq_actions_count,
        mock_eats_orders_tracking,
        mock_cargo_claims_external_performer,
        mock_cargo_claims_points_eta_failed,
):
    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'lateness',
            'detector_name': 'lateness',
            'promised_at_for_lateness_detector': '2020-04-28T12:00:00+03:00',
        },
    )

    assert_db_problems(
        pgsql['eats_proactive_support'], expected_db_problems_count,
    )
    assert_db_actions(
        pgsql['eats_proactive_support'], expected_stq_actions_count,
    )

    assert (
        mock_eats_orders_tracking.times_called
        == expected_eats_orders_tracking_count
    )
    assert (
        mock_cargo_claims_points_eta_failed.times_called
        == expected_cargo_claims_count
    )
    assert (
        mock_cargo_claims_external_performer.times_called
        == expected_cargo_claims_count
    )
    assert (
        stq.eats_proactive_support_actions.times_called
        == expected_stq_actions_count
    )


@pytest.fixture(name='mock_pointseta_not_assigned_courier')
def _mock_pointseta_not_assigned_courier(mockserver):
    @mockserver.json_handler(CARGO_POINTS_ETA_URL)
    def mock(request):
        return mockserver.make_response(
            status=409,
            json={'code': 'no_performer_info', 'message': 'no performer info'},
        )

    return mock


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(EATS_PROACTIVE_SUPPORT_PROBLEM_LATENESS=LATENESS_SETTINGS)
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@CONFIG_LATENESS_ON
@CONFIG_ETA_PROVIDER
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.parametrize(
    """order_nr,expected_eats_orders_tracking_count,expected_cargo_claims_count,
    expected_db_problems_count,expected_stq_actions""",
    [
        (
            '129',
            1,
            1,
            1,
            'not_assigned_courier_actions.json',
        ),  # not_assigned_courier_and_confirmed_order
        ('128', 1, 1, 0, 'empty_actions.json'),
    ],  # not_assigned_courier_and_taken_order
    ids=[
        'not_assigned_courier_and_confirmed_order',
        'not_assigned_courier_and_taken_order',
    ],
)
@pytest.mark.experiments3(filename='lateness_exp.json')
@pytest.mark.now(
    '2020-04-28T11:50:00+03:00',
)  # - 10 min below promise_at from fill_orders.sql
async def test_lateness_detector_not_assigned_courier(
        stq_runner,
        pgsql,
        stq,
        order_nr,
        expected_eats_orders_tracking_count,
        expected_cargo_claims_count,
        expected_db_problems_count,
        expected_stq_actions,
        mock_eats_orders_tracking,
        mock_cargo_claims_external_performer,
        mock_pointseta_not_assigned_courier,
        load_json,
):
    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'lateness',
            'detector_name': 'lateness',
            'promised_at_for_lateness_detector': '2020-04-28T12:00:00+03:00',
        },
    )

    loaded_stq_actions = load_json(expected_stq_actions)['actions']
    assert_db_problems(
        pgsql['eats_proactive_support'], expected_db_problems_count,
    )
    assert_db_actions(pgsql['eats_proactive_support'], len(loaded_stq_actions))

    assert (
        mock_eats_orders_tracking.times_called
        == expected_eats_orders_tracking_count
    )
    assert (
        mock_pointseta_not_assigned_courier.times_called
        == expected_cargo_claims_count
    )
    assert (
        mock_cargo_claims_external_performer.times_called
        == expected_cargo_claims_count
    )
    assert stq.eats_proactive_support_actions.times_called == len(
        loaded_stq_actions,
    )


@pytest.fixture(name='mock_cargo_claims_points_eta_multipoints')
def _mock_cargo_claims_points_eta_multipoints(mockserver):
    @mockserver.json_handler(CARGO_POINTS_ETA_URL)
    def mock(request):
        return mockserver.make_response(
            status=200,
            json={
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
                        'visit_order': 2,
                        'visit_status': 'pending',
                        'visited_at': {
                            'expected': '2020-04-28T12:20:00+03:00',
                        },
                    },
                    {
                        'id': 2,
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
                            'expected': '2020-04-28T12:20:00+03:00',
                        },
                    },
                ],
                'performer_position': [37.8, 55.4],
            },
        )

    return mock


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(EATS_PROACTIVE_SUPPORT_PROBLEM_LATENESS=LATENESS_SETTINGS)
@CONFIG_LATENESS_ON
@CONFIG_ETA_PROVIDER
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.parametrize(
    """order_nr,expected_eats_orders_tracking_count,expected_cargo_claims_count,
    expected_db_problems_count,expected_stq_actions_count""",
    [('129', 1, 1, 0, 0)],  # multipoints
    ids=['multipoints'],
)
@pytest.mark.experiments3(filename='lateness_exp.json')
@pytest.mark.now(
    '2020-04-28T11:50:00+03:00',
)  # - 10 min below promise_at from fill_orders.sql
async def test_lateness_detector_multipoints(
        stq_runner,
        pgsql,
        stq,
        order_nr,
        expected_eats_orders_tracking_count,
        expected_cargo_claims_count,
        expected_db_problems_count,
        expected_stq_actions_count,
        mock_eats_orders_tracking,
        mock_cargo_claims_external_performer,
        mock_cargo_claims_points_eta_multipoints,
):
    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'lateness',
            'detector_name': 'lateness',
            'promised_at_for_lateness_detector': '2020-04-28T12:00:00+03:00',
        },
    )

    assert_db_problems(
        pgsql['eats_proactive_support'], expected_db_problems_count,
    )
    assert_db_actions(
        pgsql['eats_proactive_support'], expected_stq_actions_count,
    )

    assert (
        mock_eats_orders_tracking.times_called
        == expected_eats_orders_tracking_count
    )
    assert (
        mock_cargo_claims_points_eta_multipoints.times_called
        == expected_cargo_claims_count
    )
    assert (
        mock_cargo_claims_external_performer.times_called
        == expected_cargo_claims_count
    )
    assert (
        stq.eats_proactive_support_actions.times_called
        == expected_stq_actions_count
    )


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(EATS_PROACTIVE_SUPPORT_PROBLEM_LATENESS=LATENESS_SETTINGS)
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@CONFIG_LATENESS_ON
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
async def test_lateness_detector_multidelivery(
        stq_runner, pgsql, stq, mock_eats_orders_tracking, mockserver,
):
    @mockserver.json_handler(CARGO_EXTERNAL_PERFORMER_URL)
    def mock_extperformer_muldelivery(request):
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
                'batch_info': {
                    'delivery_order': [
                        {'claim_id': '123', 'order': 1},
                        {'claim_id': '124', 'order': 2},
                        {'claim_id': '125', 'order': 3},
                    ],
                },
            },
        )

    order_nr = '129'
    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'lateness',
            'detector_name': 'lateness',
            'promised_at_for_lateness_detector': '2020-04-28T12:00:00+03:00',
        },
    )

    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert_db_actions(pgsql['eats_proactive_support'], 0)

    assert mock_eats_orders_tracking.times_called == 1
    assert mock_extperformer_muldelivery.times_called == 1
    assert stq.eats_proactive_support_actions.times_called == 0


@pytest.fixture(name='mock_pointseta_with_valid_lateness')
def _mock_pointseta_with_valid_lateness(mockserver):
    @mockserver.json_handler(CARGO_POINTS_ETA_URL)
    def mock(request):
        return mockserver.make_response(
            status=200, json=POINTS_ETA_RESPONSE_WITH_NO_LATENESS,
        )

    return mock


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(EATS_PROACTIVE_SUPPORT_PROBLEM_LATENESS=LATENESS_SETTINGS)
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@pytest.mark.experiments3(filename='lateness_exp.json')
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.parametrize(
    """order_nr,expected_eats_orders_tracking_count,
    expected_cargo_claims_count,expected_db_problems_count,
    expected_stq_actions,expected_stq_detections_count""",
    [
        (
            '128',
            1,
            1,
            0,
            'empty_actions.json',
            1,
        ),  # valid_courier_lateness_or_not_detected_problem_with_repeat
    ],
    ids=['valid_courier_lateness_or_not_detected_problem_with_repeat'],
)
@CONFIG_LATENESS_ON
@CONFIG_ETA_PROVIDER
@pytest.mark.now(
    '2020-04-28T11:50:00+03:00',
)  # - 10 min below promise_at from fill_orders.sql
async def test_lateness_detector_with_no_lateness(
        stq_runner,
        pgsql,
        stq,
        order_nr,
        expected_eats_orders_tracking_count,
        expected_cargo_claims_count,
        expected_db_problems_count,
        expected_stq_actions,
        expected_stq_detections_count,
        mock_eats_orders_tracking,
        mock_cargo_claims_external_performer,
        mock_pointseta_with_valid_lateness,
        load_json,
):
    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'lateness',
            'detector_name': 'lateness',
            'promised_at_for_lateness_detector': '2020-04-28T12:00:00+03:00',
        },
    )

    assert_db_problems(
        pgsql['eats_proactive_support'], expected_db_problems_count,
    )
    loaded_stq_actions = load_json(expected_stq_actions)['actions']
    assert_db_actions(pgsql['eats_proactive_support'], len(loaded_stq_actions))

    assert (
        mock_eats_orders_tracking.times_called
        == expected_eats_orders_tracking_count
    )
    assert (
        mock_pointseta_with_valid_lateness.times_called
        == expected_cargo_claims_count
    )
    assert (
        mock_cargo_claims_external_performer.times_called
        == expected_cargo_claims_count
    )
    assert stq.eats_proactive_support_actions.times_called == len(
        loaded_stq_actions,
    )
    assert (
        stq.eats_proactive_support_detections.times_called
        == expected_stq_detections_count
    )
    for _, expected_stq_action in enumerate(loaded_stq_actions):
        action_task = stq.eats_proactive_support_actions.next_call()
        assert action_task['queue'] == 'eats_proactive_support_actions'
        assert action_task['kwargs']['order_nr'] == order_nr
        assert (
            action_task['kwargs']['action_type'] == expected_stq_action['type']
        )

    if stq.eats_proactive_support_detections.times_called != 0:
        task = stq.eats_proactive_support_detections.next_call()
        assert task['queue'] == 'eats_proactive_support_detections'
        assert task['kwargs']['order_nr'] == order_nr
        assert task['kwargs']['detector_name'] == 'lateness'
        assert task['kwargs']['event_name'] == 'additional_lateness'
