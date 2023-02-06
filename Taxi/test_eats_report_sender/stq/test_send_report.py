import asynctest
import pytest

from eats_report_sender.components.senders import sftp_sender
from eats_report_sender.internal import exceptions
from eats_report_sender.stq import send_report


async def test_should_raise_exception_if_cannot_find_report(
        task_info, stq3_context, load_json,
):
    not_existed_uuid = load_json('report_data.json')['not_existed']['uuid']
    with pytest.raises(exceptions.CannotFindReportException):
        await send_report.task(stq3_context, task_info, uuid=not_existed_uuid)


def _has_correct_status(pgsql, uuid, expected_status):
    with pgsql['eats_report_sender'].cursor() as cursor:
        cursor.execute(f'select status from reports where uuid=\'{uuid}\'')
        actual_status = list(row[0] for row in cursor)[0]
    assert expected_status == actual_status


@pytest.mark.pgsql('eats_report_sender', files=['eats_report_sender.sql'])
async def test_should_set_status_in_success_if_has_correct_run(
        task_info, stq3_context, load_json, pgsql, mockserver,
):
    s3_file_content = '<Body>testtesttest</Body>'

    sftp_sender.SftpSender.send = asynctest.CoroutineMock()

    @mockserver.handler('/mds-s3', prefix=True)
    async def _mds_s3_mock(request, **kwargs):  # noqa: W0612
        return mockserver.make_response(
            status=200, response=s3_file_content, headers={'ETag': 'asdf'},
        )

    existed_uuid = load_json('report_data.json')['existed']['uuid']
    existed_id = load_json('report_data.json')['existed']['id']
    _has_correct_status(pgsql, existed_uuid, 'new')
    await send_report.task(stq3_context, task_info, id=existed_id)
    _has_correct_status(pgsql, existed_uuid, 'success')


@pytest.mark.pgsql('eats_report_sender', files=['eats_report_sender.sql'])
async def test_should_set_status_in_fail_if_has_incorrect_run(
        task_info, stq3_context, load_json, pgsql,
):
    existed_uuid = load_json('report_data.json')['existed']['uuid']
    existed_id = load_json('report_data.json')['existed']['id']
    _has_correct_status(pgsql, existed_uuid, 'new')

    stq3_context.report_sender.send = asynctest.CoroutineMock(
        side_effect=Exception,
    )

    with pytest.raises(Exception):
        await send_report.task(stq3_context, task_info, id=existed_id)
    _has_correct_status(pgsql, existed_uuid, 'fail')


@pytest.mark.parametrize(
    'max_task_retries, should_called', [(0, False), (3, True)],
)
async def test_task_should_stop_if_max_retry_limit_is_over(
        stq3_context,
        patch,
        task_info,
        monkeypatch,
        max_task_retries,
        should_called,
):
    @patch('eats_report_sender.stq.send_report._task')
    async def send_report_logic_mock(*args, **kwargs):
        pass

    stq3_context.config.EATS_REPORT_SENDER_MAX_TASK_RETRIES[
        'max_task_retries'
    ] = max_task_retries
    await send_report.task(stq3_context, task_info, uuid='123')
    called = len(send_report_logic_mock.calls) > 0
    assert called == should_called
