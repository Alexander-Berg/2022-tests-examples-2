import pytest

TARIFF_DESCRIPTIONS = {
    'express': {
        'title_key': {'__default__': 'tariff.express.title'},
        'text_key': {'__default__': 'tariff.express.text'},
    },
    'cargo': {
        'title_key': {'__default__': 'tariff.cargo.title'},
        'text_key': {'__default__': 'tariff.cargo.text'},
    },
}

CORP_CLIENT_ID = 'corp_client_id_12312312312312312'

HEADERS = {
    'Accept-Language': 'ru',
    'X-B2B-Client-Id': CORP_CLIENT_ID,
    'X-Cargo-Api-Prefix': '/b2b/cargo/integration/',
}

AVAILABLE_INTERVALS = {
    'available_intervals': [
        {
            'from': '2022-02-19T19:10:00+00:00',
            'to': '2022-02-19T22:00:00+00:00',
        },
        {
            'from': '2022-02-20T02:10:00+00:00',
            'to': '2022-02-20T06:00:00+00:00',
        },
    ],
}

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.translations(
        cargo={
            'tariff.express.title': {'ru': 'Экспресс'},
            'tariff.express.text': {'ru': 'Тариф экспресс'},
            'tariff.cargo.title': {'ru': 'Грузовой'},
            'tariff.cargo.text': {'ru': 'Тариф грузовой'},
        },
    ),
]


@pytest.fixture(name='request_api_integration_v1_delivery_services')
def _request_api_integration_v1_tariffs(taxi_cargo_matcher):
    async def wrapper(headers=None, request=None):
        headers = headers if headers else HEADERS
        request = request if request else {'start_point': [37.1, 55.1]}
        response = await taxi_cargo_matcher.post(
            '/api/integration/v1/delivery-methods',
            headers=headers,
            json=request,
        )
        return response

    return wrapper


@pytest.mark.config(
    CARGO_MATCHER_TARIFF_DESCRIPTIONS_BY_COUNTRY=TARIFF_DESCRIPTIONS,
    CARGO_SDD_TAXI_TARIFF_SETTINGS={
        'remove_in_tariffs': True,
        'remove_in_admin_tariffs': False,
        'name': 'cargo',
    },
)
async def test_happy_path(
        request_api_integration_v1_delivery_services,
        mockserver,
        exp3_same_day,
):
    await exp3_same_day(corp_id=CORP_CLIENT_ID)

    @mockserver.json_handler(
        '/cargo-sdd/api/integration/v1/same-day/delivery-intervals',
    )
    def _intervals(request):
        assert request.json['corp_client_id'] == CORP_CLIENT_ID
        assert request.json['route_points'][0] == {
            'coordinates': {'lon': 37.1, 'lat': 55.1},
        }

        return AVAILABLE_INTERVALS

    response = await request_api_integration_v1_delivery_services()

    assert response.status_code == 200

    express_delivery = response.json()['express_delivery']
    assert express_delivery['allowed']
    tariffs = express_delivery['available_tariffs']
    assert len(tariffs) == 1
    available_tariff = tariffs[0]
    assert available_tariff['name'] == 'express'
    assert available_tariff['title'] == 'Экспресс'
    assert available_tariff['text'] == 'Тариф экспресс'

    same_day_delivery = response.json()['same_day_delivery']
    assert same_day_delivery['allowed']
    assert (
        same_day_delivery['available_intervals']
        == AVAILABLE_INTERVALS['available_intervals']
    )


async def test_empty_coordinates_and_address(taxi_cargo_matcher):
    response = await taxi_cargo_matcher.post(
        '/api/integration/v1/delivery-methods', headers=HEADERS, json={},
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'bad_request',
        'message': 'Необходимо передать координаты или топоним точки',
    }


async def test_undefined_address(
        request_api_integration_v1_delivery_services, yamaps,
):
    response = await request_api_integration_v1_delivery_services(
        request={'fullname': 'abracadabra'},
    )
    assert response.status_code == 400
    assert (
        response.json()['message']
        == 'Не удалось преобразовать адрес abracadabra в координаты: '
        'проверьте корректность адреса или попробуйте'
        ' указать координаты вручную'
    )


@pytest.mark.config(
    CARGO_SDD_TAXI_TARIFF_SETTINGS={
        'remove_in_tariffs': True,
        'remove_in_admin_tariffs': False,
        'name': 'cargo',
    },
)
async def test_run_geocoder(
        mockserver,
        yamaps,
        load_json,
        exp3_same_day,
        request_api_integration_v1_delivery_services,
):
    await exp3_same_day(corp_id=CORP_CLIENT_ID)

    @mockserver.json_handler(
        '/cargo-sdd/api/integration/v1/same-day/delivery-intervals',
    )
    def _intervals(request):
        assert (
            request.json['route_points'][0]['coordinates']['lon']
            == coordinates[0]
        )
        assert (
            request.json['route_points'][0]['coordinates']['lat']
            == coordinates[1]
        )
        return AVAILABLE_INTERVALS

    yamaps_response = load_json('yamaps_response.json')
    coordinates = yamaps_response['geometry']

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects_callback(req):
        return [yamaps_response]

    response = await request_api_integration_v1_delivery_services(
        request={'fullname': 'fullname'},
    )

    assert response.status_code == 200
    assert _intervals.times_called == 1
