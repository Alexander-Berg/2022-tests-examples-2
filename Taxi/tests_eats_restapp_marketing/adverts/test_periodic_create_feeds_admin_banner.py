import pytest


def get_periodic_config():
    return pytest.mark.config(
        EATS_RESTAPP_MARKETING_ADVERT_SETTINGS={
            'banner_periodic': {
                'cluster': 'hahn',
                'ids_table': '//table',
                'direct_data': '//table',
                'check_period': 100,
                'number_of_checks': 100,
            },
            'create_feeds_admin_banner_periodic': {
                'enabled': True,
                'period': 60,
            },
        },
    )


@get_periodic_config()
async def test_run_periodic(
        taxi_eats_restapp_marketing,
        testpoint,
        mock_feeds_admin,
        mock_table_banners,
        mock_table_campaigns,
        stq,
):
    # статус not_created -  не пытаемся создать баннер
    mock_table_campaigns.push_campaign(
        campaign_id=1, passport_id=111111, status='not_created',
    )
    inner_campaign_id_1 = mock_table_campaigns.get_inner_campaign_id(1)
    mock_table_banners.push_place_banner(
        place_id=1,
        banner_id=111,
        inner_campaign_id=inner_campaign_id_1,
        image='111banner_image_campaign_1',
    )

    mock_table_campaigns.push_campaign(
        campaign_id=2, passport_id=222222, status='in_creation_process',
    )
    inner_campaign_id_2 = mock_table_campaigns.get_inner_campaign_id(2)
    mock_table_banners.push_place_banner(
        place_id=2,
        banner_id=221,
        inner_campaign_id=inner_campaign_id_2,
        image='221_banner_image_campaign_2',
    )
    mock_table_banners.push_place_banner(
        place_id=3,
        banner_id=222,
        inner_campaign_id=inner_campaign_id_2,
        image='222_banner_image_campaign_2',
    )
    mock_table_banners.push_place_banner(
        place_id=4,
        banner_id=223,
        inner_campaign_id=inner_campaign_id_2,
        image='223_banner_image_campaign_2',
    )

    mock_table_campaigns.push_campaign(
        campaign_id=3, passport_id=333333, status='in_creation_process',
    )
    inner_campaign_id_3 = mock_table_campaigns.get_inner_campaign_id(3)
    # нет banner_id из директа - не пытаемся создать баннер
    mock_table_banners.push_place_banner(
        place_id=5,
        banner_id=None,
        inner_campaign_id=inner_campaign_id_3,
        image='null_banner_image_campaign_3',
    )
    mock_table_banners.push_place_banner(
        place_id=6,
        banner_id=331,
        inner_campaign_id=inner_campaign_id_3,
        image='331_banner_image_campaign_3',
    )

    @testpoint('create-feeds-admin-banner-worker-finished')
    def handle_finished(arg):
        pass

    async with taxi_eats_restapp_marketing.spawn_task(
            'create-feeds-admin-banner',
    ):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'

    assert (
        stq.eats_restapp_marketing_create_feeds_admin_banner.times_called == 4
    )
