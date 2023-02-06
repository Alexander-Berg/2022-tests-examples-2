import asynctest
import pytest

from integration_procaas.internal import Phases  # pylint: disable=C5521

from eats_menu_processor.components.menu_processor import (  # noqa: E501 pylint: disable=C5521
    MenuProcessor,
)
from eats_menu_processor.enums import ResultsStatus  # pylint: disable=C5521


def check_status(conn, uuid, status):
    with conn.cursor() as cursor:
        cursor.execute(f'select status from results where uuid=\'{uuid}\'')
        return cursor.fetchone()['status'] == status


async def test_processing_call_processor_with_right_args(
        stq3_context, run_processing, processing_data, patch,
):
    @patch(
        'eats_menu_processor.components.menu_processor.MenuProcessor.process',
    )
    async def _mock_menu_process(**kwargs):
        processing_data.pop('uuid')
        assert kwargs == processing_data
        return ''

    await run_processing(**processing_data)


async def test_processing_task_set_success_status(
        run_processing, emp_pgsql_conn, emp_results, processing_data,
):
    MenuProcessor.process = asynctest.CoroutineMock(return_value='')
    await run_processing(**processing_data)
    assert check_status(
        emp_pgsql_conn, emp_results['uuid'], ResultsStatus.SUCCESS,
    )


async def test_processing_save_processed_menu_s3_key(
        run_processing, emp_pgsql_conn, emp_results, processing_data,
):
    processed_s3_key = '/s3/key/processed_file.txt'
    MenuProcessor.process = asynctest.CoroutineMock(
        return_value=processed_s3_key,
    )
    await run_processing(**processing_data)
    with emp_pgsql_conn.cursor() as cursor:
        cursor.execute(
            f'select processed_s3_key from results '
            f'where uuid=\'{emp_results["uuid"]}\'',
        )
        return cursor.fetchone()['processed_s3_key'] == processed_s3_key


async def test_processing_task_set_fail_status(
        run_processing, emp_pgsql_conn, emp_results, processing_data,
):
    MenuProcessor.process = asynctest.CoroutineMock(side_effect=Exception)

    with pytest.raises(Exception):
        await run_processing(**processing_data)
    assert check_status(
        emp_pgsql_conn, emp_results['uuid'], ResultsStatus.FAIL,
    )


async def test_processing_task_call_procaas_after_success(
        run_processing,
        stq3_context,
        emp_pgsql_conn,
        processing_data,
        mock_processing,
        patch,
):
    MenuProcessor.process = asynctest.CoroutineMock(
        return_value='/s3/bucket/file.json',
    )

    task_mock = asynctest.CoroutineMock()
    stq3_context.stq.eats_integration_menu_processing_answers.call = task_mock

    await run_processing(**processing_data)

    assert task_mock.call_count == 1
    assert task_mock.call_args[1]['kwargs']['phase'] == Phases.PROCESSED.value


async def test_processing_task_call_procaas_after_fail(
        run_processing,
        stq3_context,
        emp_pgsql_conn,
        processing_data,
        mock_processing,
):
    MenuProcessor.process = asynctest.CoroutineMock(side_effect=Exception)

    task_mock = asynctest.CoroutineMock()
    stq3_context.stq.eats_integration_menu_processing_answers.call = task_mock
    with pytest.raises(Exception):
        await run_processing(**processing_data)
    assert task_mock.call_count == 1
    row = task_mock.call_args[1]['kwargs']
    assert row['phase'] == Phases.FALLBACK.value
    error_text = 'eats_menu_processor: Fail processing'
    assert row['data']['error_text'] == error_text
