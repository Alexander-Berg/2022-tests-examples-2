# pylint: disable=C0302
import pytest

import generated.clients_libs.supportai_models.supportai_lib as supportai_lib_module  # noqa pylint: disable=line-too-long

from supportai.common import state as state_module


@pytest.mark.parametrize(
    ('text', 'wiz_response', 'results'),
    [
        (
            'город москва улица новый арбат дом 12 корпус 3',
            {
                'rules': {
                    'Text': {
                        'Request': (
                            'город москва улица новый арбат дом 12 корпус 3'
                        ),
                        'UserRequest': (
                            'город москва улица новый арбат дом 12 корпус 3'
                        ),
                        'RequestLenTruncated': '0',
                    },
                    'NormalizeRequest': {
                        'QueryTruncated': '0',
                        'RuleResult': '3',
                        'BannerRequest': (
                            'город москва улица новый арбат дом 12 корпус 3'
                        ),
                    },
                    'LangRecognizer': {'RuleResult': '3'},
                    'RelevLocale': {
                        'SearchCountryID': '225',
                        'SearchRegion': '225',
                    },
                    'Commercial': {
                        'CommercialLength': '1',
                        'Commercial': '0.086957',
                        'RuleResult': '3',
                    },
                    'QSegments': {'RuleResult': '3'},
                    'GeoAddr': {
                        'Type': 'StreetInCity',
                        'RuleResult': '3',
                        'LowestGeoLevel': 'House',
                        'Body': '{"Variants":[{"City":"город москва","Street":"улица новый арбат","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":true,"Weight":0.997,"CommonIDs":[213],"CityIDs":[213]}],"BestGeo":213,"BestInheritedGeo":213}',  # noqa
                        'Pos': '0',
                        'BestGeo': '213',
                        'UnfilteredAnswer': '{"Body":{"Variants":[{"City":"город москва","Street":"улица новый арбат","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":true,"Weight":0.997}],"BestGeo":213,"BestInheritedGeo":213,"Weight":0.997},"Pos":0,"Length":9,"NormalizedText":"город москва, улица новый арбат, дом 12 корпус 3","Type":"StreetInCity"}',  # noqa
                        'Length': '9',
                        'CityIDsStr': '213',
                        'weight': '0.996895',
                        'NormalizedText': (
                            'город москва, улица новый арбат, дом 12 корпус 3'
                        ),
                    },
                },
            },
            ['город москва,улица новый арбат,дом 12 корпус 3'],
        ),
        (
            'Здравствуйте. Сориентируйте, я могу забрать заказ сегодня? Работает ли магазин на выдачу?',  # noqa
            {
                'rules': {
                    'Text': {
                        'Request': 'здравствуйте. сориентируйте, я могу забрать заказ сегодня? работает ли магазин на выдачу?',  # noqa
                        'UserRequest': 'Здравствуйте. Сориентируйте, я могу забрать заказ сегодня? Работает ли магазин на выдачу?',  # noqa
                        'RequestLenTruncated': '0',
                    },
                    'NormalizeRequest': {
                        'QueryTruncated': '0',
                        'RuleResult': '3',
                        'BannerRequest': 'здравствуйте сориентируйте я могу забрать заказ сегодня работает ли магазин на выдачу',  # noqa
                    },
                    'GeoAddr': {
                        'UnfilteredAnswer': '{"Body":{"Variants":[{"City":"магазин","HasOwnGeoIds":false,"Weight":0.017}],"BestGeo":-1,"BestInheritedGeo":29321,"Weight":0.017},"Pos":9,"Length":1,"NormalizedText":"магазин","Type":"City"}',  # noqa
                    },
                },
            },
            [],
        ),
        (
            'город москва улица ленина дом 12 корпус 3',  # noqa
            {
                'rules': {
                    'Text': {
                        'Request': (
                            'город москва улица ленина дом 12 корпус 3'
                        ),  # noqa
                        'UserRequest': (
                            'город москва улица ленина дом 12 корпус 3'  # noqa
                        ),
                        'RequestLenTruncated': '0',
                    },
                    'NormalizeRequest': {
                        'QueryTruncated': '0',
                        'RuleResult': '3',
                        'BannerRequest': (
                            'город москва улица ленина дом 12 корпус 3'  # noqa
                        ),
                    },
                    'LangRecognizer': {'RuleResult': '3'},
                    'RelevLocale': {
                        'SearchCountryID': '225',
                        'SearchRegion': '225',
                    },
                    'Commercial': {
                        'CommercialLength': '1',
                        'Commercial': '0.086957',
                        'RuleResult': '3',
                    },
                    'QSegments': {'RuleResult': '3'},
                    'GeoAddr': {
                        'Type': ['City', 'Street'],
                        'RuleResult': '3',
                        'LowestGeoLevel': 'House',
                        'Body': [
                            '{"Variants":[{"City":"город москва","HasOwnGeoIds":true,"Weight":0.992,"CityIDs":[213]}],"BestGeo":213,"BestInheritedGeo":213}',  # noqa
                            '{"Variants":[{"Street":"улица ленина","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[2,6,7,8,9,10,11,12,15,19,20,21,25,33,35,36,37,38,43,44,46,49,50,53,55,56,57,58,62,63,64,65,66,68,74,76,77,80,143,146,153,154,157,162,164,165,172,192,193,195,198,214,215,216,222,236,237,240,959,968,970,971,1058,1091,1092,1093,1094,1104,1107,10274,10275,10291,10292,10293,10295,10300,10305,10315,10316,10317,10368,10646,10647,10649,10651,10652,10654,10655,10656,10659,10660,10661,10662,10663,10665,10667,10668,10669,10670,10671,10674]},{"Street":"улица в. ленина","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[20259]},{"Street":"улица зеленая","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[24765]},{"Street":"улица ильича","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[10761,106005]},{"Street":"улица биласа","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[24661]},{"Street":"улица криничная","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[27577]},{"Street":"улица кунаева","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[116946]},{"Street":"улица уютная","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[27842]},{"Street":"улица вишневая","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[28533]},{"Street":"улица достык","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[162,29487]},{"Street":"улица дружбы","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[20552]},{"Street":"улица киевская","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[10343]},{"Street":"улица националэ","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[101536]},{"Street":"улица соборная","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[27314,28690]},{"Street":"улица талгат","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[116780]},{"Street":"улица троицкая","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[27476]},{"Street":"улица шевченко","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[24421]},{"Street":"улица школьная","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[24765]},{"Street":"улица имени ленина","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[10689,10821,122951,136795,138414,146157]},{"Street":"улица малая ленина","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[10710,101163]},{"Street":"улица в. и. ленина","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[38,102099,102100,102101,102108]},{"Street":"улица азербаева","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[162]},{"Street":"улица культуры","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[28428]},{"Street":"улица лоцманская","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[28190]},{"Street":"улица набережная","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[101046]},{"Street":"улица парковая","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[24765]},{"Street":"улица радостная","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[28731]},{"Street":"улица центральная","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[24755,24765,27069,27147,27156]},{"Street":"улица слободская","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[24765]},{"Street":"улица софиевская","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[28525]},{"Street":"улица шайкорган","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[29406]},{"Street":"улица шептицкого","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[24742]},{"Street":"улица абылай хана","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[29422,29497]},{"Street":"улица айтеке би","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[20273]},{"Street":"улица верхняя ленина","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[1094]},{"Street":"улица бейбитшилик","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[116869]},{"Street":"улица ришельевская","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[145]},{"Street":"улица слобожанская","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[24765]},{"Street":"улица стельмащука","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[24520]},{"Street":"улица трапезонская","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[28865]},{"Street":"улица чернявского","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[131720]},{"Street":"улица барвинковская","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[24407]},{"Street":"улица воздвиженская","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[24512]},{"Street":"улица воскресенская","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[10923]},{"Street":"улица грушевского","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[27424,28906]},{"Street":"улица тауелсыздык","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[29585]},{"Street":"улица а. кунанбаева","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[29594]},{"Street":"улица владимира ленина","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[975,10276,104925,121086,126360]},{"Street":"улица героев крут","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[28344]},{"Street":"улица им. в. и. ленина","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998,"CommonIDs":[10902]}],"BestGeo":-1,"BestInheritedGeo":143}',  # noqa
                        ],
                        'BestInheritedGeo': ['213', '143'],
                        'Pos': ['0', '2'],
                        'BestGeo': ['213', '-1'],
                        'UnfilteredAnswer': [
                            '{"Body":{"Variants":[{"City":"город москва","HasOwnGeoIds":true,"Weight":0.992}],"BestGeo":213,"BestInheritedGeo":213,"Weight":0.992},"Pos":0,"Length":2,"NormalizedText":"город москва","Type":"City"}',  # noqa
                            '{"Body":{"Variants":[{"Street":"улица ленина","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица в. ленина","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица зеленая","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица ильича","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица биласа","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица криничная","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица кунаева","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица уютная","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица вишневая","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица достык","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица дружбы","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица киевская","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица националэ","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица соборная","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица талгат","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица троицкая","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица шевченко","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица школьная","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица имени ленина","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица малая ленина","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица в. и. ленина","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица азербаева","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица культуры","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица лоцманская","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица набережная","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица парковая","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица радостная","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица центральная","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица слободская","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица софиевская","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица шайкорган","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица шептицкого","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица абылай хана","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица айтеке би","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица верхняя ленина","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица бейбитшилик","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица ришельевская","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица слобожанская","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица стельмащука","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица трапезонская","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица чернявского","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица барвинковская","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица воздвиженская","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица воскресенская","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица грушевского","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица тауелсыздык","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица а. кунанбаева","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица владимира ленина","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица героев крут","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998},{"Street":"улица им. в. и. ленина","HouseNumber":"дом 12 корпус 3","HasOwnGeoIds":false,"Weight":0.998}],"BestGeo":-1,"BestInheritedGeo":143,"Weight":0.998},"Pos":2,"Length":6,"NormalizedText":"улица ленина, дом 12 корпус 3","Type":"Street"}',  # noqa
                        ],
                        'Length': ['2', '6'],
                        'CityIDsStr': '213',
                        'weight': ['0.991900', '0.998301'],
                        'NormalizedText': [
                            'город москва',
                            'улица ленина, дом 12 корпус 3',
                        ],
                    },
                },
            },
            ['город москва,улица ленина,дом 12 корпус 3'],
        ),
        (
            'город москва',  # noqa
            {
                'rules': {
                    'Text': {
                        'Request': 'город москва',
                        'UserRequest': 'город москва',
                        'RequestLenTruncated': '0',
                    },
                    'NormalizeRequest': {
                        'QueryTruncated': '0',
                        'RuleResult': '3',
                        'BannerRequest': 'город москва',
                    },
                    'IsNav': {'RuleResult': '3'},
                    'LangRecognizer': {'RuleResult': '3'},
                    'RelevLocale': {
                        'SearchCountryID': '225',
                        'SearchRegion': '225',
                    },
                    'QSegments': {'RuleResult': '3'},
                    'GeoAddr': {
                        'Type': 'City',
                        'RuleResult': '3',
                        'LowestGeoLevel': 'Locality',
                        'Body': '{"Variants":[{"City":"город москва","HasOwnGeoIds":true,"Weight":1.000,"CityIDs":[213]}],"BestGeo":213,"BestInheritedGeo":213}',  # noqa
                        'BestInheritedGeo': '213',
                        'Pos': '0',
                        'BestGeo': '213',
                        'UnfilteredAnswer': '{"Body":{"Variants":[{"City":"город москва","HasOwnGeoIds":true,"Weight":1.000}],"BestGeo":213,"BestInheritedGeo":213,"Weight":1.000},"Pos":0,"Length":2,"NormalizedText":"город москва","Type":"City"}',  # noqa
                        'Length': '2',
                        'CityIDsStr': '213',
                        'weight': '1.000000',
                        'NormalizedText': 'город москва',
                    },
                },
            },
            ['город москва'],
        ),
    ],
)
async def test_address_entity_extractor(
        create_nlu, web_context, text, wiz_response, results, core_flags,
):
    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }
    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {'messages': [{'author': 'user', 'text': text}]},
            'features': [],
        },
    )
    state = state_module.State(feature_layers=[{}])
    nlu = await create_nlu(
        config_path='configuration.json',
        namespace='justschool_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response=wiz_response,
    )

    nlu_response = await nlu(request, state, web_context, core_flags)
    assert nlu_response.entities['address_extractor'].values == results


@pytest.mark.parametrize(
    'config_path',
    [
        'test_city_entity_extractor_short_city_name.json',
        'test_city_entity_extractor_two_cities_in_text.json',
        'test_city_entity_extractor_no_city_in_text.json',
        'test_city_entity_extractor_one_city_in_text.json',
    ],
)
async def test_city_entity_extractor(
        create_nlu, web_context, config_path, load_json, core_flags,
):

    config = load_json(config_path)
    text, wiz_response, results = (
        config['text'],
        config['wiz_response'],
        config['results'],
    )
    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }
    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {'messages': [{'author': 'user', 'text': text}]},
            'features': [],
        },
    )
    state = state_module.State(feature_layers=[{}])
    nlu = await create_nlu(
        config_path='configuration.json',
        namespace='justschool_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response=wiz_response,
    )

    nlu_response = await nlu(request, state, web_context, core_flags)
    assert nlu_response.entities['city_extractor'].values == results


@pytest.mark.parametrize(
    'config_path',
    [
        'test_street_entity_extractor_one_street_in_text.json',
        'test_street_entity_extractor_only_street_in_text.json',
    ],
)
async def test_street_entity_extractor(
        create_nlu, web_context, config_path, load_json, core_flags,
):

    config = load_json(config_path)
    text, wiz_response, results = (
        config['text'],
        config['wiz_response'],
        config['results'],
    )
    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }
    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {'messages': [{'author': 'user', 'text': text}]},
            'features': [],
        },
    )
    state = state_module.State(feature_layers=[{}])
    nlu = await create_nlu(
        config_path='configuration.json',
        namespace='justschool_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response=wiz_response,
    )

    nlu_response = await nlu(request, state, web_context, core_flags)
    assert nlu_response.entities['street_extractor'].values == results


@pytest.mark.parametrize(
    'config_path', ['test_metro_entity_extractor_one_metro_in_text.json'],
)
async def test_metro_entity_extractor_one_metro_in_text(
        create_nlu, web_context, config_path, load_json, core_flags,
):

    config = load_json(config_path)
    text, wiz_response, results = (
        config['text'],
        config['wiz_response'],
        config['results'],
    )
    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }
    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {'messages': [{'author': 'user', 'text': text}]},
            'features': [],
        },
    )
    state = state_module.State(feature_layers=[{}])
    nlu = await create_nlu(
        config_path='configuration.json',
        namespace='justschool_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response=wiz_response,
    )

    nlu_response = await nlu(request, state, web_context, core_flags)
    assert nlu_response.entities['metro_extractor'].values == results


@pytest.mark.parametrize(
    'config_path', ['test_village_entity_extractor_one_village_in_text.json'],
)
async def test_village_entity_extractor(
        create_nlu, web_context, config_path, load_json, core_flags,
):
    config = load_json(config_path)
    text, wiz_response, results = (
        config['text'],
        config['wiz_response'],
        config['results'],
    )
    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }
    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {'messages': [{'author': 'user', 'text': text}]},
            'features': [],
        },
    )
    state = state_module.State(feature_layers=[{}])
    nlu = await create_nlu(
        config_path='configuration.json',
        namespace='justschool_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response=wiz_response,
    )

    nlu_response = await nlu(request, state, web_context, core_flags)
    assert nlu_response.entities['village_extractor'].values == results


@pytest.mark.parametrize(
    'config_path',
    [
        'test_org_entity_extractor_one_org_in_text.json',
        'test_org_entity_extractor_one_org_in_text_2.json',
        'test_org_entity_extractor_org_with_three_words_in_name_in_text.json',  # noqa
    ],
)
async def test_org_entity_extractor(
        create_nlu, web_context, config_path, load_json, core_flags,
):
    config = load_json(config_path)
    text, wiz_response, results = (
        config['text'],
        config['wiz_response'],
        config['results'],
    )
    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }
    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {'messages': [{'author': 'user', 'text': text}]},
            'features': [],
        },
    )
    state = state_module.State(feature_layers=[{}])
    nlu = await create_nlu(
        config_path='configuration.json',
        namespace='justschool_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response=wiz_response,
    )

    nlu_response = await nlu(request, state, web_context, core_flags)
    assert nlu_response.entities['organization_extractor'].values == results


@pytest.mark.parametrize(
    'config_path',
    [
        'test_house_number_entity_extractor_one_house_number_in_text.json',  # noqa
    ],
)
async def test_house_number_entity_extractor_one_house_number_in_text(
        create_nlu, web_context, config_path, load_json, core_flags,
):
    config = load_json(config_path)
    text, wiz_response, results = (
        config['text'],
        config['wiz_response'],
        config['results'],
    )
    supportai_models_response = {
        'most_probable_topic': 'Cancel_lesson',
        'probabilities': [
            {'topic_name': 'Cancel_lesson', 'probability': 0.8},
            {'topic_name': 'Move_lesson', 'probability': 0.2},
        ],
    }
    request = supportai_lib_module.SupportRequest.deserialize(
        {
            'dialog': {'messages': [{'author': 'user', 'text': text}]},
            'features': [],
        },
    )
    state = state_module.State(feature_layers=[{}])
    nlu = await create_nlu(
        config_path='configuration.json',
        namespace='justschool_dialog',
        supportai_models_response=supportai_models_response,
        wiz_response=wiz_response,
    )

    nlu_response = await nlu(request, state, web_context, core_flags)
    assert nlu_response.entities['house_number_extractor'].values == results
