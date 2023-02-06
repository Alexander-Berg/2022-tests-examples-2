#  pylint: disable=protected-access
#  type: ignore
import io
import re
from typing import Dict
import urllib.parse

import pandas as pd
import pytest

from supportai_lib.tasks import base_task

from supportai_statistics.generated.stq3 import stq_context
from supportai_statistics.stq import stats_processing
from test_supportai_statistics import clickhouse_responses
from . import common


def validate_ch_request(req_args, req_kwargs) -> Dict:
    url = req_args[1]
    query_params = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    assert query_params.pop('database', [None])[0] == 'supportai_api'
    params_for_template = set(query_params.keys())
    params_for_template = {param[6:] for param in params_for_template}

    db_query = req_kwargs['data']
    template_params = re.findall(r'{[^:]+:', db_query)
    template_params = {param[1:-1] for param in template_params}
    assert template_params <= params_for_template

    return query_params


@pytest.mark.project(slug='some_project')
@pytest.mark.parametrize('tags', [[], ['first', 'second']])
async def test_export_dialogs_stats(
        stq3_context: stq_context.Context,
        response_mock,
        mockserver,
        mock_clickhouse_host,
        create_task,
        get_task_file,
        tags,
):
    def mock_ch(*args, **kwargs):
        validate_ch_request(args, kwargs)
        query = kwargs['data']
        if 'sure_topic sure_topic' not in query:
            return response_mock(
                json=clickhouse_responses.get_dialogs(
                    with_topics=False, period_type='day', tags=tags,
                ),
            )
        return response_mock(
            json=clickhouse_responses.get_dialogs(
                with_topics=True, period_type='day', tags=tags,
            ),
        )

    host_list = stq3_context.clickhouse._clickhouse_policy._host_list

    mock_clickhouse_host(clickhouse_response=mock_ch, request_url=host_list[0])

    topics_call_count = 0

    @mockserver.json_handler('/supportai/supportai/v1/topics')
    async def _topics_resp(_):
        nonlocal topics_call_count
        if topics_call_count:
            return {'topics': []}

        topics_call_count += 1

        return {
            'topics': [
                {'id': '1', 'slug': 'topic1', 'title': 'Тема 1'},
                {'id': '2', 'slug': 'topic2', 'title': 'Тема 2'},
                {'id': '3', 'slug': 'topic3', 'title': 'Тема 2'},
                {'id': '4', 'slug': 'topic4', 'title': 'Тема 2'},
            ],
        }

    params = {
        'topic_slugs': ['topic1', 'topic2'],
        'columns': [
            'total_number',
            'automated_number',
            'closed_number',
            'messages_automated_number',
        ],
    }
    if tags:
        params['tags'] = tags

    task = create_task(type_='export_personal_account_overview', params=params)

    await stats_processing.task(stq3_context, 'test', task_id=task.id)

    assert (
        task.status == base_task.TaskStatus.COMPLETED.value
    ), task.error_message
    assert task.file_id is not None

    file_data = get_task_file(task.file_id)

    assert file_data is not None

    all_data = pd.read_excel(
        io.BytesIO(file_data[1]), sheet_name=None, na_filter=False,
    )

    expected_columns = [
        'Заголовок',
        'Диалоги',
        'Автоматизация диалогов',
        'Доля (Автоматизация диалогов)',
        'Закрыто',
        'Доля (Закрыто)',
        'Автоматизация сообщений',
    ]
    if tags:
        expected_columns.extend(
            [
                'Тег first',
                'Доля (Тег first)',
                'Тег second',
                'Доля (Тег second)',
            ],
        )

    aggregated = all_data['Всего'].to_dict('records')
    assert list(all_data['Всего'].columns) == expected_columns

    topics = all_data['Тематики'].to_dict('records')
    assert len(topics) == 2

    assert len(all_data['Детализация по тематикам'].to_dict('records')) == 5

    def equal_float(lhs, rhs):
        return abs(rhs - lhs) < 0.0001

    assert aggregated[0]['Заголовок'] == 'Выбранные тематики'
    assert aggregated[0]['Диалоги'] == 30
    assert aggregated[0]['Автоматизация диалогов'] == 14
    assert equal_float(aggregated[0]['Доля (Автоматизация диалогов)'], 0.46667)
    assert aggregated[0]['Закрыто'] == 4
    assert equal_float(aggregated[0]['Доля (Закрыто)'], 0.133333)
    assert aggregated[0]['Автоматизация сообщений'] == 4
    assert 'Перевод к оператору' not in aggregated[0]

    if tags:
        assert aggregated[0]['Тег first'] == 9
        assert equal_float(aggregated[0]['Доля (Тег first)'], 0.3)
        assert aggregated[0]['Тег second'] == 90
        assert equal_float(aggregated[0]['Доля (Тег second)'], 3)


@pytest.mark.project(slug='some_project')
@pytest.mark.parametrize('tags', [[], ['first']])
@pytest.mark.parametrize('call_direction', ['incoming', 'outgoing'])
@pytest.mark.parametrize('empty_ch_response', [True, False])
async def test_export_grouped_calls_stats(
        stq3_context: stq_context.Context,
        response_mock,
        mockserver,
        mock_clickhouse_host,
        create_task,
        get_task_file,
        tags,
        call_direction,
        empty_ch_response,
):
    def mock_ch(*args, **kwargs):
        validate_ch_request(args, kwargs)
        query = kwargs['data']
        if empty_ch_response:
            return response_mock(json=clickhouse_responses.get_empty())
        if 'period' in query:
            return response_mock(
                json=clickhouse_responses.get_calls_batches_by_hour(tags),
            )
        return response_mock(
            json=clickhouse_responses.get_calls_grouped(
                group_by='hour', tags=tags,
            ),
        )

    def compare_rows(lhs, rhs):
        for lhs_value, rhs_value in zip(lhs, rhs):
            if isinstance(lhs_value, str) and isinstance(rhs_value, str):
                assert lhs_value == rhs_value
            elif isinstance(lhs_value, int) and isinstance(rhs_value, int):
                assert lhs_value == rhs_value
            elif isinstance(lhs_value, float) and isinstance(rhs_value, float):
                assert abs(lhs_value - rhs_value) < 0.001
            else:
                assert False, (lhs_value, rhs_value)

    host_list = stq3_context.clickhouse._clickhouse_policy._host_list
    mock_clickhouse_host(clickhouse_response=mock_ch, request_url=host_list[0])

    params = {
        'call_direction': call_direction,
        'stats_type': 'calls_grouped',
        'columns': [
            'start_at',
            'total_seconds',
            'calls',
            'call_attempts',
            'ended_count',
        ],
    }
    if tags:
        params['tags'] = tags

    task = create_task(type_='export_personal_account_overview', params=params)

    await stats_processing.task(stq3_context, 'test', task_id=task.id)

    assert (
        task.status == base_task.TaskStatus.COMPLETED.value
    ), task.error_message

    assert task.file_id is not None
    file_data = get_task_file(task.file_id)
    assert file_data is not None

    all_data = pd.read_excel(
        io.BytesIO(file_data[1]), sheet_name=None, na_filter=False,
    )
    expected_sheet_titles = {'Всего', 'Периоды'}
    if call_direction == 'outgoing':
        expected_sheet_titles.add('Детализация обзвонов по периодам')

    assert expected_sheet_titles == set(all_data)

    expected_columns = [
        'Заголовок',
        'Время начала',
        'Продолжительность, с',
        'Обработано номеров',
        'Всего звонков',
        'Звонков успешно завершилось',
        'Доля (Звонков успешно завершилось)',
    ]
    if tags:
        expected_columns += ['Тег first', 'Доля (Тег first)']

    for sheet in all_data.values():
        assert list(sheet.columns) == expected_columns

    expected_titles_and_start_at = {
        'Всего': [['Все звонки', '2022-05-30T12:32:25+03:00']],
        'Периоды': [
            ['2022-05-30T12:00:00+03:00', '2022-05-30T12:32:25+03:00'],
            ['2022-05-30T16:00:00+03:00', '2022-05-30T16:57:42+03:00'],
            ['2022-05-30T18:00:00+03:00', '2022-05-30T18:23:42+03:00'],
            ['2022-05-31T11:00:00+03:00', '2022-05-31T11:49:05+03:00'],
        ],
        'Детализация обзвонов по периодам': [
            ['2022-05-30 12:00:00', '2022-05-30T12:32:25+03:00'],
            ['3462', '2022-05-30T12:32:25+03:00'],
            ['2022-05-30 16:00:00', '2022-05-30T16:57:42+03:00'],
            ['3463', '2022-05-30T16:57:42+03:00'],
            ['3464', '2022-05-30T16:59:29+03:00'],
            ['2022-05-30 18:00:00', '2022-05-30T18:23:42+03:00'],
            ['3467', '2022-05-30T18:23:42+03:00'],
            ['3468', '2022-05-30T18:29:29+03:00'],
            ['3469', '2022-05-30T18:31:36+03:00'],
            ['3470', '2022-05-30T18:31:53+03:00'],
            ['2022-05-31 11:00:00', '2022-05-31T11:49:05+03:00'],
            ['3471', '2022-05-31T11:49:05+03:00'],
        ],
    }
    expected_count_fields = {
        'Всего': [[66, 10, 13, 1, 0.077, 14, 1.077]],
        'Периоды': [
            [0, 1, 1, 0, 0.0, 2, 2.0],
            [22, 4, 4, 0, 0.0, 3, 0.75],
            [40, 4, 7, 1, 0.142, 4, 0.571],
            [4, 1, 1, 0, 0.0, 5, 5.0],
        ],
        'Детализация обзвонов по периодам': [
            [0, 1, 1, 0, 0.0, 2, 2.0],
            [0, 1, 1, 0, 0.0, 2, 2.0],
            [22, 4, 4, 0, 0.0, 7, 1.75],
            [0, 3, 3, 0, 0.0, 3, 1.0],
            [22, 1, 1, 0, 0.0, 4, 4.0],
            [40, 4, 7, 1, 0.142, 26, 3.714],
            [20, 1, 1, 1, 1.0, 5, 5.0],
            [10, 1, 2, 0, 0.0, 6, 3.0],
            [0, 1, 1, 0, 0.0, 7, 7.0],
            [10, 1, 3, 0, 0.0, 8, 2.667],
            [4, 1, 1, 0, 0.0, 9, 9.0],
            [4, 1, 1, 0, 0.0, 9, 9.0],
        ],
    }

    for sheet_title in expected_sheet_titles:
        sheet_content = common.dataframe_to_table(all_data[sheet_title])
        if empty_ch_response:
            if sheet_title == 'Всего':
                compare_rows(
                    sheet_content[0], ['Все звонки', '', 0, 0, 0, 0, 0, 0, 0],
                )
            else:
                assert sheet_content == [], sheet_title
            continue

        expected_title_and_start_at = expected_titles_and_start_at[sheet_title]
        expected_counts = expected_count_fields[sheet_title]
        for row, expected_title_part, expected_count_part in zip(
                sheet_content, expected_title_and_start_at, expected_counts,
        ):
            compare_rows(row[:2], expected_title_part)
            compare_rows(row[2:], expected_count_part)


@pytest.mark.project(slug='some_project')
@pytest.mark.parametrize('batch_id', ['some_batch', None])
@pytest.mark.parametrize('empty_ch_response', [True, False])
async def test_export_separate_calls_stats(
        stq3_context: stq_context.Context,
        response_mock,
        mockserver,
        mock_clickhouse_host,
        create_task,
        get_task_file,
        batch_id,
        empty_ch_response,
        monkeypatch,
):
    limit = 2

    monkeypatch.setattr(
        'supportai_statistics.stq.tasks.export_statistics.'
        'SEPARATE_CALLS_WRITTEN_UNTIL_SLEEP',
        limit,
    )

    def mock_ch(*args, **kwargs):
        query_params = validate_ch_request(args, kwargs)
        limit_ = int(query_params['param_limit'][0])
        offset_ = int(query_params['param_offset'][0])
        assert limit_ == limit
        if empty_ch_response:
            return response_mock(json=clickhouse_responses.get_empty())
        return response_mock(
            json=clickhouse_responses.get_separate_calls(limit_, offset_),
        )

    host_list = stq3_context.clickhouse._clickhouse_policy._host_list
    mock_clickhouse_host(clickhouse_response=mock_ch, request_url=host_list[0])

    params = {
        'call_direction': 'outgoing',
        'stats_type': 'calls_separated',
        'columns': [
            'start_at',
            'total_seconds',
            'calls',
            'call_attempts',
            'ended_count',
        ],
    }
    if batch_id:
        params['batch_id'] = batch_id
    else:
        params['start_date'] = 1

    task = create_task(type_='export_personal_account_overview', params=params)

    await stats_processing.task(stq3_context, 'test', task_id=task.id)

    assert (
        task.status == base_task.TaskStatus.COMPLETED.value
    ), task.error_message

    assert task.file_id is not None
    file_data = get_task_file(task.file_id)
    assert file_data is not None

    all_data = pd.read_excel(
        io.BytesIO(file_data[1]), sheet_name=None, na_filter=False, dtype=str,
    )
    expected_sheet_titles = {
        f'Звонки обзвона {batch_id}'
        if batch_id
        else 'Звонки за период с 1970.01.01 03-00-01',
    }

    assert expected_sheet_titles == set(all_data)

    expected_columns = [
        'Id звонка',
        'Номер пользователя',
        'Номер робота',
        'Время инициации',
        'Время начала',
        'Длительность, с',
        'Количество попыток',
        'Статус',
    ]

    for sheet in all_data.values():
        assert list(sheet.columns) == expected_columns

    expected_content = [
        ['2199', '+79166914539', '+74950852266', '2022-05-30T16:57:42+03:00']
        + ['', '0', '1', 'Сбросили звонок'],
        ['2200', '+79166914539', '+74950852266', '2022-05-30T16:57:43+03:00']
        + ['2022-05-30T16:57:46+03:00', '22', '2', 'Ошибка'],
        ['2201', '+79166914539', '', '2022-05-30T16:57:44+03:00']
        + ['', '0', '1', 'Недозвон'],
        ['2202', '+79166914539', '+74950852266', '2022-05-30T16:57:45+03:00']
        + ['2022-05-30T16:57:50+03:00', '50', '1', 'ОК'],
    ] * int(not empty_ch_response)

    assert (
        common.dataframe_to_table(list(all_data.values())[0])
        == expected_content
    )
