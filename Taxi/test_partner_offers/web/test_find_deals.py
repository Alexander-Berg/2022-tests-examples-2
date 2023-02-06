# pylint: disable=unused-variable
import datetime

import aiohttp
import pytest

from partner_offers import models
from partner_offers.db_access import for_consumers as db_access
from partner_offers.generated.service.swagger.models import api


EXPECTED_RESPONSE = api.ConsumersDealsData(
    calculated_at=datetime.datetime.fromisoformat('2019-06-07T12:15+03:00'),
    categories=[
        api.CategoryForConsumer(
            icon_url='https://example.com/im.png',
            icon_url_night='https://example.com/im.png',
            id='food',
            name='Еда',
            pins_limit=15,
            rebate='15%',
        ),
    ],
    deals=[
        api.DealForConsumer(
            id='11',
            category_id='food',
            locations=['11'],
            title='Some title',
            subtitle='Test',
            description=api.DealForConsumer.Description(
                title='Some desc title',
                text='Str',
                icon_url='http://htllo/ert.im',
            ),
            type='discount',
            terms=api.ConsumerTermsDiscount(text='Hello', percent='15%'),
        ),
    ],
    locations=[
        api.LocationForConsumer(
            id='11',
            name='Грибница1',
            icon_url='https://example.com/image.jpg',
            geo=api.LocationForConsumer.Geo(latitude=55.0, longitude=37.5),
            address='Any address, actually',
            is_open=True,
            is_open_changes_at=[
                '2020-01-10T13:21:21.455966+01:00',
                '2020-01-10T18:21:42.402768+02:10',
            ],
            categories=[
                api.LocationForConsumer.CategoriesItem(
                    category_id='food', rebate='15%',
                ),
            ],
        ),
    ],
    polling_delay_seconds=1800,
)


EXPECTED_RETRIEVE_ALL_RESPONSES = [
    [
        {
            'feed_id': 'feeeed',
            'feeds_admin_id': '01234567890123456789012345678901',
            'title': 'Mcdonalds (hopefully)',
            'category_ids': ['tire', 'food'],
            'price': '4',
        },
    ],
    [
        {
            'feed_id': 'feeeed',
            'feeds_admin_id': '01234567890123456789012345678901',
            'title': 'Mcdonalds (hopefully)',
            'category_ids': ['tire', 'food'],
            'price': '4',
        },
        {
            'feed_id': 'feeeed',
            'feeds_admin_id': '01234567890123456789012345678xxx',
            'title': 'Mcdonalds (hopefully)',
            'subtitle': 'Big mac',
            'description': 'Test full data',
            'category_ids': ['washing', 'food'],
        },
    ],
    [],
]

EXPECTED_RETRIEVE_ALL_CATEGORIES = [
    [
        {
            'id': 'tire',
            'name': 'tire',
            'priority': 0,
            'icon_url': '<pin_icon>',
            'icon_url_night': '<night_pin_icon>',
        },
        {
            'id': 'food',
            'name': 'food',
            'priority': 1,
            'icon_url': '<pin_icon>',
            'icon_url_night': '<night_pin_icon>',
        },
    ],
    [
        {
            'id': 'tire',
            'name': 'tire',
            'priority': 1,
            'icon_url': '<pin_icon>',
            'icon_url_night': '<night_pin_icon>',
        },
        {
            'id': 'washing',
            'name': 'washing',
            'priority': 0,
            'icon_url': '<pin_icon>',
            'icon_url_night': '<night_pin_icon>',
        },
        {
            'id': 'food',
            'name': 'food',
            'priority': 2,
            'icon_url': '<pin_icon>',
            'icon_url_night': '<night_pin_icon>',
        },
    ],
    [],
]


EXPECTED_DEALS_ITEMS = [
    {
        'category_id': 'food',
        'description': {'title': 'some'},
        'id': '1',
        'locations': ['101'],
        'terms': {'new_price': '4₽', 'old_price': '5₽'},
        'title': 'First',
        'type': 'fix_price',
    },
    {
        'category_id': 'food',
        'description': {'title': 'some'},
        'id': '2',
        'locations': ['101'],
        'terms': {'text': 'Hee', 'price': '5₽'},
        'title': 'Second',
        'type': 'coupon',
    },
    {
        'category_id': 'food',
        'description': {'title': 'some'},
        'id': '3',
        'locations': ['101'],
        'terms': {'text': 'Some', 'percent': '10%'},
        'title': 'Third',
        'type': 'discount',
    },
]


TRANSLATIONS = {
    'Food': {'ru': 'Еда', 'en': 'Food'},
    'Service': {'ru': 'Сервис'},
    'Help': {'ru': 'Помощь'},
    'VAT': {'ru': 'Ват'},
}

CATEGORIES_DATA = [
    {
        'category': 'food',
        'name': 'Food',
        'icon_url': 'https://example.com/im.png',
        'icon_url_night': 'https://example.com/im.png',
        'pins_limit': 15,
    },
    {
        'category': 'service',
        'name': 'Service',
        'icon_url': 'https://example.com/im.png',
        'icon_url_night': 'https://example.com/im.png',
        'pins_limit': 5,
    },
    {
        'category': 'help',
        'name': 'Help',
        'icon_url': 'https://example.com/im.png',
        'icon_url_night': 'https://example.com/im.png',
        'pins_limit': 15,
    },
    {
        'category': 'vat',
        'name': 'VAT',
        'icon_url': 'https://example.com/im.png',
        'icon_url_night': 'https://example.com/im.png',
        'pins_limit': 15,
    },
]

WORK_TIME_CONF = {
    'must_open_in_near_minutes': 30,
    'how_long_schedule_to_send_minutes': 24 * 60,
}

DRIVER_REQUEST_HEADERS = {
    'X-Request-Application-Version': '9.10',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'X-YaTaxi-Park-Id': 'some',
    'X-YaTaxi-Driver-Profile-Id': 'driver',
    'User-Agent': 'Taximeter 9.10',
    'Accept-Language': 'ru-RU',
}


@pytest.fixture(name='mock_contractor_merch_client')
def _mock_contractor_merch_client(mockserver):
    @mockserver.json_handler(
        '/contractor-merch/internal/contractor-merch/v1/offers/retrieve-all',
    )
    def _retrieve_all(request):
        return context.retrieve_all_response

    class Context:
        def __init__(self):
            self.retrieve_all = _retrieve_all
            self.retrieve_all_response = {'feeds': {}, 'categories': {}}

        def set_retrieve_all_response(self, response):
            self.retrieve_all_response = response

    context = Context()

    return context


@pytest.mark.client_experiments3(
    consumer='partner-offers/v1_driver_deals_available',
    config_name='partner_offers_validate_taximeter_version',
    file_args='configs3/validate_taximeter_version_default_args.json',
    value={'enabled': True},
)
@pytest.mark.config(CONTRACTOR_MERCH_OFFERS_ENABLED=True)
async def test_find_deals_ok(
        patch, web_app_client, mock_contractor_merch_client,
):
    @patch(
        'taxi.clients.driver_tags.DriverTagsClient.v1_drivers_match_profile',
    )
    async def mock_driver_tags_drivers_match(
            park_id, driver_uuid, *args, **kwargs,
    ):
        assert park_id == 'some'
        assert driver_uuid == 'driver'

        class ResponseObj:
            async def json(self):
                return {'tags': ['sometag', 'bronze', 'other_tag']}

        return ResponseObj()

    @patch('partner_offers.data_for_consumer.get_basic_db_data')
    async def get_basic_db_data(
            consumer: models.Consumer,
            loyalties: str,
            antitags: str,
            longitude: float,
            latitude: float,
            *args,
            **kwargs,
    ):
        assert consumer == models.Consumer.DRIVER
        assert set(loyalties) == {'bronze', 'contractor_market_place'}
        assert longitude == 50.8
        assert latitude == 37.7

        return db_access.BasicDbData(
            location_to_deals={},
            locations={},
            calc_at=datetime.datetime.now(),
            open_work_times={},
            deal_ids=set(),
            deals={},
            partners={},
        )

    @patch('partner_offers.data_for_consumer.get_driver_deals_from_db_data')
    async def get_driver_deals_from_db_data(
            db_data: db_access.BasicDbData,
            park_id: str,
            driver_id: str,
            locale: str,
            *args,
            **kwargs,
    ):
        assert locale == 'ru'

        return EXPECTED_RESPONSE

    response = await web_app_client.get(
        '/v1/driver/deals-available',
        params={'latitude': '37.7', 'longitude': '50.8'},
        headers=DRIVER_REQUEST_HEADERS,
    )
    assert response.status == 200, await response.text()
    assert await response.json() == EXPECTED_RESPONSE.serialize()

    assert bool(get_basic_db_data.calls) is True
    assert bool(get_driver_deals_from_db_data.calls) is True


@pytest.mark.config(CONTRACTOR_MERCH_OFFERS_ENABLED=True)
@pytest.mark.parametrize(
    ['park_id', 'driver_id'],
    [
        pytest.param(
            'some',
            'driver',
            marks=pytest.mark.client_experiments3(
                consumer='partner-offers/v1_driver_deals_available',
                config_name='partner_offers_validate_taximeter_version',
                file_args=(
                    'configs3/validate_taximeter_version_default_args.json'
                ),
                value={'enabled': False},
            ),
            id='config did not match',
        ),
        pytest.param(
            'another',
            'driver',
            marks=pytest.mark.client_experiments3(
                consumer='partner-offers/v1_driver_deals_available',
                config_name='partner_offers_validate_taximeter_version',
                file_args=(
                    'configs3/validate_taximeter_version_default_args.json'
                ),
                value={'enabled': True},
            ),
            id='config parameters did not match',
        ),
    ],
)
async def test_invalid_taximeter_version(
        patch,
        web_app_client,
        mock_contractor_merch_client,
        park_id,
        driver_id,
):
    @patch(
        'taxi.clients.driver_tags.DriverTagsClient.v1_drivers_match_profile',
    )
    async def mock_driver_tags_drivers_match(
            park_id, driver_uuid, *args, **kwargs,
    ):
        class ResponseObj:
            async def json(self):
                return {'tags': ['silver', 'bronze']}

        return ResponseObj()

    mock_contractor_merch_client.retrieve_all_response = {
        'feeds': EXPECTED_RETRIEVE_ALL_RESPONSES[0],
        'categories': EXPECTED_RETRIEVE_ALL_CATEGORIES[0],
    }

    response = await web_app_client.get(
        '/v1/driver/deals-available',
        params={'latitude': '37.7', 'longitude': '50.8'},
        headers={
            **DRIVER_REQUEST_HEADERS,
            'X-YaTaxi-Park-Id': park_id,
            'X-YaTaxi-Driver-Profile-Id': driver_id,
        },
    )

    response_json = await response.json()

    assert response.status == 200

    response_json.pop('calculated_at')
    assert response_json == {
        'categories': [],
        'deals': [],
        'locations': [],
        'polling_delay_seconds': 1800,
    }


@pytest.mark.pgsql('partner_offers', files=['pg_init.sql'])
@pytest.mark.client_experiments3(
    consumer='partner-offers/v1_driver_deals_available',
    config_name='partner_offers_validate_taximeter_version',
    file_args='configs3/validate_taximeter_version_default_args.json',
    value={'enabled': True},
)
@pytest.mark.config(
    PARTNER_DEALS_PARTNER_CATEGORIES=CATEGORIES_DATA,
    PARTNER_DEALS_WORK_TIMES=WORK_TIME_CONF,
    PARTNER_DEALS_POLLING_DELAY=1800,
    CONTRACTOR_MERCH_OFFERS_ENABLED=False,
)
@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
async def test_no_loyalty(patch, web_app_client):
    @patch(
        'taxi.clients.driver_tags.DriverTagsClient.v1_drivers_match_profile',
    )
    async def mock_driver_tags_drivers_match(
            park_id, driver_uuid, *args, **kwargs,
    ):
        assert park_id == 'some'
        assert driver_uuid == 'driver'

        class ResponseObj:
            async def json(self):
                return {'tags': ['sometag', 'other_tag']}

        return ResponseObj()

    @patch('partner_offers.data_for_consumer.get_deals_and_locations')
    async def get_deals_and_locations(
            consumer: models.Consumer,
            loyalty_status: str,
            longitude: float,
            latitude: float,
            locale: str,
            *args,
            **kwargs,
    ):
        return EXPECTED_RESPONSE

    @patch('partner_offers.data_for_consumer.empty_consumers_deals_data')
    def empty_consumers_deals_data(context):
        return api.ConsumersDealsData(
            calculated_at=datetime.datetime.fromisoformat(
                '2019-06-07T12:15+03:00',
            ),
            categories=[],
            deals=[],
            locations=[],
            polling_delay_seconds=1800,
        )

    response = await web_app_client.get(
        '/v1/driver/deals-available',
        params={'latitude': '37.7', 'longitude': '50.8'},
        headers=DRIVER_REQUEST_HEADERS,
    )
    assert response.status == 200, await response.text()
    assert await response.json() == {
        'calculated_at': '2019-06-07T12:15:00+03:00',
        'deals': [],
        'locations': [],
        'categories': [],
        'polling_delay_seconds': 1800,
    }

    assert bool(get_deals_and_locations.calls) is False
    assert bool(empty_consumers_deals_data.calls) is True


@pytest.mark.now('2020-01-01T00:00:00')
@pytest.mark.pgsql('partner_offers', files=['multi_tagged_search.sql'])
@pytest.mark.client_experiments3(
    consumer='partner-offers/v1_driver_deals_available',
    config_name='partner_offers_validate_taximeter_version',
    file_args='configs3/validate_taximeter_version_default_args.json',
    value={'enabled': True},
)
@pytest.mark.config(
    PARTNER_DEALS_PARTNER_CATEGORIES=CATEGORIES_DATA,
    PARTNER_DEALS_WORK_TIMES=WORK_TIME_CONF,
    PARTNER_DEALS_POLLING_DELAY=1800,
)
@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
async def test_multiple_tags(
        web_app_client,
        mockserver,
        patch,
        load_json,
        mock_contractor_merch_client,
):
    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _multi_tags(request):
        return {'tags': ['silver', 'bronze']}

    response = await web_app_client.get(
        '/v1/driver/deals-available',
        params={'latitude': '80.4', 'longitude': '40.5'},
        headers=DRIVER_REQUEST_HEADERS,
    )
    assert response.status == 200, await response.text()
    assert await response.json() == load_json('multi-tagged-response.json')


@pytest.mark.now('2020-01-01T00:00:00')
@pytest.mark.pgsql('partner_offers', files=['multi_tagged_search.sql'])
@pytest.mark.config(
    PARTNER_DEALS_PARTNER_CATEGORIES=CATEGORIES_DATA,
    PARTNER_DEALS_WORK_TIMES=WORK_TIME_CONF,
    PARTNER_DEALS_POLLING_DELAY=1800,
)
@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
async def test_multiple_tags_find_for_anyone(
        web_app_client,
        mockserver,
        mock_contractor_merch_client,
        patch,
        load_json,
):
    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _multi_tags(request):
        return {'tags': ['silver', 'bronze']}

    response = await web_app_client.post(
        '/v1/deals-available',
        json={
            'consumer_type': 'driver',
            'consumer_loyalties': ['silver', 'bronze'],
            'latitude': 80.4,
            'longitude': 40.5,
        },
    )
    assert response.status == 200, await response.text()
    assert await response.json() == load_json('multi-tagged-response.json')


@pytest.mark.now('2020-01-01T00:00:00')
@pytest.mark.pgsql('partner_offers', files=['antitags_search.sql'])
@pytest.mark.client_experiments3(
    consumer='partner-offers/v1_driver_deals_available',
    config_name='partner_offers_validate_taximeter_version',
    file_args='configs3/validate_taximeter_version_default_args.json',
    value={'enabled': True},
)
@pytest.mark.config(
    PARTNER_DEALS_PARTNER_CATEGORIES=CATEGORIES_DATA,
    PARTNER_DEALS_WORK_TIMES=WORK_TIME_CONF,
    PARTNER_DEALS_POLLING_DELAY=1800,
    PARTNER_DEALS_CONSUMER_TAGS={
        'courier': {},
        'driver': {'silver': {}, 'platinum': {}},
    },
    PARTNER_DEALS_CONSUMER_ANTITAGS=['antitag'],
)
@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
@pytest.mark.parametrize(
    'tags, response_json',
    [
        (['silver'], 'antitags_full_response.json'),
        (['silver', 'antitag'], 'antitags_filtred_response.json'),
    ],
)
async def test_antitags(
        web_app_client,
        mockserver,
        patch,
        load_json,
        mock_contractor_merch_client,
        tags,
        response_json,
):
    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _multi_tags(request):
        return {'tags': tags}

    response = await web_app_client.get(
        '/v1/driver/deals-available',
        params={'latitude': '80.4', 'longitude': '40.5'},
        headers=DRIVER_REQUEST_HEADERS,
    )
    assert response.status == 200, await response.text()
    assert await response.json() == load_json(response_json)


@pytest.mark.pgsql('partner_offers', files=['pg_init.sql'])
@pytest.mark.client_experiments3(
    consumer='partner-offers/v1_driver_deals_available',
    config_name='partner_offers_validate_taximeter_version',
    file_args='configs3/validate_taximeter_version_default_args.json',
    value={'enabled': True},
)
@pytest.mark.config(
    PARTNER_DEALS_PARTNER_CATEGORIES=CATEGORIES_DATA,
    PARTNER_DEALS_WORK_TIMES=WORK_TIME_CONF,
    PARTNER_DEALS_POLLING_DELAY=1800,
    CONTRACTOR_MERCH_OFFERS_ENABLED=True,
)
@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
@pytest.mark.parametrize(
    'test_id, answers', [(0, [0, 2]), (1, [0, 1, 2]), (2, [2])],
)
async def test_find_deals_with_offers_enabled(
        web_app_client,
        mockserver,
        mock_contractor_merch_client,
        load_json,
        test_id,
        answers,
):
    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _multi_tags(request):
        return {'tags': ['silver', 'bronze']}

    mock_contractor_merch_client.retrieve_all_response = {
        'feeds': EXPECTED_RETRIEVE_ALL_RESPONSES[test_id],
        'categories': EXPECTED_RETRIEVE_ALL_CATEGORIES[test_id],
    }

    response = await web_app_client.get(
        '/v1/driver/deals-available',
        params={'latitude': '37.7', 'longitude': '50.8'},
        headers=DRIVER_REQUEST_HEADERS,
    )

    assert mock_contractor_merch_client.retrieve_all.times_called == 1
    assert mock_contractor_merch_client.retrieve_all.next_call()[
        'request'
    ].json == {'driver': {'park_id': 'some', 'driver_profile_id': 'driver'}}

    resp_json = await response.json()

    assert response.status == 200, await response.text()

    expected_deals = [
        {
            'category_id': 'cm_tire',
            'description': {'title': 'Mcdonalds (hopefully)'},
            'id': '1',
            'locations': ['101'],
            'terms': {'price': '4₽'},
            'title': 'Mcdonalds (hopefully)',
            'type': 'coupon',
            'marketplace_immutable_offer_id': (
                '01234567890123456789012345678901'
            ),
        },
        {
            'category_id': 'cm_washing',
            'description': {
                'title': 'Mcdonalds (hopefully)',
                'text': 'Test full data',
            },
            'id': '2',
            'locations': ['101'],
            'terms': {'price': '0₽'},
            'title': 'Mcdonalds (hopefully)',
            'subtitle': 'Big mac',
            'type': 'coupon',
            'marketplace_immutable_offer_id': (
                '01234567890123456789012345678xxx'
            ),
        },
        {
            'category_id': 'food',
            'description': {'title': 'some'},
            'id': '3',
            'locations': ['101'],
            'terms': {'text': 'Some', 'percent': '10%'},
            'title': 'Third',
            'type': 'discount',
        },
    ]

    expected_categories = ['cm_tire', 'cm_washing', 'food']

    assert resp_json['deals'] == [expected_deals[i] for i in answers]
    assert (
        resp_json['locations'][0]['categories'][0]['category_id']
        == expected_categories[test_id]
    )


@pytest.mark.pgsql('partner_offers', files=['pg_init.sql'])
@pytest.mark.client_experiments3(
    consumer='partner-offers/v1_driver_deals_available',
    config_name='partner_offers_validate_taximeter_version',
    file_args='configs3/validate_taximeter_version_default_args.json',
    value={'enabled': True},
)
@pytest.mark.config(
    PARTNER_DEALS_PARTNER_CATEGORIES=CATEGORIES_DATA,
    PARTNER_DEALS_WORK_TIMES=WORK_TIME_CONF,
    PARTNER_DEALS_POLLING_DELAY=1800,
    CONTRACTOR_MERCH_OFFERS_ENABLED=False,
)
@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
async def test_find_deals_with_offers_disabled(
        web_app_client, mockserver, load_json,
):
    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _multi_tags(request):
        return {'tags': ['silver', 'bronze']}

    @mockserver.json_handler(
        '/contractor-merch/internal/contractor-merch/v1/offers/retrieve-all',
    )
    def _retrieve_all(request):
        assert False, 'Must not be called'

    response = await web_app_client.get(
        '/v1/driver/deals-available',
        params={'latitude': '37.7', 'longitude': '50.8'},
        headers=DRIVER_REQUEST_HEADERS,
    )

    resp_json = await response.json()

    assert response.status == 200, await response.text()
    assert resp_json['deals'] == EXPECTED_DEALS_ITEMS[2:]


@pytest.mark.pgsql('partner_offers', files=['pg_init.sql'])
@pytest.mark.client_experiments3(
    consumer='partner-offers/v1_driver_deals_available',
    config_name='partner_offers_validate_taximeter_version',
    file_args='configs3/validate_taximeter_version_default_args.json',
    value={'enabled': True},
)
@pytest.mark.config(
    PARTNER_DEALS_PARTNER_CATEGORIES=CATEGORIES_DATA,
    PARTNER_DEALS_WORK_TIMES=WORK_TIME_CONF,
    PARTNER_DEALS_POLLING_DELAY=1800,
    CONTRACTOR_MERCH_OFFERS_ENABLED=True,
)
@pytest.mark.translations(taximeter_backend_driver_messages=TRANSLATIONS)
async def test_retrieve_all_error_response(
        web_app_client, mockserver, load_json,
):
    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _multi_tags(request):
        return {'tags': ['silver', 'bronze']}

    @mockserver.json_handler(
        '/contractor-merch/internal/contractor-merch/v1/offers/retrieve-all',
    )
    def _retrieve_all(request):
        assert request.json == {
            'driver': {'park_id': 'some', 'driver_profile_id': 'driver'},
        }

        return aiohttp.web.json_response({}, status=500)

    response = await web_app_client.get(
        '/v1/driver/deals-available',
        params={'latitude': '37.7', 'longitude': '50.8'},
        headers=DRIVER_REQUEST_HEADERS,
    )

    resp_json = await response.json()

    assert response.status == 200, await response.text()
    assert resp_json['deals'] == [EXPECTED_DEALS_ITEMS[2]]
