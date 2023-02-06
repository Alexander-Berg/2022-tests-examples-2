# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import json

import bson
from django import test as django_test
import pytest

from taxi.core import async
from taxi.core import db


_NOW = datetime.datetime(2018, 5, 28, 12, 13, 14)
_YESTERYEAR = datetime.datetime(2017, 5, 28, 12, 13, 14)


@pytest.mark.parametrize('mongo_fixture,request_data,expected_status_code,'
                         'expected_mongo', [
    (
        [],
        {
            'list': {
                'id': '1',
                'type': 1,
                'description': '',
                'creation_reason': '',
            },
        },
        200,
        [
            {
                '_id': '1',
                'type': 1,
                'description': '',
                'creation_reason': '',
                'created': _NOW,
                'updated': _NOW,
            },
        ],
    ),
    (
        [
            {
                '_id': '1',
                'type': 1,
                'created': _NOW,
                'updated': _NOW,
            },
        ],
        {
            'list': {
                'id': '1',
                'type': 2,
                'description': '',
                'creation_reason': '',
            },
        },
        409,
        [
            {
                '_id': '1',
                'type': 1,
                'created': _NOW,
                'updated': _NOW,
            },
        ],
    ),
])
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb()
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_entity_lists_create_list(
        patch, mongo_fixture, request_data, expected_status_code,
        expected_mongo):
    yield _setup_mongo(mongo_fixture)

    test_client = django_test.Client()
    response = test_client.post(
        '/api/antifraud/entity_lists/create_list/',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    assert response.status_code == expected_status_code

    yield _check_mongo(db.antifraud_entity_list, expected_mongo)


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(antifraud_entity_list='main', antifraud_entity_item='main',
                    antifraud_rules='main'
)
@pytest.mark.asyncenv('blocking')
def test_entity_lists_clear_list():
    test_client = django_test.Client()
    response = test_client.post(
        '/api/antifraud/entity_lists/clear_list/',
        data=json.dumps({
            'list_id': '2',
            'ticket': 'TAXISECTEAM-1',
        }),
        content_type='application/json',
    )
    assert response.status_code == 200
    assert json.loads(response.content) == {}


@pytest.mark.parametrize('process', ['delete'])
@pytest.mark.parametrize('request_data,expected_status_code,expected_mongo,'
                         'processes', [
    (
        {
            'list_id': '2',
            'ticket': 'TAXISECTEAM-1',
        },
        200,
        {
            'entity_lists': [
                {
                    '_id': '1',
                    'type': 1,
                    'created': _YESTERYEAR,
                    'updated': _YESTERYEAR,
                },
                {
                    '_id': '3',
                    'type': 1,
                    'creation_reason': 'FY that\'s why',
                    'created': _YESTERYEAR,
                    'updated': _YESTERYEAR,
                },
            ],
            'entity_items': [
                {
                    '_id': bson.ObjectId('5b17fa09bb013f5a95bc7811'),
                    'list_id': '1',
                    'value': 'v11',
                    'created': _NOW,
                    'updated': _NOW,
                },
                {
                    '_id': bson.ObjectId('5b17fa09bb013f5a95bc7812'),
                    'list_id': '1',
                    'value': 'v12',
                    'created': _NOW,
                    'updated': _NOW,
                },
                {
                    '_id': bson.ObjectId('5b17fa09bb013f5a95bc7813'),
                    'list_id': '1',
                    'value': 'v13',
                    'created': _NOW,
                    'updated': _NOW,
                },
                {
                    '_id': bson.ObjectId('5b17fa09bb013f5a95bc7831'),
                    'list_id': '3',
                    'value': 'v31',
                    'created': _NOW,
                    'updated': _NOW,
                },
                {
                    '_id': bson.ObjectId('5b17fa09bb013f5a95bc7832'),
                    'list_id': '3',
                    'value': 'v32',
                    'created': _NOW,
                    'updated': _NOW,
                },
                {
                    '_id': bson.ObjectId('5b17fa09bb013f5a95bc7833'),
                    'list_id': '3',
                    'value': 'v33',
                    'created': _NOW,
                    'updated': _NOW,
                },
            ],
        },
        ['delete', 'clear']
    ),
    (
        {
            'list_id': '4',
            'ticket': 'TAXISECTEAM-1',
        },
        404,
        {
            'entity_lists': [
                {
                    '_id': '1',
                    'type': 1,
                    'created': _YESTERYEAR,
                    'updated': _YESTERYEAR,
                },
                {
                    '_id': '2',
                    'type': 2,
                    'description': 'У Маши шары',
                    'created': _YESTERYEAR,
                    'updated': _YESTERYEAR,
                },
                {
                    '_id': '3',
                    'type': 1,
                    'creation_reason': 'FY that\'s why',
                    'created': _YESTERYEAR,
                    'updated': _YESTERYEAR,
                },
            ],
            'entity_items': None,
        },
        ['delete', 'clear']
    ),
    (
        {
            'list_id': '1',
            'ticket': 'TAXISECTEAM-1',
        },
        409,
        {
            'entity_lists': [
                {
                    '_id': '1',
                    'type': 1,
                    'created': _YESTERYEAR,
                    'updated': _YESTERYEAR,
                },
                {
                    '_id': '2',
                    'type': 2,
                    'description': 'У Маши шары',
                    'created': _YESTERYEAR,
                    'updated': _YESTERYEAR,
                },
                {
                    '_id': '3',
                    'type': 1,
                    'creation_reason': 'FY that\'s why',
                    'created': _YESTERYEAR,
                    'updated': _YESTERYEAR,
                },
            ],
            'entity_items': None,
        },
        ['delete']
    ),
])
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(antifraud_entity_list='main', antifraud_entity_item='main',
                    antifraud_rules='main'
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_entity_lists_delete_list(
        patch, process, request_data, expected_status_code, expected_mongo,
        processes):
    if process in processes:
        test_client = django_test.Client()
        response = test_client.post(
            '/api/antifraud/entity_lists/%s_list/' % process,
            data=json.dumps(request_data),
            content_type='application/json'
        )
        assert response.status_code == expected_status_code

        if process == 'delete':
            yield _check_mongo(
                db.antifraud_entity_list,
                expected_mongo['entity_lists']
            )
        yield _check_mongo(
            db.antifraud_entity_item,
            expected_mongo['entity_items']
        )


@pytest.mark.parametrize('request_data,expected_status_code,expected_mongo', [
    (
        {
            'list': {
                'id': '1',
                'description': 'azaza',
            },
        },
        200,
        [
            {
                '_id': '1',
                'type': 1,
                'description': 'azaza',
                'created': _YESTERYEAR,
                'updated': _NOW,
            },
        ],
    ),
    (
        {
            'list': {
                'id': '2',
                'description': 'azaza',
            },
        },
        200,
        [
            {
                '_id': '2',
                'type': 2,
                'description': 'azaza',
                'created': _YESTERYEAR,
                'updated': _NOW,
            },
        ],
    ),
    (
        {
            'list': {
                'id': '3',
                'creation_reason': 'ololo',
            },
        },
        200,
        [
            {
                '_id': '3',
                'type': 1,
                'creation_reason': 'ololo',
                'created': _YESTERYEAR,
                'updated': _NOW,
            },
        ],
    ),
    (
        {
            'list': {
                'id': '1',
                'description': 'azaza',
                'creation_reason': 'ololo',
            },
        },
        200,
        [
            {
                '_id': '1',
                'type': 1,
                'description': 'azaza',
                'creation_reason': 'ololo',
                'created': _YESTERYEAR,
                'updated': _NOW,
            },
        ],
    ),
    (
        {
            'list': {
                'id': '1',
            },
        },
        200,
        [
            {
                '_id': '1',
                'type': 1,
                'created': _YESTERYEAR,
                'updated': _YESTERYEAR,
            },
        ],
    ),
    (
        {
            'list': {
                'id': '4',
                'description': 'azaza',
            },
        },
        404,
        None,
    ),
])
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(antifraud_entity_list='main')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_entity_lists_edit_list(
        patch, request_data, expected_status_code, expected_mongo):
    test_client = django_test.Client()
    response = test_client.post(
        '/api/antifraud/entity_lists/edit_list/',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    assert response.status_code == expected_status_code

    yield _check_mongo(
        db.antifraud_entity_list,
        expected_mongo,
        check_docs_count=False,
    )


@pytest.mark.parametrize('mongo_fixture,expected_response_data', [
    (
        [
            {
                '_id': '4',
                'type': 1,
                'created': _NOW,
                'updated': _NOW,
            },
            {
                '_id': '2',
                'type': 2,
                'description': 'azaza',
                'creation_reason': 'ololo',
                'created': _NOW,
                'updated': _NOW,
            },
            {
                '_id': '3',
                'type': 1,
                'description': 'azaza',
                'created': _NOW,
                'updated': _NOW,
            },
            {
                '_id': '1',
                'type': 1,
                'creation_reason': 'ololo',
                'created': _NOW,
                'updated': _NOW,
            },
        ],
        {
            'lists': [
                {
                    'id': '1',
                    'type': 1,
                    'creation_reason': 'ololo',
                },
                {
                    'id': '2',
                    'type': 2,
                    'description': 'azaza',
                    'creation_reason': 'ololo',
                },
                {
                    'id': '3',
                    'type': 1,
                    'description': 'azaza',
                },
                {
                    'id': '4',
                    'type': 1,
                },
            ],
        },
    ),
    (
        [
            {
                '_id': '3',
                'type': 2,
                'created': _NOW,
                'updated': _NOW,
            },
        ],
        {
            'lists': [
                {
                    'id': '3', 'type': 2,
                },
            ],
        },
    ),
    (
        [],
        {
            'lists': [],
        },
    ),
])
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb()
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_entity_lists_search_lists(
        patch, mongo_fixture, expected_response_data):
    yield _setup_mongo(mongo_fixture)

    test_client = django_test.Client()
    response = test_client.post(
        '/api/antifraud/entity_lists/search_lists/'
    )
    response_data = json.loads(response.content)
    assert response_data == expected_response_data


@pytest.mark.parametrize(
    'request_data, attachments, expected_status_code, expected_mongo', [
    (
        {
            'ticket': 'TAXISECTEAM-1',
        },
        {
            'azaza.txt': '{"list_id": "1", "items": ["1", "2", "3"]}',
        },
        200,
        [
            {
                'list_id': '1',
                'value': '1',
                'created': _NOW,
                'updated': _NOW,
            },
            {
                'list_id': '1',
                'value': '2',
                'created': _NOW,
                'updated': _NOW,
            },
            {
                'list_id': '1',
                'value': '3',
                'created': _NOW,
                'updated': _NOW,
            },
        ]
    ),
    (
        {
            'ticket': 'TAXISECTEAM-1',
        },
        {
            'azaza.txt': '{"list_id": "2", "items": [{"1": {"2": 3}}]}',
        },
        200,
        [
            {
                'list_id': '2',
                'value': {'1': {'2': 3}},
                'created': _NOW,
                'updated': _NOW,
            },
        ]
    ),
    (
        {
            'ticket': 'TAXISECTEAM-1',
        },
        {
            'azaza.txt': '{"list_id": "1", "items": []}',
        },
        200,
        []
    ),
    (
        {
            'ticket': 'TAXIBACKEND-1',
        },
        {
            'azaza.txt': '{"list_id": "1", "items": []}',
        },
        400,
        []
    ),
    (
        {
            'ticket': 'TAXISECTEAM-1',
        },
        {
            'azaza.txt': '{"list_id": "1", "items": [{"1": 1}]}',
        },
        400,
        []
    ),
    (
        {
            'ticket': 'TAXISECTEAM-1',
        },
        {
            'azaza.txt': '{"list_id": "2", "items": ["1"]}',
        },
        400,
        []
    ),
    (
        {
            'ticket': 'TAXISECTEAM-1',
        },
        {
            'azaza.txt': '{"list_id": "4", "items": ["1"]}',
        },
        404,
        []
    ),
    (
        {
            'ticket': 'TAXISECTEAM-1',
        },
        {},
        400,
        []
    ),
    (
        {
            'ticket': 'TAXISECTEAM-1',
        },
        {
            'azaza1.txt': '{"list_id": "1", "items": ["1"]}',
            'azaza2.txt': '{"list_id": "2", "items": ["2"]}',
        },
        400,
        []
    ),
])
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(antifraud_entity_list='main')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_entity_lists_add_items(
        patch, request_data, attachments, expected_status_code,
        expected_mongo):
    _patch_startrack(patch, attachments)

    test_client = django_test.Client()
    response = test_client.post(
        '/api/antifraud/entity_lists/add_items/',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    assert response.status_code == expected_status_code

    yield _check_mongo(db.antifraud_entity_item, expected_mongo, 'value',
                       ignore_time_vals=True)


@pytest.mark.parametrize('request_data,expected_status_code,'
                         'expected_response_data,expected_mongo', [
    (
        {
            'item_ids': [
                '5b17fa09bb013f5a95bc7811',
                '5b17fa09bb013f5a95bc7812',
                '5b17fa09bb013f5a95bc7813',
                '5b17fa09bb013f5a95bc7821',
                '5b17fa09bb013f5a95bc7822',
                '5b17fa09bb013f5a95bc7823',
                '5b17fa09bb013f5a95bc7832',
                '5b17fa09bb013f5a95bc7833',
            ],
        },
        200,
        {'deleted': 8},
        [
            {
                '_id': bson.ObjectId('5b17fa09bb013f5a95bc7831'),
                'list_id': '3',
                'value': 'v31',
                'created': _NOW,
                'updated': _NOW,
            },
        ]
    ),
    (
        {
            'item_ids': [
                '5b17fa09bb013f5a95bc7811',
                '5b17fa09bb013f5a95bc7811',
                '5b17fa09bb013f5a95bc7812',
                '5b17fa09bb013f5a95bc7813',
            ],
        },
        200,
        {'deleted': 3},
        [
            {
                '_id': bson.ObjectId('5b17fa09bb013f5a95bc7821'),
                'list_id': '2',
                'value': {'f1': 'v121', 'f2': 'v221'},
                'created': _NOW,
                'updated': _NOW,
            },
            {
                '_id': bson.ObjectId('5b17fa09bb013f5a95bc7822'),
                'list_id': '2',
                'value': {'f1': 'v122', 'f2': 'v222'},
                'created': _NOW,
                'updated': _NOW,
            },
            {
                '_id': bson.ObjectId('5b17fa09bb013f5a95bc7823'),
                'list_id': '2',
                'value': {'f1': 'v123', 'f2': 'v223'},
                'created': _NOW,
                'updated': _NOW,
            },
            {
                '_id': bson.ObjectId('5b17fa09bb013f5a95bc7831'),
                'list_id': '3',
                'value': 'v31',
                'created': _NOW,
                'updated': _NOW,
            },
            {
                '_id': bson.ObjectId('5b17fa09bb013f5a95bc7832'),
                'list_id': '3',
                'value': 'v32',
                'created': _NOW,
                'updated': _NOW,
            },
            {
                '_id': bson.ObjectId('5b17fa09bb013f5a95bc7833'),
                'list_id': '3',
                'value': 'v33',
                'created': _NOW,
                'updated': _NOW,
            },
        ]
    ),
    (
        {
            'item_ids': [
                '5b17fa09bb013f5a95bc7811',
                '5b17fa09bb013f5a95bc7812',
                '5b17fa09bb013f5a95bc7813',
                '5b17fa09bb013f5a95bc7844',
                '5b17fa09bb013f5a95bc7821',
                '5b17fa09bb013f5a95bc7822',
                '5b17fa09bb013f5a95bc7823',
                '5b17fa09bb013f5a95bc7832',
                '5b17fa09bb013f5a95bc7833',
            ],
        },
        200,
        {'deleted': 8},
        [
            {
                '_id': bson.ObjectId('5b17fa09bb013f5a95bc7831'),
                'list_id': '3',
                'value': 'v31',
                'created': _NOW,
                'updated': _NOW,
            },
        ]
    ),
    (
        {
            'item_ids': ['123'],
        },
        200,
        None,
        None
    ),
])
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(antifraud_entity_item='main')
@pytest.mark.asyncenv('blocking')
def test_entity_lists_search_and_delete_items(
        patch, request_data, expected_status_code, expected_response_data,
        expected_mongo):
    test_client = django_test.Client()
    response = test_client.post(
        '/api/antifraud/entity_lists/search_and_delete_items/',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    assert response.status_code == expected_status_code


@pytest.mark.parametrize('request_data,expected_status_code,'
                         'expected_response_data', [
    (
        {
            'list_id': '1',
        },
        200,
        {
            'items': [
                {
                    'id': '5b17fa09bb013f5a95bc7811',
                    'value': 'v11',
                },
                {
                    'id': '5b17fa09bb013f5a95bc7812',
                    'value': 'v12',
                },
                {
                    'id': '5b17fa09bb013f5a95bc7813',
                    'value': 'v13',
                },
            ],
        }
    ),
    (
        {
            'list_id': '4',
        },
        404,
        None
    ),
])
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(antifraud_entity_list='main', antifraud_entity_item='main')
@pytest.mark.asyncenv('blocking')
def test_entity_lists_search_items(
        patch, request_data, expected_status_code, expected_response_data):
    test_client = django_test.Client()
    response = test_client.post(
        '/api/antifraud/entity_lists/search_items/',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    assert response.status_code == expected_status_code
    if expected_response_data:
        response_data = json.loads(response.content)
        assert response_data == expected_response_data


@async.inline_callbacks
def _setup_mongo(mongo_fixture):
    if len(mongo_fixture) > 0:
        yield db.antifraud_entity_list.insert(mongo_fixture)


@async.inline_callbacks
def _check_mongo(mongo_db, expected_mongo, id_field_name='_id',
                 check_docs_count=True, ignore_time_vals=False):
    if expected_mongo:
        if check_docs_count:
            docs_count = yield mongo_db.count()
            assert docs_count == len(expected_mongo)

        for expected_doc in expected_mongo:
            doc = yield mongo_db.find_one({
                    id_field_name: expected_doc[id_field_name],
                })
            if id_field_name != '_id' and doc:
                del doc['_id']
            if ignore_time_vals:
                for field_name in ['created', 'updated']:
                    if field_name in expected_doc:
                        assert field_name in doc
                        assert isinstance(
                            doc[field_name], type(expected_doc[field_name])
                        )
                        del doc[field_name]
                        del expected_doc[field_name]
            assert doc == expected_doc


def _patch_startrack(patch, attachments):
    @patch('taxi.external.startrack.get_attachments_info')
    @async.inline_callbacks
    def get_attachments_info(ticket):
        assert ticket == 'TAXISECTEAM-1'

        attachments_info = []
        i = 1
        for attachment_name in attachments:
            attachments_info.append(
                {
                    'id': i,
                    'name': attachment_name,
                }
            )
            i += 1
        yield async.return_value(attachments_info)

    @patch('taxi.external.startrack.get_text_attachment')
    @async.inline_callbacks
    def get_text_attachment(ticket, attachment_id, attachment_name):
        assert ticket == 'TAXISECTEAM-1'
        assert attachment_id == 1
        assert attachment_name == 'azaza.txt'

        yield async.return_value(attachments[attachment_name])

    @patch('taxi.external.startrack.get_ticket_info')
    @async.inline_callbacks
    def get_ticket_info(ticket):
        assert ticket == 'TAXISECTEAM-1'
        yield async.return_value()
