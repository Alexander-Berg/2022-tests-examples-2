# -*- coding: utf-8 -*-

import copy
import datetime
import pytest

from taxi.conf import settings
from taxi.external import zendesk as zendesk_ext
from taxi.internal import dbh
from taxi.internal import taximeter
from taxi.internal import zendesk
from taxi.util import dates


class PatchedClient:

    def __init__(self, id):
        self.id = id


class ZClient(object):
        def __init__(self, id='yataxi'):
            self.counter = 0
            self.tickets = {}
            self.id = id

        def ticket_create(self, data):
            self.counter += 1
            ticket_id = self.counter
            res = copy.copy(data)
            res['ticket']['id'] = ticket_id
            res['ticket']['requester_id'] = 'STUB_ID'
            self.tickets[ticket_id] = res
            return res

        def ticket_update(self, ticket_id, data):
            self.tickets[ticket_id].update(data['ticket'])

        def ticket_get(self, ticket_id):
            return self.tickets[ticket_id]

        def user_create_or_update(self, data):
            return {'user': {'id': 1}}


@pytest.mark.filldb(_fill=True)
@pytest.inlineCallbacks
@pytest.mark.parametrize(
    'zone_name,expected_result',
    [
        (
            'moscow',
            'yataxi'
        ),
        (
            'baku',
            'yutaxi'
        )
    ]
)
def test_choose_zendesk(zone_name, expected_result, monkeypatch):

    def get_client_by_id(id):
        client = PatchedClient(id)
        return client

    monkeypatch.setattr(
        zendesk_ext, 'get_zendesk_client_by_id', get_client_by_id
    )

    client = yield zendesk.get_zendesk_client_by_order('_id', zone_name)
    assert client.id == expected_result


@pytest.mark.filldb(_fill=False)
@pytest.inlineCallbacks
@pytest.mark.parametrize(
    'country,expected_result',
    [
        (
            'rus',
            'yuataxi'
        ),
        (
            'aze',
            'yutaxi'
        ),
        (
            'tst',
            'yataxi'
        )
    ]
)
@pytest.mark.config(ZENDESK_BY_COUNTRIES={
        '__default__': 'yataxi',
        'aze': 'yutaxi',
        'rus': 'yuataxi'
})
def test_choose_zendesk_by_country(country, expected_result, monkeypatch):

    def get_client_by_id(id):
        client = PatchedClient(id)
        return client

    monkeypatch.setattr(
        zendesk_ext, 'get_zendesk_client_by_id', get_client_by_id
    )

    client = yield zendesk.get_zendesk_client_by_country(country)
    assert client.id == expected_result


NOW = datetime.datetime(2018, 6, 26)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'order_request_due,due,order_created,created,expected_due',
    [
        (
            datetime.datetime(2018, 6, 22),
            {},
            {},
            {},
            datetime.datetime(2018, 6, 22)
        ),
        (
            {},
            datetime.datetime(2018, 6, 23),
            {},
            {},
            datetime.datetime(2018, 6, 23)
        ),
        (
            {},
            {},
            datetime.datetime(2018, 6, 24),
            {},
            datetime.datetime(2018, 6, 24)
        ),
        (
            {},
            {},
            {},
            datetime.datetime(2018, 6, 25),
            datetime.datetime(2018, 6, 25)
        ),
        (
            {},
            {},
            {},
            {},
            NOW
        )
    ]
)
@pytest.mark.filldb(_fill=True)
@pytest.inlineCallbacks
def test_create_compensation_ticket(patch, order_request_due, due, order_created, created, expected_due, monkeypatch):

    @patch('taxi_stq._client.put')
    def put(queue=None, eta=None, task_id=None, args=None, kwargs=None):
        pass

    park = dbh.parks.Doc({
        'city': 'Moscow',
        'billing_email': 'testpark@yandex.ru',
        'name': 'Park1'
    })
    order_proc_dict = {
        '_id': 'order1',
        'created': created,
        'order': {
            'created': order_created,
            "request": {
                "payment": {"type": "cash"},
                "due": order_request_due
            },
            "performer": {"candidate_index": 0}
        },
        "candidates": [
            {
                "driver_id": "drv_id",
                "alias_id": "driver_order",
                "db_id": "db_id"
            }
        ],
        "performer": {
            "candidate_index": 0,
        },
        'aliases': []
    }
    if due:
        order_proc_dict['aliases'].append({'due': due, 'id': 'driver_order'})
    order_proc = dbh.order_proc.Doc(order_proc_dict)

    zclient = ZClient('yataxi')

    def get_client_by_order(id, zone, log_extra):
        return zclient

    monkeypatch.setattr(zendesk_ext, 'get_zendesk_client', lambda: zclient)
    monkeypatch.setattr(zendesk, 'get_zendesk_client_by_order',
                        get_client_by_order)

    yield zendesk.create_compensation_ticket(park, order_proc, 100, 'Please',
                                             'alias_123')

    ticket = zclient.ticket_get(1)
    comment = ticket['comment']['body']
    url_taximeter = taximeter.admin_url_by_id('db_id', 'driver_order')
    url_taxi_order = settings.ADMIN_URL + 'orders/' + order_proc.pk
    expected_due_string = dates.timestring(
        expected_due, format=zendesk.SHORT_DATE_FORMAT)

    assert ticket['ticket']['custom_fields'] == [
        {'id': 38647729, 'value': 'order1'},
        {'id': 360000161885, 'value': 'alias_123'}
    ]
    assert comment.find(url_taximeter) != -1
    assert comment.find(url_taxi_order) != -1
    assert ticket['ticket']['comment']['body'].find(expected_due_string) != -1

    call = put.calls[0]
    assert call['queue'] == 'support_info_zendesk_to_startrack'
    assert call['args'][1] == 'compensation_ticket'


@pytest.mark.parametrize(
    'email,billing_email,expected_requester', [
        ('testpark@yandex.ru', None, 'testpark@yandex.ru'),
        (None, 'testpark2@yandex.ru', 'testpark2@yandex.ru'),
        (None, None, 'park_1@taxi.yandex.ru'),
    ])
@pytest.mark.filldb(_fill=True)
@pytest.inlineCallbacks
def test_create_moderation_ticket(patch, monkeypatch, email, billing_email,
                                  expected_requester):
    @patch('taxi_stq._client.put')
    def put(queue=None, eta=None, task_id=None, args=None, kwargs=None):
        pass

    park = dbh.parks.Doc({
        'name': 'Park1',
        'billing_email': billing_email,
        'email': email,
        '_id': '1'
    })
    order = dbh.orders.Doc({
        '_id': 'order1',
    })

    zclient = ZClient('yataxi')

    def get_client_by_order(id, zone):
        return zclient

    monkeypatch.setattr(zendesk_ext, 'get_zendesk_client', lambda: zclient)
    monkeypatch.setattr(zendesk, 'get_zendesk_client_by_order',
                        get_client_by_order)

    yield zendesk.create_moderation_ticket(
        park, order, 'paid_by_cash', 'login', 'some important comment',
        False
    )

    ticket = zclient.ticket_get(1)
    assert ticket['ticket']['requester']['email'] == expected_requester

    call = put.calls[0]
    assert call['queue'] == 'support_info_zendesk_to_startrack'
    assert call['args'][1] == 'moderation_ticket'


@pytest.mark.parametrize(
    'message_type,kwargs,expected_ticket',
    [
        (
            'text',
            {
                'public': True
            },
            {
                'ticket': {
                    'id': 1,
                    'requester_id': 'STUB_ID'
                },
                'comment': {
                    'author_id': 1,
                    'body': 'message',
                    'public': True
                }
            }
        ),
        (
            'text',
            {
                'public': False
            },
            {
                'ticket': {
                    'id': 1,
                    'requester_id': 'STUB_ID'
                },
                'comment': {
                    'author_id': 2780965569,
                    'body': 'message',
                    'public': False
                }
            }
        ),
        (
            'csat',
            {
                'csat_value': 'amazing',
                'csat_reasons': [
                    'fast answer',
                    'thank you'
                ]
            },
            {
                'ticket': {
                    'id': 1,
                    'requester_id': 'STUB_ID'
                },
                'comment': {
                    'body': 'fast answer,thank you',
                    'public': False
                },
                'author_id': 1,
                'status': 'closed',
                'custom_fields': [
                    {'id': 45387925, 'value': 5}
                ]
            }
        )
    ]
)
@pytest.inlineCallbacks
def test_add_comment_from_chat_to_zendesk(monkeypatch, message_type, kwargs,
                                          expected_ticket):
    zclient = ZClient()
    monkeypatch.setattr(zendesk_ext, 'get_zendesk_client', lambda: zclient)

    zclient.ticket_create({'ticket': {}})
    yield zendesk.add_comment_from_chat_to_zendesk(
        ticket_id=1,
        author_id=1,
        message_id=1,
        message='message',
        message_type=message_type,
        **kwargs)

    ticket = zclient.ticket_get(1)
    assert ticket == expected_ticket


@pytest.mark.parametrize("phone, expected", [
    ("", "null@newdriver.taxi.yandex.ru"),
    ("+79991112233", "9991112233@newdriver.taxi.yandex.ru"),
    ("+79991112233; +79993332211", "9991112233@newdriver.taxi.yandex.ru"),
    ("+79991112233 +79993332211", "9991112233@newdriver.taxi.yandex.ru"),
])
def test__build_email_from_phone(phone, expected):
    assert zendesk._build_email_from_phone(phone) == expected


@pytest.mark.parametrize("id,excepted_ticket", [
    (
            "req1",
            {'ticket': {
                'comment': {'body': 'body'},
                'requester': {
                    'name': 'driver',
                    'email': '9000000000@newdriver.taxi.yandex.ru',
                },
                'requester_id': 'STUB_ID',
                'id': 1,
                'custom_fields': [
                    {'id': 114099646774, 'value': 'term'},
                    {'id': 30290925, 'value': 'driver'},
                    {'id': 114099634573, 'value': 'campaign'},
                    {'id': 114099634873, 'value': 'content'},
                    {'id': 114094677794, 'value': '100500'},
                    {'id': 114099646754, 'value': 'source'},
                    {'id': 30557445, 'value': '+79000000000'},
                ],
                'subject': 'theme'
            },
            },
    ),
])
@pytest.mark.current
@pytest.mark.filldb(_fill=True)
@pytest.inlineCallbacks
def test_create_newdriver_ticket(id, excepted_ticket, monkeypatch):
    zen_client = ZClient('yataxi')

    def get_client():
        return zen_client

    monkeypatch.setattr(
        zendesk_ext, 'get_zendesk_newdrivers_client', get_client
    )

    yield zendesk.create_newdriver_ticket(id)
    ticket = zen_client.ticket_get(1)
    assert sorted(ticket) == sorted(excepted_ticket)
