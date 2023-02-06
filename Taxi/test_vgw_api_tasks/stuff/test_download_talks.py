# pylint: disable=redefined-outer-name,unused-variable
from aiohttp import web
import pytest

from vgw_api_tasks.generated.cron import run_cron


@pytest.mark.parametrize(
    'error', [None, 'vgw_client', 'record_format', 'not_found'],
)
@pytest.mark.pgsql(
    'vgw_api', files=('gateways.sql', 'forwardings.sql', 'talks.sql'),
)
@pytest.mark.client_experiments3(
    consumer='vgw_api_tasks/download_talks_task',
    config_name='config_vgw_api_tasks_download_talks',
    args=[],
    value={
        'whitelist': {'region_ids': [100], 'gateway_ids': ['gateway_id_1']},
    },
    # all regions and all gatesays
)
async def test_download_talks(cron_context, error, mockserver):
    already_downloaded = False

    @mockserver.json_handler('/test.com', prefix=True)
    def _request(request):
        assert not already_downloaded
        assert 'too_fresh_talk' not in request.url
        if error == 'vgw_client':
            return web.Response(status=500)
        headers = request.headers
        assert 'Basic gateway_token_' in headers['Authorization']
        if error == 'record_format':
            return web.Response(text='test')
        if error == 'not_found':
            return web.Response(status=404)
        return web.Response(text='RIFF test')

    await run_cron.main(
        ['vgw_api_tasks.stuff.download_talks', '-t', '0', '-d'],
    )
    if not error:
        result = await cron_context.client_mds_s3.download_content(
            '3965F307FC39B1E8C2462119E7672A0F',
        )
        assert result == b'RIFF test'

        # check that second launch will do nothing
        already_downloaded = True
        await run_cron.main(['vgw_api_tasks.stuff.download_talks', '-t', '0'])
        pool = cron_context.pg.slave_pool
        async with pool.acquire() as connection:
            row = await connection.fetchrow(
                'SELECT * FROM forwardings.talks WHERE s3_key IS NOT NULL;',
            )
        assert row
        assert row['s3_key'] == '3965F307FC39B1E8C2462119E7672A0F'


async def run_task_and_check_results(
        cron_context, already_downloaded, set_of_keys,
):
    await run_cron.main(
        ['vgw_api_tasks.stuff.download_talks', '-t', '0', '-d'],
    )
    for key in set_of_keys:
        result = await cron_context.client_mds_s3.download_content(key)
        assert result == b'RIFF test'

    pool = cron_context.pg.slave_pool
    async with pool.acquire() as connection:
        rows = await connection.fetch(
            'SELECT s3_key FROM forwardings.talks WHERE s3_key IS NOT NULL;',
        )
    assert {elem['s3_key'] for elem in rows} == set_of_keys

    # check that second launch will do nothing
    already_downloaded = True  # noqa: F841
    await run_cron.main(['vgw_api_tasks.stuff.download_talks', '-t', '0'])
    pool = cron_context.pg.slave_pool
    async with pool.acquire() as connection:
        rows = await connection.fetch(
            'SELECT s3_key FROM forwardings.talks WHERE s3_key IS NOT NULL;',
        )
    assert {elem['s3_key'] for elem in rows} == set_of_keys


@pytest.mark.pgsql(
    'vgw_api',
    files=(
        'gateways_for_test_download_with_whitelist.sql',
        'forwardings_for_test_download_with_whitelist.sql',
        'talks_for_test_download_with_whitelist.sql',
    ),
)
@pytest.mark.client_experiments3(
    consumer='vgw_api_tasks/download_talks_task',
    config_name='config_vgw_api_tasks_download_talks',
    args=[],
    value={
        'whitelist': {
            'region_ids': [161, 163],
            'gateway_ids': ['gateway_id_1', 'gateway_id_2'],
        },
    },
)
async def test_download_all(cron_context, mockserver):
    already_downloaded = False

    @mockserver.json_handler('/test.com', prefix=True)
    def _request(request):
        assert not already_downloaded
        assert 'too_fresh_talk' not in request.url
        headers = request.headers
        assert 'Basic gateway_token_' in headers['Authorization']
        return web.Response(text='RIFF test')

    await run_task_and_check_results(
        cron_context, already_downloaded, {'key1', 'key2', 'key3', 'key4'},
    )


@pytest.mark.pgsql(
    'vgw_api',
    files=(
        'gateways_for_test_download_with_whitelist.sql',
        'forwardings_for_test_download_with_whitelist.sql',
        'talks_for_test_download_with_whitelist.sql',
    ),
)
@pytest.mark.client_experiments3(
    consumer='vgw_api_tasks/download_talks_task',
    config_name='config_vgw_api_tasks_download_talks',
    args=[],
    value={
        'whitelist': {
            'region_ids': [161, 163],
            'gateway_ids': ['gateway_id_1'],
        },
    },
)
async def test_download_many_region_ids(cron_context, mockserver):
    already_downloaded = False

    @mockserver.json_handler('/test.com', prefix=True)
    def _request(request):
        assert not already_downloaded
        assert 'too_fresh_talk' not in request.url
        headers = request.headers
        assert 'Basic gateway_token_' in headers['Authorization']
        return web.Response(text='RIFF test')

    await run_task_and_check_results(
        cron_context, already_downloaded, {'key1', 'key2'},
    )


@pytest.mark.pgsql(
    'vgw_api',
    files=(
        'gateways_for_test_download_with_whitelist.sql',
        'forwardings_for_test_download_with_whitelist.sql',
        'talks_for_test_download_with_whitelist.sql',
    ),
)
@pytest.mark.client_experiments3(
    consumer='vgw_api_tasks/download_talks_task',
    config_name='config_vgw_api_tasks_download_talks',
    args=[],
    value={
        'whitelist': {
            'region_ids': [161],
            'gateway_ids': ['gateway_id_1', 'gateway_id_2'],
        },
    },
)
async def test_download_many_gateway_ids(cron_context, mockserver):
    already_downloaded = False

    @mockserver.json_handler('/test.com', prefix=True)
    def _request(request):
        assert not already_downloaded
        assert 'too_fresh_talk' not in request.url
        headers = request.headers
        assert 'Basic gateway_token_' in headers['Authorization']
        return web.Response(text='RIFF test')

    await run_task_and_check_results(
        cron_context, already_downloaded, {'key2', 'key4'},
    )


@pytest.mark.pgsql(
    'vgw_api',
    files=(
        'gateways_for_test_download_with_whitelist.sql',
        'forwardings_for_test_download_with_whitelist.sql',
        'talks_for_test_download_with_whitelist.sql',
    ),
)
@pytest.mark.client_experiments3(
    consumer='vgw_api_tasks/download_talks_task',
    config_name='config_vgw_api_tasks_download_talks',
    args=[],
    value={
        'whitelist': {'region_ids': [163], 'gateway_ids': ['gateway_id_1']},
    },
)
async def test_download_by_region_id_and_by_gateways(cron_context, mockserver):
    already_downloaded = False

    @mockserver.json_handler('/test.com', prefix=True)
    def _request(request):
        assert not already_downloaded
        assert 'too_fresh_talk' not in request.url
        headers = request.headers
        assert 'Basic gateway_token_' in headers['Authorization']
        return web.Response(text='RIFF test')

    await run_task_and_check_results(
        cron_context, already_downloaded, {'key1'},
    )


@pytest.mark.pgsql(
    'vgw_api',
    files=(
        'gateways_for_test_download_with_whitelist.sql',
        'forwardings_for_test_download_with_whitelist.sql',
        'talks_for_test_download_with_whitelist.sql',
    ),
)
@pytest.mark.client_experiments3(
    consumer='vgw_api_tasks/download_talks_task',
    config_name='config_vgw_api_tasks_download_talks',
    args=[],
    value={'whitelist': {'region_ids': [163], 'gateway_ids': []}},
)
async def test_no_one_download_by_gateway_ids(cron_context):

    await run_cron.main(
        ['vgw_api_tasks.stuff.download_talks', '-t', '0', '-d'],
    )

    pool = cron_context.pg.slave_pool
    async with pool.acquire() as connection:
        rows = await connection.fetch(
            'SELECT s3_key FROM forwardings.talks WHERE s3_key IS NOT NULL;',
        )
    assert not rows


@pytest.mark.pgsql(
    'vgw_api',
    files=(
        'gateways_for_test_download_with_whitelist.sql',
        'forwardings_for_test_download_with_whitelist.sql',
        'talks_for_test_download_with_whitelist.sql',
    ),
)
@pytest.mark.client_experiments3(
    consumer='vgw_api_tasks/download_talks_task',
    config_name='config_vgw_api_tasks_download_talks',
    args=[],
    value={'whitelist': {'region_ids': [], 'gateway_ids': ['gateway_id_1']}},
)
async def test_no_one_download_by_region_ids(cron_context):
    await run_cron.main(
        ['vgw_api_tasks.stuff.download_talks', '-t', '0', '-d'],
    )

    pool = cron_context.pg.slave_pool
    async with pool.acquire() as connection:
        rows = await connection.fetch(
            'SELECT s3_key FROM forwardings.talks WHERE s3_key IS NOT NULL;',
        )
    assert not rows


@pytest.mark.pgsql(
    'vgw_api',
    files=(
        'gateways_for_test_download_with_whitelist.sql',
        'forwardings_for_test_download_with_whitelist.sql',
        'talks_for_test_download_with_whitelist.sql',
    ),
)
@pytest.mark.client_experiments3(
    consumer='vgw_api_tasks/download_talks_task',
    config_name='config_vgw_api_tasks_download_talks',
    args=[],
    value={'whitelist': {'region_ids': [], 'gateway_ids': []}},
)
async def test_no_one_download_by_whitelist(cron_context):

    await run_cron.main(
        ['vgw_api_tasks.stuff.download_talks', '-t', '0', '-d'],
    )

    pool = cron_context.pg.slave_pool
    async with pool.acquire() as connection:
        rows = await connection.fetch(
            'SELECT s3_key FROM forwardings.talks WHERE s3_key IS NOT NULL;',
        )
    assert not rows
