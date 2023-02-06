from aiohttp import web
import pytest


ADDRESS_MATCHER_PATH = '/taxi_order_by_phone/match_address/v1'

# pylint: disable=C0103
pytestmark = [
    pytest.mark.enable_ml_handler(url_path=ADDRESS_MATCHER_PATH),
    pytest.mark.download_ml_resource(
        attrs={'type': 'zerosuggest_address_matcher'},
    ),
]


@pytest.mark.skip(reason='test of an unused handle')
@pytest.mark.parametrize(
    'model,user_input,result,acknowledgement,address,result_model',
    [
        (
            'acknowledgement',
            'Да',
            'positive',
            'positive',
            None,
            'acknowledgement',
        ),
        (
            'acknowledgement',
            'нет',
            'negative',
            'negative',
            None,
            'acknowledgement',
        ),
        (
            'acknowledgement',
            'оператор',
            'operator',
            'operator',
            None,
            'acknowledgement',
        ),
        (
            'address',
            'Some street',
            'Some street',
            None,
            'Some street',
            'address',
        ),
        ('both', 'Some street', 'Some street', None, 'Some street', 'address'),
        (
            'both',
            'нет Some street',
            'Some street',
            'negative',
            'Some street',
            'address',
        ),
        ('both', 'неверно', 'negative', 'negative', None, 'acknowledgement'),
    ],
)
async def test_taxi_order_by_phone(
        web_app_client,
        model,
        user_input,
        result,
        acknowledgement,
        address,
        result_model,
        mockserver,
):
    @mockserver.json_handler('/yamaps/yandsearch')
    # pylint: disable=unused-variable
    async def ymaps_handler(request):
        if result_model == 'address':
            return web.json_response(
                data={
                    'features': [
                        {
                            'geometry': {
                                'coordinates': [0.1, 0.2],
                                'type': '',
                            },
                            'properties': {
                                'description': '',
                                'name': '',
                                'GeocoderMetaData': {
                                    'Address': {
                                        'country_code': 'RU',
                                        'formatted': '',
                                        'Components': [],
                                    },
                                },
                                'URIMetaData': {'URI': {'uri': result}},
                            },
                        },
                    ],
                },
            )

        return web.json_response(data={'features': []})

    @mockserver.json_handler('/wizard/wizard')
    # pylint: disable=unused-variable
    async def wizard_handler(request):
        if result_model == 'address':
            return web.json_response(
                data={'rules': {'GeoAddr': {'NormalizedText': result}}},
            )

        return web.json_response(data={'rules': {}})

    resp = await web_app_client.post(
        f'/taxi_order_by_phone/v1',
        json={
            'user_input': user_input,
            'model': model,
            'city': {'latitude': 0.1, 'longitude': 0.1},
        },
    )

    assert resp.status == 200

    resp_json = await resp.json()

    assert resp_json['result'] == result
    assert resp_json['model'] == result_model

    if acknowledgement:
        assert resp_json['acknowledgement'] == acknowledgement
    else:
        assert 'acknowledgement' not in resp_json

    if address:
        assert resp_json['address'] == address
    else:
        assert 'address' not in resp_json


async def test_score_zerosuggest_handler(web_app_client):
    response = await web_app_client.post(
        ADDRESS_MATCHER_PATH,
        json={
            'zerosuggest_items': [
                {
                    'title': f'title_{index}',
                    'subtitle': f'subtitle_{index}',
                    'index': index,
                }
                for index in range(10)
            ],
            'user_message': 'some message',
        },
    )
    assert response.status == 200

    response_json = await response.json()
    scored_zerosuggest_items = response_json.get('scored_zerosuggest_items')
    assert scored_zerosuggest_items is not None
    for item in scored_zerosuggest_items:
        zerosuggest_item = item.get('zerosuggest_item')
        assert zerosuggest_item is not None
        index = zerosuggest_item.get('index')
        assert index is not None
        assert zerosuggest_item.get('title') == f'title_{index}'
        assert zerosuggest_item.get('subtitle') == f'subtitle_{index}'
        assert item.get('score') is not None
