import pytest

from tests_cardstorage import common


ORDER_ID492 = 'Х492НК77'
ORDER_ID503 = 'Х503НК99'
CARD_X234 = 'card-x2345b3e693972872b9b58946'
CARD_X717 = 'card-x717eb3e693972872b9b5a317'
CARD_X987 = 'card-x9876b3e693972872b9b50087'


@pytest.mark.config(TVM_ENABLED=True)
@common.tvm_ticket
@pytest.mark.parametrize('tvm, code', [(False, 401), (True, 200)])
async def test_update_card_access(tvm, code, taxi_cardstorage):
    body = {'yandex_uid': '123', 'card_id': CARD_X234}
    headers = {'X-Ya-Service-Ticket': common.MOCK_TICKET if tvm else ''}
    response = await taxi_cardstorage.post(
        'v1/update_card', json=body, headers=headers,
    )
    assert response.status_code == code


async def test_update_card_regions(taxi_cardstorage, mongodb):
    body = {
        'yandex_uid': '123',
        'card_id': CARD_X234,
        'regions_checked': ['336', '447'],
    }
    response = await taxi_cardstorage.post('v1/update_card', json=body)
    assert response.status_code == 200
    record = mongodb.cards.find_one({'owner_uid': '123'})
    assert len(record['regions_checked']) == 3
    assert {'id': 225} in record['regions_checked']
    assert {'id': 336} in record['regions_checked']
    assert {'id': 447} in record['regions_checked']

    # Idempotency check
    response = await taxi_cardstorage.post('v1/update_card', json=body)
    assert response.status_code == 200
    record = mongodb.cards.find_one({'owner_uid': '123'})
    assert len(record['regions_checked']) == 3

    body = {
        'yandex_uid': '123',
        'card_id': CARD_X234,
        'regions_to_delete': ['336', '447'],
    }
    response = await taxi_cardstorage.post('v1/update_card', json=body)
    assert response.status_code == 200
    record = mongodb.cards.find_one({'owner_uid': '123'})
    assert len(record['regions_checked']) == 1
    assert {'id': 225} in record['regions_checked']
    assert {'id': 336} not in record['regions_checked']
    assert {'id': 447} not in record['regions_checked']

    response = await taxi_cardstorage.post('v1/update_card', json=body)
    assert response.status_code == 200
    record = mongodb.cards.find_one({'owner_uid': '123'})
    assert len(record['regions_checked']) == 1

    response = await taxi_cardstorage.post(
        'v1/update_card',
        json={
            'yandex_uid': '123',
            'card_id': CARD_X234,
            'regions_checked': ['not_a_number'],
        },
    )
    assert response.status_code == 400


async def test_update_card_valid(taxi_cardstorage, mongodb):
    body = {'yandex_uid': '123', 'card_id': CARD_X234, 'valid': False}
    response = await taxi_cardstorage.post('v1/update_card', json=body)
    assert response.status_code == 200
    record = mongodb.cards.find_one({'owner_uid': '123'})
    assert not record['valid']


async def test_update_card_busy(taxi_cardstorage, mongodb):
    body = {
        'yandex_uid': '123',
        'card_id': CARD_X234,
        'mark_busy': ORDER_ID492,
    }
    response = await taxi_cardstorage.post('v1/update_card', json=body)
    assert response.status_code == 200
    record = mongodb.cards.find_one({'owner_uid': '123'})
    assert record['busy_with'] == [{'order_id': ORDER_ID492}]

    body = {
        'yandex_uid': '123',
        'card_id': CARD_X234,
        'mark_busy': ORDER_ID503,
    }
    response = await taxi_cardstorage.post('v1/update_card', json=body)
    assert response.status_code == 200
    record = mongodb.cards.find_one({'owner_uid': '123'})
    assert len(record['busy_with']) == 2
    assert {'order_id': ORDER_ID492} in record['busy_with']
    assert {'order_id': ORDER_ID503} in record['busy_with']

    body = {
        'yandex_uid': '123',
        'card_id': CARD_X234,
        'unmark_busy': ORDER_ID492,
    }
    response = await taxi_cardstorage.post('v1/update_card', json=body)
    assert response.status_code == 200
    record = mongodb.cards.find_one({'owner_uid': '123'})
    assert record['busy_with'] == [{'order_id': ORDER_ID503}]


async def test_update_card_complex(taxi_cardstorage, mongodb):
    body = {
        'yandex_uid': '123',
        'card_id': CARD_X234,
        'regions_checked': ['336', '447'],
        'mark_busy': ORDER_ID492,
        'valid': False,
    }
    response = await taxi_cardstorage.post('v1/update_card', json=body)
    assert response.status_code == 200
    record = mongodb.cards.find_one({'owner_uid': '123'})
    assert not record['valid']
    assert record['busy_with'] == [{'order_id': ORDER_ID492}]
    assert len(record['regions_checked']) == 3
    assert {'id': 225} in record['regions_checked']
    assert {'id': 336} in record['regions_checked']
    assert {'id': 447} in record['regions_checked']


async def test_update_card_bad_busy_request(taxi_cardstorage, mongodb):
    body = {
        'yandex_uid': '123',
        'card_id': CARD_X234,
        'mark_busy': ORDER_ID492,
        'unmark_busy': ORDER_ID492,
    }
    response = await taxi_cardstorage.post('v1/update_card', json=body)
    assert response.status_code == 400
