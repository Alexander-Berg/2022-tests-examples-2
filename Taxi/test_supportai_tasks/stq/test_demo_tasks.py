#  pylint: disable=protected-access

import io
from typing import Any
from typing import Dict
from typing import List

from aiohttp import web
import pytest
import xlsxwriter

from supportai_lib.tasks import base_task
from supportai_lib.tasks import constants

from supportai_tasks.generated.stq3 import stq_context
from supportai_tasks.stq import runner


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.project(slug='sample_project'),
]


STATS_DATA = [
    {
        'date': '2021-06-20',
        'topic': 'topic1',
        'total_number': 5,
        'automated_number': 1,
    },
    {
        'date': '2021-06-21',
        'topic': 'topic1',
        'total_number': 6,
        'automated_number': 2,
    },
    {
        'date': '2021-06-22',
        'topic': 'topic2',
        'total_number': 7,
        'automated_number': 3,
    },
]

DIALOGS_DATA: List[Dict[str, Any]] = [
    {
        'topic': 'topic1',
        'feature1': 'Dialog 1',
        'xxx': 'XXX',
        'Unnamed: 3': 'Привет',
        'Unnamed: 4': 'Здраствуйте, я Бот',
        'Unnamed: 5': 'У меня проблемы',
        'Unnamed: 6': 'Ну и хорошо',
    },
    {
        'topic': 'topic1',
        'feature1': 'Dialog 2',
        'xxx': 'XXX',
        'Unnamed: 3': 'Привет',
        'Unnamed: 4': 'Здраствуйте, я Бот',
        'Unnamed: 5': 12345,
    },
    {
        'topic': 'topic2',
        'feature1': 'Dialog 3',
        'xxx': 'XXX',
        'Unnamed: 3': 'Где мой заказ?',
        'Unnamed: 4': 'Пропал',
    },
    {'topic': 'topic2', 'feature1': 'Dialog 4', 'xxx': 'XXX'},
]


@pytest.fixture(name='mocked_config')
def mock_config(mockserver):
    @mockserver.json_handler('/supportai/supportai/v1/features')
    async def _features_resp(request):
        return {
            'features': [
                {
                    'id': '1',
                    'slug': 'feature1',
                    'type': 'str',
                    'description': 'Feature 1',
                    'domain': [],
                },
                {
                    'id': '2',
                    'slug': 'xxx',
                    'type': 'str',
                    'description': 'XXX Feature',
                    'domain': [],
                },
            ],
        }

    @mockserver.json_handler('/supportai/supportai/v1/topics')
    async def _topics_resp(request):
        return {
            'topics': [
                {'id': '1', 'slug': 'topic1', 'title': 'Topic 1'},
                {'id': '2', 'slug': 'topic2', 'title': 'Topic 2'},
            ],
        }


@pytest.fixture(name='run_demo_task')
def run_demo_task_fixture(
        stq3_context: stq_context.Context, create_task_file, create_task,
):
    async def _run_demo_task(data: List[Dict[str, Any]], type_: str):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        worksheet = workbook.add_worksheet('statistics')

        for row_num, entity in enumerate(data):
            if row_num == 0:
                for col_num, col_name in enumerate(entity.keys()):
                    if not col_name.startswith('Unnamed'):
                        worksheet.write(0, col_num, col_name)

            for col_num, item in enumerate(entity.items()):
                data = item[1]
                worksheet.write(row_num + 1, col_num, data)

        workbook.close()
        output.seek(0)

        file = create_task_file(
            filename='import.xlsx',
            content_type=constants.XLSX_CONTENT_TYPE,
            content=output.read(),
        )

        task = create_task(type_=type_, file_id=file.id)

        await runner.task(stq3_context, 'test', task_id=task.id)

        assert (
            task.status == base_task.TaskStatus.COMPLETED.value
        ), task.error_message

    return _run_demo_task


@pytest.mark.pgsql('supportai_tasks', files=['sample_project.sql'])
async def test_demo_stats_import_task(
        stq3_context: stq_context.Context,
        mock_clickhouse_host,
        response_mock,
        mocked_config,
        run_demo_task,
):
    # For pylint
    if not stq3_context.clickhouse._clickhouse_policy:
        return

    def handle(*args, **kwargs):
        return response_mock(json={})

    host_list = stq3_context.clickhouse._clickhouse_policy._host_list

    mock_clickhouse_host(clickhouse_response=handle, request_url=host_list[0])

    await run_demo_task(STATS_DATA, 'demo_stats_import')


@pytest.mark.pgsql('supportai_tasks', files=['sample_project.sql'])
async def test_demo_dialogs_import_task(
        stq3_context: stq_context.Context,
        mockserver,
        mocked_config,
        run_demo_task,
):
    @mockserver.json_handler('/supportai-context/v1/contexts/bulk')
    # pylint: disable=unused-variable
    async def bulk_context_handler(request):
        assert len(request.json['contexts']) == 3
        print(request.json)

        assert len(request.json['contexts'][0]['records']) == 2

        record = request.json['contexts'][0]['records'][0]

        assert record['request']['dialog']['messages'][0]['text'] == 'Привет'
        assert record['response']['reply']['text'] == 'Здраствуйте, я Бот'

        return web.json_response(
            data={
                'contexts': request.json['contexts'],
                'total': len(request.json['contexts']),
            },
        )

    @mockserver.json_handler('/supportai-context/v1/contexts')
    # pylint: disable=unused-variable
    async def delete_context_handler(request):
        return web.json_response(data={})

    await run_demo_task(DIALOGS_DATA, 'demo_dialogs_import')
