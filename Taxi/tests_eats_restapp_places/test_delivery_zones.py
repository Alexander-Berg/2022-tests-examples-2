# pylint: disable=import-error

import json

import pytest
import yandex.maps.proto.driving.summary_pb2 as ProtoDrivingSummary
import yandex.maps.proto.masstransit.summary_pb2 as ProtoMasstransitSummary


PARTNER_ID = 1
PLACE_ID = 42

DEFAULT_TIME = 50
DEFAULT_DISTANCE = 100

DEFAULT_HEADERS = {
    'X-YaEda-PartnerId': str(PARTNER_ID),
    'Content-type': 'application/json',
}

HANDLE_URL = '/4.0/restapp-front/places/v2/delivery-zones?place_id={}'

REQ = {
    'delivery_zones': {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [[[55, 56], [57, 58], [59, 60], [60, 61]]],
                },
                'properties': {
                    'id': 2334,
                    'name': 'fff',
                    'enabled': True,
                    'average_delivery_time': 45,
                    'delivery_condition': {
                        'thresholds': [{'order_price': 0, 'delivery_cost': 0}],
                    },
                },
            },
        ],
    },
}


INCORRECT_TIME_REQ = {
    'delivery_zones': {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [[[55, 56], [57, 58], [59, 60], [60, 61]]],
                },
                'properties': {
                    'id': 2334,
                    'name': 'fff',
                    'enabled': True,
                    'average_delivery_time': 600,
                    'delivery_condition': {
                        'thresholds': [{'order_price': 0, 'delivery_cost': 0}],
                    },
                },
            },
        ],
    },
}


@pytest.fixture(name='mock_eats_core_delivery_zones', autouse=True)
def _mock_eats_core_delivery_zones(mockserver, request, load_json):
    eats_core_error = request.node.get_closest_marker('eats_core_error')

    @mockserver.json_handler('/eats-core/v1/places/delivery-zones')
    def _mock_core(request):
        if request.method == 'GET':
            return mockserver.make_response(
                status=200,
                json=load_json(
                    'eats_core/delivery_zones/mock_get_response.json',
                ),
            )

        assert (
            request.json['delivery_zones']['features'][0]['properties'][
                'average_delivery_time'
            ]
            == 45
        )

        if eats_core_error and 'message' in eats_core_error.kwargs:
            return mockserver.make_response(
                status=400,
                json={
                    'code': '400',
                    'message': eats_core_error.kwargs['message'],
                },
            )

        return mockserver.make_response(
            status=200,
            json=load_json('eats_core/delivery_zones/mock_post_response.json'),
        )


@pytest.fixture(name='mock_maps_router_summary', autouse=True)
def _mock_maps_router_summary(mockserver, request):
    route = request.node.get_closest_marker('route')
    if route:
        time = route.kwargs['time']
        distance = route.kwargs['distance']
    else:
        time = DEFAULT_TIME
        distance = DEFAULT_DISTANCE

    @mockserver.handler('/maps-router/v2/summary')
    def _mock_router(request):
        return mockserver.make_response(
            response=_proto_driving_summary(time, distance),
            status=200,
            content_type='application/x-protobuf',
        )


def _proto_driving_summary(time, distance):
    response = ProtoDrivingSummary.Summaries()
    item = response.summaries.add()
    item.weight.time.value = time
    item.weight.time.text = ''
    item.weight.time_with_traffic.value = time
    item.weight.time_with_traffic.text = ''
    item.weight.distance.value = distance
    item.weight.distance.text = ''
    item.flags.blocked = False
    return response.SerializeToString()


def _proto_masstransit_summary(time, distance):
    response = ProtoMasstransitSummary.Summaries()
    item = response.summaries.add()
    item.weight.time.value = time
    item.weight.time.text = ''
    item.weight.walking_distance.value = distance
    item.weight.walking_distance.text = ''
    item.weight.transfers_count = 1
    return response.SerializeToString()


@pytest.mark.experiments3(filename='places_settings.json')
async def test_delivery_zone_success(
        taxi_eats_restapp_places,
        mock_maps_router_summary,
        mock_eats_core_delivery_zones,
        mock_restapp_authorizer,
        mockserver,
):
    @mockserver.handler('/maps-pedestrian-router/pedestrian/v2/summary')
    def _mock_pedestrian_router(request):
        return mockserver.make_response(
            response=_proto_masstransit_summary(2500, 10500),
            status=200,
            content_type='application/x-protobuf',
        )

    response = await taxi_eats_restapp_places.post(
        HANDLE_URL.format(PLACE_ID),
        headers=DEFAULT_HEADERS,
        data=json.dumps(REQ),
    )

    assert response.status_code == 200


@pytest.mark.experiments3(filename='places_settings.json')
@pytest.mark.config(ROUTER_SELECT=[{'routers': ['yamaps']}])
async def test_router_crashed(
        taxi_eats_restapp_places,
        mock_eats_core_delivery_zones,
        mock_restapp_authorizer,
        mockserver,
):
    @mockserver.handler('/maps-router/v2/summary')
    def _mock_router(request):
        raise mockserver.NetworkError()

    response = await taxi_eats_restapp_places.post(
        HANDLE_URL.format(PLACE_ID),
        headers=DEFAULT_HEADERS,
        data=json.dumps(REQ),
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': (
            'Не удалось сохранить зону. '
            'Попробуйте обновить страницу и сохранить зону снова. '
            'Если ошибка остаётся, повторите позже.'
        ),
    }


@pytest.mark.experiments3(filename='places_settings.json')
async def test_places_delivery_zone_incorrect_time(
        taxi_eats_restapp_places,
        mock_eats_core_delivery_zones,
        mock_restapp_authorizer,
):
    response = await taxi_eats_restapp_places.post(
        HANDLE_URL.format(PLACE_ID),
        headers=DEFAULT_HEADERS,
        data=json.dumps(INCORRECT_TIME_REQ),
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'invalid_time',
        'message': 'Время доставки должно быть от 30 до 300 минут',
    }


@pytest.mark.experiments3(filename='places_settings_big_max_time.json')
@pytest.mark.route(time=50000, distance=100)
async def test_places_delivery_zone_time_validation_error(
        taxi_eats_restapp_places,
        mock_maps_router_summary,
        mock_eats_core_delivery_zones,
        mock_restapp_authorizer,
):
    response = await taxi_eats_restapp_places.post(
        HANDLE_URL.format(PLACE_ID),
        headers=DEFAULT_HEADERS,
        data=json.dumps(REQ),
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'invalid_time',
        'message': 'Зона большая: введите время от 850 до 1400 минут',
    }


@pytest.mark.experiments3(filename='places_settings_skip_map_check.json')
@pytest.mark.route(time=50000, distance=100)
async def test_places_delivery_zone_skip_map_check(
        taxi_eats_restapp_places,
        mock_maps_router_summary,
        mock_eats_core_delivery_zones,
        mock_restapp_authorizer,
):
    response = await taxi_eats_restapp_places.post(
        HANDLE_URL.format(PLACE_ID),
        headers=DEFAULT_HEADERS,
        data=json.dumps(REQ),
    )

    assert response.status_code == 200


@pytest.mark.experiments3(filename='places_settings.json')
@pytest.mark.route(time=50000, distance=100)
async def test_places_delivery_zone_time_validation_skip_error(
        taxi_eats_restapp_places,
        mock_maps_router_summary,
        mock_eats_core_delivery_zones,
        mock_restapp_authorizer,
):
    response = await taxi_eats_restapp_places.post(
        HANDLE_URL.format(PLACE_ID),
        headers=DEFAULT_HEADERS,
        data=json.dumps(REQ),
    )

    assert response.status_code == 200


@pytest.mark.experiments3(filename='places_settings_dont_skip.json')
@pytest.mark.route(time=50000, distance=100)
async def test_places_delivery_zone_time_dont_skip_validation_skip_error(
        taxi_eats_restapp_places,
        mock_maps_router_summary,
        mock_eats_core_delivery_zones,
        mock_restapp_authorizer,
):
    response = await taxi_eats_restapp_places.post(
        HANDLE_URL.format(PLACE_ID),
        headers=DEFAULT_HEADERS,
        data=json.dumps(REQ),
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'invalid_time',
        'message': (
            'Доставка на этой зоне > 300 мин. '
            'Пожалуйста, проверьте адрес ресторана и '
            'корректность зоны.'
        ),
    }


@pytest.mark.experiments3(filename='places_settings.json')
async def test_places_delivery_zone_403_on_authorizer_403(
        taxi_eats_restapp_places, mock_restapp_authorizer_403,
):
    response = await taxi_eats_restapp_places.post(
        HANDLE_URL.format(PLACE_ID),
        headers=DEFAULT_HEADERS,
        data=json.dumps(REQ),
    )

    assert response.status_code == 403
    assert response.json() == {
        'code': '403',
        'message': (
            'Не удалось сохранить зону. '
            'Попробуйте обновить страницу и сохранить зону снова. '
            'Если ошибка остаётся, повторите позже.'
        ),
    }


@pytest.mark.experiments3(filename='places_settings.json')
async def test_places_delivery_zone_400_on_core_400(
        taxi_eats_restapp_places, mock_eats_core_400, mock_restapp_authorizer,
):
    response = await taxi_eats_restapp_places.post(
        HANDLE_URL.format(PLACE_ID),
        headers=DEFAULT_HEADERS,
        data=json.dumps(REQ),
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': (
            'Не удалось сохранить зону. '
            'Попробуйте обновить страницу и сохранить зону снова. '
            'Если ошибка остаётся, повторите позже.'
        ),
    }


@pytest.mark.experiments3(filename='places_settings.json')
async def test_places_delivery_zone_404_on_core_404(
        taxi_eats_restapp_places, mock_eats_core_404, mock_restapp_authorizer,
):
    response = await taxi_eats_restapp_places.post(
        HANDLE_URL.format(PLACE_ID),
        headers=DEFAULT_HEADERS,
        data=json.dumps(REQ),
    )

    assert response.status_code == 404
    assert response.json() == {'code': '404', 'message': 'Зона не найдена'}


@pytest.mark.experiments3(filename='places_settings.json')
async def test_delivery_zone_success_get(
        taxi_eats_restapp_places,
        mock_eats_core_delivery_zones,
        mock_restapp_authorizer,
):
    response = await taxi_eats_restapp_places.get(
        HANDLE_URL.format(PLACE_ID), headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 200


@pytest.mark.experiments3(filename='places_settings.json')
async def test_places_delivery_zone_403_on_authorizer_403_get(
        taxi_eats_restapp_places, mock_restapp_authorizer_403,
):
    response = await taxi_eats_restapp_places.get(
        HANDLE_URL.format(PLACE_ID), headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 403
    assert response.json() == {
        'code': '403',
        'message': (
            'Не удалось сохранить зону. '
            'Попробуйте обновить страницу и сохранить зону снова. '
            'Если ошибка остаётся, повторите позже.'
        ),
    }


@pytest.mark.experiments3(filename='places_settings.json')
async def test_places_delivery_zone_400_on_core_400_get(
        taxi_eats_restapp_places, mock_eats_core_400, mock_restapp_authorizer,
):
    response = await taxi_eats_restapp_places.get(
        HANDLE_URL.format(PLACE_ID), headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': (
            'Не удалось сохранить зону. '
            'Попробуйте обновить страницу и сохранить зону снова. '
            'Если ошибка остаётся, повторите позже.'
        ),
    }


@pytest.mark.experiments3(filename='places_settings.json')
async def test_places_delivery_zone_404_on_core_404_get(
        taxi_eats_restapp_places, mock_eats_core_404, mock_restapp_authorizer,
):
    response = await taxi_eats_restapp_places.get(
        HANDLE_URL.format(PLACE_ID), headers=DEFAULT_HEADERS,
    )

    assert response.status_code == 404
    assert response.json() == {'code': '404', 'message': 'Зона не найдена'}


@pytest.mark.experiments3(filename='places_settings.json')
@pytest.mark.eats_core_error(
    message='Delivery cost must be positive and less than 9999.',
)
async def test_places_delivery_zone_incorrect_delivery_condition(
        taxi_eats_restapp_places,
        mock_maps_router_summary,
        mock_restapp_authorizer,
        mock_eats_core_delivery_zones,
):
    response = await taxi_eats_restapp_places.post(
        HANDLE_URL.format(PLACE_ID),
        headers=DEFAULT_HEADERS,
        data=json.dumps(REQ),
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'invalid_condition',
        'message': (
            'Стоимость доставки - целочисленные значения; '
            '>=0; максимум 4-значное число до 9999 ₽'
        ),
    }


@pytest.mark.experiments3(filename='places_settings.json')
@pytest.mark.eats_core_error(message='Duplicate delivery zone name.')
async def test_places_delivery_zone_incorrect_name(
        taxi_eats_restapp_places,
        mock_maps_router_summary,
        mock_restapp_authorizer,
        mock_eats_core_delivery_zones,
):
    response = await taxi_eats_restapp_places.post(
        HANDLE_URL.format(PLACE_ID),
        headers=DEFAULT_HEADERS,
        data=json.dumps(REQ),
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'invalid_name',
        'message': 'Зона с таким названием уже существует',
    }


@pytest.mark.experiments3(filename='places_settings.json')
@pytest.mark.eats_core_error(
    message='Amount of points should be greater than 3',
)
async def test_places_delivery_zone_incorrect_zone(
        taxi_eats_restapp_places,
        mock_maps_router_summary,
        mock_restapp_authorizer,
        mock_eats_core_delivery_zones,
):
    response = await taxi_eats_restapp_places.post(
        HANDLE_URL.format(PLACE_ID),
        headers=DEFAULT_HEADERS,
        data=json.dumps(REQ),
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'invalid_zone',
        'message': 'Добавьте для зоны не менее 4 вершин',
    }


@pytest.mark.experiments3(filename='places_settings.json')
@pytest.mark.eats_core_error(message='Something went wrong.')
async def test_places_delivery_zone_incorrect_something(
        taxi_eats_restapp_places,
        mock_maps_router_summary,
        mock_restapp_authorizer,
        mock_eats_core_delivery_zones,
):
    response = await taxi_eats_restapp_places.post(
        HANDLE_URL.format(PLACE_ID),
        headers=DEFAULT_HEADERS,
        data=json.dumps(REQ),
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': (
            'Не удалось сохранить зону. '
            'Попробуйте обновить страницу и сохранить зону снова. '
            'Если ошибка остаётся, повторите позже.'
        ),
    }
