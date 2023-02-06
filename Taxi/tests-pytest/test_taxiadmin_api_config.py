# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json
import urllib

from django import test as django_test
import pytest

from taxi import config
from taxi.core import async
from taxi.core import db
from taxi.external import startrack

from taxiadmin import audit


@pytest.mark.parametrize(
    'params,expected_count',
    [
        ({}, 1716),
        ({'tag': 'fallback'}, 9),
        ({'group': 'billing'}, 74),
        ({'name': '_enabled'}, 115),
        ({'description': 'глобал'}, 13),
        ({'group': 'billing', 'description': 'глобал'}, 2),
        ({'group': 'billing', 'name': 'card', 'description': 'глобал'}, 1),
        (
            {
                'group': 'route',
                'name': 'router_42group_enabled',
                'description': 'глобал',
                'tag': 'fallback',
            },
            0,
        ),
    ]
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    ADMIN_AUDIT_TICKET_REQUIRED_CONFIGS=[
        'FORCED_SURGE_OFFER_TTL',
        'PROMOCODES_ENABLED'
    ],
)
def test_get_list(params, expected_count):
    def byteify(params):
        str_params = {}
        for key, value in params.iteritems():
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            str_params[key] = value
        return str_params

    if params:
        query = '?' + urllib.urlencode(byteify(params))
    else:
        query = ''
    response = django_test.Client().get(
        ('/api/config/list/' + query).encode('utf-8')
    )
    assert response.status_code == 200
    data = json.loads(response.content)
    assert len(data['items']) >= expected_count
    if not params:
        ticket_required_configs = {
            item['name'] for item in data['items'] if item['ticket_required']
        }
        assert ticket_required_configs == {
            'ADMIN_AUDIT_TICKET_REQUIRED_CONFIGS',
            'FORCED_SURGE_OFFER_TTL',
            'PROMOCODES_ENABLED',
        }


@pytest.mark.asyncenv('blocking')
def test_get_groups():
    response = django_test.Client().get('/api/config/groups/')
    assert response.status_code == 200
    data = json.loads(response.content)
    assert len(data) > 10
    for item in data:
        assert 'name' in item


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(
    ADMIN_AUDIT_TICKET_REQUIRED_CONFIGS=['FORCED_SURGE_OFFER_TTL']
)
@pytest.inline_callbacks
def test_get():
    url = '/api/config/get/FORCED_SURGE_OFFER_TTL/'
    response = django_test.Client().get(url)
    assert response.status_code == 200
    value = yield config.FORCED_SURGE_OFFER_TTL.get()
    assert json.loads(response.content) == {
        'value': value,
        'group': 'surge',
        'name': 'FORCED_SURGE_OFFER_TTL',
        'tags': [],
        'ticket_required': True,
        'description': 'Сколько времени будет действовать '
                       'предложение из routestats (сек)'
    }
    yield config.FORCED_SURGE_OFFER_TTL.save(value + 100)
    response = django_test.Client().get(url)
    assert response.status_code == 200
    assert json.loads(response.content) == {
        'value': value + 100,
        'group': 'surge',
        'name': 'FORCED_SURGE_OFFER_TTL',
        'tags': [],
        'ticket_required': True,
        'description': 'Сколько времени будет действовать '
                       'предложение из routestats (сек)'
    }


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_save_value():
    url = '/api/config/save/FORCED_SURGE_OFFER_TTL/'
    old_value = yield config.FORCED_SURGE_OFFER_TTL.get()
    data = {
        'old_value': old_value,
        'new_value': {},
    }
    response = django_test.Client().post(url, json.dumps(data),
                                         'application/json')
    assert response.status_code == 406
    data = {
        'old_value': old_value - 1,
        'new_value': old_value + 100,
    }
    response = django_test.Client().post(url, json.dumps(data),
                                         'application/json')
    assert response.status_code == 409
    data['old_value'] += 1
    response = django_test.Client().post(url, json.dumps(data),
                                         'application/json')
    assert response.status_code == 200
    new_value = yield config.FORCED_SURGE_OFFER_TTL.get_fresh()
    assert new_value == old_value + 100

    url = '/api/config/save/PROMOCODES_ENABLED/'
    old_value = yield config.PROMOCODES_ENABLED.get()
    data = {
        'old_value': old_value,
        'new_value': not old_value,
    }
    response = django_test.Client().post(url, json.dumps(data),
                                         'application/json')
    assert response.status_code == 200


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_ticket_required(patch):
    @patch('taxiadmin.audit.check_ticket')
    @async.inline_callbacks
    def check_ticket(ticket_key, login, **kwargs):
        if ticket_key != (yield 'TAXIRATE-1'):
            raise audit.TicketError

    assert (yield config.ADMIN_AUDIT_TICKET_REQUIRED_CONFIGS.get()) == []
    url = '/api/config/save/FORCED_SURGE_OFFER_TTL/'
    data = {
        'old_value': 5 * 60,
        'new_value': 10 * 60,
    }
    response = django_test.Client().post(
        url, json.dumps(data), 'application/json'
    )
    assert response.status_code == 200

    url = '/api/config/save/ADMIN_AUDIT_TICKET_REQUIRED_CONFIGS/'
    data = {
        'old_value': [],
        'new_value': ['FORCED_SURGE_OFFER_TTL'],
    }
    response = django_test.Client().post(
        url, json.dumps(data), 'application/json'
    )
    assert response.status_code == 406
    data['ticket'] = 'TAXIRATE-1'
    response = django_test.Client().post(
        url, json.dumps(data), 'application/json'
    )
    assert response.status_code == 200

    url = '/api/config/save/FORCED_SURGE_OFFER_TTL/'
    data = {
        'old_value': 10 * 60,
        'new_value': 5 * 60,
    }
    response = django_test.Client().post(
        url, json.dumps(data), 'application/json'
    )
    assert response.status_code == 406
    data['ticket'] = 'TAXIRATE-1'
    response = django_test.Client().post(
        url, json.dumps(data), 'application/json'
    )
    assert response.status_code == 200

    url = '/api/config/save/ADMIN_AUDIT_TICKET_REQUIRED_CONFIGS/'
    data = {
        'old_value': ['FORCED_SURGE_OFFER_TTL'],
        'new_value': ['FORCED_SURGE_OFFER_TTL_TYPO'],
        'ticket': 'TAXIRATE-1'
    }
    response = django_test.Client().post(
        url, json.dumps(data), 'application/json'
    )
    assert response.status_code == 406


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_edit_comment_or_related_ticket(patch):
    @patch('taxi.external.startrack.get_ticket_info')
    @async.inline_callbacks
    def get_ticket_info(ticket):
        yield
        if ticket != 'test_ticket':
            raise startrack.ApiError
        async.return_value()

    yield config.FORCED_SURGE_OFFER_TTL.save(300)

    set_url = '/api/config/save/FORCED_SURGE_OFFER_TTL/'
    get_url = '/api/config/get/FORCED_SURGE_OFFER_TTL/'

    comment = 'test_comment'
    related_ticket = 'test_ticket'

    response = django_test.Client().post(
        set_url, json.dumps({
            'old_value': 300,
            'new_value': 500,
            'comment': comment
        }),
        'application/json',
    )
    assert response.status_code == 200
    response = django_test.Client().get(get_url)
    assert json.loads(response.content)['comment'] == comment

    response = django_test.Client().post(
        set_url, json.dumps({
            'old_value': 500,
            'new_value': 500,
            'related_ticket': 'wrong_ticket'
        }),
        'application/json',
    )
    assert response.status_code == 400

    response = django_test.Client().post(
        set_url, json.dumps({
            'old_value': 500,
            'new_value': 500,
            'related_ticket': related_ticket
        }),
        'application/json',
    )
    assert response.status_code == 200
    response = django_test.Client().get(get_url)
    result = json.loads(response.content)
    assert 'comment' not in result
    assert result['related_ticket'] == related_ticket

    response = django_test.Client().post(
        set_url, json.dumps({
            'old_value': 500,
            'new_value': 300,
        }),
        'application/json',
    )
    assert response.status_code == 200
    response = django_test.Client().get(get_url)
    result = json.loads(response.content)
    assert 'ticket' not in result
    assert 'comment' not in result


@pytest.mark.config(
    ADMIN_EDIT_CONFIG_REASON_REQUIRED=True,
    ADMIN_AUDIT_USE_SERVICE=False,
)
@pytest.mark.now('2018-12-12T00:00:00')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_reason_required():
    data = {
        'old_value': True,
        'new_value': False,
    }

    response = django_test.Client().post(
        '/api/config/save/ADMIN_EDIT_CONFIG_REASON_REQUIRED/',
        json.dumps(data),
        'application/json'
    )

    assert response.status_code == 400

    data['reason'] = 'reason'

    response = django_test.Client().post(
        '/api/config/save/ADMIN_EDIT_CONFIG_REASON_REQUIRED/',
        json.dumps(data),
        'application/json'
    )
    assert response.status_code == 200
    log_admin = yield db.log_admin.find_one({'action': 'save_value'})
    log_admin.pop('_id')
    assert log_admin == {
        'action': 'save_value',
        'timestamp': datetime.datetime(2018, 12, 12),
        'login': 'dmkurilov',
        'object_id': 'ADMIN_EDIT_CONFIG_REASON_REQUIRED',
        'arguments': {
            'comment': None,
            'name': 'ADMIN_EDIT_CONFIG_REASON_REQUIRED',
            'old_value': True,
            'value': False,
            'reason': 'reason',
            'related_ticket': None
        }
    }
