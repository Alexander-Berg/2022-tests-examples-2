import pytest


@pytest.mark.translations(
    tariff={
        'name.selfdriving': {'ru': 'Я сам!'},
        'name.demostand': {'ru': 'demostand'},
        'name.uberstart': {'ru': 'uberstart'},
        'name.uberblack': {'ru': 'uberblack'},
        'name.econom': {'ru': 'Экономь!'},
        'name.comfort': {'ru': 'comfort'},
        'name.comfortplus': {'ru': 'comfortplus'},
        'name.business': {'ru': 'business'},
        'name.ubernight': {'ru': 'Убер в ночи'},
        'name.ultimate': {'ru': 'ultimate'},
        'name.maybach': {'ru': 'maybach'},
        'name.uberlux': {'ru': 'uberlux'},
        'name.uberx': {'ru': 'uberx'},
        'name.uberkids': {'ru': 'uberkids'},
        'name.premium_van': {'ru': 'premium_van'},
        'name.minivan': {'ru': 'minivan'},
        'name.child_tariff': {'ru': 'child_tariff'},
        'name.personal_driver': {'ru': 'personal_driver'},
        'name.suv': {'ru': 'suv'},
        'name.premium_suv': {'ru': 'premium_suv'},
        'name.cargo': {'ru': 'cargo'},
        'name.night': {'ru': 'night'},
        'name.universal': {'ru': 'universal'},
        'name.pool': {'ru': 'pool'},
        'name.express': {'ru': 'express'},
        'name.drive': {'ru': 'Драйв!'},
        'interval_description': {'ru': 'от %(minimal_price)s'},
        'routestats.legacy_details.description': {'ru': 'всего'},
        'currency_with_sign.rub': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency_sign.rub': {'ru': '₽'},
        'currency.rub': {'ru': 'руб.'},
        'routestats.surge.description': {'ru': 'Тариф временно увеличен'},
        'routestats.surge.reason_pins_free': {
            'ru': (
                'Это вынужденная мера, так как спрос на такси чрезвычайно '
                'высок. Она позволит привлечь больше водителей.'
            ),
        },
        'routestats.surge.button_text': {'ru': 'Вызвать такси'},
        'routestats.surge.comment': {
            'ru': (
                'Вы сможете заказать такси по обычному тарифу, когда спрос '
                'уменьшится'
            ),
        },
        'routestats.surge.title': {'ru': '×%(surge_coeff)s'},
        'routestats.surge.surcharge_title': {
            'ru': '+%(surcharge)s $SIGN$$CURRENCY$',
        },
        'routestats.surge.mult_and_surcharge_title': {
            'ru': '×%(surge_coeff)s +%(surcharge)s $SIGN$$CURRENCY$',
        },
    },
    client_messages={
        'mainscreen.description_selfdriving_moscow': {
            'ru': 'Nissan Tiida, Mazda Demio, Toyota Corolla',
        },
        'mainscreen.description_ubernight': {'ru': 'Juke'},
        'mainscreen.description_vip': {'ru': 'Oka'},
        'routestats.tariff_unavailable.tariff_is_inactive': {
            'ru': 'Нет свободных машин',
        },
        'routestats.econom.tariff_unavailable.tariff_is_inactive': {
            'ru': 'Совсем нет свободных машин',
        },
        'routestats.tariff_unavailable.pool_no_match': {
            'ru': 'Не нашлось попутчиков по маршруту',
        },
        'routestats.tariff_unavailable.no_free_cars_nearby': {
            'ru': 'Нет у нас свободных машин',
        },
        'surge_reduced_lookandfeel.alert': {'ru': 'Высокий спрос'},
        'surge_reduced_lookandfeel.card_title': {
            'ru': 'Тариф временно увеличен',
        },
        'surge_reduced_lookandfeel.card_body': {
            'ru': (
                'Из-за высокого спроса на такси рядом с вами не хватает '
                'свободных машин. Стоимость поездок временно увеличилась '
                '— это позволит привлечь больше водителей в ваш район. Как '
                'только их будет достаточно, цена сразу же станет прежней.'
            ),
        },
        'surge_reduced_lookandfeel.card_ok': {'ru': 'Понятно'},
    },
)
@pytest.mark.config(
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': [
            'eda',
            'lavka',
            'express',
            'econom',
            'business',
            'comfortplus',
            'vip',
            'pool',
            'ultimate',
            'maybach',
            'minivan',
            'drivers_pool',
            'child_tariff',
            'start',
            'standart',
            'mkk',
            'selfdriving',
            'demostand',
            'promo',
            'premium_van',
            'mkk_antifraud',
            'cargo',
            'personal_driver',
            'suv',
            'premium_suv',
            'universal',
            'night',
            'drive',
        ],
        'yauber': [
            'uberx',
            'uberselect',
            'uberblack',
            'uberkids',
            'uberstart',
            'uberlux',
            'ubervan',
            'uberselectplus',
            'ubernight',
        ],
    },
    TARIFF_KEY_OVERRIDE={
        'econom': [
            {
                'from': 'routestats.tariff_unavailable.tariff_is_inactive',
                'to': (
                    'routestats.econom.tariff_unavailable.tariff_is_inactive'
                ),
            },
        ],
    },
    UBER_PREFERRED_CATEGORIES_ORDER=['ubernight', 'uberblack', 'uberlux'],
    ROUTESTATS_SURGE_ICON_SHOW=False,
    SURGE_COLOR_BUTTON_MIN_VALUE_ZONE={'__default__': 1.2},
    SURGE_POPUP_MIN_COEFF_ZONE={'__default__': 2.5, 'moscow': 1.5},
    MAX_ALPHA_SURCHARGE_ONLY_USER=0.1,
    MIN_ALPHA_SURGE_ONLY_USER=0.8,
    CURRENCY_FORMATTING_RULES={'RUB': {'__default__': 2}},
)
@pytest.mark.experiments3(
    match={
        'applications': [
            {'name': 'uber_android', 'version_range': {'from': '0.0.0'}},
        ],
        'enabled': True,
        'predicate': {'type': 'true'},
    },
    name='uber_disable_color_button',
    consumers=['uservices/routestats'],
    clauses=[],
    default_value={'enabled': True},
)
@pytest.mark.experiments3(
    is_config=True,
    name='skip_hidden_tariff_info',
    consumers=['uservices/routestats'],
    default_value={'enabled': True},
)
@pytest.mark.experiments3(
    is_config=True,
    name='routestats:uservices:fallback:plugins:top_level_fallback:create_pin',
    consumers=['uservices/routestats'],
    default_value={'enabled': True},
)
@pytest.mark.experiments3(
    is_config=True,
    name='routestats:uservices:fallback:plugins:top_level_fallback:surger',
    consumers=['uservices/routestats'],
    default_value={'enabled': True},
)
@pytest.mark.tariff_settings(filename='tariff_settings.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.parametrize(
    'brand, prefix',
    [
        pytest.param('yataxi', '', id='default'),
        pytest.param('yauber', 'uber_', id='uber'),
    ],
)
async def test_basic_fallback(
        taxi_routestats, mockserver, load_json, brand, prefix,
):
    @mockserver.json_handler('/pin-storage/v1/create_pin')
    def v1_create_pin(request):
        expected_pin = dict(
            user_id='',
            personal_phone_id='123-45',
            tariff_zone='moscow',
            point_a=[37.587569, 55.733393],
            client=dict(name=f'{prefix}android', version=[99, 100, 101]),
            user_layer='default',
            classes=[],
            experiments=[],
            is_fake=False,
            calculation_id='so_awfully_huge_surge',
        )
        assert request.json['pin'] == expected_pin
        return mockserver.make_response(
            status=200, json={'timestamp': '12345'},
        )

    @mockserver.json_handler('/surge-calculator/v1/calc-surge')
    def v1_calc_surge(request):
        req = request.json
        if brand == 'yataxi':
            assert set(req['classes']) == set(
                [
                    'econom',
                    'business',
                    'comfortplus',
                    'vip',
                    'ultimate',
                    'maybach',
                    'premium_van',
                    'minivan',
                    'child_tariff',
                    'personal_driver',
                    'selfdriving',
                    'suv',
                    'premium_suv',
                    'cargo',
                    'night',
                    'universal',
                    'pool',
                    'express',
                    'demostand',
                    'drive',
                ],
            )
        elif brand == 'yauber':
            assert set(req['classes']) == set(
                [
                    'uberx',
                    'uberstart',
                    'uberkids',
                    'uberlux',
                    'uberblack',
                    'ubernight',
                ],
            )
        else:
            assert False
        req.pop('classes')
        assert req == dict(
            user_id='',
            phone_id='some_phone_id',
            tariff_zone='moscow',
            point_a=[37.587569, 55.733393],
            intent='price_calculation',
            authorized=False,
            use_cache=True,
        )
        surge = load_json(f'{prefix}surger_response.json')
        return mockserver.make_response(json=surge, status=200)

    pa_headers = {
        'X-Request-Language': 'ru',
        'X-Request-Application': (
            'app_ver1=99,app_ver2=100,app_ver3=101,'
            f'app_name={prefix}android,app_brand={brand}'
        ),
        'X-YaTaxi-PhoneId': 'some_phone_id',
        'X-YaTaxi-User': 'personal_phone_id=123-45',
    }

    req = {
        'route': [[37.587569, 55.733393]],
        'summary_version': 2,
        'format_currency': True,
    }
    response = await taxi_routestats.post(
        'v1/routestats/fallback', req, headers=pa_headers,
    )
    # create_pin is deattached, so it can be 0 or 1 call
    assert v1_create_pin.times_called in (0, 1)
    assert v1_calc_surge.times_called == 1
    assert response.status_code == 200
    assert response.json() == load_json(f'{prefix}fallback_response.json')
