# pylint: disable=inconsistent-return-statements,redefined-outer-name,
import pytest

from taxi.pg import pool

from taxi_strongbox.generated.cron import run_cron


@pytest.mark.pgsql('strongbox', files=['test_refresh_secrets.sql'])
async def test_refresh_secrets(cron_context, mockserver):
    @mockserver.json_handler('/vault-api/', prefix=True)
    def _request(request):
        headers = request.headers
        url = request.url
        assert headers['Authorization'] == 'OAuth vault_api_token'
        if 'secrets/' in url:
            if 'YAV_UUID_1' in url:
                return mockserver.make_response(
                    json={
                        'status': 'ok',
                        'secret': {
                            'secret_versions': [
                                {
                                    'version': 'VERSION_UUID_0',
                                    'created_at': 100,
                                },
                                {
                                    'version': 'VERSION_UUID_1',
                                    'created_at': 200,
                                },
                            ],
                        },
                    },
                )
            if 'YAV_UUID_2' in url:
                return mockserver.make_response(
                    json={
                        'status': 'ok',
                        'secret': {
                            'secret_versions': [
                                {
                                    'version': 'VERSION_UUID_2',
                                    'created_at': 300,
                                },
                                {
                                    'version': 'VERSION_UUID_3',
                                    'created_at': 400,
                                },
                            ],
                        },
                    },
                )
            if 'YAV_UUID_3' in url:
                return mockserver.make_response(
                    json={
                        'status': 'ok',
                        'secret': {
                            'secret_versions': [
                                {
                                    'version': 'VERSION_UUID_5',
                                    'created_at': 400,
                                },
                            ],
                        },
                    },
                )

    await run_cron.main(
        ['taxi_strongbox.crontasks.refresh_secrets', '-t', '0'],
    )

    master_pool: pool.Pool = cron_context.pg.master_pool
    async with master_pool.acquire() as conn:
        rows = await conn.fetch('SELECT * FROM secrets.secrets')
    updated_values = {row['updated'] for row in rows}
    assert 150 in updated_values
    assert 450 not in updated_values
    assert {row['version_uuid'] for row in rows} == {
        'VERSION_UUID_1',
        'VERSION_UUID_3',
    }
    async with master_pool.acquire() as conn:
        rows = await conn.fetch('SELECT * FROM secrets.groups')
    assert {row['version_uuid'] for row in rows} == {'VERSION_UUID_5'}
