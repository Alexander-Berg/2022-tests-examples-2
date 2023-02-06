import dataclasses
import datetime
import typing

from feeds_admin import utils


DEFAULT_TIMEZONE = datetime.timezone(offset=datetime.timedelta(hours=3))
DATE = datetime.date(year=2020, month=10, day=30)
TIME = datetime.time(
    hour=1, minute=2, second=3, microsecond=4, tzinfo=DEFAULT_TIMEZONE,
)
DATETIME = datetime.datetime(
    year=2020,
    month=10,
    day=30,
    hour=1,
    minute=2,
    second=3,
    microsecond=4,
    tzinfo=DEFAULT_TIMEZONE,
)
TIMEDELTA = datetime.timedelta(days=1)
SUB = 'test_feeds_admin.utils.test_dataclasses.Sub'


@dataclasses.dataclass
class Sub:
    value: str


class NamespaceClass:
    @dataclasses.dataclass
    class Internal:
        pass


@dataclasses.dataclass
class Class:
    int: int
    string: str
    list: typing.List
    dict: typing.Dict
    opt: typing.Optional[str]
    time: datetime.time
    date: datetime.date
    dttm: datetime.datetime
    delta: datetime.timedelta
    sub: Sub


DESERIALIZED = Class(
    int=123,
    string='Hello',
    list=[3, 'World', Sub(value='li.sub')],
    dict={'i': 3, 's': 'World', 'sub': Sub(value='di.sub')},
    opt=None,
    time=TIME,
    date=DATE,
    dttm=DATETIME,
    delta=TIMEDELTA,
    sub=Sub(value='sub'),
)

SERIALIZED = {
    'class_': 'test_feeds_admin.utils.test_dataclasses.Class',
    'int': 123,
    'string': 'Hello',
    'list': [3, 'World', {'class_': SUB, 'value': 'li.sub'}],
    'dict': {'i': 3, 's': 'World', 'sub': {'class_': SUB, 'value': 'di.sub'}},
    'opt': None,
    'time': {'class_': 'datetime.time', 'value': TIME.isoformat()},
    'date': {'class_': 'datetime.date', 'value': DATE.isoformat()},
    'dttm': {'class_': 'datetime.datetime', 'value': DATETIME.isoformat()},
    'delta': {
        'class_': 'datetime.timedelta',
        'value': TIMEDELTA.total_seconds(),
    },
    'sub': {'class_': SUB, 'value': 'sub'},
}


def test_to_dict():
    assert utils.dataclasses.to_dict(DESERIALIZED) == SERIALIZED


def test_from_dict():
    assert utils.dataclasses.from_dict(SERIALIZED) == DESERIALIZED


def test_to_dict_from_dict():
    assert (
        utils.dataclasses.from_dict(utils.dataclasses.to_dict(DESERIALIZED))
        == DESERIALIZED
    )
