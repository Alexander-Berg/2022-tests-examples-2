from pytest import mark
import json
import pytest

from callcenter_etl.layer.yt.ods.asterisk.ivr_action.impl import get_numbers, get_user_text


@mark.parametrize(
    "raw_json, expected_result", [
        pytest.param(
            {
                'worker_name': 'after_disp_call_flow',
                'action_type': 'ask_result',
                'action_kwargs': json.dumps({'user_input': 'DIGIT: 1'})
            },
            '1'
        ),
        pytest.param(
            {
                'worker_name': 'after_disp_call_flow',
                'action_type': 'ask_result',
                'action_kwargs': json.dumps({'user_input': 'да да да я тут'})
            },
            None
        ),
        pytest.param(
            {
                'worker_name': 'after_disp_call_flow',
                'action_type': 'ask_result',
                'action_kwargs': json.dumps({})
            },
            None
        ),
        pytest.param(
            {
                'worker_name': 'order_status_worker_2_0',
                'action_type': 'input_result',
                'action_kwargs': json.dumps({'numbers': '3', 'kwargs': {'numbers': '0'}})
            },
            '3'
        ),
        pytest.param(
            {
                'worker_name': 'order_status_worker',
                'action_type': 'input_completed',
                'action_kwargs': json.dumps({'kwargs': {'numbers': '0'}})
            },
            '0'
        ),
        pytest.param(
            {
                'worker_name': 'order_status_worker',
                'action_type': 'input_completed',
                'action_kwargs': json.dumps({})
            },
            None
        )
    ]
)
def test_get_numbers(raw_json, expected_result):
    actual_result = get_numbers(raw_json)
    assert actual_result == expected_result


@mark.parametrize(
    "raw_json, expected_result", [
        pytest.param(
            {
                'worker_name': 'after_disp_call_flow',
                'action_type': 'ask_result',
                'action_kwargs': json.dumps({'user_input': 'DIGIT: 1'})
            },
            None
        ),
        pytest.param(
            {
                'worker_name': 'after_disp_call_flow',
                'action_type': 'ask_result',
                'action_kwargs': json.dumps({'user_input': 'да да да я тут'})
            },
            'да да да я тут'
        ),
        pytest.param(
            {
                'worker_name': 'after_disp_call_flow',
                'action_type': 'input_completed',
                'action_kwargs': json.dumps({})
            },
            None
        ),
    ]
)
def test_get_user_text(raw_json, expected_result):
    actual_result = get_user_text(raw_json)
    assert actual_result == expected_result
