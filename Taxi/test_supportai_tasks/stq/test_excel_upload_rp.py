import io

from aiohttp import web
import pytest
import xlsxwriter

from supportai_lib.tasks import base_task
from supportai_lib.tasks import constants


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.config(
        TVM_RULES=[
            {'src': 'supportai-tasks', 'dst': 'supportai-context'},
            {'src': 'supportai-tasks', 'dst': 'stq-agent'},
        ],
    ),
    pytest.mark.config(
        SUPPORTAI_TASKS_RP_UPLOAD_SETTINGS={
            'batch_size': 2,
            'sleep_between_batches': 1,
        },
    ),
]


def _get_file_data():
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet('Лист 1')

    worksheet.write(0, 0, 'text')
    worksheet.write(0, 1, 'topic_slug')

    for i, (text, topic_slug) in enumerate(
            [
                ('текст', 'totalchest1'),
                ('текст', 'totalchest1'),
                ('текст', 'totalchest1'),
                ('текст', 'totalchest2'),
                ('текст', 'totalchest3'),
                ('текст', 'totalchest4'),
            ],
    ):
        worksheet.write(i + 1, 0, text)
        worksheet.write(i + 1, 1, topic_slug)

    workbook.close()
    output.seek(0)

    return output


async def test_upload_rp_success(
        stq3_context, mockserver, stq_runner, create_task, create_task_file,
):
    file = create_task_file(
        filename='upload_rp.xlsx',
        content_type=constants.XLSX_CONTENT_TYPE,
        content=_get_file_data().read(),
    )

    db_task = create_task(type_='excel_upload_rp_task', file_id=file.id)

    rp_request_count = 0

    @mockserver.json_handler('/supportai-reference-phrases/v1/matrix')
    # pylint: disable=unused-variable
    async def handler_rp(request):
        nonlocal rp_request_count
        rp_request_count += 1

        return web.json_response(data={'matrix': []})

    await stq_runner.supportai_admin_export.call(
        task_id='task', args=(), kwargs={'task_id': db_task.id},
    )

    assert db_task.status == base_task.TaskStatus.COMPLETED.value

    assert rp_request_count == 5
