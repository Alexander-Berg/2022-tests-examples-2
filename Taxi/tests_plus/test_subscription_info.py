import pytest

DEFAULT_FEATURES = {
    'action': {'text': 'subscriptions.plus.action'},
    'features': [
        {
            'icon': 'drive_icon_image_tag',
            'subtitle': 'subscriptions.feature.subtitle.drive',
            'title': 'subscriptions.feature.title.drive',
            'type': 'drive',
        },
    ],
    'price': {'currency': 'RUB', 'value': '169'},
    'subtitle': 'subscriptions.plus.subtitle',
    'title': 'subscriptions.plus.title',
    'purchase_info': {
        'action': 'subscriptions.plus.purchase_info.action_text',
        'title': 'subscriptions.plus.purchase_info.not_trial.title',
    },
}

TARIFF = {
    'currency_with_sign.default': {'en': '$VALUE$ $SIGN$$CURRENCY$'},
    'currency_with_sign.rub': {'en': '$VALUE$ $ZNAK$$CURRENCY$'},
    'currency.rub': {'en': 'rub.'},
    'currency_sign.rub': {'en': 'R'},
}


@pytest.mark.config(PLUS_SERVICE_ENABLED=False)
@pytest.mark.config(
    PLUS_ALLOWED_SUBSCRIPTIONS_BY_COUNTRIES={'ru': ['plus_russia']},
)
async def test_subscription_not_enabled(web_plus):
    result = await web_plus.subscription_info.request(
        subscription_id='plus_russia',
    ).perform()

    assert result.status_code == 429


@pytest.mark.config(PLUS_ALLOWED_SUBSCRIPTIONS_BY_COUNTRIES={'ru': []})
async def test_subscription_not_available(web_plus):
    result = await web_plus.subscription_info.request(
        subscription_id='plus_russia',
    ).perform()

    assert result.status_code == 409


@pytest.mark.config(
    PLUS_ALLOWED_SUBSCRIPTIONS_BY_COUNTRIES={'ru': ['plus_russia']},
    PLUS_SUBSCRIPTION_FEATURES={},
)
async def test_subscription_not_configured(web_plus):
    result = await web_plus.subscription_info.request(
        subscription_id='plus_russia',
    ).perform()

    assert result.status_code == 409


@pytest.mark.config(
    PLUS_ALLOWED_SUBSCRIPTIONS_BY_COUNTRIES={'ru': ['plus_russia']},
)
@pytest.mark.config(
    PLUS_SUBSCRIPTION_FEATURES={'plus_russia': DEFAULT_FEATURES},
)
@pytest.mark.translations(
    tariff=TARIFF,
    client_messages={
        'subscriptions.plus.action': {'en': 'Buy plus'},
        'subscriptions.feature.subtitle.drive': {'en': 'Yandex.Drive'},
        'subscriptions.feature.title.drive': {'en': 'Discount <b>10%</b>'},
        'subscriptions.plus.subtitle': {'en': '1 day free, %(value)s after'},
        'subscriptions.plus.title': {'en': 'What is subscription?'},
    },
)
async def test_subscription_ok(web_plus):
    result = await web_plus.subscription_info.request(
        subscription_id='plus_russia',
    ).perform()

    assert result.status_code == 200
    content = result.json()

    assert content == {
        'subscription_id': 'plus_russia',
        'title': 'What is subscription?',
        'subtitle': '1 day free, 169 $ZNAK$$CURRENCY$ after',
        'currency_rules': {
            'code': 'RUB',
            'sign': 'R',
            'template': '$VALUE$ $ZNAK$$CURRENCY$',
            'text': 'rub.',
        },
        'features': [
            {
                'type': 'drive',
                'title': 'Discount <b>10%</b>',
                'subtitle': 'Yandex.Drive',
                'icon': 'drive_icon_image_tag',
            },
        ],
        'action': {'text': 'Buy plus'},
    }


@pytest.mark.config(
    PLUS_ALLOWED_SUBSCRIPTIONS_BY_COUNTRIES={'ru': ['ya_plus_trial_rus']},
)
@pytest.mark.config(
    PLUS_SUBSCRIPTION_FEATURES={'ya_plus_trial_rus': DEFAULT_FEATURES},
)
@pytest.mark.translations(
    tariff=TARIFF,
    client_messages={
        'subscriptions.plus.action': {'en': 'Buy plus'},
        'subscriptions.feature.subtitle.drive': {'en': 'Yandex.Drive'},
        'subscriptions.feature.title.drive': {'en': 'Discount <b>10%</b>'},
        'subscriptions.plus.subtitle': {'en': '1 day free, %(value)s after'},
        'subscriptions.plus.title': {'en': 'What is subscription?'},
    },
)
async def test_trial_subscription_ok(web_plus):
    result = await web_plus.subscription_info.request(
        subscription_id='ya_plus_trial_rus',
    ).perform()

    assert result.status_code == 200
