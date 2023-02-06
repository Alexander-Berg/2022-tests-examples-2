# pylint: skip-file
# flake8: noqa

# This code was migrated from taxi/backend
# see https://github.yandex-team.ru/taxi/backend/blob/develop/tests-pytest/test_config_validators.py

import pytest

from taxi_config_schemas.validation import validators


@pytest.mark.parametrize(
    'validator_func,value',
    [
        (validators.integer, 42),
        (validators.number, 3.14),
        (validators.string, 'a string'),
        (validators.regex('^\w+ \w+$'), 'a string'),
        (validators.gte(0), 0),
        (validators.gte(0), 1),
        (validators.gt(0), 1),
        (validators.eq(1), 1),
        (validators.lt(0), -1),
        (validators.lte(0), 0),
        (validators.lte(0), -1),
        (validators.dictionary({'a': validators.integer}), {'a': 1}),
        (validators.point, [3.14, 3.14]),
        (validators.zone_polygon, [[3.14, 3.14], [4.13, 4.13], [5.12, 5.12]]),
        (validators.zone_circle, {'center': [3.14, 3.14], 'radius': 1}),
        (
            validators.zone_variant,
            {'type': 'circle', 'data': {'center': [3.14, 3.14], 'radius': 1}},
        ),
        (
            validators.zone_variant,
            {'type': 'polygon', 'data': [[3, 3], [4, 4], [5, 5]]},
        ),
    ],
)
def test_validators_ok(validator_func, value):
    assert validator_func(value) is None


@pytest.mark.parametrize(
    'target,missing_ok,extra_ok,result',
    [
        ({'key1': True, 'key2': 1, 'key3': 'value3'}, False, False, None),
        ([], False, False, validators.DICTIONARY_ERROR),
        (
            {'key1': True, 'key2': 1, 'key3': 'value3', 'key4': None},
            False,
            False,
            validators.EXTRA_KEY_ERROR % 'key4',
        ),
        (
            {'key1': True, 'key2': 1, 'key3': 'value3', 'key4': None},
            False,
            True,
            None,
        ),
        (
            {'key1': True, 'key2': 1},
            False,
            False,
            validators.MISSING_KEY_ERROR % 'key3',
        ),
        ({'key1': True, 'key2': 1}, True, False, None),
        (
            {'key1': None, 'key2': 1, 'key3': 'value3'},
            False,
            False,
            'at key1: ' + validators.BOOLEAN_ERROR,
        ),
        (
            {'key1': False, 'key2': -1, 'key3': 'value3'},
            False,
            False,
            'at key2: ' + validators.GT_ERROR % (-1, 0),
        ),
        (
            {'key1': False, 'key2': 1, 'key3': None},
            False,
            False,
            'at key3: ' + validators.STRING_ERROR,
        ),
    ],
)
def test_dictionary_validator(target, missing_ok, extra_ok, result):
    validator_func = validators.dictionary(
        {
            'key1': validators.boolean,
            'key2': validators.gt(0),
            'key3': validators.string,
        },
        missing_ok=missing_ok,
        extra_ok=extra_ok,
    )
    assert validator_func(target) == result


@pytest.mark.config(ALL_CATEGORIES=['econom', 'vip'])
@pytest.mark.parametrize('tariff_name', ['vip', 'pool'])
def test_tariff_validator_async(web_app_client, tariff_name):
    if tariff_name == 'vip':
        assert validators.tariff(tariff_name) is None
    else:
        assert validators.tariff(tariff_name)


@pytest.mark.parametrize(
    'value,expected_error',
    [
        ([], None),
        ([{'enabled': True, 'export_tag': 'qwerty'}], None),
        (
            [
                {
                    'enabled': True,
                    'export_tag': 'qwerty',
                    'created_before': '1d2h3s',
                },
            ],
            None,
        ),
        (
            [
                {
                    'enabled': True,
                    'export_tag': 'qwerty',
                    'created_before': '2018-05-07 12:34:56',
                },
            ],
            None,
        ),
        (
            [
                {
                    'enabled': True,
                    'export_tag': 'qwerty',
                    'created_before': 'asdf',
                },
            ],
            (
                'at created_before: '
                + validators.DATETIME_STRING_ERROR
                + ' or '
                + validators.REGEX_ERROR
                % r'^(?:\d+d)?(?:\d+h)?(?:\d+m)?(?:\d+s)?$'
            ),
        ),
        ([{}], validators.MISSING_KEY_ERROR % 'export_tag'),
        ([{'enabled': True, 'export_tag': 'qwerty', 'qwerty': 'asdf'}], None),
        (
            [{'enabled': True, 'export_tag': 'qwerty', 'tags_all': 'qwe'}],
            'at tags_all: ' + validators.SEQUENCE_ERROR,
        ),
        (
            [{'enabled': True, 'export_tag': 'qwerty', 'tags_all': ['qwe']}],
            None,
        ),
        (
            [{'enabled': 123, 'export_tag': 'qwerty'}],
            'at enabled: ' + validators.BOOLEAN_ERROR,
        ),
        (
            [
                {
                    'enabled': True,
                    'export_tag': 'qwerty',
                    'meta_has': {'qwe': 'asd'},
                },
            ],
            None,
        ),
        (
            [
                {
                    'enabled': True,
                    'export_tag': 'qwerty',
                    'meta_has': {'qwe': ['asd', 'fgh']},
                },
            ],
            None,
        ),
        (
            [{'enabled': True, 'export_tag': 'qwerty', 'meta_has': 'qwerty'}],
            'at meta_has: ' + validators.DICTIONARY_ERROR,
        ),
        ([{'enabled': True, 'export_tag': 'qwerty', 'status': '123'}], None),
        (
            [
                {
                    'enabled': True,
                    'export_tag': 'qwerty',
                    'status': ['123', '456'],
                },
            ],
            None,
        ),
        (
            [{'enabled': True, 'export_tag': 'qwerty', 'status': 123}],
            'at status: '
            + validators.STRING_ERROR
            + ' or '
            + validators.SEQUENCE_ERROR,
        ),
    ],
)
def test_chatterbox_rules_validator(value, expected_error):
    error = validators.chatterbox_export_rules_config(value)
    assert error == expected_error


@pytest.mark.parametrize(
    'value, expected_error',
    [
        ({}, 'has missing key: __default__'),
        (
            {
                '__default__': {
                    '__default__': {
                        '__default__': {'taxi_host': 'some_host_default'},
                    },
                },
            },
            None,
        ),
        (
            {
                '__default__': {
                    '__default__': {
                        '__default__': {'taxi_host': 'some_host_default'},
                    },
                },
                'yango': {'__default__': {'__default__': {}}},
            },
            None,
        ),
        (
            {
                '__default__': {
                    '__default__': {
                        '__default__': {'taxi_host': 'some_host_default'},
                    },
                },
                'unknown_app': {'__default__': {'__default__': {}}},
            },
            None,
        ),
        (
            {
                '__default__': {
                    '__default__': {
                        '__default__': {'taxi_host': 'some_host_default'},
                    },
                },
                'yango': {
                    '__default__': {'__default__': {}},
                    'rus': {'__default__': {}},
                },
            },
            None,
        ),
        (
            {
                '__default__': {'__default__': {'__default__': {}}},
                'yango': {
                    '__default__': {'__default__': {}},
                    'russia': {'__default__': {}},
                },
            },
            'russia not in [\'__default__\', \'common\'] or must be a '
            'lowercase ISO 3166-1 three-letter country code',
        ),
        (
            {
                '__default__': {
                    '__default__': {
                        '__default__': {'taxi_host': 'some_host_default'},
                    },
                },
                'yango': {
                    '__default__': {'__default__': {}},
                    'rus': {'__default__': {}, 'ru': {}},
                },
            },
            None,
        ),
        (
            {
                '__default__': {
                    '__default__': {
                        '__default__': {'taxi_host': 'some_host_default'},
                    },
                },
                'yango': {
                    '__default__': {'__default__': {}},
                    'rus': {
                        '__default__': {},
                        'ru': {'taxi_host': 'some_host'},
                    },
                },
            },
            None,
        ),
        (
            {
                '__default__': {
                    '__default__': {
                        '__default__': {'taxi_host': 'some_host_default'},
                    },
                },
                'yango': {
                    '__default__': {'__default__': {}},
                    'rus': {
                        '__default__': {},
                        'RURU': {'taxi_host': 'some_host'},
                    },
                },
            },
            'RURU must equal to __default__ or must be a lowercase '
            'ISO 639-1 two-letter language code',
        ),
    ],
)
def test_ride_report_params_validator(value, expected_error):
    validator_func = validators.ride_report_extended_config()
    error = validator_func(value)
    assert error == expected_error


@pytest.mark.parametrize(
    'value, expected_error',
    [
        (
            {
                'sync_delay': {
                    '__default__': {'warning': 10, 'critical': 20},
                    'some_rule': {'warning': 20, 'critical': 30},
                },
                'archiving': {'__default__': {'warning': 10, 'critical': 20}},
            },
            None,
        ),
        (
            {
                'sync_delay': {
                    '__default__': {'warning': 10, 'critical': 20},
                    'some_rule': {'warning': 20, 'critical': 30},
                },
                'archiving': {'__default__': {'bad_key': 10, 'bad_key_2': 20}},
            },
            validators.EXTRA_KEY_ERROR % 'bad_key',
        ),
        (
            {
                'sync_delay': {
                    '__default__': {'warning': 10, 'critical': 20},
                    'some_rule': {'warning': 20, 'critical': 30},
                },
                'archiving': 10,
            },
            validators.ONE_TYPE_VALUES % (['sync_delay'], ['archiving']),
        ),
        (
            {
                'sync_delay': {
                    '__default__': {'warning': 10, 'critical': 20},
                    'some_rule': {'warning': 20, 'critical': 30},
                },
                'archiving': {'__default__': {}},
            },
            validators.MISSING_KEY_ERROR % 'critical',
        ),
        (
            {
                'archiving_delay': {
                    '__default__': {'critical': 3600, 'warning': 1800},
                },
                'sync_delay': {
                    '__default__': {
                        'disabled_rules_sync_delay': {
                            'critical': 172800,
                            'warning': 86400,
                        },
                        'sync_delay': {'critical': 3600, 'warning': 1800},
                    },
                    '__overrides__': [
                        {
                            'items': ['rule-to-arnold', 'rule-to-hahn'],
                            'value': {
                                'sync_delay': {
                                    'critical': 6000,
                                    'warning': 6000,
                                },
                            },
                        },
                    ],
                },
            },
            None,
        ),
    ],
)
def test_monrun_checks_config_validator(value, expected_error):
    error = validators.monrun_checks_config(value)
    assert error == expected_error
