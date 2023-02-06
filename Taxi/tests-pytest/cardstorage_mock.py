from taxi.core import async
from taxi.core import db


def mock_cardstorage(patch):
    def format_card(card):
        card['owner'] = card.pop('owner_uid')
        card['card_id'] = card.pop('payment_id')
        if 'billing_id' in card:
            card['billing_card_id'] = card.pop('billing_id')
        card['busy_with'] = card.get('busy_with', [])
        if 'permanent_payment_id' in card:
            card['permanent_card_id'] = card.pop('permanent_payment_id')
        regions_checked = []
        for region in card.get('regions_checked', ()):
            regions_checked.append(str(region['id']))
        card['regions_checked'] = regions_checked
        card['bound'] = not card.pop('unbound', False)
        return card

    @patch('taxi.external.cardstorage.get_payment_methods')
    @async.inline_callbacks
    def cardstorage_get_payment_methods(request, log_extra=None):
        cards = yield db.cards.find({'owner_uid': request.yandex_uid}).run().result
        async.return_value([format_card(card) for card in cards])

    @patch('taxi.external.cardstorage.get_cards')
    @async.inline_callbacks
    def cardstorage_get_cards(request, log_extra=None):
        query = {}
        if hasattr(request, 'busy_id'):
            query['busy_with'] = request.busy_id
        if hasattr(request, 'number'):
            query['number'] = request.number
        if not query:
            raise RuntimeError('number or busy_id shall be specified')
        cards = yield db.cards.find(query).run().result
        async.return_value([format_card(card) for card in cards])

    @patch('taxi.external.cardstorage.get_card')
    @async.inline_callbacks
    def get_card(request, log_extra=None):
        query = {
            'owner_uid': request.yandex_uid,
            'payment_id': request.card_id
        }
        card = yield db.cards.find_one(query)
        async.return_value(format_card(card) if card else None)

    @patch('taxi.external.cardstorage.update_card')
    @async.inline_callbacks
    def update_card(request, log_extra=None):
        if hasattr(request, 'mark_busy'):
            yield db.cards.update(
                {'payment_id': request.card_id},
                {'$addToSet': {'busy_with': {'order_id': request.mark_busy}}}
            )
        if hasattr(request, 'unmark_busy'):
            yield db.cards.update(
                {'payment_id': request.card_id},
                {'$pull': {'busy_with': {'order_id': request.unmark_busy}}}
            )

        if hasattr(request, 'regions_checked'):
            regions = [{'id': int(r)} for r in request.regions_checked]
            yield db.cards.update(
                {'payment_id': request.card_id},
                {'$addToSet': {
                    'regions_checked': {'$each': regions}
                }}
            )
        if hasattr(request, 'regions_to_delete'):
            regions = [{'id': int(r)} for r in request.regions_to_delete]
            yield db.cards.update(
                {'payment_id': request.card_id},
                {'$pull': {
                    'regions_checked': {'$in': regions}
                }}
            )
