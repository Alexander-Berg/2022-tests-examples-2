import dataclasses


import pytest

from . import test_common


@dataclasses.dataclass
class PayInfo:
    num_orders: int
    income: dict = dataclasses.field(default_factory=dict)
    bonus: dict = dataclasses.field(default_factory=dict)
    guarantee: dict = dataclasses.field(default_factory=dict)


def _params(pay_info):
    params = {
        'day': '28',
        'month': {'keyset': 'notify', 'key': 'helpers.month_4_part'},
        'in_zone': {
            'keyset': 'taximeter_messages',
            'key': 'subventions_feed.in_zone.moscow',
        },
        'income': pay_info.income,
        'n_orders': {
            'params': {'count': str(pay_info.num_orders)},
            'keyset': 'taximeter_messages',
            'key': 'subventions_done_feed.daily_guarantee.n_orders',
        },
    }
    if pay_info.bonus:
        assert pay_info.guarantee
        params['bonus'] = pay_info.bonus
        params['guarantee'] = pay_info.guarantee

    return params


def _title(pay_info):
    return (
        'subvention_communications.daily_guarantee.bonus_title'
        if pay_info.bonus
        else 'subvention_communications.daily_guarantee.exceeded_title'
    )


def _key(pay_info):
    return (
        'subvention_communications.daily_guarantee.bonus_text'
        if pay_info.bonus
        else 'subvention_communications.daily_guarantee.exceeded_text'
    )


def _check_driver_wall_handler(driver_wall_handler, expected_calls, pay_info):
    expected_request = {
        'id': 'abcd1234abcd',
        'template': {
            'title': {'keyset': 'taximeter_messages', 'key': _title(pay_info)},
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


@pytest.mark.parametrize(
    'notifications', (['wall'], ['push'], ['push', 'wall']),
)
@pytest.mark.parametrize(
    'billing_doc, pay_info, failed',
    [
        (
            'doc_exceeded.json',
            PayInfo(
                income=test_common.make_money_params('4883 ₽'), num_orders=30,
            ),
            False,
        ),
        (
            'doc_bonus.json',
            PayInfo(
                income=test_common.make_money_params('800 ₽'),
                num_orders=10,
                bonus=test_common.make_money_params('250 ₽'),
                guarantee=test_common.make_money_params('1000 ₽'),
            ),
            False,
        ),
        ('doc_wrong.json', None, True),
    ],
)
async def test_nmfg_pay(
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
            'nmfg', 'pay', notifications,
        ),
    )

    clients.add_rule(test_common.create_nmfg_rule())
    billing_doc_json = load_json(billing_doc)
    clients.add_doc(test_common.make_billing_doc(billing_doc_json))

    request = {
        'idempotency_key': 'abcd1234abcd',
        'drivers': [
            {'park_id': 'dbid1', 'driver_profile_id': 'uuid1'},
            {'park_id': 'dbid2', 'driver_profile_id': 'uuid2'},
        ],
        'rule_type': 'nmfg',
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
    assert clients.rules_select.times_called == 1
    assert clients.docs_by_id.times_called == 1
    if failed:
        return

    _check_driver_push_handler(
        clients.driver_bulk_push, notifications.count('push'), pay_info,
    )
    _check_driver_wall_handler(
        clients.driver_wall_add, notifications.count('wall'), pay_info,
    )
