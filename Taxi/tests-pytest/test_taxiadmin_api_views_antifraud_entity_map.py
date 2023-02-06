# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import json

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
            'entity': {
                'name': '1',
                'description': '',
                'creation_reason': '',
            },
        },
        200,
        [
            {
                'name': '1',
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
                'name': '1',
                'created': _NOW,
                'updated': _NOW,
            },
        ],
        {
            'entity': {
                'name': '1',
                'description': '',
                'creation_reason': '',
            },
        },
        409,
        [
            {
                'name': '1',
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
def test_entity_map_create_map(
        patch, mongo_fixture, request_data, expected_status_code,
        expected_mongo):
    yield _setup_mongo(mongo_fixture)

    response = django_test.Client().post(
        '/api/antifraud/entity_map/',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    assert response.status_code == expected_status_code

    yield _check_mongo(db.antifraud_entity_map, expected_mongo)


@pytest.mark.parametrize('name,expected_status_code,expected_mongo', [
    (
        '2',
        200,
        {
            'entity_map': [
                {
                    'name': '1',
                    'created': _YESTERYEAR,
                    'updated': _YESTERYEAR,
                },
                {
                    'name': '3',
                    'creation_reason': 'Creation reason three',
                    'created': _YESTERYEAR,
                    'updated': _YESTERYEAR,
                },
            ],
        },
    ),
    (
        '4',
        404,
        {
            'entity_map': [
                {
                    'name': '1',
                    'created': _YESTERYEAR,
                    'updated': _YESTERYEAR,
                },
                {
                    'name': '2',
                    'description': 'Description two',
                    'created': _YESTERYEAR,
                    'updated': _YESTERYEAR,
                },
                {
                    'name': '3',
                    'creation_reason': 'Creation reason three',
                    'created': _YESTERYEAR,
                    'updated': _YESTERYEAR,
                },
            ],
        },
    ),
    (
        '1',
        409,
        {
            'entity_map': [
                {
                    'name': '1',
                    'created': _YESTERYEAR,
                    'updated': _YESTERYEAR,
                },
                {
                    'name': '2',
                    'description': 'Description two',
                    'created': _YESTERYEAR,
                    'updated': _YESTERYEAR,
                },
                {
                    'name': '3',
                    'creation_reason': 'Creation reason three',
                    'created': _YESTERYEAR,
                    'updated': _YESTERYEAR,
                },
            ],
        },
    ),
])
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(antifraud_entity_map='main', antifraud_rules='main')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_entity_map_delete_entity(name, expected_status_code, expected_mongo):
    response = django_test.Client().delete(
        '/api/antifraud/entity_map/%s/' % name
    )
    assert response.status_code == expected_status_code

    yield _check_mongo(
        db.antifraud_entity_map,
        expected_mongo['entity_map']
    )


@pytest.mark.parametrize('name,request_data,expected_status_code,expected_mongo', [
    (
        '1',
        {
            'entity': {
                'description': 'Description one',
            },
        },
        200,
        [
            {
                'name': '1',
                'description': 'Description one',
                'created': _YESTERYEAR,
                'updated': _NOW,
            },
        ],
    ),
    (
        '2',
        {
            'entity': {
                'description': 'Description two(two)',
            },
        },
        200,
        [
            {
                'name': '2',
                'description': 'Description two(two)',
                'created': _YESTERYEAR,
                'updated': _NOW,
            },
        ],
    ),
    (
        '3',
        {
            'entity': {
                'description': 'Description three',
            },
        },
        200,
        [
            {
                'name': '3',
                'description': 'Description three',
                'creation_reason': 'Creation reason three',
                'created': _YESTERYEAR,
                'updated': _NOW,
            },
        ],
    ),
    (
        '3',
        {
            'entity': {
                'creation_reason': 'Creation reason three(three)',
            },
        },
        200,
        [
            {
                'name': '3',
                'creation_reason': 'Creation reason three(three)',
                'created': _YESTERYEAR,
                'updated': _NOW,
            },
        ],
    ),
    (
        '1',
        {
            'entity': {
                'description': 'Description one',
                'creation_reason': 'Creation reason one',
            },
        },
        200,
        [
            {
                'name': '1',
                'description': 'Description one',
                'creation_reason': 'Creation reason one',
                'created': _YESTERYEAR,
                'updated': _NOW,
            },
        ],
    ),
    (
        '1',
        {
            'entity': {
            },
        },
        200,
        [
            {
                'name': '1',
                'created': _YESTERYEAR,
                'updated': _NOW,
            },
        ],
    ),
    (
        '4',
        {
            'entity': {
                'description': 'Description four',
                'creation_reason': 'Creation reason four',
            },
        },
        404,
        None,
    ),
])
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(antifraud_entity_map='main')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_entity_map_edit_meta(
        name, request_data, expected_status_code, expected_mongo):
    response = django_test.Client().put(
        '/api/antifraud/entity_map/%s/' % name,
        data=json.dumps(request_data),
        content_type='application/json'
    )
    assert response.status_code == expected_status_code

    yield _check_mongo(
        db.antifraud_entity_map,
        expected_mongo,
        check_docs_count=False,
    )


@pytest.mark.parametrize('mongo_fixture,expected_response_data', [
    (
        [
            {
                'name': '4',
                'created': _NOW,
                'updated': _NOW,
            },
            {
                'name': '2',
                'description': 'description 2',
                'creation_reason': 'creation 2',
                'created': _NOW,
                'updated': _NOW,
            },
            {
                'name': '3',
                'description': 'description 3',
                'created': _NOW,
                'updated': _NOW,
            },
            {
                'name': '1',
                'creation_reason': 'creation 1',
                'created': _NOW,
                'updated': _NOW,
            },
        ],
        {
            'entities': [
                {
                    'name': '1',
                    'creation_reason': 'creation 1',
                },
                {
                    'name': '2',
                    'description': 'description 2',
                    'creation_reason': 'creation 2',
                },
                {
                    'name': '3',
                    'description': 'description 3',
                },
                {
                    'name': '4'
                },
            ],
        },
    ),
    (
        [
            {
                'name': '3',
                'created': _NOW,
                'updated': _NOW,
            },
        ],
        {
            'entities': [
                {
                    'name': '3'
                },
            ],
        },
    ),
    (
        [],
        {
            'entities': [],
        },
    ),
])
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb()
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_entity_map_get(mongo_fixture, expected_response_data):
    yield _setup_mongo(mongo_fixture)

    response = django_test.Client().get(
        '/api/antifraud/entity_map/'
    )
    response_data = json.loads(response.content)
    assert response_data == expected_response_data


@pytest.mark.parametrize(
    'name, request_data, attachments, expected_status_code, expected_mongo', [
    (
        '1',
        {
            'ticket': 'TAXISECTEAM-1',
        },
        {
            'attachment.txt': '{"name": "1", "value": {"tmp": true}}',
        },
        200,
        [
            {
                'name': '1',
                'value': {"tmp": True},
                'created': _YESTERYEAR,
                'updated': _NOW,
            },
        ]
    ),
    (
        "2",
        {
            'ticket': 'TAXISECTEAM-1',
        },
        {
            'attachment.txt': '{"name": "2", "value": {"1": {"2": 3}}}',
        },
        200,
        [
            {
                'name': '2',
                'value': {'1': {'2': 3}},
                'description': 'Description two',
                'created': _YESTERYEAR,
                'updated': _NOW,
            },
        ]
    ),
    (
        "1",
        {
            'ticket': 'TAXIBACKEND-1',
        },
        {
            'attachment.txt': '{"name": "1", "value": {"tmp": true}}',
        },
        400,
        []
    ),
    (
        "1",
        {
            'ticket': 'TAXISECTEAM-1',
        },
        {
            'attachment.txt': '{"name": "1", "value": []}',
        },
        400,
        []
    ),
    (
        "1",
        {
            'ticket': 'TAXISECTEAM-1',
        },
        {
            'attachment.txt': '{"name": "1", "value": "some_string"}',
        },
        400,
        []
    ),
    (
        "1",
        {
            'ticket': 'TAXISECTEAM-1',
        },
        {
            'attachment.txt': '{"name": "1", "value": {}}',
        },
        200,
        []
    ),
    (
        "1",
        {
            'ticket': 'TAXISECTEAM-1',
        },
        {
            'attachment.txt': '{"name": "2", "value": {}}',
        },
        400,
        []
    ),
    (
        "4",
        {
            'ticket': 'TAXISECTEAM-1',
        },
        {
            'attachment.txt': '{"name": "4", "value": {}}',
        },
        404,
        []
    ),
    (
        "1",
        {
            'ticket': 'TAXISECTEAM-1',
        },
        {
            'attachment.txt': '{"name": "2", "value": {}',
        },
        400,
        []
    ),
    (
        "1",
        {
            'ticket': 'TAXISECTEAM-1',
        },
        {
            'attachment.txt': '{"value": {}}',
        },
        400,
        []
    ),
    (
        "1",
        {
            'ticket': 'TAXISECTEAM-1',
        },
        {
            'attachment.txt': '{"name": "1"}',
        },
        400,
        []
    ),
    (
        "1",
        {
            'ticket': 'TAXISECTEAM-1',
        },
        {},
        400,
        []
    ),
    (
        "2",
        {
            'ticket': 'TAXISECTEAM-1',
        },
        {
            'attachment.txt': '{"name": "2", "value": {}}',
            'attachment2.txt': '{"name": "2", "value": {}}',
        },
        400,
        []
    ),
])
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(antifraud_entity_map='main')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_entity_map_value(
        patch, name, request_data, attachments, expected_status_code,
        expected_mongo):
    _patch_startrack(patch, attachments)

    test_client = django_test.Client()
    response = test_client.put(
        '/api/antifraud/entity_map/%s/value/' % name,
        data=json.dumps(request_data),
        content_type='application/json'
    )
    assert response.status_code == expected_status_code

    yield _check_mongo(db.antifraud_entity_map, expected_mongo,
                       check_docs_count=False)


@async.inline_callbacks
def _setup_mongo(mongo_fixture):
    if len(mongo_fixture) > 0:
        yield db.antifraud_entity_map.insert(mongo_fixture)


@async.inline_callbacks
def _check_mongo(mongo_db, expected_mongo, id_field_name='name',
                 check_docs_count=True, ignore_time_vals=False):
    if expected_mongo:
        if check_docs_count:
            docs_count = yield mongo_db.count()
            assert docs_count == len(expected_mongo)

        for expected_doc in expected_mongo:
            doc = yield mongo_db.find_one({
                    id_field_name: expected_doc[id_field_name],
                })
            if doc:
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
        assert attachment_name == 'attachment.txt'

        yield async.return_value(attachments[attachment_name])

    @patch('taxi.external.startrack.get_ticket_info')
    @async.inline_callbacks
    def get_ticket_info(ticket):
        assert ticket == 'TAXISECTEAM-1'
        yield async.return_value()
