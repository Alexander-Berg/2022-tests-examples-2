# pylint: disable=unused-variable
import json

import pytest

from tests_eats_proactive_support import utils

DRIVER_PROFILE_RETRIEVE_URL = '/driver-profiles/v1/driver/profiles/retrieve'
PROBLEM_TYPE = 'courier_idle'
COURIER_ROBOCALL_TYPE = 'courier_robocall'
PHONE_ID = '12345'
DEFAULT_PARK_ID = '123'
DEFAULT_DRIVER_ID = '345'
DEFAULT_ORDER_NR = '100000-100000'

ACTION_TYPE = 'place_robocall'
ACTION_PAYLOAD = json.dumps({'delay_sec': 0, 'voice_line': 'dummy_voice_line'})
PLACE_ID_FOR_EATS_ROBOCALL = 41

CATALOG_STORAGE_RESPONSE_FOR_EATS_ROBOCALL = {
    'places': [
        {
            'place_id': 41,
            'created_at': '2021-01-01T09:00:00+06:00',
            'updated_at': '2021-01-01T09:00:00+06:00',
            'place': {
                'slug': 'some_slug',
                'enabled': True,
                'name': 'some_name',
                'revision': 1,
                'type': 'native',
                'business': 'restaurant',
                'launched_at': '2021-01-01T09:00:00+06:00',
                'payment_methods': ['cash', 'payture', 'taxi'],
                'gallery': [{'type': 'image', 'url': 'some_url', 'weight': 1}],
                'brand': {
                    'id': 100,
                    'slug': 'some_slug',
                    'name': 'some_brand',
                    'picture_scale_type': 'aspect_fit',
                },
                'address': {'city': 'Moscow', 'short': 'some_address'},
                'country': {
                    'id': 1,
                    'name': 'Russia',
                    'code': 'RU',
                    'currency': {'sign': 'RUB', 'code': 'RUB'},
                },
                'categories': [{'id': 1, 'name': 'some_name'}],
                'quick_filters': {
                    'general': [{'id': 1, 'slug': 'some_slug'}],
                    'wizard': [{'id': 1, 'slug': 'some_slug'}],
                },
                'region': {'id': 1, 'geobase_ids': [1], 'time_zone': 'UTC'},
                'location': {'geo_point': [52.569089, 39.60258]},
                'rating': {'users': 5.0, 'admin': 5.0, 'count': 1},
                'price_category': {'id': 1, 'name': 'some_name', 'value': 5.0},
                'extra_info': {},
                'features': {
                    'ignore_surge': False,
                    'supports_preordering': False,
                    'fast_food': False,
                },
                'timing': {
                    'preparation': 60.0,
                    'extra_preparation': 60.0,
                    'average_preparation': 60.0,
                },
                'sorting': {'weight': 5, 'popular': 5},
                'assembly_cost': 1,
                'contacts': [
                    {
                        'personal_phone_id': 'new_robocall_personal_phone_id',
                        'type': 'auto_call',
                    },
                ],
            },
        },
    ],
}


@pytest.fixture(name='mock_driver_profile_retrieve_for_eats_robocall')
def _mock_driver_profile_retrieve_for_eats_robocall(mockserver):
    @mockserver.json_handler(DRIVER_PROFILE_RETRIEVE_URL)
    def mock(request):
        return mockserver.make_response(
            status=200,
            json={
                'profiles': [
                    {
                        'park_driver_profile_id': (
                            DEFAULT_PARK_ID + '_' + DEFAULT_PARK_ID
                        ),
                        'data': {
                            'phone_pd_ids': [
                                {'pd_id': 'new_robocall_personal_phone_id'},
                            ],
                        },
                    },
                ],
            },
        )

    return mock


@pytest.mark.parametrize(
    """db_action_state,expected_action_result,
    expected_result_count,expected_exception_count,
    expected_driver_profile_called, expected_eats_robocall_called,
    eats_robocall_code, eats_robocall_response""",
    [
        (
            'created',
            'success',
            1,
            0,
            1,
            1,
            200,
            {'call_id': 'dummy_external_task_id'},
        ),  # greenflow
        (
            'created',
            'failed',
            1,
            0,
            1,
            1,
            400,
            {'code': 'dummy_error_code_400', 'message': 'dummy_message_400'},
        ),  # 400_from_robocall
        (
            'created',
            'need_retry',
            1,
            0,
            1,
            1,
            500,
            {'code': 'dummy_error_code_500', 'message': 'dummy_message_500'},
        ),  # 500_from_robocall
    ],
    ids=['greenflow', '400_from_robocall', '500_from_robocall'],
)
async def test_actions_courier_robocall_greenflow_and_robocall_errors(
        stq_runner,
        pgsql,
        testpoint,
        mock_driver_profile_retrieve_for_eats_robocall,
        db_action_state,
        expected_action_result,
        expected_result_count,
        expected_exception_count,
        expected_driver_profile_called,
        expected_eats_robocall_called,
        eats_robocall_code,
        eats_robocall_response,
        mockserver,
):
    order_nr = DEFAULT_ORDER_NR

    @mockserver.json_handler(
        '/eats-robocall/internal/eats-robocall/v1/create-call',
    )
    def _mock_eats_robocall(request):
        return mockserver.make_response(
            status=eats_robocall_code, json=eats_robocall_response,
        )

    @testpoint('eats-proactive-support-actions-actor::DoActionException')
    def _actions_actor_exception_testpoint(data):
        pass

    @testpoint('eats-proactive-support-actions-actor::DoActionResult')
    def _actions_actor_result_testpoint(action_result):
        assert action_result == expected_action_result

    await utils.db_insert_order(
        pgsql,
        order_nr,
        'cancelled',
        park_id=DEFAULT_PARK_ID,
        driver_id=DEFAULT_DRIVER_ID,
    )
    problem_id = await utils.db_insert_problem(pgsql, order_nr, PROBLEM_TYPE)

    action_type = 'courier_robocall'
    voice_line = 'dummy_voice_line'
    action_payload = json.dumps({'delay_sec': 0, 'voice_line': voice_line})
    action_id = await utils.db_insert_action(
        pgsql,
        problem_id,
        order_nr,
        action_type,
        action_payload,
        db_action_state,
    )

    await stq_runner.eats_proactive_support_actions.call(
        task_id='order_nr:' + order_nr + '_action_id:' + str(action_id),
        kwargs={
            'order_nr': order_nr,
            'action_id': action_id,
            'action_type': action_type,
        },
    )

    assert (
        _actions_actor_exception_testpoint.times_called
        == expected_exception_count
    )
    assert (
        _actions_actor_result_testpoint.times_called == expected_result_count
    )

    assert (
        mock_driver_profile_retrieve_for_eats_robocall.times_called
        == expected_driver_profile_called
    )

    assert _mock_eats_robocall.times_called == expected_eats_robocall_called
    real_communication_request = _mock_eats_robocall.next_call()[
        'request'
    ].json
    assert real_communication_request['context']['order_nr'] == order_nr
    assert real_communication_request['scenario_name'] == voice_line
    assert (
        real_communication_request['personal_phone_id']
        == 'new_robocall_personal_phone_id'
    )


@pytest.fixture(name='mock_eats_robocall_for_eater')
def _mock_eats_robocall_for_eater(mockserver):
    @mockserver.json_handler(
        '/eats-robocall/internal/eats-robocall/v1/create-call',
    )
    def mock(request):
        order_nr = request.json['context']['order_nr']
        if order_nr == '100000-100004':
            return mockserver.make_response(
                status=200, json={'call_id': 'dummy_external_task_id_2'},
            )
        if order_nr == '100000-100005':
            return mockserver.make_response(
                status=400,
                json={
                    'code': 'dummy_error_code_400',
                    'message': 'dummy_message_400',
                },
            )
        return mockserver.make_response(
            status=500,
            json={
                'code': 'dummy_error_code_500',
                'message': 'dummy_message_500',
            },
        )

    return mock


@pytest.mark.parametrize(
    """order_nr, phone_id, db_action_state,expected_action_result,
    expected_result_count,expected_exception_count""",
    [
        (
            '100000-100004',
            'new_robocall_personal_phone_id',
            'created',
            'success',
            1,
            0,
        ),
        (
            '100000-100005',
            'new_robocall_personal_phone_id',
            'created',
            'failed',
            1,
            0,
        ),
        (
            '100000-100006',
            'new_robocall_personal_phone_id',
            'created',
            'need_retry',
            1,
            0,
        ),
    ],
)
async def test_actions_eater_robocall(
        stq_runner,
        pgsql,
        testpoint,
        mock_eats_robocall_for_eater,
        order_nr,
        phone_id,
        db_action_state,
        expected_action_result,
        expected_result_count,
        expected_exception_count,
):
    @testpoint('eats-proactive-support-actions-actor::DoActionException')
    def _actions_actor_exception_testpoint(data):
        pass

    @testpoint('eats-proactive-support-actions-actor::DoActionResult')
    def _actions_actor_result_testpoint(action_result):
        assert action_result == expected_action_result

    await utils.db_insert_order(pgsql, order_nr, 'cancelled')
    await utils.db_insert_order_sensitive_data(
        pgsql, order_nr, eater_personal_phone_id=phone_id,
    )
    problem_id = await utils.db_insert_problem(
        pgsql, order_nr, 'order_cancelled',
    )

    action_type = 'eater_robocall'
    action_payload = json.dumps(
        {'delay_sec': 0, 'voice_line': 'dummy_voice_line'},
    )
    action_id = await utils.db_insert_action(
        pgsql,
        problem_id,
        order_nr,
        action_type,
        action_payload,
        db_action_state,
    )

    await stq_runner.eats_proactive_support_actions.call(
        task_id='order_nr:' + order_nr + '_action_id:' + str(action_id),
        kwargs={
            'order_nr': order_nr,
            'action_id': action_id,
            'action_type': action_type,
        },
    )

    assert (
        _actions_actor_exception_testpoint.times_called
        == expected_exception_count
    )
    assert (
        _actions_actor_result_testpoint.times_called == expected_result_count
    )


@pytest.fixture(name='mock_eats_catalog_storage')
def _mock_eats_catalog_storage(mockserver):
    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage/v1/'
        + 'search/places/list',
    )
    def mock(request):
        assert len(request.json['place_ids']) == 1
        return mockserver.make_response(
            status=200, json=CATALOG_STORAGE_RESPONSE_FOR_EATS_ROBOCALL,
        )

    return mock


@pytest.mark.parametrize(
    """order_nr,place_id,db_action_state,robocall_response_status,
    robocall_response_body,expected_stq_failed,expected_action_result,
    expected_result_count,expected_exception_count""",
    [
        (
            '100000-100004',
            PLACE_ID_FOR_EATS_ROBOCALL,
            'created',
            200,
            {'call_id': 'dummy_external_task_id_2'},
            False,
            'success',
            1,
            0,
        ),
        (
            '100000-100005',
            PLACE_ID_FOR_EATS_ROBOCALL,
            'created',
            400,
            {'code': 'dummy_error_code_400', 'message': 'dummy_message_400'},
            False,
            'failed',
            1,
            0,
        ),
        (
            '100000-100006',
            PLACE_ID_FOR_EATS_ROBOCALL,
            'created',
            500,
            {'code': 'dummy_error_code_500', 'message': 'dummy_message_500'},
            True,
            'failed',
            0,
            1,
        ),
    ],
)
async def test_actions_place_robocall(
        mockserver,
        stq_runner,
        pgsql,
        testpoint,
        mock_eats_catalog_storage,
        order_nr,
        place_id,
        db_action_state,
        robocall_response_status,
        robocall_response_body,
        expected_stq_failed,
        expected_action_result,
        expected_result_count,
        expected_exception_count,
):
    @mockserver.json_handler(
        '/eats-robocall/internal/eats-robocall/v1/create-call',
    )
    def _mock_eats_robocall(request):
        return mockserver.make_response(
            status=robocall_response_status, json=robocall_response_body,
        )

    @testpoint('eats-proactive-support-actions-actor::DoActionException')
    def _actions_actor_exception_testpoint(data):
        pass

    @testpoint('eats-proactive-support-actions-actor::DoActionResult')
    def _actions_actor_result_testpoint(action_result):
        assert action_result == expected_action_result

    await utils.db_insert_order(
        pgsql, order_nr, 'cancelled', place_id=str(place_id),
    )
    problem_id = await utils.db_insert_problem(
        pgsql, order_nr, 'order_cancelled',
    )

    action_id = await utils.db_insert_action(
        pgsql,
        problem_id,
        order_nr,
        ACTION_TYPE,
        ACTION_PAYLOAD,
        db_action_state,
    )

    await stq_runner.eats_proactive_support_actions.call(
        task_id='order_nr:' + order_nr + '_action_id:' + str(action_id),
        kwargs={
            'order_nr': order_nr,
            'action_id': action_id,
            'action_type': ACTION_TYPE,
        },
        expect_fail=expected_stq_failed,
    )

    assert (
        _actions_actor_exception_testpoint.times_called
        == expected_exception_count
    )
    assert (
        _actions_actor_result_testpoint.times_called == expected_result_count
    )
