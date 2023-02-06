import pytest

from tests_card_filter import helpers


@pytest.fixture(name='mock_card_antifraud')
def mock_card_antifraud_fixture(mockserver):
    def _mock_card_antifraud(
            all_payments_available=False, available_cards=None,
    ):
        @mockserver.json_handler('/card-antifraud/v1/payment/availability')
        def handler(request):
            return {
                'all_payments_available': all_payments_available,
                'available_cards': available_cards or [],
            }

        return handler

    return _mock_card_antifraud


async def test_fallback_card_antifraud(
        taxi_card_filter, statistics, mock_cardstorage, mockserver,
):
    @mockserver.json_handler('/card-antifraud/v1/payment/availability')
    def _mock_card_antifraud(request):
        return mockserver.make_response('', status=500)

    statistics.fallbacks = ['card-filter.card-antifraud']
    await taxi_card_filter.invalidate_caches()

    request = {'yandex_uid': '111111', 'user_id': 'user_id'}
    headers = {'X-Yandex-UID': '111111', 'X-Remote-IP': '213.180.193.1'}
    async with statistics.capture(taxi_card_filter) as capture:
        response = await taxi_card_filter.post(
            '/v1/filteredcards', json=request, headers=headers,
        )

    assert response.status_code == 200
    assert capture.statistics['card-filter.card-antifraud.error'] == 1
    assert 'card-filter.card-antifraud.success' not in capture.statistics


async def test_statistics_update_card_antifraud(
        taxi_card_filter, statistics, mock_cardstorage, mockserver,
):
    @mockserver.json_handler('/card-antifraud/v1/payment/availability')
    def _mock_card_antifraud(request):
        return mockserver.make_response('', status=500)

    request = {'yandex_uid': '111111', 'user_id': 'user_id'}
    headers = {'X-Yandex-UID': '111111', 'X-Remote-IP': '213.180.193.1'}
    async with statistics.capture(taxi_card_filter) as capture:
        response = await taxi_card_filter.post(
            '/v1/filteredcards', json=request, headers=headers,
        )

    assert response.status_code == 500
    assert capture.statistics['card-filter.card-antifraud.error'] == 1


async def test_statistics_429(
        taxi_card_filter, statistics, mock_cardstorage, mockserver,
):
    @mockserver.json_handler('/card-antifraud/v1/payment/availability')
    def _mock_card_antifraud(request):
        return mockserver.make_response('{}', status=429)

    request = {'yandex_uid': '111111', 'user_id': 'user_id'}
    headers = {'X-Yandex-UID': '111111', 'X-Remote-IP': '213.180.193.1'}
    async with statistics.capture(taxi_card_filter) as capture:
        response = await taxi_card_filter.post(
            '/v1/filteredcards', json=request, headers=headers,
        )

    assert response.status_code == 200
    assert capture.statistics['card-filter.card-antifraud.error.429'] == 1


@pytest.mark.parametrize(
    ['verification_level', 'card_available'],
    [
        pytest.param(
            'unknown',
            True,
            id='verification_level=unknown, no prioritized check',
            marks=pytest.mark.config(
                TRUST_VERIFICATION_LEVEL_CHECK_PRIORITIZED_CARD_CURRENCY_LIST=[],  # noqa: E501 pylint: disable=line-too-long
            ),
        ),
        pytest.param(
            '3ds',
            True,
            id='verification_level=3ds, no prioritized check',
            marks=pytest.mark.config(
                TRUST_VERIFICATION_LEVEL_CHECK_PRIORITIZED_CARD_CURRENCY_LIST=[],  # noqa: E501 pylint: disable=line-too-long
            ),
        ),
        pytest.param(
            'unknown',
            False,
            id='verification_level=unknown, prioritized check',
            marks=pytest.mark.config(
                TRUST_VERIFICATION_LEVEL_CHECK_PRIORITIZED_CARD_CURRENCY_LIST=[  # noqa: E501 pylint: disable=line-too-long
                    'RUB',
                ],
            ),
        ),
        pytest.param(
            '3ds',
            True,
            id='verification_level=3ds, prioritized check',
            marks=pytest.mark.config(
                TRUST_VERIFICATION_LEVEL_CHECK_PRIORITIZED_CARD_CURRENCY_LIST=[  # noqa: E501 pylint: disable=line-too-long
                    'RUB',
                ],
            ),
        ),
    ],
)
@pytest.mark.config(CARD_ANTIFRAUD_VERIFICATION_LEVELS_BLACKLIST=['unknown'])
async def test_prioritized_trust_verification_level_check_legacy(
        mock_cardstorage,
        mock_card_antifraud,
        taxi_card_filter,
        verification_level,
        card_available,
):
    mock_cardstorage(
        [
            helpers.make_card(
                verification_details={'level': verification_level},
                currency='RUB',
            ),
        ],
    )
    mock_card_antifraud(all_payments_available=True)

    request = {
        'yandex_uid': '111111',
        'user_id': 'user_id',
        'zone_name': 'moscow',
    }
    headers = {'X-Yandex-UID': '111111', 'X-Remote-IP': '213.180.193.1'}
    await taxi_card_filter.invalidate_caches()
    response = await taxi_card_filter.post(
        '/v1/filteredcards/legacy', json=request, headers=headers,
    )

    assert response.status_code == 200
    if card_available:
        cards = response.json()['available_cards']
    else:
        cards = response.json()['unverified_cards']

    assert len(cards) == 1
    assert cards[0]['usable'] == card_available
