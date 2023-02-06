import socket

import pytest

from stq_agent_py3.common import stq_config
from stq_agent_py3.generated.cron import run_cron

NDA_URLS = {
    '/stq-queue/edit/processing': 'aaabbbb',
    '/stq-queue/edit/processing_zero': 'aaabbbb_0',
    '/stq-queue/edit/processing_v2': 'ccccddddeeee',
    '/stq-queue/edit/non_critical': 'fffttttqqq',
    '/stq-queue/edit/without_problems': 'lalala',
    '/stq-queue/edit/no_data_critical': 'lololo',
    '/stq-queue/edit/no_data_non-critical': 'lelele',
}


@pytest.mark.fillstqdb(
    collections=[
        ('stq', 'dbstqorder0', 'processing_0'),
        ('stq', 'dbstqorder0', 'processing_1'),
        ('stq', 'dbstqorder0', 'processing_3'),
        ('stq', 'dbstqorder0', 'processing_4'),
        ('stq', 'dbstqorder0', 'processing_v2_0'),
        ('stq', 'dbstqorder0', 'processing_v2_1'),
    ],
)
@pytest.mark.now('2020-01-01T23:12:13.0')
async def test(mockserver, web_context):
    @mockserver.handler('/nda', prefix=True)
    async def _nda_url_generator(request):
        return mockserver.make_response(
            'https://nda.ya.ru/t/{}'.format(NDA_URLS[request.query['url']]),
            headers={'Content-Type': 'text/javascript; charset=utf-8'},
        )

    @mockserver.json_handler('/stq-agent/queues/stats')
    async def _stq_agent_stats(request):
        queues = request.json.get('queues', [])
        if 'processing_in_bad_db' in queues:
            return mockserver.make_response('', status=500)
        stats = {
            'queues': {
                queue: {'failed': 2, 'abandoned': 10}
                for queue in queues
                if queue
                not in (
                    'without_problems',
                    'no_data_critical',
                    'no_data_non-critical',
                )
            },
        }
        stats['queues'].update(
            {'without_problems': {'failed': 0, 'abandoned': 0}},
        )
        return stats

    response = []

    @mockserver.json_handler('/juggler/events')
    async def _juggler(request):
        response.append(request.json)
        return {'events': [], 'accepted_events': 0, 'success': True}

    await run_cron.main(
        ['stq_agent_py3.crontasks.push_checks_to_juggler', '-t', '0'],
    )
    config = await stq_config.get_configs(web_context, need_meta_data=True)
    assert (
        [(doc.queue_name, doc.queue_stats.serialize()) for doc in config]
        == [
            (
                'processing',
                {
                    'failed': 2,
                    'abandoned': 10,
                    'status': 'CRIT',
                    'no_data': False,
                    'datetime_of_actual_data': '2020-01-01 23:12:13',
                },
            ),
            (
                'processing_in_bad_db',
                {
                    'abandoned': 0,
                    'failed': 0,
                    'no_data': True,
                    'status': 'WARN',
                },
            ),
            (
                'processing_zero',
                {
                    'failed': 2,
                    'abandoned': 10,
                    'status': 'CRIT',
                    'no_data': False,
                    'datetime_of_actual_data': '2020-01-01 23:12:13',
                },
            ),
            (
                'processing_v2',
                {
                    'failed': 2,
                    'abandoned': 10,
                    'status': 'CRIT',
                    'no_data': False,
                    'datetime_of_actual_data': '2020-01-01 23:12:13',
                },
            ),
            (
                'non_critical',
                {
                    'failed': 2,
                    'abandoned': 10,
                    'status': 'CRIT',
                    'no_data': False,
                    'datetime_of_actual_data': '2020-01-01 23:12:13',
                },
            ),
            (
                'without_problems',
                {
                    'failed': 0,
                    'abandoned': 0,
                    'status': 'OK',
                    'no_data': False,
                    'datetime_of_actual_data': '2020-01-01 23:12:13',
                },
            ),
            (
                'no_data_critical',
                {
                    'abandoned': 14,
                    'failed': 35,
                    'no_data': True,
                    'status': 'WARN',
                    'datetime_of_actual_data': '2021-11-29 16:23:11.187925',
                },
            ),
            (
                'no_data_non-critical',
                {
                    'abandoned': 14,
                    'failed': 35,
                    'no_data': True,
                    'status': 'OK',
                    'datetime_of_actual_data': '2021-11-29 16:23:11.187925',
                },
            ),
        ]
    )
    host = socket.gethostname()
    assert response == [
        {
            'source': 'stq-agent-py3',
            'events': [
                {
                    'description': (
                        'CRIT: '
                        'processing (https://nda.ya.ru/t/aaabbbb): '
                        '2 failed, 10 abandoned, '
                        '3 tasks queued in all shards (too many). '
                        'processing_v2 (https://nda.ya.ru/t/ccccddddeeee): '
                        '2 failed, 10 abandoned, '
                        '5 tasks queued in all shards (too many). '
                        'processing_zero (https://nda.ya.ru/t/aaabbbb_0): '
                        '2 failed, 10 abandoned; '
                        'WARN: failed: no data for no_data_critical. '
                        'failed: no data for processing_in_bad_db'
                    ),
                    'service': 'stq-agent-py3-stq-fails-critical',
                    'status': 'CRIT',
                    'instance': '',
                    'host': host,
                },
                {
                    'description': (
                        'CRIT: non_critical (https://nda.ya.ru/t/fffttttqqq): '
                        '2 failed, 10 abandoned, '
                        '3 tasks queued in all shards (too many)'
                    ),
                    'service': 'stq-agent-py3-stq-fails-non-critical',
                    'status': 'CRIT',
                    'instance': '',
                    'host': host,
                },
                {
                    'description': (
                        'CRIT: '
                        'non_critical (https://nda.ya.ru/t/fffttttqqq): '
                        '2 failed, 10 abandoned, '
                        '3 tasks queued in all shards (too many). '
                        'processing (https://nda.ya.ru/t/aaabbbb): '
                        '2 failed, 10 abandoned, '
                        '3 tasks queued in all shards (too many). '
                        'processing_zero (https://nda.ya.ru/t/aaabbbb_0): '
                        '2 failed, 10 abandoned; '
                        'WARN: failed: no data for no_data_critical. '
                        'failed: no data for processing_in_bad_db'
                    ),
                    'service': 'taxi-stq-fails-ordercycle',
                    'status': 'CRIT',
                    'instance': '',
                    'host': host,
                },
                {
                    'description': (
                        'CRIT: '
                        'processing_v2 (https://nda.ya.ru/t/ccccddddeeee): '
                        '2 failed, 10 abandoned, '
                        '5 tasks queued in all shards (too many)'
                    ),
                    'service': 'taxi-stq-fails-ordercycle_v2',
                    'status': 'CRIT',
                    'instance': '',
                    'host': host,
                },
            ],
        },
    ]
