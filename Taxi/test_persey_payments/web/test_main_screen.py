# pylint: disable=protected-access

import pytest

from test_persey_payments import conftest


@pytest.mark.translations(
    client_messages={
        'persey-payments.contribution.participants_tmpl': {
            'ru': [
                '$PARTICIPANTS_NUM$ человек',
                '$PARTICIPANTS_NUM$ человека',
                '$PARTICIPANTS_NUM$ человека',
            ],
        },
    },
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': '₽'},
    },
)
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.config(PERSEY_PAYMENTS_MOD_WHITELIST=[12, 21])
@pytest.mark.parametrize(
    'application, brand, expected_resp',
    [
        pytest.param(
            'android',
            'yataxi',
            'expected_resp_simple.json',
            marks=conftest.ride_subs_config(),
        ),
        pytest.param(
            'android',
            'yataxi',
            'expected_resp_simple.json',
            marks=conftest.ride_subs_config(
                {'application_fund_id': {'iphone': 'gift_to_an_angel'}},
            ),
        ),
        pytest.param(
            'iphone',
            'yataxi',
            'expected_resp_gift_to_an_angel.json',
            marks=conftest.ride_subs_config(
                {'application_fund_id': {'iphone': 'gift_to_an_angel'}},
            ),
        ),
    ],
)
async def test_simple(
        taxi_persey_payments_web,
        load_json,
        application,
        brand,
        expected_resp,
        mock_participant_count,
):
    x_request_application = f'app_name={application},app_brand={brand}'

    response = await taxi_persey_payments_web.post(
        '/4.0/persey-payments/v1/charity/main_screen',
        json={},
        headers={
            'X-Yandex-UID': '123',
            'X-YaTaxi-PhoneId': 'af35af35af35af35af35af35',
            'X-Request-Language': 'ru',
            'X-Request-Application': x_request_application,
        },
    )

    assert response.status == 200, await response.json()
    assert await response.json() == load_json(expected_resp)


@pytest.mark.translations(
    client_messages={
        'persey-payments.contribution.participants_tmpl': {
            'ru': '$PARTICIPANTS_NUM$ человек',
            'en': '$PARTICIPANTS_NUM$ person',
        },
    },
    tariff={
        'currency_with_sign.default': {
            'ru': '$VALUE$ $SIGN$$CURRENCY$',
            'en': '$VALUE$ $SIGN$$CURRENCY$',
        },
        'currency.rub': {'ru': '₽', 'en': '₽'},
    },
    notify={'a': {'b': 'c'}},
)
@pytest.mark.config(PERSEY_PAYMENTS_MOD_WHITELIST=[12, 21])
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.parametrize(
    'locale, expected_contribution',
    [
        ('ru', {'participants_num': 600, 'participants_tmpl': '600 человек'}),
        ('en', {'participants_num': 600, 'participants_tmpl': '600 person'}),
    ],
)
async def test_participants_num(
        web_app_client,
        web_app,
        locale,
        expected_contribution,
        mock_participant_count,
):
    response = await web_app_client.post(
        '/4.0/persey-payments/v1/charity/main_screen',
        json={},
        headers={
            'X-Yandex-UID': '123',
            'X-YaTaxi-PhoneId': 'af35af35af35af35af35af35',
            'X-Request-Language': locale,
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
        },
    )

    assert response.status == 200
    assert (await response.json())['contribution'] == expected_contribution


@pytest.mark.translations(
    client_messages={
        'persey-payments.contribution.participants_tmpl': {
            'ru': [
                '$PARTICIPANTS_NUM$ человек',
                '$PARTICIPANTS_NUM$ человека',
                '$PARTICIPANTS_NUM$ человека',
            ],
        },
    },
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': '₽'},
    },
)
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@conftest.ride_subs_config()
@pytest.mark.parametrize(
    'exp_default_index, exp_options',
    [
        (0, [10]),
        pytest.param(
            1,
            [21, 12],
            marks=pytest.mark.config(PERSEY_PAYMENTS_MOD_WHITELIST=[12, 21]),
        ),
    ],
)
async def test_mod_whitelist(
        taxi_persey_payments_web,
        exp_default_index,
        exp_options,
        mock_participant_count,
):
    response = await taxi_persey_payments_web.post(
        '/4.0/persey-payments/v1/charity/main_screen',
        json={},
        headers={
            'X-Yandex-UID': '123',
            'X-YaTaxi-PhoneId': 'af35af35af35af35af35af35',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
        },
    )

    assert response.status == 200

    response_json = await response.json()
    assert response_json['mod_info']['default_index'] == exp_default_index
    assert [
        o['value'] for o in response_json['mod_info']['options']
    ] == exp_options


@pytest.mark.translations(
    client_messages={
        'persey-payments.contribution.participants_tmpl': {
            'ru': '$PARTICIPANTS_NUM$ человек',
        },
    },
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency.rub': {'ru': '₽', 'en': '₽'},
    },
    notify={'a': {'b': 'c'}},
)
@pytest.mark.config(PERSEY_PAYMENTS_MOD_WHITELIST=[12, 21])
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
async def test_track_bound_uids(
        web_app_client, web_app, mock_participant_count,
):
    response = await web_app_client.post(
        '/4.0/persey-payments/v1/charity/main_screen',
        json={},
        headers={
            'X-Yandex-UID': '123',
            'X-YaTaxi-PhoneId': 'af35af35af35af35af35af35',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
        },
    )

    assert response.status == 200
    assert (await response.json())['contribution']['participants_num'] == 600
