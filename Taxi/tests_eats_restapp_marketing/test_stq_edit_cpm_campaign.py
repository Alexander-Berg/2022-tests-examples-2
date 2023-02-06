import pytest

from tests_eats_restapp_marketing import sql


PLACE_IDS = [1, 2, 3]
BANNER_ID = 1
FEEDS_ADMIN_BANNER_ID = 'banner_id'

INNER_CAMPAIGN_ID = '1'
PASSPORT_ID = 1229582676
STATUS_ACTIVE = 'active'
STATUS_SUSPENDED = 'suspended'

CAMPAIGN_PARAMETERS = {
    'averagecpm': 2,
    'spend_limit': 100,
    'strategy_type': 'kWbMaximumImpressions',
    'start_date': '2022-05-04T10:00:00+03:00',
    'finish_date': '2022-06-04T10:00:00+03:00',
}


@pytest.mark.pgsql('eats_tokens', files=['insert_tokens.sql'])
@pytest.mark.parametrize(
    'status', [pytest.param(STATUS_ACTIVE), pytest.param(STATUS_SUSPENDED)],
)
async def test_happy_path(
        mockserver,
        eats_restapp_marketing_db,
        pgsql,
        stq,
        stq_runner,
        mock_feeds_admin,
        mock_direct_campaigns,
        status,
):

    expected_campaign = sql.Campaign(
        id=INNER_CAMPAIGN_ID,
        campaign_type=sql.CampaignType.CPM_BANNER_CAMPAIGN,
        passport_id=PASSPORT_ID,
        parameters=CAMPAIGN_PARAMETERS,
        status=sql.CampaignStatus.UPDATING,
    )

    expected_campaign.id = sql.insert_campaign(
        eats_restapp_marketing_db, expected_campaign,
    )

    expected_banner = sql.Banner(
        id=BANNER_ID,
        place_id=PLACE_IDS[0],
        inner_campaign_id=INNER_CAMPAIGN_ID,
        banner_id=BANNER_ID,
        feeds_admin_id=FEEDS_ADMIN_BANNER_ID,
    )

    expected_banner.id = sql.insert_banner(
        eats_restapp_marketing_db, expected_banner,
    )

    await stq_runner.eats_restapp_marketing_edit_cpm_campaign.call(
        task_id=INNER_CAMPAIGN_ID,
        kwargs={
            'inner_campaign_id': INNER_CAMPAIGN_ID,
            'campaign_status': status,
        },
        expect_fail=False,
    )

    assert mock_direct_campaigns.times_called == 1

    if status == STATUS_ACTIVE:
        assert mock_feeds_admin.publish_banner_times_called == 1
        assert mock_feeds_admin.unpublish_banner_times_called == 1
    else:
        assert mock_feeds_admin.publish_banner_times_called == 0
        assert mock_feeds_admin.unpublish_banner_times_called == 0

    # check status
    if status == STATUS_ACTIVE:
        expected_campaign.status = sql.CampaignStatus.ACTIVE
    else:
        expected_campaign.status = sql.CampaignStatus.SUSPENDED

    actual_campaigns = sql.get_all_campaigns(eats_restapp_marketing_db)
    assert actual_campaigns == [expected_campaign]


@pytest.mark.parametrize(
    'status', [pytest.param(STATUS_ACTIVE), pytest.param(STATUS_SUSPENDED)],
)
async def test_no_tokens(
        mockserver,
        eats_restapp_marketing_db,
        pgsql,
        stq,
        stq_runner,
        mock_feeds_admin,
        mock_direct_campaigns,
        status,
):

    expected_campaign = sql.Campaign(
        id=INNER_CAMPAIGN_ID,
        campaign_type=sql.CampaignType.CPM_BANNER_CAMPAIGN,
        passport_id=PASSPORT_ID,
        parameters=CAMPAIGN_PARAMETERS,
        status=sql.CampaignStatus.UPDATING,
    )

    expected_campaign.id = sql.insert_campaign(
        eats_restapp_marketing_db, expected_campaign,
    )

    expected_banner = sql.Banner(
        id=BANNER_ID,
        place_id=PLACE_IDS[0],
        inner_campaign_id=INNER_CAMPAIGN_ID,
        banner_id=BANNER_ID,
        feeds_admin_id=FEEDS_ADMIN_BANNER_ID,
    )

    expected_banner.id = sql.insert_banner(
        eats_restapp_marketing_db, expected_banner,
    )

    await stq_runner.eats_restapp_marketing_edit_cpm_campaign.call(
        task_id=INNER_CAMPAIGN_ID,
        kwargs={
            'inner_campaign_id': INNER_CAMPAIGN_ID,
            'campaign_status': status,
        },
        expect_fail=False,
        reschedule_counter=1,
    )
