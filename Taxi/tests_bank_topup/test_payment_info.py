import pytest

from tests_bank_topup import common

DEFAULT_LOCALE = 'ru'
DEFAULT_THRESHOLD_AMOUNT = '1500'


def get_headers(yabank_session_uuid=common.DEFAULT_YABANK_SESSION_UUID):
    return {
        'X-Yandex-BUID': common.DEFAULT_YANDEX_BUID,
        'X-Yandex-UID': common.DEFAULT_YANDEX_UID,
        'X-YaBank-PhoneID': common.DEFAULT_YABANK_PHONE_ID,
        'X-YaBank-SessionUUID': yabank_session_uuid,
        'X-Ya-User-Ticket': common.DEFAULT_USER_TICKET,
    }


def get_headers_exps_disabled():
    return get_headers(yabank_session_uuid='disabled')


def get_headers_exps_enabled():
    return get_headers(yabank_session_uuid='enabled')


def make_autotopup_widget(
        currency=common.DEFAULT_CURRENCY,
        currency_sign=common.DEFAULT_CURRENCY_SIGN,
        threshold_amount=DEFAULT_THRESHOLD_AMOUNT,
        money_amount=common.DEFAULT_AMOUNT,
        l10_threshold_amount=DEFAULT_THRESHOLD_AMOUNT,
        l10_money_amount=common.DEFAULT_AMOUNT,
):
    return {
        'title': (
            'Пополнять на %s\xa0%s, когда на счете меньше %s\xa0%s'
            % (
                l10_money_amount,
                currency_sign,
                l10_threshold_amount,
                currency_sign,
            )
        ),
        'description': 'Так вы не упустите кэшбек, если забыли про баланс',
        'switch': 'OFF',
        'payload': {
            'type': 'LIMIT_EXACT',
            'agreement_id': common.DEFAULT_PUBLIC_AGREEMENT_ID,
            'payment_method_id': common.DEFAULT_PAYMENT_METHOD_ID,
            'threshold': {'amount': threshold_amount, 'currency': currency},
            'money': {'amount': money_amount, 'currency': currency},
        },
    }


@pytest.mark.parametrize(
    'payment_status, info_status',
    [
        ('CREATED', 'CREATED'),
        ('FAILED', 'FAILED'),
        ('REFUNDED', 'FAILED'),
        ('FAILED_SAVED', 'FAILED'),
        ('REFUNDED_SAVED', 'FAILED'),
        ('SUCCESS_SAVED', 'SUCCESS'),
        ('CLEARING', 'SUCCESS'),
        ('CLEARED', 'SUCCESS'),
        ('SUCCESS_SAVING', 'PROCESSING'),
        ('REFUNDED_SAVING', 'PROCESSING'),
        ('FAILED_SAVING', 'PROCESSING'),
        ('REFUNDING', 'PROCESSING'),
        ('PAYMENT_RECEIVED', 'PROCESSING'),
    ],
)
async def test_ok(pgsql, taxi_bank_topup, payment_status, info_status):
    body = {'payment_id': common.TEST_PAYMENT_ID}
    headers = get_headers()

    common.set_payment_status(pgsql, status=payment_status)

    response = await taxi_bank_topup.post(
        '/v1/topup/v1/payment/get_info', json=body, headers=headers,
    )
    assert response.status_code == 200
    json = response.json()
    assert json['payment_info']['payment_id'] == common.TEST_PAYMENT_ID
    assert json['status'] == info_status
    assert json['payment_info']['image'] == 'image_url'
    assert json['payment_info']['money'] == {
        'amount': '100',
        'currency': 'RUB',
    }
    assert (
        json['payment_info']['creation_timestamp']
        == '2021-10-31T00:34:00.0+00:00'
    )


async def test_payment_id_wrong_format(taxi_bank_topup):
    body = {'payment_id': 'wrong_format'}
    headers = get_headers()
    response = await taxi_bank_topup.post(
        '/v1/topup/v1/payment/get_info', json=body, headers=headers,
    )
    assert response.status_code == 400


async def test_not_found(taxi_bank_topup):
    body = {'payment_id': 'd9abbfb7-84d4-44be-94b3-8f8ea7eb31d0'}
    headers = get_headers()
    response = await taxi_bank_topup.post(
        '/v1/topup/v1/payment/get_info', json=body, headers=headers,
    )
    assert response.status_code == 404


async def test_wrong_user(taxi_bank_topup):
    body = {'payment_id': common.TEST_PAYMENT_ID}
    headers = get_headers()
    headers.update({'X-Yandex-BUID': 'wrong_buid'})
    response = await taxi_bank_topup.post(
        '/v1/topup/v1/payment/get_info', json=body, headers=headers,
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'card_bin, payment_system, last_digits, description',
    [
        ('423412', 'VISA', '1234', 'С карты Visa ···· 1234'),
        ('5234', 'MASTERCARD', '2345', 'С карты MasterCard ···· 2345'),
        ('2234', 'MIR', '3456', 'С карты МИР ···· 3456'),
        ('8234', 'UNKNOWN', '4567', 'С карты ···· 4567'),
        (None, None, None, 'С карты'),
    ],
)
async def test_card_description(
        taxi_bank_topup,
        pgsql,
        payment_system,
        card_bin,
        last_digits,
        description,
):
    body = {'payment_id': common.TEST_PAYMENT_ID}
    headers = get_headers()
    if payment_system:
        common.set_card_info(pgsql, payment_system, card_bin, last_digits)
    response = await taxi_bank_topup.post(
        '/v1/topup/v1/payment/get_info', json=body, headers=headers,
    )

    json = response.json()
    assert json['payment_info']['description'] == description


async def test_no_tanker_key(taxi_bank_topup, pgsql, taxi_config):
    topup_config = taxi_config.get('BANK_TOPUP_TRANSACTIONS_TANKER_KEYS')
    topup_config['payment_system_name']['mir'] = 'no_key'
    body = {'payment_id': common.TEST_PAYMENT_ID}

    common.set_card_info(pgsql, 'MIR', '2234', 'С карты МИР ···· 3456')
    headers = get_headers()

    response = await taxi_bank_topup.post(
        '/v1/topup/v1/payment/get_info', json=body, headers=headers,
    )

    assert response.json() == {
        'code': '500',
        'message': 'Internal Server Error',
    }


@pytest.mark.parametrize(
    'locale, topup',
    [('en', 'Top up'), ('ru', 'Пополнение'), ('unknown', 'Пополнение')],
)
async def test_tanker_locales(
        taxi_bank_topup, locale, topup, pgsql, taxi_config,
):

    body = {'payment_id': common.TEST_PAYMENT_ID}
    common.set_card_info(pgsql, 'MIR', '2234', 'С карты МИР ···· 3456')
    headers = get_headers()
    headers.update({'X-Request-Language': locale})
    response = await taxi_bank_topup.post(
        '/v1/topup/v1/payment/get_info', json=body, headers=headers,
    )

    assert response.json()['payment_info']['name'] == topup


@pytest.mark.parametrize(
    'payment_status',
    [
        'CREATED',
        'FAILED',
        'REFUNDED',
        'FAILED_SAVED',
        'REFUNDED_SAVED',
        'SUCCESS_SAVED',
        'CLEARING',
        'CLEARED',
        'SUCCESS_SAVING',
        'REFUNDED_SAVING',
        'FAILED_SAVING',
        'REFUNDING',
        'PAYMENT_RECEIVED',
    ],
)
async def test_autotupop_widget_not_shown_if_experiment_not_exists(
        pgsql, taxi_bank_topup, payment_status,
):

    body = {'payment_id': common.TEST_PAYMENT_ID}
    headers = get_headers(
        yabank_session_uuid=common.DEFAULT_YABANK_SESSION_UUID,
    )
    headers.update({'X-Request-Language': DEFAULT_LOCALE})
    common.set_payment_status(pgsql, status=payment_status)

    response = await taxi_bank_topup.post(
        '/v1/topup/v1/payment/get_info', json=body, headers=headers,
    )

    assert response.status_code == 200
    assert not response.json().__contains__('widgets')


@pytest.mark.experiments3(filename='topup_autotopup_widgets_experiments.json')
@pytest.mark.config(BANK_TOPUP_WALLET_CURRENCY_PRECISION={'RUB': 2})
@pytest.mark.parametrize(
    'payment_status',
    [
        'CREATED',
        'FAILED',
        'REFUNDED',
        'FAILED_SAVED',
        'REFUNDED_SAVED',
        'SUCCESS_SAVED',
        'CLEARING',
        'CLEARED',
        'SUCCESS_SAVING',
        'REFUNDED_SAVING',
        'FAILED_SAVING',
        'REFUNDING',
        'PAYMENT_RECEIVED',
    ],
)
async def test_autotupop_widget_not_shown_if_disabled_in_experiment(
        pgsql, taxi_bank_topup, payment_status,
):

    body = {'payment_id': common.TEST_PAYMENT_ID}
    headers = get_headers_exps_disabled()
    headers.update({'X-Request-Language': DEFAULT_LOCALE})
    common.set_payment_status(pgsql, status=payment_status)

    response = await taxi_bank_topup.post(
        '/v1/topup/v1/payment/get_info', json=body, headers=headers,
    )

    assert response.status_code == 200
    assert not response.json().__contains__('widgets')


@pytest.mark.experiments3(filename='topup_autotopup_widgets_experiments.json')
@pytest.mark.config(BANK_TOPUP_WALLET_CURRENCY_PRECISION={'RUB': 2})
@pytest.mark.parametrize(
    'payment_status, expected_widgets',
    [
        ('CREATED', []),
        ('PAYMENT_RECEIVED', []),
        ('FAILED', []),
        ('REFUNDED', []),
        ('REFUNDING', []),
        ('FAILED_SAVED', []),
        ('REFUNDED_SAVED', []),
        ('SUCCESS_SAVED', [make_autotopup_widget()]),
        ('CLEARING', [make_autotopup_widget()]),
        ('CLEARED', [make_autotopup_widget()]),
        ('FAILED_SAVING', []),
        ('REFUNDED_SAVING', []),
        ('SUCCESS_SAVING', []),
    ],
)
async def test_autotupop_widget_shown_with_allowed_status(
        pgsql, taxi_bank_topup, payment_status, expected_widgets,
):
    body = {'payment_id': common.TEST_PAYMENT_ID}
    headers = get_headers_exps_enabled()
    headers.update({'X-Request-Language': DEFAULT_LOCALE})
    common.set_payment_status(pgsql, status=payment_status)

    response = await taxi_bank_topup.post(
        '/v1/topup/v1/payment/get_info', json=body, headers=headers,
    )

    assert response.status_code == 200
    assert response.json().get('widgets', []) == expected_widgets


@pytest.mark.experiments3(filename='topup_autotopup_widgets_experiments.json')
@pytest.mark.config(BANK_TOPUP_WALLET_CURRENCY_PRECISION={'RUB': 2})
@pytest.mark.parametrize(
    'payment_currency, expected_widgets',
    [('RUB', [make_autotopup_widget()]), ('EUR', []), ('USD', [])],
)
@pytest.mark.parametrize(
    'payment_status', ['SUCCESS_SAVED', 'CLEARING', 'CLEARED'],
)
async def test_autotupop_widget_not_shown_if_currency_precision_not_in_config(
        pgsql,
        taxi_bank_topup,
        payment_currency,
        expected_widgets,
        payment_status,
):
    body = {'payment_id': common.TEST_PAYMENT_ID}
    headers = get_headers_exps_enabled()
    headers.update({'X-Request-Language': DEFAULT_LOCALE})
    common.set_payment_status(pgsql, status=payment_status)
    common.set_payment_currency(pgsql, currency=payment_currency)

    response = await taxi_bank_topup.post(
        '/v1/topup/v1/payment/get_info', json=body, headers=headers,
    )

    assert response.status_code == 200
    assert response.json().get('widgets', []) == expected_widgets


@pytest.mark.experiments3(filename='topup_autotopup_widgets_experiments.json')
@pytest.mark.parametrize(
    'currency_precision, expected_widgets',
    [
        ({'RUB': 0}, [make_autotopup_widget()]),
        ({'RUB': 2}, [make_autotopup_widget()]),
        ({'RUB': 4}, []),
    ],
)
@pytest.mark.parametrize(
    'payment_status', ['SUCCESS_SAVED', 'CLEARING', 'CLEARED'],
)
async def test_autotupop_widget_not_shown_if_currency_precision_not_supported(
        pgsql,
        taxi_config,
        taxi_bank_topup,
        currency_precision,
        expected_widgets,
        payment_status,
):
    taxi_config.set_values(
        {'BANK_TOPUP_WALLET_CURRENCY_PRECISION': currency_precision},
    )

    body = {'payment_id': common.TEST_PAYMENT_ID}
    headers = get_headers_exps_enabled()
    headers.update({'X-Request-Language': DEFAULT_LOCALE})
    common.set_payment_status(pgsql, status=payment_status)

    response = await taxi_bank_topup.post(
        '/v1/topup/v1/payment/get_info', json=body, headers=headers,
    )

    assert response.status_code == 200
    assert response.json().get('widgets', []) == expected_widgets


@pytest.mark.experiments3(filename='topup_autotopup_widgets_experiments.json')
@pytest.mark.parametrize(
    'payment_amount, currency_precision, expected_widgets',
    [
        (
            '123',
            {'RUB': 2},
            [
                make_autotopup_widget(
                    money_amount='123', l10_money_amount='123',
                ),
            ],
        ),
        (
            '123.4',
            {'RUB': 2},
            [
                make_autotopup_widget(
                    money_amount='123.4', l10_money_amount='123,4',
                ),
            ],
        ),
        (
            '123.45',
            {'RUB': 2},
            [
                make_autotopup_widget(
                    money_amount='123.45', l10_money_amount='123,45',
                ),
            ],
        ),
        ('123.456', {'RUB': 2}, []),
    ],
)
@pytest.mark.parametrize(
    'payment_status', ['SUCCESS_SAVED', 'CLEARING', 'CLEARED'],
)
async def test_autotupop_widget_not_shown_if_decimal_exception(
        pgsql,
        taxi_config,
        taxi_bank_topup,
        payment_amount,
        currency_precision,
        expected_widgets,
        payment_status,
):
    taxi_config.set_values(
        {'BANK_TOPUP_WALLET_CURRENCY_PRECISION': currency_precision},
    )

    body = {'payment_id': common.TEST_PAYMENT_ID}
    headers = get_headers_exps_enabled()
    headers.update({'X-Request-Language': DEFAULT_LOCALE})
    common.set_payment_status(pgsql, status=payment_status)
    common.set_payment_amount(pgsql, amount=payment_amount)

    response = await taxi_bank_topup.post(
        '/v1/topup/v1/payment/get_info', json=body, headers=headers,
    )

    assert response.status_code == 200
    assert response.json().get('widgets', []) == expected_widgets


@pytest.mark.experiments3(filename='topup_autotopup_widgets_experiments.json')
@pytest.mark.config(BANK_TOPUP_WALLET_CURRENCY_PRECISION={'RUB': 2})
@pytest.mark.parametrize(
    'payment_amount, expected_widgets',
    [
        ('50', []),
        (
            '150',
            [
                make_autotopup_widget(
                    money_amount='150', l10_money_amount='150',
                ),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'payment_status', ['SUCCESS_SAVED', 'CLEARING', 'CLEARED'],
)
async def test_autotupop_widget_not_shown_if_payment_amount_less_min_amount(
        pgsql,
        taxi_bank_topup,
        payment_amount,
        expected_widgets,
        payment_status,
):
    body = {'payment_id': common.TEST_PAYMENT_ID}
    headers = get_headers_exps_enabled()
    headers.update({'X-Request-Language': DEFAULT_LOCALE})
    common.set_payment_status(pgsql, status=payment_status)
    common.set_payment_amount(pgsql, amount=payment_amount)

    response = await taxi_bank_topup.post(
        '/v1/topup/v1/payment/get_info', json=body, headers=headers,
    )

    assert response.status_code == 200
    assert response.json().get('widgets', []) == expected_widgets


@pytest.mark.experiments3(filename='topup_autotopup_widgets_experiments.json')
@pytest.mark.config(BANK_TOPUP_WALLET_CURRENCY_PRECISION={'RUB': 2})
@pytest.mark.parametrize(
    'payment_status', ['SUCCESS_SAVED', 'CLEARING', 'CLEARED'],
)
async def test_widget_not_shown_if_active_autotopup_exists(
        pgsql, taxi_bank_topup, payment_status,
):
    body = {'payment_id': common.TEST_PAYMENT_ID}
    headers = get_headers_exps_enabled()
    headers.update({'X-Request-Language': DEFAULT_LOCALE})
    common.set_payment_status(pgsql, status=payment_status)

    common.insert_autotopup(
        pgsql,
        common.make_autotopup(
            bank_uid=common.DEFAULT_YANDEX_BUID, enabled=True,
        ),
    )

    response = await taxi_bank_topup.post(
        '/v1/topup/v1/payment/get_info', json=body, headers=headers,
    )

    assert response.status_code == 200
    assert not response.json().__contains__('widgets')


@pytest.mark.experiments3(filename='topup_autotopup_widgets_experiments.json')
@pytest.mark.config(BANK_TOPUP_WALLET_CURRENCY_PRECISION={'RUB': 2})
@pytest.mark.parametrize(
    'payment_status', ['SUCCESS_SAVED', 'CLEARING', 'CLEARED'],
)
async def test_widget_shown_if_not_active_autotopup_exists(
        pgsql, taxi_bank_topup, payment_status,
):
    body = {'payment_id': common.TEST_PAYMENT_ID}
    headers = get_headers_exps_enabled()
    headers.update({'X-Request-Language': DEFAULT_LOCALE})
    common.set_payment_status(pgsql, status=payment_status)

    common.insert_autotopup(
        pgsql,
        common.make_autotopup(
            bank_uid=common.ANOTHER_YANDEX_BUID, enabled=False,
        ),
    )

    response = await taxi_bank_topup.post(
        '/v1/topup/v1/payment/get_info', json=body, headers=headers,
    )

    assert response.status_code == 200
    assert response.json()['widgets'] == [make_autotopup_widget()]


@pytest.mark.experiments3(filename='topup_autotopup_widgets_experiments.json')
@pytest.mark.config(BANK_TOPUP_WALLET_CURRENCY_PRECISION={'RUB': 2})
@pytest.mark.parametrize(
    'payment_status', ['SUCCESS_SAVED', 'CLEARING', 'CLEARED'],
)
async def test_widget_shown_if_autotopup_exists_with_another_buid(
        pgsql, taxi_bank_topup, payment_status,
):
    body = {'payment_id': common.TEST_PAYMENT_ID}
    headers = get_headers_exps_enabled()
    headers.update({'X-Request-Language': DEFAULT_LOCALE})
    common.set_payment_status(pgsql, status=payment_status)

    common.insert_autotopup(
        pgsql,
        common.make_autotopup(
            bank_uid=common.ANOTHER_YANDEX_BUID, enabled=True,
        ),
    )

    response = await taxi_bank_topup.post(
        '/v1/topup/v1/payment/get_info', json=body, headers=headers,
    )

    assert response.status_code == 200
    assert response.json()['widgets'] == [make_autotopup_widget()]


@pytest.mark.experiments3(filename='topup_autotopup_widgets_experiments.json')
@pytest.mark.config(
    BANK_TOPUP_WALLET_CURRENCY_PRECISION={'RUB': 2, 'EUR': 2, 'USD': 2},
)
@pytest.mark.parametrize(
    'payment_currency,' 'expected_currency_sign,',
    [('RUB', '₽'), ('EUR', '€'), ('USD', '$')],
)
@pytest.mark.parametrize(
    'payment_status', ['SUCCESS_SAVED', 'CLEARING', 'CLEARED'],
)
async def test_autotupop_widget_content_support_diff_currency(
        pgsql,
        taxi_bank_topup,
        payment_status,
        payment_currency,
        expected_currency_sign,
):
    body = {'payment_id': common.TEST_PAYMENT_ID}
    headers = get_headers_exps_enabled()
    headers.update({'X-Request-Language': DEFAULT_LOCALE})
    common.set_payment_status(pgsql, status=payment_status)
    common.set_payment_currency(pgsql, currency=payment_currency)

    response = await taxi_bank_topup.post(
        '/v1/topup/v1/payment/get_info', json=body, headers=headers,
    )

    assert response.status_code == 200
    assert response.json()['widgets'] == [
        make_autotopup_widget(
            currency=payment_currency, currency_sign=expected_currency_sign,
        ),
    ]


@pytest.mark.experiments3(filename='topup_autotopup_widgets_experiments.json')
@pytest.mark.config(BANK_TOPUP_WALLET_CURRENCY_PRECISION={'RUB': 2})
@pytest.mark.parametrize(
    'payment_status', ['SUCCESS_SAVED', 'CLEARING', 'CLEARED'],
)
async def test_autotupop_widget_content_if_money_set_in_experiment(
        pgsql, taxi_bank_topup, payment_status,
):
    body = {'payment_id': common.TEST_PAYMENT_ID}
    headers = get_headers(yabank_session_uuid='enabled_with_money')
    headers.update({'X-Request-Language': DEFAULT_LOCALE})
    common.set_payment_status(pgsql, status=payment_status)

    response = await taxi_bank_topup.post(
        '/v1/topup/v1/payment/get_info', json=body, headers=headers,
    )

    assert response.status_code == 200
    assert response.json()['widgets'] == [
        make_autotopup_widget(money_amount='300', l10_money_amount='300'),
    ]
