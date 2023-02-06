# pylint: disable=unused-variable,redefined-outer-name,unused-argument

import pytest


@pytest.fixture(autouse=True)
def skip_validation(patch):
    @patch(
        'crm_admin.utils.validation.filters_yt_validators'
        '.validate_filters_values',
    )
    async def validation(*agrs, **kwargs):
        return []


@pytest.mark.parametrize(
    'campaign_id, status, error_msg',
    [
        (1, 200, None),
        (2, 200, None),
        (3, 200, None),
        (4, 424, 'Unsuitable campaign state'),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_process_segment(
        web_app_client, campaign_id, status, error_msg, patch,
):
    @patch('crm_admin.utils.startrek.startrek.TicketManager.create_ticket')
    async def create_ticket(*args, **kwargs):
        pass

    @patch('crm_admin.utils.startrek.startrek.TicketManager.add_comment')
    async def add_comment(*args, **kwargs):
        pass

    response = await web_app_client.post(
        '/v1/process/segment', params={'id': campaign_id},
    )
    assert response.status == status

    if error_msg:
        msg = await response.json()
        assert error_msg in msg['message']


@pytest.mark.config(
    CRM_ADMIN_CALCULATIONS_STQ_ENABLED={
        'segment_enabled': True,
        'group_enabled': True,
    },
)
@pytest.mark.parametrize(
    'campaign_id, status, error_msg',
    [
        (1, 200, None),
        (2, 200, None),
        (3, 200, None),
        (4, 424, 'Unsuitable campaign state'),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_new_processor_segment(
        web_app_client, campaign_id, status, error_msg, patch,
):
    @patch('crm_admin.utils.startrek.startrek.TicketManager.create_ticket')
    async def create_ticket(*args, **kwargs):
        pass

    @patch('crm_admin.utils.startrek.startrek.TicketManager.add_comment')
    async def add_comment(*args, **kwargs):
        pass

    response = await web_app_client.post(
        '/v1/process/segment', params={'id': campaign_id},
    )
    assert response.status == status

    if error_msg:
        msg = await response.json()
        assert error_msg in msg['message']
