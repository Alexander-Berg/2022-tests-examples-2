# pylint: disable=protected-access
import collections
import datetime
import re
from typing import Any
from typing import Dict
import urllib.parse

import pytest

from test_supportai_statistics import clickhouse_responses

COUNTERS_COLUMNS_FOR_GROUPED = {
    'total_seconds',
    'calls',
    'call_attempts',
    'connected_first_attempt',
    'connected_second_attempt',
    'ended_count',
    'forwarded_count',
    'no_answer_count',
    'user_busy_count',
    'hangup_count',
    'error_count',
}

CLICKHOUSE_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
CLICKHOUSE_DATE_FORMAT = '%Y-%m-%d'

SEPARATED_CALLS_DATETIME_FIELDS = {'initiated_at', 'started_at'}


def validate_ch_request(req_args, req_kwargs):
    url = req_args[1]
    query_params = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    assert query_params.pop('database', [None])[0] == 'supportai_api'
    params_for_template = set(query_params.keys())
    params_for_template = {param[6:] for param in params_for_template}

    db_query = req_kwargs['data']
    template_params = re.findall(r'{[^:]+:', db_query)
    template_params = {param[1:-1] for param in template_params}
    assert template_params <= params_for_template


@pytest.mark.parametrize(
    ('group_by', 'empty_ch_response'),
    [('batch_id', False), ('hour', False), ('month', False), ('month', True)],
)
@pytest.mark.parametrize('tags', [[], ['first'], ['first', 'second']])
async def test_get_calls_statistics_grouped(
        web_context,
        web_app_client,
        group_by,
        empty_ch_response,
        mock_clickhouse_host,
        response_mock,
        tags,
):
    def mock_grouped(*args, **kwargs):
        validate_ch_request(args, kwargs)
        if empty_ch_response:
            return response_mock(json=clickhouse_responses.get_empty())
        ch_response = clickhouse_responses.get_calls_grouped(group_by, tags)
        return response_mock(json=ch_response)

    host_list = web_context.clickhouse._clickhouse_policy._host_list
    mock_clickhouse_host(
        clickhouse_response=mock_grouped, request_url=host_list[0],
    )

    params = {
        'project_slug': 'some_project',
        'user_id': '12321',
        'direction': 'outgoing',
        'start': '10',
        'end': '20',
        'group_by': group_by,
    }
    if tags:
        params['tags'] = ','.join(tags)

    response = await web_app_client.get(
        'v1/statistics/calls/grouped', params=params,
    )
    assert response.status == 200

    response_json = await response.json()
    aggregated = response_json.pop('aggregated', None)
    groups = response_json.pop('groups', None)
    if empty_ch_response:
        expected_aggregated = {
            'title': '',
            'total_seconds': 0,
            'calls': 0,
            'call_attempts': 0,
            'connected_first_attempt': 0,
            'connected_second_attempt': 0,
            'ended_count': 0,
            'forwarded_count': 0,
            'no_answer_count': 0,
            'user_busy_count': 0,
            'hangup_count': 0,
            'error_count': 0,
        }
        if tags:
            expected_aggregated['tag_counters'] = [
                {'tag_name': tag, 'count': 0} for tag in tags
            ]
        assert aggregated == expected_aggregated
        assert groups == []
        return

    assert aggregated and groups and not response_json

    dt_keys_to_format = {'start_at'}
    if group_by != 'batch_id':
        dt_keys_to_format.add('title')

    expected_groups = clickhouse_responses.get_calls_grouped(group_by, tags)[
        'data'
    ]
    expected_aggregated: Dict[str, Any] = collections.defaultdict(int)
    if tags:
        expected_aggregated['tag_counters'] = [
            {'tag_name': tag, 'count': 0} for tag in tags
        ]
    for group_idx, expected_group in enumerate(expected_groups):
        if group_by == 'batch_id':
            expected_group['batch_status'] = 'finished'
        for key, value in expected_group.items():
            if key in COUNTERS_COLUMNS_FOR_GROUPED:
                expected_group[key] = int(value)
                expected_aggregated[key] += int(value)
            elif key in dt_keys_to_format:
                dt_format = (
                    CLICKHOUSE_DATETIME_FORMAT
                    if not key == 'title' or not group_by == 'month'
                    else CLICKHOUSE_DATE_FORMAT
                )
                expected_group[key] = (
                    datetime.datetime.strptime(value, dt_format)
                    .replace(
                        tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
                    )
                    .isoformat()
                )
        if group_idx == 0:
            expected_aggregated['start_at'] = expected_group['start_at']
        if tags:
            expected_group['tag_counters'] = [
                {
                    'tag_name': tag,
                    'count': expected_group.pop(f'{tag}_tag_number', None),
                }
                for tag in tags
            ]
            for idx, tag in enumerate(tags):
                expected_aggregated['tag_counters'][idx][
                    'count'
                ] += expected_group['tag_counters'][idx]['count']

    expected_aggregated['title'] = ''

    assert groups == expected_groups
    assert aggregated == expected_aggregated


async def test_get_calls_statistics_separated(
        web_context,
        web_app_client,
        clickhouse_query_storage,
        mock_clickhouse_host,
        response_mock,
):
    def mock_separated(*args, **kwargs):
        validate_ch_request(args, kwargs)
        return response_mock(
            json=clickhouse_responses.get_separate_calls(limit=-1, offset=0),
        )

    host_list = web_context.clickhouse._clickhouse_policy._host_list
    mock_clickhouse_host(
        clickhouse_response=mock_separated, request_url=host_list[0],
    )

    response = await web_app_client.get(
        'v1/statistics/calls/separated'
        '?project_slug=some_project&user_id=12321&start=1&end=10'
        '&direction=outgoing&limit=10&offset=0',
    )
    assert response.status == 200
    response_json = await response.json()
    calls = response_json.pop('calls', None)
    assert calls and not response_json

    expected_calls = clickhouse_responses.get_separate_calls(
        limit=-1, offset=0,
    )['data']
    for expected_call in expected_calls:
        none_keys = []
        for key, value in expected_call.items():
            if value is None:
                none_keys.append(key)
            elif key in SEPARATED_CALLS_DATETIME_FIELDS:
                expected_call[key] = (
                    datetime.datetime.strptime(
                        value, CLICKHOUSE_DATETIME_FORMAT,
                    )
                    .replace(
                        tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
                    )
                    .isoformat()
                )
        for key in none_keys:
            expected_call.pop(key)

    assert calls == expected_calls


async def test_separated_handle_validation(web_app_client):
    for direction in ['incoming', 'outgoing']:
        for start, end in [(2, 3), (None, None), (2, None)]:
            for batch_id in ['3', None]:
                params = {
                    'project_slug': 'some_project',
                    'user_id': '12321',
                    'limit': '100',
                    'offset': '0',
                    'direction': direction,
                }
                if start:
                    params['start'] = start
                if end:
                    params['end'] = end
                if batch_id:
                    params['batch_id'] = batch_id

                expected_status = (
                    400
                    if (
                        not (start and end)
                        and (
                            direction == 'incoming'
                            or direction == 'outgoing'
                            and not batch_id
                        )
                    )
                    else 200
                )

                response = await web_app_client.get(
                    'v1/statistics/calls/separated', params=params,
                )

                assert response.status == expected_status


@pytest.mark.config(
    SUPPORTAI_STATISTICS_PROJECTS_SETTINGS={
        'automated_after_hours': 6,
        'not_answered_minutes': 30,
    },
)
@pytest.mark.parametrize('period_type', ['hour', 'month'])
@pytest.mark.parametrize('tags', [[], ['first'], ['first', 'second']])
async def test_dialogs_statistics(
        web_app_client,
        web_context,
        mock_clickhouse_host,
        response_mock,
        mockserver,
        period_type,
        tags,
):
    def mock_dialogs(*args, **kwargs):
        validate_ch_request(args, kwargs)
        query = kwargs['data']
        if 'sure_topic sure_topic' not in query:
            return response_mock(
                json=clickhouse_responses.get_dialogs(
                    with_topics=False, period_type=period_type, tags=tags,
                ),
            )
        return response_mock(
            json=clickhouse_responses.get_dialogs(
                with_topics=True, period_type=period_type, tags=tags,
            ),
        )

    host_list = web_context.clickhouse._clickhouse_policy._host_list

    mock_clickhouse_host(
        clickhouse_response=mock_dialogs, request_url=host_list[0],
    )

    @mockserver.json_handler('/supportai/supportai/v1/topics')
    async def _(request):
        if request.query['offset'] == '0':
            return {
                'topics': [
                    {'id': '1', 'slug': 'topic1', 'title': 'Topic 1'},
                    {'id': '2', 'slug': 'topic2', 'title': 'Topic 2'},
                ],
            }
        if request.query['offset'] == '100':
            return {
                'topics': [
                    {'id': '3', 'slug': 'topic3', 'title': 'Topic 3'},
                    {'id': '4', 'slug': 'topic4', 'title': 'Topic 4'},
                ],
            }
        return {'topics': []}

    params = {
        'user_id': '34',
        'project_slug': 'ya_market',
        'period_type': period_type,
    }
    if tags:
        params['tags'] = ','.join(tags)

    response = await web_app_client.get(
        '/v1/statistics/dialogs', params=params,
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

    if tags:
        tag_counters = aggregated['aggregated']['tag_counters']
        assert len(tags) == len(tag_counters)
        for tag, counter_dict in zip(tags, tag_counters):
            assert tag == counter_dict['tag_name']

            if tag == 'first':
                assert counter_dict['count'] == 9
            if tag == 'second':
                assert counter_dict['count'] == 90
        for idx, period in enumerate(aggregated['periods']):
            tag_counters = period['tag_counters']
            assert len(tags) == len(tag_counters)
            for tag, counter_dict in zip(tags, tag_counters):
                assert tag == counter_dict['tag_name']
                if tag == 'first':
                    assert counter_dict['count'] == idx + 2
                if tag == 'second':
                    assert counter_dict['count'] == (idx + 2) * 10
    else:
        assert 'tag_counters' not in aggregated['aggregated']
        assert all('tag_counters' not in row for row in aggregated['periods'])

    assert len(response_json['topics']) == 2
    assert response_json['topics'][0]['aggregated']['title'] == 'Topic 1'
    assert response_json['topics'][0]['aggregated']['messages_number'] == 7
    assert len(response_json['topics'][0]['periods']) == 2
    assert response_json['topics'][0]['periods'][0]['closed_number'] == 2

    topic_one = response_json['topics'][0]
    topic_two = response_json['topics'][1]

    if tags:
        tag_counters_one = topic_one['aggregated']['tag_counters']
        tag_counters_two = topic_two['aggregated']['tag_counters']
        assert len(tags) == len(tag_counters_one)
        assert len(tags) == len(tag_counters_two)
        for tag, counter_dict_one, counter_dict_two in zip(
                tags, tag_counters_one, tag_counters_two,
        ):
            assert tag == counter_dict_one['tag_name']
            if tag == 'first':
                assert counter_dict_one['count'] == 5
                assert counter_dict_two['count'] == 4
            if tag == 'second':
                assert counter_dict_one['count'] == 50
                assert counter_dict_two['count'] == 40
    else:
        for topic in (topic_one, topic_two):
            assert 'tag_counters' not in topic['aggregated']
            assert all('tag_counters' not in row for row in topic['periods'])
