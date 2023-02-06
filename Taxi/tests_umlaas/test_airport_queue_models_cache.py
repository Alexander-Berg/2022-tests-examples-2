import datetime

import pytest

_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

_ATLAS_DETAILED_DATA_RESPONSE = {
    'meta': {
        'columns_description': [
            {'name': 'ts', 'type_name': 'UInt32'},
            {'name': 'car_class', 'type_name': 'String'},
            {'name': 'source_geoarea', 'type_name': 'String'},
            {'name': 'requests_count', 'type_name': 'UInt64'},
            {'name': 'trips_count', 'type_name': 'UInt64'},
        ],
        'data_increment_mark': '2020-11-12T10:52:45+03:00',
    },
    'data': [
        {
            'ts': 1603974600,
            'car_class': 'comfortplus',
            'source_geoarea': 'vko',
            'requests_count': 3,
            'trips_count': 0,
        },
        {
            'ts': 1603974601,
            'car_class': 'econom',
            'source_geoarea': 'vko',
            'requests_count': 3,
            'trips_count': 1,
        },
        {
            'ts': 1603974602,
            'car_class': 'comfortplus',
            'source_geoarea': 'yerevan_airport',
            'requests_count': 5,
            'trips_count': 2,
        },
        {
            'ts': 1603974603,
            'car_class': 'comfort',
            'source_geoarea': 'yerevan_airport',
            'requests_count': 10,
            'trips_count': 3,
        },
    ],
}

_EXPECTED_CAPACITIES = {'Bombardier CRJ200': 52, 'Boeing 737-700C': 0}

_DEFAULT_CAPACITY = 160


@pytest.fixture(name='mock_atlas_data_access_default')
def _mock_atlas_data_access_default(mockserver):
    @mockserver.json_handler('/atlas-backend/v1/data-access/detailed')
    def handler(request):
        return {'data': [], 'meta': {'columns_description': []}}

    return handler


def parse_datetime(datetime_str):
    return datetime.datetime.strptime(datetime_str, _DATETIME_FORMAT)


@pytest.mark.config(
    DISPATCH_AIRPORT_ML_SETTINGS={
        'vko': {
            'ml_visible_classes': [
                'econom',
                'business',
                'comfortplus',
                'vip',
                'ultimate',
                'minivan',
                'child_tariff',
                'maybach',
                'premium_van',
            ],
        },
        'yerevan_airport': {
            'ml_visible_classes': [
                'start',
                'standart',
                'vip',
                'minivan',
                'child_tariff',
                'comfortplus',
            ],
        },
    },
    UMLAAS_QUEUE_MODEL_CACHE_UPDATE_ENABLED=True,
    UMLAAS_QUEUE_MODEL_CACHE_ORDERS_COUNT_ENABLED=True,
    UMLAAS_QUEUE_MODEL_CACHE_ORDERS_COUNT_INTERVAL={
        'length': 30,
        'offset': 10,
    },
    UMLAAS_AIRPORT_QUEUE_TARIFF_MAPPING=[
        {'model_tariff': 'econom', 'atlas_tariffs': ['econom']},
        {
            'model_tariff': 'comfortplus',
            'atlas_tariffs': ['comfort', 'comfortplus'],
        },
    ],
    UMLAAS_AIRPORT_QUEUE_RESOURCES=[{'name': 'model', 'resource_name': '0'}],
)
async def test_airport_queue_models_cache(
        mock_atlas_data_access_default, taxi_umlaas, mockserver, testpoint,
):
    @testpoint('airport_queue_models_cache_update_now')
    def cache_update_now_testpoint(now):
        return now

    @testpoint('airport_queue_models_cache_ml_request')
    def ml_request_testpoint(ml_request):
        return ml_request

    @mockserver.json_handler('/atlas-backend/v1/data-access/detailed')
    async def mock_atlas_data_access(request):
        update_now = await cache_update_now_testpoint.wait_call()
        update_now = update_now['now']

        assert request.json['metric_id'] == 'airport_orders_aggregate'
        parameters = request.json['parameters']
        source_geoareas = parameters['source_geoareas']
        assert sorted(source_geoareas) == ['vko', 'yerevan_airport']
        assert (
            parameters['ts']['from'] == update_now - 40 * 60
        )  # 40 minutes = length + offset
        assert (
            parameters['ts']['to'] == update_now - 10 * 60
        )  # 10 minutes = offset
        return _ATLAS_DETAILED_DATA_RESPONSE

    await taxi_umlaas.enable_testpoints()
    await mock_atlas_data_access.wait_call()

    assert ml_request_testpoint.times_called == 1
    ml_request = ml_request_testpoint.next_call()['ml_request']
    assert parse_datetime(
        ml_request['last_order_time_point'],
    ) == parse_datetime('2020-11-12T10:52:45+03:00')
    assert (
        {
            (item['airport_zone'], item['tariff_class'])
            for item in ml_request['items']
        }
        == {
            ('vko', 'econom'),
            ('vko', 'comfortplus'),
            ('yerevan_airport', 'comfortplus'),
        }
    )
    for item in ml_request['items']:
        assert len(item['orders']) == 30
        assert all(val == 0 for val in item['orders'])
        assert len(item['success_orders']) == 30
        assert all(val == 0 for val in item['success_orders'])


@pytest.mark.now('2022-03-30T12:00:00Z')
@pytest.mark.config(
    DISPATCH_AIRPORT_ML_SETTINGS={
        'vko': {
            'ml_visible_classes': [
                'econom',
                'business',
                'comfortplus',
                'vip',
                'ultimate',
                'minivan',
                'child_tariff',
                'maybach',
                'premium_van',
            ],
            'iata_code': 'vko',
            'enable_timetable': True,
            'timezone': 'Europe/Moscow',
        },
        'ekb_airport': {
            'ml_visible_classes': [
                'start',
                'standart',
                'vip',
                'minivan',
                'child_tariff',
                'comfortplus',
            ],
            'iata_code': 'ekb',
            'enable_timetable': True,
            'timezone': 'Asia/Yekaterinburg',
        },
    },
    UMLAAS_QUEUE_MODEL_CACHE_UPDATE_ENABLED=True,
    UMLAAS_QUEUE_MODEL_CACHE_ORDERS_COUNT_ENABLED=False,
)
async def test_avia_timetable(taxi_umlaas, mockserver, testpoint, load_json):
    @testpoint('airport_queue_models_avia_timetable')
    def avia_timetable_testpoint(avia_timetable):
        return avia_timetable

    @mockserver.json_handler('/avia/v1/airport/vko/flight/')
    async def mock_yandex_avia_vko_timetable(request):
        return load_json('avia_vko_response.json')

    @mockserver.json_handler('/avia/v1/airport/ekb/flight/')
    async def mock_yandex_avia_ekb_timetable(request):
        return load_json('avia_ekb_response.json')

    await taxi_umlaas.enable_testpoints()

    await mock_yandex_avia_vko_timetable.wait_call()
    await mock_yandex_avia_ekb_timetable.wait_call()

    result = (await avia_timetable_testpoint.wait_call())['avia_timetable']
    result['ekb_airport'].sort(key=lambda x: x['number'])
    result['vko'].sort(key=lambda x: x['number'])
    assert result == {
        'ekb_airport': load_json('avia_ekb_etalon.json'),
        'vko': load_json('avia_vko_etalon.json'),
    }


@pytest.mark.now('2022-03-30T12:00:00Z')
@pytest.mark.config(
    DISPATCH_AIRPORT_ML_SETTINGS={
        'vko': {
            'ml_visible_classes': ['econom'],
            'iata_code': 'vko',
            'enable_timetable': True,
            'timezone': 'Europe/Moscow',
        },
    },
    UMLAAS_AIRPORT_QUEUE_TARIFF_MAPPING=[
        {'model_tariff': 'econom', 'atlas_tariffs': ['econom']},
        {
            'model_tariff': 'comfortplus',
            'atlas_tariffs': ['comfort', 'comfortplus'],
        },
    ],
    UMLAAS_AIRCRAFT_CAPACITIES={
        'Bombardier CRJ200': 52,
        '__default__': _DEFAULT_CAPACITY,
    },
    UMLAAS_QUEUE_MODEL_CACHE_UPDATE_ENABLED=True,
    UMLAAS_QUEUE_MODEL_CACHE_ORDERS_COUNT_ENABLED=False,
)
async def test_arrivals(taxi_umlaas, mockserver, testpoint, load_json):
    @testpoint('airport_queue_models_cache_update_now')
    def cache_update_now_testpoint(now):
        return now

    @testpoint('airport_queue_models_cache_ml_request')
    def ml_request_testpoint(ml_request):
        return ml_request

    @mockserver.json_handler('/avia/v1/airport/vko/flight/')
    async def mock_yandex_avia_vko_timetable(request):
        return load_json('avia_vko_response.json')

    await taxi_umlaas.enable_testpoints()
    await cache_update_now_testpoint.wait_call()
    await mock_yandex_avia_vko_timetable.wait_call()

    assert ml_request_testpoint.times_called == 1
    ml_request = ml_request_testpoint.next_call()['ml_request']

    assert len(ml_request['items']) == 1
    ml_request_item = ml_request['items'][0]

    assert ml_request_item['airport_zone'] == 'vko'
    assert len(ml_request_item['arrivals']) == 4
    for flight in ml_request_item['arrivals']:
        assert flight['capacity'] == _EXPECTED_CAPACITIES.get(
            flight['aircraft'], _DEFAULT_CAPACITY,
        )


@pytest.mark.now('2022-03-30T12:00:00Z')
@pytest.mark.config(
    DISPATCH_AIRPORT_ML_SETTINGS={
        'vko': {
            'ml_visible_classes': ['econom', 'comfortplus'],
            'iata_code': 'vko',
            'enable_timetable': True,
            'timezone': 'Europe/Moscow',
        },
    },
    UMLAAS_AIRPORT_QUEUE_TARIFF_MAPPING=[
        {'model_tariff': 'econom', 'atlas_tariffs': ['econom']},
        {
            'model_tariff': 'comfortplus',
            'atlas_tariffs': ['comfort', 'comfortplus'],
        },
    ],
    UMLAAS_AIRCRAFT_CAPACITIES={
        'Bombardier CRJ200': 52,
        '__default__': _DEFAULT_CAPACITY,
    },
    UMLAAS_QUEUE_MODEL_CACHE_UPDATE_ENABLED=True,
    UMLAAS_QUEUE_MODEL_CACHE_ORDERS_COUNT_ENABLED=False,
    UMLAAS_AIRPORT_QUEUE_RESOURCES=[
        {'name': 'model_with_linear_corrections', 'resource_name': '1'},
    ],
)
@pytest.mark.experiments3(
    filename='umlaas_airport_queue_predictor_params.json',
)
async def test_linear_corrections(
        taxi_umlaas, mockserver, testpoint, load_json,
):
    @testpoint('airport_queue_models_cache_update_now')
    def cache_update_now_testpoint(now):
        return now

    @mockserver.json_handler('/avia/v1/airport/vko/flight/')
    async def mock_yandex_avia_vko_timetable(request):
        return load_json('avia_vko_response.json')

    @testpoint('airport_queue_models_cache_ml_responses')
    def ml_responses_testpoint(ml_responses):
        return ml_responses

    await taxi_umlaas.enable_testpoints()
    await cache_update_now_testpoint.wait_call()
    await mock_yandex_avia_vko_timetable.wait_call()

    assert ml_responses_testpoint.times_called == 1
    ml_responses = ml_responses_testpoint.next_call()['ml_responses']

    assert 'model_with_linear_corrections' in ml_responses
    for item in ml_responses['model_with_linear_corrections']['items']:
        assert item['airport_zone'] == 'vko'
        if item['tariff_class'] == 'econom':
            assert item['prediction'] / item['time_interval'] == 186
        elif item['tariff_class'] == 'comfortplus':
            assert item['prediction'] / item['time_interval'] == 0.372
        else:
            assert item['prediction'] == 0
