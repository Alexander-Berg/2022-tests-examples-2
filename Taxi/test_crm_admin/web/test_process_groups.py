# pylint: disable=unused-variable,invalid-name

import pytest

from crm_admin import storage


PROCESS_GROUP_URL = '/v1/process/groups'


@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.parametrize(
    'campaign_id, status',
    # id=3: no segment, id=10: does not exist
    [(1, 200), (3, 424), (10, 424)],
)
async def test_process_groups(web_app_client, stq, campaign_id, status, patch):
    @patch('crm_admin.api.process_groups.start_task')
    async def start_task(*args, **kwargs):
        pass

    response = await web_app_client.post(
        PROCESS_GROUP_URL, params={'id': campaign_id},
    )
    assert response.status == status
    assert len(start_task.calls) == (status == 200)


@pytest.mark.pgsql('crm_admin', files=['init_without_groups.sql'])
@pytest.mark.parametrize(
    'campaign_id, segment_id, expected_status',
    [(1, 1, 200), (2, 2, 200), (3, 3, 424)],
)
async def test_process_groups_without_groups(
        web_app_client,
        web_context,
        patch,
        campaign_id,
        segment_id,
        expected_status,
):
    @patch('crm_admin.api.process_groups.start_task')
    async def start_task(*args, **kwargs):
        pass

    response = await web_app_client.post(
        PROCESS_GROUP_URL, params={'id': campaign_id},
    )

    db_group = storage.DbGroup(web_context)
    groups = await db_group.fetch_by_segment(segment_id)

    assert response.status == expected_status
    assert len(start_task.calls) == (expected_status == 200)
    assert (expected_status == 200) == bool(groups)


@pytest.mark.config(
    CRM_ADMIN_CALCULATIONS_STQ_ENABLED={
        'segment_enabled': True,
        'group_enabled': True,
    },
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
@pytest.mark.parametrize(
    'campaign_id, status',
    # id=3: no segment, id=10: does not exist
    [(1, 200), (3, 424), (10, 424)],
)
async def test_new_processor_groups(
        web_app_client, stq, campaign_id, status, patch,
):
    @patch('crm_admin.api.process_groups.start_task')
    async def start_task(*args, **kwargs):
        pass

    response = await web_app_client.post(
        PROCESS_GROUP_URL, params={'id': campaign_id},
    )
    assert response.status == status
    assert len(start_task.calls) == (status == 200)


@pytest.mark.config(
    CRM_ADMIN_CALCULATIONS_STQ_ENABLED={
        'segment_enabled': True,
        'group_enabled': True,
    },
)
@pytest.mark.pgsql('crm_admin', files=['init_without_groups.sql'])
@pytest.mark.parametrize(
    'campaign_id, segment_id, expected_status',
    [(1, 1, 200), (2, 2, 200), (3, 3, 424)],
)
async def test_new_processor_groups_without_groups(
        web_app_client,
        web_context,
        patch,
        campaign_id,
        segment_id,
        expected_status,
):
    @patch('crm_admin.api.process_groups.start_task')
    async def start_task(*args, **kwargs):
        pass

    response = await web_app_client.post(
        PROCESS_GROUP_URL, params={'id': campaign_id},
    )

    db_group = storage.DbGroup(web_context)
    groups = await db_group.fetch_by_segment(segment_id)

    assert response.status == expected_status
    assert len(start_task.calls) == (expected_status == 200)
    assert (expected_status == 200) == bool(groups)
