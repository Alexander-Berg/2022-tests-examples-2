import pytest

from taxi import pro_app

from taxi_selfreg.generated.service.cities_cache import plugin as cities_cache
from taxi_selfreg.generated.service.swagger.models import api
from taxi_selfreg.generated.web import web_context as context_module


MOSCOW = cities_cache.City(
    name='Москва',
    lat=55.45,
    lon=37.37,
    country_id='rus',
    region_id='213',
    geoarea='moscow',
)

BAD_CITY = cities_cache.City(
    name='Город без региона', lat=55.45, lon=37.37, country_id='rus',
)

EXPECT_PARK_CHOICES = [
    api.ParksChoice(
        park_id='foo_db_id',
        name='foo_name',
        address='foo_address',
        contact_phones=['foo_phone'],
        location=api.PositionObject(lat=55.45, lon=37.37),
    ),
    api.ParksChoice(
        park_id='', name='bad_name', address='', contact_phones=[],
    ),
    api.ParksChoice(
        park_id='bar_db_id', name='bar_name', address='', contact_phones=[],
    ),
]


@pytest.mark.config(
    TAXIMETER_BRAND_TO_APP_FAMILY_MAPPING={
        'az': 'taximeter',
        'rida': 'rida',
        'turla': 'modus',
        'uber': 'uberdriver',
        'vezet': 'vezet',
        'yandex': 'taximeter',
        'yango': 'taximeter',
    },
)
@pytest.mark.parametrize(
    'brand, fleet_type',
    [
        (pro_app.Brand.YANDEX, 'taximeter'),
        (pro_app.Brand.AZERBAIJAN, 'taximeter'),
        (pro_app.Brand.YANGO, 'taximeter'),
        (pro_app.Brand.UBER, 'uberdriver'),
        (pro_app.Brand.RIDA, 'rida'),
        (pro_app.Brand.TURLA, 'modus'),
        (pro_app.Brand.VEZET, 'vezet'),
    ],
)
async def test_sf_park_gambling_fleet_types(
        web_context: context_module.Context,
        mock_hiring_conditions_choose,
        load_json,
        brand,
        fleet_type,
):
    # arrange
    request_params = load_json('request_params.json')[fleet_type]
    request_to_gambling = load_json('request_to_gambling.json')[fleet_type]
    gambling_response_status = 200
    gambling_response_body = load_json('gambling_response.json')['items']
    gambling_response = mock_hiring_conditions_choose(
        gambling_response_body, gambling_response_status,
    )

    # act
    result = await web_context.sf_park_gambling.get_driver_parks(
        city_doc=MOSCOW, brand=brand, **request_params,
    )

    # assert
    assert gambling_response.has_calls
    gambling_request = gambling_response.next_call()['request']
    assert gambling_request.method == 'POST'
    assert gambling_request.json == request_to_gambling

    assert repr(result) == repr(EXPECT_PARK_CHOICES)


async def test_sf_park_gambling_bad_city(
        web_context: context_module.Context,
        mock_hiring_conditions_choose,
        load_json,
):
    # arrange
    city = BAD_CITY
    fleet_type = 'taximeter'
    brand = pro_app.Brand.YANDEX
    request_params = load_json('request_params.json')[fleet_type]
    gambling_response_status = 200
    gambling_response_body = load_json('gambling_response.json')['items']
    gambling_response = mock_hiring_conditions_choose(
        gambling_response_body, gambling_response_status,
    )

    # act
    result = await web_context.sf_park_gambling.get_driver_parks(
        city_doc=city, brand=brand, **request_params,
    )

    assert not gambling_response.has_calls
    assert result == []
