# pylint: disable=unused-variable

import json

import pytest

from tests_eats_proactive_support import utils

ACTION_TYPE = 'place_robocall'

ACTION_PAYLOAD = json.dumps({'delay_sec': 0, 'voice_line': 'dummy_voice_line'})

PLACE_ID = 40

CATALOG_STORAGE_RESPONSE = {
    'places': [
        {
            'place_id': PLACE_ID,
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
                    {'personal_phone_id': 'phone_id_1', 'type': 'auto_call'},
                ],
            },
        },
    ],
}


@pytest.fixture(name='mock_eats_catalog_storage')
def _mock_eats_catalog_storage(mockserver):
    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage/v1/'
        + 'search/places/list',
    )
    def mock(request):
        assert len(request.json['place_ids']) == 1
        place_id = request.json['place_ids'][0]
        assert place_id == PLACE_ID
        return mockserver.make_response(
            status=200, json=CATALOG_STORAGE_RESPONSE,
        )

    return mock


@pytest.mark.parametrize(
    """order_nr,db_action_state,robocall_response_status,
    robocall_response_body,expected_stq_failed,expected_action_result,
    expected_result_count,expected_exception_count""",
    [
        (
            '100000-100004',
            'created',
            200,
            {'call_id': 'dummy_external_task_id'},
            False,
            'success',
            1,
            0,
        ),
        (
            '100000-100005',
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
        pgsql, order_nr, 'cancelled', place_id=str(PLACE_ID),
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


async def test_actions_place_robocall_wrong_action_payload(
        stq_runner, pgsql, testpoint, mock_eats_catalog_storage,
):
    @testpoint('eats-proactive-support-actions-actor::DoActionException')
    def _actions_actor_exception_testpoint(data):
        pass

    @testpoint('eats-proactive-support-actions-actor::DoActionResult')
    def _actions_actor_result_testpoint(action_result):
        assert action_result == 'failed'

    order_nr = '100000-200000'
    await utils.db_insert_order(
        pgsql, order_nr, 'cancelled', place_id=str(PLACE_ID),
    )
    problem_id = await utils.db_insert_problem(
        pgsql, order_nr, 'order_cancelled',
    )

    action_id = await utils.db_insert_action(
        pgsql,
        problem_id,
        order_nr,
        ACTION_TYPE,
        json.dumps({'invalid_payload': 'yes'}),
        'created',
    )

    await stq_runner.eats_proactive_support_actions.call(
        task_id='order_nr:' + order_nr + '_action_id:' + str(action_id),
        kwargs={
            'order_nr': order_nr,
            'action_id': action_id,
            'action_type': ACTION_TYPE,
        },
    )

    assert _actions_actor_exception_testpoint.times_called == 0
    assert _actions_actor_result_testpoint.times_called == 1
