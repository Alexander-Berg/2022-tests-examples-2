import bson
import pytest

from taxi.util import dates

from audit import extended_models
from audit.generated.service.swagger import models


@pytest.mark.parametrize(
    'query, expected',
    [
        ({}, {}),
        (
            {
                'ticket': 'ticket-1',
                'ticket_queue': 'ticket',
                'id': '000000000000000000000001',
                'id_till': '000000000000000000000002',
                'action': 'action1',
                'actions': ['action1', 'action2'],
                'home_zone': 'ru',
                'conditions': {'p': 'card'},
                'arguments_ids': ['000000000000000000000002', 'not_object_id'],
                'arguments_id': 'not_object_id',
                'date_till': '2019-04-24T21:00:00+03:00',
                'date_from': '2019-04-24T22:00:00+03:00',
                'check_task_id_exists': True,
                'clids_and_numbers': [{'clid': '1', 'car_number': '3'}],
            },
            {
                'ticket': 'ticket-1',
                '_id': bson.ObjectId('000000000000000000000001'),
                'action': 'action1',
                'arguments.request.home_zone': 'ru',
                'arguments.cn': {'p': 'card'},
                'arguments._id': {'$in': ['not_object_id']},
                'timestamp': {
                    '$lte': dates.parse_timestring(
                        '2019-04-24T21:00:00+03:00',
                    ),
                    '$gte': dates.parse_timestring(
                        '2019-04-24T22:00:00+03:00',
                    ),
                },
                'arguments.response.task_id': {'$exists': True},
                'arguments.request.items': {
                    '$in': [{'clid': '1', 'car_number': '3'}],
                },
            },
        ),
        (
            {
                'ticket_queue': 'ticket',
                'id_till': '000000000000000000000002',
                'actions': ['action1', 'action2'],
                'home_zone': 'ru',
                'conditions': {'p': 'card'},
                'arguments_ids': ['000000000000000000000002', 'not_object_id'],
                'date_till': '2019-04-24T21:00:00+03:00',
            },
            {
                'ticket': {'$regex': '^ticket\\-'},
                '_id': {'$lt': bson.ObjectId('000000000000000000000002')},
                'action': {'$in': ['action1', 'action2']},
                'arguments.request.home_zone': 'ru',
                'arguments.cn': {'p': 'card'},
                'arguments._id': {
                    '$in': [
                        bson.ObjectId('000000000000000000000002'),
                        '000000000000000000000002',
                        'not_object_id',
                    ],
                },
                'timestamp': {
                    '$lte': dates.parse_timestring(
                        '2019-04-24T21:00:00+03:00',
                    ),
                },
            },
        ),
    ],
)
async def test_robot_logs_query_serialize(query, expected):
    robot_query = models.api.RobotLogsQuery.deserialize(query)
    extended_robot_query = extended_models.RobotLogsQuery(robot_query)
    assert extended_robot_query.serialize() == expected


async def test_extended_log(db):
    doc = await db.log_admin.find_one({})
    expected_deserialized_doc = {
        'id': '000000000000000000000001',
        'action': 'action_1',
        'timestamp': '2018-11-01T21:00:00.000Z',
        'login': 'malenko',
        'arguments': {},
    }
    models_log = extended_models.LogRecord.deserialize(
        expected_deserialized_doc,
    )
    extended_log = extended_models.LogRecord(models_log)
    serialized_log = extended_log.serialize()
    assert doc == serialized_log
