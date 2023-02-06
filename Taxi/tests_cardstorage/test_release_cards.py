import pytest

from tests_cardstorage import common


CARD_1_UID_123 = 'card-x2345b3e693972872b9b58946'
CARD_2_UID_123 = 'card-x2345b3e693972872b9b58947'
CARD_3_UID_456 = 'card-x717eb3e693972872b9b5a317'
CARD_4_UID_456 = 'card-x717eb3e693972872b9b5a318'


@pytest.mark.config(TVM_ENABLED=True)
@common.tvm_ticket
@pytest.mark.parametrize('tvm, code', [(False, 401), (True, 200)])
async def test_release_cards_access(tvm, code, taxi_cardstorage):
    body = {'busy_id': '123'}
    headers = {'X-Ya-Service-Ticket': common.MOCK_TICKET if tvm else ''}
    response = await taxi_cardstorage.post(
        'v1/release_cards', json=body, headers=headers,
    )
    assert response.status_code == code


@pytest.mark.parametrize(
    'body',
    [
        ({'busy_id': 'not_exists'}),
        ({'busy_id': '123'}),
        ({'busy_id': '123', 'except_card_id': 'not_exists'}),
        ({'busy_id': '123', 'except_card_id': CARD_1_UID_123}),
        ({'busy_id': '456', 'except_card_id': CARD_4_UID_456}),
        ({'busy_id': '123', 'except_yandex_uid': 'not_exists'}),
        ({'busy_id': '456', 'except_yandex_uid': '123'}),
        ({'busy_id': '123', 'except_yandex_uid': '456'}),
    ],
)
async def test_release_cards(taxi_cardstorage, mongodb, body):
    response = await taxi_cardstorage.post('v1/release_cards', json=body)
    assert response.status_code == 200
    cards = mongodb.cards.find({})
    state = ({'order_id': '123'}, {'order_id': '456'})
    item = {'order_id': body['busy_id']}
    for card in cards:
        busy_with = card['busy_with']
        if (
                card['payment_id'] == body.get('except_card_id')
                or card['owner_uid'] == body.get('except_yandex_uid')
                or item not in state
        ):
            assert busy_with == list(state)
        else:
            changed = list(state)
            changed.remove(item)
            assert busy_with == changed
