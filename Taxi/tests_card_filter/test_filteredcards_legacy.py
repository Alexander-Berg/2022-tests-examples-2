import pytest

AVAILABLE_CARDS = [
    {
        'billing_card_id': 'x717eb3e693972872b9b5a317',
        'bin': '400000',
        'bound': True,
        'busy': False,
        'busy_with': [],
        'card_id': 'card-x717eb3e693972872b9b5a317',
        'currency': 'RUB',
        'ebin_tags': [],
        'expiration_month': 5,
        'expiration_year': 2022,
        'from_db': False,
        'number': '400000****1139',
        'owner': '789',
        'permanent_card_id': 'card-x717eb3e693972872b9b5a317',
        'possible_moneyless': False,
        'region_id': '225',
        'regions_checked': [],
        'system': 'VISA',
        'unverified': False,
        'valid': True,
    },
]


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
            '/v1/filteredcards/legacy', json=request, headers=headers,
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
            '/v1/filteredcards/legacy', json=request, headers=headers,
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
            '/v1/filteredcards/legacy', json=request, headers=headers,
        )

    assert response.status_code == 200
    assert capture.statistics['card-filter.card-antifraud.error.429'] == 1


@pytest.fixture(name='mock_card_antifraud')
def card_antifraud_fixture(mockserver):
    def _mock_card_antifraud(available_cards):
        @mockserver.json_handler('/card-antifraud/v1/payment/availability')
        def handler(request):
            return {
                'all_payments_available': True,
                'available_cards': available_cards,
            }

        return handler

    return _mock_card_antifraud


@pytest.mark.experiments3(
    is_config=False,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='card_filter_no_expiration_time',
    consumers=['card_filter/card_with_no_expiration_time'],
    clauses=[
        {
            'title': '1',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.parametrize(
    'source,is_expiration_time_exist', [('api-proxy', False), (None, True)],
)
async def test_cards_with_bin(
        taxi_card_filter,
        mock_card_antifraud,
        mock_cardstorage,
        source,
        is_expiration_time_exist,
):
    mock_cardstorage(AVAILABLE_CARDS)
    mock_card_antifraud(AVAILABLE_CARDS)

    request = {'yandex_uid': '111111', 'user_id': 'user_id', 'source': source}
    headers = {'X-Yandex-UID': '111111', 'X-Remote-IP': '213.180.193.1'}

    response = await taxi_card_filter.post(
        '/v1/filteredcards/legacy', json=request, headers=headers,
    )

    assert response.status_code == 200
    available_cards = response.json()['available_cards']
    assert (
        available_cards[0].get('expiration_time') is not None
    ) == is_expiration_time_exist


async def test_cardstorage_request(
        taxi_card_filter, mock_card_antifraud, mock_cardstorage,
):
    expected_cardstorage_request = {
        'cache_preferred': False,
        'currency': 'RUB',
        'mark_unavailable_bindings': True,
        'service_type': 'card',
        'show_unbound': False,
        'show_unverified': False,
        'yandex_uid': '111111',
    }
    mock_cardstorage(AVAILABLE_CARDS, expected_cardstorage_request)
    mock_card_antifraud(AVAILABLE_CARDS)

    request = {
        'yandex_uid': '111111',
        'user_id': 'user_id',
        'source': 'api-proxy',
        'zone_name': 'moscow',
    }
    headers = {'X-Yandex-UID': '111111', 'X-Remote-IP': '213.180.193.1'}

    response = await taxi_card_filter.post(
        '/v1/filteredcards/legacy', json=request, headers=headers,
    )

    assert response.status_code == 200
