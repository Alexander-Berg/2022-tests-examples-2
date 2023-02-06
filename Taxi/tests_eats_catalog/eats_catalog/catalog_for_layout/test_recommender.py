import json

from dateutil import parser
# pylint: disable=import-error
from dj.services.eats.eats_recommender.recommender.server.proto import (
    places_pb2,
)  # noqa: F401
import eats_restapp_marketing_cache.models as ermc_models
from google.protobuf import json_format
# pylint: enable=import-error
import pytest

from eats_catalog import adverts
from eats_catalog import experiments
from eats_catalog import storage


def make_default_banners(
        eats_catalog_storage, yabs, eats_restapp_marketing_cache_mock,
):
    courier_types = [
        storage.CouriersType.Pedestrian,
        storage.CouriersType.Bicycle,
        storage.CouriersType.Vehicle,
        storage.CouriersType.Monorcycle,
        storage.CouriersType.YandexTaxi,
    ]

    working_intervals = [
        storage.WorkingInterval(
            start=parser.parse('2022-04-08T09:00:00+03:00'),
            end=parser.parse('2022-04-08T23:00:00+03:00'),
        ),
    ]

    for place_id in [1, 2, 3, 4, 5]:
        eats_catalog_storage.add_place(
            storage.Place(
                slug=f'place_{place_id}',
                place_id=place_id,
                brand=storage.Brand(brand_id=place_id),
                new_rating=storage.NewRating(place_id),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=working_intervals,
                couriers_type=courier_types[place_id - 1],
            ),
        )
        if place_id < 4:
            eats_restapp_marketing_cache_mock.add_banner(
                ermc_models.PlaceBanner(place_id=place_id, banner_id=place_id),
            )

    banners = [1, 2, 3]
    for banner_id in banners:
        yabs.add_banner(adverts.create_yabs_service_banner(banner_id))


@pytest.mark.now('2022-04-08T13:10:00+03:00')
@experiments.eats_catalog_recommender_config()
@pytest.mark.parametrize(
    'recommended_places, recommender_called, expected_places,  yabs_called',
    [
        pytest.param(
            2,
            1,
            2,
            1,
            id='filtered 1 place',
            marks=(
                experiments.eats_catalog_yabs_coefficients(
                    source='recommender',
                    coefficients=adverts.Coefficients(
                        relevance_multiplier=1, send_relevance=True,
                    ),
                )
            ),
        ),
        pytest.param(
            0,
            1,
            0,
            0,
            id='filtered all places',
            marks=(
                experiments.eats_catalog_yabs_coefficients(
                    source='recommender',
                    coefficients=adverts.Coefficients(
                        relevance_multiplier=1, send_relevance=True,
                    ),
                )
            ),
        ),
        pytest.param(
            0,
            0,
            3,
            1,
            id='recommender_disabled',
            marks=(
                experiments.eats_catalog_yabs_coefficients(
                    source='none',
                    coefficients=adverts.Coefficients(
                        relevance_multiplier=1, send_relevance=True,
                    ),
                )
            ),
        ),
    ],
)
@experiments.advertisements(source='yabs')
@experiments.yabs_settings(adverts.YabsSettings())
async def test_advert_places_log(
        eats_restapp_marketing_cache_mock,
        catalog_for_layout,
        eats_catalog_storage,
        yabs,
        mockserver,
        recommended_places,
        recommender_called,
        expected_places,
        yabs_called,
):

    expected_additional_banners = [
        {
            'banner_id': 1,
            'ignore_context': True,
            'value_coefs': {'A': 1.0, 'B': recommended_places, 'C': 0},
        },
        {
            'banner_id': 2,
            'ignore_context': True,
            'value_coefs': {'A': 1.0, 'B': recommended_places - 1, 'C': 0},
        },
        {
            'banner_id': 3,
            'ignore_context': True,
            'value_coefs': {'A': 1.0, 'B': recommended_places - 2, 'C': 0},
        },
    ]

    def yabs_callback(request):
        assert 'additional-banners' in request.query

        sorted_banners = sorted(
            json.loads(request.query['additional-banners']),
            key=lambda banner: banner['banner_id'],
        )
        assert (
            sorted_banners == expected_additional_banners[0:recommended_places]
        )

    if recommender_called > 0:
        yabs.request_assertion_callback = yabs_callback

    @mockserver.json_handler('/eats-recommender/v1/recommend/places')
    def recommender_places(request):
        request_proto = places_pb2.TRequest()
        request_proto.ParseFromString(request.get_data())

        data = json.loads(json_format.MessageToJson(request_proto))
        data['Places'].sort(key=lambda place: (place['Id']))

        assert data == {
            'Experiments': ['experiment'],
            'User': {'EaterId': '1234', 'PassportUid': '12341212'},
            'Places': [
                {
                    'Id': '1',
                    'CourierType': 'CT_Pedestrian',
                    'EstimatedTime': {'Min': 25, 'Max': 35},
                    'Rating': {'Average': 1.0},
                    'IsAvailable': True,
                },
                {
                    'Id': '2',
                    'CourierType': 'CT_Bicycle',
                    'EstimatedTime': {'Min': 25, 'Max': 35},
                    'Rating': {'Average': 2.0},
                    'IsAvailable': True,
                },
                {
                    'Id': '3',
                    'CourierType': 'CT_Vehicle',
                    'EstimatedTime': {'Min': 25, 'Max': 35},
                    'Rating': {'Average': 3.0},
                    'IsAvailable': True,
                },
            ],
        }

        data['Places'].sort(key=lambda place: int(place['Id']))

        items = []
        count = len(data['Places'][0:recommended_places])
        for place in data['Places'][0:recommended_places]:
            items.append({'Id': place['Id'], 'Relevance': count})
            count -= 1

        response = places_pb2.TResponse()
        json_format.ParseDict(
            {
                'Recommendations': [
                    {'Experiment': data['Experiments'][0], 'Items': items},
                ],
            },
            response,
        )

        return mockserver.make_response(
            response.SerializeToString(deterministic=True),
        )

    make_default_banners(
        eats_catalog_storage, yabs, eats_restapp_marketing_cache_mock,
    )

    block_id = 'adverts'
    response = await catalog_for_layout(
        blocks=[
            {
                'id': block_id,
                'type': 'open',
                'disable_filters': False,
                'advert_settings': {
                    'ads_only': True,
                    'indexes': [0, 1, 2, 3, 4],
                },
            },
        ],
    )

    response_json = response.json()

    assert response.status_code == 200
    assert recommender_places.times_called == recommender_called
    assert yabs.times_called == yabs_called
    # один рекламный блок - один вызов в yabs
    assert len(response_json['blocks']) == yabs_called
    if expected_places > 0:
        assert len(response_json['blocks'][0]['list']) == expected_places
    else:
        assert not response_json['blocks']


@pytest.mark.now('2022-04-08T13:10:00+03:00')
@experiments.advertisements(source='yabs')
@experiments.eats_catalog_recommender_config()
@experiments.yabs_settings(adverts.YabsSettings())
@experiments.eats_catalog_yabs_coefficients(
    source='recommender',
    coefficients=adverts.Coefficients(
        relevance_multiplier=1, send_relevance=True,
    ),
)
async def test_recommender_error(
        catalog_for_layout,
        mockserver,
        eats_catalog_storage,
        yabs,
        eats_restapp_marketing_cache_mock,
):
    # EDACAT-3035
    # Проверяет используется ли старая логика рекламы
    # если рекоммендер не ответил

    @mockserver.json_handler('/eats-recommender/v1/recommend/places')
    def recommender_places(_):
        return mockserver.make_response(status=500)

    make_default_banners(
        eats_catalog_storage, yabs, eats_restapp_marketing_cache_mock,
    )

    block_id = 'adverts'
    response = await catalog_for_layout(
        blocks=[
            {
                'id': block_id,
                'type': 'open',
                'disable_filters': False,
                'advert_settings': {
                    'ads_only': True,
                    'indexes': [0, 1, 2, 3, 4],
                },
            },
        ],
    )

    response_json = response.json()

    assert response.status_code == 200
    assert recommender_places.times_called == 1
    assert yabs.times_called == 1
    assert len(response_json['blocks']) == 1
    assert len(response_json['blocks'][0]['list']) == 3
