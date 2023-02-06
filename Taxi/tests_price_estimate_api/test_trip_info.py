import json

from google.protobuf import json_format
from price_estimate_api import trip_info_pb2  # pylint: disable=E0401
import pytest

TRANSLATIONS = {
    'tariff': {
        'old_category_name.econom': {'en': 'Economy', 'ru': 'Эконом'},
        'old_category_name.business': {'en': 'Comfort', 'ru': 'Комфорт'},
        'old_category_name.comfortplus': {'en': 'Comfort+', 'ru': 'Комфорт+'},
        'old_category_name.vip': {'en': 'Business', 'ru': 'Бизнес'},
        'old_category_name.minivan': {'en': 'Minivan', 'ru': 'Минивэн'},
        'currency_with_sign.default': {
            'en': '$VALUE$ $SIGN$$CURRENCY$',
            'ru': '$VALUE$ $SIGN$$CURRENCY$',
        },
        'currency.rub': {'en': 'rub', 'ru': 'руб.'},
        'interval_description': {
            'en': 'from %(minimal_price)s',
            'ru': 'от %(minimal_price)s',
        },
        'round.tens_minutes': {
            'en': '%(value).0f min',
            'ru': '%(value).0f мин',
        },
    },
}


@pytest.fixture(name='trip_info_services')
def _trip_info_services(mockserver, load_binary, load_json):
    class Context:
        def __init__(self):
            self.locale = None

        def set_locale(self, locale):
            self.locale = locale

    context = Context()

    @mockserver.json_handler('/driver-eta/eta')
    def _mock_driver_eta(request):
        return load_json('eta_response_2.json')

    @mockserver.json_handler('/pricing-data-preparer/v2/prepare')
    def _mock_v2_prepare(request):
        assert 'Accept-Language' in request.headers
        assert (
            request.headers['Accept-Language'] == context.locale
            if context.locale
            else 'en'
        )

        input_json = json.loads(request.get_data())
        assert input_json.get('modifications_scope') == 'taxi'
        assert 'zone' in input_json and input_json['zone']
        requested_categories = input_json['categories']
        waypoints = len(input_json['waypoints'])
        if waypoints == 1:
            result = load_json('pricing_data_preparer_1.json')
        elif waypoints == 2:
            result = load_json('pricing_data_preparer_2.json')
        else:
            assert False
        # Leave only requested categories
        bad_categories = set()
        for category in result['categories']:
            if category not in requested_categories:
                bad_categories.add(category)
        for category in bad_categories:
            del result['categories'][category]
        return result

    @mockserver.json_handler('/yaga-adjust/adjust/position')
    def _mock_graph(request):
        data = json.loads(request.get_data())
        max_distance = data['max_distance']
        assert max_distance in (1000.0, 1.0)
        lon = data['longitude']
        lat = data['latitude']
        if max_distance == 1.0 and lon == 37 and lat == 56:
            return {'adjusted': []}
        return {
            'adjusted': [
                {'longitude': lon, 'latitude': lat, 'geo_distance': 100},
            ],
        }

    return context


@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize(
    'request_params,expected_result_json',
    [
        ('rll=37.589569560,55.733434780~37,56', 'response_two_points.json'),
        ('rll=37.589569560,55.733434780', 'response_one_point.json'),
        (
            'lang=en&rll=37.589569560,55.733434780~37,56',
            'response_two_points_en.json',
        ),
        (
            'lang=en&rll=37.589569560,55.733434780',
            'response_one_point_en.json',
        ),
    ],
)
async def test_trip_info_various_requests(
        taxi_price_estimate_api,
        trip_info_services,
        request_params,
        expected_result_json,
        load_json,
):
    expected_result = load_json(expected_result_json)
    response = await taxi_price_estimate_api.post(
        'trip_info?' + request_params, {},
    )
    assert response.status_code == 200
    data = response.json()
    assert data == expected_result


@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
async def test_trip_info_no_service(
        taxi_price_estimate_api, trip_info_services,
):
    response = await taxi_price_estimate_api.post(
        'trip_info?rll=30.0,60.0~30.01,60.01', {},
    )
    assert response.status_code == 200
    assert response.content == b''


@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
async def test_trip_info_multiple_classes(
        taxi_price_estimate_api, trip_info_services,
):
    response = await taxi_price_estimate_api.post(
        'trip_info?rll=37.589569560,55.733434780&class=econom,business', {},
    )
    assert response.status_code == 200
    assert response.content == b''


@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize(
    'request_params,expected_result',
    [('rll=37.589569560,55.733434780~37,56&class=bullshit', b'')],
)
async def test_trip_info_no_available_tariff(
        taxi_price_estimate_api,
        trip_info_services,
        request_params,
        expected_result,
):
    response = await taxi_price_estimate_api.post(
        'trip_info?' + request_params, {},
    )
    assert response.status_code == 200
    assert expected_result == response.content


@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize(
    'request_params,expected_result_json',
    [
        (
            'lang=en&rll=37.589569560,55.733434780~37,56',
            'response_one_point_bad_route.json',
        ),
    ],
)
@pytest.mark.config(ROUTEINFO_MAX_CALC_DISTANCE=10)
async def test_trip_info_long_points(
        taxi_price_estimate_api,
        trip_info_services,
        request_params,
        expected_result_json,
        load_json,
):
    expected_result = load_json(expected_result_json)
    response = await taxi_price_estimate_api.post(
        'trip_info?' + request_params, {},
    )
    assert response.status_code == 200
    data = response.json()
    assert data == expected_result


@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize(
    'request_params,expected_code,expected_response',
    [
        (
            'lang=en&rll=37.589569560,55.733434780~37,56',
            200,
            'response_one_point_bad_route.json',
        ),
        ('rll=37,56~37.589569560,55.733434780', 200, None),
    ],
)
@pytest.mark.config(ROUTEINFO_MAX_ROAD_DISTANCE=1)
async def test_trip_info_impossible_route(
        taxi_price_estimate_api,
        trip_info_services,
        request_params,
        expected_code,
        expected_response,
        load_json,
):
    response = await taxi_price_estimate_api.get(
        'trip_info?' + request_params, {},
    )
    assert response.status_code == expected_code
    if expected_response:
        assert response.json() == load_json(expected_response)
    else:
        assert response.content == b''


@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
async def test_trip_info_no_waiting_time(
        taxi_price_estimate_api, trip_info_services, load_json, mockserver,
):
    @mockserver.json_handler('/driver-eta/eta')
    def _mock_driver_eta(request):
        return load_json('eta_response_1.json')

    response = await taxi_price_estimate_api.post(
        'trip_info?rll=37.589569560,55.733434780&class=vip', {},
    )
    assert response.status_code == 200
    assert response.json() == load_json('response_no_waiting_time.json')


@pytest.mark.parametrize(
    'request_params,expected_response',
    [
        ('rll=37.589569560,55.733434780~37,56', 'response_two_points_pb.json'),
        ('rll=37.589569560,55.733434780', 'response_one_point_pb.json'),
    ],
)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
async def test_trip_info_protobuf_response(
        taxi_price_estimate_api,
        trip_info_services,
        load_json,
        expected_response,
        request_params,
):
    response = await taxi_price_estimate_api.post(
        'trip_info?' + request_params,
        {},
        headers={'Accept': 'application/x-protobuf'},
    )
    assert response.status_code == 200
    pb_response = trip_info_pb2.TripInfo()
    pb_response.ParseFromString(response.content)
    result = json_format.MessageToDict(pb_response)
    assert result == load_json(expected_response)


@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize('lang', [None, 'en', 'ru'])
async def test_trip_info_pass_locale(
        taxi_price_estimate_api, trip_info_services, lang, load_json,
):
    request_params = ''
    expected_result = load_json(
        'response_one_point{}.json'.format('_{}'.format(lang) if lang else ''),
    )
    if lang:
        request_params = 'lang={}'.format(lang)
        trip_info_services.set_locale(lang)
    response = await taxi_price_estimate_api.post(
        'trip_info?rll=37.589569560,55.733434780&' + request_params, {},
    )
    assert response.status_code == 200
    data = response.json()
    assert data == expected_result
