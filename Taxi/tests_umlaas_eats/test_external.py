import json

# pylint: disable=import-error
from dj.services.eats.eats_recommender.recommender.server.proto import (
    places_pb2,
)  # noqa: F401
from eats_bigb import eats_bigb
from google.protobuf import json_format
import pytest

from tests_umlaas_eats import experiments


@pytest.mark.parametrize(
    'bigb_times_called',
    [
        pytest.param(1, marks=(experiments.ENABLE_BIGB), id='bigb endabled'),
        pytest.param(0, id='bigb disabled'),
    ],
)
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
@pytest.mark.bigb(
    eats_bigb.Profile(
        passport_uid='12341212',
        brand_stats={
            179: eats_bigb.BrandStatistics(views=22, opens=12),
            3179: eats_bigb.BrandStatistics(views=12, opens=2),
            11787: eats_bigb.BrandStatistics(views=12, opens=12),
        },
        demographics=eats_bigb.Demograpics(
            gender=eats_bigb.Gender.FEMALE,
            age_category=eats_bigb.AgeCategory.BETWEEN_45_AND_54,
            income_level=eats_bigb.IncomeLevel.LOW,
        ),
    ),
)
async def test_bigb_request(
        catalog_v1, load_json, mockserver, testpoint, bigb_times_called,
):
    @testpoint('eats-bigb:parse_profile')
    def bigb_parse(data):
        assert data['passport_uid'] == '12341212'
        assert data['demographics'] == {
            'age_category': 'between_45_and_54',
            'gender': 'female',
            'income_level': 'low',
        }

        # NOTE: Фиксируем порядок элментов в статистике брендов чтобы избежать
        # флапов - в cpp это unordered_map, поэтому список может иметь
        # произвольный порядок.
        data['brands_stats'].sort(key=lambda brand: brand['brand_id'])
        assert data['brands_stats'] == [
            {'brand_id': 179, 'views': 22, 'opens': 12},
            {'brand_id': 3179, 'views': 12, 'opens': 2},
            {'brand_id': 11787, 'views': 12, 'opens': 12},
        ]

    web_response = await catalog_v1(
        load_json('request.json'), headers={'x-yandex-uid': '12341212'},
    )

    assert bigb_parse.times_called == bigb_times_called
    assert web_response.status == 200


@experiments.recommender(name='highest_rating')
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_recommender(catalog_v1, load_json, mockserver):
    @mockserver.json_handler('/eats-recommender/v1/recommend/places')
    def recommender_places(request):
        request_proto = places_pb2.TRequest()
        request_proto.ParseFromString(request.get_data())

        data = json.loads(json_format.MessageToJson(request_proto))
        data['Places'].sort(
            key=lambda place: (
                place['EstimatedTime']['Min'],
                int(place['Id']),
            ),
        )

        assert data == {
            'Experiments': ['highest_rating'],
            'User': {'PassportUid': '12341212', 'EaterId': '1184610'},
            'Places': [
                {
                    'Id': '76511',
                    'CourierType': 'CT_YandexTaxi',
                    'EstimatedTime': {'Min': 10, 'Max': 20},
                    'Rating': {'Average': 4.955},
                    'IsAvailable': True,
                },
                {
                    'Id': '3621',
                    'CourierType': 'CT_Pedestrian',
                    'EstimatedTime': {'Min': 30, 'Max': 30},
                    'Rating': {'Average': 4.76, 'Shown': 4.8},
                    'IsAvailable': True,
                },
                {
                    'Id': '11271',
                    'CourierType': 'CT_Pedestrian',
                    'EstimatedTime': {'Min': 30, 'Max': 40},
                    'Rating': {'Average': 3.9412, 'Shown': 4.0},
                    'IsAvailable': True,
                },
                {
                    'Id': '36575',
                    'CourierType': 'CT_Pedestrian',
                    'EstimatedTime': {'Min': 30, 'Max': 40},
                    'Rating': {'Average': 4.6914, 'Shown': 4.7},
                    'IsAvailable': True,
                },
                {
                    'Id': '56622',
                    'CourierType': 'CT_Pedestrian',
                    'EstimatedTime': {'Min': 30, 'Max': 40},
                    'Rating': {'Average': 4.8242, 'Shown': 4.8},
                    'IsAvailable': True,
                },
                {
                    'Id': '24938',
                    'CourierType': 'CT_YandexTaxi',
                    'EstimatedTime': {'Min': 35, 'Max': 45},
                    'Rating': {'Average': 4.6069, 'Shown': 4.6},
                    'IsAvailable': True,
                },
                {
                    'Id': '24968',
                    'CourierType': 'CT_Pedestrian',
                    'EstimatedTime': {'Min': 35, 'Max': 45},
                    'Rating': {'Average': 4.6154, 'Shown': 4.6},
                    'IsAvailable': True,
                },
                {
                    'Id': '10465',
                    'CourierType': 'CT_Pedestrian',
                    'EstimatedTime': {'Min': 40, 'Max': 50},
                    'Rating': {'Average': 4.745, 'Shown': 4.7},
                    'IsAvailable': True,
                },
                {
                    'Id': '3265',
                    'CourierType': 'CT_Pedestrian',
                    'EstimatedTime': {'Min': 45, 'Max': 55},
                    'Rating': {'Average': 4.775, 'Shown': 4.8},
                    'IsAvailable': True,
                },
            ],
        }

        data['Places'].sort(key=lambda place: int(place['Id']))

        items = []
        count = len(data['Places'])
        for place in data['Places']:
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

    web_response = await catalog_v1(
        load_json('request.json'), headers={'x-yandex-uid': '12341212'},
    )

    assert recommender_places.times_called == 1
    assert web_response.status == 200

    data = web_response.json()
    order = [item['id'] for item in data['result']]

    assert order == [
        3265,
        3621,
        10465,
        11271,
        24938,
        24968,
        36575,
        56622,
        76511,
    ]


@experiments.recommender(name='highest_rating')
@pytest.mark.eats_catalog_storage_cache(file='eats-catalog-storage.json')
async def test_recommender_error(catalog_v1, load_json, mockserver):
    @mockserver.json_handler('/eats-recommender/v1/recommend/places')
    def recommender_places(_):
        return mockserver.make_response(status=500)

    web_response = await catalog_v1(
        load_json('request.json'), headers={'x-yandex-uid': '12341212'},
    )

    assert recommender_places.times_called == 1
    assert web_response.status == 200

    data = web_response.json()
    assert len(data['result']) == 9
