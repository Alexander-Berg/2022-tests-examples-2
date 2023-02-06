import pytest

from taxi.core import async
from taxi.core import db
from taxi.external import chat
from taxi.internal import dbh
from taxi.internal.order_kit.plg import chat_processing


@async.inline_callbacks
def prepare_events(ev_list, order):
    collection = db.chat_events_queue
    yield collection.update({'_id': {'$in': ev_list}},
                            {'$set': {'order_id': order}},
                            multi=True)


@pytest.mark.config(CLIENTDRIVER_CHAT_ALLOWED_CATEGORIES=['econom', 'personal_driver'])
@pytest.mark.config(CLIENTDRIVER_CHAT_TRANSPORTING_CATEGORIES=['personal_driver'])
@pytest.mark.parametrize('order_id,events,chat_id,chat_visible', [
    ('order_id', [], {}, None),
    ('order_id', ['not_handled'], {}, None),
    ('order_id', ['created'], 'created_chat_id', False),
    ('order_id', ['created', 'assigned'], 'created_chat_id', True),
    ('order_id', ['created', 'assigned', 'autoreorder'], 'created_chat_id', False),
    ('order_id', ['created', 'assigned', 'autoreorder', 'transporting'], {}, None),
    ('order_id', ['created', 'assigned', 'finished'], {}, None),
    ('order_id_2', ['created', 'assigned', 'transporting'], 'created_chat_id', True),
    ('order_id_2', ['created', 'assigned', 'transporting', 'finished'], {}, None),
])
@pytest.inline_callbacks
def test_chat_processing(patch, order_id, events, chat_id, chat_visible):
    @patch('taxi.external.chat.create')
    @async.inline_callbacks
    def create(*args, **kwrags):
        yield async.return_value(chat_id)

    @patch('taxi.external.chat.post_update_with_retry')
    @async.inline_callbacks
    def update(*args, **kwrags):
        yield async.return_value()

    yield prepare_events(events, order_id)
    yield chat_processing.process_chat_events(order_id, {})

    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    assert proc.chat_id == chat_id
    assert proc.chat_visible == chat_visible

    dbh_events = dbh.chat_events_queue
    new_list = yield dbh_events.Doc.retrieve_events(
        order_id, dbh_events.STATUS_NEW)
    assert len(new_list) == 0


@pytest.mark.config(CLIENTDRIVER_CHAT_ALLOWED_CATEGORIES=['econom', 'personal_driver'])
@pytest.mark.config(CLIENTDRIVER_CHAT_TRANSPORTING_CATEGORIES=['personal_driver'])
@pytest.mark.config(CLIENTDRIVER_CHAT_ENABLING_RESTRICTIONS={
    'enabled': True,
    'disallowed_payment_types': ['cash'],
    'min_orders_count': 10
})
@pytest.mark.parametrize('order_id,order_counts,chat_visible', [
    ('order_id', 1, True),
    ('order_id', 200, True),
    ('order_id_2', 1, None),
    ('order_id_2', 50, True),
])
@pytest.inline_callbacks
def test_chat_creation_restriction(patch, order_id, order_counts, chat_visible):
    @patch('taxi.external.chat.create')
    @async.inline_callbacks
    def create(*args, **kwrags):
        yield async.return_value('123')

    @patch('taxi.external.chat.post_update_with_retry')
    @async.inline_callbacks
    def update(*args, **kwrags):
        yield async.return_value()

    @patch('taxi.external.user_statistics._v1_orders')
    @async.inline_callbacks
    def v1_orders(*args, **kwargs):
        yield async.return_value({
              "data": [
                {
                  "counters": [
                    {
                      "counted_from": "2021-06-22T10:03:08.782+0000",
                      "counted_to": "2022-02-08T12:57:31.18+0000",
                      "properties": [
                      ],
                      "value": order_counts
                    }
                  ],
                  "identity": {
                    "type": "yandex_uid",
                    "value": "123"
                  }
                }
              ]
            }
        )

    yield prepare_events(['created', 'assigned'], order_id)
    yield chat_processing.process_chat_events(order_id, {})

    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    assert proc.chat_visible == chat_visible

    dbh_events = dbh.chat_events_queue
    new_list = yield dbh_events.Doc.retrieve_events(
        order_id, dbh_events.STATUS_NEW)
    assert len(new_list) == 0


@pytest.mark.parametrize('events,func,failed,cancelled', [
    (
            ['created_fail', 'assigned_fail'],
            'handle_creation',
            ['created_fail'],
            ['assigned_fail']
    ),
    (
            ['created_fail', 'assigned_fail'],
            'handle_assigning',
            ['assigned_fail'],
            []
    ),
    (
            ['created_fail', 'assigned_fail', 'autoreorder', 'finished'],
            'handle_assigning',
            [],
            ['created_fail', 'assigned_fail', 'autoreorder'],
    ),
])
@pytest.inline_callbacks
def test_chat_processing_error(patch, events, func, failed, cancelled):
    @patch('taxi.external.chat.create')
    @async.inline_callbacks
    def create(*args, **kwrags):
        yield async.return_value("chat_id")

    @patch('taxi.internal.order_kit.driver_client_chat.%s' % func)
    @async.inline_callbacks
    def error_func(*args, **kwrags):
        raise chat.BaseError

    order_id = 'order_id'
    yield prepare_events(events, order_id)
    yield chat_processing.process_chat_events(order_id, {})

    dbh_events = dbh.chat_events_queue
    ev_list = yield dbh_events.Doc.retrieve_events(
        order_id, dbh_events.STATUS_FAILED)
    failed_events = [x['_id'] for x in ev_list]
    assert failed_events == failed

    ev_list = yield dbh_events.Doc.retrieve_events(
        order_id, dbh_events.STATUS_CANCELLED)
    cancelled_events = [x['_id'] for x in ev_list]
    assert cancelled_events == cancelled

    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    assert (proc.chat_visible or False) is False


@pytest.mark.parametrize('events,cancelled', [
    (
            ['created', 'assigned', 'finished'],
            ['created', 'assigned'],
    ),
])
@pytest.inline_callbacks
def test_close_chat(events, cancelled):
    order_id = 'order_id'
    yield prepare_events(events, order_id)
    yield chat_processing.process_chat_events(order_id, {})

    dbh_events = dbh.chat_events_queue
    ev_list = yield dbh_events.Doc.retrieve_events(
        order_id, dbh_events.STATUS_CANCELLED)
    cancelled = [x['_id'] for x in ev_list]
    assert cancelled == cancelled

    done_list = yield dbh_events.Doc.retrieve_events(
        order_id, dbh_events.STATUS_DONE)
    assert len(done_list) == 1


@pytest.mark.parametrize('events', [
    (['send_message']),
])
@pytest.inline_callbacks
def test_send_message(events, patch):
    chat_text = "Chat Text!"
    chat_id = 'chat_id'

    @patch('taxi.external.chat.create')
    @async.inline_callbacks
    def create(*args, **kwrags):
        yield async.return_value(chat_id)

    @patch('taxi.external.chat.post_update_with_retry')
    @async.inline_callbacks
    def update(cid, url, payload_maker, **kwrags):
        payload = payload_maker({}, {})
        message = payload['message']
        assert cid == chat_id
        assert message['text'] == chat_text
        assert message['metadata']['message_key'] == 'chat.msg'
        assert message['metadata']['event_index'] == 7
        yield async.return_value()

    @patch('taxi.internal.notifications.order.text_formatter.make_text')
    @async.inline_callbacks
    def make_text(*args, **kwrags):
        yield async.return_value(chat_text)

    order_id = 'order_id'
    yield prepare_events(events, order_id)
    yield chat_processing.process_chat_events(order_id, {})

    dbh_events = dbh.chat_events_queue
    new_list = yield dbh_events.Doc.retrieve_events(
        order_id, dbh_events.STATUS_NEW)
    assert len(new_list) == 0


@pytest.inline_callbacks
def test_enqueue_chat_event():
    order_id = 'test_order_id'
    event = 'send_message'
    performer_index = 6
    event_index = 7
    message_key = 'send_message_key'
    payload = {'title': 'Title'}

    task = dbh.chat_events_queue.new_task(
        order_id, event, performer_index, event_index, message_key, payload)
    task.enqueue()

    ev_list = yield dbh.chat_events_queue.Doc.retrieve_events(
        order_id, dbh.chat_events_queue.STATUS_NEW)
    ev = ev_list[0]

    assert ev.order_id == order_id
    assert ev.event_key == event
    assert ev.state_metadata.performer_index == performer_index
    assert ev.state_metadata.event_index == event_index
    assert ev.state_metadata.event_index == event_index
    assert ev.message_data.message_key == message_key
    assert ev.message_data.payload == payload
