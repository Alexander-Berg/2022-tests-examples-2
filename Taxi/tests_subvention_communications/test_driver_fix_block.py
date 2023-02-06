import pytest

from . import test_common


def _check_driver_wall_handler(driver_wall_handler, expected_calls):
    expected_request = {
        'id': 'abcd1234abcd',
        'template': {
            'text': {
                'keyset': 'taximeter_messages',
                'key': 'subvention_communications.driver_fix.block',
            },
            'title': {
                'keyset': 'taximeter_messages',
                'key': 'subvention_communications.driver_fix.block_title',
            },
            'alert': True,
            'type': 'newsletter',
        },
        'filters': {'drivers': ['dbid_uuid']},
    }
    test_common.check_handler(
        driver_wall_handler, expected_calls, expected_request,
    )


def _check_driver_push_handler(driver_push_handler, expected_calls):
    expected_request = {
        'drivers': [{'dbid': 'dbid', 'uuid': 'uuid'}],
        'code': 1300,
        'action': 'MessageNew',
        'data': {
            'text': {
                'keyset': 'taximeter_messages',
                'key': 'subvention_communications.driver_fix.block',
            },
        },
    }
    test_common.check_handler(
        driver_push_handler, expected_calls, expected_request,
    )


def _check_driver_sms_handler(driver_sms_handler, expected_calls):
    expected_request = {
        'park_id': 'dbid',
        'driver_id': 'uuid',
        'text': {
            'keyset': 'taximeter_messages',
            'key': 'subvention_communications.driver_fix.block',
        },
        'intent': 'driver_fix_subventions',
        'sender': 'go',
    }
    test_common.check_handler(
        driver_sms_handler, expected_calls, expected_request,
    )


@pytest.mark.parametrize(
    'notifications', (['push'], ['sms'], ['wall'], ['sms', 'push', 'wall']),
)
@pytest.mark.parametrize('use_rule_fraud_handler', [True, False])
async def test_driver_fix_block(
        taxi_subvention_communications,
        mockserver,
        taxi_config,
        notifications,
        clients,
        stq,
        stq_runner,
        use_rule_fraud_handler,
):
    taxi_config.set(
        SUBVENTION_COMMUNICATIONS_NOTIFICATIONS=test_common.create_config(
            'driver_fix', 'fraud', notifications,
        ),
    )

    if use_rule_fraud_handler:
        request = {
            'idempotency_key': 'abcd1234abcd',
            'drivers': [{'park_id': 'dbid', 'driver_profile_id': 'uuid'}],
            'rule_type': 'driver_fix',
            'rule_id': '_id/1',
            'date': '2020-04-28',
        }
        response = await taxi_subvention_communications.post(
            '/v1/rule/fraud', json=request,
        )
        assert response.status_code == 200
    else:
        response = await taxi_subvention_communications.post(
            '/v1/driver_fix/block',
            json={
                'idempotency_token': 'abcd1234abcd',
                'driver_info': {
                    'park_id': 'dbid',
                    'driver_profile_id': 'uuid',
                },
            },
        )
        assert response.status_code == 200

    rule_data = {
        'drivers': [{'park_id': 'dbid', 'driver_profile_id': 'uuid'}],
        'rule_type': 'driver_fix',
        'idempotency_key': 'abcd1234abcd',
        'type': 'fraud',
    }
    await test_common.check_and_process_queue(stq, stq_runner, rule_data)

    _check_driver_push_handler(
        clients.driver_bulk_push, notifications.count('push'),
    )
    _check_driver_wall_handler(
        clients.driver_wall_add, notifications.count('wall'),
    )
    _check_driver_sms_handler(clients.send_sms, notifications.count('sms'))
