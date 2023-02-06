import pytest


DETECTORS_CONFIG = {
    'courier_idle': {
        'events_settings': [
            {'enabled': True, 'delay_sec': 0, 'order_event': 'confirmed'},
            {
                'enabled': True,
                'delay_sec': 0,
                'order_event': 'check_courier_idle',
            },
        ],
    },
}
MAP_CARGO_ALIAS_TO_CLIENT_ID = {'111': {'client_id': '123'}}
COURIER_IDLE_SETTINGS = {
    'period_sec': 300,
    'maximal_allowed_idle_sec': 600,
    'maximal_allowed_eta_increase_sec': 900,
    'courier_poisition_time_point_delta_sec': 60,
    'geocoordinates_delta': {'lat_delta': 0.0001, 'lon_delta': 0.0001},
    'maximal_order_lifetime_after_promise_sec': 86400,
    'actions': {
        'action_courier_increasing_eta_to_client': {
            'type': 'courier_robocall',
            'payload': {'delay_sec': 0, 'voice_line': 'go_go_go'},
        },
        'action_courier_idle_to_client': {
            'type': 'courier_robocall',
            'payload': {'delay_sec': 0, 'voice_line': 'stand_up_and_go'},
        },
        'action_courier_increasing_eta_to_place': {
            'type': 'courier_robocall',
            'payload': {'delay_sec': 0, 'voice_line': 'go_go_go'},
        },
        'action_courier_idle_to_place': {
            'type': 'courier_robocall',
            'payload': {'delay_sec': 0, 'voice_line': 'stand_up_and_go'},
        },
    },
}

COURIER_IDLE_EXP = pytest.mark.experiments3(
    name='eats_proactive_support_courier_idle_detector',
    consumers=['eats_proactive_support/courier_idle'],
    default_value={'enabled': True},
    clauses=[
        {
            'enabled': True,
            'extension_method': 'replace',
            'value': {'enabled': False},
            'predicate': {
                'init': {
                    'arg_name': 'device_id',
                    'arg_type': 'string',
                    'value': 'detector_off',
                },
                'type': 'eq',
            },
        },
    ],
)


TRACKING_URL = (
    '/eats-orders-tracking/internal/'
    'eats-orders-tracking/v1/get-claim-by-order-nr'
)
CARGO_POINTS_ETA_URL = '/cargo-claims/api/integration/v1/claims/points-eta'
CARGO_PERFORMER_POSITION_URL = (
    '/cargo-claims/api/integration/v1/claims/performer-position'
)
CARGO_EXTERNAL_PERFORMER_URL = '/cargo-claims/internal/external-performer'
DEFAULT_COURIER_ID = 'park_id1_driver_id1'


def generate_points_eta_response(
        status='pending',
        type_str='destination',
        eta='2020-04-28T12:20:00+03:00',
        point_id=1,
):
    return {
        'id': 'temp_id',
        'route_points': [
            {
                'id': point_id + 10,
                'address': {
                    'fullname': '3',
                    'coordinates': [40.8, 50.4],
                    'country': '3',
                    'city': '3',
                    'street': '3',
                    'building': '3',
                },
                'type': 'return',
                'visit_order': 4,
                'visit_status': 'arrived',
                'visited_at': {'expected': '2019-04-28T12:20:00+03:00'},
            },
            {
                'id': point_id - 1,
                'address': {
                    'fullname': '3',
                    'coordinates': [40.8, 50.4],
                    'country': '3',
                    'city': '3',
                    'street': '3',
                    'building': '3',
                },
                'type': 'source',
                'visit_order': 2,
                'visit_status': 'visited',
                'visited_at': {'actual': '2019-04-28T10:20:00+03:00'},
            },
            {
                'id': point_id,
                'address': {
                    'fullname': '3',
                    'coordinates': [40.8, 50.4],
                    'country': '3',
                    'city': '3',
                    'street': '3',
                    'building': '3',
                },
                'type': type_str,
                'visit_order': 3,
                'visit_status': status,
                'visited_at': {'expected': eta},
            },
        ],
    }


def gen_performer_position_response(lat=1.0, lon=2.0, timestamp=1588063801):
    return {'position': {'lat': lat, 'lon': lon, 'timestamp': timestamp}}


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


def assert_db_order_park_driver_id(psql, order_nr, park_id, driver_id):
    cursor = psql.cursor()
    sql_script = f"""SELECT park_id, driver_id
    FROM eats_proactive_support.orders WHERE order_nr = '{order_nr}';"""
    cursor.execute(sql_script)
    data = cursor.fetchall()
    assert len(data) == 1
    assert data[0][0] == park_id
    assert data[0][1] == driver_id


def assert_new_detection_task(
        task,
        order_nr,
        fixed_eta=None,
        point_id=None,
        fixed_start_idle_time=None,
        fixed_courier_coordinates=None,
        fixed_courier_id=None,
):
    assert task['queue'] == 'eats_proactive_support_detections'
    assert task['kwargs']['order_nr'] == order_nr
    assert task['kwargs']['detector_name'] == 'courier_idle'
    assert task['kwargs']['event_name'] == 'check_courier_idle'
    if fixed_eta:
        assert (
            task['kwargs']['fixed_eta_for_courier_idle_detector'] == fixed_eta
        )
    if point_id:
        assert (
            task['kwargs']['fixed_point_id_for_courier_idle_detector']
            == point_id
        )
    if fixed_start_idle_time:
        assert (
            task['kwargs']['fixed_start_idle_for_courier_idle_detector']
            == fixed_start_idle_time
        )
    if fixed_courier_coordinates:
        assert (
            task['kwargs'][
                'fixed_courier_coordinates_for_courier_idle_detector'
            ]
            == fixed_courier_coordinates
        )
    if fixed_courier_id:
        assert (
            task['kwargs']['fixed_courier_id_for_courier_idle_detector']
            == fixed_courier_id
        )


def assert_new_action_task(task, order_nr):
    assert task['queue'] == 'eats_proactive_support_actions'
    assert task['kwargs']['order_nr'] == order_nr


@pytest.fixture(name='mock_eats_orders_tracking')
def _mock_eats_orders_tracking(mockserver):
    @mockserver.json_handler(TRACKING_URL)
    def mock(request):
        order_nr = request.query['order_nr']
        mock_response = {
            'order_nr': order_nr,
            'claim_id': order_nr,
            'claim_alias': '111',
        }
        return mockserver.make_response(status=200, json=mock_response)

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


@pytest.fixture(name='mock_cargo_claims_points_eta')
def _mock_cargo_claims_points_eta(mockserver):
    @mockserver.json_handler(CARGO_POINTS_ETA_URL)
    def mock(request):
        return mockserver.make_response(
            status=200, json=generate_points_eta_response(),
        )

    return mock


@pytest.fixture(name='mock_cargo_claims_performer_position')
def _mock_cargo_claims_performer_position(mockserver):
    @mockserver.json_handler(CARGO_PERFORMER_POSITION_URL)
    def mock(request):
        return mockserver.make_response(
            status=200, json=gen_performer_position_response(),
        )

    return mock


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@COURIER_IDLE_EXP
@pytest.mark.now('2020-04-28T11:50:00+03:00')
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
async def test_courier_idle_detector_feat_flag_off(stq_runner, pgsql, stq):
    order_nr = '124'  # deivce_id gen off feat_flag

    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'confirmed',
            'detector_name': 'courier_idle',
        },
    )

    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert_db_actions(pgsql['eats_proactive_support'], 0)

    assert stq.eats_proactive_support_actions.times_called == 0
    assert stq.eats_proactive_support_detections.times_called == 0


@pytest.mark.parametrize(
    """fixed_park_driver_id, current_park_id, current_driver_id,"""
    """order_nr, courier_busy, expected_stq_detection_count""",
    [
        (None, None, '125', '123', False, 0),
        (None, '125', None, '123', False, 0),
        ('124_125', '125', '125', '123', False, 1),
        ('124_125', 'park_id126', 'driver_id126', '126', False, 1),
        ('124_125', 'park_id127', 'driver_id127', '127', True, 1),
    ],
    ids=[
        'no_driver_id',
        'no_park_id',
        'courier_changed',
        'courier_finished_order',
        'courier_busy',
    ],
)
@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@pytest.mark.now('2020-04-28T11:50:00+03:00')
@COURIER_IDLE_EXP
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
async def test_courier_idle_detector_different_driver_data(
        stq_runner,
        mockserver,
        pgsql,
        stq,
        mock_eats_orders_tracking,
        fixed_park_driver_id,
        current_driver_id,
        current_park_id,
        order_nr,
        courier_busy,
        expected_stq_detection_count,
        mock_cargo_claims_performer_position,
        mock_cargo_claims_points_eta,
):
    @mockserver.json_handler(CARGO_EXTERNAL_PERFORMER_URL)
    def mock_extperformer_driverdata(request):
        return mockserver.make_response(
            status=200,
            json={
                'car_info': {'model': 'car_model_1', 'number': 'car_number_1'},
                'eats_profile_id': '123',
                'name': 'Kostya',
                'first_name': 'some first name',
                'legal_name': 'park_name_1',
                'driver_id': current_driver_id,
                'park_id': current_park_id,
                'taxi_alias_id': 'order_alias_id_1',
            },
        )

    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'check_courier_idle',
            'detector_name': 'courier_idle',
            'fixed_courier_id_for_courier_idle_detector': fixed_park_driver_id,
        },
    )

    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert_db_actions(pgsql['eats_proactive_support'], 0)

    assert mock_eats_orders_tracking.times_called == 1
    assert mock_extperformer_driverdata.times_called == 1

    assert stq.eats_proactive_support_actions.times_called == 0
    assert (
        stq.eats_proactive_support_detections.times_called
        == expected_stq_detection_count
    )
    if expected_stq_detection_count != 0:  # for changed courier
        task = stq.eats_proactive_support_detections.next_call()
        if courier_busy:
            fixed_courier_id = None
        else:
            fixed_courier_id = current_park_id + '_' + current_driver_id
            assert_db_order_park_driver_id(
                pgsql['eats_proactive_support'],
                order_nr,
                current_park_id,
                current_driver_id,
            )
        assert_new_detection_task(
            task, order_nr, fixed_courier_id=fixed_courier_id,
        )


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@COURIER_IDLE_EXP
@pytest.mark.now('2020-04-28T11:50:00+03:00')
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
async def test_courier_idle_detector_multidelivery(
        stq_runner, mockserver, pgsql, stq, mock_eats_orders_tracking,
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

    order_nr = '123'

    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'confirmed',
            'detector_name': 'courier_idle',
        },
    )

    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert_db_actions(pgsql['eats_proactive_support'], 0)

    assert mock_eats_orders_tracking.times_called == 1
    assert mock_extperformer_muldelivery.times_called == 1

    assert stq.eats_proactive_support_actions.times_called == 0
    assert stq.eats_proactive_support_detections.times_called == 0


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_PROBLEM_COURIER_IDLE=COURIER_IDLE_SETTINGS,
)
@pytest.mark.now('2020-04-28T11:50:00+03:00')
@COURIER_IDLE_EXP
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
async def test_courier_idle_detector_no_corp_client_id(
        stq_runner,
        mockserver,
        pgsql,
        stq,
        mock_cargo_claims_external_performer,
):
    order_nr = '123'

    @mockserver.json_handler(TRACKING_URL)
    def mock_tracking_no_default_alias(request):
        return mockserver.make_response(
            status=200,
            json={
                'order_nr': order_nr,
                'claim_id': order_nr,
                'claim_alias': 'unknown',
            },
        )

    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'confirmed',
            'detector_name': 'courier_idle',
        },
    )

    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert_db_actions(pgsql['eats_proactive_support'], 0)

    assert mock_tracking_no_default_alias.times_called == 1
    assert mock_cargo_claims_external_performer.times_called == 1

    assert stq.eats_proactive_support_actions.times_called == 0
    assert stq.eats_proactive_support_detections.times_called == 0


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_PROBLEM_COURIER_IDLE=COURIER_IDLE_SETTINGS,
)
@COURIER_IDLE_EXP
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.now('2020-04-28T11:50:00+03:00')
async def test_courier_idle_detector_not_actual_geo_data(
        stq_runner,
        mockserver,
        pgsql,
        stq,
        mock_eats_orders_tracking,
        mock_cargo_claims_external_performer,
):
    @mockserver.json_handler(CARGO_PERFORMER_POSITION_URL)
    def mock_perpos_not_actual_geodata(request):
        return mockserver.make_response(
            status=200,
            json={
                'position': {'lat': 1.0, 'lon': 2.0, 'timestamp': 1000000000},
            },
        )

    order_nr = '123'
    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'confirmed',
            'detector_name': 'courier_idle',
        },
    )

    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert_db_actions(pgsql['eats_proactive_support'], 0)

    assert mock_eats_orders_tracking.times_called == 1
    assert mock_cargo_claims_external_performer.times_called == 1
    assert mock_perpos_not_actual_geodata.times_called == 1

    assert stq.eats_proactive_support_actions.times_called == 0
    assert stq.eats_proactive_support_detections.times_called == 1

    task = stq.eats_proactive_support_detections.next_call()
    assert_new_detection_task(task, order_nr)


@pytest.mark.parametrize(
    """order_nr""",
    ['123_not_exist', '125', '130'],
    ids=['no_order_in_db', 'finished_order', 'stack_order'],
)
@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_PROBLEM_COURIER_IDLE=COURIER_IDLE_SETTINGS,
)
@pytest.mark.now('2020-04-28T11:50:00+03:00')
@COURIER_IDLE_EXP
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
async def test_courier_idle_detector_not_correct_order(
        stq_runner, pgsql, stq, order_nr,
):

    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'confirmed',
            'detector_name': 'courier_idle',
        },
    )

    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert_db_actions(pgsql['eats_proactive_support'], 0)

    assert stq.eats_proactive_support_actions.times_called == 0
    assert stq.eats_proactive_support_detections.times_called == 0


@pytest.mark.parametrize(
    """visit_status, visit_type, multipoints,"""
    """expected_stq_detections_count""",
    [
        ('arrived', 'destination', False, 1),
        ('visited', 'destination', False, 1),
        ('pending', 'return', False, 0),
        (None, None, True, 0),
    ],
    ids=[
        'courier_arrived_now',
        'courier_visited_point',
        'courier_returning',
        'multipoints',
    ],
)
@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_PROBLEM_COURIER_IDLE=COURIER_IDLE_SETTINGS,
)
@COURIER_IDLE_EXP
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.now('2020-04-28T11:50:00+03:00')
async def test_courier_idle_detector_not_interesting_points(
        stq_runner,
        mockserver,
        pgsql,
        stq,
        mock_eats_orders_tracking,
        mock_cargo_claims_external_performer,
        mock_cargo_claims_performer_position,
        visit_status,
        visit_type,
        multipoints,
        expected_stq_detections_count,
):
    @mockserver.json_handler(CARGO_POINTS_ETA_URL)
    def mock_pointseta_custom_responses(request):
        if multipoints:
            mock_response = {
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
                        'visit_order': 5,
                        'visit_status': 'pending',
                        'visited_at': {
                            'expected': '2020-04-28T12:20:00+03:00',
                        },
                    },
                    {
                        'id': 234,
                        'address': {
                            'fullname': '3',
                            'coordinates': [40.8, 50.4],
                            'country': '3',
                            'city': '3',
                            'street': '3',
                            'building': '3',
                        },
                        'type': 'return',
                        'visit_order': 4,
                        'visit_status': 'return',
                        'visited_at': {
                            'expected': '2019-04-28T12:20:00+03:00',
                        },
                    },
                    {
                        'id': 2,
                        'address': {
                            'fullname': '3',
                            'coordinates': [42.8, 52.4],
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
            }
        else:
            mock_response = generate_points_eta_response(
                status=visit_status, type_str=visit_type,
            )
        return mockserver.make_response(status=200, json=mock_response)

    order_nr = '123'

    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'confirmed',
            'detector_name': 'courier_idle',
        },
    )

    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert_db_actions(pgsql['eats_proactive_support'], 0)

    assert mock_eats_orders_tracking.times_called == 1
    assert mock_cargo_claims_external_performer.times_called == 1
    assert mock_cargo_claims_performer_position.times_called == 1
    assert mock_pointseta_custom_responses.times_called == 1

    assert stq.eats_proactive_support_actions.times_called == 0
    assert (
        stq.eats_proactive_support_detections.times_called
        == expected_stq_detections_count
    )
    if expected_stq_detections_count != 0:
        task = stq.eats_proactive_support_detections.next_call()
        assert_new_detection_task(task, order_nr)


@pytest.mark.parametrize(
    """fixed_coordinates,current_coordinates,fixed_start_idle_time,"""
    """result_start_idle_time,"""
    """expected_sqt_detections_count,expected_sqt_actions_count""",
    [
        (
            None,
            {'lat': 0.0, 'lon': 0.0},
            '2020-04-28T08:20:00+00:00',
            None,
            1,
            0,
        ),  # no_fixed_coordinates
        (
            {'lat': 5.0, 'lon': 6.0},
            {'lat': 5.0, 'lon': 6.0},
            None,
            '2020-04-28T08:45:00+00:00',
            1,
            0,
        ),  # not_changed_position_with_no_fixed_start_idle_time
        (
            {'lat': 5.0, 'lon': 6.0},
            {'lat': 5.0, 'lon': 6.0},
            '2020-04-28T08:45:00+00:00',
            '2020-04-28T08:45:00+00:00',
            1,
            0,
        ),  # not_changed_position_with_small_idle_time_decreased_eta
        (
            {'lat': 5.0, 'lon': 6.0},
            {'lat': 5.0, 'lon': 6.0},
            '2020-04-28T08:40:00+00:00',
            None,
            0,
            1,
        ),  # not_changed_position_with_big_idle_time_problem
    ],
    ids=[
        'no_fixed_coordinates',
        'not_changed_position_with_no_fixed_start_idle_time',
        'not_changed_position_with_small_idle_time_decreased_eta',
        'not_changed_position_with_big_idle_time_problem',
    ],
)
@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_PROBLEM_COURIER_IDLE=COURIER_IDLE_SETTINGS,
)
@COURIER_IDLE_EXP
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.now('2020-04-28T8:50:00+00:00')
async def test_courier_idle_detector_with_different_coordinates(
        stq_runner,
        mockserver,
        pgsql,
        stq,
        mock_eats_orders_tracking,
        mock_cargo_claims_external_performer,
        mock_cargo_claims_points_eta,
        fixed_coordinates,
        current_coordinates,
        fixed_start_idle_time,
        result_start_idle_time,
        expected_sqt_detections_count,
        expected_sqt_actions_count,
):
    @mockserver.json_handler(CARGO_PERFORMER_POSITION_URL)
    def mock_performer_coord_responses(request):
        return mockserver.make_response(
            status=200,
            json=gen_performer_position_response(
                lat=current_coordinates['lat'], lon=current_coordinates['lon'],
            ),
        )

    order_nr = '123'

    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'check_courier_idle',
            'detector_name': 'courier_idle',
            'fixed_eta_for_courier_idle_detector': (
                '2020-04-28T09:30:00+00:00'
            ),  # eta is bigger than default points-eta response
            'fixed_point_id_for_courier_idle_detector': 1,
            'fixed_courier_coordinates_for_courier_idle_detector': (
                fixed_coordinates
            ),
            'fixed_start_idle_for_courier_idle_detector': (
                fixed_start_idle_time
            ),
            'fixed_courier_id_for_courier_idle_detector': DEFAULT_COURIER_ID,
        },
    )

    problems_count = expected_sqt_actions_count
    assert_db_problems(pgsql['eats_proactive_support'], problems_count)
    assert_db_actions(
        pgsql['eats_proactive_support'], expected_sqt_actions_count,
    )

    assert mock_eats_orders_tracking.times_called == 1
    assert mock_cargo_claims_external_performer.times_called == 1
    assert mock_performer_coord_responses.times_called == 1
    assert mock_cargo_claims_points_eta.times_called == 1

    assert (
        stq.eats_proactive_support_actions.times_called
        == expected_sqt_actions_count
    )
    assert (
        stq.eats_proactive_support_detections.times_called
        == expected_sqt_detections_count
    )

    if expected_sqt_detections_count != 0:
        task = stq.eats_proactive_support_detections.next_call()
        assert_new_detection_task(
            task,
            order_nr,
            point_id=1,
            fixed_courier_coordinates=current_coordinates,
            fixed_start_idle_time=result_start_idle_time,
            fixed_courier_id=DEFAULT_COURIER_ID,
        )
    if expected_sqt_actions_count != 0:
        task = stq.eats_proactive_support_actions.next_call()
        assert_new_action_task(task, order_nr)


@pytest.mark.parametrize(
    """fixed_eta, current_eta, current_point_id, result_eta,"""
    """expected_sqt_detections_count, expected_sqt_actions_count""",
    [
        (
            None,
            '2020-04-28T09:20:00+00:00',
            1,
            '2020-04-28T09:20:00+00:00',
            1,
            0,
        ),  # no_fixed_eta
        ('2020-04-28T09:20:00+00:00', None, 1, None, 1, 0),  # no_current_eta
        (
            '2020-04-28T09:20:00+00:00',
            '2020-04-28T09:20:00+00:00',
            2,
            '2020-04-28T09:20:00+00:00',
            1,
            0,
        ),  # destination_point_changed
        (
            '2020-04-28T09:20:00+00:00',
            '2020-04-28T09:19:00+00:00',
            1,
            '2020-04-28T09:19:00+00:00',
            1,
            0,
        ),  # eta_decreased_no_problem
        (
            '2020-04-28T09:20:00+00:00',
            '2020-04-28T09:25:00+00:00',
            1,
            '2020-04-28T09:20:00+00:00',
            1,
            0,
        ),  # courier_moving_idle_allowed_no_problem
        (
            '2020-04-28T09:20:00+00:00',
            '2020-04-28T09:50:00+00:00',
            1,
            None,
            0,
            1,
        ),  # courier_moving_idle_with_problem
    ],
    ids=[
        'no_fixed_eta',
        'no_current_eta',
        'destination_point_changed',
        'eta_decreased_no_problem',
        'courier_moving_idle_allowed_no_problem',
        'courier_moving_idle_with_problem',
    ],
)
@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@pytest.mark.config(
    EATS_PROACTIVE_SUPPORT_PROBLEM_COURIER_IDLE=COURIER_IDLE_SETTINGS,
)
@COURIER_IDLE_EXP
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.now('2020-04-28T11:50:00+03:00')
async def test_courier_idle_detector_with_different_eta(
        stq_runner,
        mockserver,
        pgsql,
        stq,
        mock_eats_orders_tracking,
        mock_cargo_claims_external_performer,
        mock_cargo_claims_performer_position,
        fixed_eta,
        current_eta,
        current_point_id,
        result_eta,
        expected_sqt_detections_count,
        expected_sqt_actions_count,
):
    @mockserver.json_handler(CARGO_POINTS_ETA_URL)
    def mock_pointseta_custom_responses(request):
        return mockserver.make_response(
            status=200,
            json=generate_points_eta_response(
                eta=current_eta, point_id=current_point_id,
            ),
        )

    order_nr = '123'

    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'check_courier_idle',
            'detector_name': 'courier_idle',
            'fixed_eta_for_courier_idle_detector': fixed_eta,
            'fixed_point_id_for_courier_idle_detector': 1,
            'fixed_courier_coordinates_for_courier_idle_detector': {
                'lat': 0.0,
                'lon': 0.0,
            },
            'fixed_courier_id_for_courier_idle_detector': DEFAULT_COURIER_ID,
        },
    )

    problems_count = expected_sqt_actions_count
    assert_db_problems(pgsql['eats_proactive_support'], problems_count)
    assert_db_actions(
        pgsql['eats_proactive_support'], expected_sqt_actions_count,
    )

    assert mock_eats_orders_tracking.times_called == 1
    assert mock_cargo_claims_external_performer.times_called == 1
    assert mock_cargo_claims_performer_position.times_called == 1
    assert mock_pointseta_custom_responses.times_called == 1

    assert (
        stq.eats_proactive_support_actions.times_called
        == expected_sqt_actions_count
    )
    assert (
        stq.eats_proactive_support_detections.times_called
        == expected_sqt_detections_count
    )

    if expected_sqt_detections_count != 0:
        task = stq.eats_proactive_support_detections.next_call()
        assert_new_detection_task(
            task,
            order_nr,
            fixed_eta=result_eta,
            point_id=current_point_id,
            fixed_courier_coordinates={'lat': 1.0, 'lon': 2.0},
            fixed_courier_id=DEFAULT_COURIER_ID,
        )
    if expected_sqt_actions_count != 0:
        task = stq.eats_proactive_support_actions.next_call()
        assert_new_action_task(task, order_nr)
