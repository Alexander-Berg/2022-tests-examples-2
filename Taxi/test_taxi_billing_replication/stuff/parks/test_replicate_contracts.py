# pylint: disable=unused-variable,line-too-long
import datetime

import pytest

from taxi import settings

from taxi_billing_replication import config
from taxi_billing_replication import cron_run


@pytest.mark.parametrize('no_changes', [True, False])
@pytest.mark.pgsql('billing_replication', files=['test_contract_changes.sql'])
async def test_contract_changes(
        patch,
        patch_aiohttp_session,
        response_mock,
        fixed_secdist,
        billing_replictaion_cron_app,
        no_changes,
):
    @patch('taxi.clients.solomon.SolomonClient.push_data')
    async def _push_data(data, handler=None, log_extra=None):
        pass

    @patch_aiohttp_session(settings.Settings.BALANCE_XMLRPC_API_HOST)
    def get_client_contracts(method, url, **kwargs):
        contract_template = (
            '<value><struct>'
            '<member>'
            '<name>IS_SIGNED</name>'
            '<value><int>{is_signed}</int></value>'
            '</member>'
            '<member>'
            '<name>ID</name>'
            '<value><int>{contract_id}</int></value>'
            '</member>'
            '</struct></value>'
        )
        result_template = (
            '<?xml version=\'1.0\'?>'
            '<methodResponse>'
            '<params>'
            '<param>'
            '<value><array><data>'
            '{contracts}'
            '</data></array></value>'
            '</param>'
            '</params>'
            '</methodResponse>'
        )
        if no_changes:
            contracts = [
                contract_template.format(is_signed=0, contract_id=2),
                contract_template.format(is_signed=0, contract_id=3),
                contract_template.format(is_signed=1, contract_id=4),
                contract_template.format(is_signed=1, contract_id=5),
                contract_template.format(is_signed=1, contract_id=6),
            ]
        else:
            contracts = [
                contract_template.format(is_signed=0, contract_id=1),
                contract_template.format(is_signed=0, contract_id=2),
                contract_template.format(is_signed=1, contract_id=4),
                contract_template.format(is_signed=0, contract_id=5),
                contract_template.format(is_signed=1, contract_id=7),
            ]
        result = result_template.format(contracts=''.join(contracts))
        return response_mock(read=result.encode())

    module = 'taxi_billing_replication.stuff.parks.replicate_contracts'
    await cron_run.run_replication_task([module, '-t', '0'])
    pool = billing_replictaion_cron_app.pg_connection_pool
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            'SELECT * FROM parks.contract_versions ORDER BY "ID", version;',
        )
    if no_changes:
        assert len(rows) == 7  # already in table
    else:
        assert len(rows) == 12
        result = [(row['ID'], row['version'], row['status']) for row in rows]
        assert result == [
            (1, 1, 'INACTIVE'),  # before test
            (1, 2, 'ACTIVE'),  # became active
            (2, 1, 'ACTIVE'),  # before test
            (3, 1, 'ACTIVE'),  # before test
            (3, 2, 'INACTIVE'),  # became inactive
            (4, 1, 'ACTIVE'),  # before test
            (5, 1, 'ACTIVE'),  # before test
            (5, 2, 'ACTIVE'),  # changed is_signed
            (6, 1, 'ACTIVE'),  # before test
            (6, 2, 'ACTIVE'),  # before test
            (6, 3, 'INACTIVE'),  # became inactive
            (7, 1, 'ACTIVE'),  # became active (new)
        ]


@pytest.mark.pgsql(
    'billing_replication', files=['test_fetch_all_contracts.sql'],
)
@pytest.mark.now('2021-03-16T09:00:00.000000+00:00')
@pytest.mark.config(
    BILLING_REPLICATION_FETCH_ALL_CONTRACTS=True,
    BILLING_REPLICATION_BALANCES_V2_SERVICE_IDS=[111],
)
@pytest.mark.parametrize('raise_error_on_cancelled_fetch', [False, True])
async def test_fetch_all_park_contracts(
        patch,
        response_mock,
        fixed_secdist,
        billing_replictaion_cron_app,
        raise_error_on_cancelled_fetch,
):
    @patch('taxi.clients.solomon.SolomonClient.push_data')
    async def _push_data(data, handler=None, log_extra=None):
        pass

    @patch('taxi.clients.billing_v2.BalanceClient.get_client_contracts')
    async def get_client_contracts(**kwargs):
        if kwargs['client_id'] == 'client_id2':
            # check fails in one client don't affect another
            return []
        if kwargs.get('add_finished') is not None:
            assert kwargs['add_finished']
            return [
                # in replica now, active
                {
                    'ID': 1,
                    'SERVICES': [111],
                    'IS_CANCELLED': 0,
                    'IS_ACTIVE': 1,
                },
                # in replica now, finished
                {
                    'ID': 2,
                    'SERVICES': [111],
                    'IS_CANCELLED': 0,
                    'IS_ACTIVE': 0,
                    'FINISH_DT': datetime.datetime(2021, 3, 16, 0, 0, 0),
                },
                # new contract
                {
                    'ID': 4,
                    'SERVICES': [111],
                    'IS_CANCELLED': 0,
                    'IS_ACTIVE': 1,
                },
                # absent in replica old contract
                {
                    'ID': 5,
                    'SERVICES': [111],
                    'IS_CANCELLED': 0,
                    'IS_ACTIVE': 0,
                    'FINISH_DT': datetime.datetime(2021, 3, 16, 0, 0, 0),
                },
                # new, not started yet, so IS_ACTIVE = 0,
                # status should be ACTIVE
                {
                    'ID': 6,
                    'SERVICES': [111],
                    'IS_CANCELLED': 0,
                    'IS_ACTIVE': 0,
                    'DT': datetime.datetime(2021, 3, 20, 0, 0, 0),
                },
            ]

        if kwargs.get('contract_signed') is not None:
            assert not kwargs['contract_signed']
            if raise_error_on_cancelled_fetch:
                raise RuntimeError
            return [
                # in replica now, diff IS_CANCELLED, not in finished
                {'ID': 3, 'IS_CANCELLED': 1, 'IS_ACTIVE': 0},
            ]

    module = 'taxi_billing_replication.stuff.parks.replicate_contracts'
    await cron_run.run_replication_task([module, '-t', '0'])
    pool = billing_replictaion_cron_app.pg_connection_pool
    async with pool.acquire() as conn:
        contracts_rows = await conn.fetch(
            'SELECT * FROM parks.contract_versions ORDER BY "ID", version;',
        )
        actual_contracts_rows = [
            (
                row['ID'],
                row['version'],
                row['status'],
                row['IS_ACTIVE'],
                row['IS_CANCELLED'],
            )
            for row in contracts_rows
        ]

        contracts_queue_rows = await conn.fetch(
            'SELECT (billing_kwargs).client_id, fail_count '
            'FROM parks.contracts_queue '
            'ORDER BY (billing_kwargs).client_id;',
        )

        balances_queue_rows = await conn.fetch(
            'SELECT (billing_kwargs).contract_id as contract_id '
            'FROM parks.balances_queue '
            'ORDER BY (billing_kwargs).contract_id;',
        )
        actual_balances_queue_rows = [
            row['contract_id'] for row in balances_queue_rows
        ]

        balances_queue_v2_rows = await conn.fetch(
            'SELECT '
            ' (billing_kwargs).contract_id as contract_id, '
            ' (billing_kwargs).service_id as service_id '
            'FROM parks.balances_queue_v2 '
            'ORDER BY (billing_kwargs).contract_id;',
        )
        actual_balances_queue_v2_rows = [
            (row['contract_id'], row['service_id'])
            for row in balances_queue_v2_rows
        ]

        if not raise_error_on_cancelled_fetch:
            assert actual_contracts_rows == [
                (1, 1, 'ACTIVE', 1, 0),
                (2, 1, 'ACTIVE', 1, 0),
                (2, 2, 'INACTIVE', 0, 0),
                (3, 1, 'INACTIVE', 1, 0),
                (3, 2, 'INACTIVE', 0, 1),
                (4, 1, 'ACTIVE', 1, 0),
                (5, 1, 'INACTIVE', 0, 0),
                (6, 1, 'ACTIVE', 0, 0),
            ]

            # check updated was successful
            assert (
                len(contracts_queue_rows) == 2
                and contracts_queue_rows[0]['fail_count'] == 0
                and contracts_queue_rows[1]['fail_count'] == 0
            )

            # ask contract balance only for active contracts 1, 4, 6
            assert actual_balances_queue_rows == [1, 4, 6]
            assert actual_balances_queue_v2_rows == [
                (1, 111),
                (4, 111),
                (6, 111),
            ]
        else:
            # mark all client contracts fetch as failed,
            # so nothing should be changed in replica and
            # update should be marked as failed
            assert actual_contracts_rows == [
                (1, 1, 'ACTIVE', 1, 0),
                (2, 1, 'ACTIVE', 1, 0),
                (3, 1, 'INACTIVE', 1, 0),
            ]

            # check update for bci=client_id was unsuccessful
            assert (
                len(contracts_queue_rows) == 2
                and contracts_queue_rows[0]['fail_count'] == 1
                and contracts_queue_rows[1]['fail_count'] == 0
            )

            # ask contract balance only for active contracts 1, 2
            assert actual_balances_queue_rows == [1, 2]
            assert actual_balances_queue_v2_rows == [(1, 111), (2, 111)]


@pytest.mark.pgsql(
    'billing_replication', files=['test_replicate_contracts.sql'],
)
@pytest.mark.now('2021-03-16T09:00:00.000000+00:00')
@pytest.mark.config(BILLING_REPLICATION_FETCH_ALL_CONTRACTS=True)
@pytest.mark.parametrize(
    'add_ar_history, '
    'expected_add_history_for_attributes, '
    'balance_response, '
    'expected_newest_contracts',
    [
        (
            False,
            ['SERVICES'],
            [
                {
                    'ID': 1,
                    'SERVICES': [111],
                    'IS_CANCELLED': 0,
                    'IS_ACTIVE': 1,
                    'FINISH_DT': None,
                    'ATTRIBUTES_HISTORY': {
                        'SERVICES': [
                            [datetime.datetime(2020, 1, 1, 0, 0), [111]],
                            [datetime.datetime(2099, 1, 1, 0, 0), [111, 128]],
                        ],
                    },
                },
                {
                    'ID': 2,
                    'SERVICES': [111],
                    'IS_CANCELLED': 0,
                    'IS_ACTIVE': 1,
                    'FINISH_DT': None,
                    'ATTRIBUTES_HISTORY': None,
                },
            ],
            [
                {
                    'ID': 1,
                    'SERVICES': [111],
                    'IS_CANCELLED': 0,
                    'IS_ACTIVE': 1,
                    'FINISH_DT': None,
                    'ATTRIBUTES_HISTORY': (
                        '{'
                        '"SERVICES": '
                        '[["2020-01-01 00:00:00", [111]], '
                        '["2099-01-01 00:00:00", [111, 128]]]'
                        '}'
                    ),
                },
                {
                    'ID': 2,
                    'SERVICES': [111],
                    'IS_CANCELLED': 0,
                    'IS_ACTIVE': 1,
                    'FINISH_DT': None,
                    'ATTRIBUTES_HISTORY': None,
                },
            ],
        ),
        (
            True,
            [
                'SERVICES',
                'PARTNER_COMMISSION_PCT2',
                'YANDEX_BANK_ENABLED',
                'YANDEX_BANK_WALLET_PAY',
                'YANDEX_BANK_WALLET_ID',
                'YANDEX_BANK_ACCOUNT_ID',
            ],
            [
                {
                    'ID': 1,
                    'SERVICES': [111],
                    'IS_CANCELLED': 0,
                    'IS_ACTIVE': 1,
                    'FINISH_DT': None,
                    'ATTRIBUTES_HISTORY': {
                        'SERVICES': [
                            [datetime.datetime(2020, 1, 1, 0, 0), [111]],
                            [datetime.datetime(2099, 1, 1, 0, 0), [111, 128]],
                        ],
                        'PARTNER_COMMISSION_PCT2': [
                            [datetime.datetime(2020, 1, 1, 0, 0), '5'],
                            [datetime.datetime(2099, 1, 1, 0, 0), '6.5'],
                        ],
                    },
                },
                {
                    'ID': 2,
                    'SERVICES': [650, 651],
                    'IS_CANCELLED': 0,
                    'IS_ACTIVE': 1,
                    'FINISH_DT': None,
                    'ATTRIBUTES_HISTORY': {
                        'SERVICES': [
                            [datetime.datetime(2020, 1, 1, 0, 0), [650]],
                            [datetime.datetime(2021, 1, 1, 0, 0), [650, 651]],
                        ],
                        'PARTNER_COMMISSION_PCT2': [
                            [datetime.datetime(2020, 1, 1, 0, 0), '1'],
                            [datetime.datetime(2021, 1, 1, 0, 0), '2'],
                        ],
                    },
                },
                {
                    'ID': 3,
                    'SERVICES': [222],
                    'IS_CANCELLED': 0,
                    'IS_ACTIVE': 1,
                    'FINISH_DT': None,
                    'ATTRIBUTES_HISTORY': {
                        'SERVICES': [
                            [datetime.datetime(2021, 1, 1, 0, 0), [222]],
                        ],
                        'PARTNER_COMMISSION_PCT2': [],
                    },
                },
            ],
            [
                {
                    'ID': 1,
                    'SERVICES': [111],
                    'IS_CANCELLED': 0,
                    'IS_ACTIVE': 1,
                    'FINISH_DT': None,
                    'ATTRIBUTES_HISTORY': (
                        '{'
                        '"SERVICES": '
                        '[["2020-01-01 00:00:00", [111]], '
                        '["2099-01-01 00:00:00", [111, 128]]], '
                        '"PARTNER_COMMISSION_PCT2": '
                        '[["2020-01-01 00:00:00", "5"], '
                        '["2099-01-01 00:00:00", "6.5"]]'
                        '}'
                    ),
                },
                {
                    'ID': 2,
                    'SERVICES': [650, 651],
                    'IS_CANCELLED': 0,
                    'IS_ACTIVE': 1,
                    'FINISH_DT': None,
                    'ATTRIBUTES_HISTORY': (
                        '{'
                        '"SERVICES": '
                        '[["2020-01-01 00:00:00", [650]], '
                        '["2021-01-01 00:00:00", [650, 651]]], '
                        '"PARTNER_COMMISSION_PCT2": '
                        '[["2020-01-01 00:00:00", "1"], '
                        '["2021-01-01 00:00:00", "2"]]'
                        '}'
                    ),
                },
                {
                    'ID': 3,
                    'SERVICES': [222],
                    'IS_CANCELLED': 0,
                    'IS_ACTIVE': 1,
                    'FINISH_DT': None,
                    'ATTRIBUTES_HISTORY': (
                        '{"SERVICES": [["2021-01-01 00:00:00", [222]]]}'
                    ),
                },
            ],
        ),
    ],
)
async def test_replicate_park_contracts_with_ar_history(
        patch,
        fixed_secdist,
        monkeypatch,
        billing_replictaion_cron_app,
        add_ar_history,
        expected_add_history_for_attributes,
        balance_response,
        expected_newest_contracts,
):
    monkeypatch.setattr(
        config.Config,
        'BILLING_REPLICATION_PARTNER_COMMISSION_PCT2_HISTORY',
        add_ar_history,
    )

    monkeypatch.setattr(
        config.Config,
        'BILLING_REPLICATION_YANDEX_BANK_HISTORY',
        add_ar_history,
    )

    @patch('taxi.clients.solomon.SolomonClient.push_data')
    async def _push_data(data, handler=None, log_extra=None):
        pass

    @patch('taxi.clients.billing_v2.BalanceClient.get_client_contracts')
    async def get_client_contracts(**kwargs):
        assert (
            kwargs['add_history_for_attributes']
            == expected_add_history_for_attributes
        )
        return balance_response

    module = 'taxi_billing_replication.stuff.parks.replicate_contracts'
    await cron_run.run_replication_task([module, '-t', '0'])
    pool = billing_replictaion_cron_app.pg_connection_pool
    async with pool.acquire() as conn:
        newest_contracts_rows = await conn.fetch(
            'SELECT * FROM parks.contract_versions WHERE expired is NULL '
            'ORDER BY "ID", version;',
        )
        actual_contracts = []
        check_keys = []
        if expected_newest_contracts:
            check_keys = expected_newest_contracts[0].keys()
        for row in newest_contracts_rows:
            check_row = {
                check_key: row.get(check_key, 'key_not_found')
                for check_key in check_keys
            }
            actual_contracts.append(check_row)
        assert actual_contracts == expected_newest_contracts
