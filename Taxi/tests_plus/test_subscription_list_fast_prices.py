import pytest


@pytest.mark.config(PLUS_SERVICE_ENABLED=False)
@pytest.mark.config(
    PLUS_ALLOWED_SUBSCRIPTIONS_BY_COUNTRIES={'ru': ['plus_russia']},
)
async def test_list_disabled(web_plus, mock_mediabilling):
    result = await web_plus.internal_list.request().perform()
    assert result.status_code == 429


@pytest.mark.config(
    PLUS_ALLOWED_SUBSCRIPTIONS_BY_COUNTRIES={},
    PLUS_SUBSCRIPTIONS_TO_PRODUCT_MAPPING={
        'ya_plus_ru': (
            'ru.yandex.mobile.music.5min.native.web.notrial.notify.debug'
        ),
        'ya_plus_belarus': (
            'ru.yandex.plus.30min.autorenewable.native.web.notrial.debug'
        ),
    },
)
async def test_list_no_country(web_plus, mock_mediabilling):
    result = await web_plus.internal_list.request().perform()
    assert result.status_code == 200
    content = result.json()
    assert not content['allowed_subscriptions']


@pytest.mark.config(
    PLUS_ALLOWED_SUBSCRIPTIONS_BY_COUNTRIES={'ru': []},
    PLUS_SUBSCRIPTIONS_TO_PRODUCT_MAPPING={
        'ya_plus_ru': (
            'ru.yandex.mobile.music.5min.native.web.notrial.notify.debug'
        ),
        'ya_plus_belarus': (
            'ru.yandex.plus.30min.autorenewable.native.web.notrial.debug'
        ),
    },
)
async def test_list_not_available(web_plus, mock_mediabilling):
    result = await web_plus.internal_list.request().perform()
    assert result.status_code == 200
    content = result.json()
    assert not content['allowed_subscriptions']


@pytest.mark.config(
    PLUS_ALLOWED_SUBSCRIPTIONS_BY_COUNTRIES={
        'ru': ['ya_plus_russia', 'kinopoisk_sub'],
    },
    PLUS_PROMOTED_SUBSCRIPTIONS_BY_COUNTRIES={'ru': ['ya_plus_russia']},
    PLUS_SUBSCRIPTIONS_TO_PRODUCT_MAPPING={
        'ya_plus_russia': (
            'ru.yandex.mobile.music.5min.native.web.notrial.notify.debug'
        ),
        'kinopoisk_sub': (
            'ru.yandex.plus.30min.autorenewable.native.web.notrial.debug'
        ),
    },
)
async def test_list_user_has_subscription(web_plus, mock_mediabilling):
    result = (
        await web_plus.internal_list.request()
        .headers(pass_flags='phonish,ya-plus')
        .perform()
    )

    assert result.status_code == 200
    content = result.json()
    assert content['allowed_subscriptions'] == [
        {
            'purchase_info': {
                'action_text': 'Подключить',
                'action_subtitle': 'и быть счастливым',
                'currency_rules': {
                    'code': 'RUB',
                    'sign': '₽',
                    'template': '$VALUE$ $SIGN$$CURRENCY$',
                    'text': 'руб.',
                },
                'title': '169 $SIGN$$CURRENCY$ в месяц',
            },
            'subscription_id': 'kinopoisk_sub',
        },
    ]
    assert not content['promoted_subscriptions']
    assert content['manage_info'] == {
        'url': 'https://plus.yandex.ru',
        'title': 'Вы в Плюсе',
        'details_text': 'детали',
    }


@pytest.mark.parametrize(
    'ip_address,subscriptions',
    [
        ('185.15.98.233', ['ya_plus_ru']),
        ('93.170.252.25', ['ya_plus_belarus']),
    ],
)
@pytest.mark.config(
    PLUS_ALLOWED_SUBSCRIPTIONS_BY_COUNTRIES={
        'ru': ['ya_plus_ru'],
        'by': ['ya_plus_belarus'],
    },
    PLUS_SUBSCRIPTIONS_TO_PRODUCT_MAPPING={
        'ya_plus_ru': (
            'ru.yandex.mobile.music.5min.native.web.notrial.notify.debug'
        ),
        'ya_plus_belarus': (
            'ru.yandex.plus.30min.autorenewable.native.web.notrial.debug'
        ),
    },
)
async def test_ip_address_resolving(
        web_plus, ip_address, subscriptions, mock_mediabilling,
):
    result = (
        await web_plus.internal_list.request()
        .headers(remote_ip=ip_address)
        .perform()
    )
    assert result.status_code == 200

    content = result.json()
    allowed = [x['subscription_id'] for x in content['allowed_subscriptions']]
    assert set(allowed) == set(subscriptions)


@pytest.mark.config(
    PLUS_ALLOWED_SUBSCRIPTIONS_BY_COUNTRIES={'ru': ['plus_30_min']},
    PLUS_PROMOTED_SUBSCRIPTIONS_BY_COUNTRIES={
        'ru': ['plus_30_min', 'plus_russia'],
    },
    PLUS_SUBSCRIPTIONS_TO_PRODUCT_MAPPING={
        'plus_5_min': (
            'ru.yandex.mobile.music.5min.native.web.notrial.notify.debug'
        ),
        'plus_30_min': (
            'ru.yandex.plus.30min.autorenewable.native.web.notrial.debug'
        ),
    },
)
async def test_list_fast_prices_basic(web_plus, mock_mediabilling):
    result = await web_plus.internal_list.request().perform()
    assert result.status_code == 200

    content = result.json()
    promoted = {
        x['subscription_id'] for x in content['promoted_subscriptions']
    }
    allowed = {x['subscription_id'] for x in content['allowed_subscriptions']}

    assert promoted == {'plus_30_min'}
    assert allowed == {'plus_30_min'}


@pytest.mark.config(
    PLUS_ALLOWED_SUBSCRIPTIONS_BY_COUNTRIES={'ru': ['plus_30_min']},
    PLUS_PROMOTED_SUBSCRIPTIONS_BY_COUNTRIES={
        'ru': ['plus_30_min', 'plus_russia'],
    },
    PLUS_SUBSCRIPTIONS_TO_PRODUCT_MAPPING={},
)
async def test_list_fast_prices_empty_mapping(web_plus, mock_mediabilling):
    result = await web_plus.internal_list.request().perform()
    assert result.status_code == 200

    content = result.json()
    promoted = {
        x['subscription_id'] for x in content['promoted_subscriptions']
    }
    allowed = {x['subscription_id'] for x in content['allowed_subscriptions']}

    assert promoted == set()
    assert allowed == set()


@pytest.mark.config(
    PLUS_ALLOWED_SUBSCRIPTIONS_BY_COUNTRIES={
        'ru': ['plus_30_min', 'plus_5_min'],
    },
    PLUS_PROMOTED_SUBSCRIPTIONS_BY_COUNTRIES={
        'ru': ['plus_30_min', 'plus_russia'],
    },
    PLUS_SUBSCRIPTIONS_TO_PRODUCT_MAPPING={
        'plus_5_min': (
            'ru.yandex.mobile.music.5min.native.web.notrial.notify.debug'
        ),
        'plus_30_min': (
            'ru.yandex.plus.30min.autorenewable.native.web.notrial.debug'
        ),
    },
)
async def test_list_fast_prices_two_subscriptions(web_plus, mock_mediabilling):
    result = await web_plus.internal_list.request().perform()
    assert result.status_code == 200

    content = result.json()
    promoted = {
        x['subscription_id'] for x in content['promoted_subscriptions']
    }
    allowed = {x['subscription_id'] for x in content['allowed_subscriptions']}

    assert promoted == {'plus_30_min'}
    assert allowed == {'plus_30_min', 'plus_5_min'}


@pytest.mark.config(
    PLUS_ALLOWED_SUBSCRIPTIONS_BY_COUNTRIES={
        'ru': ['ya_plus_ru', 'ya_plus_ru_trial'],
    },
    PLUS_PROMOTED_SUBSCRIPTIONS_BY_COUNTRIES={
        'ru': ['ya_plus_ru', 'ya_plus_ru_trial'],
    },
    PLUS_SUBSCRIPTIONS_TO_PRODUCT_MAPPING={
        'ya_plus_ru': (
            'ru.yandex.mobile.music.5min.native.web.notrial.notify.debug'
        ),
        'ya_plus_ru_trial': (
            'ru.yandex.plus.30min.autorenewable.native.web.notrial.debug'
        ),
    },
)
async def test_list_check_allow_trial(web_plus, mock_mediabilling):
    result = await web_plus.internal_list.request().perform()
    assert result.status_code == 200

    content = result.json()
    promoted = {
        x['subscription_id'] for x in content['promoted_subscriptions']
    }
    allowed = {x['subscription_id'] for x in content['allowed_subscriptions']}

    allowed_trial = [
        x
        for x in content['allowed_subscriptions']
        if x['subscription_id'] == 'ya_plus_ru_trial'
    ]

    assert promoted == {'ya_plus_ru', 'ya_plus_ru_trial'}
    assert allowed == {'ya_plus_ru', 'ya_plus_ru_trial'}
    assert allowed_trial[0] == {
        'subscription_id': 'ya_plus_ru_trial',
        'purchase_info': {
            'title': 'Первый месяц бесплатно',
            'subtitle': 'потом за 169 $SIGN$$CURRENCY$/мес',
            'action_text': 'Подключить',
            'action_subtitle': 'и быть счастливым',
            'currency_rules': {
                'code': 'RUB',
                'sign': '₽',
                'template': '$VALUE$ $SIGN$$CURRENCY$',
                'text': 'руб.',
            },
        },
    }


@pytest.mark.experiments3()
@pytest.mark.parametrize(
    'has_plus, has_cashback_plus',
    [(False, False), (False, True), (True, False), (True, True)],
)
async def test_could_upgrade_plus(
        web_plus, mock_mediabilling, has_plus, has_cashback_plus,
):
    pass_flags = ['phonish']
    if has_plus:
        pass_flags.append('ya-plus')
    if has_cashback_plus:
        pass_flags.append('cashback-plus')

    headers = dict(pass_flags=','.join(pass_flags))

    result = (
        await web_plus.internal_list.request().headers(**headers).perform()
    )
    assert result.status_code == 200

    content = result.json()

    import pprint
    pprint.pprint(content)

    could_upgrade_plus = has_plus and not has_cashback_plus
    assert content['could_upgrade_plus'] == could_upgrade_plus

    if could_upgrade_plus:
        assert 'upgrade_info' in content
        upgrade_info = content['upgrade_info']
        expected = {
            'upgrade_button': {
                'title': 'Кэшбек вместо скидки',
                'subtitle': '10% остаются с вами',
                'action_text': 'Активировать баллы',
                'action_subtitle': 'вместо скидки',
            },
        }
        assert upgrade_info == expected


@pytest.mark.experiments3(
    filename='experiments3_no_could_upgrade_subscription.json',
)
@pytest.mark.parametrize(
    'has_plus, has_cashback_plus',
    [(False, False), (False, True), (True, False), (True, True)],
)
async def test_could_upgrade_plus_no_exp_could_upgrade_subscription(
        web_plus, mock_mediabilling, has_plus, has_cashback_plus,
):
    pass_flags = ['phonish']
    if has_plus:
        pass_flags.append('ya-plus')
    if has_cashback_plus:
        pass_flags.append('cashback-plus')

    headers = dict(pass_flags=','.join(pass_flags))

    result = (
        await web_plus.internal_list.request().headers(**headers).perform()
    )
    assert result.status_code == 200

    content = result.json()

    assert not content['could_upgrade_plus']


@pytest.mark.experiments3(filename='experiments3_no_fetch_wallets.json')
@pytest.mark.parametrize(
    'has_plus, has_cashback_plus',
    [(False, False), (False, True), (True, False), (True, True)],
)
async def test_could_upgrade_plus_no_exp_fetch_wallets(
        web_plus, mockserver, mock_mediabilling, has_plus, has_cashback_plus,
):
    @mockserver.handler('/plus-wallet/v1/balances')
    def _mock_balances(request):
        # we should not go here
        assert False

    pass_flags = ['phonish']
    if has_plus:
        pass_flags.append('ya-plus')
    if has_cashback_plus:
        pass_flags.append('cashback-plus')

    headers = dict(pass_flags=','.join(pass_flags))

    result = (
        await web_plus.internal_list.request().headers(**headers).perform()
    )
    assert result.status_code == 200

    content = result.json()
    assert not content['could_upgrade_plus']


@pytest.mark.experiments3()
@pytest.mark.parametrize(
    'balance, expect_upgrade_button',
    [(None, False), ('0.000', False), ('100.000', True)],
)
async def test_could_upgrade_plus_balance(
        web_plus,
        mockserver,
        mock_mediabilling,
        balance,
        expect_upgrade_button,
):
    @mockserver.handler('/plus-wallet/v1/balances')
    def _mock_balances(request):
        balances = []
        if balance is not None:
            balances.append(
                {
                    'balance': balance,
                    'currency': 'RUB',
                    'wallet_id': 'some_wallet_id',
                },
            )
        return mockserver.make_response(
            json={'balances': balances}, status=200,
        )

    pass_flags = ['phonish', 'ya-plus']

    headers = dict(pass_flags=','.join(pass_flags))

    result = (
        await web_plus.internal_list.request().headers(**headers).perform()
    )
    assert result.status_code == 200

    content = result.json()
    assert content['could_upgrade_plus'] == expect_upgrade_button


@pytest.mark.config(PLUS_TARGET_SUBSCRIPTIONS='landing-taxi')
@pytest.mark.parametrize(
    'target',
    [
        pytest.param('landing-taxi'),
        pytest.param(
            'taxi-exp',
            marks=pytest.mark.experiments3(
                filename='experiments3_one_month_trial.json',
            ),
        ),
    ],
)
async def test_another_target_by_exp(web_plus, mockserver, target):
    @mockserver.handler('/fast-prices/billing/transitions')
    def _mock_get_transitions(request):
        assert request.query['target'] == target
        return mockserver.make_response('{"transitions": []}', status=200)

    result = await web_plus.internal_list.request().perform()
    assert result.status_code == 200
