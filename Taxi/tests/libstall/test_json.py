import datetime
import json

import dateutil.tz

from libstall import json_pp


class TJ:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def pure_python(self):
        return {
            'a': self.a,
            'b': self.b
        }


def test_json(tap):
    tap.plan(1)
    tap.eq(
        json_pp.dumps(TJ(1, 2)),
        json.dumps({'a': 1, 'b': 2}).replace(' ', ''),
        'dumps',
    )
    tap()


def test_datetime(tap):
    with tap.plan(2):
        now = datetime.datetime.now().timestamp()
        o = {
            'datetime':
                datetime.datetime.fromtimestamp(now, dateutil.tz.tzlocal()),
        }

        o['date'] = o['datetime'].date()

        tap.ok(o, 'объект собран')
        tap.like(
            json_pp.dumps(o),
            r'"datetime":\s*'
            r'"\d{4}(-\d{2}){2}T\d{2}(:\d{2}){2}(\.\d+)?([+-]\d{2}:\d{2})?"',
            'Дата время соответствуют регекспу такси')
