import pytest

from taxi.util import dates

from crm_admin import entity
from crm_admin import storage


@pytest.mark.parametrize(
    'campaign_id, target_id, entity_id',
    [(1, 1, 1), (1, 2, 2), (3, 4, 3), (1, 100, -1), (3, 100, -1)],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_fetch(
        web_context, load_json, campaign_id, target_id, entity_id,
):
    db_conn = storage.DbTargetLink(web_context)

    conn_entity = await db_conn.fetch(
        campaign_id=campaign_id, target_id=target_id,
    )
    expected = load_json('records.json').get(str(entity_id))

    if expected is None or conn_entity is None:
        assert conn_entity == expected
    else:
        assert conn_entity.connection_id == expected['id']
        assert conn_entity.campaign_id == expected['campaign_id']
        assert conn_entity.target_id == expected['target_id']
        assert str(conn_entity.created_at) == expected['created_at']
        assert str(conn_entity.updated_at) == expected['updated_at']
        assert str(conn_entity.deleted_at) == str(expected['deleted_at'])


@pytest.mark.parametrize(
    'connection_id, entity_id', [(1, 1), (2, 2), (4, 3), (3, -1), (-100, -1)],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_fetch_by_id(web_context, load_json, connection_id, entity_id):
    db_conn = storage.DbTargetLink(web_context)

    conn_entity = await db_conn.fetch_by_id(connection_id=connection_id)
    expected = load_json('records.json').get(str(entity_id))

    if expected is None or conn_entity is None:
        assert conn_entity == expected
    else:
        assert conn_entity.connection_id == expected['id']
        assert conn_entity.campaign_id == expected['campaign_id']
        assert conn_entity.target_id == expected['target_id']
        assert str(conn_entity.created_at) == expected['created_at']
        assert str(conn_entity.updated_at) == expected['updated_at']
        assert str(conn_entity.deleted_at) == str(expected['deleted_at'])


@pytest.mark.parametrize(
    'campaign_id, target_id, entity_id',
    [(1, 1, 1), (1, 2, 2), (100, 100, -1), (1, 4, -1)],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.now('2022-04-04 04:04:04')
async def test_delete(
        web_context, load_json, campaign_id, target_id, entity_id,
):
    db_conn = storage.DbTargetLink(web_context)

    try:
        conn_entity = await db_conn.delete(
            campaign_id=campaign_id, target_id=target_id,
        )
    except entity.EntityNotFound:
        assert entity_id == -1
        return

    expected = load_json('records.json')[str(entity_id)]

    assert conn_entity.connection_id == expected['id']
    assert conn_entity.campaign_id == expected['campaign_id']
    assert conn_entity.target_id == expected['target_id']
    assert str(conn_entity.created_at) == expected['created_at']
    assert conn_entity.updated_at == dates.utcnow()
    assert conn_entity.deleted_at == dates.utcnow()


@pytest.mark.parametrize(
    'connection_id, entity_id', [(1, 1), (2, 2), (3, -1), (-100, -1)],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.now('2022-04-04 05:05:05')
async def test_delete_by_id(web_context, load_json, connection_id, entity_id):
    db_conn = storage.DbTargetLink(web_context)

    try:
        conn_entity = await db_conn.delete_by_id(connection_id=connection_id)
    except entity.EntityNotFound:
        assert entity_id == -1
        return

    expected = load_json('records.json')[str(entity_id)]

    assert conn_entity.connection_id == expected['id']
    assert conn_entity.campaign_id == expected['campaign_id']
    assert conn_entity.target_id == expected['target_id']
    assert str(conn_entity.created_at) == expected['created_at']
    assert conn_entity.updated_at == dates.utcnow()
    assert conn_entity.deleted_at == dates.utcnow()


@pytest.mark.parametrize('campaign_id, target_id', [(3, 1), (3, 2)])
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.now('2022-04-04 05:05:05')
async def test_create_not_exists(
        web_context, load_json, campaign_id, target_id,
):
    db_conn = storage.DbTargetLink(web_context)

    conn_entity = await db_conn.create(
        campaign_id=campaign_id, target_id=target_id,
    )

    assert conn_entity.connection_id == 5
    assert conn_entity.campaign_id == campaign_id
    assert conn_entity.target_id == target_id
    assert conn_entity.created_at == dates.utcnow()
    assert conn_entity.updated_at == dates.utcnow()
    assert not conn_entity.deleted_at


@pytest.mark.parametrize('campaign_id, target_id, entity_id', [(3, 4, 3)])
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.now('2022-04-04 05:05:05')
async def test_create_exists(
        web_context, load_json, campaign_id, target_id, entity_id,
):
    db_conn = storage.DbTargetLink(web_context)

    conn_entity = await db_conn.create(
        campaign_id=campaign_id, target_id=target_id,
    )

    expected = load_json('records.json')[str(entity_id)]

    assert conn_entity.connection_id == expected['id']
    assert conn_entity.campaign_id == expected['campaign_id']
    assert conn_entity.target_id == expected['target_id']
    assert conn_entity.created_at == dates.utcnow()
    assert conn_entity.updated_at == dates.utcnow()
    assert not conn_entity.deleted_at
