import copy
import typing

import pytest

from . import helpers as h
from . import ui_helpers as uih


def assert_response(response, expected):
    code, body = expected
    assert {
        'code': response.status_code,
        'body': (
            response.text
            if isinstance(body, str) or not response.text
            else response.json()
        ),
    } == {'code': code, 'body': body}


async def get_offer_params_check(
        taxi_scooters_subscription,
        language: str,
        screens: typing.List[str],
        authorize: bool = True,
        expected: typing.Tuple[int, typing.Dict] = None,
):
    params = {'position': h.TEST_POSITION}
    if screens:
        params['screens'] = ','.join(screens)
    headers = {'X-Request-Language': language}
    if authorize:
        headers.update(h.HEADERS)
    response = await taxi_scooters_subscription.get(
        '/scooters-subscriptions/v1/subscriptions/offer-params',
        params=params,
        headers=headers,
    )
    if expected:
        assert_response(response, expected)
    return response


async def get_screen_check(
        taxi_scooters_subscription,
        screen: str,
        language: str,
        has_plus: bool,
        geobase_ids_path: typing.List[int] = None,
        position: str = None,
        expected: typing.Tuple[int, typing.Dict] = None,
):
    params = {'position': position or h.TEST_POSITION}
    if geobase_ids_path:
        params['geobase_ids_path'] = ','.join(map(str, geobase_ids_path))
    headers = {**h.HEADERS, 'X-Request-Language': language}
    if has_plus:
        headers['X-YaTaxi-Pass-Flags'] = 'ya-plus'
    response = await taxi_scooters_subscription.get(
        f'/scooters-subscriptions/v1/subscriptions/screen/{screen}',
        params=params,
        headers=headers,
    )
    if expected is not None:
        assert_response(response, expected)


EXPECTED_SUBSCRIPTION_NONE = {
    'title': uih.atext([uih.text('Бесплатный старт')]),
    'badges': [uih.badge(uih.atext([uih.text('New!')]), color='#ff0000')],
    'action': {
        'type': 'webapp',
        'web_app_url': (
            'https://m.taxi.taxi.tst.yandex.ru'
            '/scooters/subscription?page=order'
        ),
        'webapp_type': 'scooters-subscription',
    },
    'processing': False,
}

EXPECTED_DISCOVERY = {
    'items': [
        {
            'action': {
                'type': 'webapp',
                'web_app_url': (
                    'https://m.taxi.taxi.tst.yandex.ru'
                    '/scooters/subscription?page=order'
                ),
                'webapp_type': 'scooters-subscription',
            },
            'background': {
                'color': '#FFDE40',
                'image_tag': 'shortcuts_subscription_promo',
            },
            'height': 3,
            'icon_tag': 'shortcuts_subscription_promo',
            'shortcut_id': 'free_unlock',
            'subtitle': '50 ₽→0',
            # 'title': will be replaced
            'type': 'action-driven',
            'width': 6,
        },
    ],
    'sections': [
        {
            'section': {
                'shortcut_ids': ['free_unlock'],
                'tags': ['gray_separator'],
                'type': 'items_linear_grid',
            },
            'slug': 'subscription_buttons',
        },
    ],
}

EXPECTED_ACTIVE_NONE: tuple = (
    404,
    {'code': 'not_found', 'message': 'No active subscription found'},
)

EXPECTED_TARIFF = {
    'sections': [
        uih.section(
            [
                uih.group(
                    [
                        {
                            'type': 'value',
                            'title': uih.atext([uih.text('Стоимость опции')]),
                            'value': uih.atext(
                                [uih.text('XXX ₽/мес')],  # will be replaced
                            ),
                        },
                        {
                            'type': 'value',
                            'title': uih.atext(
                                [
                                    uih.text('Старт'),
                                    uih.text(
                                        '\nв поминутном тарифе',
                                        font_size=13,
                                        color='#9E9B98',
                                    ),
                                ],
                            ),
                            'value': uih.atext([uih.text('0 ₽')]),
                        },
                    ],
                    title=uih.atext([uih.text('Стоимость')]),
                ),
                uih.group(
                    [
                        uih.atext(
                            [
                                uih.text(
                                    'Если за весь период ни разу не катались, '
                                    'можно отменить. Это бесплатно',
                                ),
                            ],
                        ),
                    ],
                    title=uih.atext([uih.text('Условия отмены')]),
                ),
                {
                    'type': 'button',
                    'title': uih.atext(
                        [uih.text('Купить за XXX ₽/мес')],  # will be replaced
                    ),
                    'background_color': '#FCE000',
                    'action': {
                        'type': 'buy',
                        'parameters': {
                            'target': 'samokat',
                            'optionOfferNames': [
                                '1month.trial.plus.samokat.399',
                            ],
                        },
                    },
                },
            ],
            title=uih.atext(
                [
                    uih.text(
                        'Опция «Самокаты»\nв подписке Яндекс Плюс',
                        font_size=24,
                    ),
                ],
            ),
        ),
    ],
}

OFFER = {
    'invoices': [
        {
            'totalPrice': {'amount': 169, 'currency': 'RUB'},
            'timestamp': 1647006179325,
        },
    ],
    'optionOffers': [
        {
            'name': '1month.trial.plus.samokat.399',
            'title': 'Самокаты',
            'text': 'Опция к подписке Плюс',
            'additionText': '169 руб. в месяц',
            'option': {'name': 'plus-samokat'},
        },
    ],
    'tariffOffer': {
        'name': '2month.trial.new_plus.199_v6',
        'title': 'Яндекс Плюс',
        'text': 'До весны бесплатно',
        'additionText': 'далее 199 ₽ в месяц',
        'tariff': {'name': 'plus'},
    },
}


@pytest.mark.parametrize(
    [
        'features',
        'has_plus',
        'purchase',
        'expected_features',
        'expected_subscription',
        'expected_active',
    ],
    [
        pytest.param(
            [],
            False,  # has_plus
            'full',
            {},
            EXPECTED_SUBSCRIPTION_NONE,
            EXPECTED_ACTIVE_NONE,
            id='featureless',
        ),
        pytest.param(
            ['UnknownFeature'],
            True,  # has_plus
            'full',
            {},
            EXPECTED_SUBSCRIPTION_NONE,
            EXPECTED_ACTIVE_NONE,
            id='unknown',
        ),
        pytest.param(
            ['plus-samokat'],
            False,  # has_plus
            'trial',
            {'free_unlock': True, 'free_parking': True},
            {
                'title': uih.atext([uih.text('Бесплатный старт')]),
                'subtitle': uih.atext(
                    [uih.text('Опция активна', font_size=13, color='#48C600')],
                ),
                'action': {
                    'type': 'webapp',
                    'web_app_url': (
                        'https://m.taxi.taxi.tst.yandex.ru'
                        '/scooters/subscription?page=info'
                    ),
                    'webapp_type': 'scooters-subscription',
                },
                'processing': False,
            },
            (
                200,
                {
                    'sections': [
                        uih.section(
                            [
                                {
                                    'type': 'value',
                                    'title': uih.atext(
                                        [uih.text('Опция «Самокаты»')],
                                    ),
                                    # 'value': will be replaced,
                                },
                                {
                                    'type': 'value',
                                    'title': uih.atext([uih.text('Начало')]),
                                    # 'value': will be replaced,
                                },
                                {
                                    'type': 'value',
                                    'title': uih.atext(
                                        [uih.text('Окончание')],
                                    ),
                                    # 'value': will be replaced,
                                },
                                {
                                    'type': 'value',
                                    'image_tag': 'pause',
                                    'title': uih.atext(
                                        [uih.text('Приостановить опцию')],
                                    ),
                                    'action': {'type': 'support_chat'},
                                },
                                {
                                    'type': 'value',
                                    'title': uih.atext(
                                        [
                                            uih.text(
                                                'Отключить опцию',
                                                color='#FA3E2C',
                                            ),
                                            uih.text(
                                                '\nчерез поддержку',
                                                font_size=13,
                                                color='#9E9B98',
                                            ),
                                        ],
                                    ),
                                    'action': {'type': 'support_chat'},
                                },
                            ],
                            title=uih.atext(
                                [
                                    uih.text(
                                        'Опция «Самокаты» в '
                                        'подписке Яндекс Плюс',
                                        font_size=24,
                                    ),
                                    uih.text(
                                        'Активна',
                                        color='#5AC31A',
                                        font_weight='medium',
                                    ),
                                ],
                            ),
                        ),
                    ],
                },
            ),
            id='featurefull',
        ),
    ],
)
@pytest.mark.parametrize(
    ['subscription_enabled'],
    [pytest.param(False, id='norender'), pytest.param(True, id='render')],
)
@pytest.mark.parametrize(
    [
        'request_language',
        'expected_activated',
        'expected_expired',
        'expected_discovery_title',
        'expected_price',
    ],
    [
        pytest.param(
            'ru',
            '09.02.2022 01:02',
            '19.02.2022 04:05',
            'Лёгкий старт\nс Плюсом',
            '169 ₽',
            id='ru',
        ),
        pytest.param(
            'en',
            '02/09/2022 01:02',
            '02/19/2022 04:05',
            'Easy start\nw Plus',
            '₽169',
            id='en',
        ),
    ],
)
@pytest.mark.now('2022-02-18T02:48:00+03:00')
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='scooters_subscription.json')
@pytest.mark.experiments3(filename='scooters_subscription_plus.json')
@pytest.mark.experiments3(filename='scooters_subscription_screens.json')
async def test_handlers(
        taxi_scooters_subscription,
        mockserver,
        experiments3,
        features,
        has_plus,
        purchase,
        subscription_enabled,
        request_language,
        expected_features,
        expected_subscription,
        expected_active,
        expected_activated,
        expected_expired,
        expected_discovery_title,
        expected_price,
):
    # Arrange
    h.mock_intervals(mockserver, features, purchase)

    h.mock_offers(mockserver, [OFFER], language=request_language.upper())

    experiments3.add_experiment(
        consumers=['scooters_subscription_tariff'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        default_value={'subscription': {'enabled': subscription_enabled}},
        name='scooters',
    )
    await taxi_scooters_subscription.invalidate_caches()

    # Act & Assert
    expected = {'features': expected_features}
    if expected_active != EXPECTED_ACTIVE_NONE:
        expected['trial'] = purchase == 'trial'
        expected['purchase'] = purchase

        items = expected_active[1]['sections'][0]['items']
        items[0]['value'] = uih.atext([uih.text(expected_price)])
        items[1]['value'] = uih.atext([uih.text(expected_activated)])
        items[2]['value'] = uih.atext([uih.text(expected_expired)])

    if subscription_enabled:
        expected['subscription'] = expected_subscription

    expected_discovery = copy.deepcopy(EXPECTED_DISCOVERY)
    expected_discovery['items'][0]['title'] = expected_discovery_title
    expected['discovery'] = expected_discovery
    await get_offer_params_check(
        taxi_scooters_subscription,
        language=request_language,
        screens=['subscription', 'discovery'],
        expected=(200, expected),
    )

    expected_grid_rows = [
        [
            {
                'type': 'cell',
                'action': {'type': 'story', 'story_id': 'test-story-id'},
                'title': uih.atext(
                    [
                        uih.text('Старт 0 ₽ вместо 50 ₽'),
                        uih.text('\nПлатите только за минуты', font_size=13),
                    ],
                ),
            },
            {
                'title': uih.atext(
                    [
                        uih.text('Бесплатное ожидание'),
                        uih.text('\nВ режиме поездки', font_size=13),
                    ],
                ),
            },
        ],
        [
            {'title': uih.atext([uih.text('Кешбэк с Плюсом')])},
            {'title': uih.atext([uih.text('Кешбэк выше')])},
        ],
    ]
    expected_options = []
    if not has_plus:
        expected_options.append(
            {
                'type': 'option',
                'image_tag': 'plus_icon',
                'title': uih.atext([uih.text('Яндекс Плюс')]),
                'right': uih.atext(
                    [
                        uih.text('До весны бесплатно'),
                        uih.text(
                            '\nдалее 199 ₽ в месяц',
                            color='#9E9B98',
                            font_size=11,
                        ),
                    ],
                ),
                'footer': {
                    'title': uih.atext(
                        [
                            uih.text('Что такое Плюс'),
                            uih.text(
                                '\nКино, музыка, кешбэк баллами',
                                color='#9E9B98',
                                font_size=11,
                            ),
                        ],
                    ),
                    'action': {'type': 'plus_home'},
                },
            },
        )
    expected_options.append(
        {
            'image_tag': 'scooter_icon',
            'title': uih.atext(
                [
                    uih.text('Самокаты'),
                    uih.text(
                        '\nОпция к подписке Плюс',
                        color='#9E9B98',
                        font_size=11,
                    ),
                ],
                alignment='right',
            ),
            'right': uih.atext([uih.text('169 руб. в месяц')]),
            'footer': {
                'title': uih.atext([uih.text('Все условия')]),
                'action': {'type': 'tariff'},
            },
        },
    )
    expected_action = {
        'type': 'buy',
        'parameters': {
            'target': 'samokat',
            'optionOfferNames': ['1month.trial.plus.samokat.399'],
        },
    }
    if not has_plus:
        expected_action['parameters'][
            'tariffOfferName'
        ] = '2month.trial.new_plus.199_v6'

    expected_main = (
        expected_active
        if expected_active != EXPECTED_ACTIVE_NONE
        else (
            200,
            {
                'sections': [
                    {
                        'image': {
                            'tag': f'plus_header_{request_language}',
                            'height': 24,
                        },
                        'items': [
                            uih.group(
                                [
                                    {
                                        'type': 'value',
                                        'image_tag': 'checkbox',
                                        'title': uih.atext(
                                            [uih.text('Blah-blah')],
                                        ),
                                    },
                                ],
                                meta_style='minor',
                            ),
                            uih.grid(expected_grid_rows),
                        ],
                        'title': uih.atext(
                            [
                                uih.text(
                                    'Бесплатный старт на самокатах',
                                    font_size=24,
                                ),
                            ],
                            alignment='center',
                        ),
                    },
                    uih.section(expected_options),
                ],
                'subsections': [
                    uih.section(
                        [
                            {
                                'type': 'button',
                                'title': uih.atext(
                                    [
                                        uih.text(
                                            f'Купить за {expected_price}/мес',
                                        ),
                                    ],
                                ),
                                'background_color': '#FCE000',
                                'action': expected_action,
                            },
                        ],
                    ),
                ],
            },
        )
    )

    await get_screen_check(
        taxi_scooters_subscription,
        screen='main',
        language=request_language,
        has_plus=has_plus,
        geobase_ids_path=h.TEST_GEOBASE_IDS_PATH,
        expected=expected_main,
    )

    expected_tariff = copy.deepcopy(EXPECTED_TARIFF)
    expected_tariff_items = expected_tariff['sections'][0]['items']
    expected_tariff_items[0]['items'][0]['value']['items'][0][
        'text'
    ] = f'{expected_price}/мес'
    expected_tariff_items[2]['title']['items'][0][
        'text'
    ] = f'Купить за {expected_price}/мес'
    if not has_plus:
        expected_tariff_items[2]['action']['parameters'][
            'tariffOfferName'
        ] = '2month.trial.new_plus.199_v6'
    await get_screen_check(
        taxi_scooters_subscription,
        screen='tariff',
        language=request_language,
        has_plus=has_plus,
        geobase_ids_path=h.TEST_GEOBASE_IDS_PATH,
        expected=(200, expected_tariff),
    )

    await get_screen_check(
        taxi_scooters_subscription,
        screen='active',
        language=request_language,
        has_plus=has_plus,
        geobase_ids_path=None,
        expected=expected_active,
    )


@pytest.mark.parametrize('purchase', ['full', 'intro', 'trial'])
@pytest.mark.now('2022-02-18T02:48:00+03:00')
@pytest.mark.experiments3(filename='scooters_subscription.json')
@pytest.mark.experiments3(filename='scooters_subscription_plus.json')
@pytest.mark.experiments3(filename='scooters_subscription_screens.json')
async def test_analytics(taxi_scooters_subscription, mockserver, purchase):
    # Arrange
    h.mock_intervals(mockserver, ['plus-samokat'], purchase)

    # Act & Assert
    await get_offer_params_check(
        taxi_scooters_subscription,
        language='ru',
        screens=[],
        expected=(
            200,
            {
                'features': {'free_parking': True, 'free_unlock': True},
                'purchase': purchase,
                'trial': purchase == 'trial',
            },
        ),
    )


@pytest.mark.parametrize('authorize', [False, True])
@pytest.mark.parametrize(
    'offers',  #
    [pytest.param([], id='none'), pytest.param([OFFER], id='some')],
)
@pytest.mark.now('2022-02-18T02:48:00+03:00')
@pytest.mark.experiments3(filename='scooters_subscription.json')
@pytest.mark.experiments3(filename='scooters_subscription_screens.json')
async def test_mediabilling_offers(
        taxi_scooters_subscription,
        mockserver,
        experiments3,
        load_json,
        authorize,
        offers,
):
    # Arrange
    scooters_subscription_plus = load_json('scooters_subscription_plus.json')[
        'configs'
    ][0]
    scooters_subscription_plus['default_value']['avoid_graphql'] = True
    experiments3.add_config(**scooters_subscription_plus)

    h.mock_intervals(mockserver, [])

    @mockserver.json_handler('/mediabilling/offers/composite')
    async def _offers_composite(request):
        expected_query = {
            'target': 'andrei',
            'features': 'basic-plus',
            'regionHierarchy': ','.join(map(str, h.TEST_GEOBASE_IDS_PATH)),
            'language': 'RU',
        }
        if authorize:
            expected_query['uid'] = h.TEST_UID
        assert request.query == expected_query

        return mockserver.make_response(
            status=200, json={'result': {'offers': offers}},
        )

    # Act & Assert
    response = await get_offer_params_check(
        taxi_scooters_subscription,
        language='ru',
        screens=['discovery'],
        authorize=authorize,
    )
    expected_json = {'features': {}}
    if not authorize:
        expected_json['discovery'] = {'unauthorized': True}
    elif offers:
        discovery = copy.deepcopy(EXPECTED_DISCOVERY)
        discovery['items'][0]['title'] = 'Лёгкий старт\nс Плюсом'
        expected_json['discovery'] = discovery
    assert response.json() == expected_json


@pytest.mark.now('2022-02-18T02:48:00+03:00')
@pytest.mark.experiments3(filename='scooters_subscription.json')
@pytest.mark.experiments3(filename='scooters_subscription_plus.json')
@pytest.mark.experiments3(filename='scooters_subscription_screens.json')
async def test_unauthorized(taxi_scooters_subscription, mockserver):
    # Arrange
    h.mock_intervals(mockserver, ['plus-samokat'])
    h.mock_offers(mockserver, [], unauthorized=True)

    # Act & Assert
    await get_offer_params_check(
        taxi_scooters_subscription,
        language='ru',
        screens=['discovery'],
        authorize=False,
        expected=(200, {'discovery': {'unauthorized': True}, 'features': {}}),
    )


@pytest.mark.parametrize('has_offer', [False, True])
@pytest.mark.now('2022-02-18T02:48:00+03:00')
@pytest.mark.experiments3(filename='scooters_subscription.json')
@pytest.mark.experiments3(filename='scooters_subscription_plus.json')
@pytest.mark.experiments3(filename='scooters_subscription_screens.json')
async def test_metrics(
        taxi_scooters_subscription,
        taxi_scooters_subscription_monitor,
        get_single_metric_by_label_values,
        mockserver,
        has_offer,
):
    # Arrange
    await taxi_scooters_subscription.tests_control(reset_metrics=True)

    async def fetch_metric():
        result = {}
        for originator in ('main', 'tariff', 'offer-params'):
            metric = await get_single_metric_by_label_values(
                taxi_scooters_subscription_monitor,
                sensor='scooters_subscription_no_offers',
                labels={'originator': originator},
            )
            if metric and metric.value:
                result[originator] = metric.value
        return result

    h.mock_intervals(mockserver, [], 'full')
    h.mock_offers(mockserver, [OFFER] if has_offer else [])

    # Act & Assert
    expected_metrics = {}

    assert await fetch_metric() == expected_metrics

    await get_offer_params_check(
        taxi_scooters_subscription, language='ru', screens=[],
    )
    assert await fetch_metric() == expected_metrics

    await get_offer_params_check(
        taxi_scooters_subscription, language='ru', screens=['discovery'],
    )
    if not has_offer:
        expected_metrics['offer-params'] = 1
    assert await fetch_metric() == expected_metrics

    await get_screen_check(
        taxi_scooters_subscription,
        screen='main',
        language='ru',
        has_plus=True,
        geobase_ids_path=h.TEST_GEOBASE_IDS_PATH,
    )
    if not has_offer:
        expected_metrics['main'] = 1
    assert await fetch_metric() == expected_metrics

    await get_screen_check(
        taxi_scooters_subscription,
        screen='tariff',
        language='ru',
        has_plus=True,
        geobase_ids_path=h.TEST_GEOBASE_IDS_PATH,
    )
    if not has_offer:
        expected_metrics['tariff'] = 1
    assert await fetch_metric() == expected_metrics

    await get_screen_check(
        taxi_scooters_subscription,
        screen='active',
        language='ru',
        has_plus=True,
        geobase_ids_path=h.TEST_GEOBASE_IDS_PATH,
    )
    assert await fetch_metric() == expected_metrics


@pytest.mark.parametrize('language', ['ru', 'en', 'fr'])
@pytest.mark.now('2022-02-18T02:48:00+03:00')
@pytest.mark.experiments3(filename='scooters_subscription.json')
@pytest.mark.experiments3(filename='scooters_subscription_plus.json')
@pytest.mark.experiments3(filename='scooters_subscription_screens.json')
async def test_languages(taxi_scooters_subscription, mockserver, language):
    # Arrange
    h.mock_intervals(mockserver, [], 'full')
    h.mock_offers(
        mockserver, [], language=('RU' if language == 'ru' else 'EN'),
    )

    await get_offer_params_check(
        taxi_scooters_subscription,
        language=language,
        screens=['discovery'],
        expected=(200, {'features': {}}),
    )


@pytest.mark.now('2022-02-18T02:48:00+03:00')
@pytest.mark.experiments3(filename='scooters_subscription.json')
@pytest.mark.experiments3(filename='scooters_subscription_plus.json')
@pytest.mark.experiments3(filename='scooters_subscription_screens.json')
async def test_wrong_position(taxi_scooters_subscription, mockserver):
    # Arrange
    h.mock_intervals(mockserver, [])
    h.mock_offers(mockserver, [], regions=[10000])

    # Act & Assert
    await get_screen_check(
        taxi_scooters_subscription,
        screen='main',
        language='ru',
        has_plus=True,
        position='0,0',
        expected=(200, {'sections': []}),
    )
