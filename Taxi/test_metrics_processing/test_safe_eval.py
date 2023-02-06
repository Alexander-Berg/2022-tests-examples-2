import datetime

import pytest

from metrics_processing.utils import safe_eval


class Driver:
    def __init__(self):
        self.udid = 'udid'
        self.licenses = {'license_1', 'license_2'}
        self.activity = 89
        self.tags = {'good', 'bad'}
        self.created = datetime.datetime.utcnow()


class Event:
    def __init__(self):
        self.event_id = 'id'
        self.timestamp = datetime.datetime.utcnow()
        self.udid = 'udid'
        self.event_type = 'order'
        self.name = 'complete'
        self.tags = ['q1', 'q2']
        self.extra_data_json = {'sp': 2.3, 'sp_alpha': None}


CONTEXT = {'driver': Driver(), 'event': Event()}
WHITELIST = {
    'driver',
    'event',
    'activity',
    'tags',
    'name',
    'event_type',
    'timestamp',
    'created',
    'extra_data_json',
    'some_string',
}


@pytest.mark.parametrize(
    'expr, expected',
    [
        ('None', False),
        ('""', False),
        ('not 0', True),
        ('not 1', False),
        ('None or None', False),
        ('None or True', True),
        ('None is None', True),
        ('True and False', False),
        ('True or False', True),
        ('False or False', False),
        ('False is not True', True),
        ('False and False', False),
        ('True and ""', False),
        ('False or 0 or 21', True),
        ('7 and 4 and 0', False),
        ('0 or 21', True),
        ('21 - 21 or 21', True),
        ('21 - 21 and 21', False),
        ('(-9) ** 3 == -729', True),
        ('0 ** 444 == 0', True),
        ('999 == 99 + 900 and True', True),
        ('999 != 99 + 900 and True', False),
        ('not (None and 3)', True),
        ('not not not None is True', True),
        ('(5 > 6) or not 0', True),
        ('7 >= (None or 5)', True),
        ('False is not 31 - 30', True),
        ('not 1 or not 2 or not "False"', False),
        ('"String" * (3 and 0)', False),
        ('"string"[2] == "r"', True),
        ('"android" in (["android", "iphone"] + ["windows"])', True),
        ('("a", "b") and ()', False),
        ('"c" in {"a", "b", "d"}', False),
        ('{"a": 1, "b": 2, 3: "c"}["b"] == 2', True),
    ],
)
def test_basic(expr, expected):
    assert safe_eval.evaluate(expr) == expected


@pytest.mark.parametrize(
    'expr, expected',
    [
        ('driver.activity == 89', True),
        ('driver.activity > 80 and "q3" in event.tags', False),
        ('event.event_type == "order" and event.name == "complete"', True),
        ('not driver.tags or not event.tags or not driver.activity', False),
        ('"good" in (None or driver.tags)', True),
        ('event.timestamp >= driver.created', True),
        ('event.extra_data_json["sp"] < 2.3', False),
        ('not event.extra_data_json["sp_alpha"]', True),
        ('event.tags[1] == "q2"', True),
    ],
)
def test_bool_with_context(expr, expected):
    assert (
        safe_eval.evaluate(
            expr,
            context=CONTEXT,
            settings=safe_eval.Settings(whitelist=WHITELIST),
        )
        == expected
    )


@pytest.mark.parametrize(
    'expr, expected',
    [
        ('driver.activity', 89),
        ('event.tags', ['q1', 'q2']),
        ('event.event_type == "order" and event.name == "complete"', True),
        ('driver.tags', {'good', 'bad'}),
        ('event.extra_data_json', {'sp': 2.3, 'sp_alpha': None}),
        ('event.extra_data_json["sp"]', 2.3),
        ('event.tags[1]', 'q2'),
        ('f\'{event.name}_{driver.activity}\'', 'complete_89'),
    ],
)
def test_execute_with_context(expr, expected):
    assert (
        safe_eval.execute(
            expr,
            context=CONTEXT,
            settings=safe_eval.Settings(whitelist=WHITELIST),
        )
        == expected
    )


@pytest.mark.parametrize(
    'expr, whitelist, exception',
    [
        # InvalidSyntaxError
        ('3 + <', None, safe_eval.InvalidSyntaxError),
        ('0 0 0', None, safe_eval.InvalidSyntaxError),
        ('ha-ha!', None, safe_eval.InvalidSyntaxError),
        # NotStatementError
        ('', None, safe_eval.NotStatementError),
        ('class q: pass', {'q', 'pass', 'class'}, safe_eval.NotStatementError),
        ('def foo(): return bar', None, safe_eval.NotStatementError),
        ('for i in "abc": i', None, safe_eval.NotStatementError),
        ('a=7', {'a'}, safe_eval.NotStatementError),
        ('driver.activity = 3', WHITELIST, safe_eval.NotStatementError),
        ('import sys', {'import', 'sys'}, safe_eval.NotStatementError),
        ('1==1\n2==2', None, safe_eval.NotStatementError),
        (
            'from taxi import money',
            {'from', 'taxi', 'import', 'money'},
            safe_eval.NotStatementError,
        ),
        # FeatureUnavailableError
        ('True if 3 > 2 else False', None, safe_eval.FeatureUnavailableError),
        ('len(event.tags) == 2', WHITELIST, safe_eval.FeatureUnavailableError),
        (
            '"reposition" in set(event.tags)',
            WHITELIST,
            safe_eval.FeatureUnavailableError,
        ),
        ('(lambda x: x + 1)(3)', WHITELIST, safe_eval.FeatureUnavailableError),
        ('[x for x in [1, 2, 3]]', None, safe_eval.FeatureUnavailableError),
        ('(x for x in [1, 2, 3])', None, safe_eval.FeatureUnavailableError),
        ('{x for x in [1, 2, 3]}', None, safe_eval.FeatureUnavailableError),
        (
            '{x: y for x in [1, 2, 3] for y in [1, 2, 3]}',
            None,
            safe_eval.FeatureUnavailableError,
        ),
        ('{"a", "b"} | {"c"}', None, safe_eval.FeatureUnavailableError),
        ('{"a", "b"} ^ {"c"}', None, safe_eval.FeatureUnavailableError),
        ('{"a", "b"} & {"c"}', None, safe_eval.FeatureUnavailableError),
        ('type(3)', None, safe_eval.FeatureUnavailableError),
        # NameNotDefinedError
        (
            '__name__ == "__main__"',
            {'__name__'},
            safe_eval.NameNotDefinedError,
        ),
        ('123 in rider.tags', None, safe_eval.NameNotDefinedError),
        # ForbiddenNameError
        ('123 in driver.licenses', WHITELIST, safe_eval.ForbiddenNameError),
        ('123 in rider.tags', WHITELIST, safe_eval.ForbiddenNameError),
        # ObjectOutOfLimitError
        ('9**9**9**9', None, safe_eval.ObjectOutOfLimitError),
        ('"multiply_me" * 10000', None, safe_eval.ObjectOutOfLimitError),
        ('driver.tags * 10000', WHITELIST, safe_eval.ObjectOutOfLimitError),
        pytest.param(
            'expr' * 10000,
            WHITELIST,
            safe_eval.ObjectOutOfLimitError,
            id='very_long_expr',
        ),
        # KeyError
        ('event.extra_data_json["non-existent-key"]', WHITELIST, KeyError),
    ],
)
def test_exceptions(expr, whitelist, exception):
    with pytest.raises(exception):
        safe_eval.evaluate(
            expr,
            context=CONTEXT,
            settings=safe_eval.Settings(whitelist=whitelist),
        )
