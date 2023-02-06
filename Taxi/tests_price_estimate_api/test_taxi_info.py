import json

from google.protobuf import json_format
from price_estimate_api import taxi_info_pb2  # pylint: disable=E0401
import pytest

TRANSLATIONS = {
    'tariff': {
        'old_category_name.econom': {'en': 'Economy', 'ru': 'Эконом'},
        'old_category_name.business': {'en': 'Comfort', 'ru': 'Комфорт'},
        'old_category_name.comfortplus': {'en': 'Comfort+', 'ru': 'Комфорт+'},
        'old_category_name.vip': {'en': 'Business', 'ru': 'Бизнес'},
        'old_category_name.minivan': {'en': 'Minivan', 'ru': 'Минивэн'},
        'old_category_name.shuttle': {'en': 'Shuttle', 'ru': 'Шаттл'},
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


@pytest.fixture(name='taxi_info_services')
def _taxi_info_services(mockserver, load_binary, load_json):
    class Context:
        def __init__(self):
            self.locale = None
            self.pdp_no_trip_information = False

        def set_locale(self, locale):
            self.locale = locale

        def set_pdp_no_trip_information(self):
            self.pdp_no_trip_information = True

    context = Context()

    @mockserver.json_handler('/driver-eta/eta')
    def _mock_driver_eta(request):
        input_json = json.loads(request.get_data())
        if len(input_json['classes']) == 2:
            return load_json('eta_response_1.json')
        if len(input_json['classes']) != 5:
            return {'classes': []}
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
        if context.pdp_no_trip_information:
            for category in result['categories'].values():
                del category['user']['trip_information']
                del category['driver']['trip_information']
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

    @mockserver.json_handler(
        '/shuttle-control/internal/shuttle-control/v1/trip-planner/search',
    )
    def _mock_shuttle_control(request):
        return load_json('shuttle_control_response.json')

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
        (
            'rll=37.589569560,55.733434780~37,56'
            '&class=econom,business,comfortplus,minivan,vip',
            'response_multiple_classes.json',
        ),
        (
            'rll=37.589569560,55.733434780~37,56&class=econom,business',
            'response_two_classes.json',
        ),
    ],
)
async def test_taxi_info_various_requests(
        taxi_price_estimate_api,
        taxi_info_services,
        request_params,
        expected_result_json,
        load_json,
        uapi_keys_auth,
):
    expected_result = load_json(expected_result_json)
    response = await taxi_price_estimate_api.post(
        'taxi_info?clid=test3&apikey=qwerty3&' + request_params, {},
    )
    assert response.status_code == 200
    data = response.json()
    assert data == expected_result
    assert uapi_keys_auth.has_calls


@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
async def test_taxi_info_no_service(
        taxi_price_estimate_api, taxi_info_services, uapi_keys_auth,
):
    response = await taxi_price_estimate_api.post(
        'taxi_info?clid=test3&apikey=qwerty3&rll=30.0,60.0~30.01,60.01', {},
    )
    assert response.status_code == 204
    assert uapi_keys_auth.has_calls


@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize(
    'request_params,expected_result',
    [('rll=37.589569560,55.733434780~37,56&class=bullshit', b'')],
)
async def test_taxi_info_no_available_tariff(
        taxi_price_estimate_api,
        taxi_info_services,
        request_params,
        expected_result,
        uapi_keys_auth,
):
    response = await taxi_price_estimate_api.post(
        'taxi_info?clid=test3&apikey=qwerty3&' + request_params, {},
    )
    assert response.status_code == 200
    assert expected_result == response.content
    assert uapi_keys_auth.has_calls


@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize(
    'request_params,expected_result_json',
    [
        (
            'lang=en&rll=37.589569560,55.733434780~37,56',
            'response_one_point_en.json',
        ),
    ],
)
@pytest.mark.config(ROUTEINFO_MAX_CALC_DISTANCE=10)
async def test_taxi_info_long_points(
        taxi_price_estimate_api,
        taxi_info_services,
        request_params,
        expected_result_json,
        load_json,
        uapi_keys_auth,
):
    expected_result = load_json(expected_result_json)
    response = await taxi_price_estimate_api.post(
        'taxi_info?clid=test3&apikey=qwerty3&' + request_params, {},
    )
    assert response.status_code == 200
    data = response.json()
    assert data == expected_result
    assert uapi_keys_auth.has_calls


@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize(
    'request_params,expected_code,expected_response',
    [
        (
            'rll=37.589569560,55.733434780~37,56',
            200,
            'response_one_point.json',
        ),
        ('rll=37,56~37.589569560,55.733434780', 204, None),
    ],
)
@pytest.mark.parametrize('pdp_no_trip_information', [True, False])
@pytest.mark.config(ROUTEINFO_MAX_ROAD_DISTANCE=1)
async def test_taxi_info_impossible_route(
        taxi_price_estimate_api,
        taxi_info_services,
        request_params,
        expected_code,
        expected_response,
        load_json,
        pdp_no_trip_information,
        uapi_keys_auth,
):
    if pdp_no_trip_information:
        taxi_info_services.set_pdp_no_trip_information()
    response = await taxi_price_estimate_api.get(
        'taxi_info?clid=test3&apikey=qwerty3&' + request_params, {},
    )
    assert response.status_code == expected_code
    if expected_response:
        assert response.json() == load_json(expected_response)
    assert uapi_keys_auth.has_calls


@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize(
    'classes,status', [('uberx', 204), ('econom', 200), ('uberx,econom', 400)],
)
async def test_taxi_info_uber_tariffs(
        taxi_price_estimate_api,
        taxi_info_services,
        classes,
        status,
        uapi_keys_auth,
):
    response = await taxi_price_estimate_api.post(
        'taxi_info?clid=test3&apikey=qwerty3'
        '&rll=37.589569560,55.733434780~37,56'
        '&class=' + classes,
        {},
    )
    assert response.status_code == status
    assert uapi_keys_auth.has_calls


@pytest.mark.parametrize(
    'request_params,expected_response',
    [
        (
            'rll=37.589569560,55.733434780~37,56'
            '&class=econom,business,comfortplus,minivan,vip',
            'response_multiple_classes_pb.json',
        ),
        ('rll=37.589569560,55.733434780~37,56', 'response_two_points_pb.json'),
        ('rll=37.589569560,55.733434780', 'response_one_point_pb.json'),
    ],
)
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
async def test_taxi_info_protobuf_response(
        taxi_price_estimate_api,
        taxi_info_services,
        load_json,
        expected_response,
        request_params,
        uapi_keys_auth,
):
    response = await taxi_price_estimate_api.post(
        'taxi_info?clid=test3&apikey=qwerty3&' + request_params,
        {},
        headers={'Accept': 'application/x-protobuf'},
    )
    assert response.status_code == 200
    pb_response = taxi_info_pb2.TaxiInfo()
    pb_response.ParseFromString(response.content)
    result = json_format.MessageToDict(pb_response)
    assert result == load_json(expected_response)
    assert uapi_keys_auth.has_calls


@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
async def test_taxi_info_bad_auth(
        taxi_price_estimate_api, taxi_info_services, uapi_keys_auth,
):
    response = await taxi_price_estimate_api.get(
        'taxi_info?clid=test3&apikey=badkey&rll=37.589569560,55.733434780', {},
    )
    assert response.status_code == 403
    assert response.json() == {'error': {'text': 'Bad clid or apikey'}}
    assert uapi_keys_auth.has_calls


@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize('lang', [None, 'en', 'ru'])
async def test_taxi_info_pass_locale(
        taxi_price_estimate_api,
        taxi_info_services,
        lang,
        load_json,
        uapi_keys_auth,
):
    request_params = ''
    expected_result = load_json(
        'response_one_point{}.json'.format('_{}'.format(lang) if lang else ''),
    )
    if lang:
        request_params = 'lang={}'.format(lang)
        taxi_info_services.set_locale(lang)
    response = await taxi_price_estimate_api.post(
        'taxi_info?clid=test3&apikey=qwerty3&rll=37.589569560,55.733434780&'
        + request_params,
        {},
    )
    assert response.status_code == 200
    data = response.json()
    assert data == expected_result
    assert uapi_keys_auth.has_calls


@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.tariff_settings(filename='tariff_settings_shuttle.json')
@pytest.mark.config(
    APPLICATION_BRAND_CATEGORIES_SETS={'__default__': ['shuttle', 'econom']},
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={
        'shuttle': {
            'android': {'version': [4, 31, 0]},
            'iphone': {'version': [600, 38, 0]},
            '2gis': {'version': [0, 0, 0]},
        },
    },
)
@pytest.mark.parametrize(
    'classes, clid, two_points, expected_response',
    [
        pytest.param(
            'shuttle',
            '2gis',
            True,
            'response_shuttle.json',
            id='shuttle, 2gis, two points',
        ),
        pytest.param(
            'shuttle',
            'random_clid',
            True,
            None,
            id='shuttle, not 2gis, two points',
        ),
        pytest.param(
            'shuttle', '2gis', False, None, id='shuttle, 2gis, one point',
        ),
        pytest.param(
            'shuttle,econom',
            '2gis',
            True,
            'response_shuttle_econom.json',
            id='shuttle+econom, 2gis, two points',
        ),
    ],
)
async def test_taxi_info_shuttle(
        classes,
        clid,
        two_points,
        expected_response,
        taxi_price_estimate_api,
        load_json,
        uapi_keys_auth,
        taxi_info_services,
):
    request_params = (
        f'clid={clid}'
        f'&apikey=qwerty3'
        f'&rll=37.589569560,55.733434780{"~37,56" if two_points else ""}'
        f'&class={classes}'
    )

    response = await taxi_price_estimate_api.post(
        'taxi_info?' + request_params, {},
    )

    assert response.status_code == 200
    if expected_response:
        assert response.content != b''
        data = response.json()
        assert data == load_json(expected_response)
    else:
        assert response.content == b''

    assert uapi_keys_auth.has_calls
