import pytest

from clowny_balancer.lib.models import manual_resize
from clowny_balancer.pytest_plugins import (
    manual_resize as manual_resize_plugin,
)


@pytest.fixture(autouse=True)
def _autoinit_db(fill_default_manual_resize):
    pass


@pytest.fixture(name='manual_resize_manager')
def _manual_resize_manager(web_context):
    return manual_resize.ManualResizeManager(web_context)


@pytest.mark.parametrize(
    ['expected_record'],
    [
        pytest.param(manual_resize_plugin.RECORD_1, id='record_1'),
        pytest.param(manual_resize_plugin.RECORD_2, id='record_2'),
    ],
)
async def test_get_record_by_id(manual_resize_manager, expected_record):
    record = await manual_resize_manager.get_by_id(expected_record.resize_id)
    assert record == expected_record


async def test_get_by_id_not_found(manual_resize_manager):
    with pytest.raises(manual_resize.NotFound):
        await manual_resize_manager.get_by_id('not-an-id')


@pytest.mark.parametrize(
    ['expected_record'],
    [
        pytest.param(manual_resize_plugin.RECORD_1, id='record_1'),
        pytest.param(manual_resize_plugin.RECORD_2, id='record_2'),
    ],
)
async def test_get_record_by_token(manual_resize_manager, expected_record):
    record = await manual_resize_manager.get_by_idempotency_token(
        expected_record.idempotency_token,
    )
    assert record == expected_record


async def test_get_by_token_not_found(manual_resize_manager):
    with pytest.raises(manual_resize.NotFound):
        await manual_resize_manager.get_by_idempotency_token('not-a-token')


async def test_add_record(manual_resize_manager, get_manual_resize):
    record = manual_resize.ManualResizeRecord(
        tp_job_id=None,
        idempotency_token='ee64c6cee89243f78305f6e2355b4766',
        status=manual_resize.Status.IN_PROGRESS,
        namespace_id='test-namespace-id-3',
        parameters=manual_resize.Parameters(
            allocation_request=manual_resize.AllocationRequest(
                replicas={'sas': 5, 'vla': 3},
                preset='NANO',
                io_intensity='NORMAL',
                network_macro='_TESTNETS_',
            ),
        ),
    )
    result_record = await manual_resize_manager.enqueue_resize(record)
    assert result_record == record
    assert len(result_record.resize_id) == 22
    record_from_db = await get_manual_resize(result_record.resize_id)
    result_dict = result_record.to_dict()
    assert record_from_db.pop('tp_job_id') is None
    assert record_from_db.pop('id') == result_dict.pop('resize_id')
    assert record_from_db == result_dict


async def test_get_in_progress_namespace(manual_resize_manager):
    record = await manual_resize_manager.get_by_in_progress_namespace(
        manual_resize_plugin.RECORD_1.namespace_id,
    )
    assert record == manual_resize_plugin.RECORD_1


async def test_not_found_in_progress_namespace(manual_resize_manager):
    with pytest.raises(manual_resize.NotFound):
        await manual_resize_manager.get_by_in_progress_namespace(
            manual_resize_plugin.RECORD_2.namespace_id,
        )
