from datetime import datetime

from aiohttp import web
import pytest

from taxi_billing_accounts import models


A_10007 = models.V2Account(
    account_id=10007,
    entity_external_id='unique_driver_id/5b60199b41e102a72fe8268c',
    agreement_id='ag-testsuite-001',
    currency='RUB',
    sub_account='income',
    opened=datetime(2018, 8, 9, 16, 13, 16, 818875),
    expired=datetime(2018, 8, 15, 22, 0, 0),
)

A_20001 = models.V2Account(
    account_id=20001,
    entity_external_id='unique_driver_id/5ac2856ae342c7944bff60b6',
    agreement_id='subvention_agreement/2018_10_17',
    currency='XXX',
    sub_account='num_orders',
    opened=datetime(2018, 7, 9, 16, 31, 52, 758819),
    expired=datetime(2018, 9, 10, 22, 0, 0),
)

A_50001 = models.V2Account(
    account_id=50001,
    entity_external_id='unique_driver_id/5b0913df30a2e52b7633b3e6',
    agreement_id='ag-testsuite-nMFG-000',
    currency='RUB',
    sub_account='income',
    opened=datetime(2018, 8, 9, 17, 5, 41, 406741),
    expired=datetime(2018, 8, 15, 22, 0, 0),
)

A_51001 = models.V2Account(
    account_id=51001,
    entity_external_id='unique_driver_id/5b0913df30a2e52b7633b3e6',
    agreement_id='ag-testsuite-nMFG-000',
    currency='XXX',
    sub_account='num_orders',
    opened=datetime(2018, 8, 9, 17, 5, 41, 651405),
    expired=datetime(2018, 8, 15, 22, 0, 0),
)

A_974001 = models.V2Account(
    account_id=9740001,
    entity_external_id='unique_driver_id/5b0913df30a2e52b7633b3e6',
    agreement_id='subvention_agreement/voronezh_daily_guarantee_2018',
    currency='RUB',
    sub_account='income',
    opened=datetime(2018, 11, 23, 9, 12, 37, 281163),
    expired=datetime(9999, 12, 31, 23, 59, 59, 999999),
)

A_5256730001 = models.V2Account(
    account_id=5256730001,
    entity_external_id='unique_driver_id/5ac2856ae342c7944bff60b6',
    agreement_id='subvention_agreement/2018_10_17',
    currency='RUB',
    sub_account='net',
    opened=datetime(2018, 7, 9, 16, 31, 52, 758819),
    expired=datetime(2018, 9, 10, 22),
)


@pytest.mark.parametrize('use_master', [True, False])
@pytest.mark.parametrize(
    'accounts,expected',
    (
        # no data
        ([], []),
        # absent account_id
        ([{'account_id': 111001}], []),
        # absent entity_external_id
        ([{'entity_external_id': 'deadbeef'}], []),
        # existed account_id
        ([{'account_id': 51001}], [A_51001]),
        # account id that overflows ordinary int
        ([{'account_id': 5256730001}], [A_5256730001]),
        # existed accounts + duplication
        (
            [
                {'account_id': 51001},
                {
                    'entity_external_id': (
                        'unique_driver_id/5b0913df30a2e52b7633b3e6'
                    ),
                },
                {'account_id': 50001},
            ],
            [A_50001, A_51001, A_974001],
        ),
        # accounts from different shards (sorted by (vshard, account_id))
        ([{'account_id': 10007}, {'account_id': 20001}], [A_20001, A_10007]),
    ),
)
@pytest.mark.pgsql(
    'billing_accounts@0',
    files=('meta.sql', 'entities@0.sql', 'accounts@0.sql'),
)
@pytest.mark.pgsql(
    'billing_accounts@1',
    files=('meta.sql', 'entities@1.sql', 'accounts@1.sql'),
)
async def test_v2_accounts_search(
        billing_accounts_client,
        request_headers,
        use_master,
        accounts,
        expected,
):
    query = {'accounts': accounts}
    if use_master:
        query['use_master'] = True
    response = await billing_accounts_client.post(
        '/v2/accounts/search', json=query, headers=request_headers,
    )
    assert response.status == web.HTTPOk.status_code
    data = await response.json()
    assert expected == [
        models.V2Account.from_json(d) for d in data['accounts']
    ]
