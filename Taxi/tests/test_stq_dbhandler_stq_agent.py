import datetime

import bson
import pytest

from stq.external import stq_agent


@pytest.mark.parametrize('data,expected', [
    (
        '{"foo": "bar"}', {'foo': 'bar'}
    ),
    (
        '{"_id": {"$oid": "5ca5e15d063b7f084f01b832"}}',
        {'_id': bson.ObjectId('5ca5e15d063b7f084f01b832')}
    ),
    (
        '{"updated": {"$date": 1554375101127}}',
        {'updated': datetime.datetime(2019, 4, 4, 10, 51, 41, 127000)}
    ),
])
@pytest.mark.nofilldb
def test_load_json_response(data, expected):
    result = stq_agent._load_json_response(data)
    assert result == expected


@pytest.mark.parametrize('data,expected', [
    (
        '{"$date": 1554375101127}',
        datetime.datetime(2019, 4, 4, 10, 51, 41, 127000)
    ),
    (
        '{"$date": "2019-04-25T15:31:39.123Z"}',
        datetime.datetime(2019, 4, 25, 15, 31, 39, 123000)
    ),
    (
        '{"$date": "2019-04-25T15:31:39Z"}',
        datetime.datetime(2019, 4, 25, 15, 31, 39, 0)
    ),
])
@pytest.mark.nofilldb
def test_load_json_datetime(data, expected):
    result = stq_agent._load_json_response(data)
    assert result == expected
