# pylint: disable=C5521
from base64 import b64decode
from base64 import b64encode
import datetime
import os
import urllib

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from dateutil import parser
import pytest

from eats_catalog import experiments
from eats_catalog import storage

NOW = parser.parse('2021-01-01T12:00:00+03:00')

YAMAPS_URI = (
    'https://yandex.ru/maps?client=777&'
    'rtext=55.72556335763928%2C36.879730224609375~'
    '55.8129%2C37.5916&rtt=pd'
)
YAMAPS_URI_SIGN = (
    'f4rTHDuUFUdXBhpxQru%2Fat7fKC%2FHhCNeNrih0dHA%2BFA'
    'BxdC6TnF8pEUMoTKC6sBM6KueVN9NaqJCLeWGButVsA%3D%3D'
)

YAMAPS_DEEPLINK = (
    'yandexmaps://maps.yandex.ru?client=777&'
    'rtext=55.72556335763928%2C36.879730224609375~'
    '55.8129%2C37.5916&rtt=pd'
)
YAMAPS_DEEPLINK_SIGN = (
    'd4VwLiNHYC4yN4r%2FlTOJA%2Bsy8%2FKNfJFdmbdd4t8g3%2FV'
    'UXXNbN0KuLM8wphzcV9uUjRcThwHUQz3%2FnFD426amSw%3D%3D'
)


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


PICKUP_MESSAGES_TRANSLATION = pytest.mark.translations(
    **{
        'eats-catalog': {
            'text.alcohol_shops.rules': {'ru': 'rules text'},
            'text.alcohol_shops.licenses': {'ru': 'licenses text'},
            'text.message.pickup.title': {'ru': 'Самовывоз'},
            'text.message.pickup.description': {
                'ru': 'Соберем заказ от %(assembling)s минут',
            },
            'text.message.pickup.footer': {
                'ru': 'Заказ будет храниться %(storage_time)s часа',
            },
        },
    },
)


def yamaps_uri_with_sign(uri, sign):
    return uri + '&signature=' + sign


def yamaps_sign_verify(data, sign):
    path_to_key = os.path.join(
        os.path.dirname(__file__),
        'static',
        'default',
        'yamaps',
        'public_key.pem',
    )
    with open(path_to_key) as file:
        public_key = RSA.importKey(file.read())
    hash_data = SHA256.new(bytes(data, encoding='utf-8'))
    signer = PKCS1_v1_5.new(public_key)
    # signer.verify is not callable
    # pylint: disable=not-callable
    return signer.verify(hash_data, b64decode(urllib.parse.unquote(sign)))
    # pylint: enable=not-callable


def yamaps_sign(data):
    path_to_key = os.path.join(
        os.path.dirname(__file__),
        'static',
        'default',
        'yamaps',
        'private_key.pem',
    )
    with open(path_to_key) as file:
        private_key = RSA.importKey(file.read())
    hash_data = SHA256.new(bytes(data, encoding='utf-8'))
    signer = PKCS1_v1_5.new(private_key)
    return urllib.parse.quote(b64encode(signer.sign(hash_data)), safe='')


def yamaps_check(uri, expected_uri, expected_sign):
    sign = yamaps_sign(expected_uri)
    assert sign == expected_sign
    assert uri == expected_uri + '&signature=' + sign
    assert yamaps_sign_verify(expected_uri, sign) is True


def themed_picture(url: str) -> dict:
    return {
        'light': {'uri': url, 'ratio': 1.33},
        'dark': {'uri': url, 'ratio': 1.33},
    }


@pytest.mark.now(NOW.isoformat('T'))
@pytest.mark.eats_regions_cache(file='regions.json')
@experiments.INCLUDE_ASSEMBLY_COST
async def test_unavailable_pickup_with_position(slug, eats_catalog_storage):
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

    response = await slug(
        'coffee_boy_novodmitrovskaya_2k6',
        query={
            'latitude': 55.802998,
            'longitude': 37.591503,
            'shippingType': 'pickup',
        },
        headers={'x-platform': 'desktop_web'},
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
                    'priceCategory': {'id': 1, 'name': '₽₽₽', 'value': 1.0},
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
                                'В стоимость входит доставка'
                                ' и сборка заказа'
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
                'locationParams': {
                    'deliveryTime': {'min': 25, 'max': 35},
                    'available': True,
                    'availableNow': True,
                    'availableByTime': True,
                    'availableByLocation': True,
                    'distance': 1.1010703634086447,
                    'availableShippingTypes': [{'type': 'delivery'}],
                    'availableTo': '2021-01-01T14:00:00+03:00',
                    'availableFrom': None,
                    'availableSlug': None,
                    'eatDay': 0,
                    'prepareTime': {'minutes': 0.0, 'readyAt': None},
                    'shippingInfoAction': {
                        'deliveryFee': {'name': '0 - 139 ₽'},
                        'message': 'Доставка',
                    },
                },
                'surge': None,
            },
            'availableTimePicker': [
                [
                    '2021-01-01T13:00:00+03:00',
                    '2021-01-01T13:30:00+03:00',
                    '2021-01-01T14:00:00+03:00',
                ],
                [
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
                'sign': '₽',
                'template': '$VALUE$ $SIGN$$CURRENCY$',
                'text': 'руб.',
            },
        },
    }


@pytest.mark.now(NOW.isoformat('T'))
@pytest.mark.eats_regions_cache(file='regions.json')
@pytest.mark.parametrize(
    'platform,expected_uri,expected_sign,expected_utm',
    [
        pytest.param(
            'desktop_web', YAMAPS_URI, YAMAPS_URI_SIGN, 'web', id='web app',
        ),
        pytest.param(
            'android_app',
            YAMAPS_DEEPLINK,
            YAMAPS_DEEPLINK_SIGN,
            'android',
            id='native android',
        ),
        pytest.param(
            'ios_app',
            YAMAPS_DEEPLINK,
            YAMAPS_DEEPLINK_SIGN,
            'ios',
            id='native ios',
        ),
    ],
)
async def test_available_pickup_with_position(
        slug,
        eats_catalog_storage,
        platform,
        expected_uri,
        expected_sign,
        expected_utm,
):
    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-01-01T10:00:00+03:00'),
            end=parser.parse('2021-01-01T18:00:00+03:00'),
        ),
        storage.WorkingInterval(
            start=parser.parse('2021-01-02T10:00:00+03:00'),
            end=parser.parse('2021-01-02T18:00:00+03:00'),
        ),
    ]

    eats_catalog_storage.add_place(
        storage.Place(
            timing=storage.PlaceTiming(
                preparation=11 * 60, extra_preparation=5.5 * 60,
            ),
            launched_at=NOW - datetime.timedelta(days=5),
            working_intervals=schedule,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(zone_id=1, place_id=1, working_intervals=schedule),
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
        'coffee_boy_novodmitrovskaya_2k6',
        query={
            'latitude': 55.72556335763928,
            'longitude': 36.879730224609375,
            'shippingType': 'pickup',
        },
        headers={'x-platform': platform, 'x-app-version': '1.12.0'},
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
                    'priceCategory': {'id': 1, 'name': '₽₽₽', 'value': 1.0},
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
                    'isPromoAvailable': False,
                    'isStore': False,
                    'brand': {'slug': 'coffee_boy_euocq'},
                    'currency': {'sign': '₽', 'code': 'RUB'},
                    'previewDeliveryFee': '',
                    'deliveryThresholds': [],
                    'deliveryConditions': None,
                    'features': {
                        'ecoPackaging': {'show': False},
                        'delivery': {'isYandexTaxi': False},
                        'map': {
                            'uri': yamaps_uri_with_sign(
                                expected_uri, expected_sign,
                            ),
                        },
                        'badge': None,
                        'favorite': None,
                        'yandexPlus': None,
                    },
                    'footerDescription': (
                        'Исполнитель (продавец): '
                        'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ '
                        '"КОФЕ БОЙ", 127015, Москва, ул Вятская, д 27, стр 11,'
                        ' ИНН 7714457772, рег.номер 1207700043759.'
                        '<br>'
                        'Режим работы: с 10:00 до 18:00'
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
                        '&utm_campaign=' + expected_utm
                    ),
                    'promos': [],
                    'promoTypes': [],
                    'constraints': {},
                    'messages': {'thresholds': {'footer': '', 'title': ''}},
                    'personalizationStrategy': None,
                    'ratingDescription': 'Хорошо',
                    'regionSlug': 'moscow',
                    'logo': LOGO,
                    'accent_color': [{'theme': 'dark', 'value': '#bada55'}],
                },
                'locationParams': {
                    'deliveryTime': {'min': 16, 'max': 16},
                    'available': True,
                    'availableNow': True,
                    'availableByTime': True,
                    'availableByLocation': True,
                    'distance': 45.57415163336143,
                    'availableShippingTypes': [{'type': 'pickup'}],
                    'availableTo': '2021-01-01T18:00:00+03:00',
                    'availableFrom': None,
                    'eatDay': 0,
                    'prepareTime': {
                        'minutes': 16.0,
                        'readyAt': '2021-01-01T12:16:30+03:00',
                    },
                    'availableSlug': None,
                    'shippingInfoAction': {
                        'deliveryFee': {'name': '0 ₽'},
                        'message': 'Доставка',
                    },
                },
                'surge': None,
            },
            'availableTimePicker': [
                [
                    '2021-01-01T12:30:00+03:00',
                    '2021-01-01T13:00:00+03:00',
                    '2021-01-01T13:30:00+03:00',
                    '2021-01-01T14:00:00+03:00',
                    '2021-01-01T14:30:00+03:00',
                ],
                [],
            ],
            'currency': {
                'code': 'RUB',
                'sign': '₽',
                'template': '$VALUE$ $SIGN$$CURRENCY$',
                'text': 'руб.',
            },
        },
    }

    yamaps_check(
        response.json()['payload']['foundPlace']['place']['features']['map'][
            'uri'
        ],
        expected_uri,
        expected_sign,
    )


@pytest.mark.now('2021-01-01T12:15:00+03:00')
async def test_pickup_before_close(slug, eats_catalog_storage):
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            slug='closing_soon',
            timing=storage.PlaceTiming(
                preparation=11 * 60, extra_preparation=5.5 * 60,
            ),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=2,
            place_id=1,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T07:00:00+03:00'),
                    end=parser.parse('2021-01-01T13:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await slug(
        'closing_soon',
        query={
            'latitude': 55.802998,
            'longitude': 37.591503,
            'shippingType': 'pickup',
        },
    )

    assert response.status_code == 200

    data = response.json()

    # NOTE(nk2ge5k): тут получается, что так как самовывоз недоступен в случе
    # если заказ будет готов меньше чем через 30 минут от закрытия заведения
    # то мы сбрасываем самовывоз и показываем как доставку/не доставку, которая
    # недоступна даже по локации. Выглядит странно, надо уточнить этот кейс
    assert data['payload']['foundPlace']['locationParams'] == {
        'deliveryTime': {'min': 30, 'max': 40},
        'available': False,
        'availableNow': False,
        'availableByTime': False,
        'availableByLocation': False,
        'distance': 1.1010703634086447,
        # NOTE(EDACAT-2322): в ходе реализации нового алгоритма определения
        # доступности самовывоза логика определения доступных способов
        # получения заказа - теперь самовывоз отображается доступным только,
        # когда действительно можно сделать заказ.
        'availableShippingTypes': [],
        'availableTo': None,
        'availableFrom': None,
        'eatDay': None,
        'prepareTime': {'minutes': 0, 'readyAt': None},
        'availableSlug': None,
        'shippingInfoAction': {
            'deliveryFee': {'name': '0 ₽'},
            'message': 'Доставка',
        },
    }


@pytest.mark.now('2021-01-01T12:15:00+03:00')
async def test_min_distance(slug, eats_catalog_storage):
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            slug='pickup',
            location=storage.Location(lat=55.802998, lon=37.591503),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=2,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T07:00:00+03:00'),
                    end=parser.parse('2021-01-01T14:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await slug(
        'pickup',
        query={
            'latitude': 55.802998,
            'longitude': 37.591503,
            'shippingType': 'pickup',
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data['payload']['foundPlace']['locationParams']['distance'] == 0.01


@pytest.mark.parametrize(
    ('brand_id', 'shipping_type', 'is_alcomarket'),
    [
        pytest.param(1, 'delivery', True),
        pytest.param(2, 'delivery', False),
        pytest.param(1, 'pickup', True),
        pytest.param(2, 'pickup', False),
    ],
)
@pytest.mark.now('2021-01-01T12:15:00+03:00')
@experiments.place_messages_pickup(
    title='text.message.pickup.title',
    description='text.message.pickup.description',
    footer='text.message.pickup.footer',
)
@PICKUP_MESSAGES_TRANSLATION
@pytest.mark.config(
    EATS_RETAIL_ALCOHOL_SHOPS={
        '1': {
            'rules': 'text.alcohol_shops.rules',
            'licenses': 'text.alcohol_shops.licenses',
            'rules_with_storage_info': {'full': {}},
            'storage_time': 4,
        },
    },
)
async def test_alcohol_shop_text(
        slug, eats_catalog_storage, brand_id, shipping_type, is_alcomarket,
):

    """
      Тест проверяет что для алкомаркета возвращается специальный тип месседжа
      pickup вне зависимости от того, с каким shipping_type был запрос.
      А для обычных магазинов - никогда нет такого специального мессежда.
    """

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=brand_id),
            slug='slug',
            location=storage.Location(lat=55.802998, lon=37.591503),
        ),
    )

    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=2,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T07:00:00+03:00'),
                    end=parser.parse('2021-01-01T14:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await slug(
        'slug',
        query={
            'latitude': 55.802998,
            'longitude': 37.591503,
            'shippingType': shipping_type,
        },
    )

    assert response.status_code == 200

    place = response.json()['payload']['foundPlace']['place']

    if not is_alcomarket:
        assert 'pickup' not in place['messages']
        return

    assert place['footerDescription'] == (
        'rules text licenses text'
        '<br><br>'
        'Исполнитель (продавец): ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ '
        '"КОФЕ БОЙ", 127015, Москва, ул Вятская, д 27, стр 11,'
        ' ИНН 7714457772, рег.номер 1207700043759.'
    )

    assert place['messages'] == {
        'pickup': {
            'description': 'Соберем заказ от 10 минут',
            'footer': 'Заказ будет храниться 4 часа',
            'title': 'Самовывоз',
        },
        'thresholds': {'footer': '', 'title': ''},
    }


@pytest.mark.parametrize('brand_id', [1, 2])
@pytest.mark.parametrize('shipping_type', ['delivery', 'pickup'])
@pytest.mark.now('2021-01-01T12:15:00+03:00')
@PICKUP_MESSAGES_TRANSLATION
@pytest.mark.config(
    EATS_RETAIL_ALCOHOL_SHOPS={
        '1': {
            'rules': 'text.alcohol_shops.rules',
            'licenses': 'text.alcohol_shops.licenses',
            'rules_with_storage_info': {'full': {}},
            'storage_time': 4,
        },
    },
)
async def test_alcohol_shop_available_shipping_types(
        slug, eats_catalog_storage, brand_id, shipping_type,
):

    """
      Тест проверяет что для заведения с самовывозом в поле
      availableShippingTypes возвращается тип получения pickup.
      Вне зависимости алкомаркет это или нет и вне зависимости с каким
      параметром shippingType был запрос в ручку slug.
    """

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=brand_id),
            slug='slug',
            location=storage.Location(lat=55.802998, lon=37.591503),
        ),
    )

    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=2,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T07:00:00+03:00'),
                    end=parser.parse('2021-01-01T14:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await slug(
        'slug',
        query={
            'latitude': 55.802998,
            'longitude': 37.591503,
            'shippingType': shipping_type,
        },
    )

    assert response.status_code == 200

    place = response.json()['payload']['foundPlace']
    assert place['locationParams']['availableShippingTypes'] == [
        {'type': 'pickup'},
    ]
