import copy


import pytest

from . import conftest


@pytest.fixture(name='mock_order_core')
def _mock_order_core(mockserver):
    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def mock(request):
        fields = [
            'order.application',
            'order.device_id',
            'order.user_agent',
            'order.nz',
            'order.calc_method',
            'order.feedback.rating',
            'order.personal_phone_id',
            'order.user_id',
            'order.user_uid',
            'order.coupon',
            'order_info.statistics.status_updates.q',
            'order_info.statistics.status_updates.c',
            'order_info.statistics.status_updates.s',
            'order_info.statistics.status_updates.t',
            'order_info.statistics.status_updates.d',
            'order_info.statistics.status_updates.i',
            'candidates.metrica_device_id',
            'candidates.driver_license',
            'candidates.driver_license_personal_id',
            'candidates.tags',
            'candidates.point',
            'performer.candidate_index',
        ]
        fields.sort()
        assert request.json == {
            'order_id': 'taxi_order_id_1',
            'require_latest': True,
            'fields': fields,
            'lookup_flags': 'none',
            'search_archive': False,
        }

        return mockserver.make_response(
            json={
                'order_id': 'taxi_order_id_1',
                'replica': 'master',
                'version': '1',
                'fields': {
                    'order': {
                        'application': 'cargo',
                        'device_id': 'user_device_id',
                        'user_agent': 'agent',
                        'nz': 'moscow',
                        'calc_method': 'some_method',
                        'feedback': {'rating': '5.0'},
                        'user_id': 'user_id',
                        'user_uid': 'user_uid',
                        'personal_phone_id': '+700000000001_pd',
                        'coupon': {
                            'percent': 50,
                            'limit': 1000000.0,
                            'series': 'coupon',
                            'value': 1000000.0,
                            'id': 'coupon1304',
                            'was_used': True,
                        },
                    },
                    'candidates': [
                        {
                            'metrica_device_id': 'driver_device_id',
                            'driver_license': 'license',
                            'driver_license_personal_id': 'license_id',
                            'tags': ['first', 'second'],
                            'point': [37.623945, 55.681219],
                        },
                    ],
                    'performer': {'candidate_index': 0},
                    'order_info': {
                        'statistics': {
                            'status_updates': [
                                {
                                    'q': 'create',
                                    'c': '2022-06-20T12:08:36.434+00:00',
                                    's': 'pending',
                                },
                                {
                                    'c': '2022-06-20T12:10:27.128+00:00',
                                    'q': 'new_driver_found',
                                },
                                {
                                    'c': '2022-06-20T12:10:28.426+00:00',
                                    'd': [37.567533, 55.725555],
                                    'q': 'seen_received',
                                    'i': 0,
                                },
                                {
                                    'c': '2022-06-20T12:10:29.125+00:00',
                                    'd': [37.567531, 55.725554],
                                    'q': 'seen',
                                    'i': 0,
                                },
                                {
                                    'c': '2022-06-20T12:10:31.572+00:00',
                                    's': 'assigned',
                                    'q': 'requestconfirm_assigned',
                                    'i': 0,
                                },
                                {
                                    'd': [37.567531, 55.72556],
                                    't': 'driving',
                                    'c': '2022-06-20T12:10:31.572+00:00',
                                    'q': 'requestconfirm_driving',
                                    'i': 0,
                                },
                                {
                                    'd': [37.567531, 55.72556],
                                    't': 'waiting',
                                    'c': '2022-06-20T12:10:32.339+00:00',
                                    'q': 'requestconfirm_waiting',
                                    'i': 0,
                                },
                                {
                                    'c': '2022-06-20T12:10:32.894+00:00',
                                    'q': 'destinations_changed',
                                },
                                {
                                    'd': [37.567534, 55.725555],
                                    't': 'transporting',
                                    'c': '2022-06-20T12:11:47.155+00:00',
                                    'q': 'requestconfirm_transporting',
                                    'i': 0,
                                },
                                {
                                    'c': '2022-06-20T12:11:47.336+00:00',
                                    'q': 'destinations_changed',
                                },
                                {
                                    'c': '2022-06-20T12:13:44.753+00:00',
                                    'q': 'destinations_changed',
                                },
                                {
                                    'q': 'requestconfirm_complete',
                                    'c': '2022-06-20T12:13:46.386+00:00',
                                    't': 'complete',
                                    's': 'finished',
                                    'd': [37.567532, 55.725575],
                                    'i': 0,
                                },
                            ],
                        },
                    },
                },
            },
            status=200,
        )

    return mock


@pytest.fixture(name='mock_order_core_failed')
def _mock_order_core_failed(mockserver):
    def mock_core(code=500):
        @mockserver.json_handler('/order-core/v1/tc/order-fields')
        def mock(request):
            return mockserver.make_response(status=code)

        return mock

    return mock_core


@pytest.fixture(name='default_calc_response_v2', autouse=True)
def _default_calc_response_v2(testpoint):
    return {
        'calculations': [
            {
                'calc_id': 'cargo-pricing/v1/01234567890123456789012345678912',
                'result': {
                    'calc_id': (
                        'cargo-pricing/v1/01234567890123456789012345678912'
                    ),
                    'prices': {
                        'total_price': '200.999',
                        'source_waiting_price_per_unit': '5',
                        'destination_waiting_price_per_unit': '10',
                    },
                    'details': {
                        'algorithm': {'pricing_case': 'default'},
                        'currency': {'code': 'RUB'},
                        'services': [],
                        'waypoints': [
                            {
                                'type': 'pickup',
                                'position': [
                                    37.58505871591705,
                                    55.75112587081837,
                                ],
                                'waiting': {
                                    'total_waiting': '0',
                                    'paid_waiting': '0',
                                    'free_waiting_time': '300',
                                    'was_limited': False,
                                    'paid_waiting_disabled': False,
                                },
                                'route': {
                                    'time_from_start': '0',
                                    'distance_from_start': '0',
                                },
                                'cargo_items': [],
                            },
                            {
                                'type': 'dropoff',
                                'position': [
                                    37.58574980969229,
                                    55.75155701795171,
                                ],
                                'waiting': {
                                    'total_waiting': '10',
                                    'paid_waiting': '0',
                                    'free_waiting_time': '600',
                                    'was_limited': False,
                                    'paid_waiting_disabled': False,
                                },
                                'route': {
                                    'time_from_start': '74.800003',
                                    'distance_from_start': '67.742577',
                                },
                                'cargo_items': [],
                            },
                        ],
                    },
                    'cancel_options': {},
                    'diagnostics': {},
                },
            },
            {
                'calc_id': 'cargo-pricing/v1/98765432100123456789012345678912',
                'result': {
                    'calc_id': (
                        'cargo-pricing/v1/98765432100123456789012345678912'
                    ),
                    'prices': {
                        'total_price': '200.999',
                        'source_waiting_price_per_unit': '5',
                        'destination_waiting_price_per_unit': '10',
                    },
                    'details': {
                        'algorithm': {'pricing_case': 'default'},
                        'currency': {'code': 'RUB'},
                        'services': [],
                        'waypoints': [
                            {
                                'type': 'pickup',
                                'position': [
                                    37.58505871591705,
                                    55.75112587081837,
                                ],
                                'waiting': {
                                    'total_waiting': '0',
                                    'paid_waiting': '0',
                                    'free_waiting_time': '300',
                                    'was_limited': False,
                                    'paid_waiting_disabled': False,
                                },
                                'route': {
                                    'time_from_start': '0',
                                    'distance_from_start': '0',
                                },
                                'cargo_items': [],
                            },
                            {
                                'type': 'dropoff',
                                'position': [
                                    37.58574980969229,
                                    55.75155701795171,
                                ],
                                'waiting': {
                                    'total_waiting': '10',
                                    'paid_waiting': '0',
                                    'free_waiting_time': '600',
                                    'was_limited': False,
                                    'paid_waiting_disabled': False,
                                },
                                'route': {
                                    'time_from_start': '74.800003',
                                    'distance_from_start': '67.742577',
                                },
                                'cargo_items': [],
                            },
                        ],
                    },
                    'cancel_options': {},
                    'diagnostics': {},
                },
            },
        ],
    }


@pytest.fixture(name='mock_calc_retrieve')
def _mock_calc_retrieve(mockserver, default_calc_response_v2):
    @mockserver.json_handler('/cargo-pricing/v2/taxi/calc/retrieve')
    def mock(request):
        assert request.json == {
            'calc_ids': [
                'cargo-pricing/v1/01234567890123456789012345678912',
                'cargo-pricing/v1/98765432100123456789012345678912',
            ],
            'reading_mode': 'master',
        }
        resp = copy.deepcopy(default_calc_response_v2)
        return resp

    return mock


@pytest.fixture(name='custom_mock_calc_retrieve')
def _custom_mock_calc_retrieve(mockserver, default_calc_response_v2):
    def custom_mock(plan_id, final_id):
        @mockserver.json_handler('/cargo-pricing/v2/taxi/calc/retrieve')
        def mock(request):
            calc_ids = [plan_id, final_id]
            calc_ids.remove(conftest.NO_PRICING_CALC_ID)
            calc_ids.sort()
            assert request.json == {
                'calc_ids': calc_ids,
                'reading_mode': 'master',
            }
            resp = copy.deepcopy(default_calc_response_v2)
            return resp

        return mock

    return custom_mock


@pytest.fixture(name='mock_calc_retrieve_failed')
def _mock_calc_retrieve_failed(mockserver, default_calc_response_v2):
    def mock(code=500):
        @mockserver.json_handler('/cargo-pricing/v2/taxi/calc/retrieve')
        def _mock(request, code=code):
            return mockserver.make_response(status=code)

        return _mock

    return mock


@pytest.fixture(name='set_calc_ids')
def _set_calc_ids(mockserver, pgsql):
    def mock(
            claim_uuid,
            plan_taxi_offer_id='cargo-pricing'
            '/v1/01234567890123456789012345678912',
            final_taxi_offer_id='cargo-pricing'
            '/v1/98765432100123456789012345678912',
            status='delivered',
            final_price=0,
    ):
        cursor = pgsql['cargo_claims'].conn.cursor()
        cursor.execute(
            'UPDATE cargo_claims.claim_estimating_results '
            f'SET taxi_offer_id=\'{plan_taxi_offer_id}\''
            f'WHERE claim_uuid = \'{claim_uuid}\'',
        )

        cursor.execute(
            'UPDATE cargo_claims.claims '
            f'SET final_pricing_calc_id=\'{final_taxi_offer_id}\', '
            f'status=\'{status}\', '
            f'final_price={final_price} '
            f'WHERE uuid_id = \'{claim_uuid}\'',
        )

    return mock


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_info_to_logbroker_stq_settings',
    consumers=['cargo-claims/claim-status'],
    clauses=[],
    default_value={'enabled': True},
    is_config=True,
)
@pytest.mark.parametrize(
    'current_status', ['delivered_finish', 'returned_finish'],
)
async def test_stq_happy_path(
        testpoint,
        state_controller,
        stq_runner,
        mock_order_core,
        set_calc_ids,
        mock_calc_retrieve,
        current_status: str,
        plan_taxi_offer_id='cargo-pricing'
        '/v1/01234567890123456789012345678912',
        final_taxi_offer_id='cargo-pricing'
        '/v1/98765432100123456789012345678912',
):
    @testpoint('logbroker_publish')
    def commit(data):
        assert data['name'] == 'events_log'
        assert '"claim":' in data['data']
        assert '"plan_pricing_info":' in data['data']
        assert '"final_pricing_info":' in data['data']
        assert '"application":' in data['data']
        assert '"performer_info":' in data['data']
        assert '"user_info":' in data['data']
        assert '"coupon_info":' in data['data']
        assert '"order_status_info"' in data['data']

    claim_info = await state_controller.apply(target_status=current_status)
    claim_uuid = claim_info.claim_id

    set_calc_ids(
        claim_uuid, plan_taxi_offer_id, final_taxi_offer_id, current_status,
    )

    await stq_runner.cargo_claims_info_to_logbroker.call(
        task_id=claim_uuid,
        args=[claim_uuid, current_status],
        expect_fail=False,
    )
    assert mock_order_core.times_called == 1
    assert mock_calc_retrieve.times_called == 1
    await commit.wait_call()


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_info_to_logbroker_stq_settings',
    consumers=['cargo-claims/claim-status'],
    clauses=[],
    default_value={'enabled': False},
    is_config=True,
)
@pytest.mark.parametrize('current_status', ['delivered_finish'])
async def test_stq_disabled(
        testpoint,
        state_controller,
        stq_runner,
        mock_order_core,
        mock_calc_retrieve,
        current_status: str,
):
    @testpoint('logbroker_publish')
    def commit(data):
        assert False

    @testpoint('config_disabled')
    def config_disabled(data):
        pass

    claim_info = await state_controller.apply(target_status=current_status)
    claim_uuid = claim_info.claim_id

    await stq_runner.cargo_claims_info_to_logbroker.call(
        task_id=claim_uuid,
        args=[claim_uuid, current_status],
        expect_fail=False,
    )
    assert mock_order_core.times_called == 0
    assert mock_calc_retrieve.times_called == 0
    assert commit.times_called == 0
    assert config_disabled.times_called == 1


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_info_to_logbroker_stq_settings',
    consumers=['cargo-claims/claim-status'],
    clauses=[],
    default_value={'enabled': True},
    is_config=True,
)
@pytest.mark.parametrize('current_status', ['delivered_finish'])
async def test_stq_exec_tries(
        testpoint,
        state_controller,
        stq_runner,
        mock_order_core,
        mock_calc_retrieve,
        current_status: str,
):
    @testpoint('logbroker_publish')
    def commit(data):
        assert False

    @testpoint('max_attempts_executed')
    def max_attempts(data):
        pass

    claim_info = await state_controller.apply(target_status=current_status)
    claim_uuid = claim_info.claim_id

    await stq_runner.cargo_claims_info_to_logbroker.call(
        task_id=claim_uuid,
        args=[claim_uuid, current_status],
        expect_fail=False,
        exec_tries=1,
    )
    assert mock_order_core.times_called == 0
    assert mock_calc_retrieve.times_called == 0
    assert commit.times_called == 0
    assert max_attempts.times_called == 1


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_info_to_logbroker_stq_settings',
    consumers=['cargo-claims/claim-status'],
    clauses=[],
    default_value={
        'enabled': True,
        'force_reschedule_on_stq_start_settings': {
            'enabled': True,
            'reschedule_delay_ms': 1000,
        },
    },
    is_config=True,
)
@pytest.mark.parametrize('current_status', ['delivered_finish'])
async def test_stq_force_reschedule(
        testpoint,
        state_controller,
        stq_runner,
        mock_order_core,
        mock_calc_retrieve,
        current_status: str,
):
    @testpoint('logbroker_publish')
    def commit(data):
        assert False

    @testpoint('reschedule_task')
    def reschedule_task(data):
        pass

    claim_info = await state_controller.apply(target_status=current_status)
    claim_uuid = claim_info.claim_id

    await stq_runner.cargo_claims_info_to_logbroker.call(
        task_id=claim_uuid,
        args=[claim_uuid, current_status],
        expect_fail=False,
    )
    assert mock_order_core.times_called == 0
    assert mock_calc_retrieve.times_called == 0
    assert commit.times_called == 0
    assert reschedule_task.times_called == 1


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_info_to_logbroker_stq_settings',
    consumers=['cargo-claims/claim-status'],
    clauses=[],
    default_value={'enabled': True},
    is_config=True,
)
@pytest.mark.parametrize('current_status', ['delivered_finish'])
@pytest.mark.parametrize('pricing_code', [500])
async def test_stq_pricing_failed(
        testpoint,
        state_controller,
        stq_runner,
        mock_order_core,
        mock_calc_retrieve_failed,
        set_calc_ids,
        current_status: str,
        pricing_code,
        plan_taxi_offer_id='cargo-pricing'
        '/v1/01234567890123456789012345678912',
        final_taxi_offer_id='cargo-pricing'
        '/v1/98765432100123456789012345678912',
):
    mock_calc = mock_calc_retrieve_failed(code=pricing_code)

    @testpoint('logbroker_publish')
    def commit(data):
        assert 'plan_pricing_info' not in data['data']
        assert 'final_pricing_info' not in data['data']

    claim_info = await state_controller.apply(target_status=current_status)
    claim_uuid = claim_info.claim_id

    set_calc_ids(
        claim_uuid, plan_taxi_offer_id, final_taxi_offer_id, current_status,
    )

    await stq_runner.cargo_claims_info_to_logbroker.call(
        task_id=claim_uuid,
        args=[claim_uuid, current_status],
        expect_fail=False,
    )
    assert mock_order_core.times_called == 1
    assert mock_calc.times_called == 1
    await commit.wait_call()


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_info_to_logbroker_stq_settings',
    consumers=['cargo-claims/claim-status'],
    clauses=[],
    default_value={'enabled': True},
    is_config=True,
)
@pytest.mark.parametrize('current_status', ['delivered_finish'])
@pytest.mark.parametrize(
    'plan_id, final_id',
    [
        [
            'cargo-pricing/v1/01234567890123456789012345678912',
            conftest.NO_PRICING_CALC_ID,
        ],
        [
            conftest.NO_PRICING_CALC_ID,
            'cargo-pricing/v1/98765432100123456789012345678912',
        ],
        [conftest.NO_PRICING_CALC_ID, conftest.NO_PRICING_CALC_ID],
    ],
)
async def test_stq_no_pricing(
        testpoint,
        state_controller,
        stq_runner,
        mock_order_core,
        custom_mock_calc_retrieve,
        set_calc_ids,
        current_status: str,
        plan_id,
        final_id,
):
    custom_mock_calc = custom_mock_calc_retrieve(plan_id, final_id)
    empty_pricing_details = (
        plan_id == conftest.NO_PRICING_CALC_ID
        and final_id == conftest.NO_PRICING_CALC_ID
    )

    @testpoint('empty_pricing_details')
    def empty_pricing(data):
        pass

    @testpoint('logbroker_publish')
    def commit(data):
        if empty_pricing_details:
            assert 'plan_pricing_info' not in data['data']
            assert 'final_pricing_info' not in data['data']
        else:
            assert 'plan_pricing_info' in data['data']
            assert 'final_pricing_info' in data['data']

    claim_info = await state_controller.apply(target_status=current_status)
    claim_uuid = claim_info.claim_id

    set_calc_ids(claim_uuid, plan_id, final_id, current_status)

    await stq_runner.cargo_claims_info_to_logbroker.call(
        task_id=claim_uuid,
        args=[claim_uuid, current_status],
        expect_fail=False,
    )
    assert mock_order_core.times_called == 1
    assert custom_mock_calc.times_called == 0 if empty_pricing_details else 1
    assert empty_pricing.times_called == 0 if empty_pricing_details else 1
    await commit.wait_call()


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_info_to_logbroker_stq_settings',
    consumers=['cargo-claims/claim-status'],
    clauses=[],
    default_value={'enabled': True},
    is_config=True,
)
@pytest.mark.parametrize('current_status', ['delivered_finish'])
@pytest.mark.parametrize('order_core_status', [400, 404, 500])
async def test_stq_no_order_core(
        testpoint,
        state_controller,
        stq_runner,
        mock_order_core_failed,
        mock_calc_retrieve,
        set_calc_ids,
        current_status: str,
        order_core_status,
):
    custom_mock = mock_order_core_failed(code=order_core_status)

    @testpoint('logbroker_publish')
    def commit(data):
        assert 'application' not in data['data']
        assert 'user_agent' not in data['data']

    claim_info = await state_controller.apply(target_status=current_status)
    claim_uuid = claim_info.claim_id

    set_calc_ids(claim_uuid, status=current_status)

    await stq_runner.cargo_claims_info_to_logbroker.call(
        task_id=claim_uuid,
        args=[claim_uuid, current_status],
        expect_fail=False,
    )
    assert custom_mock.times_called == 1
    assert mock_calc_retrieve.times_called == 1
    await commit.wait_call()
