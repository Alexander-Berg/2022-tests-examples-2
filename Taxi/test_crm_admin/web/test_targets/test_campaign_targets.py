import pytest

from taxi.util import dates

from crm_admin import storage


@pytest.mark.parametrize(
    'campaign_id, expected_target_ids', [(1, [1, 2]), (3, [])],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.now('2022-04-04 04:04:04')
async def test_get_targets(
        web_context, web_app_client, campaign_id, expected_target_ids,
):
    response = await web_app_client.get(f'/v1/campaigns/{campaign_id}/targets')
    response_data = await response.json()
    response_target_ids = [entity['id'] for entity in response_data]

    assert response.status == 200
    assert response_target_ids == expected_target_ids


@pytest.mark.parametrize(
    'campaign_id, target_id, is_exist',
    [(1, 4, False), (3, 1, False), (3, 4, True)],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.now('2022-04-04 04:04:04')
async def test_add_target(
        web_context, web_app_client, campaign_id, target_id, is_exist,
):
    response = await web_app_client.post(
        f'/v1/campaigns/{campaign_id}/targets',
        params={'target_id': target_id},
    )

    db_conn = storage.DbTargetLink(context=web_context)
    conn_entity = await db_conn.fetch(
        campaign_id=campaign_id, target_id=target_id,
    )

    assert response.status == 200
    assert conn_entity.created_at == dates.utcnow()
    assert conn_entity.updated_at == dates.utcnow()
    assert not conn_entity.deleted_at


@pytest.mark.parametrize(
    'campaign_id, target_id, status',
    [(1, 1, 200), (1, 2, 200), (1, 3, 400), (3, 3, 400), (3, 4, 400)],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.now('2022-04-04 04:04:04')
async def test_delete_target(
        web_context, web_app_client, campaign_id, target_id, status,
):
    response = await web_app_client.delete(
        f'/v1/campaigns/{campaign_id}/targets',
        params={'target_id': target_id},
    )

    db_conn = storage.DbTargetLink(context=web_context)
    conn_entity = await db_conn.fetch(
        campaign_id=campaign_id, target_id=target_id,
    )

    assert response.status == status
    if status == 200:
        assert conn_entity.deleted_at == dates.utcnow()
        assert conn_entity.updated_at == dates.utcnow()
