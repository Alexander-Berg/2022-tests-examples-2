#  pylint: disable=protected-access
#  type: ignore
import io

import pandas as pd
import pytest

from supportai_lib.tasks import base_task

from supportai_tasks.generated.stq3 import stq_context
from supportai_tasks.stq import runner


@pytest.fixture(name='statistics_ch_resp_export')
def gen_topic_ch_resp():
    return {
        'statistics': {'elapsed': 0.5, 'rows_read': 100, 'bytes_read': 10},
        'meta': [],
        'data': [
            {
                'sure_topic': 'topic1',
                'period_start_date': '2021-03-18 00:00:00',
                'total_number': 11,
                'automated_number': 5,
                'closed_number': 2,
                'forwarded_number': 0,
                'not_answered_number': 2,
                'reopened_number': 1,
                'messages_number': 4,
                'messages_automated_number': 1,
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
                'messages_automated_number': 3,
                'minutes': 13.5,
            },
        ],
        'rows': 2,
    }


@pytest.mark.pgsql('supportai_tasks', files=['sample_project.sql'])
async def test_export_personal_account_overview(
        stq3_context: stq_context.Context,
        response_mock,
        mockserver,
        mock_clickhouse_host,
        statistics_ch_resp_export,
        create_task,
        get_task_file,
):
    host = stq3_context.clickhouse._clickhouse_policy._host_list

    def handle(*args, **kwargs):
        return response_mock(json=statistics_ch_resp_export)

    mock_clickhouse_host(clickhouse_response=handle, request_url=host[0])

    @mockserver.json_handler('/supportai/supportai/v1/topics')
    async def _topics_resp(request):
        return {
            'topics': [
                {'id': '1', 'slug': 'topic1', 'title': 'Тема 1'},
                {'id': '2', 'slug': 'topic2', 'title': 'Тема 2'},
                {'id': '3', 'slug': 'topic3', 'title': 'Тема 2'},
                {'id': '4', 'slug': 'topic4', 'title': 'Тема 2'},
            ],
        }

    task = create_task(
        type_='export_personal_account_overview',
        params={
            'topic_slugs': ['topic1'],
            'columns': [
                'total_number',
                'automated_number',
                'closed_number',
                'messages_automated_number',
            ],
        },
    )

    await runner.task(stq3_context, 'test', task_id=task.id)

    assert task.status == base_task.TaskStatus.COMPLETED.value
    assert task.file_id is not None

    file_data = get_task_file(task.file_id)

    assert file_data is not None

    all_data = pd.read_excel(
        io.BytesIO(file_data[1]), sheet_name=None, na_filter=False,
    )

    aggregated = all_data['Всего'].to_dict('records')
    topics = all_data['Тематики'].to_dict('records')
    assert len(topics) == 1

    assert len(all_data['Детализация тематик'].to_dict('records')) == 3

    assert aggregated[0]['Заголовок'] == 'Выбранные тематики'
    assert aggregated[0]['Диалоги'] == 21
    assert aggregated[0]['Автоматизация диалогов'] == 9
    assert aggregated[0]['Доля (Автоматизация диалогов)'] == 0.429
    assert aggregated[0]['Закрыто'] == 3
    assert aggregated[0]['Доля (Закрыто)'] == 0.143
    assert aggregated[0]['Автоматизация сообщений'] == 4
    assert 'Перевод к оператору' not in aggregated[0]
