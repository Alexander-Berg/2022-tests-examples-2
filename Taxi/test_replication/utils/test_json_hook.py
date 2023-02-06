import datetime
import decimal

from dateutil import tz
import pytest

from replication.utils import json_hook

_TEST_OBJ = object()


@pytest.mark.nofilldb
@pytest.mark.parametrize(
    'json_dumper,json_loader,doc,expected',
    [
        (
            json_hook.default_dumper,
            json_hook.default_loader,
            {'decimal': decimal.Decimal('12.3334')},
            '{"decimal": {"$decimal": "12.3334"}}',
        ),
        (
            json_hook.default_dumper,
            json_hook.default_loader,
            {'data': {'time': datetime.datetime(2025, 2, 5, 20, 0)}},
            '{"data": {"time": {"$datetime": "2025-02-05T20:00:00"}}}',
        ),
        (
            json_hook.default_dumper,
            json_hook.default_loader,
            {
                'tz': datetime.datetime(
                    2025, 2, 5, 20, 0, tzinfo=tz.gettz('Europe/Moscow'),
                ),
            },
            '{"tz": {"$datetime": "2025-02-05T20:00:00+03:00"}}',
        ),
        (
            json_hook.default_dumper,
            json_hook.default_loader,
            {
                'data': [
                    {'date': datetime.date(2025, 2, 5)},
                    123,
                    'xxx\\test',
                    'тест',
                    decimal.Decimal('12.01'),
                ],
            },
            '{"data": ['
            '{"date": {"$datetime_date": "2025-02-05"}}, '
            '123, '
            '"xxx\\\\test", '
            '"тест", '
            '{"$decimal": "12.01"}'
            ']}',
        ),
        (
            json_hook.Dumper(),
            json_hook.Loader(),
            {'abc': [1, 2, 3]},
            '{"abc": [1, 2, 3]}',
        ),
        (
            json_hook.Dumper(
                [
                    (
                        '$mock_obj',
                        lambda v: {'$mock_obj': 0} if v is _TEST_OBJ else None,
                    ),
                ],
            ),
            json_hook.Loader([('$mock_obj', lambda v: _TEST_OBJ)]),
            {'abc': [_TEST_OBJ, 1, 2]},
            '{"abc": [{"$mock_obj": 0}, 1, 2]}',
        ),
    ],
)
def test_json_hook(json_dumper, json_loader, doc, expected):
    assert json_dumper.dumps(doc) == expected
    assert json_loader.loads(expected) == doc
