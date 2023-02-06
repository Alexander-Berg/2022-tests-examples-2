# pylint: disable=unused-variable,line-too-long
import pytest

from taxi_billing_replication import cron_run


@pytest.mark.parametrize(
    ['int_api_response', 'expected_db_state'],
    [
        pytest.param(
            {
                'clients': [
                    {
                        'id': 'client_id1',
                        'billing_client_id': '1',
                        'yandex_uid': 'client_id1_uid',
                        'updated_at': '1.1',
                    },
                    {
                        'id': 'client_id2',
                        'billing_client_id': None,
                        'yandex_uid': 'client_id2_uid',
                        'updated_at': '1.2',
                    },
                    {
                        'id': 'client_id3',
                        'billing_client_id': '3',
                        'yandex_uid': 'new_client_id3_uid',
                        'updated_at': '1.3',
                    },
                    {
                        'id': 'client_id4',
                        'billing_client_id': '4',
                        'yandex_uid': 'client_id4_uid',
                        'updated_at': '1.4',
                    },
                ],
            },
            {
                '1': {
                    'id': '1',
                    'corp_id': 'client_id1',
                    'yandex_uid': 'client_id1_uid',
                },
                '3': {
                    'id': '3',
                    'corp_id': 'client_id3',
                    'yandex_uid': 'new_client_id3_uid',
                },
                '4': {
                    'id': '4',
                    'corp_id': 'client_id4',
                    'yandex_uid': 'client_id4_uid',
                },
            },
            id='ordinary',
        ),
    ],
)
@pytest.mark.config(
    BILLING_REPLICATION_CORP_ENABLED=True,
    BILLING_REPLICATION_CHUNK_DELAYS={'corp': {'clients': 0}},
)
@pytest.mark.pgsql('billing_replication', files=['test_corp_clients.sql'])
async def test_sync_client_ids(
        patch,
        patch_aiohttp_session,
        response_mock,
        fixed_secdist,
        billing_replictaion_cron_app,
        int_api_response,
        expected_db_state,
        mockserver,
):
    @mockserver.json_handler('/corp-int-api/v1/clients/list')
    def clients_list(request):
        passed_updated_at = float(request.query['updated_at'])
        response = [
            resp
            for resp in int_api_response['clients']
            if float(resp['updated_at']) > passed_updated_at
        ]
        return {'clients': response}

    module = 'taxi_billing_replication.stuff.corp.sync_client_ids'
    await cron_run.run_replication_task([module, '-t', '0'])

    pool = billing_replictaion_cron_app.pg_connection_pool
    async with pool.acquire() as conn:
        rows = await conn.fetch('SELECT * FROM corp.clients;')

    assert len(rows) == len(expected_db_state)
    for db_row in rows:
        expected_row = expected_db_state[db_row['id']]
        for key, value in expected_row.items():
            assert db_row[key] == value, db_row
