from tests_eats_restapp_marketing import sql

CAMPAIGN_ID = 'campaign1'
YANDEX_UID = 'yandex_uid1'
PLACE_IDS = [1, 2, 3]
BANNER_ID = 1
FEEDS_ADMIN_BANNER_ID = 'banner_id'
FEEDS_ADMIN_MEDIA_ID = 'media_id1'

INNER_CAMPAIGN_ID = '1'
PASSPORT_ID = 1
STATUS_IN_CREATION_PROCESS = 'in_creation_process'
STATUS_READY = 'ready'


async def test_happy_path(
        testpoint,
        mockserver,
        eats_restapp_marketing_db,
        pgsql,
        stq,
        stq_runner,
        mock_feeds_admin,
):

    expected_campaign = sql.Campaign(
        id=INNER_CAMPAIGN_ID,
        campaign_type=sql.CampaignType.CPM_BANNER_CAMPAIGN,
        passport_id=1229582676,
        parameters={
            'averagecpm': 2,
            'spend_limit': 100,
            'strategy_type': 'kWbMaximumImpressions',
        },
        status=sql.CampaignStatus.IN_CREATION_PROCESS,
    )

    expected_campaign.id = sql.insert_campaign(
        eats_restapp_marketing_db, expected_campaign,
    )

    expected_banner = sql.Banner(
        id=BANNER_ID,
        place_id=PLACE_IDS[0],
        inner_campaign_id=INNER_CAMPAIGN_ID,
        banner_id=BANNER_ID,
    )

    expected_banner.id = sql.insert_banner(
        eats_restapp_marketing_db, expected_banner,
    )

    await stq_runner.eats_restapp_marketing_create_feeds_admin_banner.call(
        task_id='eats_restapp_marketing_create_feeds_admin_banner_task_1',
        kwargs={
            'campaign_id': CAMPAIGN_ID,
            'yandex_uid': YANDEX_UID,
            'banner_id': BANNER_ID,
            'media_id': FEEDS_ADMIN_MEDIA_ID,
            'restaurant_ids': [PLACE_IDS[0]],
        },
        expect_fail=False,
    )

    # check feeds-admin
    is_request_ok = mock_feeds_admin.check_create_banner_request(
        media_id=FEEDS_ADMIN_MEDIA_ID,
        campaign_id=CAMPAIGN_ID,
        yandex_uid=YANDEX_UID,
        banner_id=BANNER_ID,
        place_id=PLACE_IDS[0],
    )
    assert is_request_ok is True
    assert mock_feeds_admin.create_banner_times_called == 1

    # check feeds_admin_id updated
    expected_banner.feeds_admin_id = 'direct_banner_id_' + str(BANNER_ID)
    actual_banners = sql.get_all_banners(eats_restapp_marketing_db)
    assert actual_banners == [expected_banner]

    # check status
    expected_campaign.status = sql.CampaignStatus.READY
    actual_campaigns = sql.get_all_campaigns(eats_restapp_marketing_db)
    assert actual_campaigns == [expected_campaign]


async def test_feeds_admin_response400(
        testpoint,
        mockserver,
        taxi_eats_restapp_marketing,
        pgsql,
        eats_restapp_marketing_db,
        stq_runner,
        mock_feeds_admin,
):

    expected_campaign = sql.Campaign(
        id=INNER_CAMPAIGN_ID,
        campaign_type=sql.CampaignType.CPM_BANNER_CAMPAIGN,
        passport_id=1229582676,
        parameters={
            'averagecpm': 2,
            'spend_limit': 100,
            'strategy_type': 'kWbMaximumImpressions',
        },
        status=sql.CampaignStatus.IN_CREATION_PROCESS,
    )
    expected_campaign.id = sql.insert_campaign(
        eats_restapp_marketing_db, expected_campaign,
    )

    expected_banner = sql.Banner(
        id=BANNER_ID,
        place_id=PLACE_IDS[0],
        inner_campaign_id=INNER_CAMPAIGN_ID,
        banner_id=BANNER_ID,
    )
    expected_banner.id = sql.insert_banner(
        eats_restapp_marketing_db, expected_banner,
    )

    # prepare feeds-admin response
    mock_feeds_admin.set_status_code(400)

    # run stq
    await stq_runner.eats_restapp_marketing_create_feeds_admin_banner.call(
        task_id='eats_restapp_marketing_create_feeds_admin_banner_task_1',
        kwargs={
            'campaign_id': CAMPAIGN_ID,
            'yandex_uid': YANDEX_UID,
            'banner_id': BANNER_ID,
            'media_id': FEEDS_ADMIN_MEDIA_ID,
            'restaurant_ids': PLACE_IDS,
        },
        expect_fail=False,
    )
    # check feeds_admin_id not updated
    actual_banners = sql.get_all_banners(eats_restapp_marketing_db)
    assert actual_banners == [expected_banner]
    assert mock_feeds_admin.create_banner_times_called == 1

    # check status
    actual_campaigns = sql.get_all_campaigns(eats_restapp_marketing_db)
    assert actual_campaigns == [expected_campaign]


async def test_feeds_admin_response503(
        testpoint,
        mockserver,
        taxi_eats_restapp_marketing,
        pgsql,
        stq_runner,
        stq,
        mock_feeds_admin,
        eats_restapp_marketing_db,
):

    expected_campaign = sql.Campaign(
        id=INNER_CAMPAIGN_ID,
        campaign_type=sql.CampaignType.CPM_BANNER_CAMPAIGN,
        passport_id=1229582676,
        parameters={
            'averagecpm': 2,
            'spend_limit': 100,
            'strategy_type': 'kWbMaximumImpressions',
        },
        status=sql.CampaignStatus.IN_CREATION_PROCESS,
    )
    expected_campaign.id = sql.insert_campaign(
        eats_restapp_marketing_db, expected_campaign,
    )

    expected_banner = sql.Banner(
        id=BANNER_ID,
        place_id=PLACE_IDS[0],
        inner_campaign_id=INNER_CAMPAIGN_ID,
        banner_id=BANNER_ID,
    )
    expected_banner.id = sql.insert_banner(
        eats_restapp_marketing_db, expected_banner,
    )

    # prepare feeds-admin response
    mock_feeds_admin.set_status_code(503)

    # run stq
    await stq_runner.eats_restapp_marketing_create_feeds_admin_banner.call(
        task_id='eats_restapp_marketing_create_feeds_admin_banner_task_1',
        kwargs={
            'campaign_id': CAMPAIGN_ID,
            'yandex_uid': YANDEX_UID,
            'banner_id': BANNER_ID,
            'media_id': FEEDS_ADMIN_MEDIA_ID,
            'restaurant_ids': PLACE_IDS,
        },
        expect_fail=False,
    )
    # check feeds_admin_id not updated
    actual_banners = sql.get_all_banners(eats_restapp_marketing_db)
    assert actual_banners == [expected_banner]
    # 503 error - stq retrying
    assert mock_feeds_admin.create_banner_times_called > 1

    # check status
    # check status
    actual_campaigns = sql.get_all_campaigns(eats_restapp_marketing_db)
    assert actual_campaigns == [expected_campaign]
