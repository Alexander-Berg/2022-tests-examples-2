import dataclasses
import datetime
import enum
import typing
import uuid

from dateutil import parser
import pytest
import pytz

from testsuite.utils import matching

from tests_eats_restapp_marketing import experiments
from tests_eats_restapp_marketing import sql

PASSPORT_ID = 1229582676


class BudgetAllocation(str, enum.Enum):
    ALL_PERIOD = 'all_period'
    WEEKLY = 'weekly'


@dataclasses.dataclass
class RequestBanner:
    image: str
    source_image: str
    text: str

    def asdict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class Request:
    place_ids: typing.List[int]
    averagecpm: float
    spend_limit: float
    budget_allocation: BudgetAllocation = BudgetAllocation.WEEKLY
    image: typing.Optional[str] = None
    banner: typing.Optional[RequestBanner] = None
    start_date: datetime.datetime = datetime.datetime.now(
        datetime.timezone.utc,
    )
    finish_date: datetime.datetime = (
        datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(days=30)
    )

    def asdict(self) -> dict:
        banner = self.banner.asdict() if self.banner is not None else None
        return {
            'place_ids': self.place_ids,
            'averagecpm': self.averagecpm,
            'spend_limit': self.spend_limit,
            'budget_allocation': self.budget_allocation,
            'image': self.image,
            'start_date': self.start_date.isoformat(),
            'finish_date': self.finish_date.isoformat(),
            'banner': banner,
        }


@pytest.fixture(name='cpm_create_bulk')
def _cpm_create_bulk(taxi_eats_restapp_marketing):
    """
    Фикстура для запросов в ручку
    `/4.0/restapp-front/marketing/v1/ad/cpm/create-bulk`
    """

    url = '/4.0/restapp-front/marketing/v1/ad/cpm/create-bulk'

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


async def test_create_bulk(
        cpm_create_bulk,
        eats_restapp_marketing_db,
        mock_blackbox_tokeninfo,
        mock_auth_partner,
        mock_authorizer_allowed,
        mock_feeds_admin,
):
    start_date = parser.parse('2022-05-04T12:00:00+03:00')
    finish_date = parser.parse('2022-06-04T12:00:00+03:00')

    response = await cpm_create_bulk(
        Request(
            place_ids=[1, 2],
            averagecpm=2,
            spend_limit=100,
            image='data:image/jpeg;base64,cXFxcXdxZXJxZXJxZXI=',
            start_date=start_date,
            finish_date=finish_date,
        ),
    )
    assert response.status_code == 201
    assert mock_feeds_admin.upload_banner_times_called == 1

    campaigns = response.json()['campaigns']
    campaigns = sorted(campaigns, key=lambda d: d['place_id'])
    assert campaigns == [
        {
            'advert_id': 1,
            'cpm_advert_id': matching.any_string,
            'has_access': True,
            'is_rating_status_ok': True,
            'place_id': 1,
            'status': 'process',
        },
        {
            'advert_id': 2,
            'cpm_advert_id': matching.any_string,
            'has_access': True,
            'is_rating_status_ok': True,
            'place_id': 2,
            'status': 'process',
        },
    ]

    campaigns = sql.get_all_campaigns(eats_restapp_marketing_db)
    assert campaigns == [
        sql.Campaign(
            id=matching.any_string,
            campaign_type=sql.CampaignType.CPM_BANNER_CAMPAIGN,
            passport_id=1229582676,
            parameters={
                'averagecpm': 2,
                'spend_limit': 100,
                'strategy_type': 'kWbMaximumImpressions',
                'start_date': start_date.astimezone(pytz.UTC).isoformat(),
                'finish_date': finish_date.astimezone(pytz.UTC).isoformat(),
            },
        ),
    ]

    banners = sql.get_all_banners(eats_restapp_marketing_db)
    assert banners == [
        sql.Banner(
            id=1,
            inner_campaign_id=campaigns[0].id,
            place_id=1,
            image=matching.any_string,
        ),
        sql.Banner(
            id=2,
            inner_campaign_id=campaigns[0].id,
            place_id=2,
            image=matching.any_string,
        ),
    ]


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_ADVERT_BULK_CREATE={'max_bulk_create_count': 3},
)
async def test_many_places(
        cpm_create_bulk, mock_authorizer_allowed, mock_feeds_admin,
):

    response = await cpm_create_bulk(
        Request(
            place_ids=[1, 2, 3, 4],
            averagecpm=2,
            spend_limit=100,
            image='data:image/jpeg;base64,cXFxcXdxZXJxZXJxZXI=',
        ),
    )
    assert mock_feeds_admin.upload_banner_times_called == 0
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'many campaigns. Limit is 3',
        'details': {'error_slug': 'MANY_CAMPAIGNS', 'max_campaigns_count': 3},
    }


async def test_cpm_create_bulk_create_no_dublicates_on_request(
        cpm_create_bulk,
        eats_restapp_marketing_db,
        mock_blackbox_tokeninfo,
        mock_auth_partner,
        mock_authorizer_allowed,
        mock_feeds_admin,
):
    """
    EDACAT-2791: проверяем, что невозможно создать больше одной CPM-кампании
    для одного ресторана.
    """

    place_ids = [1, 1]
    expected_banner = sql.Banner(
        id=1,
        place_id=1,
        inner_campaign_id=matching.any_string,
        image=matching.any_string,
    )

    response = await cpm_create_bulk(
        Request(
            place_ids=place_ids,
            averagecpm=10,
            spend_limit=100,
            image='data:image/jpeg;base64,cXFxcXdxZXJxZXJxZXI=',
        ),
    )
    assert response.status_code == 201

    actual_banners = sql.get_all_banners(eats_restapp_marketing_db)
    assert len(actual_banners) == 1
    assert expected_banner == actual_banners[0]


async def test_cpm_create_bulk_create_no_dublicates_if_any_exists(
        cpm_create_bulk,
        eats_restapp_marketing_db,
        mock_blackbox_tokeninfo,
        mock_auth_partner,
        mock_authorizer_allowed,
        mock_feeds_admin,
):
    """
    EDACAT-2791: проверяем, что невозможно создать больше одной CPM-кампании
    для одного ресторана, если для РК уже заведен баннер, а также, что не для
    таких банннеров, несоздаются кампании.
    """

    campaign = sql.Campaign(
        id=str(uuid.uuid4()),
        campaign_type=sql.CampaignType.CPM_BANNER_CAMPAIGN,
        passport_id=1229582676,
        parameters={
            'averagecpm': 2,
            'spend_limit': 100,
            'strategy_type': 'kWbMaximumImpressions',
        },
    )
    campaign.id = sql.insert_campaign(eats_restapp_marketing_db, campaign)

    banner = sql.Banner(
        id=1, place_id=1, inner_campaign_id=campaign.id, image='testsuite',
    )
    banner.id = sql.insert_banner(eats_restapp_marketing_db, banner)

    place_ids = [1]
    response = await cpm_create_bulk(
        Request(
            place_ids=place_ids,
            averagecpm=10,
            spend_limit=100,
            image='data:image/jpeg;base64,cXFxcXdxZXJxZXJxZXI=',
        ),
    )
    assert response.status_code == 201

    banners = sql.get_all_banners(eats_restapp_marketing_db)
    assert banners == [banner]

    campaigns = sql.get_all_campaigns(eats_restapp_marketing_db)
    assert campaigns == [campaign]


@pytest.mark.parametrize(
    'cpm_request, status_code',
    [
        pytest.param(
            Request(
                place_ids=[1],
                averagecpm=2,
                spend_limit=100,
                image='data:image/jpeg;base64,cXFxcXdxZXJxZXJxZXI=',
                start_date=parser.parse('2022-05-04T12:00:00+03:00'),
                finish_date=parser.parse('2021-05-04T12:00:00+03:00'),
            ),
            400,
            id='start date is bigger than finish date',
        ),
        pytest.param(
            Request(
                place_ids=[1],
                averagecpm=2,
                spend_limit=100,
                image='data:image/jpeg;base64,cXFxcXdxZXJxZXJxZXI=',
                start_date=parser.parse('2022-05-04T12:00:00+03:00'),
                finish_date=parser.parse('2022-06-04T12:00:00+03:00'),
            ),
            400,
            marks=(
                experiments.cpm_create_bulk_settings(
                    min_average_cpm=10,
                    min_spend_limit=50,
                    min_spend_wb=50,
                    min_spend_cp=9300,
                ),
            ),
            id='average cpm is less than config',
        ),
        pytest.param(
            Request(
                place_ids=[1],
                averagecpm=20,
                spend_limit=100,
                image='data:image/jpeg;base64,cXFxcXdxZXJxZXJxZXI=',
                start_date=parser.parse('2022-05-04T12:00:00+03:00'),
                finish_date=parser.parse('2022-06-04T12:00:00+03:00'),
            ),
            400,
            marks=(
                experiments.cpm_create_bulk_settings(
                    min_average_cpm=10,
                    min_spend_limit=500,
                    min_spend_wb=500,
                    min_spend_cp=9300,
                ),
            ),
            id='spend limit is less than config',
        ),
        pytest.param(
            Request(
                place_ids=[1],
                averagecpm=20,
                spend_limit=1000,
                image='data:image/jpeg;base64,cXFxcXdxZXJxZXJxZXI=',
                start_date=parser.parse('2022-05-04T12:00:00+03:00'),
                finish_date=parser.parse('2022-06-04T12:00:00+03:00'),
            ),
            201,
            marks=(
                experiments.cpm_create_bulk_settings(
                    min_average_cpm=10,
                    min_spend_limit=500,
                    min_spend_wb=500,
                    min_spend_cp=9300,
                ),
            ),
            id='all ok',
        ),
        pytest.param(
            Request(
                place_ids=[1],
                averagecpm=20,
                spend_limit=1000,
                budget_allocation=BudgetAllocation.ALL_PERIOD,
                image='data:image/jpeg;base64,cXFxcXdxZXJxZXJxZXI=',
                start_date=parser.parse('2022-05-04T12:00:00+03:00'),
                finish_date=parser.parse('2022-06-04T12:00:00+03:00'),
            ),
            400,
            marks=(
                experiments.cpm_create_bulk_settings(
                    min_average_cpm=10,
                    min_spend_limit=500,
                    min_spend_wb=500,
                    min_spend_cp=9300,
                ),
            ),
            id='cp limit is less then config',
        ),
        pytest.param(
            Request(
                place_ids=[1],
                averagecpm=20,
                spend_limit=9300,
                budget_allocation=BudgetAllocation.ALL_PERIOD,
                image='data:image/jpeg;base64,cXFxcXdxZXJxZXJxZXI=',
                start_date=parser.parse('2022-05-04T12:00:00+03:00'),
                finish_date=parser.parse('2022-06-04T12:00:00+03:00'),
            ),
            201,
            marks=(
                experiments.cpm_create_bulk_settings(
                    min_average_cpm=10,
                    min_spend_limit=500,
                    min_spend_wb=500,
                    min_spend_cp=9300,
                ),
            ),
            id='cp limit is ok',
        ),
    ],
)
async def test_cpm_create_bulk_create_validation(
        cpm_create_bulk,
        eats_restapp_marketing_db,
        mock_blackbox_tokeninfo,
        mock_auth_partner,
        mock_authorizer_allowed,
        mock_feeds_admin,
        cpm_request,
        status_code,
):
    """
    EDACAT-2797: тест проверяет валидацию ручки создания cpm-баннеров.
    """

    response = await cpm_create_bulk(cpm_request)
    assert response.status_code == status_code


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_UPLOAD_BANNERS_SETTINGS={
        'front_image_prefix': 'data;',  # deprecated
        'max_image_size': 10,
    },
)
@pytest.mark.parametrize(
    'image, banner, status_code',
    [
        pytest.param(None, None, 400, id='no images'),
        pytest.param(
            'data:image/jpeg;base64,bG9ydW0gaXBzdW1lIGhlbGxvIHdvcmxkIGZvby'
            'BiYXIgY3BwIGlzIGdvb2QgZm9yIHlvdXIgaGVhbHRo',
            None,
            400,
            id='image size too big',
        ),
        pytest.param(
            None,
            RequestBanner(
                image=(
                    'data:image/jpeg;base64,bG9ydW0gaXBzdW1lIGhlbGxvI'
                    'HdvcmxkIGZvbyBiYXIgY3BwIGlzIGdvb2QgZm9yIHlvdXIgaGVhbHRo'
                ),
                source_image='data:image/jpeg;base64,Zm9v',
                text='testsuite',
            ),
            400,
            id='banner image size too big',
        ),
        pytest.param(
            None,
            RequestBanner(
                image='Zm9v',
                source_image=(
                    'data:image/jpeg;base64,bG9ydW0gaXBzdW1lIGhlbGxvI'
                    'HdvcmxkIGZvbyBiYXIgY3BwIGlzIGdvb2QgZm9yIHlvdXIgaGVhbHRo'
                ),
                text='testsuite',
            ),
            400,
            id='banner orig image size too big',
        ),
        pytest.param(
            None,
            RequestBanner(
                image='data:image/jpeg;base64,aGVsbG8=',
                source_image='data:image/jpeg;base64,aGVsbG8=',
                text='testsuite',
            ),
            201,
            id='all good',
        ),
    ],
)
async def test_cpm_create_bulk_validate_image_size(
        cpm_create_bulk,
        mock_blackbox_tokeninfo,
        mock_auth_partner,
        mock_authorizer_allowed,
        mock_feeds_admin,
        image: typing.Optional[str],
        banner: typing.Optional[RequestBanner],
        status_code: int,
):
    request = Request(
        place_ids=[1],
        averagecpm=20,
        spend_limit=1000,
        image=image,
        banner=banner,
        start_date=parser.parse('2022-05-04T12:00:00+03:00'),
        finish_date=parser.parse('2022-06-04T12:00:00+03:00'),
    )
    response = await cpm_create_bulk(request)
    assert response.status_code == status_code


@pytest.mark.now('2022-06-20T12:00:00')
@pytest.mark.config(
    EATS_RESTAPP_MARKETING_UPLOAD_BANNERS_SETTINGS={
        'front_image_prefix': 'data:image/jpeg;base64,',
        'max_image_size': 10,
    },
)
async def test_cpm_create_bulk_upload_multiple_images(
        cpm_create_bulk,
        eats_restapp_marketing_db,
        mock_blackbox_tokeninfo,
        mock_auth_partner,
        mock_authorizer_allowed,
        mock_feeds_admin,
):
    place_ids = [1]
    request_banner = RequestBanner(
        image='data:image/jpeg;base64,aGVsbG8=',
        source_image='data:image/jpeg;base64,aGVsbG8=',
        text='testsuite text',
    )

    request = Request(
        place_ids=place_ids,
        averagecpm=20,
        spend_limit=1000,
        banner=request_banner,
        start_date=parser.parse('2022-06-20T12:00:00+00:00'),
        finish_date=parser.parse('2022-08-20T12:00:00+00:00'),
    )

    response = await cpm_create_bulk(request)
    assert response.status_code == 201
    assert mock_feeds_admin.upload_banner_times_called == 2

    campaigns = sql.get_all_campaigns(eats_restapp_marketing_db)
    assert campaigns

    banners = sql.get_all_banners(eats_restapp_marketing_db)
    assert len(banners) == len(place_ids)

    banner = banners.pop(0)
    assert banner.image == matching.any_string
    assert banner.original_image_id == matching.any_string
    assert banner.image_text == request_banner.text


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_UPLOAD_BANNERS_SETTINGS={
        'front_image_prefix': 'data:image/jpeg;base64,',
        'max_image_size': 10000,
    },
)
async def test_cpm_create_bulk_feeds_admin_500(
        cpm_create_bulk,
        eats_restapp_marketing_db,
        mock_blackbox_tokeninfo,
        mock_auth_partner,
        mock_authorizer_allowed,
        mock_feeds_admin,
):

    mock_feeds_admin.set_status_code(500)

    request_banner = RequestBanner(
        image='data:image/jpeg;base64,aGVsbG8=',
        source_image='data:image/jpeg;base64,aGVsbG8=',
        text='testsuite text',
    )

    request = Request(
        place_ids=[1],
        averagecpm=20,
        spend_limit=1000,
        banner=request_banner,
        start_date=parser.parse('2022-06-20T12:00:00+00:00'),
        finish_date=parser.parse('2022-08-20T12:00:00+00:00'),
    )

    response = await cpm_create_bulk(request)
    assert response.status_code == 500
    assert mock_feeds_admin.upload_banner_times_called >= 1

    campaigns = sql.get_all_campaigns(eats_restapp_marketing_db)
    assert not campaigns

    banners = sql.get_all_banners(eats_restapp_marketing_db)
    assert not banners


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_UPLOAD_BANNERS_SETTINGS={
        'front_image_prefix': 'data:image/jpeg;base64,',
        'max_image_size': 10000,
    },
)
async def test_cpm_create_bulk_403(
        cpm_create_bulk,
        eats_restapp_marketing_db,
        mock_blackbox_tokeninfo,
        mock_auth_partner_not_manager,
        mock_authorizer_forbidden,
        mock_feeds_admin,
):

    mock_feeds_admin.set_status_code(500)

    request_banner = RequestBanner(
        image='data:image/jpeg;base64,aGVsbG8=',
        source_image='data:image/jpeg;base64,aGVsbG8=',
        text='testsuite text',
    )

    request = Request(
        place_ids=[1],
        averagecpm=20,
        spend_limit=1000,
        banner=request_banner,
        start_date=parser.parse('2022-06-20T12:00:00+00:00'),
        finish_date=parser.parse('2022-08-20T12:00:00+00:00'),
    )

    response = await cpm_create_bulk(request)
    assert response.status_code == 403
