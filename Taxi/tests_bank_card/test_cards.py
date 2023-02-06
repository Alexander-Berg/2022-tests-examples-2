import pytest

from tests_bank_card import common


def make_expiration_str(month, year):
    return '{:02d}/{:2d}'.format(month, year % 100)


def java_token_to_client_token(token):
    token_id = token['reference_id']
    token.pop('reference_id')
    token['token'] = ''
    token['token_id'] = token_id
    return token


def check_default_cards(core_card_mock, response):
    assert response.status_code == 200
    assert len(response.json()['cards']) == len(core_card_mock.cards_list)
    for i in range(0, len(core_card_mock.cards_list)):
        original_card = core_card_mock.cards_list[i]
        response_card = response.json()['cards'][i]

        expected_tokens = []
        for token in original_card['tokens']:
            if token['type'] != 'UNDEFINED':
                expected_tokens.append(java_token_to_client_token(token))

        assert response_card == {
            'card_id': original_card['public_card_id'],
            'last_pan_digits': original_card['last_pan_digits'],
            'expiration_date': make_expiration_str(
                original_card['exp_month'], original_card['exp_year'],
            ),
            'status': original_card['status'],
            'payment_system': original_card['payment_system'],
            'tokens': expected_tokens,
        }


async def test_get_all_cards(taxi_bank_card, mockserver, core_card_mock):
    response = await taxi_bank_card.post(
        'v1/card/v1/get_card_public_info',
        headers=common.default_headers(),
        json={},
    )

    check_default_cards(core_card_mock, response)


@pytest.mark.parametrize('card_idx', [0, 1])
async def test_get_all_cards_filtered(
        taxi_bank_card, mockserver, core_card_mock, card_idx,
):
    original_card = core_card_mock.cards_list[card_idx]
    core_card_mock.set_card_info(original_card)

    response = await taxi_bank_card.post(
        'v1/card/v1/get_card_public_info',
        headers=common.default_headers(),
        json={'card_id': original_card['public_card_id']},
    )

    assert response.status_code == 200
    assert len(response.json()['cards']) == 1

    expected_tokens = []
    for token in original_card['tokens']:
        if token['type'] != 'UNDEFINED':
            expected_tokens.append(java_token_to_client_token(token))

    assert response.json()['cards'][0] == {
        'card_id': original_card['public_card_id'],
        'last_pan_digits': original_card['last_pan_digits'],
        'payment_system': original_card['payment_system'],
        'status': original_card['status'],
        'expiration_date': make_expiration_str(
            original_card['exp_month'], original_card['exp_year'],
        ),
        'tokens': expected_tokens,
    }


async def test_get_all_cards_none(taxi_bank_card, mockserver, core_card_mock):
    core_card_mock.set_cards_list([])

    response = await taxi_bank_card.post(
        'v1/card/v1/get_card_public_info',
        headers=common.default_headers(),
        json={},
    )

    assert response.status_code == 200
    assert response.json()['cards'] == []


async def test_get_all_cards_filtered_not_found(
        taxi_bank_card, mockserver, core_card_mock,
):
    core_card_mock.set_http_status_code(404)
    core_card_mock.set_card_info({'code': '404', 'message': 'some_text'})

    response = await taxi_bank_card.post(
        'v1/card/v1/get_card_public_info',
        headers=common.default_headers(),
        json={'card_id': '1'},
    )

    assert response.status_code == 200
    assert response.json()['cards'] == []


@pytest.mark.parametrize('status', ['ACTIVE', 'FROZEN', 'DELETED'])
async def test_get_card_list_no_reason_and_link_non_blocked_statuses(
        taxi_bank_card, mockserver, core_card_mock, status,
):
    card = {
        'public_card_id': '2',
        'cardholder_name': '',
        'bin': '321321',
        'last_pan_digits': '0987',
        'exp_month': 12,
        'exp_year': 2093,
        'payment_system': 'MIR',
        'status': status,
        'tokens': [],
    }
    core_card_mock.set_card_info(card)

    headers = common.default_headers()
    headers['X-Request-Language'] = 'ru'

    response = await taxi_bank_card.post(
        'v1/card/v1/get_card_public_info',
        headers=headers,
        json={'card_id': card['public_card_id']},
    )

    assert response.status_code == 200
    assert 'block_reason' not in response.json()
    assert 'support_url' not in response.json()


@pytest.mark.parametrize(
    'locale,localized_text',
    [
        ('ru', 'Карта заблокирована'),
        ('en', 'Card is blocked'),
        ('ch', 'Карта заблокирована'),
    ],
)
@pytest.mark.config(BANK_SUPPORT_URL={'support_url': 'some_support_url'})
async def test_get_card_list_blocked_reason_locale(
        taxi_bank_card, mockserver, core_card_mock, locale, localized_text,
):
    card = {
        'public_card_id': '2',
        'cardholder_name': '',
        'bin': '321321',
        'last_pan_digits': '0987',
        'exp_month': 12,
        'exp_year': 2093,
        'payment_system': 'MIR',
        'status': 'BLOCKED',
        'tokens': [],
    }
    core_card_mock.set_card_info(card)

    headers = common.default_headers()
    headers['X-Request-Language'] = locale

    response = await taxi_bank_card.post(
        'v1/card/v1/get_card_public_info',
        headers=headers,
        json={'card_id': card['public_card_id']},
    )

    assert response.status_code == 200
    assert len(response.json()['cards']) == 1
    assert response.json()['cards'][0] == {
        'card_id': '2',
        'expiration_date': '12/93',
        'last_pan_digits': '0987',
        'payment_system': 'MIR',
        'status': 'BLOCKED',
        'block_reason': localized_text,
        'support_url': 'some_support_url',
        'tokens': [],
    }


async def test_cards_info_agreement_id_and_card_id(
        taxi_bank_card, mockserver, core_card_mock,
):
    response = await taxi_bank_card.post(
        'v1/card/v1/get_card_public_info',
        headers=common.default_headers(),
        json={'card_id': '123', 'agreement_id': '321'},
    )
    assert response.status_code == 400
    assert core_card_mock.list_by_agreement_handler.times_called == 0
    assert core_card_mock.list_handler.times_called == 0
    assert core_card_mock.get_by_id_handler.times_called == 0


async def test_cards_info_agreement_not_found(
        taxi_bank_card, mockserver, core_card_mock,
):
    core_card_mock.set_http_status_code(404)
    core_card_mock.set_cards_list_response(
        {'code': '404', 'message': 'some_text'},
    )

    response = await taxi_bank_card.post(
        'v1/card/v1/get_card_public_info',
        headers=common.default_headers(),
        json={'agreement_id': '321'},
    )
    assert response.status_code == 200
    assert response.json()['cards'] == []
    assert core_card_mock.list_by_agreement_handler.times_called == 1


async def test_cards_info_agreement_bad_request(
        taxi_bank_card, mockserver, core_card_mock,
):
    core_card_mock.set_http_status_code(400)
    core_card_mock.set_cards_list_response(
        {'code': '400', 'message': 'some_text'},
    )

    response = await taxi_bank_card.post(
        'v1/card/v1/get_card_public_info',
        headers=common.default_headers(),
        json={'agreement_id': '321'},
    )
    assert response.status_code == 500
    assert core_card_mock.list_by_agreement_handler.times_called == 1


async def test_cards_info_agreement_ok(
        taxi_bank_card, mockserver, core_card_mock,
):
    response = await taxi_bank_card.post(
        'v1/card/v1/get_card_public_info',
        headers=common.default_headers(),
        json={'agreement_id': '321'},
    )
    check_default_cards(core_card_mock, response)
    assert core_card_mock.list_by_agreement_handler.times_called == 1


@pytest.mark.parametrize('http_status', [200, 202, 400, 404, 409, 500])
async def test_set_status_card_proxy(
        taxi_bank_card, mockserver, core_card_mock, http_status,
):
    core_card_mock.set_http_status_code(http_status)

    if http_status in [400, 404, 409]:
        core_card_mock.set_status_set_response(
            {'code': 'some_code', 'message': 'msg'},
        )

    headers = common.default_headers()
    headers['X-Idempotency-Token'] = '7ED58D18-63AA-4838-9EC7-8DFBF9E9D6BB'

    response = await taxi_bank_card.post(
        'v1/card/v1/set_status',
        headers=headers,
        json={'card_id': 'some_card_id', 'status': 'ACTIVE'},
    )

    expected_code = http_status
    if http_status == 202:
        expected_code = 500

    assert response.status_code == expected_code


def get_card_with_payment_system(payment_system):
    card = {
        'public_card_id': '2',
        'cardholder_name': '',
        'bin': '321321',
        'last_pan_digits': '0987',
        'exp_month': 12,
        'exp_year': 2093,
        'payment_system': '---',
        'status': 'ACTIVE',
        'tokens': [],
    }
    card['payment_system'] = payment_system
    return card


def generate_cards_lists(payment_systems_of_cards):
    cards_list = []
    for payment_system in payment_systems_of_cards:
        card = get_card_with_payment_system(payment_system)
        cards_list.append(card)
    return cards_list


@pytest.mark.config(
    BANK_AVAILABLE_PAYMENT_SYSTEMS={'all_payment_systems_are_available': True},
)
async def test_get_all_cards_without_unavailable_payment_systems(
        taxi_bank_card, mockserver, core_card_mock,
):
    response = await taxi_bank_card.post(
        'v1/card/v1/get_card_public_info',
        headers=common.default_headers(),
        json={},
    )

    check_default_cards(core_card_mock, response)


@pytest.mark.parametrize(
    'payment_systems_of_cards',
    [['VISA', 'AMERICAN_EXPRESS', 'VISA', 'MIR', 'VISA']],
)
@pytest.mark.parametrize(
    'available_payment_systems, result_payment_systems',
    [
        (['MIR'], ['MIR']),
        (['MIR', 'VISA'], ['VISA', 'VISA', 'MIR', 'VISA']),
        (['MASTERCARD'], []),
    ],
)
async def test_get_all_cards_of_several_available_payment_system(
        taxi_bank_card,
        mockserver,
        core_card_mock,
        taxi_config,
        payment_systems_of_cards,
        available_payment_systems,
        result_payment_systems,
):
    taxi_config.set_values(
        {
            'BANK_AVAILABLE_PAYMENT_SYSTEMS': {
                'payment_systems_list': available_payment_systems,
                'all_payment_systems_are_available': False,
            },
        },
    )
    cards_list = generate_cards_lists(payment_systems_of_cards)
    expected_cards_list = generate_cards_lists(result_payment_systems)

    core_card_mock.set_cards_list(cards_list)
    response = await taxi_bank_card.post(
        'v1/card/v1/get_card_public_info',
        headers=common.default_headers(),
        json={},
    )

    core_card_mock.set_cards_list(expected_cards_list)
    check_default_cards(core_card_mock, response)
