# pylint: disable=unused-variable,redefined-outer-name

import pytest

from crm_admin import settings
from crm_admin import storage
from crm_admin.utils import common
from crm_admin.utils.campaign import campaign as campaign_utils
from test_crm_admin.utils import audience_cfg

CRM_ADMIN_GROUPS_V2 = {'all_on': True}


@pytest.mark.config(
    CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2,
    CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS,
)
@pytest.mark.parametrize(
    'campaign_id, expected_state',
    [
        (1, settings.SEGMENT_EXPECTED_STATE),
        (2, settings.SEGMENT_EXPECTED_STATE),
        (3, settings.SEGMENT_EXPECTED_STATE),
        (4, settings.NEW_CAMPAIGN),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_clone_at_state(
        web_app_client, web_context, patch, campaign_id, expected_state,
):
    @patch('crm_admin.utils.startrek.startrek.TicketManager.create_ticket')
    async def create_ticket(*args, **kwargs):
        pass

    @patch('crm_admin.utils.startrek.startrek.TicketManager.add_comment')
    async def add_comment(*args, **kwargs):
        pass

    params = {'source_campaign_id': campaign_id, 'name': 'new campaign'}
    owner = 'user'

    response = await web_app_client.post(
        '/v1/campaigns/clone', json=params, headers={'X-Yandex-Login': owner},
    )

    assert response.status == 200
    answer = await response.json()

    db_campaign = storage.DbCampaign(web_context)
    new_campaign = await db_campaign.fetch(answer['id'])
    assert new_campaign.state == expected_state


@pytest.mark.config(
    CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2,
    CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS,
)
async def test_clone_error(web_app_client):
    campaign_id = 100

    params = {'source_campaign_id': campaign_id, 'name': 'new campaign'}
    owner = 'user'

    response = await web_app_client.post(
        '/v1/campaigns/clone', json=params, headers={'X-Yandex-Login': owner},
    )

    assert response.status == 404


@pytest.mark.config(
    CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2,
    CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS,
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_clone_campaign(web_app_client, web_context, patch):
    @patch('crm_admin.utils.startrek.startrek.TicketManager.create_ticket')
    async def create_ticket(*args, **kwargs):
        return 'new ticket'

    @patch('crm_admin.utils.startrek.startrek.TicketManager.add_comment')
    async def add_comment(*args, **kwargs):
        pass

    campaign_id = 6
    params = {'source_campaign_id': campaign_id, 'name': 'new campaign'}
    owner = 'another user'

    response = await web_app_client.post(
        '/v1/campaigns/clone', json=params, headers={'X-Yandex-Login': owner},
    )

    assert response.status == 200
    answer = await response.json()

    db_campaign = storage.DbCampaign(web_context)
    source_campaign = await db_campaign.fetch(campaign_id)
    new_campaign = await db_campaign.fetch(answer['id'])

    #
    # campaign
    #

    assert new_campaign.state == 'READY'
    assert new_campaign.name == params['name']
    assert new_campaign.ticket == 'new ticket'
    assert new_campaign.owner_name == owner
    assert new_campaign.salt != source_campaign.salt
    assert new_campaign.entity_type == source_campaign.entity_type
    assert new_campaign.trend == source_campaign.trend
    assert new_campaign.kind == source_campaign.kind
    assert new_campaign.subkind == source_campaign.subkind
    assert new_campaign.efficiency == source_campaign.efficiency
    assert new_campaign.com_politic == source_campaign.com_politic
    assert new_campaign.global_control == source_campaign.global_control

    assert new_campaign.root_id == new_campaign.campaign_id
    assert new_campaign.parent_id is None
    assert new_campaign.child_id is None
    assert new_campaign.version_state == settings.VersionState.DRAFT

    #
    # segment
    #

    assert new_campaign.segment_id

    def serialize(settings):
        return [item.serialize() for item in settings]

    assert serialize(new_campaign.settings) == serialize(
        source_campaign.settings,
    )

    db_segment = storage.DbSegment(web_context)
    new_segment = await db_segment.fetch(new_campaign.segment_id)
    source_segment = await db_segment.fetch(source_campaign.segment_id)

    assert not new_segment.yql_shared_url
    assert not new_segment.aggregate_info
    assert new_segment.yt_table == campaign_utils.create_segment_table_url(
        web_context, new_campaign.campaign_id,
    )
    assert new_segment.mode == source_segment.mode
    assert new_segment.control == source_segment.control

    #
    # groups
    #
    db_group = storage.DbGroup(web_context)
    new_groups = await db_group.fetch_by_segment(new_segment.segment_id)
    source_groups = await db_group.fetch_by_segment(source_segment.segment_id)
    assert len(source_groups) == len(new_groups)

    for source, target in zip(source_groups, new_groups):
        assert target.params.state == settings.GROUP_STATE_NEW

        assert target.params.name == source.params.name
        assert target.params.share == source.params.share
        assert target.params.channel == source.params.channel
        assert target.params.content == source.params.content

        assert target.params.computed is None
        assert target.params.sent is None
        assert target.params.sender is None

        assert target.params.version_info
        assert target.params.version_info.root_id == target.params.id
        assert target.params.version_info.parent_id is None
        assert target.params.version_info.child_id is None
        assert (
            target.params.version_info.version_state
            == settings.VersionState.DRAFT
        )

    #
    # creatives
    #
    db_creative = storage.DbCreative(web_context)
    new_creatives = await db_creative.fetch_by_campaign_id(
        new_campaign.campaign_id, None, None,
    )
    source_creatives = await db_creative.fetch_by_campaign_id(
        source_campaign.campaign_id, None, None,
    )
    assert len(new_creatives) == len(source_creatives)

    for source, target in zip(source_creatives, new_creatives):
        assert target.params.serialize() == source.params.serialize()
        assert target.name == source.name

        assert target.root_id == target.creative_id
        assert target.parent_id is None
        assert target.child_id is None
        assert target.version_state == settings.VersionState.DRAFT


@pytest.mark.config(
    CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2,
    CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS,
)
@pytest.mark.parametrize('forget_creative_ticket', [True, False, None])
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_clone_creative(
        web_app_client, web_context, patch, forget_creative_ticket,
):
    @patch('crm_admin.utils.startrek.startrek.TicketManager.create_ticket')
    async def create_ticket(*args, **kwargs):
        return 'new ticket'

    @patch('crm_admin.utils.startrek.startrek.TicketManager.add_comment')
    async def add_comment(*args, **kwargs):
        pass

    campaign_id = 6
    params = {
        'source_campaign_id': campaign_id,
        'name': 'new campaign',
        'forget_creative_ticket': forget_creative_ticket,
    }
    owner = 'another user'

    response = await web_app_client.post(
        '/v1/campaigns/clone', json=params, headers={'X-Yandex-Login': owner},
    )

    assert response.status == 200
    answer = await response.json()

    db_campaign = storage.DbCampaign(web_context)
    source_campaign = await db_campaign.fetch(campaign_id)
    new_campaign = await db_campaign.fetch(answer['id'])

    if forget_creative_ticket:
        assert new_campaign.creative is None
    else:
        assert new_campaign.creative == source_campaign.creative


@pytest.mark.config(
    CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2,
    CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS,
)
@pytest.mark.parametrize('salt', [None, 'salt'])
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_clone_salt(web_app_client, patch, salt):
    @patch('crm_admin.utils.startrek.startrek.TicketManager.create_ticket')
    async def create_ticket(*args, **kwargs):
        return 'new ticket'

    @patch('crm_admin.utils.startrek.startrek.TicketManager.add_comment')
    async def add_comment(*args, **kwargs):
        pass

    campaign_id = 6
    params = {
        'source_campaign_id': campaign_id,
        'name': 'new campaign',
        'salt': salt,
    }
    owner = 'another user'

    response = await web_app_client.post(
        '/v1/campaigns/clone', json=params, headers={'X-Yandex-Login': owner},
    )

    assert response.status == 200
    answer = await response.json()

    if not salt:
        assert answer['salt'] == common.default_campaign_salt(answer['id'])
    else:
        assert answer['salt'] == salt


@pytest.mark.config(
    CRM_ADMIN_GROUPS_V2=CRM_ADMIN_GROUPS_V2,
    CRM_ADMIN_SETTINGS=audience_cfg.CRM_ADMIN_SETTINGS,
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_clone_feed(web_context, web_app_client, patch):
    @patch('crm_admin.utils.startrek.startrek.TicketManager.create_ticket')
    async def create_ticket(*args, **kwargs):
        return 'new ticket'

    @patch('crm_admin.utils.startrek.startrek.TicketManager.add_comment')
    async def add_comment(*args, **kwargs):
        pass

    @patch('crm_admin.utils.feed.copy_feed')
    async def copy_feed(*args, **kwargs):
        return 'new_feed'

    campaign_id = 5
    params = {'source_campaign_id': campaign_id, 'name': 'new campaign'}
    owner = 'user'

    response = await web_app_client.post(
        '/v1/campaigns/clone', json=params, headers={'X-Yandex-Login': owner},
    )

    assert response.status == 200
    answer = await response.json()

    assert copy_feed.calls

    db_group = storage.DbGroup(web_context)
    groups = await db_group.fetch_by_campaign_id(answer['id'])
    group = groups[0]

    assert group.params.feed_id == 'new_feed'
