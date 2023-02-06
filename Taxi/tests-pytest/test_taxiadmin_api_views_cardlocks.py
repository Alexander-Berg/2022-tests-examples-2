# -*- coding: utf-8 -*-
import pytest

from taxi.core import async
from taxiadmin.api.views import cardlocks


@pytest.inline_callbacks
def test_get_cards(patch):
    class Card:
        pass

    @patch('taxi.internal.card_operations.get_cards_from_db')
    @async.inline_callbacks
    def get_cards_from_db(busy_id):
        yield
        assert busy_id == '1234'
        card = Card()
        card.card_id = 'x987'
        card.owner = 'uid1'
        async.return_value([card])

    @patch('taxi.internal.card_operations.get_cards')
    @async.inline_callbacks
    def get_cards(owner_uid, **kwargs):
        yield
        assert owner_uid == 'uid2'
        card = Card()
        card.card_id = 'x987'
        card.owner = 'uid2'
        async.return_value([card])

    cards = yield cardlocks._get_cards({'_id': '1234', 'user_uid': 'uid2'})
    assert {card.card_id for card in cards} == {'x987'}
    assert {card.owner for card in cards} == {'uid1', 'uid2'}
