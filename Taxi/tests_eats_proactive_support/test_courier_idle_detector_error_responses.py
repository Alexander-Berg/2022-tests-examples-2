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
                'visit_order': 3,
                'visit_status': 'arrived',
                'visited_at': {'expected': '2019-04-28T12:20:00+03:00'},
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
                'visit_order': 1,
                'visit_status': status,
                'visited_at': {'expected': eta},
            },
        ],
        'performer_position': [37.8, 55.4],
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


def assert_new_detection_task(
        task,
        order_nr,
        fixed_eta=None,
        point_id=None,
        fixed_start_idle_time=None,
        fixed_courier_coordinates=None,
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
async def test_courier_idle_detector_tracking_400(
        stq_runner, mockserver, pgsql, stq,
):
    @mockserver.json_handler(TRACKING_URL)
    def mock_eats_orders_tracking_400(request):
        return mockserver.make_response(
            status=400,
            json={
                'code': 'NOT_FOUND_COURIER_DATA',
                'message': 'not found courier data',
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

    assert mock_eats_orders_tracking_400.times_called == 1
    assert stq.eats_proactive_support_actions.times_called == 0
    assert stq.eats_proactive_support_detections.times_called == 1


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@COURIER_IDLE_EXP
@pytest.mark.now('2020-04-28T11:50:00+03:00')
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
async def test_courier_idle_detector_tracking_500(
        stq_runner, mockserver, pgsql, stq,
):
    @mockserver.json_handler(TRACKING_URL)
    def mock_eats_orders_tracking_500(request):
        return mockserver.make_response(
            status=500,
            json={'code': 'some_problem', 'message': 'some_problem'},
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

    assert mock_eats_orders_tracking_500.times_called == 1
    assert stq.eats_proactive_support_actions.times_called == 0
    assert stq.eats_proactive_support_detections.times_called == 0


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@COURIER_IDLE_EXP
@pytest.mark.now('2020-04-28T11:50:00+03:00')
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
async def test_courier_idle_detector_external_performer_404(
        stq_runner, mockserver, pgsql, stq, mock_eats_orders_tracking,
):
    @mockserver.json_handler(CARGO_EXTERNAL_PERFORMER_URL)
    def mock_external_performer_404(request):
        return mockserver.make_response(
            status=404, json={'code': 'not_found', 'message': 'some_message'},
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
    assert mock_external_performer_404.times_called == 1

    assert stq.eats_proactive_support_actions.times_called == 0
    assert stq.eats_proactive_support_detections.times_called == 0


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@COURIER_IDLE_EXP
@pytest.mark.now('2020-04-28T11:50:00+03:00')
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
async def test_courier_idle_detector_external_performer_500(
        stq_runner, mockserver, pgsql, stq, mock_eats_orders_tracking,
):
    @mockserver.json_handler(CARGO_EXTERNAL_PERFORMER_URL)
    def mock_external_performer_500(request):
        return mockserver.make_response(
            status=500, json={'code': 'db_problem', 'message': 'some_message'},
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
    assert mock_external_performer_500.times_called == 3

    assert stq.eats_proactive_support_actions.times_called == 0
    assert stq.eats_proactive_support_detections.times_called == 0


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@COURIER_IDLE_EXP
@pytest.mark.now('2020-04-28T11:50:00+03:00')
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
async def test_courier_idle_detector_performer_position_404(
        stq_runner,
        mockserver,
        pgsql,
        stq,
        mock_eats_orders_tracking,
        mock_cargo_claims_external_performer,
):
    @mockserver.json_handler(CARGO_PERFORMER_POSITION_URL)
    def mock_performer_position_404(request):
        return mockserver.make_response(
            status=404, json={'code': 'not_found', 'message': 'some_message'},
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
    assert mock_performer_position_404.times_called == 1

    assert stq.eats_proactive_support_actions.times_called == 0
    assert stq.eats_proactive_support_detections.times_called == 1

    task = stq.eats_proactive_support_detections.next_call()
    assert_new_detection_task(task, order_nr)


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@COURIER_IDLE_EXP
@pytest.mark.now('2020-04-28T11:50:00+03:00')
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
async def test_courier_idle_detector_performer_position_409(
        stq_runner,
        mockserver,
        pgsql,
        stq,
        mock_eats_orders_tracking,
        mock_cargo_claims_external_performer,
):
    @mockserver.json_handler(CARGO_PERFORMER_POSITION_URL)
    def mock_performer_position_409(request):
        return mockserver.make_response(
            status=409, json={'code': 'not_found', 'message': 'some_message'},
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
    assert mock_performer_position_409.times_called == 1

    assert stq.eats_proactive_support_actions.times_called == 0
    assert stq.eats_proactive_support_detections.times_called == 1

    task = stq.eats_proactive_support_detections.next_call()
    assert_new_detection_task(task, order_nr)


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@COURIER_IDLE_EXP
@pytest.mark.now('2020-04-28T11:50:00+03:00')
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
async def test_courier_idle_detector_performer_position_500(
        stq_runner,
        mockserver,
        pgsql,
        stq,
        mock_eats_orders_tracking,
        mock_cargo_claims_external_performer,
):
    @mockserver.json_handler(CARGO_PERFORMER_POSITION_URL)
    def mock_performer_position_500(request):
        return mockserver.make_response(
            status=500, json={'code': 'db_error', 'message': 'some_message'},
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
    assert mock_performer_position_500.times_called == 3

    assert stq.eats_proactive_support_actions.times_called == 0
    assert stq.eats_proactive_support_detections.times_called == 0


@pytest.mark.parametrize(
    """code_409, expected_stq_detections_count""",
    [
        ('no_performer_info', 0),
        ('inappropriate_status', 0),
        ('unknown_performer_position', 1),
        ('not_found', 0),
    ],
    ids=[
        'points_eta_no_performer_info',
        'points_eta_inappropriate_status',
        'points_eta_unknown_performer_position',
        'points_eta_not_found',
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
@pytest.mark.now('2020-04-28T11:50:00+03:00')
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.now('2020-04-28T11:50:00+03:00')
async def test_courier_idle_detector_points_eta_409(
        stq_runner,
        mockserver,
        pgsql,
        stq,
        mock_eats_orders_tracking,
        mock_cargo_claims_external_performer,
        mock_cargo_claims_performer_position,
        code_409,
        expected_stq_detections_count,
):
    @mockserver.json_handler(CARGO_POINTS_ETA_URL)
    def mock_points_eta_409(request):
        return mockserver.make_response(
            status=409, json={'code': code_409, 'message': 'some_message'},
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
    assert mock_cargo_claims_performer_position.times_called == 1
    assert mock_points_eta_409.times_called == 1

    assert stq.eats_proactive_support_actions.times_called == 0
    assert (
        stq.eats_proactive_support_detections.times_called
        == expected_stq_detections_count
    )
    if expected_stq_detections_count != 0:
        task = stq.eats_proactive_support_detections.next_call()
        assert_new_detection_task(task, order_nr)


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
async def test_courier_idle_detector_points_eta_500(
        stq_runner,
        mockserver,
        pgsql,
        stq,
        mock_eats_orders_tracking,
        mock_cargo_claims_external_performer,
        mock_cargo_claims_performer_position,
):
    @mockserver.json_handler(CARGO_POINTS_ETA_URL)
    def mock_points_eta_500(request):
        return mockserver.make_response(
            status=500, json={'code': 'db_error', 'message': 'some_message'},
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
    assert mock_cargo_claims_performer_position.times_called == 1
    assert mock_points_eta_500.times_called == 3

    assert stq.eats_proactive_support_actions.times_called == 0
    assert stq.eats_proactive_support_detections.times_called == 0
