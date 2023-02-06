from dateutil import parser
import pytest

from tests_eats_retail_market_integration import models
from tests_eats_retail_market_integration.eats_catalog_internals import storage

MOCK_NOW = '2021-12-24T08:00:00+00:00'
LATITUDE = 55.725326
LONGITUDE = 37.567051
REGION_ID = 1
SHOPS_LIMIT = 1

BRAND_1_ID = '1'
BRAND_2_ID = '2'
BRAND_3_ID = '3'
PLACE_1_ID = '1'
PLACE_2_ID = '2'
PLACE_3_ID = '3'
PLACE_4_ID = '4'
PLACE_5_ID = '5'
PLACE_6_ID = '6'
PLACE_7_ID = '7'
PLACE_8_ID = '8'

CATALOG_REQUEST = {
    'blocks': [
        {
            'condition': {
                'init': {
                    'arg_name': 'business',
                    'arg_type': 'string',
                    'value': 'shop',
                },
                'type': 'eq',
            },
            'disable_filters': False,
            'round_eta_to_hours': False,
            'id': 'SHOPS_ONLY_MARKET',
            'type': 'any',
            'with_delivery_conditions': True,
            'with_extra_delivery_meta': True,
            'limit': 50,
        },
    ],
    'condition': {
        'init': {
            'arg_name': 'business',
            'arg_type': 'string',
            'value': 'shop',
        },
        'type': 'eq',
    },
    'location': {'latitude': LATITUDE, 'longitude': LONGITUDE},
}

EATS_CUSTOMER_SLOTS_REQUEST_PLACES = [
    {'estimated_delivery_duration': 6900, 'place_id': int(PLACE_2_ID)},
    {'estimated_delivery_duration': 6900, 'place_id': int(PLACE_7_ID)},
    {'estimated_delivery_duration': 6900, 'place_id': int(PLACE_8_ID)},
]


@pytest.mark.now(MOCK_NOW)
async def test_get_available_shops_using_eats_catalog(
        load_json,
        mockserver,
        taxi_eats_retail_market_integration,
        save_brands_to_db,
        save_market_brand_places_to_db,
        update_taxi_config,
):
    update_taxi_config(
        'EATS_RETAIL_MARKET_INTEGRATION_HYPERLOCAL_SHOPS',
        {'use_catalog_lib': False},
    )

    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _mock_eats_catalog(request):
        catalog_response = load_json('catalog_response.json')
        if request.json['blocks'][0]['limit'] == SHOPS_LIMIT:
            # check limit
            CATALOG_REQUEST['blocks'][0]['limit'] = request.json['blocks'][0][
                'limit'
            ]
            catalog_response['blocks'][0]['list'] = [
                catalog_response['blocks'][0]['list'][0:SHOPS_LIMIT],
            ]
        assert request.json == CATALOG_REQUEST
        return catalog_response

    response = await taxi_eats_retail_market_integration.get(
        '/v1/market/hyperlocal_shops'
        f'?latitude={LATITUDE}&longitude={LONGITUDE}&region_id={REGION_ID}',
    )

    assert response.status_code == 200
    assert _mock_eats_catalog.has_calls

    response = response.json()
    expected_response = load_json('hyperlocal_shops_response.json')

    assert response['currency'] == expected_response['currency']
    assert sorted_by_market_shop_id(
        response['shops'],
    ) == sorted_by_market_shop_id(expected_response['shops'])


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    EATS_RETAIL_MARKET_INTEGRATION_HYPERLOCAL_SHOPS={
        'shops_limit': SHOPS_LIMIT,
    },
)
async def test_get_available_shops_with_limit(
        load_json,
        mockserver,
        taxi_eats_retail_market_integration,
        save_brands_to_db,
        save_market_brand_places_to_db,
):
    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    @mockserver.json_handler('/eats-catalog/internal/v1/catalog-for-layout')
    def _mock_eats_catalog(request):
        CATALOG_REQUEST['blocks'][0]['limit'] = SHOPS_LIMIT
        assert request.json == CATALOG_REQUEST

        catalog_response = load_json('catalog_response.json')
        catalog_response['blocks'][0]['list'] = catalog_response['blocks'][0][
            'list'
        ][0:SHOPS_LIMIT]
        return catalog_response

    response = await taxi_eats_retail_market_integration.get(
        '/v1/market/hyperlocal_shops'
        f'?latitude={LATITUDE}&longitude={LONGITUDE}&region_id={REGION_ID}',
    )

    assert response.status_code == 200
    assert _mock_eats_catalog.has_calls

    assert len(response.json()['shops']) == SHOPS_LIMIT


@pytest.mark.now(MOCK_NOW)
async def test_get_available_shops_using_places_lib(
        taxi_eats_retail_market_integration,
        eats_catalog_storage,
        load_json,
        save_brands_to_db,
        save_market_brand_places_to_db,
):
    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    # this place will be deduplicated as place_id=2 will be added for brand 1
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=int(PLACE_1_ID),
            slug=PLACE_1_ID,
            brand=storage.Brand(brand_id=int(BRAND_1_ID)),
            business=storage.Business.Shop,
        ),
    )
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=int(PLACE_2_ID),
            slug=PLACE_2_ID,
            brand=storage.Brand(brand_id=int(BRAND_1_ID)),
            business=storage.Business.Shop,
        ),
    )
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=int(PLACE_7_ID),
            slug=PLACE_7_ID,
            brand=storage.Brand(brand_id=int(BRAND_2_ID)),
            business=storage.Business.Shop,
        ),
    )

    response = await taxi_eats_retail_market_integration.get(
        '/v1/market/hyperlocal_shops'
        f'?latitude={LATITUDE}&longitude={LONGITUDE}&region_id={REGION_ID}',
    )

    assert response.status_code == 200

    response = response.json()
    expected_response = load_json('hyperlocal_shops_response_via_lib.json')

    assert response['currency'] == expected_response['currency']
    assert sorted_by_priority(response['shops']) == sorted_by_priority(
        expected_response['shops'],
    )


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    EATS_RETAIL_MARKET_INTEGRATION_HYPERLOCAL_SHOPS={
        'use_catalog_lib': True,
        'use_slots_availability': True,
    },
)
async def test_filter_shops_due_to_slots_availability(
        taxi_eats_retail_market_integration,
        eats_catalog_storage,
        load_json,
        mockserver,
        save_brands_to_db,
        save_market_brand_places_to_db,
        testpoint,
):
    @mockserver.json_handler(
        '/eats-customer-slots/api/v1/places/calculate-delivery-time',
    )
    def _mock_eats_customer_slots(request):
        assert (
            sorted(request.json['places'], key=lambda item: item['place_id'])
            == EATS_CUSTOMER_SLOTS_REQUEST_PLACES
        )
        slots_response = load_json('slots_response.json')
        return slots_response

    @testpoint('hyperlocal_shops-places_availability')
    def check_places_availability(data_json):
        assert sorted(data_json, key=lambda item: item['place_id']) == [
            {'place_id': int(PLACE_2_ID), 'is_available_now': True},
            {'place_id': int(PLACE_7_ID), 'is_available_now': False},
            {'place_id': int(PLACE_8_ID), 'is_available_now': True},
        ]

    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    eats_places_set_init_places(eats_catalog_storage)

    response = await taxi_eats_retail_market_integration.get(
        '/v1/market/hyperlocal_shops'
        f'?latitude={LATITUDE}&longitude={LONGITUDE}&region_id={REGION_ID}',
    )

    assert response.status_code == 200

    response = response.json()
    assert _mock_eats_customer_slots.has_calls

    expected_response = load_json(
        'hyperlocal_shops_response_for_slots_test.json',
    )

    assert response['currency'] == expected_response['currency']
    assert sorted_by_priority(response['shops']) == sorted_by_priority(
        expected_response['shops'],
    )

    assert check_places_availability.times_called == 1


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(
    EATS_RETAIL_MARKET_INTEGRATION_HYPERLOCAL_SHOPS={'use_catalog_lib': True},
    EATS_NOMENCLATURE_EXPORT_TO_MARKET_BRANDS_BLACK_LIST={
        'brand_ids': [int(BRAND_1_ID)],
    },
)
async def test_filter_brands_black_list(
        taxi_eats_retail_market_integration,
        eats_catalog_storage,
        load_json,
        save_brands_to_db,
        save_market_brand_places_to_db,
):
    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    # places 2, 7 and 8 are set, but place 2 has brand 1,
    # which is blacklisted, so it doesn't get to response
    eats_places_set_init_places(eats_catalog_storage)

    response = await taxi_eats_retail_market_integration.get(
        '/v1/market/hyperlocal_shops'
        f'?latitude={LATITUDE}&longitude={LONGITUDE}&region_id={REGION_ID}',
    )

    assert response.status_code == 200

    response = response.json()
    expected_response = load_json(
        'hyperlocal_shops_response_brands_black_list_test.json',
    )

    assert response['currency'] == expected_response['currency']
    assert sorted_by_priority(response['shops']) == sorted_by_priority(
        expected_response['shops'],
    )


@pytest.mark.now(MOCK_NOW)
async def test_logging(
        taxi_eats_retail_market_integration,
        eats_catalog_storage,
        testpoint,
        save_brands_to_db,
        save_market_brand_places_to_db,
):
    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    @testpoint('yt-logger-hyperlocal-shops-log')
    def yt_logger_hyperlocal_shops_log(data):
        del data['timestamp']
        assert data == {
            'currency': 'RUR',
            'latitude': LATITUDE,
            'longitude': LONGITUDE,
            'region_id': REGION_ID,
            'response_code': 200,
            'shops': [
                {'market_shop_id': 7, 'priority': 0},
                {'market_shop_id': 2, 'priority': 1},
            ],
            'X-AppMetrica-DeviceId': '1e50abaa3e95bf8542fb5d0c783a8feb',
            'X-Ya-PUID': '4065912996',
            'X-Ya-YUID': '9993495911650037913',
        }

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=int(PLACE_2_ID),
            slug=PLACE_2_ID,
            brand=storage.Brand(brand_id=int(BRAND_1_ID)),
            business=storage.Business.Shop,
        ),
    )
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=int(PLACE_7_ID),
            slug=PLACE_7_ID,
            brand=storage.Brand(brand_id=int(BRAND_2_ID)),
            business=storage.Business.Shop,
        ),
    )

    headers = {
        'X-Ya-PUID': '4065912996',
        'X-Ya-YUID': '9993495911650037913',
        'X-AppMetrica-DeviceId': '1e50abaa3e95bf8542fb5d0c783a8feb',
    }

    response = await taxi_eats_retail_market_integration.get(
        '/v1/market/hyperlocal_shops'
        f'?latitude={LATITUDE}&longitude={LONGITUDE}&region_id={REGION_ID}',
        headers=headers,
    )

    assert response.status_code == 200
    assert yt_logger_hyperlocal_shops_log.times_called == 1


def sorted_by_market_shop_id(data):
    return sorted(data, key=lambda item: item['market_shop_id'])


def sorted_by_priority(data):
    return sorted(data, key=lambda item: item['priority'])


def _generate_db_init_data():
    brand1 = models.Brand(brand_id=BRAND_1_ID, slug='brand1')
    brand1.add_places(
        [
            models.Place(place_id=PLACE_1_ID, slug='place1'),
            models.Place(place_id=PLACE_2_ID, slug='place2'),
            models.Place(place_id=PLACE_3_ID, slug='place3'),
            models.Place(place_id=PLACE_4_ID, slug='place4'),
            models.Place(place_id=PLACE_5_ID, slug='place5'),
            models.Place(place_id=PLACE_6_ID, slug='place6'),
        ],
    )
    brand2 = models.Brand(brand_id=BRAND_2_ID, slug='brand2')
    brand2.add_places([models.Place(place_id=PLACE_7_ID, slug='place7')])
    brand3 = models.Brand(brand_id=BRAND_3_ID, slug='brand2')
    brand3.add_places([models.Place(place_id=PLACE_8_ID, slug='place8')])
    brands = [brand1, brand2, brand3]

    market_brand_places = [
        models.MarketBrandPlace(
            brand_id=BRAND_1_ID,
            place_id=PLACE_1_ID,
            business_id=1,
            partner_id=1,
            feed_id=1,
        ),
        models.MarketBrandPlace(
            brand_id=BRAND_1_ID,
            place_id=PLACE_2_ID,
            business_id=1,
            partner_id=2,
            feed_id=2,
        ),
        models.MarketBrandPlace(
            brand_id=BRAND_1_ID,
            place_id=PLACE_3_ID,
            business_id=1,
            partner_id=3,
            feed_id=3,
        ),
        models.MarketBrandPlace(
            brand_id=BRAND_1_ID,
            place_id=PLACE_5_ID,
            business_id=1,
            partner_id=5,
            feed_id=5,
        ),
        models.MarketBrandPlace(
            brand_id=BRAND_1_ID,
            place_id=PLACE_6_ID,
            business_id=1,
            partner_id=6,
            feed_id=6,
        ),
        models.MarketBrandPlace(
            brand_id=BRAND_2_ID,
            place_id=PLACE_7_ID,
            business_id=2,
            partner_id=7,
            feed_id=7,
        ),
        models.MarketBrandPlace(
            brand_id=BRAND_3_ID,
            place_id=PLACE_8_ID,
            business_id=3,
            partner_id=8,
            feed_id=8,
        ),
    ]
    return {'brands': brands, 'market_brand_places': market_brand_places}


def eats_places_set_init_places(eats_catalog_storage):
    open_schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-12-24T06:00:00+00:00'),
            end=parser.parse('2021-12-24T18:00:00+00:00'),
        ),
    ]
    # asap slot available - included in result
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=int(PLACE_2_ID),
            slug=PLACE_2_ID,
            brand=storage.Brand(brand_id=int(BRAND_1_ID)),
            business=storage.Business.Shop,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=int(PLACE_2_ID),
            working_intervals=open_schedule,
        ),
    )
    # asap slot unavailable - excluded from result
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=int(PLACE_7_ID),
            slug=PLACE_7_ID,
            brand=storage.Brand(brand_id=int(BRAND_2_ID)),
            business=storage.Business.Shop,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=int(PLACE_7_ID),
            working_intervals=open_schedule,
        ),
    )
    # no asap info - included in result
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=int(PLACE_8_ID),
            slug=PLACE_8_ID,
            brand=storage.Brand(brand_id=int(BRAND_3_ID)),
            business=storage.Business.Shop,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=int(PLACE_8_ID),
            working_intervals=open_schedule,
        ),
    )
