import dataclasses


import pytest

from . import test_common


@dataclasses.dataclass
class PayInfo:
    time_args: dict = dataclasses.field(default_factory=dict)
    income: dict = dataclasses.field(default_factory=dict)
    bonus: dict = dataclasses.field(default_factory=dict)
    guarantee: dict = dataclasses.field(default_factory=dict)


def _params(pay_info):
    params = {
        'day': '28',
        'month': {'keyset': 'notify', 'key': 'helpers.month_4_part'},
        'income': pay_info.income,
        'time_on_line': pay_info.time_args,
        'guarantee': pay_info.guarantee,
    }
    if pay_info.bonus:
        params['bonus'] = pay_info.bonus

    return params


def _key(pay_info):
    return (
        'subvention_communications.geobooking.bonus'
        if pay_info.bonus
        else 'subvention_communications.geobooking.guarantee_exceeded'
    )


def _check_driver_wall_handler(driver_wall_handler, expected_calls, pay_info):
    expected_request = {
        'id': 'abcd1234abcd',
        'template': {
            'title': {
                'keyset': 'taximeter_messages',
                'key': 'subvention_communications.geobooking.wall_title',
            },
            'text': {
                'keyset': 'taximeter_messages',
                'key': _key(pay_info),
                'params': _params(pay_info),
            },
            'type': 'newsletter',
            'alert': False,
        },
        'filters': {'drivers': ['dbid1_uuid1', 'dbid2_uuid2']},
    }
    test_common.check_handler(
        driver_wall_handler, expected_calls, expected_request,
    )


def _check_driver_push_handler(driver_push_handler, expected_calls, pay_info):
    expected_request = {
        'data': {
            'text': {
                'keyset': 'taximeter_messages',
                'key': _key(pay_info),
                'params': _params(pay_info),
            },
        },
        'code': 1300,
        'action': 'MessageNew',
        'drivers': [
            {'dbid': 'dbid1', 'uuid': 'uuid1'},
            {'dbid': 'dbid2', 'uuid': 'uuid2'},
        ],
    }
    test_common.check_handler(
        driver_push_handler, expected_calls, expected_request,
    )


def _create_geobooking_rule():
    return {
        'currency': 'RUB',
        'cursor': '1',
        'end': '2019-05-04T11:30:00+0300',
        'geoareas': ['subv_zone1'],
        'hours': [],
        'is_personal': False,
        'is_relaxed_income_matching': False,
        'is_relaxed_order_time_matching': False,
        'log': [],
        'min_online_minutes': 0,
        'payment_type': 'add',
        'profile_payment_type_restrictions': 'none',
        'rate_free_per_minute': '1.23',
        'rate_on_order_per_minute': '1.23',
        'start': '2019-04-04T12:00:00+0300',
        'status': 'enabled',
        'subvention_rule_id': '_id/1',
        'tags': ['tag1'],
        'tariff_zones': ['moscow'],
        'taxirate': 'TAXIRATE-21',
        'time_zone': {'id': 'Europe/Moscow', 'offset': '+03'},
        'type': 'geo_booking',
        'updated': '2018-08-01T12:59:23.231000+00:00',
        'visible_to_driver': True,
        'week_days': ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
        'workshift': {'end': '18:00', 'start': '08:00'},
    }


@pytest.mark.parametrize(
    'notifications', (['wall'], ['push'], ['push', 'wall']),
)
@pytest.mark.parametrize(
    'billing_doc, pay_info, failed',
    [
        (
            'doc_exceeded.json',
            PayInfo(
                income=test_common.make_money_params('270 ₽'),
                guarantee=test_common.make_money_params('250 ₽'),
                time_args=test_common.make_time_args(minutes='15', hours='1'),
            ),
            False,
        ),
        (
            'doc_bonus.json',
            PayInfo(
                income=test_common.make_money_params('100 ₽'),
                bonus=test_common.make_money_params('200 ₽'),
                guarantee=test_common.make_money_params('300 ₽'),
                time_args=test_common.make_time_args(minutes='15'),
            ),
            False,
        ),
        ('doc_wrong.json', None, True),
        ('doc_wrong_precision.json', None, True),
        (
            'doc_ok_precision.json',
            PayInfo(
                income=test_common.make_money_params('100 ₽'),
                bonus=test_common.make_money_params('200 ₽'),
                guarantee=test_common.make_money_params('300 ₽'),
                time_args=test_common.make_time_args(minutes='15'),
            ),
            False,
        ),
    ],
)
async def test_pay(
        taxi_subvention_communications,
        taxi_config,
        notifications,
        clients,
        stq,
        stq_runner,
        load_json,
        billing_doc,
        pay_info,
        failed,
):
    taxi_config.set(
        SUBVENTION_COMMUNICATIONS_NOTIFICATIONS=test_common.create_config(
            'geobooking', 'pay', notifications,
        ),
    )

    clients.add_rule(_create_geobooking_rule())
    clients.add_doc(test_common.make_billing_doc(load_json(billing_doc)))

    request = {
        'idempotency_key': 'abcd1234abcd',
        'drivers': [
            {'park_id': 'dbid1', 'driver_profile_id': 'uuid1'},
            {'park_id': 'dbid2', 'driver_profile_id': 'uuid2'},
        ],
        'rule_type': 'geobooking',
        'rule_id': '_id/1',
        'date': '2020-04-28',
        'doc_id': 443556,
    }

    response = await taxi_subvention_communications.post(
        '/v1/rule/pay', json=request,
    )
    assert response.status_code == 200

    await test_common.check_and_process_queue(
        stq, stq_runner, request, expect_fail=failed,
    )
    assert clients.rules_select.times_called == 0
    assert clients.docs_by_id.times_called == 1
    if failed:
        return

    _check_driver_push_handler(
        clients.driver_bulk_push, notifications.count('push'), pay_info,
    )
    _check_driver_wall_handler(
        clients.driver_wall_add, notifications.count('wall'), pay_info,
    )


async def test_geobooking_fraud(
        taxi_subvention_communications, taxi_config, clients,
):
    request = {
        'idempotency_key': 'abcd1234abcd',
        'drivers': [{'park_id': 'dbid1', 'driver_profile_id': 'uuid1'}],
        'rule_type': 'geobooking',
        'rule_id': '_id/1',
        'date': '2020-04-28',
    }
    response = await taxi_subvention_communications.post(
        '/v1/rule/fraud', json=request,
    )
    assert response.status_code == 400
