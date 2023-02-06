import json

import pytest


def get_config(enabled):
    config = {
        'enabled': enabled,
        'retrying_policy': {
            'min_retry_delay': 150,
            'delay_multiplier': 1.1,
            'max_random_delay': 10,
            'max_possible_delay': 600,
        },
        'lb_read_batch': 100,
    }
    return config


@pytest.mark.config(
    BALANCE_REPLICA_LB_READER_SETTINGS={
        '__default__': get_config(enabled=False),
        'personal_accounts_lb_reader': get_config(enabled=True),
    },
)
async def test_message(taxi_balance_replica, testpoint, get_personal_accounts):
    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie1'

    accounts = get_personal_accounts()
    assert accounts == []

    response = await taxi_balance_replica.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'personal-account-lb-reader',
                'data': json.dumps(
                    {
                        'classname': 'PersonalAccount',
                        'obj': {
                            'contract_id': 1,
                            'external_id': 'ЛСТ-1',
                            'id': 1,
                            'service_code': 'AGENT_REWARD',
                        },
                        'version': 0,
                    },
                ),
                'topic': '/balance/testsuite/personal-account',
                'cookie': 'cookie1',
            },
        ),
    )
    assert response.status_code == 200

    async with taxi_balance_replica.spawn_task('personal_account_lb_reader'):
        await commit.wait_call()

    accounts = get_personal_accounts()
    assert len(accounts) == 1
    assert accounts == [
        {
            'id': 1,
            'version': 0,
            'contract_id': 1,
            'external_id': 'ЛСТ-1',
            'service_code': 'AGENT_REWARD',
        },
    ]


@pytest.mark.config(
    BALANCE_REPLICA_LB_READER_SETTINGS={
        '__default__': get_config(enabled=False),
        'personal_accounts_lb_reader': get_config(enabled=True),
    },
)
async def test_skip_null(
        taxi_balance_replica, testpoint, get_personal_accounts,
):
    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie in ['cookie1', 'cookie2', 'cookie3']

    accounts = get_personal_accounts()
    assert accounts == []

    response = await taxi_balance_replica.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'personal-account-lb-reader',
                'data': json.dumps(
                    {
                        'classname': 'PersonalAccount',
                        'obj': {
                            'contract_id': 1,
                            'external_id': None,
                            'id': 1,
                            'service_code': 'AGENT_REWARD',
                        },
                        'version': 0,
                    },
                ),
                'topic': '/balance/testsuite/personal-account',
                'cookie': 'cookie1',
            },
        ),
    )
    assert response.status_code == 200

    response = await taxi_balance_replica.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'personal-account-lb-reader',
                'data': json.dumps(
                    {
                        'classname': 'PersonalAccount',
                        'obj': {
                            'contract_id': 1,
                            'external_id': 'ЛСТ-1',
                            'id': 1,
                            'service_code': None,
                        },
                        'version': 0,
                    },
                ),
                'topic': '/balance/testsuite/personal-account',
                'cookie': 'cookie2',
            },
        ),
    )
    assert response.status_code == 200

    response = await taxi_balance_replica.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'personal-account-lb-reader',
                'data': json.dumps(
                    {
                        'classname': 'PersonalAccount',
                        'obj': {
                            'contract_id': None,
                            'external_id': 'ЛСТ-1',
                            'id': 1,
                            'service_code': 'AGENT_REWARD',
                        },
                        'version': 0,
                    },
                ),
                'topic': '/balance/testsuite/personal-account',
                'cookie': 'cookie3',
            },
        ),
    )
    assert response.status_code == 200

    async with taxi_balance_replica.spawn_task('personal_account_lb_reader'):
        await commit.wait_call()
        await commit.wait_call()
        await commit.wait_call()

    accounts = get_personal_accounts()
    assert accounts == []


@pytest.mark.config(
    BALANCE_REPLICA_LB_READER_SETTINGS={
        '__default__': get_config(enabled=False),
        'personal_accounts_lb_reader': get_config(enabled=True),
    },
)
@pytest.mark.pgsql(
    'balance-replica',
    queries=[
        'INSERT INTO personal_accounts.personal_account('
        'id, version, contract_id, external_id, service_code'
        ') '
        'VALUES (0, 0, 0, \'ЛСТ-0\', \'YANDEX_SERVICE\')',
    ],
)
async def test_insert_only_new_version(
        taxi_balance_replica, testpoint, get_personal_accounts,
):
    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie1'

    response = await taxi_balance_replica.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'personal-account-lb-reader',
                'data': json.dumps(
                    {
                        'classname': 'PersonalAccount',
                        'obj': {
                            'contract_id': 0,
                            'external_id': 'ЛСТ-1',
                            'id': 0,
                            'service_code': 'YANDEX_SERVICE',
                        },
                        'version': 0,
                    },
                ),
                'topic': '/balance/testsuite/personal-account',
                'cookie': 'cookie1',
            },
        ),
    )
    assert response.status_code == 200

    async with taxi_balance_replica.spawn_task('personal_account_lb_reader'):
        await commit.wait_call()

    accounts = get_personal_accounts()
    assert accounts == [
        {
            'contract_id': 0,
            'id': 0,
            'version': 0,
            'service_code': 'YANDEX_SERVICE',
            'external_id': 'ЛСТ-0',
        },
    ]


@pytest.mark.config(
    BALANCE_REPLICA_LB_READER_SETTINGS={
        '__default__': get_config(enabled=False),
        'personal_accounts_lb_reader': get_config(enabled=True),
    },
)
async def test_error(
        taxi_balance_replica, testpoint, get_personal_accounts, stq,
):
    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie1'

    accounts = get_personal_accounts()
    assert accounts == []

    data = json.dumps(
        {'classname': 'PersonalAccount', 'obj': None, 'version': 0},
    )
    response = await taxi_balance_replica.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'personal-account-lb-reader',
                'data': data,
                'topic': '/balance/testsuite/personal-account',
                'cookie': 'cookie1',
            },
        ),
    )
    assert response.status_code == 200

    async with taxi_balance_replica.spawn_task('personal_account_lb_reader'):
        await commit.wait_call()

    accounts = get_personal_accounts()
    assert accounts == []
    assert stq.balance_replica_personal_accounts.times_called == 1
    stq_call = stq.balance_replica_personal_accounts.next_call()
    stq_call.pop('eta')
    stq_call['kwargs'].pop('log_extra')
    assert stq_call == {
        'queue': 'balance_replica_personal_accounts',
        'id': 'personal_accounts_error_7e4c590b2f10a5891cf17ecdda2ffd24',
        'args': [],
        'kwargs': {
            'error_msg': 'Field \'obj.id\' is missing',
            'raw_data': data,
            'source': 'lb',
        },
    }
