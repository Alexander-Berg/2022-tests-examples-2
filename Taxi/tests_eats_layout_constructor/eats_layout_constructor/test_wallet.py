import pytest

from . import configs
from . import experiments
from . import utils

BASIC_COLOR = [
    {'theme': 'light', 'value': '#000000'},
    {'theme': 'dark', 'value': '#ffffff'},
]

CURRENCY_RULES = pytest.mark.config(
    CURRENCY_FORMATTING_RULES={'RUB': {'__default__': 2}},
    CURRENCY_ROUNDING_RULES={'__default__': {'__default__': 0.1}},
)


LAYOUT_WITH_WALLET = pytest.mark.layout(
    slug='layout_1',
    widgets=[
        utils.Widget(
            name='wallet',
            type='wallet',
            meta={
                'wallet': {
                    'url': 'http://wallet-example.net',
                    'icon': {
                        'uri': 'http://wallet-example.net/wallet.png',
                        'color': BASIC_COLOR,
                    },
                    'balance_color': BASIC_COLOR,
                    'total_color': BASIC_COLOR,
                    'description_color': BASIC_COLOR,
                },
                'qr': {
                    'url': 'http://wallet-example.net/where-qr-go',
                    'icon': {
                        'uri': 'http://wallet-example.net/qr.png',
                        'color': BASIC_COLOR,
                    },
                    'text': {
                        'key': 'wallet.qr.text',
                        'default_text': 'QR-code',
                        'color': BASIC_COLOR,
                    },
                    'background': [],
                },
            },
        ),
    ],
)


TRANSLATIONS = pytest.mark.translations(
    **{
        'eats-layout-constructor': {
            'widgets.wallet.qr.text': {'ru': 'QR-код'},
            'widgets.wallet.unlimited': {'ru': 'Безлимит'},
            'widgets.wallet.description.month': {'ru': 'Лимит на месяц'},
        },
        'tariff': {
            'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        },
    },
)


@TRANSLATIONS
@LAYOUT_WITH_WALLET
@CURRENCY_RULES
@configs.keep_empty_layout()
@configs.layout_experiment_name()
@experiments.layout('layout_1')
async def test_wallet(layout_constructor, mockserver):
    @mockserver.json_handler('/corp-users/v1/users-limits/eats/fetch')
    def user_limits(request):
        assert (
            request.headers['x-yataxi-user']
            == 'personal_phone_id=hello_taxi_user'
        )

        return {
            'users': [
                {
                    'id': '4550652957e84174b2ac47e4b49dba80',
                    'client_id': 'beed2277ae71428db1029c07394e542c',
                    'client_name': 'Test Client 1',
                    'limits': [
                        {
                            'limit_id': '794e6c05f439497989dcce6b2fcb30c4',
                            'limits': {
                                'orders_cost': {
                                    'currency': 'RUB',
                                    'currency_sign': '₽',
                                    'balance': '1622.4300',
                                    'value': '3600',
                                    'period': 'month',
                                },
                            },
                        },
                    ],
                },
                {
                    'id': '5e2b6345e4af44939121c9f286962693',
                    'client_id': '8a50ffc8c43f41df81f4d93b54bc36e1',
                    'client_name': 'Test Client 2',
                    'limits': [
                        {
                            'limit_id': '1bee3212e2544e45b582191dea27ead2',
                            'limits': {
                                'orders_cost': {
                                    'currency': 'RUB',
                                    'currency_sign': '₽',
                                    'balance': '11',
                                    'value': '11',
                                    'period': 'month',
                                },
                            },
                        },
                    ],
                },
                {
                    'id': '0017aae4b21d435cb9ea3b1d73447d8a',
                    'client_id': 'abdf92df57c44091bb4424c82c0ef86b',
                    'client_name': 'Test Client 3',
                    'limits': [
                        {
                            'limit_id': '2a66a3cf155b49ec9805201ad82e583d',
                            'limits': {},
                        },
                    ],
                },
            ],
        }

    response = await layout_constructor.post(
        headers={'x-yataxi-user': 'personal_phone_id=hello_taxi_user'},
    )

    assert user_limits.times_called == 1
    assert response.status_code == 200
    data = response.json()

    layout = [item['id'] for item in data['layout']]
    assert layout == ['1_wallet']

    assert len(data['data']['wallets']) == 1

    wallet = data['data']['wallets'][0]

    assert wallet == {
        'id': '1_wallet',
        'payload': {
            'button': {
                'background': [],
                'icon': {
                    'color': BASIC_COLOR,
                    'uri': 'http://wallet-example.net/qr.png',
                },
                'text': {'color': BASIC_COLOR, 'text': 'QR-code'},
                'url': 'http://wallet-example.net/where-qr-go',
            },
            'wallet': {
                'balance': {
                    'color': BASIC_COLOR,
                    'price_formatted': '1622.4$SIGN$$CURRENCY$',
                },
                'description': {
                    'color': BASIC_COLOR,
                    'text': 'Лимит на месяц',
                },
                'icon': {
                    'color': BASIC_COLOR,
                    'uri': 'http://wallet-example.net/wallet.png',
                },
                'total': {
                    'color': BASIC_COLOR,
                    'price_formatted': ' / 3600$SIGN$$CURRENCY$',
                },
                'url': 'http://wallet-example.net',
            },
            'currency': {
                'code': 'RUB',
                'sign': '₽',
                'text': 'руб.',
                'template': '$VALUE$\xa0$SIGN$$CURRENCY$',
            },
        },
        'template_name': 'wallet_template',
    }


@TRANSLATIONS
@LAYOUT_WITH_WALLET
@CURRENCY_RULES
@configs.keep_empty_layout()
@configs.layout_experiment_name()
@experiments.layout('layout_1')
async def test_wallet_unlimited(layout_constructor, mockserver):
    @mockserver.json_handler('/corp-users/v1/users-limits/eats/fetch')
    def user_limits(request):
        assert request.headers['x-yataxi-user']

        return {
            'users': [
                {
                    'id': '0017aae4b21d435cb9ea3b1d73447d8a',
                    'client_id': 'abdf92df57c44091bb4424c82c0ef86b',
                    'client_name': 'Test Client 3',
                    'limits': [
                        {
                            'limit_id': '2a66a3cf155b49ec9805201ad82e583d',
                            'limits': {},
                        },
                    ],
                },
            ],
        }

    response = await layout_constructor.post(
        headers={'x-yataxi-user': 'personal_phone_id=hello_taxi_user'},
    )

    assert user_limits.times_called == 1
    assert response.status_code == 200
    data = response.json()

    layout = [item['id'] for item in data['layout']]
    assert layout == ['1_wallet']

    assert len(data['data']['wallets']) == 1

    wallet = data['data']['wallets'][0]

    assert wallet == {
        'id': '1_wallet',
        'payload': {
            'button': {
                'background': [],
                'icon': {
                    'color': BASIC_COLOR,
                    'uri': 'http://wallet-example.net/qr.png',
                },
                'text': {'color': BASIC_COLOR, 'text': 'QR-code'},
                'url': 'http://wallet-example.net/where-qr-go',
            },
            'wallet': {
                'balance': {
                    'color': BASIC_COLOR,
                    'price_formatted': 'Безлимит',
                },
                'icon': {
                    'color': BASIC_COLOR,
                    'uri': 'http://wallet-example.net/wallet.png',
                },
                'url': 'http://wallet-example.net',
            },
            'currency': {
                'code': 'RUB',
                'sign': '₽',
                'text': 'руб.',
                'template': '$VALUE$\xa0$SIGN$$CURRENCY$',
            },
        },
        'template_name': 'wallet_template',
    }
