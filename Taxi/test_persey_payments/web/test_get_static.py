import pytest

from test_persey_payments import conftest


CLIENT_MESSAGES = {
    'persey-payments.static.menu.title': {'ru': 'Помощь рядом'},
    'persey-payments.static.menu.subtitle': {'ru': 'Благотворительный проект'},
    'persey-payments.static.main_screen.common.header.title_tmpl': {
        'ru': '$PARTICIPANTS_NUM$ чел.',
    },
    'persey-payments.static.main_screen.common.header.subtitle_tmpl': {
        'ru': 'уже помогают',
    },
    'persey-payments.static.main_screen.common.title': {'ru': 'Помощь рядом'},
    'persey-payments.static.main_screen.common.text_tmpl': {
        'ru': (
            'Цена каждой вашей поездки, заказа Еды или Лавки будет '
            'округляться в пределах $MOD$ — разница пойдет в помощь врачам'
        ),
    },
    'persey-payments.static.main_screen.common.details.button_text': {
        'ru': 'Узнать больше',
    },
    'persey-payments.static.main_screen.subscribed.contribution.title': {
        'ru': 'Ваш вклад',
    },
    (
        'persey-payments.static.main_screen.subscribed.contribution.'
        'no_contribution_image_text'
    ): {'ru': '...'},
    'persey-payments.static.main_screen.subscribed.subs_toggle_title': {
        'ru': 'Вы помогаете врачам',
    },
    'persey-payments.static.main_screen.subscribed.share.button_text': {
        'ru': 'Поделиться',
    },
    'persey-payments.static.main_screen.subscribed.share.og_tags.title': {
        'ru': 'Помощь рядом',
    },
    (
        'persey-payments.static.main_screen.subscribed.share.og_tags.'
        'description'
    ): {'ru': 'Я доначу со своих поездок в такси'},
    'persey-payments.static.main_screen.no_subs.contribution.title': {
        'ru': '346 ₽ → 350 ₽',
    },
    'persey-payments.static.main_screen.no_subs.contribution.image_text': {
        'ru': '4₽',
    },
    'persey-payments.static.main_screen.no_subs.offer_title': {
        'ru': 'Условия оферты',
    },
    'persey-payments.static.main_screen.no_subs.subs_button_text': {
        'ru': 'Попробовать',
    },
    'persey-payments.static.profile_screen.title': {'ru': 'Помощь рядом'},
    'persey-payments.static.profile_screen.value': {
        'ru': 'Вы помогаете врачам',
    },
    'persey-payments.static.on_subs_dialog.title': {'en': 'Spasibo za pomosh'},
    'persey-payments.static.on_subs_dialog.text_tmpl': {
        'ru': (
            'Теперь стоимость каждой вашей поездки будет округляться '
            'в пределах $MOD$ — и разница пойдет в помощь врачам'
        ),
    },
    'persey-payments.static.on_subs_dialog.close_button_text': {
        'ru': 'Закрыть',
    },
    'persey-payments.static.main_screen.no_subs.screen_text.title': {
        'ru': 'Простой способ помогать людям',
    },
    'persey-payments.static.main_screen.no_subs.screen_text.text_tmpl': {
        'ru': 'Недлинный текст',
    },
    'persey-payments.static.main_screen.subscribed.screen_text.title': {
        'ru': 'Вы помогаете проекту «Помощь рядом»',
    },
    'persey-payments.static.main_screen.subscribed.screen_text.text_tmpl': {
        'ru': 'Ещё недлинный текст',
    },
    'tanker_override': {'ru': 'Текст подменен'},
}
TARIFF = {
    'currency.rub': {'ru': 'руб.'},
    'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
    'currency_sign.rub': {'ru': '₽'},
}


@pytest.mark.parametrize(
    'expected_resp',
    [
        pytest.param(
            'expected_resp_simple.json',
            marks=pytest.mark.translations(
                client_messages=CLIENT_MESSAGES, tariff=TARIFF,
            ),
        ),
        pytest.param(
            'expected_resp_tanker_override.json',
            marks=[
                pytest.mark.translations(
                    client_messages=CLIENT_MESSAGES, tariff=TARIFF,
                ),
                conftest.ride_subs_config(
                    callback=lambda c: c['static_response'].update(
                        {
                            '__tanker_overrides__': {
                                'persey-payments.static.menu.title': (
                                    'tanker_override'
                                ),
                            },
                        },
                    ),
                ),
            ],
        ),
        pytest.param(
            'expected_resp_no_translations.json',
            marks=pytest.mark.translations(tariff=TARIFF),
        ),
    ],
)
async def test_simple(taxi_persey_payments_web, load_json, expected_resp):
    response = await taxi_persey_payments_web.get(
        '/4.0/persey-payments/v1/charity/static',
        headers={
            'X-Yandex-UID': '123',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android',
        },
    )

    assert response.status == 200
    assert await response.json() == load_json(expected_resp)
