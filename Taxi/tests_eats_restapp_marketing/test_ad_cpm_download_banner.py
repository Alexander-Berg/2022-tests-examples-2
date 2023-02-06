from urllib import parse

import pytest

from tests_eats_restapp_marketing import sql


@pytest.fixture(name='cpm_download_banner')
def _cpm_download_banner(taxi_eats_restapp_marketing):
    """
    Фикстура для запросов в ручку
    `/4.0/restapp-front/marketing/v1/ad/cpm/download-banner`
    """

    url = '/4.0/restapp-front/marketing/v1/ad/cpm/download_banner'

    async def get(partner_id: int = 1, campaign_id: str = '1'):
        headers = {'X-YaEda-PartnerId': str(partner_id)}
        query = {'campaign_id': campaign_id}
        return await taxi_eats_restapp_marketing.get(
            url + '?' + parse.urlencode(query), headers=headers,
        )

    return get


async def test_happy_path(
        cpm_download_banner,
        mock_feeds_admin,
        eats_restapp_marketing_db,
        mock_auth_partner,
):

    place_id_1: int = 111111
    inner_campaign_id_1: str = '1'
    image_1: str = 'image_1_identificator'
    banner_1 = sql.Banner(
        id=1,
        place_id=place_id_1,
        inner_campaign_id=inner_campaign_id_1,
        image=image_1,
    )
    sql.insert_campaign(
        eats_restapp_marketing_db, sql.Campaign(id=inner_campaign_id_1),
    )

    sql.insert_banner(database=eats_restapp_marketing_db, banner=banner_1)

    place_id_2: int = 222222
    inner_campaign_id_2: str = '2'
    image_2: str = 'image_2_identificator'
    banner_2 = sql.Banner(
        id=2,
        place_id=place_id_2,
        inner_campaign_id=inner_campaign_id_2,
        image=image_2,
    )
    sql.insert_campaign(
        eats_restapp_marketing_db, sql.Campaign(id=inner_campaign_id_2),
    )

    sql.insert_banner(database=eats_restapp_marketing_db, banner=banner_2)

    response = await cpm_download_banner(campaign_id=inner_campaign_id_1)
    assert mock_feeds_admin.download_banner_times_called == 1
    assert mock_feeds_admin.check_download_banner_request(media_id=image_1)
    assert response.status_code == 200

    response = await cpm_download_banner(campaign_id=inner_campaign_id_2)
    assert mock_feeds_admin.download_banner_times_called == 2
    assert mock_feeds_admin.check_download_banner_request(media_id=image_2)
    assert response.status_code == 200


async def test_no_campaign_404(
        cpm_download_banner,
        mock_feeds_admin,
        eats_restapp_marketing_db,
        mock_auth_partner,
):
    place_id_1: int = 111111
    contained_campaign: str = '1'
    image_1 = 'image_1_identificator'
    banner_1 = sql.Banner(
        id=1,
        place_id=place_id_1,
        inner_campaign_id=contained_campaign,
        image=image_1,
    )
    sql.insert_campaign(
        eats_restapp_marketing_db, sql.Campaign(id=contained_campaign),
    )

    sql.insert_banner(database=eats_restapp_marketing_db, banner=banner_1)

    noncontained_campaign: str = '2'
    response = await cpm_download_banner(campaign_id=noncontained_campaign)
    assert mock_feeds_admin.download_banner_times_called == 0
    assert response.status_code == 404


async def test_feeds_admin_no_response_400(
        cpm_download_banner,
        mock_feeds_admin,
        eats_restapp_marketing_db,
        mock_auth_partner,
):
    mock_feeds_admin.set_status_code(500)
    place_id_1: int = 111111
    inner_campaign_id_1: str = '1'
    image_1 = 'image_1_identificator'
    banner_1 = sql.Banner(
        id=1,
        place_id=place_id_1,
        inner_campaign_id=inner_campaign_id_1,
        image=image_1,
    )
    sql.insert_campaign(
        eats_restapp_marketing_db, sql.Campaign(id=inner_campaign_id_1),
    )

    sql.insert_banner(database=eats_restapp_marketing_db, banner=banner_1)
    response = await cpm_download_banner(campaign_id=inner_campaign_id_1)
    assert response.status_code == 400
