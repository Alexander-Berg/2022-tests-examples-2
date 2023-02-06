import pytest

from tests_eats_restapp_marketing import sql


TASK_ID = 'task123'


CAMPAIGN_ID = 'campaign1'
YANDEX_UID = 'yandex_uid1'
PLACE_IDS = [1, 2, 3]
BANNER_ID = 1
FEEDS_ADMIN_MEDIA_ID = 'media_id1'

INNER_CAMPAIGN_ID = '1'
PASSPORT_ID = 1229582676
STATUS_IN_CREATION_PROCESS = 'in_creation_process'
STATUS_READY = 'ready'


@pytest.mark.parametrize(
    'status',
    [
        pytest.param('approved', id='approve'),
        pytest.param('rejected', id='reject'),
    ],
)
@pytest.mark.pgsql('eats_tokens', files=['insert_tokens.sql'])
@pytest.mark.now('2021-01-01T12:00:00Z')
async def test_moderation_result_post_basic(
        eats_restapp_marketing_db, taxi_eats_restapp_marketing, status, stq,
):
    expected_campaign = sql.Campaign(
        id=INNER_CAMPAIGN_ID,
        campaign_type=sql.CampaignType.CPM_BANNER_CAMPAIGN,
        passport_id=PASSPORT_ID,
        parameters={
            'averagecpm': 2,
            'spend_limit': 100,
            'strategy_type': 'kWbMaximumImpressions',
            'start_date': '2022-01-01T00:00:00+00:00',
            'finish_date': '2022-10-01T00:00:00+00:00',
        },
        status=sql.CampaignStatus.NOT_CREATED,
    )

    expected_campaign.id = sql.insert_campaign(
        eats_restapp_marketing_db, expected_campaign,
    )

    expected_banner = sql.Banner(
        id=BANNER_ID,
        place_id=PLACE_IDS[0],
        inner_campaign_id=INNER_CAMPAIGN_ID,
        image=FEEDS_ADMIN_MEDIA_ID,
        banner_id=BANNER_ID,
        status=sql.BannerStatus.IN_MODERATION,
    )

    expected_banner.id = sql.insert_banner(
        eats_restapp_marketing_db, expected_banner,
    )

    response = await taxi_eats_restapp_marketing.post(
        '/internal/marketing/v1/ad/moderation',
        json={
            'task_id': TASK_ID,
            'context': {
                'media_id': FEEDS_ADMIN_MEDIA_ID,
                'data': [{'id': '1', 'place_id': '2'}],
            },
            'queue': 'restapp_moderation_cpm_banners',
            'status': status,
            'actual_payload': {},
            'payload': {'photo_url': 'gsfghhs'},
        },
    )

    assert response.status_code == 200

    if status == 'approved':
        expected_banner.status = sql.BannerStatus.APPROVED
    else:
        expected_banner.status = sql.BannerStatus.REJECTED

    actual_banners = sql.get_all_banners(eats_restapp_marketing_db)
    assert actual_banners == [expected_banner]

    if status == 'approved':
        assert stq.eats_restapp_marketing_add_banner_ads.times_called == 1
        task = stq.eats_restapp_marketing_add_banner_ads.next_call()
        task_kwargs = task['kwargs']
        task_kwargs.pop('log_extra')
        assert task_kwargs == {
            'token_id': 2,
            'inner_campaign_id': INNER_CAMPAIGN_ID,
        }


@pytest.mark.parametrize(
    'status, code',
    [
        pytest.param('approved', 404, id='approve'),
        pytest.param('rejected', 404, id='reject'),
    ],
)
@pytest.mark.pgsql('eats_tokens', files=['insert_tokens.sql'])
@pytest.mark.now('2021-01-01T12:00:00Z')
async def test_moderation_result_empty_banners(
        eats_restapp_marketing_db, taxi_eats_restapp_marketing, status, code,
):
    expected_campaign = sql.Campaign(
        id=INNER_CAMPAIGN_ID,
        campaign_type=sql.CampaignType.CPM_BANNER_CAMPAIGN,
        passport_id=PASSPORT_ID,
        parameters={
            'averagecpm': 2,
            'spend_limit': 100,
            'strategy_type': 'kWbMaximumImpressions',
            'start_date': '2022-01-01T00:00:00+00:00',
            'finish_date': '2022-10-01T00:00:00+00:00',
        },
        status=sql.CampaignStatus.NOT_CREATED,
    )

    expected_campaign.id = sql.insert_campaign(
        eats_restapp_marketing_db, expected_campaign,
    )

    response = await taxi_eats_restapp_marketing.post(
        '/internal/marketing/v1/ad/moderation',
        json={
            'task_id': TASK_ID,
            'context': {
                'media_id': FEEDS_ADMIN_MEDIA_ID,
                'data': [{'id': '1', 'place_id': '1'}],
            },
            'queue': 'restapp_moderation_cpm_banners',
            'status': status,
            'actual_payload': {},
            'payload': {'photo_url': 'gsfghhs'},
        },
    )

    assert response.status_code == code


@pytest.mark.now('2021-01-01T12:00:00Z')
async def test_moderation_result_post_invalid(
        taxi_eats_restapp_marketing, eats_restapp_marketing_db,
):

    expected_campaign = sql.Campaign(
        id=INNER_CAMPAIGN_ID,
        campaign_type=sql.CampaignType.CPM_BANNER_CAMPAIGN,
        passport_id=PASSPORT_ID,
        parameters={
            'averagecpm': 2,
            'spend_limit': 100,
            'strategy_type': 'kWbMaximumImpressions',
            'start_date': '2022-01-01T00:00:00+00:00',
            'finish_date': '2022-10-01T00:00:00+00:00',
        },
        status=sql.CampaignStatus.NOT_CREATED,
    )

    expected_campaign.id = sql.insert_campaign(
        eats_restapp_marketing_db, expected_campaign,
    )

    expected_banner = sql.Banner(
        id=BANNER_ID,
        place_id=PLACE_IDS[0],
        inner_campaign_id=INNER_CAMPAIGN_ID,
        image=FEEDS_ADMIN_MEDIA_ID,
        banner_id=BANNER_ID,
        status=sql.BannerStatus.IN_MODERATION,
    )

    expected_banner.id = sql.insert_banner(
        eats_restapp_marketing_db, expected_banner,
    )

    response = await taxi_eats_restapp_marketing.post(
        '/internal/marketing/v1/ad/moderation',
        json={
            'task_id': TASK_ID,
            'context': {
                'media_id': FEEDS_ADMIN_MEDIA_ID,
                'data': [{'id': '1', 'place_id': '1'}],
            },
            'queue': 'restapp_moderation_cpm_banners',
            'status': 'approved',
            'actual_payload': {},
            'payload': {'photo_url': 'gsfghhs'},
        },
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    'status, code',
    [
        pytest.param('approved', 404, id='approve'),
        pytest.param('rejected', 404, id='reject'),
    ],
)
@pytest.mark.pgsql('eats_tokens', files=['insert_tokens.sql'])
@pytest.mark.now('2021-01-01T12:00:00Z')
async def test_moderation_result_empty_banners_request(
        eats_restapp_marketing_db, taxi_eats_restapp_marketing, status, code,
):
    expected_campaign = sql.Campaign(
        id=INNER_CAMPAIGN_ID,
        campaign_type=sql.CampaignType.CPM_BANNER_CAMPAIGN,
        passport_id=PASSPORT_ID,
        parameters={
            'averagecpm': 2,
            'spend_limit': 100,
            'strategy_type': 'kWbMaximumImpressions',
            'start_date': '2022-01-01T00:00:00+00:00',
            'finish_date': '2022-10-01T00:00:00+00:00',
        },
        status=sql.CampaignStatus.NOT_CREATED,
    )

    expected_campaign.id = sql.insert_campaign(
        eats_restapp_marketing_db, expected_campaign,
    )

    response = await taxi_eats_restapp_marketing.post(
        '/internal/marketing/v1/ad/moderation',
        json={
            'task_id': TASK_ID,
            'context': {'media_id': FEEDS_ADMIN_MEDIA_ID, 'data': []},
            'queue': 'restapp_moderation_cpm_banners',
            'status': status,
            'actual_payload': {},
            'payload': {'photo_url': 'gsfghhs'},
        },
    )

    assert response.status_code == code
