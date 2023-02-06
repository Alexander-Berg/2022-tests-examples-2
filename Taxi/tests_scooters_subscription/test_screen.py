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


async def get_offer_params_check(taxi_scooters_subscription, expected):
    response = await taxi_scooters_subscription.get(
        '/scooters-subscriptions/v1/subscriptions/offer-params',
        params={'position': h.TEST_POSITION, 'screens': ['subscription']},
        headers=h.HEADERS,
    )
    assert_response(response, expected)


def mock_offers(mockserver, second_timestamp_inc=0):
    h.mock_offers(
        mockserver,
        [
            {
                'invoices': [
                    {
                        'totalPrice': {'amount': 169, 'currency': 'RUB'},
                        'timestamp': 1643592780123,
                    },
                    {
                        'totalPrice': {'amount': 169, 'currency': 'RUB'},
                        'timestamp': (1646011980123 + second_timestamp_inc),
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
            },
        ],
        language='EN',
    )


@pytest.mark.now('2022-01-31T01:33:00+00:00')
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='scooters_subscription.json')
@pytest.mark.experiments3(filename='scooters_subscription_plus.json')
@pytest.mark.experiments3(
    filename='scooters_subscription_screens-builtin.json',
)
async def test_main(taxi_scooters_subscription, mockserver):
    # Arrange
    h.mock_intervals(mockserver, [])
    mock_offers(mockserver)

    # Act
    response = await taxi_scooters_subscription.get(
        '/scooters-subscriptions/v1/subscriptions/screen/main',
        headers=h.HEADERS,
        params={'position': h.TEST_POSITION},
    )

    # Assert
    expected_options = [
        {
            'image_tag': 'scooter_icon',
            'title': uih.atext(
                [
                    uih.text('Самокаты'),
                    uih.text(
                        '\nОпция к подписке Плюс',
                        font_size=11,
                        color='#9E9B98',
                    ),
                ],
            ),
            'right': uih.atext([uih.text('169 руб. в месяц')]),
            'footer': {
                'title': uih.atext([uih.text('Все условия')]),
                'action': {'type': 'tariff', 'tariff_id': 'tid'},
            },
        },
    ]
    expected_grid = [
        [
            uih.cell(
                uih.atext(
                    [
                        uih.text('Старт 0 ₽ вместо 50 ₽'),
                        uih.text('\nПлатите только за минуты', font_size=13),
                    ],
                ),
            ),
            uih.cell(
                uih.atext(
                    [
                        uih.text('Бесплатное ожидание'),
                        uih.text('\nВ режиме поездки', font_size=13),
                    ],
                ),
            ),
        ],
        [
            uih.cell(uih.atext([uih.text('Кешбэк с Плюсом')])),
            uih.cell(uih.atext([uih.text('Кешбэк выше')])),
        ],
    ]
    assert_response(
        response,
        (
            200,
            {
                'sections': [
                    uih.section(
                        [uih.grid(expected_grid)],
                        image={'tag': 'plus_header_ru', 'height': 24},
                        title=uih.atext(
                            [
                                uih.text(
                                    'Бесплатный старт на самокатах',
                                    font_size=24,
                                ),
                            ],
                            alignment='center',
                        ),
                    ),
                    uih.section(
                        [{'type': 'options', 'options': expected_options}],
                    ),
                ],
                'subsections': [
                    uih.section(
                        [
                            {
                                'type': 'button',
                                'title': uih.atext(
                                    [uih.text('Купить за 169 руб. в месяц')],
                                ),
                                'background_color': '#FCE000',
                                'action': {
                                    'type': 'buy',
                                    'parameters': {
                                        'target': 'samokat',
                                        'productIds': [
                                            '1month.trial.plus.samokat.399',
                                        ],
                                    },
                                },
                            },
                        ],
                    ),
                ],
            },
        ),
    )


@pytest.mark.now('2022-01-31T01:33:00+00:00')
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='scooters_subscription.json')
@pytest.mark.experiments3(filename='scooters_subscription_plus.json')
@pytest.mark.experiments3(
    filename='scooters_subscription_screens-builtin.json',
)
async def test_main_wrong_period(taxi_scooters_subscription, mockserver):
    # Arrange
    h.mock_intervals(mockserver, [])
    mock_offers(mockserver, second_timestamp_inc=-24 * 60 * 60 * 1000)

    # Act
    response = await taxi_scooters_subscription.get(
        '/scooters-subscriptions/v1/subscriptions/screen/main',
        headers=h.HEADERS,
        params={'position': h.TEST_POSITION},
    )

    assert_response(response, (200, {'sections': []}))
