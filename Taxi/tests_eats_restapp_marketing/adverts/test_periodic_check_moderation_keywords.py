import pytest

from tests_eats_restapp_marketing import sql

DEFAULT_PATAMETERS = {
    'averagecpm': 2,
    'spend_limit': 100,
    'strategy_type': 'kWbMaximumImpressions',
    'start_date': '2022-07-20T11:20:00+03:00',
    'finish_date': '2022-08-20T11:20:00+03:00',
}


@pytest.mark.pgsql('eats_restapp_marketing', files=['insert_adverts.sql'])
@pytest.mark.pgsql('eats_tokens', files=['insert_tokens.sql'])
@pytest.mark.campaigns(
    sql.Campaign(
        id='1',
        campaign_type=sql.CampaignType.CPM_BANNER_CAMPAIGN,
        campaign_id='1',
        passport_id=111111,
        parameters=DEFAULT_PATAMETERS,
    ),
    sql.Campaign(
        id='2',
        campaign_type=sql.CampaignType.CPM_BANNER_CAMPAIGN,
        campaign_id='2',
        passport_id=1229582676,
        parameters=DEFAULT_PATAMETERS,
    ),
    sql.Campaign(
        id='3',
        campaign_type=sql.CampaignType.CPM_BANNER_CAMPAIGN,
        campaign_id='3',
        passport_id=444,
        parameters=DEFAULT_PATAMETERS,
    ),
)
@pytest.mark.banners(
    sql.Banner(id=1, place_id=1, inner_campaign_id='1'),
    sql.Banner(id=2, place_id=2, inner_campaign_id='2'),
    sql.Banner(id=3, place_id=3, inner_campaign_id='3'),
)
async def test_periodic_check_moderation_keywords_run(
        testpoint, mockserver, taxi_eats_restapp_marketing, pgsql, load_json,
):
    cursor = pgsql['eats_restapp_marketing'].cursor()

    get_keywords = load_json('get_keywords.json')

    @mockserver.json_handler('/direct/json/v5/keywords')
    def _keywords_handler(req):
        return mockserver.make_response(status=200, json=get_keywords)

    await taxi_eats_restapp_marketing.run_periodic_task(
        'eats-restapp-marketing-periodic-check-moderation-keywords-periodic',
    )

    cursor.execute(
        """
        SELECT
            keyword_id,
            keyword,
            advert_id,
            state,
            status,
            inner_campaign_id
        FROM eats_restapp_marketing.keywords
        ORDER BY keyword_id
        """,
    )

    assert set(cursor) == {
        (1, None, 1114, 'on', 'draft', None),
        (2, None, 3913, 'on', 'rejected', None),
        (3, 'Пироги', 1111, 'on', 'accepted', None),
        (4, 'Пицца', 2222, 'off', 'accepted', None),
        (5, 'Напитки', 2222, 'on', 'draft', None),
        (6, None, 2222, 'off', 'rejected', None),
        (7, 'еда', 2222, 'on', 'accepted', None),
        (8, 'еда_1', None, 'on', 'accepted', '1'),
        (9, 'еда_2', None, 'on', 'accepted', '1'),
        (10, None, None, 'suspended', 'unknown', '4'),
    }
