# pylint: disable=C5521
# pylint: disable=C0302
import datetime
import json

from dateutil import parser
import pytest

from eats_catalog import configs
from eats_catalog import experiments
from eats_catalog import storage

NOW = parser.parse('2021-01-01T12:00:00+03:00')

LOGO = [
    {
        'theme': 'dark',
        'value': [
            {
                'logo_url': (
                    'https://avatars.mds.yandex.net/get-eda/aaaaaa/214x140'
                ),
                'size': 'small',
            },
        ],
    },
]


SERVICE_FEE_TITLE = 'Работа сервиса'


SERVICE_FEE_DESCRIPTION = """
    Ассортимент и предложения партнёров можно изучить в Яндекс Еде бесплатно.
    Чтобы оформить заказ в Яндекс Еде, потребуется оплатить сбор.
    Нажимая "Верно, к оплате", вы соглашаетесь с этими условиями.
    """


SERVICE_FEE_TRANSLATIONS = {
    'eats-catalog': {
        'slug.service_fee.title': {'ru': SERVICE_FEE_TITLE},
        'slug.service_fee.description': {'ru': SERVICE_FEE_DESCRIPTION},
    },
    'tariff': {
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
    },
}


def get_conditions(weight_threshold, heavy_weight_cost):
    return {
        'weight_threshold': weight_threshold,
        'heavy_weight_cost': heavy_weight_cost,
    }


def get_thresholds(min_v, max_v, weight_cost, decimal_weight_cost, title):
    return {
        'orderWeight': {'min': min_v, 'max': max_v},
        'weightCost': weight_cost,
        'decimalWeightCost': decimal_weight_cost,
        'title': title,
    }


def themed_picture(url: str) -> dict:
    return {
        'light': {'uri': url, 'ratio': 1.33},
        'dark': {'uri': url, 'ratio': 1.33},
    }


MESSAGE_DESCRIPTION = (
    'Итоговая сумма зависит от'
    ' стоимости и веса заказа,'
    ' расстояния между вами и'
    ' магазином и того, доставляет'
    ' курьер пешком или на машине.'
)

WEIGHT_DESCRIPTION = 'Её целиком получит курьер, если заказ выйдет тяжёлым.'


@pytest.mark.now('2021-01-01T12:00:00+03:00')
@experiments.currency_sign('<category-₽>')
@pytest.mark.eats_regions_cache(file='regions.json')
@pytest.mark.translations(**SERVICE_FEE_TRANSLATIONS)
@configs.eats_catalog_rating_meta()
@experiments.SHOW_SERVICE_FEE
@pytest.mark.parametrize(
    [
        'weight_conditions',
        'weight_thresholds',
        'message_description',
        'weight_description',
    ],
    [
        pytest.param(
            [
                get_conditions(0, 0),
                get_conditions(8000, 40),
                get_conditions(15000, 80),
            ],
            [
                get_thresholds('0', '8000', 0, '0', 'для заказа до 8 кг'),
                get_thresholds(
                    '8000', '15000', 40, '40', 'для заказа 8-15 кг',
                ),
                get_thresholds('15000', '', 80, '80', 'для заказа от 15 кг'),
            ],
            MESSAGE_DESCRIPTION[:10],
            WEIGHT_DESCRIPTION[:10],
            marks=pytest.mark.translations(
                **{
                    'eats-catalog': {
                        'common.weight_from': {
                            'ru': 'для заказа от %(from)s кг',
                        },
                        'common.weight_up_to': {
                            'ru': 'для заказа до %(up_to)s кг',
                        },
                        'common.weight_range': {
                            'ru': 'для заказа %(from)s-%(up_to)s кг',
                        },
                        'slug.delivery_message.description': {
                            'ru': MESSAGE_DESCRIPTION[:10],
                        },
                        'slug.weight_thresholds.description': {
                            'ru': WEIGHT_DESCRIPTION[:10],
                        },
                    },
                },
            ),
            id='keys_present_in_keyset_1',
        ),
        pytest.param(
            [get_conditions(0, 0), get_conditions(8000, 40)],
            [
                get_thresholds('0', '8000', 0, '0', 'до 8 кг'),
                get_thresholds('8000', '', 40, '40', 'от 8 кг'),
            ],
            MESSAGE_DESCRIPTION,
            WEIGHT_DESCRIPTION,
            marks=pytest.mark.translations(
                **{
                    'eats-catalog': {
                        'common.weight_from': {'ru': 'от %(from)s кг'},
                        'common.weight_up_to': {'ru': 'до %(up_to)s кг'},
                        'common.weight_range': {'ru': '%(from)s-%(up_to)s кг'},
                        'slug.delivery_message.description': {
                            'ru': MESSAGE_DESCRIPTION,
                        },
                        'slug.weight_thresholds.description': {
                            'ru': WEIGHT_DESCRIPTION,
                        },
                    },
                },
            ),
            id='keys_present_in_keyset_2',
        ),
        pytest.param(
            [],
            None,
            MESSAGE_DESCRIPTION,
            WEIGHT_DESCRIPTION,
            id='keys_absent_in_keyset',
        ),
    ],
)
async def test_with_position(
        slug,
        mockserver,
        prediction,
        delivery_price,
        surge,
        eats_catalog_storage,
        weight_conditions,
        weight_thresholds,
        message_description,
        weight_description,
):

    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-01-01T10:00:00+03:00'),
            end=parser.parse('2021-01-01T14:00:00+03:00'),
        ),
        storage.WorkingInterval(
            start=parser.parse('2021-01-02T10:00:00+03:00'),
            end=parser.parse('2021-01-02T14:00:00+03:00'),
        ),
    ]

    eats_catalog_storage.add_place(
        storage.Place(
            launched_at=NOW - datetime.timedelta(days=5),
            new_rating=storage.NewRating(show=False),
            features=storage.Features(
                constraints=[
                    storage.Constraint(
                        storage.ConstraintCode.MaxOrderPrice, 50000,
                    ),
                    storage.Constraint(
                        storage.ConstraintCode.MaxOrderWeight, 12,
                    ),
                ],
            ),
            timing=storage.PlaceTiming(extra_preparation=60.0),
            working_intervals=schedule,
        ),
    )
    eats_catalog_storage.add_zone(storage.Zone(working_intervals=schedule))

    @mockserver.json_handler('/eats-offers/v1/offer/match')
    def eats_offers_match(request):
        assert {
            'session_id': 'blablabla',
            'need_prolong': True,
            'parameters': {'location': [0, 0]},
        } == request.json

        return mockserver.make_response(
            status=404,
            response=json.dumps({'code': 'NOT_FOUND', 'message': 'not_found'}),
        )

    @mockserver.json_handler('/eats-offers/v1/offer/set')
    def eats_offers_set(request):
        assert {
            'session_id': 'blablabla',
            'parameters': {'location': [0, 0]},
            'payload': {},
        } == request.json

        expires = (NOW + datetime.timedelta(hours=2)).isoformat('T')

        return {
            'session_id': 'blablabla',
            'request_time': '2021-01-01T12:00:00+03:00',
            'expiration_time': expires,
            'prolong_count': 0,
            'parameters': {
                'delivery_time': '2021-01-01T12:00:00+03:00',
                'location': [37.591503, 55.802998],
            },
            'payload': {},
            'status': 'PAYLOAD_UPDATED',
        }

    prediction.set_place_time(place_id=1, min_minutes=100, max_minutes=500)
    prediction.expected_request = {
        'predicting_at': '2021-01-01T09:00:00+00:00',
        'server_time': '2021-01-01T09:00:00+00:00',
        'user_location': {'lat': 55.802998, 'lon': 37.591503},
        'requested_times': [
            {
                'id': 1,
                'place': {
                    'id': 1,
                    'time_to_delivery': 23,
                    'average_preparation_time': 12.0,
                    'place_increment': 1.0,
                    'region_delivery_time_offset': -10.0,
                    'zone_id': 1.0,
                    'brand_id': 1,
                    'is_fast_food': False,
                    'average_user_rating': 4.8002,
                    'price_category': 1,
                    'location': {'lon': 37.5916, 'lat': 55.8129},
                    'delivery_type': 'native',
                    'courier_type': 'pedestrian',
                },
                'default_times': {
                    'total_time': 36.0,
                    'cooking_time': 12.0,
                    'delivery_time': 23.0,
                    'boundaries': {'min': 30, 'max': 40},
                },
            },
        ],
    }

    delivery_price.set_delivery_conditions(
        [
            {'order_price': 0, 'delivery_cost': 2023},
            {'order_price': 100, 'delivery_cost': 401},
            {'order_price': 10000, 'delivery_cost': 2},
        ],
    )

    delivery_price.set_weight_conditions(weight_conditions)
    delivery_price.set_place_surge(
        {
            'placeId': 1,
            'nativeInfo': {
                'deliveryFee': 199,
                'loadLevel': 91,
                'surgeLevel': 2,
            },
        },
    )

    delivery_price.expected_request = {
        'add_surge_inside_pricing': False,
        'due': '2021-01-01T09:00:00+00:00',
        'offer': '2021-01-01T09:00:00+00:00',
        'place_info': {
            'brand_id': 1,
            'place_id': 1,
            'position': [37.5916, 55.8129],
            'region_id': 1,
            'type': 'native',
            'business_type': 'restaurant',
            'currency': {'sign': '₽'},
        },
        'route_info': {'distance_m': 1101.0703634086447, 'time_sec': 24000.0},
        'user_info': {
            'user_id': '123',
            'device_id': 'test_simple',
            'position': [37.591503, 55.802998],
        },
        'zone_info': {'zone_name': 'Zone Name', 'zone_type': 'pedestrian'},
    }

    @mockserver.json_handler('/eats-core/v1/export/settings/regions-settings')
    def regions_settings(request):
        return {
            'payload': {
                'defaultMarketPlaceOffset': 0,
                'defaultNativeOffset': -10,
                'regionsOptions': [
                    {
                        'nativeMaxDeliveryFee': 1500,
                        'offset': -10,
                        'regionId': 1,
                        'yandexTaxiMaxDeliveryFee': None,
                    },
                ],
                'storeOptions': {'minTime': 10, 'offset': 10},
            },
        }

    response = await slug(
        'coffee_boy_novodmitrovskaya_2k6',
        query={'latitude': 0, 'longitude': 0},
        headers={
            'x-device-id': 'test_simple',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-User': 'user_id=123',
            'X-Eats-Session': 'blablabla',
        },
    )

    assert response.status_code == 200
    assert prediction.times_called == 1
    assert eats_offers_match.times_called == 1
    assert eats_offers_set.times_called == 1
    assert regions_settings.times_called == 2

    assert surge.times_called == 0
    assert delivery_price.times_called == 1

    expected_response = {
        'payload': {
            'foundPlace': {
                'place': {
                    'id': 1,
                    'name': 'Тестовое заведение 1293',
                    'slug': 'coffee_boy_novodmitrovskaya_2k6',
                    'market': False,
                    'tags': [{'id': 1, 'name': 'Завтраки'}],
                    'priceCategory': {
                        'id': 1,
                        'name': '<category-₽><category-₽><category-₽>',
                        'value': 1.0,
                    },
                    'rating': None,
                    'ratingCount': None,
                    'minimalOrderPrice': 0,
                    'minimalDeliveryCost': 0,
                    'isNew': True,
                    'picture': {
                        'uri': (
                            '/images/1387779/71876d2d734cf1c006ba-{w}x{h}.jpg'
                        ),
                        'ratio': 1.33,
                    },
                    'image': themed_picture(
                        '/images/1387779/71876d2d734cf1c006ba-{w}x{h}.jpg',
                    ),
                    'deliveryConditions': 'Доставка 2–1500 ₽',
                    'deliveryThresholds': [
                        {
                            'name': 'на заказ до 99 ₽',
                            'orderPrice': {
                                'min': 0,
                                'decimalMin': '0',
                                'max': 99,
                                'decimalMax': '99',
                            },
                            'deliveryCost': 1500,
                            'decimalDeliveryCost': '1500',
                        },
                        {
                            'name': 'на заказ 100-9999 ₽',
                            'orderPrice': {
                                'min': 100,
                                'decimalMin': '100',
                                'max': 9999,
                                'decimalMax': '9999',
                            },
                            'deliveryCost': 401,
                            'decimalDeliveryCost': '401',
                        },
                        {
                            'name': 'на заказ от 10000 ₽',
                            'orderPrice': {
                                'min': 10000,
                                'decimalMin': '10000',
                                'max': None,
                                'decimalMax': None,
                            },
                            'deliveryCost': 2,
                            'decimalDeliveryCost': '2',
                        },
                    ],
                    'isPromoAvailable': False,
                    'isStore': False,
                    'brand': {'slug': 'coffee_boy_euocq'},
                    'currency': {'sign': '₽', 'code': 'RUB'},
                    'previewDeliveryFee': '',
                    'features': {
                        'ecoPackaging': {'show': False},
                        'delivery': {'isYandexTaxi': False},
                        'map': None,
                        'yandexPlus': None,
                        'badge': None,
                        'favorite': None,
                    },
                    'footerDescription': (
                        'Исполнитель (продавец): '
                        'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ '
                        '"КОФЕ БОЙ", 127015, Москва, ул Вятская, д 27, стр 11,'
                        ' ИНН 7714457772, рег.номер 1207700043759.'
                        '<br>'
                        'Режим работы: с 07:00 до 11:00'
                    ),
                    'business': 'restaurant',
                    'availablePaymentMethods': [1, 2, 3, 4],
                    'type': {'id': 1, 'name': 'Ресторан'},
                    'address': {
                        'location': {
                            'longitude': 37.5916,
                            'latitude': 55.8129,
                        },
                        'city': 'Москва',
                        'short': 'Новодмитровская улица, 2к6',
                    },
                    'sharedLink': (
                        'https://eda.yandex/restaurant/'
                        'coffee_boy_novodmitrovskaya_2k6'
                        '?utm_source=rst_shared_link&utm_medium=referral&'
                        'utm_campaign=superapp_taxi_web'
                    ),
                    'messages': {
                        'constraints': {'title': 'Лимиты', 'footer': ''},
                        'thresholds': {
                            'title': 'Стоимость доставки',
                            'footer': '',
                            'description': message_description,
                        },
                    },
                    'constraints': {
                        'maximum_order_price': {
                            'text': '50000 ₽',
                            'value': 50000.0,
                        },
                        'maximum_order_weight': {
                            'text': '12 кг',
                            'value': 12.0,
                        },
                    },
                    'promos': [],
                    'promoTypes': [],
                    'personalizationStrategy': None,
                    'ratingDescription': None,
                    'regionSlug': 'moscow',
                    'logo': LOGO,
                    'accent_color': [{'theme': 'dark', 'value': '#bada55'}],
                    'service_fee': {
                        'title': SERVICE_FEE_TITLE,
                        'amount': '49',
                        'description': SERVICE_FEE_DESCRIPTION,
                    },
                },
                'locationParams': {
                    'deliveryTime': {'min': 100, 'max': 500},
                    'available': True,
                    'availableNow': True,
                    'availableByTime': True,
                    'availableByLocation': True,
                    'distance': 1.1010703634086447,
                    'availableShippingTypes': [{'type': 'delivery'}],
                    'availableFrom': None,
                    'availableSlug': None,
                    'availableTo': '2021-01-01T11:00:00+00:00',
                    'eatDay': 0,
                    'prepareTime': {'minutes': 0.0, 'readyAt': None},
                    'shippingInfoAction': {
                        'deliveryFee': {'name': '201 ₽'},
                        'message': 'Повышенный спрос',
                    },
                },
                'surge': {
                    'deliveryFee': 201,
                    'description': 'Повышенный спрос',
                    'message': (
                        'Заказов сейчас очень много — чтобы еда приехала '
                        'в срок, стоимость доставки временно увеличена'
                    ),
                    'title': 'Повышенный спрос',
                },
            },
            'availableTimePicker': [
                [
                    '2021-01-01T10:00:00+00:00',
                    '2021-01-01T10:30:00+00:00',
                    '2021-01-01T11:00:00+00:00',
                ],
                [
                    '2021-01-02T08:00:00+00:00',
                    '2021-01-02T08:30:00+00:00',
                    '2021-01-02T09:00:00+00:00',
                    '2021-01-02T09:30:00+00:00',
                    '2021-01-02T10:00:00+00:00',
                    '2021-01-02T10:30:00+00:00',
                    '2021-01-02T11:00:00+00:00',
                ],
            ],
            'currency': {
                'code': 'RUB',
                'sign': '<category-₽>',
                'template': '$VALUE$ $SIGN$$CURRENCY$',
                'text': 'руб.',
            },
        },
    }

    place = expected_response['payload']['foundPlace']['place']
    if weight_thresholds is not None:
        place['weightThresholds'] = weight_thresholds
        place['messages']['weightThresholds'] = {
            'title': 'Доплата за вес',
            'footer': '',
            'description': weight_description,
        }

    assert response.json() == expected_response


@pytest.mark.now('2021-01-01T12:00:00+03:00')
@experiments.INCLUDE_ASSEMBLY_COST
@experiments.currency_sign('sign')
@pytest.mark.eats_regions_cache(file='regions.json')
async def test_without_position(taxi_eats_catalog, eats_catalog_storage):
    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-01-01T10:00:00+03:00'),
            end=parser.parse('2021-01-01T14:00:00+03:00'),
        ),
        storage.WorkingInterval(
            start=parser.parse('2021-01-02T10:00:00+03:00'),
            end=parser.parse('2021-01-02T14:00:00+03:00'),
        ),
    ]

    eats_catalog_storage.add_place(
        storage.Place(
            launched_at=NOW - datetime.timedelta(days=5),
            working_intervals=schedule,
        ),
    )
    eats_catalog_storage.add_zone(storage.Zone(working_intervals=schedule))

    response = await taxi_eats_catalog.get(
        '/eats-catalog/v1/slug/coffee_boy_novodmitrovskaya_2k6',
        headers={
            'x-device-id': 'test_simple',
            'x-platform': 'desktop_web',
            'x-app-version': '1.12.0',
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        'payload': {
            'foundPlace': {
                'place': {
                    'id': 1,
                    'name': 'Тестовое заведение 1293',
                    'slug': 'coffee_boy_novodmitrovskaya_2k6',
                    'market': False,
                    'tags': [{'id': 1, 'name': 'Завтраки'}],
                    'priceCategory': {
                        'id': 1,
                        'name': 'signsignsign',
                        'value': 1.0,
                    },
                    'rating': 4.8,
                    'ratingCount': '123',
                    'minimalOrderPrice': 0,
                    'minimalDeliveryCost': 0,
                    'isNew': True,
                    'picture': {
                        'uri': (
                            '/images/1387779/71876d2d734cf1c006ba-{w}x{h}.jpg'
                        ),
                        'ratio': 1.33,
                    },
                    'image': themed_picture(
                        '/images/1387779/71876d2d734cf1c006ba-{w}x{h}.jpg',
                    ),
                    'deliveryConditions': 'Доставка и сборка 123–262 ₽',
                    'deliveryThresholds': [
                        {
                            'name': 'на заказ до 499 ₽',
                            'orderPrice': {
                                'min': 0,
                                'decimalMin': '0',
                                'max': 499,
                                'decimalMax': '499',
                            },
                            'deliveryCost': 262,
                            'decimalDeliveryCost': '262',
                        },
                        {
                            'name': 'на заказ 500-1999 ₽',
                            'orderPrice': {
                                'min': 500,
                                'decimalMin': '500',
                                'max': 1999,
                                'decimalMax': '1999',
                            },
                            'deliveryCost': 212,
                            'decimalDeliveryCost': '212',
                        },
                        {
                            'name': 'на заказ от 2000 ₽',
                            'orderPrice': {
                                'min': 2000,
                                'decimalMin': '2000',
                                'max': None,
                                'decimalMax': None,
                            },
                            'deliveryCost': 123,
                            'decimalDeliveryCost': '123',
                        },
                    ],
                    'isPromoAvailable': False,
                    'isStore': False,
                    'brand': {'slug': 'coffee_boy_euocq'},
                    'currency': {'sign': '₽', 'code': 'RUB'},
                    'previewDeliveryFee': '',
                    'features': {
                        'ecoPackaging': {'show': False},
                        'delivery': {'isYandexTaxi': False},
                        'badge': None,
                        'favorite': None,
                        'map': None,
                        'yandexPlus': None,
                    },
                    'footerDescription': (
                        'Исполнитель (продавец): '
                        'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ '
                        '"КОФЕ БОЙ", 127015, Москва, ул Вятская, д 27, стр 11,'
                        ' ИНН 7714457772, рег.номер 1207700043759.'
                        '<br>'
                        'Режим работы: с 10:00 до 14:00'
                    ),
                    'business': 'restaurant',
                    'availablePaymentMethods': [1, 2, 4],
                    'type': {'id': 1, 'name': 'Ресторан'},
                    'address': {
                        'location': {
                            'longitude': 37.5916,
                            'latitude': 55.8129,
                        },
                        'city': 'Москва',
                        'short': 'Новодмитровская улица, 2к6',
                    },
                    'sharedLink': (
                        'https://eda.yandex/restaurant/'
                        'coffee_boy_novodmitrovskaya_2k6'
                        '?utm_source=rst_shared_link&utm_medium=referral'
                        '&utm_campaign=web'
                    ),
                    'messages': {
                        'thresholds': {
                            'title': 'Условия сборки и доставки',
                            'footer': (
                                'В стоимость входит'
                                ' доставка и сборка заказа'
                            ),
                            'description': (
                                'Итоговая сумма зависит от'
                                ' стоимости и веса заказа,'
                                ' расстояния между вами и'
                                ' магазином и того, доставляет'
                                ' курьер пешком или на машине.'
                            ),
                        },
                    },
                    'constraints': {},
                    'promos': [],
                    'promoTypes': [],
                    'personalizationStrategy': None,
                    'ratingDescription': 'Хорошо',
                    'regionSlug': 'moscow',
                    'logo': LOGO,
                    'accent_color': [{'theme': 'dark', 'value': '#bada55'}],
                },
                'locationParams': None,
                'surge': None,
            },
            'availableTimePicker': [
                [
                    '2021-01-01T12:00:00+03:00',
                    '2021-01-01T12:30:00+03:00',
                    '2021-01-01T13:00:00+03:00',
                    '2021-01-01T13:30:00+03:00',
                    '2021-01-01T14:00:00+03:00',
                ],
                [
                    '2021-01-02T10:00:00+03:00',
                    '2021-01-02T10:30:00+03:00',
                    '2021-01-02T11:00:00+03:00',
                    '2021-01-02T11:30:00+03:00',
                    '2021-01-02T12:00:00+03:00',
                    '2021-01-02T12:30:00+03:00',
                    '2021-01-02T13:00:00+03:00',
                    '2021-01-02T13:30:00+03:00',
                    '2021-01-02T14:00:00+03:00',
                ],
            ],
            'currency': {
                'code': 'RUB',
                'sign': 'sign',
                'template': '$VALUE$ $SIGN$$CURRENCY$',
                'text': 'руб.',
            },
        },
    }


@pytest.mark.now('2021-01-19T22:25:00+03:00')
async def test_delivery_time(slug, mockserver, eats_catalog_storage):
    @mockserver.json_handler('/eats-core/v1/export/settings/couriers-stats')
    def courier_stats(_):
        return {
            'payload': {
                'pedestrian': {
                    'nearby': {'distance': 0.1, 'tempo': 15, 'fixTime': 1},
                    'near': {'distance': 2, 'tempo': 15, 'fixTime': 6},
                    'far': {'distance': None, 'tempo': 10, 'fixTime': 16},
                    'faraway': {'distance': 4, 'tempo': 3, 'fixTime': 44},
                },
                'bicycle': {
                    'nearby': {'distance': 0.1, 'tempo': 12, 'fixTime': 1},
                    'near': {'distance': 2, 'tempo': 12, 'fixTime': 5},
                    'far': {'distance': None, 'tempo': 12, 'fixTime': 5},
                    'faraway': {'distance': 4, 'tempo': 3, 'fixTime': 44},
                },
                'electric_bicycle': {
                    'nearby': {'distance': 0.1, 'tempo': 12, 'fixTime': 1},
                    'near': {'distance': 2, 'tempo': 12, 'fixTime': 5},
                    'far': {'distance': None, 'tempo': 12, 'fixTime': 5},
                    'faraway': {'distance': 4, 'tempo': 3, 'fixTime': 44},
                },
                'vehicle': {
                    'nearby': {'distance': 0.1, 'tempo': 10, 'fixTime': 1},
                    'near': {'distance': 2, 'tempo': 10, 'fixTime': 6},
                    'far': {'distance': None, 'tempo': 3, 'fixTime': 20},
                    'faraway': {'distance': 4, 'tempo': 3, 'fixTime': 44},
                },
                'motorcycle': {
                    'nearby': {'distance': 0.1, 'tempo': 10, 'fixTime': 1},
                    'near': {'distance': 2, 'tempo': 10, 'fixTime': 6},
                    'far': {'distance': None, 'tempo': 3, 'fixTime': 20},
                    'faraway': {'distance': 4, 'tempo': 3, 'fixTime': 44},
                },
            },
        }

    eats_catalog_storage.add_place(
        storage.Place(
            timing=storage.PlaceTiming(
                average_preparation=17 * 60, extra_preparation=0,
            ),
            location=storage.Location(lon=37.541027, lat=55.79728),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            couriers_type=storage.CouriersType.YandexTaxi,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-19T0:00:00+03:00'),
                    end=parser.parse('2021-01-20T0:00:00+03:00'),
                ),
                storage.WorkingInterval(
                    start=parser.parse('2021-01-20T0:00:00+03:00'),
                    end=parser.parse('2021-01-21T0:00:00+03:00'),
                ),
                storage.WorkingInterval(
                    start=parser.parse('2021-01-21T0:00:00+03:00'),
                    end=parser.parse('2021-01-22T0:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await slug(
        'coffee_boy_novodmitrovskaya_2k6',
        query={'latitude': 55.73442, 'longitude': 37.583948},
    )

    assert response.status_code == 200
    assert courier_stats.times_called != 0

    data = response.json()
    place = data['payload']['foundPlace']

    assert place['locationParams']['deliveryTime'] == {'min': 50, 'max': 60}

    assert (
        place['locationParams']['availableTo'] == '2021-01-20T00:00:00+03:00'
    )
    assert data['payload']['availableTimePicker'] == [
        [
            '2021-01-19T23:30:00+03:00',
            '2021-01-20T00:00:00+03:00',
            '2021-01-20T00:30:00+03:00',
            '2021-01-20T01:00:00+03:00',
            '2021-01-20T01:30:00+03:00',
            '2021-01-20T02:00:00+03:00',
            '2021-01-20T02:30:00+03:00',
            '2021-01-20T03:00:00+03:00',
            '2021-01-20T03:30:00+03:00',
            '2021-01-20T04:00:00+03:00',
            '2021-01-20T04:30:00+03:00',
            '2021-01-20T05:00:00+03:00',
            '2021-01-20T05:30:00+03:00',
            '2021-01-20T06:00:00+03:00',
        ],
        [
            '2021-01-20T06:30:00+03:00',
            '2021-01-20T07:00:00+03:00',
            '2021-01-20T07:30:00+03:00',
            '2021-01-20T08:00:00+03:00',
            '2021-01-20T08:30:00+03:00',
            '2021-01-20T09:00:00+03:00',
            '2021-01-20T09:30:00+03:00',
            '2021-01-20T10:00:00+03:00',
            '2021-01-20T10:30:00+03:00',
            '2021-01-20T11:00:00+03:00',
            '2021-01-20T11:30:00+03:00',
            '2021-01-20T12:00:00+03:00',
            '2021-01-20T12:30:00+03:00',
            '2021-01-20T13:00:00+03:00',
            '2021-01-20T13:30:00+03:00',
            '2021-01-20T14:00:00+03:00',
            '2021-01-20T14:30:00+03:00',
            '2021-01-20T15:00:00+03:00',
            '2021-01-20T15:30:00+03:00',
            '2021-01-20T16:00:00+03:00',
            '2021-01-20T16:30:00+03:00',
            '2021-01-20T17:00:00+03:00',
            '2021-01-20T17:30:00+03:00',
            '2021-01-20T18:00:00+03:00',
            '2021-01-20T18:30:00+03:00',
            '2021-01-20T19:00:00+03:00',
            '2021-01-20T19:30:00+03:00',
            '2021-01-20T20:00:00+03:00',
            '2021-01-20T20:30:00+03:00',
            '2021-01-20T21:00:00+03:00',
            '2021-01-20T21:30:00+03:00',
            '2021-01-20T22:00:00+03:00',
            '2021-01-20T22:30:00+03:00',
            '2021-01-20T23:00:00+03:00',
            '2021-01-20T23:30:00+03:00',
        ],
    ]


@pytest.mark.parametrize(
    'user_agent, place_strategy, response_code',
    [
        pytest.param(
            'MagnitApp_Android/1.2.2',
            'default',
            404,
            id='magnit app -> eda place',
        ),
        pytest.param(
            'MagnitApp_Ios/1.2.2',
            'whitelabel_only',
            200,
            id='magnit app -> whitelabel place',
        ),
        pytest.param(
            'android_app',
            'whitelabel_only',
            404,
            id='eda app -> whitelabel place',
        ),
        pytest.param('ios_app', 'default', 200, id='eda app -> eda place'),
    ],
)
@pytest.mark.now('2021-01-01T12:00:00+03:00')
async def test_availability_strategy(
        slug, user_agent, place_strategy, response_code, eats_catalog_storage,
):
    eats_catalog_storage.add_place(
        storage.Place(
            launched_at=NOW - datetime.timedelta(days=5),
            features=storage.Features(availability_strategy=place_strategy),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+03:00'),
                    end=parser.parse('2021-01-01T14:00:00+03:00'),
                ),
                storage.WorkingInterval(
                    start=parser.parse('2021-01-02T10:00:00+03:00'),
                    end=parser.parse('2021-01-02T14:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await slug(
        'coffee_boy_novodmitrovskaya_2k6',
        query={'latitude': 55.802998, 'longitude': 37.591503},
        headers={
            'user-agent': user_agent,
            'x-device-id': 'test_simple',
            'x-platform': 'desktop_web',
            'x-app-version': '1.12.0',
        },
    )

    assert response.status_code == response_code


async def test_slug_promo(slug, mockserver, eats_catalog_storage):
    eats_catalog_storage.add_place(
        storage.Place(launched_at=NOW - datetime.timedelta(days=5)),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+03:00'),
                    end=parser.parse('2021-01-01T14:00:00+03:00'),
                ),
                storage.WorkingInterval(
                    start=parser.parse('2021-01-02T10:00:00+03:00'),
                    end=parser.parse('2021-01-02T14:00:00+03:00'),
                ),
            ],
        ),
    )

    @mockserver.json_handler('/eats-core-promo/server/api/v1/promo/active')
    def _active(_):
        return {
            'cursor': '',
            'promos': [
                {
                    'id': 1,
                    'name': 'Бесплатные тесты',
                    'description': 'При написании фичи, тесты в подарок',
                    'type': {
                        'id': 1,
                        'name': 'Тесты в подарок',
                        'picture': 'http://istock/harold',
                        'detailed_picture': 'http://istock/pepe',
                    },
                    'places': [{'id': 1, 'disabled_by_surge': False}],
                },
                {
                    'id': 2,
                    'name': 'Без описания',
                    'type': {
                        'id': 1,
                        'name': 'Тесты в подарок',
                        'picture': 'http://istock/harold',
                        'detailed_picture': 'http://istock/pepe',
                    },
                    'places': [{'id': 1, 'disabled_by_surge': False}],
                },
            ],
        }

    response = await slug(
        'coffee_boy_novodmitrovskaya_2k6',
        query={'latitude': 55.802998, 'longitude': 37.591503},
    )

    assert response.status_code == 200

    place = response.json()['payload']['foundPlace']['place']
    assert place['promos'] == [
        {
            'id': 1,
            'name': 'Бесплатные тесты',
            'description': 'При написании фичи, тесты в подарок',
            'type': {
                'id': 1,
                'name': 'Тесты в подарок',
                'pictureUri': 'http://istock/harold',
                'detailedPictureUrl': 'http://istock/pepe',
            },
        },
        {
            'id': 2,
            'name': 'Без описания',
            'description': '',
            'type': {
                'id': 1,
                'name': 'Тесты в подарок',
                'pictureUri': 'http://istock/harold',
                'detailedPictureUrl': 'http://istock/pepe',
            },
        },
    ]
    assert place['promoTypes'] == [
        {
            'id': 1,
            'name': 'Тесты в подарок',
            'pictureUri': 'http://istock/harold',
            'detailedPictureUrl': 'http://istock/pepe',
        },
    ]


@experiments.DISABLE_PROMOS
async def test_slug_promo_disable(slug, mockserver, eats_catalog_storage):
    eats_catalog_storage.add_place(storage.Place(slug='no_promo'))
    eats_catalog_storage.add_zone(storage.Zone())

    @mockserver.json_handler('/eats-core-promo/server/api/v1/promo/active')
    def _active(_):
        return {
            'cursor': '',
            'promos': [
                {
                    'id': 1,
                    'name': 'Бесплатные тесты',
                    'description': 'При написании фичи, тесты в подарок',
                    'type': {
                        'id': 1,
                        'name': 'Тесты в подарок',
                        'picture': 'http://istock/harold',
                        'detailed_picture': 'http://istock/pepe',
                    },
                    'places': [{'id': 1, 'disabled_by_surge': False}],
                },
                {
                    'id': 2,
                    'name': 'Без описания',
                    'type': {
                        'id': 1,
                        'name': 'Тесты в подарок',
                        'picture': 'http://istock/harold',
                        'detailed_picture': 'http://istock/pepe',
                    },
                    'places': [{'id': 1, 'disabled_by_surge': False}],
                },
            ],
        }

    response = await slug(
        'no_promo', query={'latitude': 55.802998, 'longitude': 37.591503},
    )

    assert response.status_code == 200

    place = response.json()['payload']['foundPlace']['place']
    assert place['promos'] == []
    assert place['promoTypes'] == []


async def test_empty_delivery_time_string(slug, eats_catalog_storage):
    eats_catalog_storage.add_place(storage.Place())

    response = await slug(
        'coffee_boy_novodmitrovskaya_2k6',
        query={
            'latitude': 55.802998,
            'longitude': 37.591503,
            'deliveryTime': '',
        },
    )

    assert response.status_code == 200


@pytest.mark.now('2021-01-01T12:00:00+03:00')
@configs.places_storage_settings(min_delivery_minutes=5)
@pytest.mark.parametrize(
    'market_time, boundaries, delivery_time',
    [
        pytest.param(40 * 60, {'min': 40, 'max': 40}, 40, id='40 minutes'),
        pytest.param(1 * 60, {'min': 1, 'max': 1}, 1, id='1 minute'),
        pytest.param(0, {'min': 145, 'max': 145}, 23, id='zero time'),
    ],
)
async def test_market_time(
        slug,
        eats_catalog_storage,
        prediction,
        market_time,
        boundaries,
        delivery_time,
):
    """
    EDACAT-791: тест проверяет, что время для маркетплейса рассчитывается
    только исходя из значения market_avg_time на зоне заведения
    """
    eats_catalog_storage.add_place(
        storage.Place(
            place_type=storage.PlaceType.Marketplace,
            timing=storage.PlaceTiming(
                preparation=60 * 60,
                extra_preparation=60 * 60,
                average_preparation=60 * 60,
            ),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            timing=storage.ZoneTimings(market_avg_time=market_time),
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+03:00'),
                    end=parser.parse('2021-01-01T14:00:00+03:00'),
                ),
            ],
        ),
    )

    prediction.expected_request = {
        'predicting_at': '2021-01-01T09:00:00+00:00',
        'server_time': '2021-01-01T09:00:00+00:00',
        'user_location': {'lat': 55.802998, 'lon': 37.591503},
        'requested_times': [
            {
                'id': 1,
                'place': {
                    'id': 1,
                    'time_to_delivery': delivery_time,
                    'average_preparation_time': 60.0,
                    'place_increment': 60.0,
                    'region_delivery_time_offset': 0.0,
                    'zone_id': 1.0,
                    'brand_id': 1,
                    'is_fast_food': False,
                    'average_user_rating': 4.8002,
                    'shown_rating': 4.8002,
                    'price_category': 1,
                    'location': {'lat': 55.8129, 'lon': 37.5916},
                    'delivery_type': 'marketplace',
                    'courier_type': 'pedestrian',
                },
                'default_times': {
                    'total_time': delivery_time + 60 + 60,
                    'cooking_time': 60.0,
                    'delivery_time': delivery_time,
                    'boundaries': boundaries,
                },
            },
        ],
    }

    response = await slug(
        'coffee_boy_novodmitrovskaya_2k6',
        query={'latitude': 55.802998, 'longitude': 37.591503},
        headers={
            'x-device-id': 'testsuite',
            'x-platform': 'ios_app',
            'x-app-version': '5.7.0',
        },
    )

    data = response.json()

    params = data['payload']['foundPlace']['locationParams']

    assert response.status_code == 200
    assert params['deliveryTime'] == boundaries


@pytest.mark.now('2021-05-25T16:22:00+03:00')
async def test_slug_available_from(slug, eats_catalog_storage):

    """
    Тест проверяет, что для заведений, которые открываетются позже чем
    конец следующих суток, но меньше чем через 48 часов от текущего
    момента availableFrom не будет показывать время за пределами следующих
    суток, на которое нельзя оформить предзаказ
    """

    eats_catalog_storage.add_place(
        storage.Place(place_id=1, slug='not_available'),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-05-27T10:00:00+03:00'),
                    end=parser.parse('2021-05-27T15:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await slug(
        'not_available', query={'latitude': 55.802998, 'longitude': 37.591503},
    )

    assert response.status_code == 200

    data = response.json()
    location_params = data['payload']['foundPlace']['locationParams']

    assert not location_params['availableFrom']


@pytest.mark.now('2021-01-01T12:00:00+03:00')
@experiments.BRAND_COLOR_OVERRIDES
async def test_slug_brand_colors_logos_overriden(
        taxi_eats_catalog, eats_catalog_storage,
):
    brand_logos = [
        storage.BrandUILogo(theme='dark', size='small'),
        storage.BrandUILogo(theme='light', size='small'),
        storage.BrandUILogo(size='medium'),
    ]
    eats_catalog_storage.add_place(
        storage.Place(
            launched_at=NOW - datetime.timedelta(days=5),
            features=storage.Features(brand_ui_logos=brand_logos),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+03:00'),
                    end=parser.parse('2021-01-01T14:00:00+03:00'),
                ),
                storage.WorkingInterval(
                    start=parser.parse('2021-01-02T10:00:00+03:00'),
                    end=parser.parse('2021-01-02T14:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await taxi_eats_catalog.get(
        '/eats-catalog/v1/slug/coffee_boy_novodmitrovskaya_2k6',
        headers={
            'x-device-id': 'test_simple',
            'x-platform': 'desktop_web',
            'x-app-version': '1.12.0',
        },
    )

    assert response.status_code == 200

    data = response.json()
    place = data['payload']['foundPlace']['place']

    assert place['accent_color'] == [
        {'theme': 'light', 'value': '#000000'},
        {'theme': 'dark', 'value': '#FFFFFF'},
    ]

    assert place['logo'] == [
        {
            'theme': 'dark',
            'value': [
                {'size': 'small', 'logo_url': 'dark_url'},
                {
                    'logo_url': (
                        'https://avatars.mds.yandex.net/get-eda/aaaaaa/214x140'
                    ),
                    'size': 'medium',
                },
            ],
        },
        {
            'theme': 'light',
            'value': [{'logo_url': 'light_url', 'size': 'small'}],
        },
    ]


@experiments.BRAND_COLOR_OVERRIDES
async def test_slug_partial_logo_override(
        taxi_eats_catalog, eats_catalog_storage,
):
    eats_catalog_storage.add_place(storage.Place())

    response = await taxi_eats_catalog.get(
        '/eats-catalog/v1/slug/coffee_boy_novodmitrovskaya_2k6',
        headers={
            'x-device-id': 'test_simple',
            'x-platform': 'desktop_web',
            'x-app-version': '1.12.0',
        },
    )

    assert response.status_code == 200

    data = response.json()
    place = data['payload']['foundPlace']['place']

    assert place['logo'] == [
        {
            'theme': 'dark',
            'value': [{'size': 'small', 'logo_url': 'dark_url'}],
        },
        {
            'theme': 'light',
            'value': [{'logo_url': 'light_url', 'size': 'small'}],
        },
    ]


@pytest.mark.now('2021-05-07T13:00:00+03:00')
@pytest.mark.parametrize(
    'place_shcedule,timepicker',
    [
        pytest.param(
            [],
            [
                [
                    '2021-05-07T13:00:00+03:00',
                    '2021-05-07T13:30:00+03:00',
                    '2021-05-07T14:00:00+03:00',
                    '2021-05-07T14:30:00+03:00',
                    '2021-05-07T15:00:00+03:00',
                    '2021-05-07T15:30:00+03:00',
                    '2021-05-07T16:00:00+03:00',
                ],
                [],
            ],
            id='no schedule config off',
        ),
        pytest.param(
            [
                storage.WorkingInterval(
                    start=parser.parse('2021-05-07T13:00:00+03:00'),
                    end=parser.parse('2021-05-07T15:00:00+03:00'),
                ),
            ],
            [
                [
                    '2021-05-07T13:00:00+03:00',
                    '2021-05-07T13:30:00+03:00',
                    '2021-05-07T14:00:00+03:00',
                    '2021-05-07T14:30:00+03:00',
                    '2021-05-07T15:00:00+03:00',
                    '2021-05-07T15:30:00+03:00',
                    '2021-05-07T16:00:00+03:00',
                ],
                [],
            ],
            id='with schedule config off',
        ),
        pytest.param(
            [],
            [
                [
                    '2021-05-07T13:00:00+03:00',
                    '2021-05-07T13:30:00+03:00',
                    '2021-05-07T14:00:00+03:00',
                    '2021-05-07T14:30:00+03:00',
                    '2021-05-07T15:00:00+03:00',
                    '2021-05-07T15:30:00+03:00',
                    '2021-05-07T16:00:00+03:00',
                ],
                [],
            ],
            marks=(
                configs.places_storage_settings(
                    enable_place_schedule_filter=True,
                    place_schedule_filter_ignore_empty=True,
                )
            ),
            id='no schedule config on and ignore',
        ),
        pytest.param(
            [],
            [[], []],
            marks=(
                configs.places_storage_settings(
                    enable_place_schedule_filter=True,
                    place_schedule_filter_ignore_empty=False,
                )
            ),
            id='no schedule config on',
        ),
        pytest.param(
            [
                storage.WorkingInterval(
                    start=parser.parse('2021-05-07T14:00:00+03:00'),
                    end=parser.parse('2021-05-07T16:00:00+03:00'),
                ),
            ],
            [
                [
                    '2021-05-07T14:00:00+03:00',
                    '2021-05-07T14:30:00+03:00',
                    '2021-05-07T15:00:00+03:00',
                    '2021-05-07T15:30:00+03:00',
                    '2021-05-07T16:00:00+03:00',
                ],
                [],
            ],
            marks=(
                configs.places_storage_settings(
                    enable_place_schedule_filter=True,
                    place_schedule_filter_ignore_empty=False,
                )
            ),
            id='with schedule config on',
        ),
        pytest.param(
            [
                storage.WorkingInterval(
                    start=parser.parse('2021-05-07T14:00:00+03:00'),
                    end=parser.parse('2021-05-07T16:00:00+03:00'),
                ),
            ],
            [
                [
                    '2021-05-07T14:00:00+03:00',
                    '2021-05-07T14:30:00+03:00',
                    '2021-05-07T15:00:00+03:00',
                    '2021-05-07T15:30:00+03:00',
                    '2021-05-07T16:00:00+03:00',
                ],
                [],
            ],
            marks=(
                configs.places_storage_settings(
                    enable_place_schedule_filter=True,
                    place_schedule_filter_ignore_empty=True,
                )
            ),
            id='with schedule config on ignore',
        ),
        pytest.param(
            [
                storage.WorkingInterval(
                    start=parser.parse('2021-05-07T14:00:00+03:00'),
                    end=parser.parse('2021-05-07T16:00:00+03:00'),
                ),
            ],
            [[], []],
            marks=(experiments.DISABLE_PREORDER),
            id='preorder disabled',
        ),
    ],
)
async def test_place_schedule_filter(
        taxi_eats_catalog, eats_catalog_storage, place_shcedule, timepicker,
):
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1, slug='some', working_intervals=place_shcedule,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-05-07T11:00:00+03:00'),
                    end=parser.parse('2021-05-07T16:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await taxi_eats_catalog.get(
        '/eats-catalog/v1/slug/some',
        headers={
            'x-device-id': 'test_simple',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data['payload']['availableTimePicker'] == timepicker


@pytest.mark.parametrize(
    'expected_id, expected_response_code',
    [
        pytest.param(1, 200, id='no filter'),
        pytest.param(
            None,
            404,
            marks=(experiments.filter_source_response(brand_ids=[1])),
            id='brand fiter',
        ),
        pytest.param(
            None,
            404,
            marks=(experiments.filter_source_response(place_ids=[1])),
            id='place filter',
        ),
        pytest.param(
            None,
            404,
            marks=experiments.always_match(
                name='eats_places_filter_random_places',
                consumer='eats-catalog-places-storage',
                value={'brand_ids': [], 'place_ids': [1]},
            ),
            id='random place filter',
        ),
    ],
)
async def test_filter_source_response(
        slug, eats_catalog_storage, expected_id, expected_response_code,
):
    """
    Проверяет применение эксперимента filter_source_response, который
    отфильтровывает заведения из выдачи при поиске
    """

    def search(request):
        if 'place_slug' in request.json:
            return {'ids': [{'place_id': 1, 'zone_ids': [1]}]}

        return {
            'ids': [
                {'place_id': 1, 'zone_ids': [1]},
                {'place_id': 2, 'zone_ids': [2]},
            ],
        }

    eats_catalog_storage.overide_search(search)

    for i in range(1, 3):
        eats_catalog_storage.add_place(
            storage.Place(
                slug=f'place_{i}', place_id=i, brand=storage.Brand(brand_id=1),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=i,
                place_id=i,
                shipping_type=storage.ShippingType.Delivery,
            ),
        )

    response = await slug(
        'place_1', query={'latitude': 55.802998, 'longitude': 37.591503},
    )

    assert response.status_code == expected_response_code
    if expected_id is not None:
        data = response.json()
        assert data['payload']['foundPlace']['place']['id'] == expected_id


ENABLE_PROLONGATION = pytest.mark.config(
    EATS_CATALOG_OFFER={'prolongation': {'place_slug': True}},
)

DISABLE_PROLONGATION = pytest.mark.config(
    EATS_CATALOG_OFFER={'prolongation': {'place_slug': False}},
)


@pytest.mark.parametrize(
    'expected_prolong',
    [
        pytest.param(True, id='offer prolong expected, default config'),
        pytest.param(
            True,
            id='offer prolong expected by config',
            marks=ENABLE_PROLONGATION,
        ),
        pytest.param(
            False,
            id='no offer prolong expected by config',
            marks=DISABLE_PROLONGATION,
        ),
    ],
)
async def test_offer_prolongation_config(slug, offers, expected_prolong):
    offers.match_request(
        {
            'need_prolong': expected_prolong,
            'parameters': {'location': [37.591503, 55.802998]},
            'session_id': 'blablabla',
        },
    )

    response = await slug(
        'place_1',
        query={'latitude': 55.802998, 'longitude': 37.591503},
        headers={'X-Eats-User': 'user_id=123', 'X-Eats-Session': 'blablabla'},
    )

    assert response.status_code == 404
    assert offers.match_times_called == 1


DESCRIPTION_TRANSLATIONS = pytest.mark.translations(
    **{
        'eats-catalog': {
            'slug.footer_description.extra.state_register_info': {
                'ru': (
                    'Registered number %(state_register_number)s, '
                    'date: %(state_register_date)s'
                ),
            },
            'slug.footer_description.extra.review_book_location': {
                'ru': 'Random place: %(review_book_location)s',
            },
            'slug.footer_description.extra.registration_date': {
                'ru': 'Random date: %(registration_date)s',
            },
            'slug.footer_description.extra.consumer_requests_contacts': {
                'ru': (
                    'Customer request contacts: %(consumer_requests_contacts)s'
                ),
            },
            'slug.footer_description.extra.payment_method': {
                'ru': 'Payment: %(payment_method)s',
            },
            'slug.footer_description.extra.shipping_type': {
                'ru': 'Shipping: Курьер',
            },
            'slug.footer_description.extra.consumer_protection_contact': {
                'ru': 'No protection: %(consumer_protection_contact)s',
            },
            'slug.footer_description.extra.retailer_contacts': {
                'ru': 'Phone me: %(retailer_contacts)s',
            },
            'slug.footer_description.extra.check_info': {
                'ru': 'Check info: %(check_additional_info)s',
            },
        },
    },
)


@pytest.mark.parametrize(
    'expected_description',
    [
        pytest.param(
            (
                'Исполнитель (продавец): '
                'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "КОФЕ БОЙ", '
                '127015, Москва, ул Вятская, д 27, стр 11, ИНН 7714457772, '
                'рег.номер 1207700043759.'
                '<br><br>Random place: Москва, Новодмитровская улица, 2к6'
                '<br><br>Customer request contacts: Отдел торговли и услуг'
                '<br><br>Payment: Онлайн'
                '<br><br>Shipping: Курьер'
                '<br><br>No protection: example@yandex.ru'
                '<br><br>Check info: url/0mWL4aKGOMNZ0w'
                '<br><br>Cтоимость упаковочных материалов'
            ),
            marks=(
                configs.extra_legal_info(
                    '1',
                    consumer_protection_contact='example@yandex.ru',
                    consumer_requests_contacts='Отдел торговли и услуг',
                    check_additional_info='url/0mWL4aKGOMNZ0w'
                    '<br><br>Cтоимость упаковочных материалов',
                    review_book_location='Москва, Новодмитровская улица, 2к6',
                ),
                DESCRIPTION_TRANSLATIONS,
            ),
            id='partial config',
        ),
        pytest.param(
            (
                'Исполнитель (продавец): '
                'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "КОФЕ БОЙ", '
                '127015, Москва, ул Вятская, д 27, стр 11, ИНН 7714457772, '
                'рег.номер 1207700043759.'
                '<br><br>Random place: Москва, Новодмитровская улица, 2к6'
                '<br><br>Customer request contacts: Отдел торговли и услуг'
                '<br><br>Payment: Онлайн'
                '<br><br>Shipping: Курьер'
                '<br><br>Check info: url/0mWL4aKGOMNZ0w'
            ),
            marks=(
                configs.extra_legal_info(
                    '1',
                    consumer_requests_contacts='Отдел торговли и услуг',
                    check_additional_info='url/0mWL4aKGOMNZ0w',
                    review_book_location='Москва, Новодмитровская улица, 2к6',
                ),
                DESCRIPTION_TRANSLATIONS,
            ),
            id='partial config',
        ),
        pytest.param(
            (
                'Исполнитель (продавец): '
                'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "КОФЕ БОЙ", '
                '127015, Москва, ул Вятская, д 27, стр 11, ИНН 7714457772, '
                'рег.номер 1207700043759.'
                '<br><br>Registered number 123, date: 03.10.2021'
                '<br><br>Random place: Москва, Новодмитровская улица, 2к6'
                '<br><br>Customer request contacts: Отдел торговли и услуг'
                '<br><br>Payment: Онлайн'
                '<br><br>Shipping: Курьер'
                '<br><br>Check info: url/0mWL4aKGOMNZ0w'
            ),
            marks=[
                configs.extra_legal_info(
                    '1',
                    state_register_date='2021-10-03T03:14:00+03:00',
                    state_register_number='123',
                    consumer_requests_contacts='Отдел торговли и услуг',
                    check_additional_info='url/0mWL4aKGOMNZ0w',
                    review_book_location='Москва, Новодмитровская улица, 2к6',
                ),
                DESCRIPTION_TRANSLATIONS,
            ],
            id='state register info',
        ),
        pytest.param(
            (
                'Исполнитель (продавец): '
                'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ '
                '"КОФЕ БОЙ", 127015, Москва, ул Вятская, д 27, стр 11,'
                ' ИНН 7714457772, рег.номер 1207700043759.'
            ),
            id='no config',
        ),
        pytest.param(
            (
                'Исполнитель (продавец): '
                'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "КОФЕ БОЙ", '
                '127015, Москва, ул Вятская, д 27, стр 11, ИНН 7714457772, '
                'рег.номер 1207700043759.'
                '<br><br>Registered number 123, date: 03.10.2021'
                '<br><br>Random place: Москва, Новодмитровская улица, 2к6'
                '<br><br>Random date: 02.10.2021'
                '<br><br>Customer request contacts: Отдел торговли и услуг'
                '<br><br>Payment: Онлайн'
                '<br><br>Shipping: Курьер'
                '<br><br>No protection: example@yandex.ru'
                '<br><br>Phone me: +012923123'
                '<br><br>Check info: url/0mWL4aKGOMNZ0w'
                '<br><br>Cтоимость упаковочных материалов'
            ),
            marks=[
                configs.extra_legal_info(
                    '1',
                    date_of_registration='2021-10-02T03:14:00+03:00',
                    consumer_protection_contact='example@yandex.ru',
                    retailer_contacts='+012923123',
                    state_register_date='2021-10-03T03:14:00+03:00',
                    state_register_number='123',
                    consumer_requests_contacts='Отдел торговли и услуг',
                    check_additional_info='url/0mWL4aKGOMNZ0w'
                    '<br><br>Cтоимость упаковочных материалов',
                    review_book_location='Москва, Новодмитровская улица, 2к6',
                ),
                DESCRIPTION_TRANSLATIONS,
            ],
            id='full config',
        ),
        pytest.param(
            (
                'Исполнитель (продавец): '
                'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "КОФЕ БОЙ", '
                '127015, Москва, ул Вятская, д 27, стр 11, ИНН 7714457772, '
                'рег.номер 1207700043759.'
            ),
            marks=[
                configs.extra_legal_info(
                    '1',
                    date_of_registration='2021-10-02T03:14:00+03:00',
                    consumer_protection_contact='example@yandex.ru',
                    retailer_contacts='+012923123',
                    state_register_date='2021-10-02T03:14:00+03:00',
                    state_register_number='123',
                    consumer_requests_contacts='Отдел торговли и услуг',
                    check_additional_info='url/0mWL4aKGOMNZ0w'
                    '<br><br>Cтоимость упаковочных материалов',
                    review_book_location='Москва, Новодмитровская улица, 2к6',
                ),
            ],
            id='full config no translations',
        ),
    ],
)
async def test_extra_description(
        slug, eats_catalog_storage, expected_description,
):

    eats_catalog_storage.add_place(
        storage.Place(
            slug='place_1', place_id=1, brand=storage.Brand(brand_id=1),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1, place_id=1, shipping_type=storage.ShippingType.Delivery,
        ),
    )

    response = await slug(
        'place_1',
        query={'latitude': 55.802998, 'longitude': 37.591503},
        headers={'x-request-language': 'ru'},
    )

    assert response.status_code == 200

    data = response.json()
    description = data['payload']['foundPlace']['place']['footerDescription']

    assert description == expected_description


@pytest.mark.now('2021-12-27T16:07:00+03:00')
@pytest.mark.parametrize(
    'delivery_time,timepicker,available_shipping',
    [
        pytest.param(
            '2021-12-27T16:07:00+03:00',
            [
                [
                    '2021-12-27T17:00:00+03:00',
                    '2021-12-27T17:30:00+03:00',
                    '2021-12-27T18:00:00+03:00',
                ],
                [],
            ],
            set(['delivery', 'pickup']),
            id='ASAP, preorder enabled',
        ),
        pytest.param(
            '2021-12-27T16:30:00+03:00',
            [
                [
                    '2021-12-27T17:00:00+03:00',
                    '2021-12-27T17:30:00+03:00',
                    '2021-12-27T18:00:00+03:00',
                ],
                [],
            ],
            set(['delivery', 'pickup']),
            id='preorder, preorder enabled',
        ),
        pytest.param(
            '2021-12-27T16:07:00+03:00',
            [[], []],
            set(['delivery', 'pickup']),
            marks=experiments.DISABLE_PREORDER,
            id='ASAP, preorder disabled',
        ),
        pytest.param(
            '2021-12-27T16:30:00+03:00',
            [[], []],
            set(['delivery', 'pickup']),
            marks=experiments.DISABLE_PREORDER,
            id='preorder, preorder disabled',
        ),
    ],
)
async def test_disable_preorder(
        slug,
        eats_catalog_storage,
        delivery_time,
        timepicker,
        available_shipping,
):

    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-12-27T11:00:00+03:00'),
            end=parser.parse('2021-12-27T18:00:00+03:00'),
        ),
    ]

    eats_catalog_storage.add_place(
        storage.Place(
            slug='place_1', place_id=1, brand=storage.Brand(brand_id=1),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=schedule,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=2,
            place_id=1,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=schedule,
        ),
    )

    response = await slug(
        'place_1',
        query={
            'latitude': 55.802998,
            'longitude': 37.591503,
            'deliveryTime': delivery_time,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data['payload']['availableTimePicker'] == timepicker

    shipping_types = set([])
    found_place = data['payload']['foundPlace']

    if (
            'locationParams' in found_place
            and 'availableShippingTypes' in found_place['locationParams']
    ):
        shipping_types = set(
            item['type']
            for item in found_place['locationParams']['availableShippingTypes']
        )

    assert shipping_types == available_shipping


@pytest.mark.now('2022-01-21T14:10:00+03:00')
@pytest.mark.parametrize(
    'supports_preorder, timepicker',
    [
        pytest.param(
            True, [['2022-01-21T15:00:00+03:00'], []], id='preorder enabled',
        ),
        pytest.param(False, [[], []], id='preorder disabled'),
        pytest.param(
            False,
            [[], []],
            marks=experiments.USE_CUSTOMER_SLOTS_SHARED,
            id='preorder disabled with slots shared',
        ),
    ],
)
async def test_preorder_support(
        slug, eats_catalog_storage, supports_preorder, timepicker,
):
    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2022-01-21T10:00:00+03:00'),
            end=parser.parse('2022-01-21T15:00:00+03:00'),
        ),
    ]

    eats_catalog_storage.add_place(
        storage.Place(
            slug='place_1',
            place_id=1,
            brand=storage.Brand(brand_id=1),
            business=storage.Business.Shop,
            features=storage.Features(supports_preordering=supports_preorder),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=schedule,
        ),
    )

    response = await slug(
        'place_1', query={'latitude': 55.802998, 'longitude': 37.591503},
    )

    assert response.status_code == 200

    data = response.json()

    assert data['payload']['availableTimePicker'] == timepicker
