import json as json_original
from libstall import json_pp as json


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
        json.dumps(TJ(1, 2)).replace(' ', ''),
        json_original.dumps({'a': 1, 'b': 2}).replace(' ', ''),
        'dumps'
    )
    tap()
