from dateutil import parser
import pytest

from tests_eats_retail_market_integration import models
from tests_eats_retail_market_integration.eats_catalog_internals import storage

MOCK_NOW = '2021-12-24T08:00:00+00:00'
HANDLER = '/v1/market/shops/thresholds'
EDA_DELIVERY_PRICE_HANDLER = '/eda-delivery-price/v1/calc-delivery-price-surge'

LATITUDE = 55.725326
LONGITUDE = 37.567051

BRAND_1_ID = '1'
BRAND_2_ID = '2'
PLACE_1_ID = '1'
PLACE_2_ID = '2'
PLACE_3_ID = '3'
SHOP_1_ID = 11


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'exp_type',
    [
        pytest.param(
            'regular_exp',
            marks=(
                pytest.mark.experiments3(
                    filename='calc_delivery_price_exp.json',
                )
            ),
            id='regular experiment',
        ),
        pytest.param(
            'small_exp',
            marks=(
                pytest.mark.experiments3(
                    filename='calc_delivery_price_small_exp.json',
                )
            ),
            id='small experiment',
        ),
    ],
)
async def test_get_shops_thresholds_from_exp(
        taxi_eats_retail_market_integration,
        eats_catalog_storage,
        save_brands_to_db,
        save_market_brand_places_to_db,
        exp_type,
):
    if exp_type == 'regular_exp':
        thresholds = _get_default_thresholds()
    else:
        thresholds = _get_small_exp_thresholds()
    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    place_id = int(PLACE_1_ID)
    shop_id = SHOP_1_ID
    _add_place_to_storage_mock(
        eats_catalog_storage, place_id=place_id, with_zone=True, zone_id=1,
    )

    request = {
        'shop_ids': [shop_id],
        'user_address': {'latitude': LATITUDE, 'longitude': LONGITUDE},
    }
    response = await taxi_eats_retail_market_integration.post(
        HANDLER, json=request,
    )

    assert response.status_code == 200
    assert response.json() == _generate_expected_response(shop_id, thresholds)


@pytest.mark.now(MOCK_NOW)
async def test_get_shops_thresholds_from_client(
        taxi_eats_retail_market_integration,
        eats_catalog_storage,
        mockserver,
        update_taxi_config,
        save_brands_to_db,
        save_market_brand_places_to_db,
):
    update_taxi_config(
        'EATS_RETAIL_MARKET_INTEGRATION_SHOPS_THRESHOLDS_SETTINGS',
        {'use_calc_delivery_price_surge': True},
    )

    place_id = int(PLACE_1_ID)
    shop_id = SHOP_1_ID
    thresholds = _get_default_thresholds()
    db_initial_data = _generate_db_init_data()

    @mockserver.json_handler(EDA_DELIVERY_PRICE_HANDLER)
    def _mock_delivery_price(request):
        return _generate_delivery_price_response(place_id, thresholds)

    save_brands_to_db(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    _add_place_to_storage_mock(
        eats_catalog_storage, place_id=place_id, with_zone=True, zone_id=1,
    )

    request = {
        'shop_ids': [shop_id],
        'user_address': {'latitude': LATITUDE, 'longitude': LONGITUDE},
    }
    response = await taxi_eats_retail_market_integration.post(
        HANDLER, json=request,
    )

    assert response.status_code == 200
    assert response.json() == _generate_expected_response(shop_id, thresholds)
    assert _mock_delivery_price.times_called == 1


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'error',
    [
        'mapping shop_id->place_id not found',
        'place in storage not found',
        pytest.param(
            'place does not have zone',
            marks=(
                pytest.mark.experiments3(
                    filename='calc_delivery_price_empty_thresholds_exp.json',
                )
            ),
        ),
        pytest.param(
            'empty thresholds in experiment',
            marks=(
                pytest.mark.experiments3(
                    filename='calc_delivery_price_empty_thresholds_exp.json',
                )
            ),
        ),
        'empty thresholds in client',
    ],
)
async def test_get_shops_thresholds_empty_response_from_exp(
        taxi_eats_retail_market_integration,
        eats_catalog_storage,
        save_brands_to_db,
        save_market_brand_places_to_db,
        # parametrize
        error,
):
    db_initial_data = _generate_db_init_data()
    save_brands_to_db(db_initial_data['brands'])
    save_market_brand_places_to_db(db_initial_data['market_brand_places'])

    place_id = int(PLACE_1_ID)
    shop_id = SHOP_1_ID
    if error == 'mapping shop_id->place_id not found':
        # do not need to add place in storage as processing will pass
        # this shop_id before requesting to places_storage
        unknown_shop_id = 99999
        shop_id = unknown_shop_id
    elif error == 'place in storage not found':
        # intentionally do not add place to places_storage
        pass
    elif error == 'place does not have zone':
        # add place to places_storage without zone, so we can't
        # match experiment, as zone_id is required kwarg
        _add_place_to_storage_mock(
            eats_catalog_storage, place_id=place_id, with_zone=False,
        )
    elif error == 'empty thresholds in experiment':
        # add place to places_storage without zone, so that
        # experiment will match, but there will be no thresholds
        _add_place_to_storage_mock(
            eats_catalog_storage, place_id=place_id, with_zone=True, zone_id=1,
        )

    request = {
        'shop_ids': [shop_id],
        'user_address': {'latitude': LATITUDE, 'longitude': LONGITUDE},
    }
    response = await taxi_eats_retail_market_integration.post(
        HANDLER, json=request,
    )

    assert response.status_code == 404


def _add_place_to_storage_mock(
        eats_catalog_storage, place_id, with_zone, zone_id=None,
):
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=place_id,
            slug=str(place_id),
            brand=storage.Brand(brand_id=1),
            business=storage.Business.Shop,
        ),
    )
    if with_zone:
        assert zone_id is not None
        schedule = [
            storage.WorkingInterval(
                start=parser.parse('2021-12-24T08:00:00+00:00'),
                end=parser.parse('2021-12-24T17:52:00+00:00'),
            ),
        ]
        eats_catalog_storage.add_zone(
            storage.Zone(
                place_id=place_id, zone_id=zone_id, working_intervals=schedule,
            ),
        )


def _generate_db_init_data():
    brand1 = models.Brand(brand_id=BRAND_1_ID, slug='brand1')
    brand1.add_places(
        [
            models.Place(place_id=PLACE_1_ID, slug='place1'),
            models.Place(place_id=PLACE_2_ID, slug='place2'),
        ],
    )
    brand2 = models.Brand(brand_id=BRAND_2_ID, slug='brand2')
    brand2.add_places([models.Place(place_id=PLACE_3_ID, slug='place3')])
    brands = [brand1, brand2]

    market_brand_places = [
        models.MarketBrandPlace(
            brand_id=BRAND_1_ID,
            place_id=PLACE_1_ID,
            business_id=1,
            partner_id=SHOP_1_ID,
            feed_id=SHOP_1_ID,
        ),
        models.MarketBrandPlace(
            brand_id=BRAND_1_ID,
            place_id=PLACE_2_ID,
            business_id=1,
            partner_id=12,
            feed_id=12,
        ),
        models.MarketBrandPlace(
            brand_id=BRAND_2_ID,
            place_id=PLACE_3_ID,
            business_id=2,
            partner_id=23,
            feed_id=23,
        ),
    ]
    return {'brands': brands, 'market_brand_places': market_brand_places}


def _generate_delivery_price_response(place_id, thresholds):
    return {
        'calculation_result': {
            'calculation_name': 'delivery_price_pipeline',
            'result': {
                'extra': {},
                'fees': [
                    {
                        'order_price': i['min_cart_price'],
                        'delivery_cost': i['delivery_cost'],
                    }
                    for i in thresholds
                ],
                'is_fallback': False,
            },
        },
        'experiment_errors': [],
        'experiment_results': [],
        'surge_extra': {},
        'surge_result': {'placeId': place_id},
        'meta': {},
    }


def _get_default_thresholds():
    return [
        {'min_cart_price': 0, 'max_cart_price': 500, 'delivery_cost': 350.0},
        {
            'min_cart_price': 500,
            'max_cart_price': 2000,
            'delivery_cost': 220.0,
        },
        {'min_cart_price': 2000, 'delivery_cost': 0.0},
    ]


def _get_small_exp_thresholds():
    return [{'min_cart_price': 0, 'delivery_cost': 350.0}]


def _generate_expected_response(shop_id, thresholds):
    return [
        {
            'currency': 'RUR',
            'delivery_time_minutes': 120,
            'shop_id': shop_id,
            'thresholds': [
                {
                    'min_cart_included': i['min_cart_price'],
                    **(
                        {'max_cart_excluded': i['max_cart_price']}
                        if 'max_cart_price' in i
                        else {}
                    ),
                    'delivery_price': i['delivery_cost'],
                }
                for i in thresholds
            ],
        },
    ]
