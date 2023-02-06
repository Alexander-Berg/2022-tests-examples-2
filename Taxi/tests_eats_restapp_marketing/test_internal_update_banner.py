import dataclasses

import pytest

from tests_eats_restapp_marketing import sql

INNER_CAMPAIGN_ID = '1'
PASSPORT_ID = 1
CAMPAIGN_PARAMETERS = {
    'averagecpm': 2,
    'spend_limit': 100,
    'strategy_type': 'kWbMaximumImpressions',
    'start_date': '2022-05-04T10:00:00+03:00',
    'finish_date': '2022-06-04T10:00:00+03:00',
}

CPM_BANNER_ID = 1
PLACE_ID = 1
AD_ID = 1
CREATIVE_ID = 1
URL = f'https://eda.yandex.ru/place/{CPM_BANNER_ID}'


@dataclasses.dataclass
class Request:
    cpm_banner_id: int
    url: str

    def asdict(self) -> dict:
        return dataclasses.asdict(self)


@pytest.fixture(name='internal_update_banner')
def _internal_update_banner(taxi_eats_restapp_marketing):
    """
    Фикстура для запросов в ручку `/internal/marketing/v1/ad/update-banner`.
    """

    url = '/internal/marketing/v1/ad/update-banner'

    async def post(body: Request):
        return await taxi_eats_restapp_marketing.post(url, json=body.asdict())

    return post


@pytest.mark.parametrize(
    'status_code, direct_calls',
    [
        pytest.param(404, 0, id='banner not found'),
        pytest.param(
            204,
            0,
            marks=(
                pytest.mark.campaigns(
                    sql.Campaign(
                        id=INNER_CAMPAIGN_ID, passport_id=PASSPORT_ID,
                    ),
                ),
                pytest.mark.banners(
                    sql.Banner(
                        id=CPM_BANNER_ID,
                        place_id=PLACE_ID,
                        inner_campaign_id=INNER_CAMPAIGN_ID,
                    ),
                ),
            ),
            id='no ad id',
        ),
        pytest.param(
            204,
            0,
            marks=(
                pytest.mark.campaigns(
                    sql.Campaign(
                        id=INNER_CAMPAIGN_ID, passport_id=PASSPORT_ID,
                    ),
                ),
                pytest.mark.banners(
                    sql.Banner(
                        id=CPM_BANNER_ID,
                        place_id=PLACE_ID,
                        inner_campaign_id=INNER_CAMPAIGN_ID,
                        ad_id=AD_ID,
                    ),
                ),
            ),
            id='no creative id',
        ),
        pytest.param(
            500,
            0,
            marks=(
                pytest.mark.campaigns(
                    sql.Campaign(
                        id=INNER_CAMPAIGN_ID, passport_id=PASSPORT_ID,
                    ),
                ),
                pytest.mark.banners(
                    sql.Banner(
                        id=CPM_BANNER_ID,
                        place_id=PLACE_ID,
                        inner_campaign_id=INNER_CAMPAIGN_ID,
                        ad_id=AD_ID,
                        creative_id=CREATIVE_ID,
                    ),
                ),
            ),
            id='broken campaign parameters',
        ),
        pytest.param(
            400,
            0,
            marks=(
                pytest.mark.campaigns(
                    sql.Campaign(
                        id=INNER_CAMPAIGN_ID,
                        passport_id=PASSPORT_ID,
                        parameters=CAMPAIGN_PARAMETERS,
                    ),
                ),
                pytest.mark.banners(
                    sql.Banner(
                        id=CPM_BANNER_ID,
                        place_id=PLACE_ID,
                        inner_campaign_id=INNER_CAMPAIGN_ID,
                        ad_id=AD_ID,
                        creative_id=CREATIVE_ID,
                    ),
                ),
            ),
            id='no token',
        ),
        pytest.param(
            204,
            1,
            marks=(
                pytest.mark.campaigns(
                    sql.Campaign(
                        id=INNER_CAMPAIGN_ID,
                        passport_id=PASSPORT_ID,
                        parameters=CAMPAIGN_PARAMETERS,
                    ),
                ),
                pytest.mark.banners(
                    sql.Banner(
                        id=CPM_BANNER_ID,
                        place_id=PLACE_ID,
                        inner_campaign_id=INNER_CAMPAIGN_ID,
                        ad_id=AD_ID,
                        creative_id=CREATIVE_ID,
                    ),
                ),
                pytest.mark.pgsql('eats_tokens', files=['insert_token.sql']),
            ),
            id='all good',
        ),
    ],
)
async def test_internal_update_banner(
        internal_update_banner,
        mock_direct_ads,
        status_code: int,
        direct_calls: int,
):
    @mock_direct_ads.request_assertion
    def _assertion(request):
        assert request.json['method'] == 'update'
        assert 'Ads' in request.json['params']

        ads = request.json['params']['Ads']
        assert ads

        advert = ads.pop(0)
        assert advert['Id'] == AD_ID
        assert 'CpmBannerAdBuilderAd' in advert

        cpm = advert['CpmBannerAdBuilderAd']
        assert 'Href' in cpm
        assert cpm['Href'] == URL

        assert 'Creative' in cpm
        assert cpm['Creative']['CreativeId'] == CREATIVE_ID

    response = await internal_update_banner(Request(CPM_BANNER_ID, URL))
    assert response.status_code == status_code
    assert mock_direct_ads.times_called == direct_calls
