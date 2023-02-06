# coding=utf-8
from __future__ import unicode_literals

import datetime
import json

from django import test as django_test
import pytest

from taxi import config
from taxi.core import async
from taxi.core import db
from taxi.external import antifraud


_NOW = datetime.datetime(2018, 5, 28, 12, 13, 14)


@pytest.mark.parametrize('mongo_fixture,request_data,expected_status_code,'
                         'expected_mongo', [
    (
        [],
        {
            'ticket': 'TAXISECTEAM-1',
            'rule': {
                'id': '1', 'type_id': 0,
                'src': 'function on_check_orders(){return true;}',
                'additional_params': {'windows': [7]},
                'description': 'a', 'reason_message': 'b',
            },
        },
        200,
        [
            {
                '_id': '1', 'type_id': 0,
                'src': 'function on_check_orders(){return true;}',
                'additional_params': {'windows': [7]},
                'description': 'a', 'reason_message': 'b',
                'enabled': False, 'test': True, 'debug': False,
                'priority': 0,
                'created': _NOW,
                'updated': _NOW,
            },
        ],
    ),
    (
            [],
            {
                'ticket': 'TAXISECTEAM-1',
                'rule': {
                    'id': '1', 'type_id': 0,
                    'src': 'function on_check_orders(){return true;}',
                    'description': 'a', 'reason_message': 'b',
                },
            },
            200,
            [
                {
                    '_id': '1', 'type_id': 0,
                    'src': 'function on_check_orders(){return true;}',
                    'additional_params': {},
                    'description': 'a', 'reason_message': 'b',
                    'enabled': False, 'test': True, 'debug': False,
                    'priority': 0,
                    'created': _NOW,
                    'updated': _NOW,
                },
            ],
    ),
    (
        [],
        {
            'ticket': 'TAXISECTEAM-1',
            'rule': {
                'id': '1', 'type_id': 1,
                'src': 'function on_check_orders(){return true;}',
                'description': 'a', 'reason_message': 'b',
            },
        },
        200,
        [
            {
                '_id': '1', 'type_id': 1,
                'src': 'function on_check_orders(){return true;}',
                'additional_params': {},
                'description': 'a', 'reason_message': 'b',
                'enabled': False, 'test': True, 'debug': False,
                'priority': 0,
                'created': _NOW,
                'updated': _NOW,
            },
        ],
    ),
    (
        [],
        {
            'ticket': 'TAXISECTEAM-1',
            'rule': {
                'id': '1', 'type_id': 1,
                'src': 'function on_check_orders(){return true;}',
                'description': 'a', 'reason_message': 'b',
                'required_entity_lists_ids': ['3'],
            },
        },
        200,
        [
            {
                '_id': '1', 'type_id': 1,
                'src': 'function on_check_orders(){return true;}',
                'additional_params': {},
                'description': 'a', 'reason_message': 'b',
                'required_entity_lists_ids': ['3'],
                'enabled': False, 'test': True, 'debug': False,
                'priority': 0,
                'created': _NOW,
                'updated': _NOW,
            },
        ],
    ),
    (
        [],
        {
            'ticket': 'TAXISECTEAM-1',
            'rule': {
                'id': '1', 'type_id': 1,
                'src': 'function on_check_orders(){return true;}',
                'description': 'a', 'reason_message': 'b',
                'required_entities_names': ['3'],
            },
        },
        200,
        [
            {
                '_id': '1', 'type_id': 1,
                'src': 'function on_check_orders(){return true;}',
                'additional_params': {},
                'description': 'a', 'reason_message': 'b',
                'required_entities_names': ['3'],
                'enabled': False, 'test': True, 'debug': False,
                'priority': 0,
                'created': _NOW,
                'updated': _NOW,
            },
        ],
    ),
    (
        [],
        {
            'ticket': 'TAXIBACKEND-1',
            'rule': {
                'id': '1', 'type_id': 1,
                'src': 'function on_check_orders(){return true;}',
                'description': 'a', 'reason_message': 'b',
            },
        },
        400,
        [],
    ),
    (
        [],
        {
            'ticket': 'TAXISECTEAM-1',
            'rule': {
                'id': '1', 'type_id': 1,
                'src': 'function on_check_orders(){return true;}',
                'description': 'a', 'reason_message': 'b',
                'required_entity_lists_ids': ['4'],
            },
        },
        400,
        [],
    ),
    (
        [],
        {
            'ticket': 'TAXISECTEAM-1',
            'rule': {
                'id': '1', 'type_id': 1,
                'src': 'function on_check_orders(){return true;}',
                'description': 'a', 'reason_message': 'b',
                'required_entities_names': ['4'],
            },
        },
        400,
        [],
    ),
    (
        [],
        {
            'ticket': 'TAXISECTEAM-1',
            'rule': {
                'id': '1', 'type_id': 1,
                'src': 'function on_check_orders(){return true;}',
                'description': 'a', 'reason_message': 'b',
                'required_entity_lists_ids': ['3', '3'],
            },
        },
        400,
        [],
    ),
    (
        [],
        {
            'ticket': 'TAXISECTEAM-1',
            'rule': {
                'id': '1', 'type_id': 1,
                'src': 'function on_check_orders(){return true;}',
                'description': 'a', 'reason_message': 'b',
                'required_entities_names': ['3', '3'],
            },
        },
        400,
        [],
    ),
    (
        [
            {
                '_id': '1', 'type_id': 0,
                'src': 'function on_check_orders(){return true;}',
                'additional_params': {'windows': [7]},
                'description': 'a', 'reason_message': 'b',
                'enabled': False, 'test': True, 'debug': False,
                'priority': 0,
                'created': _NOW,
                'updated': _NOW,
            },
        ],
        {
            'ticket': 'TAXISECTEAM-1',
            'rule': {
                'id': '1', 'type_id': 0,
                'src': 'function on_check_orders(){return true;}',
                'additional_params': {'windows': [7]},
                'description': 'a', 'reason_message': 'b',
            },
        },
        409,
        [
            {
                '_id': '1', 'type_id': 0,
                'src': 'function on_check_orders(){return true;}',
                'additional_params': {'windows': [7]},
                'description': 'a', 'reason_message': 'b',
                'enabled': False, 'test': True, 'debug': False,
                'priority': 0,
                'created': _NOW,
                'updated': _NOW,
            },
        ],
    ),
])
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(antifraud_entity_list='main', antifraud_entity_map='main')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_rules_add(patch, mongo_fixture, request_data, expected_status_code,
                   expected_mongo):
    @patch('taxi.external.startrack.get_ticket_info')
    @async.inline_callbacks
    def get_ticket_info(ticket):
        assert ticket == 'TAXISECTEAM-1'
        yield async.return_value()

    yield _setup_mongo(mongo_fixture)

    test_client = django_test.Client()
    response = test_client.post(
        '/api/antifraud/rules/add/',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    assert response.status_code == expected_status_code
    assert len(get_ticket_info.calls) == int(
        request_data['ticket'] == 'TAXISECTEAM-1'
    )
    yield _check_rules_in_mongo(expected_mongo)


@pytest.mark.parametrize('mongo_fixture,expected_response_data', [
    (
        [
            {
                '_id': '3', 'type_id': 0,
                'src': 'function on_check_orders(){return true;}',
                'additional_params': {'windows': [15]},
                'description': 'e', 'reason_message': 'f',
                'enabled': False, 'test': False, 'debug': False,
                'priority': 2,
                'created': _NOW,
                'updated': _NOW,
            },
            {
                '_id': '1', 'type_id': 0,
                'src': 'function on_check_orders(){return true;}',
                'additional_params': {'windows': [1]},
                'description': 'a', 'reason_message': 'b',
                'enabled': False, 'test': True, 'debug': False,
                'priority': 0,
                'created': _NOW,
                'updated': _NOW,
            },
            {
                '_id': '4', 'type_id': 1,
                'src': 'function on_check_orders(){return false;}',
                'additional_params': {},
                'description': 'g', 'reason_message': 'h',
                'enabled': True, 'test': True, 'debug': True,
                'priority': 3,
                'created': _NOW,
                'updated': _NOW,
            },
            {
                '_id': '2', 'type_id': 1,
                'src': 'function on_check_orders(){return false;}',
                'additional_params': {},
                'description': 'c', 'reason_message': 'd',
                'enabled': True, 'test': False, 'debug': True,
                'priority': 1,
                'created': _NOW,
                'updated': _NOW,
            },
        ],
        {
            'rules': [
                {
                    'id': '1', 'type_id': 0,
                    'src': 'function on_check_orders(){return true;}',
                    'additional_params': {'windows': [1]},
                    'description': 'a', 'reason_message': 'b',
                    'enabled': False, 'test': True, 'debug': False,
                    'priority': 0,
                },
                {
                    'id': '2', 'type_id': 1,
                    'src': 'function on_check_orders(){return false;}',
                    'additional_params': {},
                    'description': 'c', 'reason_message': 'd',
                    'enabled': True, 'test': False, 'debug': True,
                    'priority': 1,
                },
                {
                    'id': '3', 'type_id': 0,
                    'src': 'function on_check_orders(){return true;}',
                    'additional_params': {'windows': [15]},
                    'description': 'e', 'reason_message': 'f',
                    'enabled': False, 'test': False, 'debug': False,
                    'priority': 2,
                },
                {
                    'id': '4', 'type_id': 1,
                    'src': 'function on_check_orders(){return false;}',
                    'additional_params': {},
                    'description': 'g', 'reason_message': 'h',
                    'enabled': True, 'test': True, 'debug': True,
                    'priority': 3,
                },
            ],
        },
    ),
    (
        [
            {
                '_id': '1', 'type_id': 0,
                'src': 'function on_check_orders(){return true;}',
                'additional_params': {'windows': [1]},
                'description': 'a', 'reason_message': 'b',
                'enabled': False, 'test': True, 'debug': False,
                'priority': 0,
                'created': _NOW,
                'updated': _NOW,
            },
        ],
        {
            'rules': [
                {
                    'id': '1', 'type_id': 0,
                    'src': 'function on_check_orders(){return true;}',
                    'additional_params': {'windows': [1]},
                    'description': 'a', 'reason_message': 'b',
                    'enabled': False, 'test': True, 'debug': False,
                    'priority': 0,
                },
            ],
        },
    ),
    (
        [],
        {
            'rules': [],
        },
    ),
    (
        [
            {
                '_id': '1', 'type_id': 0,
                'src': 'function on_check_orders(){return true;}',
                'description': 'a', 'reason_message': 'b',
                'enabled': False, 'test': True, 'debug': False,
                'priority': 0,
                'created': _NOW,
                'updated': _NOW,
            },
            {
                '_id': '2', 'type_id': 0,
                'src': 'function on_check_orders(){return true;}',
                'additional_params': True,
                'description': 'a', 'reason_message': 'b',
                'enabled': False, 'test': True, 'debug': False,
                'priority': 0,
                'created': _NOW,
                'updated': _NOW,
            },
            {
                '_id': 3, 'type_id': 0,
                'src': 'function on_check_orders(){return true;}',
                'additional_params': {},
                'description': 'a', 'reason_message': 'b',
                'enabled': False, 'test': True, 'debug': False,
                'priority': 0,
                'created': _NOW,
                'updated': _NOW,
            },
            {
                '_id': '4', 'type_id': '0',
                'src': 'function on_check_orders(){return true;}',
                'additional_params': {},
                'description': 'a', 'reason_message': 'b',
                'enabled': False, 'test': True, 'debug': False,
                'priority': 0,
                'created': _NOW,
                'updated': _NOW,
            },
        ],
        {
            'rules': [],
        },
    ),
])
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb()
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_rules_list(patch, mongo_fixture, expected_response_data):
    yield _setup_mongo(mongo_fixture)

    test_client = django_test.Client()
    response = test_client.post('/api/antifraud/rules/list/')
    response_data = json.loads(response.content)
    assert response_data == expected_response_data


@pytest.mark.parametrize('request_data,expected_status_code,'
                         'expected_response_data', [
    (
        {
            'rule': {
                'type_id': 0,
                'src': 'function on_check_orders() { return 1; }',
                'additional_params': {
                    'windows': [1, 7],
                },
            },
        },
        200,
        {'tests_passed': True}
    ),
    (
        {
            'rule': {
                'type_id': 1,
                'src': 'function on_check_drivers() { return true; }',
            },
        },
        200,
        {'tests_passed': True}
    ),
])
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb()
@pytest.mark.asyncenv('blocking')
def test_rules_check(
        patch, request_data, expected_status_code, expected_response_data):
    @patch('taxi.external.antifraud._request')
    @async.inline_callbacks
    def _request(location, request, timeout=15, control=False,
                 tvm_src_service=None, tvm_dst_service=None, log_extra=None):
        assert control is False
        assert tvm_src_service == 'admin'
        assert tvm_dst_service == 'antifraud'
        assert location == 'rules/test'

        async.return_value({'tests_passed': True})

    test_client = django_test.Client()
    response = test_client.post(
        '/api/antifraud/rules/check/',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    assert response.status_code == expected_status_code
    response_data = json.loads(response.content)
    assert response_data == expected_response_data


@pytest.mark.parametrize(
    'request_data, expected_status_code, expected_response_data',
    [
        (
            {
                'rule': {
                    'type_id': 0,
                    'src': 'function on_check_order() {return 1;}',
                    'additional_params': {'windows': [1]},
                },
            },
            200,
            {
                'error': 'tests_results: tests failed',
                'tests_passed': False,
                'tests_results': 'tests failed',
            },
        ),
        (
            {
                'rule': {
                    'type_id': 1,
                    'src': 'function on_check_orders() {return 1;}',
                    'additional_params': {'windows': [2]},
                },
            },
            400,
            {
                'code': 'general',
                'message': 'BadRequest',
                'status': 'error',
            },
        ),
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb()
@pytest.mark.asyncenv('blocking')
def test_rules_check_fail(
        patch, request_data, expected_status_code, expected_response_data):
    @patch('taxi.external.antifraud._request')
    @async.inline_callbacks
    def _request(location, request, timeout=15, control=False,
                 tvm_src_service=None, tvm_dst_service=None, log_extra=None):
        yield
        if request['rule']['type'] == 1:
            raise antifraud.BadRequest('BadRequest')
        async.return_value(
            {
                'tests_passed': False,
                'tests_results': 'tests failed',
            },
        )

    test_client = django_test.Client()
    response = test_client.post(
        '/api/antifraud/rules/check/',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    assert response.status_code == expected_status_code
    response_data = json.loads(response.content)
    assert response_data == expected_response_data


@pytest.mark.parametrize('param_name,param_val', [
    (
        'enabled', True
    ),
    (
        'test', True
    ),
    (
        'debug', True
    ),
    (
        'priority', 1
    ),
])
@pytest.mark.parametrize('rule_ids,expected_status_code', [
    (
        ['1'],
        200,
    ),
    (
        ['1', '2'],
        200,
    ),
    (
        ['1', '1'],
        400,
    ),
    (
        ['3'],
        404,
    ),
    (
        ['1', '2', '3'],
        404,
    ),
])
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(antifraud_rules='for_set_params')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_rules_set_params(patch, param_name, param_val, rule_ids,
                          expected_status_code):
    request_data = _prepare_set_params_request(rule_ids, param_name, param_val)

    test_client = django_test.Client()
    response = test_client.post(
        '/api/antifraud/rules/set_%s/' % param_name,
        data=json.dumps(request_data),
        content_type='application/json'
    )
    assert response.status_code == expected_status_code

    if response.status_code != 400:
        yield _check_rule_params_in_mongo(rule_ids, param_name, param_val)


@pytest.mark.asyncenv('blocking')
def test_rules_list_rule_types_from_code():
    test_client = django_test.Client()
    response = test_client.post('/api/antifraud/rules/list_rule_types/')
    assert response.status_code == 200
    assert json.loads(response.content)['rule_types'] == [
        {
            'id': 0,
            'name': 'Cубсидии',
        },
        {
            'id': 1,
            'name': 'Персональные субсидии',
        },
        {
            'id': 2,
            'name': 'Сигнатуры водителя',
        },
        {
            'id': 3,
            'name': 'Антифейк',
        },
        {
            'id': 4,
            'name': 'Минимальный доход',
        },
        {
            'id': 5,
            'name': 'Страховые компенсации',
        },
        {
            'id': 6,
            'name': 'Геобукинг',
        },
        {
            'id': 7,
            'name': 'Гарантия дохода',
        },
        {
            'id': 8,
            'name': 'Еда',
        },
        {
            'id': 9,
            'name': 'Еда (post)',
        },
        {
            'id': 10,
            'name': 'Еда (сигнатура)',
        },
        {
            'id': 11,
            'name': 'Платёжный антифрод',
        },
        {
            'id': 12,
            'name': 'Уровни привязок карт',
        },
        {
            'id': 13,
            'name': 'Заправки',
        },
        {
            'id': 14,
            'name': 'Водительские промокоды',
        },
        {
            'id': 15,
            'name': 'Дополнительная верификация для карт',
        },
        {
            'id': 16,
            'name': 'Запрет смены способа оплаты',
        },
        {
            'id': 17,
            'name': 'Частичные списания',
        },
    ]


@pytest.mark.asyncenv('blocking')
@pytest.mark.config(AFS_JS_RULES_PROPERTIES_ENABLED=True)
@pytest.mark.config(AFS_JS_RULES_PROPERTIES=[
    {
        'id': 0,
        'name': 'Cубсидии (персоналки)',
    },
    {
        'id': 1,
        'name': 'Персональные субсидии',
    },
])
def test_rules_list_rule_types_from_config():
    test_client = django_test.Client()
    response = test_client.post('/api/antifraud/rules/list_rule_types/')
    assert response.status_code == 200
    assert json.loads(response.content)['rule_types'] == (
        config.AFS_JS_RULES_PROPERTIES.get()
    )


@async.inline_callbacks
def _setup_mongo(mongo_fixture):
    if len(mongo_fixture) > 0:
        yield db.antifraud_rules.insert(mongo_fixture)


@async.inline_callbacks
def _check_rules_in_mongo(expected_mongo):
    rules_count = yield db.antifraud_rules.count()
    assert rules_count == len(expected_mongo)

    for expected_rule in expected_mongo:
        rule = yield db.antifraud_rules.find_one({
                '_id': expected_rule['_id'],
            })
        assert rule == expected_rule


def _prepare_set_params_request(rule_ids, param_name, param_val):
    params = []
    for rule_id in rule_ids:
        params.append({'rule_id': rule_id, param_name: param_val})
    return {'params': params}


@async.inline_callbacks
def _check_rule_params_in_mongo(rule_ids, param_name, param_val):
    for rule_id in rule_ids:
        rule = yield db.antifraud_rules.find_one({
                '_id': rule_id,
            })
        if rule:
            assert rule[param_name] == param_val
