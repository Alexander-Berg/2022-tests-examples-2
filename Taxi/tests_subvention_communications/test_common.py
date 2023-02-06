import copy
import functools
import json

import pytest

import testsuite

PG_CLUSTER = 'subvention_communications'

GET_UPDATES_TASK_NAME = 'personal_goal_updates'

PERIODIC_TASKS = {GET_UPDATES_TASK_NAME}


class _DoesntMatterType:
    def __eq__(self, other):
        return True


# Use this value to skip checking some value
DOESNT_MATTER = _DoesntMatterType()


def suspend_periodic_tasks(func):
    @pytest.mark.suspend_periodic_tasks(*PERIODIC_TASKS)
    @functools.wraps(func)
    async def wrapped(*args, **kwargs):
        return await func(*args, **kwargs)

    return wrapped


async def run_personal_goal_updates_task_once(  # pylint: disable=C0103
        service,
):
    await service.run_periodic_task(GET_UPDATES_TASK_NAME)


def extract_all_requests(handler):
    calls = []
    while True:
        try:
            calls.append(handler.next_call()['request'])
        except testsuite.utils.callinfo.CallQueueEmptyError:
            break
    return calls


def extract_all_bodies(handler):
    return [call.json for call in extract_all_requests(handler)]


def check_handler(handler, expected_calls, expected_request=None):
    assert handler.times_called == expected_calls
    if not expected_calls:
        return None
    request = handler.next_call()['request'].json
    if expected_request is not None:
        assert request == expected_request
    return request


async def check_and_process_queue(stq, stq_runner, kwargs, expect_fail=False):
    assert stq.subvention_communications.times_called == 1
    next_call = stq.subvention_communications.next_call()
    next_call_kwargs = json.loads(next_call['kwargs']['rule_data'])
    assert all(next_call_kwargs[key] == data for key, data in kwargs.items())
    await stq_runner.subvention_communications.call(
        task_id=next_call['id'],
        args=[],
        kwargs=next_call['kwargs'],
        expect_fail=expect_fail,
    )


def create_config(rule_type, action_type, notifications):
    default_config = {
        'driver_fix': {
            'fraud': [],
            'pay': [],
            'new': [],
            'sms_settings': {
                'intent': 'driver_fix_subventions',
                'sender': 'go',
            },
        },
        'nmfg': {'fraud': [], 'pay': [], 'new': []},
        'geobooking': {'fraud': [], 'pay': [], 'new': []},
        'personal_goals': {
            'fraud': [],
            'pay': [],
            'new': [],
            'sms_settings': {'intent': 'personal_goal_new', 'sender': 'go'},
        },
    }
    res = copy.deepcopy(default_config)
    res[rule_type][action_type] = notifications
    return res


def create_nmfg_rule():
    return {
        'currency': 'RUB',
        'cursor': '2999-12-31T21:00:00.000000+00:00/5b9be1d3f7a16f1ae64f77f7',
        'driver_points': 51,
        'end': '2999-12-31T21:00:00.000000+00:00',
        'hours': [],
        'is_personal': False,
        'log': [],
        'order_payment_type': None,
        'start': '2018-09-12T21:00:00.000000+00:00',
        'status': 'enabled',
        'subvention_rule_id': '_id/1',
        'tags': [],
        'tariff_zones': ['moscow'],
        'taximeter_daily_guarantee_tag': '',
        'taxirate': '',
        'time_zone': {'id': 'Europe/Moscow', 'offset': '+03:00'},
        'trips_bounds': [
            {'bonus_amount': '1000', 'lower_bound': 10, 'upper_bound': 19},
            {'bonus_amount': '2200', 'lower_bound': 20, 'upper_bound': 29},
            {'bonus_amount': '3300', 'lower_bound': 30},
        ],
        'type': 'daily_guarantee',
        'updated': '2018-09-12T21:00:00.000000+00:00',
        'visible_to_driver': True,
        'week_days': ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
    }


def make_billing_doc(support_info):
    return {
        'doc_id': 1,
        'kind': 'kind',
        'topic': 'topc',
        'external_ref': 'external_ref',
        'event_at': '2020-02-02T00:00:00+00:00',
        'process_at': '2020-02-02T00:00:00+00:00',
        'service': 'service',
        'created': '2020-02-02T00:00:00+00:00',
        'status': 'complete',
        'tags': ['tag'],
        'data': support_info,
    }


def make_money_params(money_with_sign):
    money, sign = money_with_sign.split(' ')
    return {
        'key': 'subventions.rule_sum',
        'keyset': 'taximeter_messages',
        'params': {'currency_sign': sign, 'sum': money},
    }


def _time_key(minutes, hours):
    if minutes and hours:
        return 'subventions.exact_time_hours_minutes'
    if not minutes:
        return 'subventions.exact_time_hours'
    return 'subventions.exact_time'


def make_time_args(minutes=None, hours=None):
    res = {
        'key': _time_key(minutes=minutes, hours=hours),
        'keyset': 'taximeter_messages',
        'params': {},
    }
    if minutes:
        res['params']['minutes'] = minutes
    if hours:
        res['params']['hours'] = hours
    return res
