import datetime

import bson
import pytest

from taxi.core import async
from taxi.core import db
from taxi.internal.audit_kit import log_admin
from taxi.internal.audit_kit.log_admin import models


@pytest.mark.config(
    ADMIN_AUDIT_USE_SERVICE=False,
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_log_admin_insert():
    @async.inline_callbacks
    def _old_insert(login, action, arguments, ticket=None, object_id=None):
        # mongo can't save fields that contain '$' or '.'
        # so we hack modifiers so that it can be saved and restored later
        modifiers = [  # add more if needed
            'set',
            'unset',
            'pull',
            'push',
            'rename',
            'currentDate',
        ]
        for modifier in modifiers:
            mongo_modifier = '$%s' % modifier
            if mongo_modifier in arguments:
                arguments['__%s__' % modifier] = dict(
                    (key.replace('.', '__dot__'), value)
                    for key, value in arguments.pop(mongo_modifier).iteritems()
                )
        doc = {
            'login': login,
            'action': action,
            'arguments': arguments,
            'timestamp': datetime.datetime.utcnow(),
        }
        if ticket:
            doc['ticket'] = ticket
        if object_id:
            doc['object_id'] = object_id

        doc_id = yield db.log_admin.insert(doc)
        async.return_value(doc_id)

    @async.inline_callbacks
    def _new_insert(login, action, arguments, ticket=None, object_id=None):
        doc_id = yield log_admin.RobotLogCreate(
            login=login,
            timestamp=datetime.datetime.utcnow(),
            arguments=arguments,
            action=action,
            ticket=ticket,
            object_id=object_id,
        ).result()
        async.return_value(doc_id)

    params = {
        'login': 'ydemidenko',
        'action': 'save_value',
        'arguments': {'$set': {'status.p': 'ok'}, 'request': 'ok'},
        'ticket': 'TAXIRATE-1',
    }
    old_inserted_doc_id = _old_insert(**params)
    new_inserted_doc_id = _new_insert(**params)
    old_inserted_doc = yield db.log_admin.find_one(
        {'_id': old_inserted_doc_id}
    )
    new_inserted_doc = yield db.log_admin.find_one(
        {'_id': new_inserted_doc_id}
    )
    del old_inserted_doc['_id']
    del new_inserted_doc['_id']
    assert old_inserted_doc == new_inserted_doc


@pytest.mark.config(
    ADMIN_AUDIT_USE_SERVICE=False,
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_log_admin_find_one():
    log_id = bson.ObjectId('23b278aa54a94422a6e72ae5')
    old_finded_doc = yield db.log_admin.find_one({'_id': log_id})
    new_finded_doc = yield log_admin.ClientLogRetrieve(pk=log_id).result()
    assert old_finded_doc == new_finded_doc


@pytest.mark.config(
    ADMIN_AUDIT_USE_SERVICE=False,
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_log_admin_client_find():
    old_finded_docs = yield db.secondary.log_admin.find(
        {'action': 'save_value'}
    ).sort([('timestamp', db.DESC)]).run()
    new_finded_docs = yield log_admin.ClientLogsRetrieve(
        actions=['save_value']
    ).result()
    assert old_finded_docs == new_finded_docs


@pytest.mark.config(
    ADMIN_AUDIT_USE_SERVICE=False,
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_log_admin_robot_find():
    old_finded_docs = yield db.log_admin.find(
        {'action': {'$in': ['save_value']}}
    ).run()
    new_finded_docs = yield log_admin.RobotLogsRetrieve(
        actions=['save_value']
    ).result()
    assert old_finded_docs == new_finded_docs


@pytest.mark.config(
    ADMIN_AUDIT_USE_SERVICE=False,
)
@pytest.mark.now('2019-01-01T10:00:00.0')
@pytest.mark.parametrize(
    'log_params,expected_service,expected_mongo',
    [
        (
            {
                'login': 'ydemidenko',
                'timestamp': '2019-01-01T10:00:00.000000',
                'arguments': {},
                'action': 'save_value',
                'id': 'tariff_editor:559134566c090a24c5a123f4',
                'ticket': 'ticket-1',
                'object_id': 'object_id_1',
            },
            {
                'login': 'ydemidenko',
                'timestamp': '2019-01-01T10:00:00.000000+0300',
                'arguments': {},
                'action': 'save_value',
                'id': 'tariff_editor:559134566c090a24c5a123f4',
                'ticket': 'ticket-1',
                'object_id': 'object_id_1',
            },
            {
                'login': 'ydemidenko',
                'timestamp': datetime.datetime(2019, 1, 1, 7),
                'arguments': {},
                'action': 'save_value',
                '_id': 'tariff_editor:559134566c090a24c5a123f4',
                'ticket': 'ticket-1',
                'object_id': 'object_id_1',
            }
        ),
        (
            {
                'login': 'ydemidenko',
                'timestamp': '2019-01-01T10:00:00.000000+0300',
                'arguments': {},
                'action': 'save_value',
            },
            {
                'login': 'ydemidenko',
                'timestamp': '2019-01-01T10:00:00.000000+0300',
                'arguments': {},
                'action': 'save_value',
            },
            {
                'login': 'ydemidenko',
                'timestamp': datetime.datetime(2019, 1, 1, 7),
                'arguments': {},
                'action': 'save_value',
            },
        ),
        (
            {
                'login': 'ydemidenko',
                'timestamp': datetime.datetime(2019, 1, 1, 10),
                'arguments': {},
                'action': 'save_value',
                'id': bson.ObjectId('559134566c090a24c5a123f4'),
            },
            {
                'login': 'ydemidenko',
                'timestamp': '2019-01-01T13:00:00.000000+0300',
                'arguments': {},
                'action': 'save_value',
                'id': '559134566c090a24c5a123f4',
            },
            {
                'login': 'ydemidenko',
                'timestamp': datetime.datetime(2019, 1, 1, 10),
                'arguments': {},
                'action': 'save_value',
                '_id': bson.ObjectId('559134566c090a24c5a123f4'),
            },
        ),
    ]
)
@pytest.mark.asyncenv('async')
def test_log_model(log_params, expected_service, expected_mongo):
    log = models.Log.deserialize(log_params)
    assert log.to_service() == expected_service
    assert log.to_mongo() == expected_mongo


@pytest.mark.config(
    ADMIN_AUDIT_USE_SERVICE=False,
)
@pytest.mark.now('2019-01-01T10:00:00.0')
@pytest.mark.parametrize(
    'params,expected_service,expected_mongo',
    [
        (
            {
                'ticket': 'ticket-1',
                'ticket_queue': 'taxirate',
                'pk': '559134566c090a24c5a123f4',
                'id_till': '559134566c090a24c5a123f4',
                'action': 'save_value',
                'actions': ['save_value'],
                'home_zone': 'home_zone',
                'conditions': {'p': 'p'},
                'arguments_ids': ['559134566c090a24c5a123f4', 'not_object_id'],
                'arguments_id': '559134566c090a24c5a123f4',
                'date_till': '2019-01-01T10:00:00.0',
                'date_from': '2019-01-01T10:00:00.0',
                'check_task_id_exists': True,
            },
            {
                'ticket': 'ticket-1',
                'ticket_queue': 'taxirate',
                'id': '559134566c090a24c5a123f4',
                'id_till': '559134566c090a24c5a123f4',
                'action': 'save_value',
                'actions': ['save_value'],
                'home_zone': 'home_zone',
                'conditions': {'p': 'p'},
                'arguments_ids': ['559134566c090a24c5a123f4', 'not_object_id'],
                'arguments_id': '559134566c090a24c5a123f4',
                'date_till': '2019-01-01T10:00:00.0',
                'date_from': '2019-01-01T10:00:00.0',
                'check_task_id_exists': True,
            },
            {
                'ticket': 'ticket-1',
                '_id': bson.ObjectId('559134566c090a24c5a123f4'),
                'action': 'save_value',
                'arguments.request.home_zone': 'home_zone',
                'arguments.cn': {'p': 'p'},
                'arguments._id': bson.ObjectId('559134566c090a24c5a123f4'),
                'timestamp': {
                    '$lte': datetime.datetime(2019, 1, 1, 7),
                    '$gte': datetime.datetime(2019, 1, 1, 7),
                },
                'arguments.response.task_id': {'$exists': True},
            },
        ),
        (
            {
                'ticket_queue': 'taxirate',
                'id_till': bson.ObjectId('559134566c090a24c5a123f4'),
                'actions': ['save_value'],
                'arguments_ids': [
                    bson.ObjectId('559134566c090a24c5a123f4'), 'not_object_id'
                ],
                'date_till': datetime.datetime(2019, 1, 1, 7),
            },
            {
                'ticket_queue': 'taxirate',
                'id_till': '559134566c090a24c5a123f4',
                'actions': ['save_value'],
                'arguments_ids': ['559134566c090a24c5a123f4', 'not_object_id'],
                'date_till': '2019-01-01T10:00:00.000000+0300',
            },
            {
                'ticket': {'$regex': '^taxirate\\-'},
                '_id': {'$lt': bson.ObjectId('559134566c090a24c5a123f4')},
                'action': {'$in': ['save_value']},
                'arguments._id': {'$in': [
                    bson.ObjectId('559134566c090a24c5a123f4'), 'not_object_id'
                ]},
                'timestamp': {
                    '$lte': datetime.datetime(2019, 1, 1, 7),
                },
            },
        ),
        (
            {
                'actions': [],
                'home_zone': '',
                'conditions': {},
                'arguments_ids': [],
            },
            {
                'actions': [],
                'home_zone': '',
                'conditions': {},
                'arguments_ids': [],
            },
            {
                'action': {'$in': []},
                'arguments.request.home_zone': '',
                'arguments._id': {'$in': []},
                'arguments.cn': {},
            },
        ),
    ]
)
@pytest.mark.asyncenv('async')
def test_robot_logs_query_model(params, expected_service, expected_mongo):
    robot_logs_query = models.RobotLogsQuery(**params)
    assert robot_logs_query.to_service() == expected_service
    assert robot_logs_query.to_mongo() == expected_mongo


@pytest.mark.config(
    ADMIN_AUDIT_USE_SERVICE=False,
)
@pytest.mark.now('2019-01-01T10:00:00.0')
@pytest.mark.parametrize(
    'params,expected_service,expected_mongo',
    [
        (
            {
                'date_from': '2019-01-01T10:00:00.0',
                'date_till': datetime.datetime(2019, 1, 1, 7),
                'exclude': ['save_value'],
                'login': 'ydemidenko',
                'object_id': 'object_id_1',
                'actions': ['save_value'],
                'newer_than': '559134566c090a24c5a123f4',
                'older_than': bson.ObjectId('559134566c090a24c5a123f4'),
            },
            {
                'date_from': '2019-01-01T10:00:00.0',
                'date_till': '2019-01-01T10:00:00.000000+0300',
                'exclude': ['save_value'],
                'actions': ['save_value'],
                'login': 'ydemidenko',
                'object_id': 'object_id_1',
            },
            {
                'login': 'ydemidenko',
                'object_id': 'object_id_1',
                'action': {'$in': ['save_value']},
                'timestamp': {
                    '$lte': datetime.datetime(2019, 1, 1, 7),
                    '$gte': datetime.datetime(2019, 1, 1, 7),
                },
                '_id': {
                    '$lt': bson.ObjectId('559134566c090a24c5a123f4'),
                    '$gt': bson.ObjectId('559134566c090a24c5a123f4'),
                },
            }
        ),
        (
            {
                'exclude': ['save_value'],
            },
            {
                'exclude': ['save_value'],
            },
            {
                'action': {'$nin': ['save_value']},
            }
        ),
    ]
)
@pytest.mark.asyncenv('async')
def test_client_logs_query_model(params, expected_service, expected_mongo):
    client_logs_query = models.ClientLogsQuery(**params)
    assert client_logs_query.to_service() == expected_service
    assert client_logs_query.to_mongo() == expected_mongo
