import pytest


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.experiments3(filename='exp3_eats_plus_badge_for_catalog.json')
async def test_non_authorized_places_list(
        taxi_eats_plus, passport_blackbox, eats_order_stats, plus_wallet,
):
    eats_order_stats()
    passport_blackbox()
    plus_wallet({'RUB': 123321})

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/presentation/cashback/places-list',
        json={'yandex_uid': '', 'place_ids': [1, 2]},
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'cashback': [
            {
                'place_id': 1,
                'cashback': 0,
                'badge': {
                    'color': [
                        {'theme': 'light', 'value': '#ffffff'},
                        {'theme': 'dark', 'value': '#ffffff'},
                    ],
                    'details_form': {
                        'background': {'styles': {'rainbow': True}},
                        'button': {
                            'deeplink': 'eda.yandex://plus/home',
                            'title': 'Подключить Плюс',
                        },
                        'description': (
                            'Подключите Яндекс Плюс, чтобы получать до 7% '
                            'кешбека за каждый заказ и обменивать баллы '
                            'на покупки.'
                        ),
                        'image_url': (
                            'https://eda.yandex/images/2794391'
                            '/f624435a72ee14b97d5809e89dd6d9e2.png'
                        ),
                        'title': 'Выгоднее с Плюсом',
                    },
                    'styles': {'rainbow': True},
                    'text': 'Баллы Плюса за 1-й заказ',
                },
            },
        ],
    }
