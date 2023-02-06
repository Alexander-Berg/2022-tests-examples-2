EMPTY_SCHEMA = {'type': 'object', 'additionalProperties': False}
SCHEMA_WITH_ENABLED = {
    'type': 'object',
    'properties': {'enabled': {'type': 'boolean'}},
    'additionalProperties': False,
}
SCHEMA_WITH_DISABLED = {
    'type': 'object',
    'properties': {'disabled': {'type': 'boolean'}},
    'additionalProperties': False,
}
ONEOF_SCHEMA = {
    'oneOf': [
        {'type': 'string'},
        {'type': 'object', 'additionalProperties': False},
    ],
}

MERGE_VALUES_BY = [
    {
        'tag': 'tag_for_merge',
        'consumer': 'test_consumer',
        'merge_method': 'dicts_recursive_merge',
    },
]
ANOTHER_TAG_MERGE_VALUES = [
    {
        'tag': 'tag_for_merge_v2',
        'consumer': 'test_consumer',
        'merge_method': 'dicts_recursive_merge',
    },
]
NON_USED_CONSUMER_MERGE_VALUES = [
    {
        'tag': 'tag_for_merge',
        'consumer': 'non_used_consumer',
        'merge_method': 'dicts_recursive_merge',
    },
]
UNSUPPORTED_MERGE_VALUES = [
    {
        'tag': 'tag_for_merge',
        'consumer': 'test_consumer',
        'merge_method': 'unsupported_merge_method',
    },
]
