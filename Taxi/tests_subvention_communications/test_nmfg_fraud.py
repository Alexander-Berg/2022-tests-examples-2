import copy

import pytest

from . import test_common


def _fraud_key(fraud_id):
    return (
        'subvention_communications.daily_guarantee.fraud'
        if fraud_id is None
        else 'subvention_communications.daily_guarantee.fraud_with_reason'
    )


def _fraud_text_params(fraud_id, clients):
    params = {
        'day': '28',
        'month': {'keyset': 'notify', 'key': 'helpers.month_4_part'},
        'in_zone': {
            'keyset': 'taximeter_messages',
            'key': 'subventions_feed.in_zone.moscow',
        },
    }
    if fraud_id:
        params['reason'] = clients.fraud_reason_tanker_info()
    return params


def _check_driver_wall_handler(
        driver_wall_handler, expected_calls, fraud_id, clients,
):
    expected_request = {
        'id': 'abcd1234abcd',
        'template': {
            'title': {
                'keyset': 'taximeter_messages',
                'key': 'subvention_communications.daily_guarantee.fraud_title',
            },
            'text': {
                'keyset': 'taximeter_messages',
                'key': _fraud_key(fraud_id),
                'params': _fraud_text_params(fraud_id, clients),
            },
            'type': 'newsletter',
            'alert': True,
        },
        'filters': {'drivers': ['dbid1_uuid1', 'dbid2_uuid2']},
    }
    test_common.check_handler(
        driver_wall_handler, expected_calls, expected_request,
    )


def _check_driver_push_handler(
        driver_push_handler, expected_calls, fraud_id, clients,
):
    expected_request = {
        'data': {
            'text': {
                'keyset': 'taximeter_messages',
                'key': _fraud_key(fraud_id),
                'params': _fraud_text_params(fraud_id, clients),
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
@pytest.mark.parametrize('fraud_id', [None, 'some_id'])
async def test_nmfg_fraud(
        taxi_subvention_communications,
        taxi_config,
        notifications,
        fraud_id,
        clients,
        stq,
        stq_runner,
        load_json,
):
    taxi_config.set(
        SUBVENTION_COMMUNICATIONS_NOTIFICATIONS=test_common.create_config(
            'nmfg', 'fraud', notifications,
        ),
    )

    clients.add_rule(test_common.create_nmfg_rule())

    request = {
        'idempotency_key': 'abcd1234abcd',
        'drivers': [
            {'park_id': 'dbid1', 'driver_profile_id': 'uuid1'},
            {'park_id': 'dbid2', 'driver_profile_id': 'uuid2'},
        ],
        'rule_type': 'nmfg',
        'rule_id': '_id/1',
        'date': '2020-04-28',
    }
    if fraud_id:
        request['fraud_reason'] = fraud_id
    response = await taxi_subvention_communications.post(
        '/v1/rule/fraud', json=request,
    )
    assert response.status_code == 200

    rule_data = copy.deepcopy(request)
    if fraud_id:
        rule_data['id'] = fraud_id
        del rule_data['fraud_reason']

    await test_common.check_and_process_queue(stq, stq_runner, rule_data)

    _check_driver_push_handler(
        clients.driver_bulk_push,
        notifications.count('push'),
        fraud_id,
        clients,
    )
    _check_driver_wall_handler(
        clients.driver_wall_add,
        notifications.count('wall'),
        fraud_id,
        clients,
    )
    assert clients.rules_select.times_called == 1
    assert clients.check_fraud_reason.times_called == (fraud_id is not None)
