import pytest

from tests_card_filter import helpers

EXPERIMENT = dict(
    is_config=False,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='card_filter_passport_card_verification',
    consumers=['card_filter/passport_card_verification'],
    clauses=[
        {
            'title': '1',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)


@pytest.fixture(name='mock_passport_card_verification')
def passport_card_verify_fixture(mockserver):
    def _mock_passport_card_verification(cards_levels=None):
        @mockserver.json_handler('passport-card-verification/execute')
        def handler(request):
            return {'cards_levels': cards_levels}

        return handler

    return _mock_passport_card_verification


@pytest.fixture(name='mock_card_antifraud')
def card_antifraud_fixture(mockserver):
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


@pytest.mark.experiments3(**EXPERIMENT)
@pytest.mark.config(CARD_ANTIFRAUD_VERIFICATION_LEVELS_BLACKLIST=['unknown'])
@pytest.mark.parametrize(
    'uri', ['/v1/filteredcards', '/v1/filteredcards/legacy'],
)
@pytest.mark.parametrize(
    [
        'cardstorage_verification_level',
        'passport_verification_level',
        'card_id',
        'is_card_available',
    ],
    [
        pytest.param(
            '3ds',
            '3ds',
            'card_id',
            True,
            id=(
                'cardstorage level is not blasklisted, '
                'passport level is not blackslited, '
                'same card_id'
            ),
        ),
        pytest.param(
            '3ds',
            'unknown',
            'card_id',
            True,
            id=(
                'cardstorage level is not blasklisted, '
                'passport level is blackslited, '
                'same card_id'
            ),
        ),
        pytest.param(
            'unknown',
            '3ds',
            'card_id',
            True,
            id=(
                'cardstorage level is blasklisted, '
                'passport level is not blackslited, '
                'same card_id'
            ),
        ),
        pytest.param(
            'unknown',
            'unknown',
            'card_id',
            False,
            id=(
                'cardstorage level is blasklisted, '
                'passport level is blackslited, '
                'same card_id'
            ),
        ),
        pytest.param(
            '3ds',
            '3ds',
            'random_card_id',
            True,
            id=(
                'cardstorage level is not blasklisted, '
                'passport level is not blackslited, '
                'different card_id'
            ),
        ),
        pytest.param(
            '3ds',
            'unknown',
            'random_card_id',
            True,
            id=(
                'cardstorage level is not blasklisted, '
                'passport level is blackslited, '
                'different card_id'
            ),
        ),
        pytest.param(
            'unknown',
            '3ds',
            'random_card_id',
            False,
            id=(
                'cardstorage level is blasklisted, '
                'passport level is not blackslited, '
                'different card_id'
            ),
        ),
        pytest.param(
            'unknown',
            'unknown',
            'random_card_id',
            False,
            id=(
                'cardstorage level is blasklisted, '
                'passport level is blackslited, '
                'different card_id'
            ),
        ),
        pytest.param(
            '3ds',
            None,
            None,
            True,
            id=(
                'cardstorage level is not blasklisted, '
                'passport response is empty'
            ),
        ),
        pytest.param(
            'unknown',
            None,
            None,
            False,
            id=(
                'cardstorage level is blasklisted, '
                'passport response is empty'
            ),
        ),
    ],
)
async def test_card_availability_verification_level(
        taxi_card_filter_monitor,
        invoke_handler,
        mock_cardstorage,
        mock_card_antifraud,
        mock_passport_card_verification,
        cardstorage_verification_level,
        passport_verification_level,
        card_id,
        is_card_available,
        uri,
        taxi_card_filter,
):
    mock_cardstorage(
        [
            helpers.make_card(
                verification_details={'level': cardstorage_verification_level},
            ),
        ],
    )
    mock_card_antifraud()

    cards = {}
    if card_id is not None:
        cards = {card_id: passport_verification_level}
    mock_passport = mock_passport_card_verification(cards)

    request = {
        'yandex_uid': '111111',
        'user_id': 'user_id',
        'yandex_login_id': 'yandex_login_id',
    }
    headers = {'X-Yandex-UID': '111111', 'X-Remote-IP': '213.180.193.1'}
    await taxi_card_filter.invalidate_caches()
    response = await taxi_card_filter.post(uri, json=request, headers=headers)

    assert response.status_code == 200
    assert mock_passport.has_calls
    json_response = response.json()
    if not is_card_available and uri == '/v1/filteredcards/legacy':
        assert json_response['unverified_cards']
        assert len(json_response['unverified_cards']) == 1
        assert json_response['unverified_cards'][0]['id'] == 'card_id'
    else:
        assert json_response['available_cards']
        assert len(json_response['available_cards']) == 1
        assert json_response['available_cards'][0]['id'] == 'card_id'
        if uri == '/v1/filteredcards':
            assert (
                json_response['available_cards'][0]['available']
                == is_card_available
            )


@pytest.mark.experiments3(**EXPERIMENT)
@pytest.mark.config(CARD_ANTIFRAUD_VERIFICATION_LEVELS_BLACKLIST=['unknown'])
@pytest.mark.parametrize(
    'uri', ['/v1/filteredcards', '/v1/filteredcards/legacy'],
)
async def test_not_request_passport_without_login_id(
        taxi_card_filter_monitor,
        invoke_handler,
        mock_cardstorage,
        mock_card_antifraud,
        mock_passport_card_verification,
        uri,
        taxi_card_filter,
):
    mock_cardstorage(
        [helpers.make_card(verification_details={'level': '3ds'})],
    )
    mock_card_antifraud()
    mock_passport = mock_passport_card_verification({'card_id': '3ds'})

    request = {'yandex_uid': '111111', 'user_id': 'user_id'}
    headers = {'X-Yandex-UID': '111111', 'X-Remote-IP': '213.180.193.1'}
    await taxi_card_filter.invalidate_caches()
    response = await taxi_card_filter.post(uri, json=request, headers=headers)

    assert response.status_code == 200
    assert not mock_passport.has_calls
