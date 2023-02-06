import pytest

from tests_cardstorage import common

CARD_X234 = 'card-x2345b3e693972872b9b58946'
CARD_X717 = 'card-x717eb3e693972872b9b5a317'
CARD_X4F5 = 'card-x4f5f1d73c0ce69d0ee16ccd2'
CARD_X002 = 'card-x000000000000000000000002'
CARD_X003 = 'card-x000000000000000000000003'
BUSY_ID = '123e4567e89b12d3a456426655440000'
NUMBER = '589000****9999'
NUMBER2 = '427901****0778'
NUMBER3 = '589000****0001'
NUMBER4 = '589000****0002'


@pytest.mark.config(TVM_ENABLED=True)
@common.tvm_ticket
@pytest.mark.parametrize('tvm, code', [(False, 401), (True, 200)])
async def test_get_cards_access(tvm, code, taxi_cardstorage):
    body = {'busy_id': '1234'}
    headers = {'X-Ya-Service-Ticket': common.MOCK_TICKET if tvm else ''}
    response = await taxi_cardstorage.post(
        'v1/cards', json=body, headers=headers,
    )
    assert response.status_code == code


async def test_empty_body(taxi_cardstorage):
    response = await taxi_cardstorage.post('v1/cards', json={})
    assert response.status_code == 400


@pytest.mark.parametrize(
    'body,found',
    [
        ({'number': 'not_found'}, False),
        ({'number': NUMBER}, True),
        ({'busy_id': 'not_found'}, False),
        ({'busy_id': BUSY_ID}, True),
        ({'number': NUMBER, 'busy_id': BUSY_ID}, 200),
    ],
)
async def test_get_card(taxi_cardstorage, mongodb, body, found):
    response = await taxi_cardstorage.post('v1/cards', json=body)
    assert response.status_code == 200
    if not found:
        assert response.json() == {'cards': []}
    else:
        db_cards = {CARD_X234, CARD_X717}
        for card in response.json()['cards']:
            db_cards.remove(card['card_id'])
            assert card['number'] == NUMBER
            assert card['busy']
            assert card['busy_with'] == [{'order_id': BUSY_ID}]
            assert card['from_db']
        assert not db_cards


@pytest.mark.parametrize(
    'body,expected_card_id,exp_value,',
    [
        ({'number': '313370****9999'}, 'card-x313373e693972872b9b58946', True),
        ({'number': '313370****9999'}, 'card-x1337', False),
    ],
)
async def test_full_card_id_experiment(
        taxi_cardstorage,
        experiments3,
        mongodb,
        body,
        expected_card_id,
        exp_value,
):
    experiments3.add_experiment(
        name='enable_long_card_id',
        consumers=['cardstorage/paymentmethods'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        default_value={'enabled': exp_value},
    )
    response = await taxi_cardstorage.post('v1/cards', json=body)
    assert response.status_code == 200
    content = response.json()
    assert len(content['cards']) == 1
    assert content['cards'][0]['card_id'] == expected_card_id


@pytest.mark.parametrize(
    'body,expected_cards',
    [
        (
            {'number': NUMBER4},
            [
                {
                    'card_id': CARD_X002,
                    'from_db': True,
                    'ebin_tags': ['tag1', 'tag2'],
                },
                {'card_id': CARD_X003, 'from_db': True, 'ebin_tags': []},
            ],
        ),
    ],
)
async def test_get_ebin_tags(taxi_cardstorage, mongodb, body, expected_cards):
    response = await taxi_cardstorage.post(
        'v1/cards', json={'number': NUMBER4},
    )
    assert response.status_code == 200
    cards = sorted(response.json()['cards'], key=lambda card: card['card_id'])
    for card, expected_card in zip(cards, expected_cards):
        assert card['number'] == NUMBER4
        for key in expected_card:
            assert card[key] == expected_card[key]
    assert len(cards) == len(expected_cards)


async def test_cards_with_the_same_id(taxi_cardstorage):
    response = await taxi_cardstorage.post(
        'v1/cards', json={'number': NUMBER2},
    )
    assert response.status_code == 200
    cards = response.json()['cards']
    assert len(cards) == 2
    owners = {'123', '456'}
    for card in cards:
        assert card['number'] == NUMBER2
        assert card['card_id'] == CARD_X4F5
        owners.remove(card['owner'])
    assert not owners


@pytest.mark.parametrize(
    'number,login_id,expected_details_path',
    [
        # No verification levels in this card, expect no details in response
        (NUMBER2, 'login-id', None),
        # Card has verification levels but not for this login-id,
        # expect no details in response
        (NUMBER3, 'absent-login-id', None),
        # Card has full details for this login, expect full details in response
        (
            NUMBER3,
            'login-id-with-full-info',
            'login_id_with_full_info_details.json',
        ),
        # Card has partial details for this login, expect partial details
        # in response
        (
            NUMBER3,
            'login-id-with-partial-info',
            'login_id_with_partial_info_details.json',
        ),
        # No login-id provided, expect no details in response
        (NUMBER3, None, None),
    ],
)
async def test_verification_details(
        taxi_cardstorage,
        mongodb,
        load_json,
        number,
        login_id,
        expected_details_path,
):
    expected_details = None
    if expected_details_path is not None:
        expected_details = load_json(expected_details_path)
    body = {'number': number}
    if login_id is not None:
        body['yandex_login_id'] = login_id
    response = await taxi_cardstorage.post('v1/cards', json=body)
    assert response.status_code == 200
    for card in response.json()['cards']:
        assert card['number'] == number
        assert card['from_db']
        assert card.get('verification_details') == expected_details
