from __future__ import unicode_literals

import json

from bson import json_util
from django import test as django_test
import pytest

from taxi.core import async
from taxi.core import db
from taxi.internal import dbh

from taxiadmin import audit
from taxiadmin.api import apiutils


def validate_discount_dict(data):
    assert type(data) is dict
    assert sorted(data.keys()) == ['discounts', 'enabled', 'version', 'zone',
                                   'zone_type']
    assert all(type(discount) is dict for discount in data['discounts'])
    assert type(data['enabled']) == bool
    assert type(data['version']) == int
    assert data['version'] > 0


@pytest.mark.parametrize('zone, code', [
    ('spb', 200),
    ('nnnnnn', 404)
])
@pytest.mark.parametrize('zone_type', [None, 'tariff_zone', 'agglomeration'])
@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb(user_discounts='')
def test_get(zone, code, zone_type):
    client = django_test.Client()
    if zone_type:
        response = client.get(
            '/api/user_discounts/get/{}/?zone_type={}'.format(zone, zone_type))
    else:
        response = client.get('/api/user_discounts/get/{}/'.format(zone))
    assert response.status_code == code, 'Got {}'.format(response.content)
    if code == 200:
        discounts = dbh.user_discounts.Doc.get_one(
            zone, zone_type if zone_type else 'tariff_zone', only_enabled=True)
        assert discounts
        data = json.loads(response.content)
        validate_discount_dict(data)
        assert len(data['discounts']) == 3


@pytest.mark.parametrize('zone, expected', [
    ('spb', True),  # enabled
    ('nnnnnn', False),  # not exists
    ('krasndoar', False)  # disabled
])
@pytest.mark.parametrize('zone_type', ['tariff_zone', 'agglomeration'])
@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb(user_discounts='')
def test_get_one(zone, expected, zone_type):
    result = True
    try:
        dbh.user_discounts.Doc.get_one(zone, zone_type, only_enabled=True)
    except dbh.user_discounts.NotFound:
        result = False
    assert result == expected


@pytest.mark.parametrize('code', [200])
@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb(user_discounts='')
def test_list(code):
    client = django_test.Client()
    response = client.get('/api/user_discounts/list/')
    assert response.status_code == code, 'Got {}'.format(response.content)
    if code == 200:
        data = json.loads(response.content)
        assert type(data) is list
        map(validate_discount_dict, data)


def fetch_doc(zone_name, zone_type):
    doc = db.user_discounts.find(
        {'zone_name': zone_name, 'zone_type': zone_type}).run().result[0]
    for discount in doc['discounts']:
        discount.pop('history')
    doc.pop('_id')
    doc['zone'] = doc.pop('zone_name')
    return doc


def post_json(client, path, data):
    content = json.dumps(data)
    return client.post(path, content, content_type='application/json')


@pytest.fixture(autouse=True)
def no_audit_checks(monkeypatch):
    def fetch_ticket_from_url(value):
        return value

    def check_ticket(ticket, *args, **kwargs):
        if not ticket:
            raise audit.TicketError('Even a fake ticket is not present!')

    def log_action(*args, **kwargs):
        pass

    @async.inline_callbacks
    def check_taxirate(ticket_key, login, check_author=False):
        yield async.return_value()

    monkeypatch.setattr(audit, 'fetch_ticket_from_url', fetch_ticket_from_url)
    monkeypatch.setattr(audit, 'check_ticket', check_ticket)
    monkeypatch.setattr(audit, 'check_taxirate', check_taxirate)


@pytest.fixture
def extract_log(load):
    def _extract_func(filename):
        log = json_util.loads(load(filename))
        log['timestamp'] = log['timestamp'].replace(
            tzinfo=None
        )
        return log
    return _extract_func


@pytest.mark.parametrize('request_data, code, expected, expected_log, expected_history', [
    ({}, 400, {}, None, []),
    (
        {
            "zone": "rnd",
            "enabled": True,
            "discounts": [],
            "ticket": "TAXIRATE-123"
        },
        200,
        {
            "zone": "rnd",
            "zone_type": "tariff_zone",
            "enabled": True,
            "discounts": [],
            "version": 1
        },
        'expected_add_log_1.json',
        []
    ),  # CORRECT
    (
        {
            "zone": "rnd",
            "zone_type": "tariff_zone",
            "enabled": True,
            "discounts": [],
            "ticket": "TAXIRATE-123"
        },
        200,
        {
            "zone": "rnd",
            "zone_type": "tariff_zone",
            "enabled": True,
            "discounts": [],
            "version": 1
        },
        'expected_add_log_1_new_format.json',
        []
    ),  # CORRECT (new format)
    (
        {
            "zone": "rnd",
            "zone_type": "agglomeration",
            "enabled": True,
            "discounts": [],
            "ticket": "TAXIRATE-123"
        },
        200,
        {
            "zone": "rnd",
            "zone_type": "agglomeration",
            "enabled": True,
            "discounts": [],
            "version": 1
        },
        'expected_add_log_1_agglomeration.json',
        []
    ),  # CORRECT (agglomeration)
    (
        {
            "zone": "nnn",
            "enabled": False,
            "discounts": [{
                "id": "000000000000000000000080",
                "num_rides_for_newbies": 10,
                "classes": ["econom"],
                "round_digits": 2,
                "final_min_value": 0.01,
                "for": "selected",
                "calculation_formula_v1_threshold": 450,
                "newbie_max_coeff": 1.5,
                "final_max_value": 0.99,
                "max_value": 0.4,
                "current_method": "full-driver-less",
                "enabled": True,
                "min_value": 0.01,
                "random_p": 0,
                "random_time_threshold": 5,
                "random_s": 0,
                "calculation_method": "formula",
                "calculation_formula_v1_p1": 10,
                "calculation_formula_v1_p2": 1,
                "calculation_formula_v1_a2": 5040,
                "calculation_formula_v1_a1": 3000,
                "calculation_formula_v1_c1": 50,
                "calculation_formula_v1_c2": 60,
                "newbie_num_coeff": 0.15,
                "payment_types": [
                    "card",
                    "applepay",
                    "googlepay",
                    "coop_account"
                ]},
            ],
            "ticket": "TAXIRATE-334"
        },
        200,
        {
            "zone": "nnn",
            "zone_type": "tariff_zone",
            "enabled": False,
            "discounts": [{
                "id": "000000000000000000000080",
                "num_rides_for_newbies": 10,
                "classes": ["econom"],
                "round_digits": 2,
                "final_min_value": 0.01,
                "for": "selected",
                "calculation_formula_v1_threshold": 450,
                "newbie_max_coeff": 1.5,
                "final_max_value": 0.99,
                "max_value": 0.4,
                "current_method": "full-driver-less",
                "enabled": True,
                "min_value": 0.01,
                "random_p": 0,
                "random_time_threshold": 5,
                "random_s": 0,
                "calculation_method": "formula",
                "calculation_formula_v1_p1": 10,
                "calculation_formula_v1_p2": 1,
                "calculation_formula_v1_a2": 5040,
                "calculation_formula_v1_a1": 3000,
                "calculation_formula_v1_c1": 50,
                "calculation_formula_v1_c2": 60,
                "newbie_num_coeff": 0.15,
                "payment_types": [
                    "card",
                    "applepay",
                    "googlepay",
                    "coop_account"
                ]}
            ],
            "version": 1
        },
        'expected_add_log_2.json',
        [{
            'id': '000000000000000000000080',
            'history': [{
                'login': 'dmkurilov',
                'ticket': 'TAXIRATE-334',
                'updated': '2018-10-24T03:00:00+0300'
            }]
        }]
    ),  # FULL
    ({
        "zone": "rnd",
        "enabled": True,
        "discounts": []
    }, 400, {}, None, []),  # TICKET NOT SPECIFIED
    ({
        "zone": "aaa",
        "enabled": True,
        "discounts": [],
        "ticket": []
    }, 400, {}, None, []),  # TICKET ERROR
    ({
        "zone": "aaa",
        "enabled": {},
        "discounts": [],
        "ticket": "TAXI-111"
    }, 400, {}, None, []),  # VALIDATION ERROR
    ({
            "zone": "spb",
            "enabled": True,
            "discounts": [],
            "ticket": "TAXIRATE-123"
     }, 409, {}, None, []),  # ALREADY EXISTS
])
@pytest.mark.config(
    ADMIN_AUDIT_USE_SERVICE=False,
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb(user_discounts='')
@pytest.mark.now('2018-10-24 00:00:00')
@pytest.inline_callbacks
def test_add(request_data, code, expected, expected_log, expected_history, extract_log):
    client = django_test.Client()
    response = post_json(client, '/api/user_discounts/add/', request_data)
    assert response.status_code == code, 'Got {}'.format(response.content)
    if code == 200:
        response_data = json.loads(response.content)
        request_zone = request_data.get('zone_name', request_data.get('zone'))
        request_zone_type = request_data.get('zone_type', 'tariff_zone')
        assert response_data['zone'] == request_zone
        assert response_data['zone_type'] == request_zone_type
        doc = fetch_doc(request_zone, request_zone_type)
        assert doc == response_data
        assert response_data == expected
        log_admin = yield db.log_admin.find_one(
            {'action': 'add_user_discounts'}
        )
        log_admin.pop('_id')
        assert log_admin == extract_log(expected_log)
        _assert_history(client, expected_history)


def _assert_history(client, expected):
    for expected_info in expected:
        request_data = {
            'discount_id': expected_info['id']
        }
        response = post_json(client, '/api/user_discounts/discount_history/', request_data)
        assert response.status_code == 200
        assert json.loads(response.content) == expected_info['history']


@pytest.mark.parametrize('request_data, zone, code, expected, expected_log, expected_history', [
    ({}, 'spb', 400, {}, None, []),
    (
        {
            "enabled": True,
            "discounts": [],
            "version": 1,
            "ticket": "TAXIRATE-123"
        },
        'spb',
        200,
        {
            "zone": "spb",
            "zone_type": "tariff_zone",
            "enabled": True,
            "discounts": [],
            "version": 2
        },
        'expected_update_log_1.json',
        []
    ),  # CORRECT
    (
        {
            "zone": "spb",
            "zone_type": "tariff_zone",
            "enabled": True,
            "discounts": [],
            "version": 1,
            "ticket": "TAXIRATE-123"
        },
        'spb',
        200,
        {
            "zone": "spb",
            "zone_type": "tariff_zone",
            "enabled": True,
            "discounts": [],
            "version": 2
        },
        'expected_update_log_1_new_format.json',
        []
    ),  # CORRECT (new format)
    (
        {
            "zone": "spb",
            "zone_type": "agglomeration",
            "enabled": True,
            "discounts": [],
            "version": 4,
            "ticket": "TAXIRATE-123"
        },
        'spb',
        200,
        {
            "zone": "spb",
            "zone_type": "agglomeration",
            "enabled": True,
            "discounts": [],
            "version": 5
        },
        'expected_update_log_1_agglomeration.json',
        []
    ),  # CORRECT (agglomeration)
    ({
        "enabled": True,
        "discounts": [],
        "version": 1,
        "ticket": "TAXIRATE-123",
        "confirmation_id": "booyaka"
    }, 'spb', 400, {}, None, []),  # VALIDATION ERROR
    (
        {
            "enabled": False,
            "discounts": [{
                "id": "000000000000000000000001",
                "num_rides_for_newbies": 10,
                "classes": ["econom"],
                "round_digits": 2,
                "final_min_value": 0.01,
                "for": "selected",
                "calculation_formula_v1_threshold": 450,
                "newbie_max_coeff": 1.5,
                "final_max_value": 0.99,
                "max_value": 0.4,
                "current_method": "full-driver-less",
                "enabled": True,
                "min_value": 0.01,
                "random_p": 0,
                "random_time_threshold": 5,
                "random_s": 0,
                "calculation_method": "formula",
                "calculation_formula_v1_p1": 10,
                "calculation_formula_v1_p2": 1,
                "calculation_formula_v1_a2": 5040,
                "calculation_formula_v1_a1": 3000,
                "calculation_formula_v1_c1": 50,
                "calculation_formula_v1_c2": 60,
                "newbie_num_coeff": 0.15,
                "payment_types": [
                    "card",
                    "applepay",
                    "googlepay"
                ],
                "count_daily_budget": True,
                "daily_budget": 10000}
            ],
            "ticket": "TAXIRATE-334",
            "version": 1
        },
        'spb',
        200,
        {
            "zone": "spb",
            "zone_type": "tariff_zone",
            "enabled": False,
            "discounts": [{
                "id": "000000000000000000000001",
                "num_rides_for_newbies": 10,
                "classes": ["econom"],
                "round_digits": 2,
                "final_min_value": 0.01,
                "for": "selected",
                "calculation_formula_v1_threshold": 450,
                "newbie_max_coeff": 1.5,
                "final_max_value": 0.99,
                "max_value": 0.4,
                "current_method": "full-driver-less",
                "enabled": True,
                "min_value": 0.01,
                "random_p": 0,
                "random_time_threshold": 5,
                "random_s": 0,
                "calculation_method": "formula",
                "calculation_formula_v1_p1": 10,
                "calculation_formula_v1_p2": 1,
                "calculation_formula_v1_a2": 5040,
                "calculation_formula_v1_a1": 3000,
                "calculation_formula_v1_c1": 50,
                "calculation_formula_v1_c2": 60,
                "newbie_num_coeff": 0.15,
                "payment_types": [
                    "card",
                    "applepay",
                    "googlepay"
                ],
                "count_daily_budget": True,
                "daily_budget": 10000}
            ],
            "version": 2
        },
        'expected_update_log_2.json',
        [{
            'id': '000000000000000000000001',
            'history': [{
                'login': 'karachevda',
                'ticket': 'TAXIRATE-007',
                'updated': '2017-10-24T03:00:00+0300'
            }, {
                'login': 'karachevda',
                'ticket': 'TAXIRATE-008',
                'updated': '2017-10-24T03:00:01+0300'
            }, {
                'login': 'karachevda',
                'ticket': 'TAXIRATE-009',
                'updated': '2017-10-24T03:00:02+0300'
            }, {
                'login': 'dmkurilov',
                'ticket': 'TAXIRATE-334',
                'updated': '2018-10-24T03:00:00+0300'
            }]
        }]
    ),  # FULL
    ({
        "enabled": True,
        "discounts": [],
        "version": 1
    }, 'spb', 400, {}, None, []),  # TICKET NOT SPECIFIED
    ({
         "enabled": True,
         "discounts": [],
         "ticket": [],
         "version": 1
    }, 'spb', 400, {}, None, []),  # TICKET ERROR
    ({
        "enabled": {},
        "discounts": [],
        "ticket": "TAXI-111"
    }, 'aaa', 400, {}, None, []),  # VALIDATION ERROR
    ({
        "enabled": True,
        "discounts": [],
        "ticket": "TAXI-123",
        "version": 1
    }, 'rnd', 404, {}, None, []),  # NOT FOUND
    ({
        "enabled": True,
        "discounts": [],
        "ticket": "TAXI-123",
        "version": 17
    }, 'spb', 409, {}, None, []),  # WRONG VERSION
    (
        {
            "enabled": True,
            "discounts": [],
            "ticket": "TAXI-123",
            "version": 1
        },
        'spb',
        200,
        {
            "zone": "spb",
            "zone_type": "tariff_zone",
            "enabled": True,
            "discounts": [],
            "version": 2
        },
        'expected_update_log_3.json',
        []
    ),  # SAME, BUT CORRECT VERSION
])
@pytest.mark.config(
    ADMIN_AUDIT_USE_SERVICE=False,
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb(user_discounts='')
@pytest.mark.now('2018-10-24 00:00:00')
@pytest.inline_callbacks
def test_update(
        request_data, zone, code, expected, expected_log, expected_history, extract_log,
):
    client = django_test.Client()
    response = post_json(client, '/api/user_discounts/update/{}/'.format(zone),
                         request_data)
    assert response.status_code == code, 'Got {}'.format(response.content)
    if code == 200:
        response_data = json.loads(response.content)
        request_zone = request_data.get('zone_name', zone)
        request_zone_type = request_data.get('zone_type', 'tariff_zone')
        doc = fetch_doc(request_zone, request_zone_type)
        assert doc == response_data
        assert response_data == expected
        log_admin = yield db.log_admin.find_one(
            {'action': 'update_user_discounts'}
        )
        log_admin.pop('_id')
        assert log_admin == extract_log(expected_log)
        _assert_history(client, expected_history)


OK = {'status': 'ok'}


def fetch_all_docs():
    doc = db.user_discounts.find().run().result
    return doc


@pytest.mark.parametrize('request_data, zone, code, expected, expected_log', [
    ({}, 'spb', 400, {}, None),
    (
        {
            'ticket': 'TAXIRATE-123',
            'version': 1
        },
        'spb',
        200,
        OK,
        'expected_delete_log.json'
    ),  # OK
    (
        {
            "zone": "spb",
            "zone_type": "tariff_zone",
            'ticket': 'TAXIRATE-123',
            'version': 1
        },
        'spb',
        200,
        OK,
        'expected_delete_log_new_format.json'
    ),  # OK (new format)
    (
        {
            "zone": "spb",
            "zone_type": "agglomeration",
            'ticket': 'TAXIRATE-123',
            'version': 4
        },
        'spb',
        200,
        OK,
        'expected_delete_log_agglomeration.json'
    ),  # OK (agglomeration)
    ({
        'ticket': 'TAXIRATE-123',
        'version': 1
    }, 'rnd', 404, OK, None),  # NOT FOUND
    ({
        'ticket': 'TAXIRATE-123',
        'version': 17
    }, 'spb', 409, {}, None),  # WRONG VERSION
    ({
        'version': 1
    }, 'spb', 400, {}, None),  # TICKET NOT SPECIFIED
    ({
         'version': 1,
         'ticket': []
    }, 'spb', 400, {}, None),  # TICKET ERROR
    ({
        'ticket': 'TAXIRATE-123',
        'version': "3"
    }, 'spb', 400, OK, None),  # VALIDATION ERROR
])
@pytest.mark.config(
    ADMIN_AUDIT_USE_SERVICE=False,
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb(user_discounts='')
@pytest.mark.now('2018-10-24 00:00:00')
@pytest.inline_callbacks
def test_delete(
        request_data, zone, code, expected, expected_log, extract_log,
):
    all_docs_before = fetch_all_docs()
    client = django_test.Client()
    response = post_json(client, '/api/user_discounts/delete/{}/'.format(zone),
                         request_data)
    assert response.status_code == code, 'Got {}'.format(response.content)
    if code == 200:
        all_docs_after = fetch_all_docs()
        assert len(all_docs_before) - 1 == len(all_docs_after)
        zone_type = request_data.get('zone_type', 'tariff_zone')
        assert any(d['zone_name'] == zone and d['zone_type'] == zone_type
                   for d in all_docs_before)
        assert not any(d['zone_name'] == zone and d['zone_type'] == zone_type
                       for d in all_docs_after)
        log_admin = yield db.log_admin.find_one(
            {'action': 'delete_user_discounts'}
        )
        log_admin.pop('_id')
        assert log_admin == extract_log(expected_log)


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('zone_name, bins', [
    ('filled-list', '123456\n234567'),
    ('empty-list', ''),
    ('none', None)
])
@pytest.mark.filldb(user_discounts='bin_filter')
def test_bin_filter_discount_get(zone_name, bins):
    client = django_test.Client()
    response = client.get('/api/user_discounts/get/{}/'.format(zone_name))
    assert response.status_code == 200, 'Got {}'.format(response.content)
    data = json.loads(response.content)
    assert len(data['discounts']) == 1
    discount = data['discounts'][0]
    if bins is None:
        assert 'bin_filter' not in discount
    else:
        assert discount['bin_filter'] == bins


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('bins_provided, expected_code, bins_saved', [
    (None, 200, None),
    ('123456', 200, [123456]),
    ('123456\n', 200, [123456]),
    ('123456 \n    ', 200, [123456]),
    ('123456\n\n\n234567', 200, [123456, 234567]),
    ('012345', 200, [12345]),
    ('12345', 406, None)
])
def test_bin_filter_discounts_put(bins_provided, expected_code, bins_saved):
    request = {
        "zone": "nnn",
        "enabled": False,
        "discounts": [{
            "id": "a122c228ba2b4d3189971a430ca6d2d3",
            "num_rides_for_newbies": 10,
            "classes": ["econom"],
            "round_digits": 2,
            "final_min_value": 0.01,
            "for": "selected",
            "calculation_formula_v1_threshold": 450,
            "newbie_max_coeff": 1.5,
            "final_max_value": 0.99,
            "max_value": 0.4,
            "current_method": "full-driver-less",
            "enabled": True,
            "min_value": 0.01,
            "random_p": 0,
            "random_time_threshold": 5,
            "random_s": 0,
            "calculation_method": "formula",
            "calculation_formula_v1_p1": 10,
            "calculation_formula_v1_p2": 1,
            "calculation_formula_v1_a2": 5040,
            "calculation_formula_v1_a1": 3000,
            "calculation_formula_v1_c1": 50,
            "calculation_formula_v1_c2": 60,
            "newbie_num_coeff": 0.15,
            "payment_types": [
              "card",
              "applepay",
              "googlepay"
            ]}
        ],
        "ticket": "TAXIRATE-334"
    }
    request['discounts'][0]['bin_filter'] = bins_provided
    client = django_test.Client()
    response = post_json(client, '/api/user_discounts/add/', request)
    assert response.status_code == expected_code, 'Got {}'.format(
        response.content
    )
    if expected_code == 200:
        response_data = json.loads(response.content)
        assert response_data['zone'] == request['zone']
        zone = request['zone']
        doc = dbh.user_discounts.Doc(fetch_doc(zone, 'tariff_zone'))
        discount = doc.discounts[0]
        if bins_saved is None:
            assert 'bin_filter' not in discount
        else:
            assert discount.bin_filter == bins_saved


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('zone_name, keys', [
    (
        'filled',
        {
            "card_title": "card_title",
            "card_subtitle": "card_subtitle",
            "payment_method_subtitle": "payment_method_subtitle"
        }
    ),
    (
        'none',
        None
    )
])
@pytest.mark.filldb(user_discounts='branding_keys')
def test_branding_keys_discount_get(zone_name, keys):
    client = django_test.Client()
    response = client.get('/api/user_discounts/get/{}/'.format(zone_name))
    assert response.status_code == 200, 'Got {}'.format(response.content)
    data = json.loads(response.content)
    assert len(data['discounts']) == 1
    discount = data['discounts'][0]
    if keys is None:
        assert 'branding_keys' not in discount
    else:
        assert discount['branding_keys'] == keys


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('branding_keys, expected_code, keys_saved', [
    (
        {
            "card_title": "card_title1",
            "card_subtitle": "card_subtitle1",
            "payment_method_subtitle": "payment_method_subtitle1"
        },
        200,
        {
            "card_title": "card_title1",
            "card_subtitle": "card_subtitle1",
            "payment_method_subtitle": "payment_method_subtitle1"
        }
    ),
    (
        {
            "card_title": "card_title1",
            "payment_method_subtitle": "payment_method_subtitle1"
        },
        200,
        {
            "card_title": "card_title1",
            "payment_method_subtitle": "payment_method_subtitle1"
        }
    ),
    (
        {
            "card_title": "card_title2",
            "card_subtitle": "card_subtitle2",
            "payment_method_subtitle": "payment_method_subtitle2"
        },
        406,
        None
    )
])
@pytest.mark.translations([
    (
        'client_messages',
        'card_title1',
        'ru',
        'card_title1'
    ),
    (
        'client_messages',
        'card_subtitle1',
        'ru',
        'card_subtitle1'
    ),
    (
        'client_messages',
        'payment_method_subtitle1',
        'ru',
        'payment_method_subtitle1'
    ),
    (
        'client_messages',
        'card_title2',
        'ru',
        'card_title2'
    )

])
def test_branding_keys_discounts_put(branding_keys, expected_code, keys_saved):
    request = {
        "zone": "nnn",
        "enabled": False,
        "discounts": [{
            "id": "a122c228ba2b4d3189971a430ca6d2d3",
            "num_rides_for_newbies": 10,
            "classes": ["econom"],
            "round_digits": 2,
            "final_min_value": 0.01,
            "for": "selected",
            "calculation_formula_v1_threshold": 450,
            "newbie_max_coeff": 1.5,
            "final_max_value": 0.99,
            "max_value": 0.4,
            "current_method": "full-driver-less",
            "enabled": True,
            "min_value": 0.01,
            "random_p": 0,
            "random_time_threshold": 5,
            "random_s": 0,
            "calculation_method": "formula",
            "calculation_formula_v1_p1": 10,
            "calculation_formula_v1_p2": 1,
            "calculation_formula_v1_a2": 5040,
            "calculation_formula_v1_a1": 3000,
            "calculation_formula_v1_c1": 50,
            "calculation_formula_v1_c2": 60,
            "newbie_num_coeff": 0.15,
            "payment_types": [
              "card",
              "applepay",
              "googlepay"
            ]}
        ],
        "ticket": "TAXIRATE-334"
    }
    request['discounts'][0]['branding_keys'] = branding_keys
    client = django_test.Client()
    response = post_json(client, '/api/user_discounts/add/', request)
    assert response.status_code == expected_code, 'Got {}'.format(
        response.content
    )
    if expected_code == 200:
        response_data = json.loads(response.content)
        assert response_data['zone'] == request['zone']
        zone = request['zone']
        doc = dbh.user_discounts.Doc(fetch_doc(zone, 'tariff_zone'))
        discount = doc.discounts[0]
        if keys_saved is None:
            assert 'branding_keys' not in discount
        else:
            assert discount.branding_keys == keys_saved


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('target', [
    'newbie_googlepay',
    'newbie_applepay',
])
def test_discount_targets(target):
    request = {
        "zone": "nnn",
        "enabled": False,
        "discounts": [{
            "id": "a122c228ba2b4d3189971a430ca6d2d3",
            "num_rides_for_newbies": 10,
            "classes": ["econom"],
            "round_digits": 2,
            "final_min_value": 0.01,
            "for": target,
            "calculation_formula_v1_threshold": 450,
            "newbie_max_coeff": 1.5,
            "final_max_value": 0.99,
            "max_value": 0.4,
            "current_method": "full-driver-less",
            "enabled": True,
            "min_value": 0.01,
            "random_p": 0,
            "random_time_threshold": 5,
            "random_s": 0,
            "calculation_method": "formula",
            "calculation_formula_v1_p1": 10,
            "calculation_formula_v1_p2": 1,
            "calculation_formula_v1_a2": 5040,
            "calculation_formula_v1_a1": 3000,
            "calculation_formula_v1_c1": 50,
            "calculation_formula_v1_c2": 60,
            "newbie_num_coeff": 0.15,
            "payment_types": [
                "card",
                "applepay",
                "googlepay"
            ]}
        ],
        "ticket": "TAXIRATE-334"
    }
    client = django_test.Client()
    response = post_json(client, '/api/user_discounts/add/', request)
    assert response.status_code == 200, 'Got {}'.format(
        response.content
    )
    response_data = json.loads(response.content)
    assert response_data['discounts'][0]['for'] == target
    zone = request['zone']
    doc = dbh.user_discounts.Doc(fetch_doc(zone, 'tariff_zone'))
    discount = doc.discounts[0]
    assert discount['for'] == target
    client = django_test.Client()
    response = client.get('/api/user_discounts/get/{}/'.format(zone))
    assert response.status_code == 200, 'Got {}'.format(response.content)
    data = json.loads(response.content)
    assert data['discounts'][0]['for'] == target


@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('calculation_method, formula_fields, table_fields,'
                         ' expected_code', [
    (
        None,
        {},
        [],
        406
    ),  # no calc method - no fields - not OK
    (
        "formula",
        {
            "calculation_formula_v1_a1": 1,
            "calculation_formula_v1_a2": 2,
            "calculation_formula_v1_p1": 3,
            "calculation_formula_v1_p2": 4,
            "calculation_formula_v1_c1": 5,
            "calculation_formula_v1_c2": 6,
            "calculation_formula_v1_threshold": 7,
        },
        [],
        200
    ),  # formula method - actual fields - OK
    (
        "formula",
        {},
        [],
        406
    ),  # formula method - no fields - not OK
    (
        "formula",
        {
            "formula_v1_a1": 1,
            "formula_v1_a2": 2,
            "formula_v1_p1": 3,
            "formula_v1_p2": 4,
            "formula_v1_c1": 5,
            "formula_v1_c2": 6,
            "formula_v1_threshold": 7,
        },
        [],
        400
    ),  # formula method - obsolete fields - not OK
    (
        "formula",
        {
            "calculation_formula_v1_a1": 1,
            "calculation_formula_v1_a2": 2,
            "calculation_formula_v1_p1": 3,
            "calculation_formula_v1_p2": 4,
            "calculation_formula_v1_c2": 6,
            "calculation_formula_v1_threshold": 7
        },
        [],
        406
    ),  # formula method - actual fields - c1 missing
    (
        "formula",
        {
            "calculation_formula_v1_a1": 1,
            "calculation_formula_v1_a2": 2,
            "calculation_formula_v1_p1": 3,
            "whatever": 4,
            "calculation_formula_v1_c1": 5,
            "calculation_formula_v1_c2": 6,
            "calculation_formula_v1_threshold": 7
        },
        [],
        400
    ),  # formula method - actual fields - p2 misspell
    (
        "table",
        {},
        [
            {
                "cost": 1,
                "discount": 2
            },
            {
                "cost": 3,
                "discount": 4
            }
        ],
        200
    ),  # table method - actual rows - OK
    (
        "table",
        {},
        [],
        406
    ),  # table method - no table
    (
        "table",
        {},
        [
            {
                "tsena": 1,
                "discount": 2
            },
            {
                "cost": 1,
                "skidka": 2
            }
        ],
        400
    )  # table method - rows misspell
])
def test_calculation_params(calculation_method, formula_fields, table_fields,
                            expected_code):
    request = {
        "zone": "nnn",
        "enabled": False,
        "discounts": [{
            "id": "a122c228ba2b4d3189971a430ca6d2d3",
            "num_rides_for_newbies": 10,
            "classes": ["econom"],
            "round_digits": 2,
            "final_min_value": 0.01,
            "for": "all",
            "newbie_max_coeff": 1.5,
            "final_max_value": 0.99,
            "max_value": 0.4,
            "current_method": "full-driver-less",
            "enabled": True,
            "min_value": 0.01,
            "random_p": 0,
            "random_time_threshold": 5,
            "random_s": 0,
            "newbie_num_coeff": 0.15,
            "payment_types": [
                "card",
                "applepay",
                "googlepay"
            ]}
        ],
        "ticket": "TAXIRATE-334"
    }
    if calculation_method:
        request['discounts'][0]["calculation_method"] = calculation_method
    if formula_fields:
        request['discounts'][0].update(formula_fields)
    if table_fields:
        request['discounts'][0]["calculation_table"] = table_fields

    client = django_test.Client()
    response = post_json(client, '/api/user_discounts/add/', request)
    assert response.status_code == expected_code, 'Got {}'.format(
        response.content
    )


@pytest.mark.parametrize('request_data, expected_code, expected_response', [
    (
        {
            'discount_id': '000000000000000000000001'
        },
        200,
        [
            {
                'login': 'karachevda',
                'ticket': 'TAXIRATE-007',
                'updated': '2017-10-24T03:00:00+0300'
            }, {
                'login': 'karachevda',
                'ticket': 'TAXIRATE-008',
                'updated': '2017-10-24T03:00:01+0300'
            }
        ]
    ),
    (
        {
            'discount_id': 'not_existed'
        },
        404,
        None
    ),
    (
        {
            'discount_id': '000000000000000000000001',
            'offset': None,
            'limit': None
        },
        400,
        None
    ),
    (
        {
            'discount_id': '000000000000000000000001',
            'offset': 2,
            'limit': 5
        },
        200,
        [
            {
                'login': 'karachevda',
                'ticket': 'TAXIRATE-009',
                'updated': '2017-10-24T03:00:02+0300'
            }
        ]
    ),
    (
        {
            'discount_id': '000000000000000000000004'
        },
        200,
        []
    )
])
@pytest.mark.asyncenv('blocking')
def test_discount_history(monkeypatch, request_data, expected_code, expected_response):
    monkeypatch.setattr(apiutils, 'DEFAULT_LIMIT', 2)
    client = django_test.Client()
    response = post_json(client, '/api/user_discounts/discount_history/', request_data)

    assert response.status_code == expected_code
    if expected_code == 200:
        assert json.loads(response.content) == expected_response


@pytest.mark.asyncenv('blocking')
def test_approvals_check(patch, load):

    @patch('taxi.external.tvm.check_ticket')
    def check_ticket(dst_service_name, ticket_body, log_extra=None):
        return True

    client = django_test.Client()
    request_data = load('approvals_check_request_data.json')
    expected_response = json.loads(
        load('approvals_check_expected_response.json'),
    )
    response = client.post(
        '/api/approvals/user_discounts_create/check/',
        request_data,
        'application/json',
        HTTP_X_YATAXI_TICKET='TAXIRATE-35',
        HTTP_X_YANDEX_LOGIN='ydemidenko',
        HTTP_X_YA_SERVICE_TICKET='tvm_ticket',
    )
    assert response.status_code == 200
    assert json.loads(response.content) == expected_response


@pytest.mark.asyncenv('blocking')
def test_approvals_apply(patch, load):

    @patch('taxi.external.tvm.check_ticket')
    def check_ticket(dst_service_name, ticket_body, log_extra=None):
        return True

    client = django_test.Client()
    request_data = load('approvals_apply_request_data.json')
    response = client.post(
        '/api/approvals/user_discounts_create/apply/',
        request_data,
        'application/json',
        HTTP_X_YATAXI_TICKET='TAXIRATE-35',
        HTTP_X_YANDEX_LOGIN='ydemidenko',
        HTTP_X_YA_SERVICE_TICKET='tvm_ticket',
    )
    assert response.status_code == 200
    assert json.loads(response.content) == {}


@pytest.mark.config(
    ALL_APPLICATIONS=[
        'android',
        'uber_by_android',
        'uber_iphone'
    ],
    APPLICATION_MAP_DISCOUNTS={
        'uber_by_android': 'uber_android'
    }
)
@pytest.mark.parametrize('expected_items', [
    (
        [
                {'value': 'android'},
                {'value': 'uber_android'},
                {'value': 'uber_iphone'}
        ]
    )
])
@pytest.mark.asyncenv('blocking')
def test_application_platforms(expected_items):
    client = django_test.Client()
    response = client.get(
        '/api/user_discounts/application_platforms/'
    )
    assert response.status_code == 200
    data = json.loads(response.content)
    items = data['items']
    assert (
        sorted(items, key=lambda x: x['value']) ==
        sorted(expected_items, key=lambda x: x['value'])
    )
