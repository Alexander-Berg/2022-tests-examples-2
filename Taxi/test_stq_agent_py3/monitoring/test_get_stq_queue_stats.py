import pytest

from stq_agent_py3.monitoring import stq_stats


@pytest.mark.parametrize(
    'queues_errors_stats, queue_count_tasks, stq_configs',
    [
        (
            {
                'queue_name': stq_stats.QueueErrorsStat(
                    failed=None, abandoned=None,
                ),
            },
            {'queue_name': None},
            [{'_id': 'queue_name', 'monitoring': {'thresholds': {}}}],
        ),
    ],
)
async def test(
        mockserver,
        web_context,
        queues_errors_stats,
        queue_count_tasks,
        stq_configs,
):
    @mockserver.handler('/nda', prefix=True)
    async def _nda_url_generator(request):
        return mockserver.make_response(
            'https://nda.ya.ru/t/aaaabbb',
            headers={'Content-Type': 'text/javascript; charset=utf-8'},
        )

    result = await stq_stats.get_stq_queue_stats(
        web_context, queues_errors_stats, queue_count_tasks, stq_configs, True,
    )

    assert result == {
        'queue_name': stq_stats.QueueStats(
            status=stq_stats.STATUS_CRITICAL,
            message=(
                'queue_name (https://nda.ya.ru/t/aaaabbb): '
                'No info about tasks in queue (check errors in cron logs '
                'stq_agent_py3-push_checks_to_juggler)'
            ),
            failed=None,
            abandoned=None,
            no_data=True,
        ),
    }
