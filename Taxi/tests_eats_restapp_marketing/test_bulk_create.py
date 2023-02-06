# flake8: noqa
# pylint: disable=import-error,wildcard-import
from eats_restapp_marketing_plugins.generated_tests import *

# Feel free to provide your custom implementation to override generated tests.
import json
import pytest


async def request_proxy_create_bulk(
        taxi_eats_restapp_marketing, partner_id, places,
):
    url = '/4.0/restapp-front/marketing/v1/ad/create-bulk'
    headers = {
        'X-YaEda-PartnerId': str(partner_id),
        'Content-type': 'application/json',
        'Authorization': 'token',
        'X-Remote-IP': '127.0.0.1',
    }
    body = {'places': places}
    extra = {'headers': headers, 'json': body}

    return await taxi_eats_restapp_marketing.post(url, **extra)


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_ADVERT_RATING_THRESHOLD={
        'rating_threshold': 3.5,
        'is_enabled': True,
        'batch_size': 1000,
        'periodic': {'interval_seconds': 3600},
    },
)
async def test_create_bulk(
        taxi_eats_restapp_marketing,
        mock_blackbox_tokeninfo,
        mock_auth_partner,
        mock_authorizer_allowed,
        mock_rating_info_ok,
        pgsql,
):
    response = await request_proxy_create_bulk(
        taxi_eats_restapp_marketing,
        123,
        [
            {'place_id': 1, 'averagecpc': 2, 'weekly_spend_limit': 5},
            {'place_id': 2, 'averagecpc': 2},
        ],
    )

    assert response.status_code == 201
    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        """
        SELECT
        place_id, averagecpc,
        weekly_spend_limit, passport_id
        FROM eats_restapp_marketing.advert
    """,
    )
    assert set(cursor) == {
        (1, 2000000, 5000000, 1229582676),
        (2, 2000000, None, 1229582676),
    }

    cursor.execute(
        """
        SELECT a.place_id,ac.token_id 
        FROM eats_restapp_marketing.advert_for_create as ac
        LEFT JOIN eats_restapp_marketing.advert a on a.id = ac.advert_id;
    """,
    )
    assert set(cursor) == {(1, 1), (2, 1)}


async def test_small_week_limit(
        taxi_eats_restapp_marketing,
        mock_blackbox_tokeninfo,
        mock_auth_partner,
        mock_authorizer_allowed,
        mock_rating_info_ok,
        pgsql,
):
    response = await request_proxy_create_bulk(
        taxi_eats_restapp_marketing,
        123,
        [
            {'place_id': 1, 'averagecpc': 2, 'weekly_spend_limit': 6},
            {'place_id': 2, 'averagecpc': 2},
            {'place_id': 3, 'averagecpc': 2, 'weekly_spend_limit': 1},
        ],
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'averagecpc can not be less than weekly_spend_limit',
        'details': {'error_slug': 'LOW_WEEK_LIMIT', 'place_ids': [3]},
    }


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_ADVERT_RATING_THRESHOLD={
        'rating_threshold': 3.5,
        'is_enabled': True,
        'batch_size': 1000,
        'periodic': {'interval_seconds': 3600},
    },
)
async def test_low_rating(
        taxi_eats_restapp_marketing,
        mock_blackbox_tokeninfo,
        mock_auth_partner,
        mock_authorizer_allowed,
        mock_rating_info_low,
        pgsql,
):
    response = await request_proxy_create_bulk(
        taxi_eats_restapp_marketing,
        123,
        [
            {'place_id': 1, 'averagecpc': 2, 'weekly_spend_limit': 5},
            {'place_id': 2, 'averagecpc': 2},
        ],
    )

    assert response.status_code == 400
    assert response.json()['code'] == '400'
    assert response.json()['message'] == 'low rating'
    assert response.json()['details']['error_slug'] == 'LOW_RATING'
    assert set(response.json()['details']['place_ids']) == {1, 2}


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_ADVERT_BULK_CREATE={'max_bulk_create_count': 3},
)
async def test_many_places(
        taxi_eats_restapp_marketing,
        mock_blackbox_tokeninfo,
        mock_authorizer_allowed,
        mock_rating_info_low,
        pgsql,
):
    response = await request_proxy_create_bulk(
        taxi_eats_restapp_marketing,
        123,
        [
            {'place_id': 1, 'averagecpc': 2},
            {'place_id': 2, 'averagecpc': 2},
            {'place_id': 3, 'averagecpc': 2},
            {'place_id': 4, 'averagecpc': 2},
        ],
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'many campaigns. Limit is 3',
        'details': {'error_slug': 'MANY_CAMPAIGNS', 'max_campaigns_count': 3},
    }


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_ADVERT_RATING_THRESHOLD={
        'rating_threshold': 3.5,
        'is_enabled': True,
        'batch_size': 1000,
        'periodic': {'interval_seconds': 3600},
    },
)
@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': 2,
            'business': 'restaurant',
            'revision_id': 1,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'sorting': {'weight': 100, 'popular': 0},
            'type': 'marketplace',
            'location': {'geo_point': [37.526789, 55.661552]},
            'brand': {
                'slug': 'Tacoland',
                'id': 3179,
                'name': '',
                'picture_scale_type': 'aspect_fit',
            },
            'price_category': {'id': 2, 'value': 3, 'name': ''},
            'rating': {'admin': 1, 'users': 4.76, 'shown': 4.8, 'count': 200},
        },
        {
            'id': 3,
            'revision_id': 1,
            'updated_at': '2020-11-26T00:00:00.000000Z',
            'type': 'native',
            'location': {'geo_point': [37.526789, 55.661552]},
            'brand': {
                'slug': 'Tacoland',
                'id': 3179,
                'name': '',
                'picture_scale_type': 'aspect_fit',
            },
        },
    ],
)
async def test_create_bulk_with_catalog(
        taxi_eats_restapp_marketing,
        mock_blackbox_tokeninfo,
        mock_auth_partner,
        mock_authorizer_allowed,
        mock_rating_info_ok,
        pgsql,
        mockserver,
):
    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage'
        '/v1/search/places-zones-ids',
    )
    def _eats_catalog_by_brands(request):
        return mockserver.make_response(
            json={
                'ids': [
                    {'place_id': 1, 'zone_ids': []},
                    {'place_id': 2, 'zone_ids': []},
                    {'place_id': 3, 'zone_ids': []},
                ],
            },
        )

    response = await request_proxy_create_bulk(
        taxi_eats_restapp_marketing,
        123,
        [
            {'place_id': 1, 'averagecpc': 2, 'weekly_spend_limit': 5},
            {'place_id': 2, 'averagecpc': 2},
        ],
    )

    assert response.status_code == 201
    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        """
        SELECT
        place_id, averagecpc,
        weekly_spend_limit, passport_id
        FROM eats_restapp_marketing.advert
    """,
    )
    assert set(cursor) == {
        (1, 2000000, 5000000, 1229582676),
        (2, 2000000, None, 1229582676),
    }

    cursor.execute(
        """
        SELECT a.place_id,ac.token_id 
        FROM eats_restapp_marketing.advert_for_create as ac
        LEFT JOIN eats_restapp_marketing.advert a on a.id = ac.advert_id;
    """,
    )
    assert set(cursor) == {(1, 1), (2, 1)}


@pytest.mark.pgsql('eats_restapp_marketing', files=['advert_resume.sql'])
@pytest.mark.config(
    EATS_RESTAPP_MARKETING_ADVERT_RATING_THRESHOLD={
        'rating_threshold': 3.5,
        'is_enabled': True,
        'batch_size': 1000,
        'periodic': {'interval_seconds': 3600},
    },
)
async def test_create_bulk_with_resume(
        taxi_eats_restapp_marketing,
        mock_blackbox_tokeninfo,
        mock_auth_partner,
        mock_authorizer_allowed,
        mock_rating_info_ok,
        pgsql,
):
    cursor = pgsql['eats_restapp_marketing'].cursor()
    # До создания балковых кампаний у нас уже есть созданная, но остановленная
    cursor.execute(
        """
        SELECT
        place_id, averagecpc,
        weekly_spend_limit, passport_id
        FROM eats_restapp_marketing.advert
    """,
    )
    assert set(cursor) == {(123, 10000000, 10000000000, 1229582676)}

    # Проверка, что данные в advert_for_create успешно обновятся
    cursor.execute(
        """
        SELECT
        averagecpc, weekly_spend_limit
        FROM eats_restapp_marketing.advert_for_create
    """,
    )
    assert set(cursor) == {(20000000, 15000000000)}

    response = await request_proxy_create_bulk(
        taxi_eats_restapp_marketing,
        123,
        [
            {'place_id': 1, 'averagecpc': 2, 'weekly_spend_limit': 5},
            {'place_id': 2, 'averagecpc': 2},
            {'place_id': 123, 'averagecpc': 15, 'weekly_spend_limit': 20000},
        ],
    )

    assert response.status_code == 201
    cursor.execute(
        """
        SELECT
        place_id, averagecpc,
        weekly_spend_limit, passport_id
        FROM eats_restapp_marketing.advert
    """,
    )
    assert set(cursor) == {
        (1, 2000000, 5000000, 1229582676),
        (2, 2000000, None, 1229582676),
        (123, 10000000, 10000000000, 1229582676),
    }

    cursor.execute(
        """
        SELECT a.place_id,ac.token_id, ac.averagecpc::bigint, 
        ac.weekly_spend_limit::bigint 
        FROM eats_restapp_marketing.advert_for_create as ac
        LEFT JOIN eats_restapp_marketing.advert a on a.id = ac.advert_id;
    """,
    )
    assert set(cursor) == {
        (1, 1, 2000000, 5000000),
        (2, 1, 2000000, None),
        (123, 1, 15000000, 20000000000),
    }


@pytest.mark.now('2021-01-10T03:00:00+00:00')
@pytest.mark.pgsql('eats_restapp_marketing', files=['advert_resume.sql'])
@pytest.mark.config(
    EATS_RESTAPP_MARKETING_ADVERT_RATING_THRESHOLD={
        'rating_threshold': 3.5,
        'is_enabled': True,
        'batch_size': 1000,
        'periodic': {'interval_seconds': 3600},
    },
    EATS_RESTAPP_MARKETING_ADVERT_ORDERS_STATS={
        'download_statistics': {
            'cluster': 'yt-local',
            'order_statisics': '//home/testsuite/orders',
            'task_period': 60,
            'batch_size': 1000,
            'order_cohorts_summary': '//home/testsuite/order_cohorts_summary',
        },
    },
)
@pytest.mark.yt(
    static_table_data=['yt_empty_order_cohorts_summary_table.yaml'],
)
async def test_create_bulk_attach_with_campaign_uuid(
        taxi_eats_restapp_marketing,
        mock_blackbox_tokeninfo,
        mock_auth_partner,
        mock_authorizer_allowed,
        mock_rating_info_ok,
        mock_blackbox_one,
        pgsql,
):
    cursor = pgsql['eats_restapp_marketing'].cursor()
    # До создания балковых кампаний у нас уже есть созданная, но остановленная
    cursor.execute(
        """
        SELECT
        place_id, averagecpc,
        weekly_spend_limit, passport_id, campaign_id
        FROM eats_restapp_marketing.advert
    """,
    )
    assert set(cursor) == {(123, 10000000, 10000000000, 1229582676, 123)}

    response = await request_proxy_create_bulk(
        taxi_eats_restapp_marketing,
        123,
        [
            {
                'place_id': 1,
                'averagecpc': 2,
                'weekly_spend_limit': 5,
                'campaign_uuid': 'aa945b93-759b-4e72-9af4-2ff26496291d',
            },
            {
                'place_id': 2,
                'averagecpc': 2,
                'campaign_uuid': 'aa945b93-759b-4e72-9af4-2ff26496291d',
            },
            {
                'place_id': 123,
                'averagecpc': 15,
                'weekly_spend_limit': 20000,
                'campaign_uuid': 'aa945b93-759b-4e72-9af4-2ff26496291d',
            },
        ],
    )

    assert response.status_code == 201
    assert response.json() == {
        'campaigns': [
            {
                'advert_id': 2,
                'average_cpc': 2,
                'campaign_uuid': 'aa945b93-759b-4e72-9af4-2ff26496291d',
                'created_at': '2021-01-10T00:00:00+0000',
                'has_access': True,
                'is_rating_status_ok': True,
                'place_id': 1,
                'status': 'process',
                'weekly_spend_limit': 5,
                'owner': {
                    'avatar': (
                        'https://avatars.mds.yandex.net/get-yapic/123/40x40'
                    ),
                    'display_name': 'Козьма Прутков',
                    'login': 'login_1',
                    'status': 'ok',
                    'yandex_uid': 1229582676,
                },
            },
            {
                'advert_id': 4,
                'average_cpc': 2,
                'campaign_uuid': 'aa945b93-759b-4e72-9af4-2ff26496291d',
                'created_at': '2021-01-10T00:00:00+0000',
                'has_access': True,
                'is_rating_status_ok': True,
                'place_id': 2,
                'status': 'process',
                'owner': {
                    'avatar': (
                        'https://avatars.mds.yandex.net/get-yapic/123/40x40'
                    ),
                    'display_name': 'Козьма Прутков',
                    'login': 'login_1',
                    'status': 'ok',
                    'yandex_uid': 1229582676,
                },
            },
            {
                'advert_id': 1,
                'average_cpc': 15,
                'campaign_id': 123,
                'campaign_uuid': 'aa945b93-759b-4e72-9af4-2ff26496291d',
                'created_at': '2021-01-10T00:00:00+0000',
                'has_access': True,
                'is_rating_status_ok': True,
                'place_id': 123,
                'status': 'process',
                'weekly_spend_limit': 20000,
                'owner': {
                    'avatar': (
                        'https://avatars.mds.yandex.net/get-yapic/123/40x40'
                    ),
                    'display_name': 'Козьма Прутков',
                    'login': 'login_1',
                    'status': 'ok',
                    'yandex_uid': 1229582676,
                },
            },
        ],
    }
    cursor.execute(
        """
        SELECT
        place_id, averagecpc,
        weekly_spend_limit, passport_id, campaign_id
        FROM eats_restapp_marketing.advert
    """,
    )
    # campaign_id set for advert in task "run_create_tasks"
    assert set(cursor) == {
        (1, 2000000, 5000000, 1229582676, None),
        (2, 2000000, None, 1229582676, None),
        (123, 10000000, 10000000000, 1229582676, 123),
    }

    cursor.execute(
        """
        SELECT a.place_id,ac.token_id, ac.averagecpc::bigint, 
        ac.weekly_spend_limit::bigint, ac.campaign_uuid
        FROM eats_restapp_marketing.advert_for_create as ac
        LEFT JOIN eats_restapp_marketing.advert a on a.id = ac.advert_id;
    """,
    )
    assert set(cursor) == {
        (1, 1, 2000000, 5000000, 'aa945b93-759b-4e72-9af4-2ff26496291d'),
        (2, 1, 2000000, None, 'aa945b93-759b-4e72-9af4-2ff26496291d'),
        (
            123,
            1,
            15000000,
            20000000000,
            'aa945b93-759b-4e72-9af4-2ff26496291d',
        ),
    }


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_ADVERT_RATING_THRESHOLD={
        'rating_threshold': 3.5,
        'is_enabled': True,
        'batch_size': 1000,
        'periodic': {'interval_seconds': 3600},
    },
)
async def test_create_bulk_with_one_campaign_uuid(
        taxi_eats_restapp_marketing,
        mock_blackbox_tokeninfo,
        mock_auth_partner,
        mock_authorizer_allowed,
        mock_rating_info_ok,
        pgsql,
):
    cursor = pgsql['eats_restapp_marketing'].cursor()
    # До создания балковых кампаний у нас уже есть созданная, но остановленная
    cursor.execute(
        """
        SELECT
        place_id, averagecpc,
        weekly_spend_limit, passport_id, campaign_id
        FROM eats_restapp_marketing.advert
    """,
    )
    assert list(cursor) == []

    response = await request_proxy_create_bulk(
        taxi_eats_restapp_marketing,
        123,
        [
            {
                'place_id': 1,
                'averagecpc': 2,
                'weekly_spend_limit': 5,
                'campaign_uuid': 'aa945b93-759b-4e72-9af4-2ff26496291d',
            },
            {
                'place_id': 2,
                'averagecpc': 2,
                'campaign_uuid': 'aa945b93-759b-4e72-9af4-2ff26496291d',
            },
            {
                'place_id': 123,
                'averagecpc': 15,
                'weekly_spend_limit': 20000,
                'campaign_uuid': 'aa945b93-759b-4e72-9af4-2ff26496291d',
            },
        ],
    )

    assert response.status_code == 201
    cursor.execute(
        """
        SELECT
        place_id, averagecpc,
        weekly_spend_limit, passport_id, campaign_id
        FROM eats_restapp_marketing.advert
    """,
    )
    # campaign_id set for advert in task "run_create_tasks"
    assert set(cursor) == {
        (1, 2000000, 5000000, 1229582676, None),
        (2, 2000000, None, 1229582676, None),
        (123, 15000000, 20000000000, 1229582676, None),
    }

    cursor.execute(
        """
        SELECT a.place_id,ac.token_id, ac.averagecpc::bigint, 
        ac.weekly_spend_limit::bigint, ac.campaign_uuid
        FROM eats_restapp_marketing.advert_for_create as ac
        LEFT JOIN eats_restapp_marketing.advert a on a.id = ac.advert_id;
    """,
    )
    assert set(cursor) == {
        (1, 1, 2000000, 5000000, 'aa945b93-759b-4e72-9af4-2ff26496291d'),
        (2, 1, 2000000, None, 'aa945b93-759b-4e72-9af4-2ff26496291d'),
        (
            123,
            1,
            15000000,
            20000000000,
            'aa945b93-759b-4e72-9af4-2ff26496291d',
        ),
    }


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_ADVERT_RATING_THRESHOLD={
        'rating_threshold': 3.5,
        'is_enabled': True,
        'batch_size': 1000,
        'periodic': {'interval_seconds': 3600},
    },
)
async def test_create_bulk_with_diff_campaign_uuid(
        taxi_eats_restapp_marketing,
        mock_blackbox_tokeninfo,
        mock_auth_partner,
        mock_authorizer_allowed,
        mock_rating_info_ok,
        pgsql,
):
    cursor = pgsql['eats_restapp_marketing'].cursor()
    # До создания балковых кампаний у нас уже есть созданная, но остановленная
    cursor.execute(
        """
        SELECT
        place_id, averagecpc,
        weekly_spend_limit, passport_id, campaign_id
        FROM eats_restapp_marketing.advert
    """,
    )
    assert list(cursor) == []

    response = await request_proxy_create_bulk(
        taxi_eats_restapp_marketing,
        123,
        [
            {
                'place_id': 1,
                'averagecpc': 2,
                'weekly_spend_limit': 5,
                'campaign_uuid': '111111-759b-4e12-9af4-2ff26496291d',
            },
            {
                'place_id': 2,
                'averagecpc': 2,
                'campaign_uuid': '222222-759b-4e72-9af4-2ff26496291d',
            },
            {
                'place_id': 123,
                'averagecpc': 15,
                'weekly_spend_limit': 20000,
                'campaign_uuid': '333333-759b-4e72-9af4-2ff26496291a',
            },
        ],
    )

    assert response.status_code == 201
    cursor.execute(
        """
        SELECT
        place_id, averagecpc,
        weekly_spend_limit, passport_id, campaign_id
        FROM eats_restapp_marketing.advert
    """,
    )
    # campaign_id set for advert in task "run_create_tasks"
    assert set(cursor) == {
        (1, 2000000, 5000000, 1229582676, None),
        (2, 2000000, None, 1229582676, None),
        (123, 15000000, 20000000000, 1229582676, None),
    }

    cursor.execute(
        """
        SELECT a.place_id,ac.token_id, ac.averagecpc::bigint, 
        ac.weekly_spend_limit::bigint, ac.campaign_uuid
        FROM eats_restapp_marketing.advert_for_create as ac
        LEFT JOIN eats_restapp_marketing.advert a on a.id = ac.advert_id;
    """,
    )
    assert set(cursor) == {
        (1, 1, 2000000, 5000000, '111111-759b-4e12-9af4-2ff26496291d'),
        (2, 1, 2000000, None, '222222-759b-4e72-9af4-2ff26496291d'),
        (123, 1, 15000000, 20000000000, '333333-759b-4e72-9af4-2ff26496291a'),
    }


@pytest.mark.pgsql(
    'eats_restapp_marketing', files=['advert_diff_campaign_id.sql'],
)
@pytest.mark.config(
    EATS_RESTAPP_MARKETING_ADVERT_RATING_THRESHOLD={
        'rating_threshold': 3.5,
        'is_enabled': True,
        'batch_size': 1000,
        'periodic': {'interval_seconds': 3600},
    },
)
async def test_create_bulk_with_diff_campaign_id_400(
        taxi_eats_restapp_marketing,
        mock_blackbox_tokeninfo,
        mock_auth_partner,
        mock_authorizer_allowed,
        mock_rating_info_ok,
        pgsql,
):
    cursor = pgsql['eats_restapp_marketing'].cursor()
    # До создания балковых кампаний у нас уже есть созданная, но остановленная
    cursor.execute(
        """
        SELECT
        place_id, averagecpc,
        weekly_spend_limit, passport_id, campaign_id
        FROM eats_restapp_marketing.advert
    """,
    )
    assert set(cursor) == {
        (123, 10000000, 10000000000, 1229582676, 123),
        (111, 10000000, 10000000000, 1229582676, 111),
    }

    response = await request_proxy_create_bulk(
        taxi_eats_restapp_marketing,
        123,
        [
            {
                'place_id': 111,
                'averagecpc': 2,
                'weekly_spend_limit': 5,
                'campaign_uuid': '111111-759b-4e12-9af4-2ff26496291d',
            },
            {
                'place_id': 123,
                'averagecpc': 2,
                'campaign_uuid': '111111-759b-4e12-9af4-2ff26496291d',
            },
            {
                'place_id': 2,
                'averagecpc': 15,
                'weekly_spend_limit': 20000,
                'campaign_uuid': '333333-759b-4e72-9af4-2ff26496291a',
            },
        ],
    )

    assert response.status_code == 400
    cursor.execute(
        """
        SELECT
        place_id, averagecpc,
        weekly_spend_limit, passport_id, campaign_id
        FROM eats_restapp_marketing.advert
    """,
    )
    # campaign_id set for advert in task "run_create_tasks"
    assert set(cursor) == {
        (123, 10000000, 10000000000, 1229582676, 123),
        (111, 10000000, 10000000000, 1229582676, 111),
    }

    cursor.execute(
        """
        SELECT a.place_id,ac.token_id, ac.averagecpc::bigint, 
        ac.weekly_spend_limit::bigint, ac.campaign_uuid
        FROM eats_restapp_marketing.advert_for_create as ac
        LEFT JOIN eats_restapp_marketing.advert a on a.id = ac.advert_id;
    """,
    )
    assert list(cursor) == []
