import uuid

import bson
import pytest


class OrderCoreContext:
    def __init__(self):
        self.post_event_times_called = 0
        self.get_fields_times_called = 0
        self.set_fields_times_called = 0
        self.create_draft_times_called = 0

        self.last_call_idempotency_token = None


@pytest.fixture(autouse=True)
def mock_order_core(mockserver, db, now):
    order_core_context = OrderCoreContext()

    @mockserver.json_handler('/order-core/internal/processing/v1/event-batch')
    def order_core_post_events(request):
        order_id = request.args['order_id']
        idempotency_token = request.headers['X-Idempotency-Token']
        order_core_context.last_call_idempotency_token = idempotency_token
        assert order_id is not None
        assert idempotency_token is not None
        request_bson = bson.BSON(request.data).decode()
        request_events = request_bson['events']
        query = request_bson.get('filter', {})
        query['_id'] = order_id
        query['_shard_id'] = _get_shard_id(order_id)

        update = request_bson.get('extra_update', {})
        events = []
        for request_event in request_events:
            event = request_event.get('event_extra_payload', {})
            event['c'] = now
            event['h'] = True
            event['q'] = request_event['event_key']
            if 'event_arg' in event:
                event['a'] = request_event['event_arg']
            else:
                event.pop('a', None)
            events.append(event)

        update.setdefault('$push', {}).setdefault(
            'order_info.statistics.status_updates', {},
        )['$each'] = events
        update.setdefault('$set', {})['processing.need_start'] = True
        update['$set']['order_info.need_sync'] = True
        update.setdefault('$inc', {})['order.version'] = 1
        update['$inc']['processing.version'] = 1
        assert (
            '$unset' not in update or update['$unset']
        )  # empty dict is False in python

        fields = request_bson.get('fields', None)

        response = db.order_proc.find_and_modify(
            query, update, fields=fields, new=True,
        )
        if response is None:
            response = db.order_proc.find_one({'_id': order_id})
            if response is not None:
                status_code = 409
            else:
                status_code = 404
            return mockserver.make_response('', status_code)

        order_core_context.post_event_times_called += 1
        return mockserver.make_response(
            bson.BSON.encode(response), 200, content_type='application/bson',
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/', prefix=True,
    )
    def order_core_post_event(request):
        event_key = request.path.rsplit('/', 1)[-1]
        order_id = request.args['order_id']
        idempotency_token = request.headers['X-Idempotency-Token']
        order_core_context.last_call_idempotency_token = idempotency_token
        assert order_id is not None
        assert idempotency_token is not None
        if event_key != 'restart-processing':
            request_bson = bson.BSON(request.data).decode()
            query = request_bson.get('filter', {})
            query['_id'] = order_id
            query['_shard_id'] = _get_shard_id(order_id)

            update = request_bson.get('extra_update', {})
            event = request_bson.get('event_extra_payload', {})
            event['c'] = now
            event['h'] = True
            event['q'] = event_key
            if 'event_arg' in event:
                event['a'] = request_bson['event_arg']
            else:
                event.pop('a', None)

            update.setdefault('$push', {}).setdefault(
                'order_info.statistics.status_updates', {},
            )['$each'] = [event]
            update.setdefault('$set', {})['processing.need_start'] = True
            update['$set']['order_info.need_sync'] = True
            update.setdefault('$inc', {})['order.version'] = 1
            update['$inc']['processing.version'] = 1

            fields = request_bson.get('fields', None)

            response = db.order_proc.find_and_modify(
                query, update, fields=fields, new=True,
            )
            if response is None:
                response = db.order_proc.find_one({'_id': order_id})
                if response is not None:
                    status_code = 409
                else:
                    status_code = 404
                return mockserver.make_response('', status_code)
        else:
            response = {'_id': order_id}

        order_core_context.post_event_times_called += 1
        return mockserver.make_response(
            bson.BSON.encode(response), 200, content_type='application/bson',
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def order_core_get_fields(request):
        order_core_context.get_fields_times_called += 1

        order_id = request.args['order_id']
        order_id_type = request.args.get('order_id_type', 'exact_id')

        if order_id_type == 'exact_id':
            query = {'_id': order_id}
        elif order_id_type == 'alias_id':
            query = {'aliases.id': order_id}
        elif order_id_type == 'client_id':
            query = {'$or': [{'_id': order_id}, {'reorder.id': order_id}]}
        elif order_id_type == 'any_id':
            query = {
                '$or': [
                    {'_id': order_id},
                    {'reorder.id': order_id},
                    {'aliases.id': order_id},
                ],
            }
        else:
            return mockserver.make_response('', 400)

        fields = bson.BSON(request.data).decode()['fields']
        assert isinstance(fields, list)
        fields.extend(['processing.version', 'order.version'])

        proc_doc = db.order_proc.find_one(query, projection=fields)
        if not proc_doc:
            return mockserver.make_response('', 404)
        response = {
            'document': proc_doc,
            'revision': {
                'order.version': proc_doc.get('order', {}).get('version', 5),
                'processing.version': proc_doc.get('processing', {}).get(
                    'version', 11,
                ),
            },
        }

        return mockserver.make_response(
            bson.BSON.encode(response), 200, content_type='application/bson',
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    def order_core_set_fields(request):
        order_core_context.set_fields_times_called += 1

        order_id = request.args['order_id']
        assert order_id

        data = bson.BSON(request.data).decode()

        order = db.order_proc.find_one({'_id': order_id})
        if not order:
            return mockserver.make_response(
                {'code': 'not_found', 'message': 'no such order'}, 404,
            )

        query = dict(data['filter'])
        assert '_id' not in query
        assert '_shard_id' not in query
        query.update(data['revision'])
        query['_id'] = order_id
        query['_shard_id'] = order['_shard_id']
        update = dict(data['update'])
        assert '$currentDate' not in update
        update.update({'$currentDate': {'updated': True}})

        proc = db.order_proc.find_and_modify(
            query, update, fields=data['fields'], new=True,
        )

        if not proc:
            return mockserver.make_response(
                {'code': 'race_condition', 'message': 'order_was_changed'},
                409,
            )

        return mockserver.make_response(
            bson.BSON.encode({'document': proc}),
            200,
            content_type='application/bson',
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/create-draft',
    )
    def order_core_create_draft(request):
        assert request.method == 'POST'
        assert request.content_type == 'application/bson'
        data = bson.BSON.decode(request.data)
        assert 'draft' in data
        draft = data['draft']
        assert '_id' not in draft['order']
        assert '_shard_id' not in draft['order']
        assert '_shard_id' not in draft

        order_id = 'f4eb6aaa29ad4a6eb53f8a7620793561'
        draft['order']['_id'] = order_id
        draft['order']['_shard_id'] = 0
        proc = db.order_proc.find_and_modify(
            {'_id': order_id, '_shard_id': 0},
            {'$setOnInsert': draft, '$currentDate': {'updated': True}},
            new=True,
            upsert=True,
        )

        order_core_context.create_draft_times_called += 1

        return mockserver.make_response(
            bson.BSON.encode({'document': proc}),
            200,
            content_type='application/bson',
        )

    return order_core_context


def _get_shard_id(order_id):
    try:
        uuid_int = uuid.UUID(order_id).int
    except (ValueError, AttributeError):
        return 0
    return (((uuid_int >> 76) & 0xF) | ((uuid_int >> 58) & 0x30)) ^ 0x24
