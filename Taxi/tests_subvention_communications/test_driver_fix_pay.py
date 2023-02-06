import dataclasses

import pytest


from . import test_common


@dataclasses.dataclass
class ExpectedResult:
    cash_income: dict = dataclasses.field(default_factory=dict)
    income: dict = dataclasses.field(default_factory=dict)
    income_to_show: dict = dataclasses.field(default_factory=dict)
    time_args: dict = dataclasses.field(default_factory=dict)
    fail: bool = False


def _make_json(params):
    res = {'time_on_line': params.time_args, 'income': params.income}
    if params.cash_income:
        res.update(
            {
                'cash_income': params.cash_income,
                'income_to_show': params.income_to_show,
            },
        )
    return res


def _make_key(params):
    if params.cash_income:
        return 'subvention_communications.driver_fix.pay_with_cash'
    return 'subvention_communications.driver_fix.pay_without_cash'


def _check_driver_wall_handler(driver_wall_handler, params, expected_calls):
    expected_request = {
        'id': 'abcd1234abcd',
        'template': {
            'text': {
                'keyset': 'taximeter_messages',
                'key': _make_key(params),
                'params': _make_json(params),
            },
            'title': {
                'keyset': 'taximeter_messages',
                'key': 'subvention_communications.driver_fix.pay_title',
            },
            'alert': False,
            'type': 'newsletter',
        },
        'filters': {'drivers': ['dbid_uuid']},
    }
    test_common.check_handler(
        driver_wall_handler, expected_calls, expected_request,
    )


def _check_driver_push_handler(driver_push_handler, params, expected_calls):
    expected_request = {
        'drivers': [{'dbid': 'dbid', 'uuid': 'uuid'}],
        'code': 1300,
        'action': 'MessageNew',
        'data': {
            'text': {
                'keyset': 'taximeter_messages',
                'key': _make_key(params),
                'params': _make_json(params),
            },
        },
    }
    test_common.check_handler(
        driver_push_handler, expected_calls, expected_request,
    )


def _check_driver_sms_handler(driver_sms_handler, params, expected_calls):
    expected_request = {
        'park_id': 'dbid',
        'driver_id': 'uuid',
        'text': {
            'keyset': 'taximeter_messages',
            'key': _make_key(params),
            'params': _make_json(params),
        },
        'intent': 'driver_fix_subventions',
        'sender': 'go',
    }
    test_common.check_handler(
        driver_sms_handler, expected_calls, expected_request,
    )


def _check_billing_reports_handler(billing_reports_handler):
    test_common.check_handler(
        billing_reports_handler,
        expected_calls=1,
        expected_request={'doc_ids': [1]},
    )


@pytest.mark.parametrize(
    'notifications', (['wall'], ['sms'], ['push'], ['sms', 'push', 'wall']),
)
@pytest.mark.parametrize('use_rule_pay_handler', [True, False])
@pytest.mark.parametrize(
    'billing_doc, expected_result',
    [
        (
            'billing_doc_with_cash.json',
            ExpectedResult(
                cash_income=test_common.make_money_params('10 ₽'),
                income=test_common.make_money_params('31 ₽'),
                income_to_show=test_common.make_money_params('21 ₽'),
                time_args=test_common.make_time_args(minutes='14'),
            ),
        ),
        (
            'billing_doc_without_cash.json',
            ExpectedResult(
                income=test_common.make_money_params('31 ₽'),
                time_args=test_common.make_time_args(hours='1'),
            ),
        ),
        (
            'billing_doc_cash_more_than_guarantee.json',
            ExpectedResult(
                cash_income=test_common.make_money_params('41 ₽'),
                income=test_common.make_money_params('31 ₽'),
                income_to_show=test_common.make_money_params('0 ₽'),
                time_args=test_common.make_time_args(minutes='4', hours='2'),
            ),
        ),
        ('billing_doc_wrong.json', ExpectedResult(fail=True)),
    ],
)
async def test_driver_fix_pay(
        taxi_subvention_communications,
        taxi_config,
        notifications,
        clients,
        load_json,
        billing_doc,
        expected_result,
        stq,
        stq_runner,
        use_rule_pay_handler,
):
    taxi_config.set(
        SUBVENTION_COMMUNICATIONS_NOTIFICATIONS=test_common.create_config(
            'driver_fix', 'pay', notifications,
        ),
    )

    billing_doc_json = load_json(billing_doc)

    clients.add_doc(test_common.make_billing_doc(billing_doc_json))

    if use_rule_pay_handler:
        request = {
            'idempotency_key': 'abcd1234abcd',
            'drivers': [{'park_id': 'dbid', 'driver_profile_id': 'uuid'}],
            'rule_type': 'driver_fix',
            'rule_id': '_id/1',
            'date': '2020-04-28',
            'doc_id': 1,
        }

        response = await taxi_subvention_communications.post(
            '/v1/rule/pay', json=request,
        )
        assert response.status_code == 200
    else:
        response = await taxi_subvention_communications.post(
            '/v1/driver_fix/pay',
            json={
                'idempotency_token': 'abcd1234abcd',
                'driver_info': {
                    'park_id': 'dbid',
                    'driver_profile_id': 'uuid',
                },
                'doc_id': 1,
            },
        )
        assert response.status_code == 200

    rule_data = {
        'drivers': [{'park_id': 'dbid', 'driver_profile_id': 'uuid'}],
        'rule_type': 'driver_fix',
        'idempotency_key': 'abcd1234abcd',
        'doc_id': 1,
        'type': 'pay',
    }
    await test_common.check_and_process_queue(
        stq, stq_runner, rule_data, expect_fail=expected_result.fail,
    )

    _check_billing_reports_handler(clients.docs_by_id)
    if expected_result.fail:
        return

    _check_driver_push_handler(
        clients.driver_bulk_push, expected_result, notifications.count('push'),
    )
    _check_driver_wall_handler(
        clients.driver_wall_add, expected_result, notifications.count('wall'),
    )
    _check_driver_sms_handler(
        clients.send_sms, expected_result, notifications.count('sms'),
    )
