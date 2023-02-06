#  pylint: disable=protected-access

import pytest

from supportai_tasks.generated.cron import run_cron


@pytest.fixture(name='project_dates_ch_resp')
def gen_project_dates_ch_resp():
    return {
        'statistics': {'elapsed': 0.5, 'rows_read': 100, 'bytes_read': 10},
        'meta': [],
        'data': [
            {'max_ts': '2021-06-23 00:00:00', 'project_id': 'ya_market'},
            {'max_ts': '2021-06-22 00:00:00', 'project_id': 'ya_lavka'},
        ],
        'rows': 2,
    }


@pytest.fixture(name='projects_stats_ch_resp')
def gen_projects_stats_ch_resp():
    return {
        'statistics': {'elapsed': 0.5, 'rows_read': 100, 'bytes_read': 10},
        'meta': [],
        'data': [
            {
                'ts': '2021-06-23 00:00:00',
                'project_id': 'ya_market',
                'chat_id': '1',
                'sure_topic': None,
                'most_probable_topic': None,
                'iteration': 0,
                'in_experiment': False,
                'replied': 1,
                'closed': 0,
                'forwarded': 0,
            },
            {
                'ts': '2021-06-22 00:00:00',
                'project_id': 'ya_lavka',
                'chat_id': '2',
                'sure_topic': None,
                'most_probable_topic': None,
                'iteration': 0,
                'in_experiment': False,
                'replied': 1,
                'closed': 0,
                'forwarded': 0,
            },
        ],
        'rows': 2,
    }


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_update_demo_stats(
        cron_context,
        mock_clickhouse_host,
        response_mock,
        web_app_client,
        project_dates_ch_resp,
        projects_stats_ch_resp,
):
    def handle(*args, **kwargs):

        if handle.times_called == 0:
            response = response_mock(json=project_dates_ch_resp)
        elif handle.times_called == 1:
            response = response_mock(json=projects_stats_ch_resp)
        else:
            response = response_mock(json={})

        handle.times_called += 1
        return response

    handle.times_called = 0

    host_list = cron_context.clickhouse._clickhouse_policy._host_list

    mock_clickhouse_host(clickhouse_response=handle, request_url=host_list[0])

    await run_cron.main(
        ['supportai_tasks.crontasks.update_demo_stats', '-t', '0'],
    )
