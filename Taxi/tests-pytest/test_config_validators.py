import pytest

from taxi.config import validator


@pytest.mark.parametrize('validator_func,value', [
    (validator.integer, 42),
    (validator.number, 3.14),
    (validator.string, 'a string'),
    (validator.regex('^\w+ \w+$'), 'a string'),
    (validator.gte(0), 0),
    (validator.gte(0), 1),
    (validator.gt(0), 1),
    (validator.eq(1), 1),
    (validator.lt(0), -1),
    (validator.lte(0), 0),
    (validator.lte(0), -1),
    (validator.dictionary({'a': validator.integer}), {'a': 1}),
    (validator.point, [3.14, 3.14]),
    (validator.zone_polygon, [[3.14, 3.14], [4.13, 4.13], [5.12, 5.12]]),
    (validator.zone_circle, {'center': [3.14, 3.14], 'radius': 1}),
    (validator.zone_variant,
     {'type': 'circle', 'data': {'center': [3.14, 3.14], 'radius': 1}}),
    (validator.zone_variant,
     {'type': 'polygon', 'data': [[3, 3], [4, 4], [5, 5]]}),
])
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_validators_ok(validator_func, value):
    assert (yield validator_func(value)) is None


@pytest.mark.parametrize('target,missing_ok,extra_ok,result', [
    (
        {'key1': True, 'key2': 1, 'key3': 'value3'},
        False, False,
        None
    ),

    (
        [],
        False, False,
        validator.DICTIONARY_ERROR
    ),

    (
        {'key1': True, 'key2': 1, 'key3': 'value3', 'key4': None},
        False, False,
        validator.EXTRA_KEY_ERROR % 'key4'
    ),

    (
        {'key1': True, 'key2': 1, 'key3': 'value3', 'key4': None},
        False, True,
        None
    ),

    (
        {'key1': True, 'key2': 1},
        False, False,
        validator.MISSING_KEY_ERROR % 'key3'
    ),

    (
        {'key1': True, 'key2': 1},
        True, False,
        None
    ),

    (
        {'key1': None, 'key2': 1, 'key3': 'value3'},
        False, False,
        'at key1: ' + validator.BOOLEAN_ERROR
    ),

    (
        {'key1': False, 'key2': -1, 'key3': 'value3'},
        False, False,
        'at key2: ' + validator.GT_ERROR % (-1, 0)
    ),

    (
        {'key1': False, 'key2': -1, 'key3': None},
        False, False,
        'at key3: ' + validator.STRING_ERROR
    ),
])
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_dictionary_validator(target, missing_ok, extra_ok, result):
    validator_func = validator.dictionary({
        'key1': validator.boolean,
        'key2': validator.gt(0),
        'key3': validator.string
    }, missing_ok=missing_ok, extra_ok=extra_ok)
    assert (yield validator_func(target)) == result


@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb(_fill=None)
@pytest.mark.config(ALL_CATEGORIES=['econom', 'vip'])
@pytest.mark.parametrize('tariff_name', ['vip', 'pool'])
def test_tariff_validator_blocking(tariff_name):
    result = validator.tariff(tariff_name)
    if tariff_name == 'vip':
        assert result is None
    else:
        assert result


@pytest.mark.asyncenv('async')
@pytest.mark.filldb(_fill=None)
@pytest.mark.config(ALL_CATEGORIES=['econom', 'vip'])
@pytest.mark.parametrize('tariff_name', ['vip', 'pool'])
@pytest.inlineCallbacks
def test_tariff_validator_async(tariff_name):
    yield validator.warmup(True)
    if tariff_name == 'vip':
        assert validator.tariff(tariff_name) is None
    else:
        assert validator.tariff(tariff_name)


@pytest.mark.parametrize('value,expected_error', [
    (
        [],
        None,
    ),
    (
        [
            {
                'enabled': True,
                'export_tag': 'qwerty',
            },
        ],
        None,
    ),
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
            'at created_before: ' + validator.DATETIME_STRING_ERROR + ' or ' +
            validator.REGEX_ERROR % r'^(?:\d+d)?(?:\d+h)?(?:\d+m)?(?:\d+s)?$'
        ),
    ),
    (
        [
            {},
        ],
        validator.MISSING_KEY_ERROR % 'export_tag',
    ),
    (
        [
            {
                'enabled': True,
                'export_tag': 'qwerty',
                'qwerty': 'asdf',
            },
        ],
        None,
    ),
    (
        [
            {
                'enabled': True,
                'export_tag': 'qwerty',
                'tags_all': 'qwe',
            },
        ],
        'at tags_all: ' + validator.SEQUENCE_ERROR,
    ),
    (
        [
            {
                'enabled': True,
                'export_tag': 'qwerty',
                'tags_all': ['qwe'],
            },
        ],
        None,
    ),
    (
        [
            {
                'enabled': 123,
                'export_tag': 'qwerty',
            },
        ],
        'at enabled: ' + validator.BOOLEAN_ERROR,
    ),
    (
        [
            {
                'enabled': True,
                'export_tag': 'qwerty',
                'meta_has': {
                    'qwe': 'asd',
                },
            },
        ],
        None,
    ),
    (
        [
            {
                'enabled': True,
                'export_tag': 'qwerty',
                'meta_has': {
                    'qwe': ['asd', 'fgh'],
                },
            },
        ],
        None,
    ),
    (
        [
            {
                'enabled': True,
                'export_tag': 'qwerty',
                'meta_has': 'qwerty',
            },
        ],
        'at meta_has: ' + validator.DICTIONARY_ERROR,
    ),
    (
        [
            {
                'enabled': True,
                'export_tag': 'qwerty',
                'status': '123',
            },
        ],
        None,
    ),
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
        [
            {
                'enabled': True,
                'export_tag': 'qwerty',
                'status': 123,
            },
        ],
        'at status: ' + validator.STRING_ERROR + ' or '
        + validator.SEQUENCE_ERROR,
    ),
])
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_chatterbox_rules_validator(value, expected_error):
    error = yield validator.chatterbox_export_rules_config(value)
    assert error == expected_error


@pytest.mark.parametrize('value, expected_error', [
     ({}, 'has missing key: __default__'),
    (
        {
            '__default__': {
                '__default__': {
                    '__default__': {
                        'taxi_host': 'some_host_default'
                    }
                }
            },
        },
        None),
    (
        {
            '__default__': {
                '__default__': {
                    '__default__': {
                        'taxi_host': 'some_host_default'
                    }
                }
            },
            'yango': {
                '__default__': {
                    '__default__': {}
                }
            }
        },
        None
    ),
    (
        {
            '__default__': {
                '__default__': {
                    '__default__': {
                        'taxi_host': 'some_host_default'
                    }
                }
            },
            'unknown_app': {
                '__default__': {
                    '__default__': {}
                }
            }
        },
        None,
    ),
    (
        {
            '__default__': {
                '__default__': {
                    '__default__': {
                        'taxi_host': 'some_host_default'
                    }
                }
            },
            'yango': {
                '__default__': {
                    '__default__': {}
                },
                'rus': {
                    '__default__': {}
                }
            }
        },
        None
    ),
    (
        {
            '__default__': {
                '__default__': {
                    '__default__': {}
                }
            },
            'yango': {
                '__default__': {
                    '__default__': {}
                },
                'russia': {
                    '__default__': {
                    }
                }
            }
        },
        "russia not in ['__default__', 'common'] or must be a "
        "lowercase ISO 3166-1 three-letter country code"
    ),
    (
        {
            '__default__': {
                '__default__': {
                    '__default__': {
                        'taxi_host': 'some_host_default'
                    }
                }
            },
            'yango': {
                '__default__': {
                    '__default__': {}
                },
                'rus': {
                    '__default__': {},
                    'ru': {}
                }
            }
        },
        None
    ),
    (
        {
            '__default__': {
                '__default__': {
                    '__default__': {
                        'taxi_host': 'some_host_default'
                    }
                }
            },
            'yango': {
                '__default__': {
                    '__default__': {}
                },
                'rus': {
                    '__default__': {},
                    'ru': {
                        'taxi_host': 'some_host'
                    }
                }
            }
        },
        None
    ),
    (
        {
            '__default__': {
                '__default__': {
                    '__default__': {
                        'taxi_host': 'some_host_default'
                    }
                }
            },
            'yango': {
                '__default__': {
                    '__default__': {

                    }
                },
                'rus': {
                    '__default__': {
                    },
                    'RURU': {
                        'taxi_host': 'some_host'
                    }
                }
            }
        },
        'RURU must equal to __default__ or must be a lowercase '
        'ISO 639-1 two-letter language code'
    ),
    (
        {
            '__default__': {
                '__default__': {
                    '__default__': {
                        'receipt_mode': 'bill'
                    }
                }
            }
        },
        None
    ),
])
def test_ride_report_params_validator(value, expected_error):
    validator_func = validator.ride_report_extended_config()
    error = validator_func(value)
    assert error == expected_error


@pytest.mark.parametrize('value, expected_error', [
    (
        {
            'sync_delay': {
                '__default__': {'warning': 10, 'critical': 20},
                'some_rule': {'warning': 20, 'critical': 30},
            },
            'archiving': {
                '__default__': {'warning': 10, 'critical': 20},
            }
        },
        None,
    ),
    (
        {
            'sync_delay': {
                '__default__': {'warning': 10, 'critical': 20},
                'some_rule': {'warning': 20, 'critical': 30},
            },
            'archiving': {
                '__default__': {'bad_key': 10, 'bad_key_2': 20},
            }
        },
        validator.EXTRA_KEY_ERROR % 'bad_key',
    ),
    (
        {
            'sync_delay': {
                '__default__': {'warning': 10, 'critical': 20},
                'some_rule': {'warning': 20, 'critical': 30},
            },
            'archiving': 10,
        },
        validator.ONE_TYPE_VALUES % (['sync_delay'], ['archiving']),
    ),
    (
        {
            'sync_delay': {
                '__default__': {'warning': 10, 'critical': 20},
                'some_rule': {'warning': 20, 'critical': 30},
            },
            'archiving': {
                '__default__': {},
            }
        },
        validator.MISSING_KEY_ERROR % 'critical',
    ),
    (
        {
            'archiving_delay': {
                '__default__': {
                    'critical': 3600,
                    'warning': 1800,
                },
            },
            'sync_delay': {
                '__default__': {
                    'disabled_rules_sync_delay': {
                        'critical': 172800,
                        'warning': 86400,
                    },
                    'sync_delay': {
                        'critical': 3600,
                        'warning': 1800,
                    },
                },
                '__overrides__': [
                    {
                        'items': [
                            'rule-to-arnold',
                            'rule-to-hahn',
                        ],
                        'value': {
                            'sync_delay': {
                                'critical': 6000,
                                'warning': 6000,
                            },
                        },
                    }
                ]
            }
        },
        None,
    )
])
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_monrun_checks_config_validator(value, expected_error):
    error = yield validator.monrun_checks_config(value)
    assert error == expected_error
