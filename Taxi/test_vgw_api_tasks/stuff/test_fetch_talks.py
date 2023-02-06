# pylint: disable=redefined-outer-name,unused-variable
import json
import logging

from aiohttp import web
import pytest

from taxi.maintenance import run
from taxi.util import dates

from vgw_api_tasks import fetch_talks_task
from vgw_api_tasks.generated.cron import run_cron
from vgw_api_tasks.stuff import fetch_talks_long

logger = logging.getLogger(__name__)


@pytest.mark.parametrize('is_error', [True, False])
@pytest.mark.pgsql(
    'vgw_api', files=('gateways.sql', 'forwardings.sql', 'talks.sql'),
)
async def test_fetch_talks(mockserver, is_error, cron_context):
    @mockserver.json_handler('/personal/v2/phones/bulk_store')
    async def _personal_data(request):
        return {'items': [{'id': 'personal_id', 'value': '+77078495185'}]}

    @mockserver.json_handler('/test.com', prefix=True)
    async def _mock_vgw_client_request(request):
        if is_error:
            return web.Response(status=500)
        headers = request.headers
        assert 'Basic gateway_token_' in headers['Authorization']
        return web.Response(
            text=json.dumps(
                [
                    {
                        'callee': '+77055751413',
                        'caller': '+77012045467',
                        'id': '3965F307FC39B1E8C2462119E7672A0F',
                        'length': '42',
                        'redirectionid': 'forwarding_id_1',
                        'start': '2019-01-10T14:52:05+03:00',
                    },
                    {
                        'callee': '+77026477885',
                        'caller': '+77078495185',
                        'id': '4C745411682C32E2FF8D912B011DB2CF',
                        'length': '22',
                        'redirectionid': 'forwarding_id_1',
                        'start': '2019-01-10T14:50:22+03:00',
                    },
                    {
                        'callee': '+77001929692',
                        'caller': '+77472137264',
                        'id': 'F85964B900FB8D6F17AE8DAE3FC6F8BE',
                        'length': '18',
                        'redirectionid': (
                            '7f5ba4122b0367d3bf711745156dcd4a02000000'
                        ),
                        'start': '2019-01-10T14:50:10+03:00',
                    },
                ],
            ),
        )

    try:
        await run_cron.main(
            ['vgw_api_tasks.stuff.fetch_talks_long', '-t', '0'],
        )
        assert not is_error
    except fetch_talks_task.FetchTalksError as exc:
        assert is_error
        assert str(exc) == (
            'talks of some gateways were not fetched: '
            '[\'gateway_id_1\', \'gateway_id_2\', '
            '\'gateway_id_3\', \'gateway_id_5\']'
        )
        return

    pool = cron_context.pg.slave_pool
    async with pool.acquire() as connection:
        rows = await connection.fetch('SELECT * FROM forwardings.talks;')
    talks_by_id = {row['id']: row for row in rows}
    assert '3965F307FC39B1E8C2462119E7672A0F' in talks_by_id
    assert '4C745411682C32E2FF8D912B011DB2CF' in talks_by_id
    assert 'F85964B900FB8D6F17AE8DAE3FC6F8BE' not in talks_by_id


@pytest.mark.pgsql(
    'vgw_api', files=('gateways.sql', 'forwardings.sql', 'talks.sql'),
)
async def test_fetch_talks_results(
        mockserver, cron_context, statistics, get_stats_by_label_values,
):
    @mockserver.json_handler('/test.com', prefix=True)
    async def _mock_vgw_client_request(request):
        headers = request.headers
        assert 'Basic gateway_token_' in headers['Authorization']
        return web.Response(
            text=json.dumps(
                [
                    {
                        'callee': '+77026477885',
                        'caller': '+77078495185',
                        'id': 'TESTID_1',
                        'length': '22',
                        'redirectionid': 'forwarding_id_1',
                        'start': '2019-01-10T14:50:22+03:00',
                        'call_result': {
                            'succeeded': True,
                            'status': 'test_status',
                            'dial_time': 150,
                        },
                    },
                    {
                        'callee': '+77026477885',
                        'caller': '+77078495185',
                        'id': 'TESTID_2',
                        'length': '22',
                        'redirectionid': 'forwarding_id_1',
                        'start': '2019-01-10T14:50:52+03:00',
                        'call_result': {
                            'succeeded': True,
                            'status': 'test_status',
                            'dial_time': 150,
                        },
                    },
                    {
                        'callee': '+77026477885',
                        'caller': 'bravo+77078495185-lima',
                        'id': 'TESTID_3',
                        'length': '22',
                        'redirectionid': 'forwarding_id_1',
                        'start': '2019-01-10T14:50:52+03:00',
                        'call_result': {
                            'succeeded': True,
                            'status': 'test_status',
                            'dial_time': 150,
                        },
                    },
                ],
            ),
        )

    @mockserver.json_handler('/personal/v2/phones/bulk_store')
    async def _personal_data(request):
        return {'items': [{'id': 'personal_id', 'value': '+77078495185'}]}

    await run_cron.main(['vgw_api_tasks.stuff.fetch_talks_long', '-t', '0'])

    pool = cron_context.pg.slave_pool
    async with pool.acquire() as connection:
        rows = await connection.fetch('SELECT * FROM forwardings.talks;')
    talks_by_id = {row['id']: row for row in rows}
    assert 'TESTID_1' in talks_by_id
    assert 'TESTID_2' in talks_by_id
    assert 'TESTID_3' in talks_by_id
    talk = talks_by_id['TESTID_1']
    assert talk['succeeded']
    assert talk['status'] == 'test_status'
    assert talk['dial_time'] == 150
    assert talk['caller_phone_id'] == 'personal_id'
    talk = talks_by_id['TESTID_3']
    assert talk['caller_phone_id'] == 'personal_id'


def _sort_sensors(sensors: list) -> list:
    return sorted(sensors, key=lambda x: x['sensor'])


def _check_handle_metrics(
        is_error: bool,
        gateways: list,
        get_stats_by_label_values,
        cron_context,
):
    if is_error:
        expected_sensors = [
            {
                'sensor': f'gateway.{gateway}.handle.GET_/talks.500.count',
                'value': 1,
            }
            for gateway in gateways
        ]
    else:
        expected_sensors = [
            {
                'sensor': f'gateway.{gateway}.handle.GET_/talks.200.count',
                'value': 1,
            }
            for gateway in gateways
        ]
    expected_sensors.extend(
        [
            {
                'sensor': f'gateway.{gateway}.handle.GET_/talks.timings',
                'value': None,
            }
            for gateway in gateways
        ],
    )
    stats = get_stats_by_label_values(cron_context, {})
    sensors = [
        {
            'sensor': stat['labels']['sensor'],
            'value': (
                stat['value']
                if 'timings' not in stat['labels']['sensor']
                else None
            ),
        }
        for stat in stats
        if stat['labels']['sensor'].startswith('gateway')
    ]
    assert _sort_sensors(sensors) == _sort_sensors(expected_sensors)


async def _check_business_metrics(is_error: bool, gateways: list, statistics):
    stats = await statistics.dump()
    if is_error:
        assert not stats
        return
    region = {'gateway_id_1': 0, 'gateway_id_2': 1}
    total = {'gateway_id_1': 2, 'gateway_id_2': 1}
    success = {'gateway_id_1': 1}
    fail = {'gateway_id_1': 1}
    short = {'gateway_id_2': 1}
    length = {'gateway_id_1': 64, 'gateway_id_2': 18}
    expected_metrics = {
        f'talks.total.gateway.{gateway}'
        f'.region.{region[gateway]}': total[gateway]
        for gateway in gateways
        if gateway in total
    }
    expected_metrics.update(
        {
            f'talks.success.gateway.{gateway}'
            f'.region.{region[gateway]}': success[gateway]
            for gateway in gateways
            if gateway in success
        },
    )
    expected_metrics.update(
        {
            f'talks.fail.gateway.{gateway}'
            f'.region.{region[gateway]}': fail[gateway]
            for gateway in gateways
            if gateway in fail
        },
    )
    expected_metrics.update(
        {
            f'talks.short.gateway.{gateway}'
            f'.region.{region[gateway]}': short[gateway]
            for gateway in gateways
            if gateway in short
        },
    )
    expected_metrics.update(
        {
            f'talks.length.sum.gateway.{gateway}': length[gateway]
            for gateway in gateways
            if gateway in length
        },
    )
    assert stats[0]['service'] == 'vgw_api_tasks_cron'
    metrics = {
        metric['name']: metric['value']
        for metric in stats[0]['metrics']
        if metric['name'].startswith('talks')
    }
    assert metrics == expected_metrics


@pytest.mark.parametrize('is_error', [True, False])
@pytest.mark.pgsql(
    'vgw_api', files=('gateways.sql', 'forwardings.sql', 'talks.sql'),
)
@pytest.mark.config(
    VGW_API_GATEWAY_SHORT_TALKS_CHECK_SETTINGS={
        '__default__': {'short_talk_max_len_s': 3},
        'gateway_id_2': {'short_talk_max_len_s': 20},
    },
)
async def test_metrics(
        mockserver,
        is_error,
        cron_context,
        loop,
        statistics,
        get_stats_by_label_values,
):
    @mockserver.json_handler('/personal/v2/phones/bulk_store')
    async def _personal_data(request):
        return {'items': [{'id': 'personal_id', 'value': '+77078495185'}]}

    @mockserver.json_handler('/test.com', prefix=True)
    async def _mock_vgw_client_request(request):
        if is_error:
            return web.Response(status=500)
        headers = request.headers
        assert 'Basic gateway_token_' in headers['Authorization']
        return web.Response(
            text=json.dumps(
                [
                    {
                        'callee': '+77055751413',
                        'caller': '+77012045467',
                        'id': '3965F307FC39B1E8C2462119E7672A0F',
                        'length': '42',
                        'redirectionid': 'forwarding_id_1',
                        'start': '2019-01-10T14:52:05+03:00',
                        'call_result': {
                            'succeeded': True,
                            'status': 'test_status',
                            'dial_time': 150,
                        },
                    },
                    {
                        'callee': '+77055751413',
                        'caller': '+77012045467',
                        'id': 'D0E003D9A621458337BA669F37BA669F',
                        'length': '42',
                        'redirectionid': 'forwarding_id_1',
                        'start': '2019-01-10T14:52:05+03:00',
                        'call_result': {
                            'succeeded': False,
                            'status': 'test_status',
                            'dial_time': 150,
                        },
                    },
                    {
                        'callee': '+77026477885',
                        'caller': '+77078495185',
                        'id': '4C745411682C32E2FF8D912B011DB2CF',
                        'length': '22',
                        'redirectionid': 'forwarding_id_1',
                        'start': '2019-01-10T14:50:22+03:00',
                        'call_result': {
                            'succeeded': True,
                            'status': 'test_status',
                            'dial_time': 150,
                        },
                    },
                    {
                        'callee': '+77001929692',
                        'caller': '+77472137264',
                        'id': 'F85964B900FB8D6F17AE8DAE3FC6F8BE',
                        'length': '18',
                        'redirectionid': 'forwarding_id_2',
                        'start': '2019-01-10T14:50:10+03:00',
                    },
                ],
            ),
        )

    stuff_context = run.StuffContext(
        lock=None,
        task_id='fetch_talks_long',
        start_time=dates.utcnow(),
        data=cron_context,
    )
    try:
        await fetch_talks_long.do_stuff(stuff_context, loop)
        assert not is_error
    except fetch_talks_task.FetchTalksError:
        assert is_error

    gateways = ['gateway_id_1', 'gateway_id_2', 'gateway_id_3', 'gateway_id_5']
    _check_handle_metrics(
        is_error, gateways, get_stats_by_label_values, cron_context,
    )
    await _check_business_metrics(is_error, gateways, statistics)


@pytest.mark.pgsql(
    'vgw_api', files=('gateways.sql', 'forwardings.sql', 'talks.sql'),
)
@pytest.mark.config(
    VGW_API_ENABLING_SAVE_DIAL_TIME={
        '__default__': False,
        'gateway_id_1': True,
    },
)
async def test_not_save_dial_time(mockserver, pgsql):
    @mockserver.json_handler('/personal/v2/phones/bulk_store')
    async def _personal_data(request):
        return {'items': [{'id': 'personal_id', 'value': '+77078495185'}]}

    @mockserver.json_handler('/test.com', prefix=True)
    async def _mock_vgw_client_request(request):
        headers = request.headers
        assert 'Basic gateway_token_' in headers['Authorization']
        return web.Response(
            text=json.dumps(
                [
                    {
                        'callee': '+77026477885',
                        'caller': '+77078495185',
                        'id': '4C745411682C32E2FF8D912B011DB2CF',
                        'length': '22',
                        'redirectionid': 'forwarding_id_1',
                        'start': '2019-01-10T14:50:22+03:00',
                        'call_result': {'dial_time': 5},
                    },
                ],
            ),
        )

    await run_cron.main(['vgw_api_tasks.stuff.fetch_talks_long', '-t', '0'])

    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        """SELECT id,
            length, forwarding_id, caller_phone, caller_phone_id,
            voip_succeeded, s3_key, succeeded, status, dial_time
            FROM forwardings.talks
            ORDER BY id;""",
    )

    assert cursor.fetchall() == [
        (
            '3965F307FC39B1E8C2462119E7672A0F',
            10,
            'forwarding_id_1',
            '',
            None,
            None,
            None,
            None,
            None,
            None,
        ),
        (
            '4C745411682C32E2FF8D912B011DB2CF',
            22,
            'forwarding_id_1',
            '+77078495185',
            'personal_id',
            None,
            None,
            None,
            None,
            5,
        ),
    ]
