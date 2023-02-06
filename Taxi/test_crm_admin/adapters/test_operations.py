import dataclasses

import pytest

from crm_admin import entity
from crm_admin import storage
from crm_admin.entity import error


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_create(web_context):
    campaign_id = 1
    operation_name = 'create_segment'

    db_operations = storage.DbOperations(web_context)
    operation = await db_operations.create(campaign_id, operation_name)

    assert operation.operation_id > 0
    assert operation.campaign_id == campaign_id
    assert operation.operation_name == operation_name
    assert operation.started_at is not None
    assert operation.finished_at is None


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_create_non_existent_campaign(web_context):
    campaign_id = 100
    operation_name = 'create_segment'

    db_operations = storage.DbOperations(web_context)
    with pytest.raises(error.EntityNotFound):
        await db_operations.create(campaign_id, operation_name)


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_update(web_context):
    operation_id = 1

    db_operations = storage.DbOperations(web_context)
    operation = await db_operations.fetch(operation_id)
    operation.status = 'some status'
    operation.operation_type = entity.OperationType.YQL
    operation.submission_id = 'some submission id'
    operation.extra_data = {'key': 'value'}

    updated_op = await db_operations.update(operation)
    assert updated_op == operation


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_update_non_existent_operation(web_context):
    operation = entity.Operation(
        operation_id=100,
        operation_name='create_segment',
        campaign_id=1,
        retry_count=0,
    )
    db_operations = storage.DbOperations(web_context)

    with pytest.raises(error.EntityNotFound):
        await db_operations.update(operation)


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_fetch(web_context, load_json):
    operation_id = 1

    db_operations = storage.DbOperations(web_context)
    operation = await db_operations.fetch(operation_id)
    operation = dataclasses.asdict(operation)
    operation['started_at'] = str(operation['started_at'])
    operation['operation_type'] = operation['operation_type'].value

    expected = load_json('operations.json')[str(operation_id)]
    assert expected == operation


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_fetch_by_campaign_id(web_context):
    campaign_id = 2
    operation_name = 'operation_name'

    db_operations = storage.DbOperations(web_context)
    await db_operations.create(campaign_id, operation_name)
    await db_operations.create(campaign_id, operation_name)
    expected = await db_operations.create(campaign_id, operation_name)

    actual = await db_operations.fetch_last_by_campaign_id(campaign_id)
    assert actual == expected


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_fetch_non_existent_operation(web_context):
    db_operations = storage.DbOperations(web_context)
    with pytest.raises(error.EntityNotFound):
        await db_operations.fetch(operation_id=100)


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_finish(web_context, load_json):
    operation_id = 1
    status = 'finished'

    db_operations = storage.DbOperations(web_context)
    await db_operations.finish(operation_id, status)
    operation = await db_operations.fetch(operation_id)
    assert operation.finished_at is not None
    assert operation.status == status


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_finish_non_existent_operation(web_context):
    db_operations = storage.DbOperations(web_context)
    with pytest.raises(error.EntityNotFound):
        await db_operations.finish(operation_id=100, status='status')


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_chained_operations(web_context):
    campaign_id = 1
    operation_name = 'operation_name'

    db_operations = storage.DbOperations(web_context)
    op1 = await db_operations.create(campaign_id, operation_name)
    assert op1.chain_id == op1.operation_id

    op2 = await db_operations.create(
        campaign_id, operation_name, parent_id=op1.operation_id,
    )
    assert op2.chain_id == op1.chain_id

    op3 = await db_operations.create(
        campaign_id, operation_name, parent_id=op2.operation_id,
    )
    assert op3.chain_id == op1.chain_id


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_abort(web_context):
    campaign_id = 1
    operation_name = 'operation_name'

    db_operations = storage.DbOperations(web_context)
    op1 = await db_operations.create(campaign_id, operation_name)
    op2 = await db_operations.create(
        campaign_id, operation_name, parent_id=op1.operation_id,
    )
    op3 = await db_operations.create(
        campaign_id, operation_name, parent_id=op1.operation_id,
    )

    await db_operations.abort(op3.operation_id)
    assert (await db_operations.fetch(op1.operation_id)).is_aborted
    assert (await db_operations.fetch(op2.operation_id)).is_aborted
    assert (await db_operations.fetch(op3.operation_id)).is_aborted
