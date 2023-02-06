# pylint: disable=redefined-outer-name
import pytest

from test_corp_clients.web import test_utils

NOW_STRING = '2021-11-01T11:00:00.0'


@pytest.fixture
def get_bound_payment_methods_mock(patch, load_json):
    @patch('taxi.clients.billing_v2.BalanceClient.get_bound_payment_methods')
    async def _get_bound_payment_methods(operator_uid, service_id):
        return test_utils.GET_BOUND_PAYMENT_METHODS_RESP


@pytest.mark.now(NOW_STRING)
@pytest.mark.parametrize(
    ['yandex_uids', 'expected_cards'],
    [
        pytest.param(
            'yandex_uid_1',
            [
                {
                    'card_id': 'card-123-long',
                    'account': '500000****1111',
                    'yandex_uid': 'yandex_uid_1',
                },
            ],
        ),
        pytest.param(
            'yandex_uid_1,yandex_uid_3,yandex_uid_4',
            [
                {
                    'card_id': 'card-123-long',
                    'account': '500000****1111',
                    'yandex_uid': 'yandex_uid_1',
                },
                {
                    'card_id': 'card-345-long',
                    'account': '500000****3333',
                    'yandex_uid': 'yandex_uid_3',
                },
            ],
        ),
    ],
)
async def test_cards_main_get(
        web_app_client, blackbox_mock, patch, db, yandex_uids, expected_cards,
):
    response = await web_app_client.get(
        '/v1/cards/main', params={'yandex_uids': yandex_uids},
    )

    assert response.status == 200
    response_json = await response.json()

    assert response_json['cards'] == expected_cards


@pytest.mark.now(NOW_STRING)
@pytest.mark.parametrize('card_id', ['card-123-long', 'card-555-long'])
async def test_cards_main_post(
        web_app_client,
        load_json,
        blackbox_mock,
        patch,
        db,
        card_id,
        get_bound_payment_methods_mock,
):
    response = await web_app_client.post(
        '/v1/cards/main',
        params={'client_id': 'client_id_1'},
        json={'card_id': card_id},
    )

    assert response.status == 200

    sort_by = [('created', 1)]

    cards = (
        await db.secondary.corp_cards_main.find({'yandex_uid': 'yandex_uid_1'})
        .sort(sort_by)
        .to_list(None)
    )

    cards_dict = {
        card['card_id']: card
        for card in test_utils.GET_BOUND_PAYMENT_METHODS_RESP
    }

    assert (
        cards[0]['date_to'] is not None
        and cards[0]['card_id_long'] == 'card-123-long'
    )
    assert (
        cards[1]['date_to'] is None
        and cards[1]['card_id_long'] == card_id
        and cards[1]['card_id_short'] == cards_dict[card_id]['id']
    )


@pytest.mark.now(NOW_STRING)
async def test_cards_main_post_new(
        web_app_client,
        load_json,
        blackbox_mock,
        patch,
        db,
        get_bound_payment_methods_mock,
):
    response = await web_app_client.post(
        '/v1/cards/main',
        params={'client_id': 'client_id_2'},
        json={'card_id': 'card-555-long'},
    )

    assert response.status == 200

    sort_by = [('created', 1)]

    cards = (
        await db.secondary.corp_cards_main.find({'yandex_uid': 'yandex_uid_2'})
        .sort(sort_by)
        .to_list(None)
    )

    assert len(cards) == 1
    assert (
        cards[0]['date_to'] is None
        and cards[0]['card_id_long'] == 'card-555-long'
    )
    assert cards[0]['account'] == '546938****9762'
    assert cards[0]['card_id_short'] == 'card-555-short'


async def test_cards_main_post_not_found(
        web_app_client, load_json, blackbox_mock, patch, db,
):
    response = await web_app_client.post(
        '/v1/cards/main',
        params={'client_id': 'client_id_xxx'},
        json={'card_id': 'card-555'},
    )

    assert response.status == 404


async def test_cards_main_delete(web_app_client, load_json, blackbox_mock, db):
    response = await web_app_client.delete(
        '/v1/cards/main', params={'client_id': 'client_id_1'},
    )

    assert response.status == 200

    sort_by = [('created', 1)]
    cards = (
        await db.secondary.corp_cards_main.find({'yandex_uid': 'yandex_uid_1'})
        .sort(sort_by)
        .to_list(None)
    )

    assert len(cards) == 1
    assert cards[0]['date_to'] is not None


async def test_cards_main_delete_not_found(
        web_app_client, load_json, blackbox_mock, patch, db,
):
    response = await web_app_client.delete(
        '/v1/cards/main',
        params={'client_id': 'client_id_xxx'},
        json={'card_id': 'card-555'},
    )

    assert response.status == 404
