import pytest
import datetime
import dateutil.parser

from ctaxi_pyml import example as pybind_objects
from taxi_pyml.example import objects as py_objects


def make_dt(year, month, day, hour, minute, second, offset_hour):
    return datetime.datetime(
        year,
        month,
        day,
        hour,
        minute,
        second,
        tzinfo=datetime.timezone(datetime.timedelta(0, 3600 * offset_hour, 0)),
    )


def test_timepoint_deserizelization_pybind():
    data = {'field': '1970-01-01T03:00:00+03:00', 'arr': []}
    obj = pybind_objects.TimePoint.deserialize(data)

    assert obj.field == datetime.datetime.fromtimestamp(0)


def test_timepoint_deserizelization_py():
    data = {'field': '1970-01-01T03:00:00+03:00', 'arr': []}
    obj = py_objects.TimePoint.deserialize(data)

    assert obj.field == make_dt(1970, 1, 1, 3, 0, 0, 3)


@pytest.fixture
def time_point_data():
    return {
        'field': '2017-04-04T15:32:22+03:00',
        'arr': ['2017-04-01T20:30:20Z', '2017-04-04T15:40:03+08:00'],
    }


def test_time_point_pybind(time_point_data):
    obj = pybind_objects.TimePoint.deserialize(time_point_data)

    def timestring_to_local_tz(timestring):
        return datetime.datetime.fromtimestamp(
            dateutil.parser.isoparse(timestring).timestamp(),
        )

    assert obj.field == timestring_to_local_tz('2017-04-04T15:32:22+03:00')
    assert obj.arr[0] == timestring_to_local_tz('2017-04-01T20:30:20Z')
    assert obj.arr[1] == timestring_to_local_tz('2017-04-04T15:40:03+08:00')

    after_serialize = obj.serialize()
    assert after_serialize == {
        'field': '2017-04-04T12:32:22+00:00',
        'arr': ['2017-04-01T20:30:20+00:00', '2017-04-04T07:40:03+00:00'],
    }

    obj2 = pybind_objects.TimePoint.deserialize(after_serialize)
    assert obj2 == obj

    assert obj2.serialize() == after_serialize


def test_time_point_py(time_point_data):
    obj = py_objects.TimePoint.deserialize(time_point_data)

    assert obj.field == make_dt(2017, 4, 4, 15, 32, 22, 3)
    assert obj.arr[0] == make_dt(2017, 4, 1, 20, 30, 20, 0)
    assert obj.arr[1] == make_dt(2017, 4, 4, 15, 40, 3, 8)

    after_serialize = obj.serialize()
    assert after_serialize == {
        'field': '2017-04-04T15:32:22+03:00',
        'arr': ['2017-04-01T20:30:20+00:00', '2017-04-04T15:40:03+08:00'],
    }

    obj2 = py_objects.TimePoint.deserialize(after_serialize)
    assert obj2 == obj

    assert obj2.serialize() == after_serialize
