import json

import pytest

from sandbox.projects.browser.severity_calculator.BrowserSeverityCalculateDau import yql_script


ITEM_WITH_STRING_VALUE3 = {
    'params': {
        'mps': {
            'main_menu': {
                'field_name': 'field',
            },
        },
    },
    'client_id': 'passman',
}
ITEM_WITH_STRING_VALUE2 = {
    'params': {
        'a_show_save_bubble': {
            'a_yandex': 'disabled',
        },
    },
    'client_id': 'cardman',
}
ITEM_WITH_STRING_VALUE = {
    'params': {
        'a_show': 'OutdatedPlugin',
    },
    'client_id': 'infobars',
}

ITEM_WITH_NUMERIC_VALUE3 = {
    'params': {
        'mps': {
            'main_menu': {
                'fields': 4,
            },
        },
    },
    'client_id': 'passman',
}
ITEM_WITH_NUMERIC_VALUE2 = {
    'params': {
        'a_submit': {
            'submit_time': 81,
        },
    },
    'client_id': 'cardman',
}
ITEM_WITH_NUMERIC_VALUE = {
    'params': {
        'submit_time': 81,
    },
    'client_id': 'cardman',
}


@pytest.mark.parametrize(('item', 'component', 'parameter', 'value', 'value2', 'value3', 'result'), (
    # 1. Values, values2 and values3 are specified.
    # Values3 are equal.
    (ITEM_WITH_STRING_VALUE3, 'passman', 'mps', 'main_menu', 'field_name', 'field', True),
    # Values3 are not equal.
    (ITEM_WITH_STRING_VALUE3, 'passman', 'mps', 'main_menu', 'field_name', 'other_field', False),
    # Values2 are not equal.
    (ITEM_WITH_STRING_VALUE3, 'passman', 'mps', 'main_menu', 'unknown', 'field', False),
    # Values are not equal.
    (ITEM_WITH_STRING_VALUE3, 'passman', 'mps', 'unknown', 'field_name', 'field', False),
    # Parameters are not equal.
    (ITEM_WITH_STRING_VALUE3, 'passman', 'unknown', 'main_menu', 'field_name', 'field', False),
    # Components are not equal.
    (ITEM_WITH_STRING_VALUE3, 'unknown', 'mps', 'main_menu', 'field_name', 'field', False),
    # Value3 is numeric.
    (ITEM_WITH_NUMERIC_VALUE3, 'passman', 'mps', 'main_menu', 'fields', 'fields_num', False),

    # 2. Values and values2 are specified, values3 are not specified.
    # Values2 are equal.
    (ITEM_WITH_STRING_VALUE2, 'cardman', 'a_show_save_bubble', 'a_yandex', 'disabled', None, True),
    # Values2 are not equal.
    (ITEM_WITH_STRING_VALUE2, 'cardman', 'a_show_save_bubble', 'a_yandex', 'on', None, False),
    # Values are not equal.
    (ITEM_WITH_STRING_VALUE2, 'cardman', 'a_show_save_bubble', 'unknown', 'disabled', None, False),
    # Parameters are not equal.
    (ITEM_WITH_STRING_VALUE2, 'cardman', 'unknown', 'a_yandex', 'on', None, False),
    # Components are not equal.
    (ITEM_WITH_STRING_VALUE2, 'unknown', 'a_show_save_bubble', 'a_yandex', 'disabled', None, False),
    # Value2 is numeric.
    (ITEM_WITH_NUMERIC_VALUE2, 'cardman', 'a_submit', 'submit_time', 'some_time', None, False),
    # Value2 is dict with specified key.
    (ITEM_WITH_STRING_VALUE3, 'passman', 'mps', 'main_menu', 'field_name', None, True),
    # Value2 is dict without specified key.
    (ITEM_WITH_STRING_VALUE3, 'passman', 'mps', 'main_menu', 'unknown', None, False),

    # 3. Values are specified, values2 and values3 are not specified.
    # Values are equal.
    (ITEM_WITH_STRING_VALUE, 'infobars', 'a_show', 'OutdatedPlugin', None, None, True),
    # Values are not equal.
    (ITEM_WITH_STRING_VALUE, 'infobars', 'a_show', 'UnknownPlugin', None, None, False),
    # Parameters are not equal.
    (ITEM_WITH_STRING_VALUE, 'infobars', 'unknown', 'OutdatedPlugin', None, None, False),
    # Components are not equal.
    (ITEM_WITH_STRING_VALUE, 'unknown', 'a_show', 'OutdatedPlugin', None, None, False),
    # Value is numeric.
    (ITEM_WITH_NUMERIC_VALUE, 'cardman', 'submit_time', 'some_time', None, None, False),
    # Value is dict with specified key.
    (ITEM_WITH_STRING_VALUE2, 'cardman', 'a_show_save_bubble', 'a_yandex', None, None, True),
    # Value is dict without specified key.
    (ITEM_WITH_STRING_VALUE2, 'cardman', 'a_show_save_bubble', 'unknown', None, None, False),

    # 4. Values, values2 and values3 are not specified.
    # There is such parameter.
    (ITEM_WITH_STRING_VALUE, 'infobars', 'a_show', None, None, None, True),
    # There are no such parameter.
    (ITEM_WITH_STRING_VALUE, 'infobars', 'unknown', None, None, None, False),
))
def test_strings(item, component, parameter, value, value2, value3, result):
    decoded_bundle = json.dumps([item])
    value = ('string', value) if value else None
    value2 = ('string', value2) if value2 else None
    value3 = ('string', value3) if value3 else None
    assert yql_script.contains_conditions(decoded_bundle, [[(component, parameter, value, value2, value3)]]) == result


@pytest.mark.parametrize(('item', 'component', 'parameter', 'value', 'value2', 'value3', 'result'), (
    # 1. Values, values2 and values3 are specified.
    # Value3 is in specified interval.
    (ITEM_WITH_NUMERIC_VALUE3, 'passman', 'mps', 'main_menu', 'fields', (2, 6), True),
    (ITEM_WITH_NUMERIC_VALUE3, 'passman', 'mps', 'main_menu', 'fields', (None, 6), True),
    (ITEM_WITH_NUMERIC_VALUE3, 'passman', 'mps', 'main_menu', 'fields', (2, None), True),
    (ITEM_WITH_NUMERIC_VALUE3, 'passman', 'mps', 'main_menu', 'fields', (None, None), True),
    # Value3 is not in specified interval.
    (ITEM_WITH_NUMERIC_VALUE3, 'passman', 'mps', 'main_menu', 'fields', (0, 2), False),
    (ITEM_WITH_NUMERIC_VALUE3, 'passman', 'mps', 'main_menu', 'fields', (None, 2), False),
    # Values2 are not equal.
    (ITEM_WITH_NUMERIC_VALUE3, 'passman', 'mps', 'main_menu', 'unknown', (2, 6), False),
    # Values are not equal.
    (ITEM_WITH_NUMERIC_VALUE3, 'passman', 'mps', 'unknown', 'fields', (2, 6), False),
    # Parameters are not equal.
    (ITEM_WITH_NUMERIC_VALUE3, 'passman', 'unknown', 'main_menu', 'fields', (2, 6), False),
    # Components are not equal.
    (ITEM_WITH_NUMERIC_VALUE3, 'unknown', 'mps', 'main_menu', 'fields', (2, 6), False),
    # Value3 is string.
    (ITEM_WITH_STRING_VALUE3, 'passman', 'mps', 'main_menu', 'field_name', (2, 6), False),

    # 2. Values and values2 are specified, values3 are not specified.
    # Value2 is in specified interval.
    (ITEM_WITH_NUMERIC_VALUE2, 'cardman', 'a_submit', 'submit_time', (75, 85), None, True),
    (ITEM_WITH_NUMERIC_VALUE2, 'cardman', 'a_submit', 'submit_time', (None, 85), None, True),
    (ITEM_WITH_NUMERIC_VALUE2, 'cardman', 'a_submit', 'submit_time', (75, None), None, True),
    (ITEM_WITH_NUMERIC_VALUE2, 'cardman', 'a_submit', 'submit_time', (None, None), None, True),
    # Value2 is not in specified interval.
    (ITEM_WITH_NUMERIC_VALUE2, 'cardman', 'a_submit', 'submit_time', (65, 75), None, False),
    (ITEM_WITH_NUMERIC_VALUE2, 'cardman', 'a_submit', 'submit_time', (None, 75), None, False),
    # Values are not equal.
    (ITEM_WITH_NUMERIC_VALUE2, 'cardman', 'a_submit', 'unknown', (75, 85), None, False),
    # Parameters are not equal.
    (ITEM_WITH_NUMERIC_VALUE2, 'cardman', 'unknown', 'submit_time', (75, 85), None, False),
    # Components are not equal.
    (ITEM_WITH_NUMERIC_VALUE2, 'unknown', 'a_submit', 'submit_time', (75, 85), None, False),
    # Value2 is string.
    (ITEM_WITH_STRING_VALUE2, 'cardman', 'a_show_save_bubble', 'a_yandex', (0, 10), None, False),

    # 3. Values are specified, values2 and values3 are not specified.
    # Value is in specified interval.
    (ITEM_WITH_NUMERIC_VALUE, 'cardman', 'submit_time', (75, 85), None, None, True),
    (ITEM_WITH_NUMERIC_VALUE, 'cardman', 'submit_time', (None, 85), None, None, True),
    (ITEM_WITH_NUMERIC_VALUE, 'cardman', 'submit_time', (75, None), None, None, True),
    (ITEM_WITH_NUMERIC_VALUE, 'cardman', 'submit_time', (None, None), None, None, True),
    # Value is not in specified interval.
    (ITEM_WITH_NUMERIC_VALUE, 'cardman', 'submit_time', (65, 75), None, None, False),
    (ITEM_WITH_NUMERIC_VALUE, 'cardman', 'submit_time', (None, 75), None, None, False),
    # Parameters are not equal.
    (ITEM_WITH_NUMERIC_VALUE, 'cardman', 'unknown', (75, 85), None, None, False),
    # Components are not equal.
    (ITEM_WITH_NUMERIC_VALUE, 'unknown', 'submit_time', (75, 85), None, None, False),
    # Value is string.
    (ITEM_WITH_STRING_VALUE, 'infobars', 'a_show', (0, 10), None, None, False),
))
def test_intervals(item, component, parameter, value, value2, value3, result):
    decoded_bundle = json.dumps([item])
    if value3:
        value = ('string', value)
        value2 = ('string', value2)
        value3 = ('interval', value3)
    elif value2:
        value = ('string', value)
        value2 = ('interval', value2)
    else:
        value = ('interval', value)
    assert yql_script.contains_conditions(decoded_bundle, [[(component, parameter, value, value2, value3)]]) == result


@pytest.mark.parametrize('decoded_bundle', (
    # Decoded bundle is not JSON.
    '',
    'string',
    # No `client_id`.
    json.dumps({
        'params': {
            'parameter': {
                'value': {
                    'value2': 'value3',
                },
            },
        },
    }),
    # `params` is not dict.
    json.dumps({
        'client_id': 'component',
        'params': 'params',
    }),
))
def test_bad_data(decoded_bundle):
    assert not yql_script.contains_conditions(decoded_bundle, [[('component', 'parameter', 'value', 'value2', 'value3')]])


def test_disjunction():
    conditions = [
        [('infobars', 'a_show', None, None, None)],
        [('cardman', 'a_show_save_bubble', ('string', 'a_yandex'), None, None)],
    ]
    assert yql_script.contains_conditions(
        json.dumps([ITEM_WITH_STRING_VALUE]), conditions)
    assert yql_script.contains_conditions(
        json.dumps([ITEM_WITH_STRING_VALUE2]), conditions)
    assert not yql_script.contains_conditions(
        json.dumps([ITEM_WITH_NUMERIC_VALUE2]), conditions)
