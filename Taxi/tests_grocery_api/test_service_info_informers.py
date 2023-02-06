import pytest

from . import common
from . import const
from . import experiments
from . import tests_headers

# pylint: disable=too-many-lines


LOCATION = const.LOCATION

NEWBIE_INFORMER = {
    'picture': 'welcome_newbie.jpg',
    'show_in_root': True,
    'text': 'Free delivery for newbies',
}


@experiments.GROCERY_API_INFORMER
@pytest.mark.parametrize(
    'antifraud_enabled, is_fraud',
    [
        pytest.param(False, True, marks=experiments.ANTIFRAUD_CHECK_DISABLED),
        pytest.param(True, False, marks=experiments.ANTIFRAUD_CHECK_ENABLED),
        pytest.param(True, True, marks=experiments.ANTIFRAUD_CHECK_ENABLED),
    ],
)
async def test_grocery_api_informer(
        taxi_grocery_api,
        antifraud,
        grocery_marketing,
        grocery_p13n,
        tristero_parcels,
        antifraud_enabled,
        is_fraud,
):
    """ basic informers config test """

    yandex_uid = tests_headers.HEADER_YANDEX_UID
    orders_count = 2 if not antifraud_enabled else None

    grocery_marketing.add_user_tag(
        'total_orders_count', orders_count, user_id=yandex_uid,
    )

    json = {
        'position': {'location': LOCATION},
        'additional_data': common.DEFAULT_ADDITIONAL_DATA,
    }
    headers = {
        'X-Yandex-UID': yandex_uid,
        'X-YaTaxi-Session': 'taxi: user-id',
        'Accept-Language': 'en',
        'User-Agent': common.DEFAULT_USER_AGENT,
    }
    grocery_p13n.set_modifiers_request_check(
        on_modifiers_request=common.default_on_modifiers_request(orders_count),
    )

    tristero_order = tristero_parcels.add_order(
        order_id='62a88408-b448-429e-8dc0-48f6995fd78e',
        uid=yandex_uid,
        status='received',
        delivery_date='2020-11-02T13:00:42.109234+00:00',
    )
    tristero_order.add_parcel(parcel_id='1', status='in_depot')
    grocery_p13n.set_discounts_request_check(
        on_discounts_info_request=lambda headers, json: json['has_parcels'],
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/service-info', json=json, headers=headers,
    )
    assert grocery_p13n.discounts_info_times_called == 1
    assert antifraud.times_discount_antifraud_called() == int(
        antifraud_enabled,
    )
    response_json = response.json()
    assert response.status_code == 200
    expected_informers = [
        {
            'name': 'test_informer',
            'picture': 'some_url',
            'text': 'hello',
            'show_in_root': True,
            'text_color': 'blue',
            'background_color': 'blue',
            'category_ids': ['category-1', 'category-2'],
            'category_group_ids': ['some_category_group'],
            'product_ids': ['product-1', 'product-2'],
            'modal': {
                'text': 'hello',
                'text_color': 'blue',
                'background_color': 'blue',
                'picture': 'some_picture',
                'title': 'some_title',
                'buttons': [
                    {
                        'variant': 'action',
                        'text': 'button',
                        'text_color': 'blue',
                        'background_color': 'blue',
                        'link': 'some_link',
                    },
                    {'variant': 'default', 'text': 'button too'},
                ],
            },
        },
    ]
    assert response_json['informers'] == expected_informers


@pytest.mark.parametrize('locale', ['ru', 'en', None])
@pytest.mark.translations(
    virtual_catalog={
        'button': {'en': 'button', 'ru': 'кнопка'},
        'button too': {'en': 'button too', 'ru': 'тоже кнопка'},
        'hello': {'en': 'hello', 'ru': 'привет'},
    },
)
@pytest.mark.parametrize('fallback_locale', ['ru', 'en'])
@experiments.GROCERY_API_INFORMER
async def test_grocery_api_informer_with_translation(
        taxi_grocery_api, locale, fallback_locale, taxi_config,
):
    """ informer keys from config are localized """

    expected_answer = {
        'ru': ['привет', 'кнопка', 'тоже кнопка'],
        'en': ['hello', 'button', 'button too'],
    }

    taxi_config.set(
        GROCERY_LOCALIZATION_FALLBACK_LANGUAGES={
            '__default__': fallback_locale,
        },
    )

    json = {'position': {'location': LOCATION}}
    headers = {'X-YaTaxi-Session': 'taxi: user-id'}
    if locale:
        headers['Accept-Language'] = locale
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/service-info', json=json, headers=headers,
    )
    response_json = response.json()

    if locale is None:
        locale = fallback_locale
    assert response.status_code == 200
    assert response_json['informers'][0]['picture'] == 'some_url'
    assert response_json['informers'][0]['text'] == expected_answer[locale][0]
    assert (
        response_json['informers'][0]['modal']['buttons'][0]['text']
        == expected_answer[locale][1]
    )
    assert (
        response_json['informers'][0]['modal']['buttons'][1]['text']
        == expected_answer[locale][2]
    )
    assert response_json['informers'][0]['show_in_root']


@pytest.mark.parametrize('user_id', ['user_id', 'another_user_id'])
@experiments.GROCERY_API_INFORMER_WITH_PREDICATE
async def test_grocery_api_informer_with_match(taxi_grocery_api, user_id):
    """ informers config uses taxi user id from auth context """

    json = {'position': {'location': LOCATION}}
    headers = {'X-YaTaxi-Session': 'taxi:' + user_id, 'Accept-Language': 'en'}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/service-info', json=json, headers=headers,
    )
    response_json = response.json()
    assert response.status_code == 200
    assert (
        response_json['informers'][0]['picture'] == 'some_url'
        if user_id == 'user_id'
        else 'another_url'
    )
    assert (
        response_json['informers'][0]['text'] == 'hello'
        if user_id == 'user_id'
        else 'bye'
    )
    assert 'category_ids' in response_json['informers'][0]


@experiments.GROCERY_API_INFORMER_IN_PRODUCT
async def test_grocery_api_informer_in_product(taxi_grocery_api):
    """ informer have product_ids """

    json = {'position': {'location': LOCATION}}
    headers = {'X-YaTaxi-Session': 'taxi: user-id'}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/service-info', json=json, headers=headers,
    )
    response_json = response.json()
    assert response.status_code == 200
    assert 'product_ids' in response_json['informers'][0]


@experiments.GROCERY_API_INFORMER_EMPTY_RESPONSE
async def test_grocery_api_informer_empty_response(taxi_grocery_api):
    """ service-info should not return informers if
    experiment informers are not full """

    json = {'position': {'location': LOCATION}}
    headers = {'X-YaTaxi-Session': 'taxi: user-id'}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/service-info', json=json, headers=headers,
    )
    response_json = response.json()
    assert response.status_code == 200
    assert response_json['informers'] == []


@pytest.mark.parametrize('handler', ['v1', 'v2'])
@experiments.GROCERY_SURGE_INFORMER
async def test_surge_informer(taxi_grocery_api, handler):
    json = {'position': {'location': LOCATION}}
    headers = {'X-YaTaxi-Session': 'taxi:id', 'Accept-Language': 'en'}
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    response_json = response.json()
    assert response_json['informers'] == [
        {
            'picture': 'surge_url',
            'text': 'bolsho surge',
            'show_in_root': False,
            'category_ids': ['some_category_id'],
        },
    ]


@pytest.mark.config(
    GROCERY_MARKETING_SHARED_CONSUMER_TAG_CHECK={
        'grocery_api_catalog': {
            'tag': 'total_paid_orders_count',
            'payment_id_divisor': 3,
        },
    },
)
@pytest.mark.parametrize(
    'total_orders_count,payment_id_orders_count,informer',
    [
        (
            10,
            0,
            {
                'picture': 'welcome.jpg',
                'show_in_root': True,
                'text': 'Sorry, no free delivery for you',
            },
        ),
        (
            0,
            10,
            {
                'picture': 'welcome.jpg',
                'show_in_root': True,
                'text': 'Sorry, no free delivery for you',
            },
        ),
        (
            0,
            0,
            {
                'picture': 'welcome_newbie.jpg',
                'show_in_root': True,
                'text': 'Free delivery for newbies',
            },
        ),
        (
            None,
            None,
            {
                'picture': 'welcome_newbie.jpg',
                'show_in_root': True,
                'text': 'Free delivery for newbies',
            },
        ),
    ],
)
@experiments.GROCERY_API_INFORMER_ORDER_COMPLETED_PREDICATE
async def test_user_orders_completed_informer(
        taxi_grocery_api,
        grocery_marketing,
        total_orders_count,
        payment_id_orders_count,
        informer,
):
    """ service-info should get user total_orders_count tag and
    use it in informers config """

    user_id = '5123618'
    payment_id = '1'
    if total_orders_count is not None:
        grocery_marketing.add_user_tag(
            'total_paid_orders_count', total_orders_count, user_id=user_id,
        )
    if payment_id_orders_count is not None:
        grocery_marketing.add_payment_id_tag(
            'total_paid_orders_count',
            payment_id_orders_count,
            payment_id=payment_id,
        )
    json = {
        'position': {'location': LOCATION},
        'current_payment_method': {'type': 'card', 'id': payment_id},
    }
    headers = {'X-Yandex-UID': user_id, 'Accept-Language': 'en'}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/service-info', json=json, headers=headers,
    )
    response_json = response.json()
    assert response.status_code == 200
    assert response_json['informers'][0] == informer
    assert grocery_marketing.retrieve_v2_times_called == 1


@pytest.mark.parametrize(
    'headers,informer',
    [({'X-Yandex-UID': '5123618'}, NEWBIE_INFORMER), ({}, NEWBIE_INFORMER)],
)
@experiments.GROCERY_API_INFORMER_ORDER_COMPLETED_PREDICATE
async def test_nouid_user_orders_completed_informer(
        taxi_grocery_api, headers, informer, grocery_marketing,
):
    """ service-info should assume that user has 0 user_orders_completed
    if there is no yandex-uid """

    json = {'position': {'location': LOCATION}}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/service-info', json=json, headers=headers,
    )
    response_json = response.json()
    assert response.status_code == 200
    assert response_json['informers'][0] == informer
    assert grocery_marketing.retrieve_v2_times_called == 1


@experiments.GROCERY_API_INFORMER_ORDER_COMPLETED_PREDICATE
async def test_grocery_marketing_error(taxi_grocery_api, mockserver):
    """ grocery-marketing downtime should not affect service-info """

    user_id = '5123618'

    @mockserver.json_handler(
        '/grocery-marketing/internal/v1/marketing/v2/tag/retrieve',
    )
    def _grocery_marketing_fail(request):
        return mockserver.make_response('Something went wrong', status=500)

    json = {'position': {'location': LOCATION}}
    headers = {'X-Yandex-UID': user_id, 'Accept-Language': 'en'}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/service-info', json=json, headers=headers,
    )
    response_json = response.json()
    assert response.status_code == 200
    assert response_json['informers'][0] == {
        'picture': 'welcome.jpg',
        'show_in_root': True,
        'text': 'Sorry, no free delivery for you',
    }
    assert _grocery_marketing_fail.times_called == 1


@pytest.mark.parametrize('handler', ['v1', 'v2'])
@pytest.mark.translations(
    virtual_catalog={
        'text': {'en': 'text', 'ru': 'текст'},
        'modal_title': {'en': 'modal title', 'ru': 'заголовок модалки'},
        'modal_text': {'en': 'modal text', 'ru': 'текст модалки'},
        'button_text': {'en': 'button text', 'ru': 'текст кнопки'},
    },
)
@pytest.mark.parametrize('locale', ['ru', 'en'])
async def test_discounts_informers(
        taxi_grocery_api, mockserver, locale, handler,
):
    user_id = '5123618'

    @mockserver.json_handler('grocery-p13n/internal/v1/p13n/v1/discounts-info')
    def grocery_discounts(request):
        return mockserver.make_response(
            json={
                'discount_informers': [
                    {
                        'hierarchy_name': 'menu_discounts',
                        'informer': {
                            'text': 'text',
                            'picture': 'picture',
                            'color': 'color',
                            'modal': {
                                'text': 'modal_text',
                                'picture': 'modal_picture',
                                'title': 'modal_title',
                                'buttons': [
                                    {
                                        'text': 'button_text',
                                        'color': 'button_color',
                                        'uri': 'button_uri',
                                    },
                                ],
                            },
                        },
                        'discount_value': {
                            'payment_type': 'money',
                            'discount_value': '100.5',
                            'discount_value_type': 'absolute',
                        },
                    },
                ],
            },
            status=200,
        )

    json = {'position': {'location': LOCATION}}
    headers = {'X-Yandex-UID': user_id, 'Accept-Language': locale}
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    assert response.status_code == 200
    assert grocery_discounts.times_called == 1
    text = 'text'
    modal_title = 'modal title'
    modal_text = 'modal text'
    button_text = 'button text'
    if locale == 'ru':
        text = 'текст'
        modal_title = 'заголовок модалки'
        modal_text = 'текст модалки'
        button_text = 'текст кнопки'

    expected_informer = {
        'picture': 'picture',
        'text': text,
        'show_in_root': True,
        'modal': {
            'text': modal_text,
            'picture': 'modal_picture',
            'title': modal_title,
            'buttons': [
                {
                    'variant': 'default',
                    'text': button_text,
                    'link': 'button_uri',
                },
            ],
        },
        'extra_data': [
            {
                'payment_type': 'money',
                'discount_value': '100.5',
                'discount_value_type': 'absolute',
            },
        ],
    }
    if handler == 'v1':
        expected_informer['background_color'] = 'color'
        expected_informer['modal']['buttons'][0][
            'background_color'
        ] = 'button_color'

    assert response.json()['informers'] == [expected_informer]


@pytest.mark.parametrize('handler', ['v1', 'v2'])
@experiments.GROCERY_CASHBACK_ANNIHILATION_INFORMER
@pytest.mark.parametrize('balance_to_annihilate', ['0', '42'])
@pytest.mark.parametrize(
    'is_cashback_annihilation_enabled',
    [
        pytest.param(
            True,
            id='cashback_annihilation_enabled',
            marks=[common.CASHBACK_ANNIHILATION_ENABLED],
        ),
        pytest.param(
            False,
            id='cashback_annihilation_disabled',
            marks=[common.CASHBACK_ANNIHILATION_DISABLED],
        ),
    ],
)
async def test_grocery_cashback_annihilation_informers(
        taxi_grocery_api,
        mockserver,
        balance_to_annihilate,
        is_cashback_annihilation_enabled,
        handler,
):
    json = {'position': {'location': LOCATION}}
    headers = {'X-YaTaxi-Session': 'taxi:id', 'Accept-Language': 'en'}

    @mockserver.json_handler('/grocery-p13n/internal/v1/p13n/v1/cashback-info')
    def _p13_cashback_info(request):
        return {
            'balance': '100500',
            'complement_payment_types': [],
            'wallet_id': 'TEST_WALLET_ID',
            'annihilation_info': {
                'annihilation_date': '2021-07-26T14:08:00+00:00',
                'balance_to_annihilate': balance_to_annihilate,
            },
        }

    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    response_json = response.json()
    if balance_to_annihilate == '0' or not is_cashback_annihilation_enabled:
        assert response_json['informers'] == []
    else:
        assert response_json['informers'] == [
            {
                'picture': 'some url',
                'text': 'cashback`s not gonna wait for you, pal!',
                'show_in_root': False,
                'category_ids': ['some_category_id'],
            },
        ]


# Проверяем что берется максимальное значение orders_count
# если доступно appmetrica_device_id_usage_count
@experiments.GROCERY_API_INFORMER_ORDER_COMPLETED_PREDICATE
@pytest.mark.parametrize('uid_count,device_count', [(0, 1), (1, 0), (3, None)])
async def test_use_right_orders_count(
        taxi_grocery_api, mockserver, uid_count, device_count,
):
    user_id = 'user_id'

    @mockserver.json_handler(
        '/grocery-marketing/internal/v1/marketing/v2/tag/retrieve',
    )
    def _grocery_marketing(request):
        return {
            'usage_count': uid_count,
            'appmetrica_device_id_usage_count': device_count,
        }

    json = {'position': {'location': LOCATION}}
    headers = {'X-Yandex-UID': user_id, 'Accept-Language': 'en'}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/service-info', json=json, headers=headers,
    )
    response_json = response.json()
    assert response.status_code == 200
    assert response_json['informers'][0] == {
        'picture': 'welcome.jpg',
        'show_in_root': True,
        'text': 'Sorry, no free delivery for you',
    }


@experiments.GROCERY_API_INFORMER
@experiments.GROCERY_API_MARKET_INFORMER
@pytest.mark.parametrize(
    'brand',
    [
        pytest.param('market', id='gets brand informers if possible'),
        pytest.param('unknown', id='fallbacks to default informers on fail'),
    ],
)
async def test_grocery_api_brand_informers(taxi_grocery_api, brand):
    """ Информеры для брендов лежат в отдельных конфигах. Если для указанного
    в запросе бренда есть конфиг информеров, то они берутся оттуда. В
    противном случае берутся стандартные информеры. """

    json = {'position': {'location': LOCATION}}
    headers = {
        'Accept-Language': 'ru',
        'X-Request-Application': (
            f'app_name=mobileweb_market_lavka_iphone,app_brand={brand}'
        ),
    }
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/service-info', json=json, headers=headers,
    )
    response_json = response.json()
    assert response.status_code == 200
    if brand == 'market':
        assert response_json['informers']
        assert response_json['informers'][0]['name'] == 'test_market_informer'
    else:
        assert response_json['informers']
        assert response_json['informers'][0]['name'] == 'test_informer'


# Проверяем что в ответе есть переведенные растяжки для десктопа
@pytest.mark.parametrize('handler', ['v1', 'v2'])
@pytest.mark.parametrize(
    'locale,fallback_locale',
    [('ru', None), ('en', None), (None, 'ru'), (None, 'en')],
)
@pytest.mark.translations(
    virtual_catalog={
        'picture_key': {'en': 'en_pic', 'ru': 'ru_pic'},
        'link_key': {'en': 'en_link', 'ru': 'ru_link'},
        'picture_x2_key': {'en': 'en_pic_x2', 'ru': 'ru_pic_x2'},
    },
)
@experiments.GROCERY_API_DESKTOP_HEAD_BANNERS
async def test_grocery_api_desktop_head_banners(
        taxi_grocery_api, locale, fallback_locale, taxi_config, handler,
):
    if fallback_locale is not None:
        taxi_config.set(
            GROCERY_LOCALIZATION_FALLBACK_LANGUAGES={
                '__default__': fallback_locale,
            },
        )

    json = {'position': {'location': LOCATION}}
    headers = {}
    if locale:
        headers['X-Request-Language'] = locale
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    response_json = response.json()

    if locale is None:
        locale = fallback_locale
    assert response.status_code == 200
    assert response_json['desktop_head_banners'] == [
        {
            'picture': '{}_pic'.format(locale),
            'picture_x2': '{}_pic_x2'.format(locale),
            'width': 2,
            'height': 1,
            'link': '{}_link'.format(locale),
            'background_color': 'black',
        },
    ]


# Проверяем переводы сторис, а так же фильтрацию
# некорректных сторис с фото и видео одновременно или без них.
@pytest.mark.translations(
    virtual_catalog={
        'title': {'ru': 'ru_title'},
        'text_caption': {'ru': 'ru_text_caption'},
        'text': {'ru': 'ru_text'},
    },
)
@experiments.GROCERY_API_INFORMER_STORIES
async def test_grocery_api_informer_stories(
        taxi_grocery_api, load_json, overlord_catalog,
):
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, LOCATION)
    json = {'position': {'location': LOCATION}}
    headers = {'X-Request-Language': 'ru'}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/service-info', json=json, headers=headers,
    )
    response_json = response.json()
    assert response.status_code == 200
    assert response_json['informers'][0]['stories'] == [
        {
            'variant': 'normal',
            'caption': 'ru_text_caption',
            'title': 'ru_title',
            'text': 'ru_text',
            'text_position': 'top',
            'text_color': 'red',
            'image': {
                'source': 'some_picture',
                'fallback_color': 'black',
                'duration_ms': 10,
            },
            'with_fade': True,
            'product_id': 'product-1',
            'buttons': [{'text': 'button_text', 'variant': 'default'}],
        },
        {
            'variant': 'inverted',
            'video': {
                'source': 'some_video',
                'cover': 'cover',
                'fallback_color': 'black',
                'source_webm': 'some_video_webm',
            },
        },
        {
            'variant': 'inverted',
            'title': 'video_and_image',
            'video': {
                'source': 'some_video',
                'cover': 'cover',
                'fallback_color': 'black',
                'source_webm': 'some_video_webm',
            },
            'image': {
                'source': 'some_picture',
                'fallback_color': 'black',
                'duration_ms': 10,
            },
        },
    ]


# Не возвращаем информер, если у него в сторис
# есть продукт которого нет в каталоге
@experiments.GROCERY_API_INFORMER_STORIES
async def test_grocery_api_informer_stories_no_product(taxi_grocery_api):
    json = {'position': {'location': LOCATION}}
    headers = {'X-Request-Language': 'ru'}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/service-info', json=json, headers=headers,
    )
    response_json = response.json()
    assert response.status_code == 200
    assert response_json['informers'] == []


@pytest.mark.parametrize('handler', ['v1', 'v2'])
@experiments.GROCERY_API_REFERRAL_INFORMERS
async def test_referral_informers(taxi_grocery_api, mockserver, handler):
    referral_informer = {
        'text': 'informer_text',
        'picture': 'informer_pic',
        'name': 'informer_name',
        'show_in_root': True,
        'modal': {
            'title': 'modal_title',
            'text': 'modal_text',
            'full_screen': True,
            'picture': 'modal_pic',
            'buttons': [
                {
                    'variant': 'action',
                    'text': 'shr_btn_text',
                    'action': 'copy',
                },
                {
                    'variant': 'action',
                    'text': 'cpy_btn_text',
                    'action': 'share',
                },
            ],
            'extra_data': {
                'text': 'extra_data_text',
                'link': 'extra_data_link',
                'additional_text': 'extra_data_additional_text',
            },
        },
    }

    @mockserver.json_handler(
        '/grocery-coupons/internal/v1/coupons/referral/informers',
    )
    def _grocery_coupons_ref_informers(request):
        return mockserver.make_response(
            json={'informers': [referral_informer]}, status=200,
        )

    json = {'position': {'location': LOCATION}}
    headers = {'X-Yandex-UID': 'user_id', 'Accept-Language': 'ru'}
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )
    response_json = response.json()
    assert response.status_code == 200
    assert response_json['informers'][0] == referral_informer


@pytest.mark.parametrize('handler', ['v1', 'v2'])
async def test_referral_informers_disabled(
        taxi_grocery_api, mockserver, handler,
):
    @mockserver.json_handler(
        '/grocery-coupons/internal/v1/coupons/referral/informers',
    )
    def _grocery_coupons_ref_informers(request):
        return mockserver.make_response(json={}, status=200)

    json = {'position': {'location': LOCATION}}
    headers = {'X-Yandex-UID': 'user_id', 'Accept-Language': 'ru'}
    response = await taxi_grocery_api.post(
        f'/lavka/v1/api/{handler}/service-info', json=json, headers=headers,
    )

    assert response.status_code == 200
    assert _grocery_coupons_ref_informers.times_called == 0
    response_json = response.json()
    assert not response_json['informers']


@experiments.GROCERY_API_INFORMER
async def test_no_grocery_api_informer_in_v2(taxi_grocery_api):
    """ v2 does not have config informers """

    json = {'position': {'location': LOCATION}}
    headers = {'X-YaTaxi-Session': 'taxi:user_id', 'Accept-Language': 'en'}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v2/service-info', json=json, headers=headers,
    )
    response_json = response.json()
    assert response.status_code == 200
    assert not response_json['informers']
