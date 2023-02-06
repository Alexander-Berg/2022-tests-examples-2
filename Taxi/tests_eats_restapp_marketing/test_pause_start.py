import dataclasses
import enum
import typing

import pytest

from tests_eats_restapp_marketing import sql


CAMPAIGN_PARAMETERS = {
    'averagecpm': 2,
    'spend_limit': 100,
    'strategy_type': 'kWbMaximumImpressions',
    'start_date': '2022-05-04T10:00:00+03:00',
    'finish_date': '2022-06-04T10:00:00+03:00',
}

INNER_CAMPAIGN_ID = '1'


class CampaignType(str, enum.Enum):
    CPC = 'cpc'
    CPM = 'cpm'


@dataclasses.dataclass
class SuspendableCampaign:
    campaign_id: str
    campaign_type: CampaignType


@dataclasses.dataclass
class Request:
    campaigns: typing.List[SuspendableCampaign] = dataclasses.field(
        default_factory=list,
    )

    def asdict(self) -> dict:
        return dataclasses.asdict(self)


@pytest.fixture(name='pause_handler')
def _pause_handler(taxi_eats_restapp_marketing):
    """
    Фикстура для запросов в ручку `/4.0/restapp-front/marketing/v1/ad/pause`.
    """

    url = '/4.0/restapp-front/marketing/v1/ad/pause'

    async def post(body: Request, partner_id: int = 1):
        headers = {
            'X-YaEda-PartnerId': str(partner_id),
            'Content-type': 'application/json',
            'Authorization': 'token',
            'X-Remote-IP': '127.0.0.1',
        }
        return await taxi_eats_restapp_marketing.post(
            url, headers=headers, json=body.asdict(),
        )

    return post


@pytest.fixture(name='start_handler')
def _start_handler(taxi_eats_restapp_marketing):
    """
    Фикстура для запросов в ручку `/4.0/restapp-front/marketing/v1/ad/start`.
    """

    url = '/4.0/restapp-front/marketing/v1/ad/start'

    async def post(body: Request, partner_id: int = 1):
        headers = {
            'X-YaEda-PartnerId': str(partner_id),
            'Content-type': 'application/json',
            'Authorization': 'token',
            'X-Remote-IP': '127.0.0.1',
        }
        return await taxi_eats_restapp_marketing.post(
            url, headers=headers, json=body.asdict(),
        )

    return post


@pytest.mark.parametrize(
    'campaign_ids, banners, campaigns, feeds_calls',
    [
        pytest.param([], [], [], 0, id='no campaigns in request'),
        pytest.param(['1', '2'], [], [], 0, id='no campaigns found'),
        pytest.param(
            [INNER_CAMPAIGN_ID],
            [
                sql.Banner(
                    id=1,
                    place_id=1,
                    inner_campaign_id=INNER_CAMPAIGN_ID,
                    status=sql.BannerStatus.IN_PROCESS,
                ),
            ],
            [
                sql.Campaign(
                    id=INNER_CAMPAIGN_ID,
                    parameters=CAMPAIGN_PARAMETERS,
                    status=sql.CampaignStatus.SUSPENDED,
                ),
            ],
            0,
            marks=(
                pytest.mark.campaigns(
                    sql.Campaign(
                        id=INNER_CAMPAIGN_ID,
                        parameters=CAMPAIGN_PARAMETERS,
                        status=sql.CampaignStatus.SUSPENDED,
                    ),
                ),
                pytest.mark.banners(
                    sql.Banner(
                        id=1,
                        place_id=1,
                        inner_campaign_id=INNER_CAMPAIGN_ID,
                        status=sql.BannerStatus.IN_PROCESS,
                    ),
                ),
            ),
            id='do not pause not active banners',
        ),
        pytest.param(
            [INNER_CAMPAIGN_ID],
            [
                sql.Banner(
                    id=1,
                    place_id=1,
                    inner_campaign_id=INNER_CAMPAIGN_ID,
                    status=sql.BannerStatus.ACTIVE,
                ),
            ],
            [
                sql.Campaign(
                    id=INNER_CAMPAIGN_ID,
                    parameters=CAMPAIGN_PARAMETERS,
                    status=sql.CampaignStatus.ACTIVE,
                ),
            ],
            0,
            marks=(
                pytest.mark.campaigns(
                    sql.Campaign(
                        id=INNER_CAMPAIGN_ID,
                        parameters=CAMPAIGN_PARAMETERS,
                        status=sql.CampaignStatus.ACTIVE,
                    ),
                ),
                pytest.mark.banners(
                    sql.Banner(
                        id=1,
                        place_id=1,
                        inner_campaign_id=INNER_CAMPAIGN_ID,
                        status=sql.BannerStatus.ACTIVE,
                    ),
                ),
            ),
            id='do not pause campaigns with no feeds admin id',
        ),
        pytest.param(
            [INNER_CAMPAIGN_ID],
            [
                sql.Banner(
                    id=1,
                    place_id=1,
                    inner_campaign_id=INNER_CAMPAIGN_ID,
                    status=sql.BannerStatus.STOPPED,
                    feeds_admin_id='1',
                ),
            ],
            [
                sql.Campaign(
                    id=INNER_CAMPAIGN_ID,
                    parameters=CAMPAIGN_PARAMETERS,
                    status=sql.CampaignStatus.SUSPENDED,
                ),
            ],
            1,
            marks=(
                pytest.mark.campaigns(
                    sql.Campaign(
                        id=INNER_CAMPAIGN_ID,
                        parameters=CAMPAIGN_PARAMETERS,
                        status=sql.CampaignStatus.ACTIVE,
                    ),
                ),
                pytest.mark.banners(
                    sql.Banner(
                        id=1,
                        place_id=1,
                        inner_campaign_id=INNER_CAMPAIGN_ID,
                        status=sql.BannerStatus.ACTIVE,
                        feeds_admin_id='1',
                    ),
                ),
            ),
            id='successfully pause cpm campaign',
        ),
        pytest.param(
            [INNER_CAMPAIGN_ID],
            [
                sql.Banner(
                    id=1,
                    place_id=1,
                    inner_campaign_id=INNER_CAMPAIGN_ID,
                    status=sql.BannerStatus.ACTIVE,
                    feeds_admin_id='1',
                ),
            ],
            [
                sql.Campaign(
                    id=INNER_CAMPAIGN_ID,
                    parameters=CAMPAIGN_PARAMETERS,
                    status=sql.CampaignStatus.UPDATING,
                ),
            ],
            0,
            marks=(
                pytest.mark.campaigns(
                    sql.Campaign(
                        id=INNER_CAMPAIGN_ID,
                        parameters=CAMPAIGN_PARAMETERS,
                        status=sql.CampaignStatus.UPDATING,
                    ),
                ),
                pytest.mark.banners(
                    sql.Banner(
                        id=1,
                        place_id=1,
                        inner_campaign_id=INNER_CAMPAIGN_ID,
                        status=sql.BannerStatus.ACTIVE,
                        feeds_admin_id='1',
                    ),
                ),
            ),
            id='pause updating cpm campaign',
        ),
    ],
)
async def test_pause_cpm(
        pause_handler,
        start_handler,
        eats_restapp_marketing_db,
        mock_auth_partner,
        mock_feeds_admin,
        campaign_ids: typing.List[str],
        banners: typing.List[sql.Banner],
        campaigns: typing.List[sql.Campaign],
        feeds_calls: int,
):
    request_campaigns = [
        SuspendableCampaign(campaign_id, CampaignType.CPM)
        for campaign_id in campaign_ids
    ]
    response = await pause_handler(Request(request_campaigns))
    assert response.status_code == 204
    assert mock_feeds_admin.unpublish_banner_times_called == feeds_calls

    actual_banners = sql.get_all_banners(eats_restapp_marketing_db)
    assert banners == actual_banners

    actual_campaigns = sql.get_all_campaigns(eats_restapp_marketing_db)
    assert campaigns == actual_campaigns


@pytest.mark.parametrize(
    'campaign_ids, banners, campaigns, feeds_calls',
    [
        pytest.param([], [], [], 0, id='No campaigns in request'),
        pytest.param(['1', '2'], [], [], 0, id='No campaigns found'),
        pytest.param(
            [INNER_CAMPAIGN_ID],
            [
                sql.Banner(
                    id=1,
                    place_id=1,
                    inner_campaign_id=INNER_CAMPAIGN_ID,
                    status=sql.BannerStatus.ACTIVE,
                ),
            ],
            [
                sql.Campaign(
                    id=INNER_CAMPAIGN_ID,
                    parameters=CAMPAIGN_PARAMETERS,
                    status=sql.CampaignStatus.ACTIVE,
                ),
            ],
            0,
            marks=(
                pytest.mark.campaigns(
                    sql.Campaign(
                        id=INNER_CAMPAIGN_ID,
                        parameters=CAMPAIGN_PARAMETERS,
                        status=sql.CampaignStatus.ACTIVE,
                    ),
                ),
                pytest.mark.banners(
                    sql.Banner(
                        id=1,
                        place_id=1,
                        inner_campaign_id=INNER_CAMPAIGN_ID,
                        status=sql.BannerStatus.ACTIVE,
                    ),
                ),
            ),
            id='Do not start active banners',
        ),
        pytest.param(
            [INNER_CAMPAIGN_ID],
            [
                sql.Banner(
                    id=1,
                    place_id=1,
                    inner_campaign_id=INNER_CAMPAIGN_ID,
                    status=sql.BannerStatus.ACTIVE,
                    feeds_admin_id='1',
                ),
            ],
            [
                sql.Campaign(
                    id=INNER_CAMPAIGN_ID,
                    parameters=CAMPAIGN_PARAMETERS,
                    status=sql.CampaignStatus.ACTIVE,
                ),
            ],
            1,
            marks=(
                pytest.mark.campaigns(
                    sql.Campaign(
                        id=INNER_CAMPAIGN_ID,
                        parameters=CAMPAIGN_PARAMETERS,
                        status=sql.CampaignStatus.SUSPENDED,
                    ),
                ),
                pytest.mark.banners(
                    sql.Banner(
                        id=1,
                        place_id=1,
                        inner_campaign_id=INNER_CAMPAIGN_ID,
                        status=sql.BannerStatus.STOPPED,
                        feeds_admin_id='1',
                    ),
                ),
            ),
            id='Successfully start cpm campaign',
        ),
        pytest.param(
            [INNER_CAMPAIGN_ID],
            [
                sql.Banner(
                    id=1,
                    place_id=1,
                    inner_campaign_id=INNER_CAMPAIGN_ID,
                    status=sql.BannerStatus.STOPPED,
                    feeds_admin_id='1',
                ),
            ],
            [
                sql.Campaign(
                    id=INNER_CAMPAIGN_ID,
                    parameters=CAMPAIGN_PARAMETERS,
                    status=sql.CampaignStatus.UPDATING,
                ),
            ],
            0,
            marks=(
                pytest.mark.campaigns(
                    sql.Campaign(
                        id=INNER_CAMPAIGN_ID,
                        parameters=CAMPAIGN_PARAMETERS,
                        status=sql.CampaignStatus.UPDATING,
                    ),
                ),
                pytest.mark.banners(
                    sql.Banner(
                        id=1,
                        place_id=1,
                        inner_campaign_id=INNER_CAMPAIGN_ID,
                        status=sql.BannerStatus.STOPPED,
                        feeds_admin_id='1',
                    ),
                ),
            ),
            id='start updating cpm campaign',
        ),
    ],
)
async def test_start_cpm(
        start_handler,
        eats_restapp_marketing_db,
        mock_auth_partner,
        mock_feeds_admin,
        campaign_ids: typing.List[str],
        banners: typing.List[sql.Banner],
        campaigns: typing.List[sql.Campaign],
        feeds_calls: int,
):
    request_campaigns = [
        SuspendableCampaign(campaign_id, CampaignType.CPM)
        for campaign_id in campaign_ids
    ]

    response = await start_handler(Request(request_campaigns))
    assert response.status_code == 204
    assert mock_feeds_admin.publish_banner_times_called == feeds_calls

    actual_banners = sql.get_all_banners(eats_restapp_marketing_db)
    assert banners == actual_banners

    actual_campaigns = sql.get_all_campaigns(eats_restapp_marketing_db)
    assert campaigns == actual_campaigns


@pytest.mark.parametrize(
    'campaign_ids, adverts',
    [
        pytest.param([], [], id='no campaigns in request'),
        pytest.param(['1', '2'], [], id='no campaigns found'),
        pytest.param(
            ['1'],
            [
                sql.Advert(
                    id=1,
                    place_id=1,
                    average_cpc=10,
                    campaign_id=1,
                    is_active=False,
                    status=sql.AdvertStatus.PAUSED,
                ),
            ],
            marks=(
                pytest.mark.adverts(
                    sql.Advert(
                        id=1,
                        place_id=1,
                        average_cpc=10,
                        campaign_id=1,
                        is_active=False,
                        status=sql.AdvertStatus.PAUSED,
                    ),
                ),
            ),
            id='do not pause paused advert',
        ),
        pytest.param(
            ['1'],
            [
                sql.Advert(
                    id=1,
                    place_id=1,
                    average_cpc=10,
                    campaign_id=1,
                    is_active=False,
                    status=sql.AdvertStatus.PAUSED,
                ),
            ],
            marks=(
                pytest.mark.campaigns(
                    sql.Campaign(
                        id=INNER_CAMPAIGN_ID, status=sql.CampaignStatus.ACTIVE,
                    ),
                ),
                pytest.mark.adverts(
                    sql.Advert(
                        id=1,
                        place_id=1,
                        average_cpc=10,
                        campaign_id=1,
                        is_active=True,
                        status=sql.AdvertStatus.STARTED,
                    ),
                ),
            ),
            id='pause active campaign',
        ),
    ],
)
async def test_pause_cpc(
        pause_handler,
        start_handler,
        eats_restapp_marketing_db,
        mock_auth_partner,
        campaign_ids: typing.List[str],
        adverts: typing.List[sql.Advert],
):
    campaigns = [
        SuspendableCampaign(campaign_id, CampaignType.CPC)
        for campaign_id in campaign_ids
    ]
    response = await pause_handler(Request(campaigns))
    assert response.status_code == 204

    actual_adverts = sql.get_all_adverts(eats_restapp_marketing_db)
    assert adverts == actual_adverts


@pytest.mark.parametrize(
    'campaign_ids, adverts',
    [
        pytest.param([], [], id='No campaigns in request'),
        pytest.param(['1', '2'], [], id='No campaigns found'),
        pytest.param(
            ['2'],
            [
                sql.Advert(
                    id=1,
                    place_id=1,
                    average_cpc=10,
                    campaign_id=1,
                    is_active=False,
                    status=sql.AdvertStatus.PAUSED,
                ),
            ],
            marks=(
                pytest.mark.adverts(
                    sql.Advert(
                        id=1,
                        place_id=1,
                        average_cpc=10,
                        campaign_id=1,
                        is_active=False,
                        status=sql.AdvertStatus.PAUSED,
                    ),
                ),
            ),
            id='Do not start another advert',
        ),
        pytest.param(
            ['1'],
            [
                sql.Advert(
                    id=1,
                    place_id=1,
                    average_cpc=10,
                    campaign_id=1,
                    is_active=True,
                    status=sql.AdvertStatus.STARTED,
                ),
            ],
            marks=(
                pytest.mark.campaigns(
                    sql.Campaign(
                        id='1',
                        parameters=CAMPAIGN_PARAMETERS,
                        status=sql.CampaignStatus.SUSPENDED,
                    ),
                ),
                pytest.mark.adverts(
                    sql.Advert(
                        id=1,
                        place_id=1,
                        average_cpc=10,
                        campaign_id=1,
                        is_active=True,
                        status=sql.AdvertStatus.PAUSED,
                    ),
                ),
            ),
            id='Start pause campaign',
        ),
    ],
)
async def test_stast_cpc(
        start_handler,
        eats_restapp_marketing_db,
        mock_auth_partner,
        campaign_ids: typing.List[str],
        adverts: typing.List[sql.Advert],
):
    campaigns = [
        SuspendableCampaign(campaign_id, CampaignType.CPC)
        for campaign_id in campaign_ids
    ]

    response = await start_handler(Request(campaigns))
    assert response.status_code == 204

    actual_adverts = sql.get_all_adverts(eats_restapp_marketing_db)
    assert adverts == actual_adverts


@pytest.mark.parametrize(
    'campaign_ids',
    [
        pytest.param(
            [INNER_CAMPAIGN_ID],
            marks=(
                pytest.mark.campaigns(
                    sql.Campaign(
                        id=INNER_CAMPAIGN_ID,
                        parameters=CAMPAIGN_PARAMETERS,
                        status=sql.CampaignStatus.ACTIVE,
                    ),
                ),
                pytest.mark.adverts(
                    sql.Advert(
                        id=1,
                        place_id=1,
                        average_cpc=10,
                        campaign_id=1,
                        is_active=True,
                        status=sql.AdvertStatus.STARTED,
                    ),
                ),
            ),
            id='Bad request',
        ),
    ],
)
async def test_bad_auth_request(
        pause_handler,
        mock_auth_partner_bad_request,
        campaign_ids: typing.List[str],
):
    campaigns = [
        SuspendableCampaign(campaign_id, CampaignType.CPC)
        for campaign_id in campaign_ids
    ]
    response = await pause_handler(Request(campaigns))
    assert response.status_code == 400


@pytest.mark.parametrize(
    'campaign_ids',
    [
        pytest.param(
            [INNER_CAMPAIGN_ID],
            marks=(
                pytest.mark.campaigns(
                    sql.Campaign(
                        id=INNER_CAMPAIGN_ID,
                        parameters=CAMPAIGN_PARAMETERS,
                        status=sql.CampaignStatus.ACTIVE,
                    ),
                ),
                pytest.mark.adverts(
                    sql.Advert(
                        id=1,
                        place_id=1,
                        average_cpc=10,
                        campaign_id=1,
                        is_active=True,
                        status=sql.AdvertStatus.STARTED,
                    ),
                ),
            ),
            id='Forbidden access',
        ),
    ],
)
async def test_forbidden_access(
        pause_handler,
        mock_auth_partner_not_manager,
        campaign_ids: typing.List[str],
):
    campaigns = [
        SuspendableCampaign(campaign_id, CampaignType.CPC)
        for campaign_id in campaign_ids
    ]
    response = await pause_handler(Request(campaigns))
    assert response.status_code == 403
