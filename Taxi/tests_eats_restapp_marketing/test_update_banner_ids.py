import pytest

from tests_eats_restapp_marketing import sql


OP_ID = 'abcde12345'

AD_ID1 = 456
AD_ID2 = 654

BANNER_ID1 = 123
BANNER_ID2 = 321


ADVERT_CONFIG = {
    'banner_periodic': {
        'caesar_cluster': 'yt-local',
        'caesar_table': '//home/testsuite/latest',
        'check_period': 1,
        'cluster': 'yt-local',
        'direct_data': '//home/testsuite/Banners',
        'ids_table': '//home/testsuite/banner_ids',
        'number_of_checks': 150,
        'task_period': 3600,
        'tmp_directory': '//tmp',
        'use_caesar': True,
    },
    'create_feeds_admin_banner_periodic': {'enabled': True, 'period': 60},
}


def fill_tabels(eats_restapp_marketing_db):
    inner_campaign_id = '1'
    banner_id = 1
    place_id = 2
    ad_id = 654

    banner = sql.Banner(
        id=banner_id,
        place_id=place_id,
        inner_campaign_id=inner_campaign_id,
        ad_id=ad_id,
    )
    sql.insert_campaign(
        eats_restapp_marketing_db, sql.Campaign(id=inner_campaign_id),
    )

    sql.insert_banner(database=eats_restapp_marketing_db, banner=banner)

    inner_advert_id = 1
    ad_id = 456
    token_id = 465
    place_id = 1
    average_cpc = 21000000
    passport_id = 11
    advert_id = 1

    advert = sql.Advert(
        id=inner_advert_id,
        place_id=place_id,
        average_cpc=average_cpc,
        passport_id=passport_id,
        is_active=False,
        ad_id=ad_id,
    )

    sql.insert_advert(database=eats_restapp_marketing_db, advert=advert)

    advert_for_create = sql.AdvertForCreate(
        id=inner_advert_id,
        advert_id=advert_id,
        token_id=token_id,
        average_cpc=average_cpc,
    )

    sql.insert_advert_for_create(
        database=eats_restapp_marketing_db,
        advert_for_create=advert_for_create,
    )


@pytest.mark.config(EATS_RESTAPP_MARKETING_ADVERT_SETTINGS=ADVERT_CONFIG)
@pytest.mark.yt(static_table_data=['yt_banners_table.yaml'])
async def test_update_banner_ids(
        taxi_eats_restapp_marketing,
        mockserver,
        testpoint,
        pgsql,
        yt_apply,
        eats_restapp_marketing_db,
):
    @mockserver.json_handler('/yql/api/v2/operations')
    def _new_operation(request):
        return {'id': OP_ID}

    @mockserver.json_handler(
        r'/yql/api/v2/operations/{}'.format(OP_ID), regex=True,
    )
    def _operation_status(request):
        return {'id': OP_ID, 'status': 'COMPLETED'}

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<operation_id>\w+)/share_id', regex=True,
    )
    def _operation_url(request, operation_id):
        return 'this_is_share_url'

    fill_tabels(eats_restapp_marketing_db)

    @testpoint('update-banner-ids-finished')
    async def handle_finished(arg):
        cursor = pgsql['eats_restapp_marketing'].cursor()
        cursor.execute(
            'SELECT banner_id '
            'FROM eats_restapp_marketing.banners '
            'WHERE ad_id IN ({})'.format(str(AD_ID2)),
        )
        rows = cursor.fetchall()
        print(rows)
        assert rows[0][0] == BANNER_ID2

        cursor = pgsql['eats_restapp_marketing'].cursor()
        cursor.execute(
            'SELECT banner_id '
            'FROM eats_restapp_marketing.advert '
            'WHERE ad_id IN ({})'.format(str(AD_ID1)),
        )
        rows = cursor.fetchall()
        assert rows[0][0] == BANNER_ID1

    async with taxi_eats_restapp_marketing.spawn_task('update-banner-ids'):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'
