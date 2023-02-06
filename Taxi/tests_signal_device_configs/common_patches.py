P1_FEATURES_JSON_PATCH = {
    'name': 'features.json',
    'update': {'distraction': {'events': {'distraction': {'enabled': False}}}},
}

SYSTEM_JSON_PATCH1 = {
    'name': 'system.json',
    'update': {'xxx': 555, 'yyy': 333},
}

OTHER_JSON_PATCH = {
    'name': 'other.json',
    'update': {'some_field1': {'some_field12': 'xxx'}, 'some_field2': 1241.4},
}

SYSTEM_JSON_PATCH2 = {
    'name': 'system.json',
    'update': {'aaa': 111, 'bbb': 222},
}

P2_FEATURES_JSON_PATCH = {
    'name': 'features.json',
    'update': {
        'distraction': {'events': {'distraction': {'enabled': False}}},
        'drowsiness': {'events': {'tired': {'enabled': False}}},
        'some_old_event': {'enabled': False},
    },
}

DEFAULT_JSON_PATCH = {
    'name': 'default.json',
    'update': {'default_v1': {'default': 3}},
}
