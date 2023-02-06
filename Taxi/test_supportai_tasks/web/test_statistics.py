#  pylint: disable=protected-access
import datetime

import pytest


@pytest.fixture(name='automated_ch_resp')
def gen_automated_ch_resp():
    return {
        'statistics': {'elapsed': 0.5, 'rows_read': 100, 'bytes_read': 10},
        'meta': [],
        'data': [
            {
                'period_start_date': '2021-03-18 00:00:00',
                'total_number': 10,
                'automated_number': 5,
                'minutes': 12.5,
            },
            {
                'period_start_date': datetime.datetime.fromisoformat(
                    '2021-03-19T00:00:00',
                ),
                'total_number': 20,
                'automated_number': 10,
                'minutes': 23.5,
            },
        ],
        'rows': 2,
    }


@pytest.fixture(name='topic_ch_resp')
def gen_topic_ch_resp():
    return {
        'statistics': {'elapsed': 0.5, 'rows_read': 100, 'bytes_read': 10},
        'meta': [],
        'data': [
            {'topic': 'topic1', 'total_number': 20, 'automated_number': 5},
            {'topic': 'topic2', 'total_number': 10, 'automated_number': 7},
        ],
        'rows': 2,
    }


@pytest.fixture(name='new_automated_ch_resp')
def gen_new_automated_ch_resp():
    return {
        'statistics': {'elapsed': 0.5, 'rows_read': 100, 'bytes_read': 10},
        'meta': [],
        'data': [
            {
                'sure_topic': 'topic1',
                'period_start_date': '2021-03-18 00:00:00',
                'total_number': 10,
                'automated_number': 5,
                'closed_number': 2,
                'forwarded_number': 0,
                'not_answered_number': 2,
                'reopened_number': 1,
                'messages_number': 4,
                'messages_automated_number': 3,
                'minutes': 12.5,
            },
            {
                'sure_topic': 'topic1',
                'period_start_date': '2021-03-19 00:00:00',
                'total_number': 10,
                'automated_number': 4,
                'closed_number': 1,
                'forwarded_number': 0,
                'not_answered_number': 2,
                'reopened_number': 2,
                'messages_number': 3,
                'messages_automated_number': 0,
                'minutes': 13.5,
            },
            {
                'sure_topic': 'topic2',
                'period_start_date': '2021-03-20 00:00:00',
                'total_number': 10,
                'automated_number': 5,
                'closed_number': 1,
                'forwarded_number': 1,
                'not_answered_number': 2,
                'reopened_number': 1,
                'messages_number': 3,
                'messages_automated_number': 1,
                'minutes': 14.5,
            },
        ],
        'rows': 3,
    }


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_automation_statistics(
        web_app_client,
        web_context,
        mock_clickhouse_host,
        response_mock,
        automated_ch_resp,
):
    def handle(*args, **kwargs):
        return response_mock(json=automated_ch_resp)

    host_list = web_context.clickhouse._clickhouse_policy._host_list

    mock_clickhouse_host(clickhouse_response=handle, request_url=host_list[0])

    response = await web_app_client.get(
        '/v2/statistics/automation'
        '?user_id=34'
        '&project_id=1'
        '&period_type=day'
        '&unit=chat'
        '&in_experiment=true',
    )
    assert response.status == 200

    response_json = await response.json()

    assert len(response_json['periods']) == 2

    assert response_json['aggregated']['total_number'] == 30
    assert response_json['aggregated']['automated_number'] == 15
    assert response_json['aggregated']['minutes'] == 36


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_topic_statistics(
        web_app_client,
        web_context,
        mock_clickhouse_host,
        response_mock,
        topic_ch_resp,
        mockserver,
):
    def handle(*args, **kwargs):
        return response_mock(json=topic_ch_resp)

    host_list = web_context.clickhouse._clickhouse_policy._host_list

    mock_clickhouse_host(clickhouse_response=handle, request_url=host_list[0])

    @mockserver.json_handler('/supportai/supportai/v1/topics')
    async def _topics_resp(request):
        return {
            'topics': [
                {'id': '1', 'slug': 'topic1', 'title': 'Topic 1'},
                {'id': '2', 'slug': 'topic2', 'title': 'Topic 2'},
                {'id': '3', 'slug': 'topic3', 'title': 'Topic 3'},
                {'id': '4', 'slug': 'topic4', 'title': 'Topic 4'},
            ],
        }

    response = await web_app_client.get(
        '/v2/statistics/topic?user_id=34&'
        'project_id=1&unit=chat&order_by=total_number',
    )
    assert response.status == 200

    response_json = await response.json()

    assert len(response_json['topics']) == 4

    assert response_json['topics'][0]['total_number'] == 20
    assert response_json['topics'][1]['total_number'] == 10


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_new_automation_statistics(
        web_app_client,
        web_context,
        mock_clickhouse_host,
        response_mock,
        new_automated_ch_resp,
        mockserver,
):
    def handle(*args, **kwargs):
        return response_mock(json=new_automated_ch_resp)

    host_list = web_context.clickhouse._clickhouse_policy._host_list

    mock_clickhouse_host(clickhouse_response=handle, request_url=host_list[0])

    @mockserver.json_handler('/supportai/supportai/v1/topics')
    async def _topics_resp(request):
        return {
            'topics': [
                {'id': '1', 'slug': 'topic1', 'title': 'Topic 1'},
                {'id': '2', 'slug': 'topic2', 'title': 'Topic 2'},
                {'id': '3', 'slug': 'topic3', 'title': 'Topic 3'},
                {'id': '4', 'slug': 'topic4', 'title': 'Topic 4'},
            ],
        }

    response = await web_app_client.get(
        '/v4/statistics/automation'
        '?user_id=34'
        '&project_slug=ya_market'
        '&period_type=day',
    )
    assert response.status == 200

    response_json = await response.json()

    aggregated = response_json['aggregated']
    assert len(aggregated['periods']) == 3
    assert aggregated['periods'][0]['automated_number'] == 5

    assert aggregated['aggregated']['title'] == ''
    assert aggregated['aggregated']['total_number'] == 30
    assert aggregated['aggregated']['messages_number'] == 10
    assert aggregated['aggregated']['messages_automated_number'] == 4
    assert aggregated['aggregated']['reopened_number'] == 4

    assert len(response_json['topics']) == 2
    assert response_json['topics'][0]['aggregated']['title'] == 'Topic 1'
    assert response_json['topics'][0]['aggregated']['messages_number'] == 7
    assert len(response_json['topics'][0]['periods']) == 2
    assert response_json['topics'][0]['periods'][0]['closed_number'] == 2
