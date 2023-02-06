import datetime
import json
import uuid

import pytest


@pytest.fixture(autouse=True)
def cardstorage(mockserver, db, load_json):
    class Context:
        trust_response = None
        persistent_id = None
        uber_persistent_id = None
        status_code = 200

    context = Context()

    def format_card(card):
        result = {}
        result['card_id'] = card['payment_id']
        result['billing_card_id'] = card.get('billing_id', '')
        result['permanent_card_id'] = card.get('permanent_payment_id', '')
        result['currency'] = card.get('currency', '')
        result['number'] = card.get('number', '')
        result['owner'] = card['owner_uid']
        result['possible_moneyless'] = card.get('possible_moneyless', False)
        result['region_id'] = str(card.get('region_id', ''))
        regions = card.get('regions_checked', ())
        result['regions_checked'] = list(map(str, regions))
        result['system'] = card.get('system', '')
        result['valid'] = card.get('valid', True)
        result['bound'] = not card.get('unbound', False)
        result['unverified'] = card.get('unverified', False)
        result['busy'] = bool(card.get('busy_with', []))
        result['busy_with'] = card.get('busy_with', [])
        result['from_db'] = card.get('from_db', False)

        exp_date = card.get('expiration_date', datetime.datetime.now())
        result['expiration_month'] = exp_date.month
        result['expiration_year'] = exp_date.year

        result['persistent_id'] = card.get('persistent_id', '')
        result['bin'] = card.get('bind', '')
        result['service_labels'] = card.get('service_labels', [])
        result['aliases'] = card.get('aliases', [])
        result['blocking_reason'] = card.get('blocking_reason', '')
        result['bin'] = card.get('bin', '')
        if 'payer_info' in card:
            payer_info = card['payer_info']
            family = {'is_owner': card.get('is_family_card_owner', True)}
            if not family['is_owner']:
                family['owner_uid'] = payer_info['uid']

                family_info = payer_info['family_info']
                family['limit'] = family_info['limit']
                family['expenses'] = family_info['expenses']
                family['currency'] = family_info['currency']
                family['frame'] = family_info['frame']
            result['family'] = family

        return result

    def set_persistent_id(card, is_uber, persistent_id=None):
        if not card.get('persistent_id'):
            if not persistent_id:
                persistent_id = ('uber:' if is_uber else '') + str(
                    uuid.uuid4(),
                )[:32]
            card['persistent_id'] = persistent_id
            label = 'taxi:persistent_id:' + persistent_id
            if label not in card['service_labels']:
                card['service_labels'].append(label)

    def check_is_uber(body):
        service_type = body.get('service_type', 'card')
        if service_type == 'uber':
            return True
        elif service_type != 'card':
            raise RuntimeError('Wrong service_type: %s' % service_type)
        return False

    def get_body(request):
        return json.loads(list(request.form.items())[0][0])

    @mockserver.json_handler('/cardstorage/v1/payment_methods')
    def mock_payment_methods(request):
        if context.status_code != 200:
            error = '{"code": "500", "message": "test"}'
            return mockserver.make_response(error, context.status_code)

        body = get_body(request)

        is_uber = check_is_uber(body)
        cache_preferred = body.get('cache_preferred', False)
        renew_after = body.get('renew_after')
        if context.trust_response and (not cache_preferred or renew_after):
            response = load_json(context.trust_response)
            ids = []
            for card in response:
                card['owner_uid'] = body['yandex_uid']
                set_persistent_id(card, is_uber, context.persistent_id)
                db.cards.update(
                    {'payment_id': card['payment_id']}, card, upsert=True,
                )
                ids.append(card['payment_id'])
            # mark all other cards of this owner as unbound
            db.cards.update(
                {'payment_id': {'$nin': ids}, 'owner_uid': body['yandex_uid']},
                {'$set': {'unbound': True}},
            )
        cards = db.cards.find({'owner_uid': body['yandex_uid']})
        return {
            'available_cards': [format_card(card) for card in cards],
            'yandex_cards': {'available_cards': []},
        }

    @mockserver.json_handler('/cardstorage/v1/cards')
    def mock_get_cards(request):
        body = get_body(request)
        check_is_uber(body)
        query = {}
        if 'busy_id' in body:
            query['busy_with'] = body['busy_id']
        if 'number' in body:
            query['number'] = body['number']
        if not query:
            raise RuntimeError('number or busy_id shall be specified')
        cards = db.cards.find(query)
        return {'cards': [format_card(card) for card in cards]}

    @mockserver.json_handler('/cardstorage/v1/card')
    def mock_get_card(request):
        body = get_body(request)
        query = {
            'owner_uid': body['yandex_uid'],
            'payment_id': body['card_id'],
        }
        card = db.cards.find_one(query)
        if card:
            set_persistent_id(card, check_is_uber(body), context.persistent_id)
            return format_card(card)
        error = '{"code": "404", "message": "Card not found"}'
        return mockserver.make_response(error, 404)

    @mockserver.json_handler('/cardstorage/v1/update_card')
    def mock_update_card(request):
        body = get_body(request)
        if 'mark_busy' in body:
            db.cards.update(
                {'payment_id': body['card_id']},
                {'$addToSet': {'busy_with': {'order_id': body['mark_busy']}}},
            )
        if 'unmark_busy' in body:
            db.cards.update(
                {'payment_id': body['card_id']},
                {'$pull': {'busy_with': {'order_id': body['unmark_busy']}}},
            )

        if 'regions_checked' in body:
            regions = [{'id': int(r)} for r in body['regions_checked']]
            db.cards.update(
                {'payment_id': body['card_id']},
                {'$addToSet': {'regions_checked': {'$each': regions}}},
            )
        if 'regions_to_delete' in body:
            regions = [{'id': int(r)} for r in body['regions_to_delete']]
            db.cards.update(
                {'payment_id': body['card_id']},
                {'$pull': {'regions_checked': {'$in': regions}}},
            )

    @mockserver.json_handler('/cardstorage/v1/release_cards')
    def mock_release_cards(request):
        body = get_body(request)
        query = {'busy_with': body['busy_id']}
        if 'except_card_id' in body or 'except_yandex_uid' in body:
            query['$nor'] = []
        if 'except_card_id' in body:
            query['$nor'].append({'payment_id': body['except_card_id']})
        if 'except_yandex_uid' in body:
            query['$nor'].append({'owner_uid': body['except_yandex_uid']})

        db.cards.update(query, {'$pull': {'busy_with': body['busy_id']}})

    return context
