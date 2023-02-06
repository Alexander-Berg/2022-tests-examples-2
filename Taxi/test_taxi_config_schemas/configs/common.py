from typing import Any
from typing import Dict

from taxi_config_schemas import config_models

CONFIGS = [
    {
        'name': 'BILLING_REPORTS_YT_INPUT_ROW_LIMIT',
        'description': '',
        'group': 'billing',
        'default': 100000000,
        'tags': ['fallback'],
        'validators': ['$integer', {'$gt': 0}],
        'full-description': 'Full description',
        'maintainers': ['dvasiliev89', 'serg-novikov'],
        'wiki': 'https://wiki.yandex-team.ru',
        'turn-off-immediately': True,
    },
    {
        'name': 'FRIEND_BRANDS',
        'description': 'Бренды с общими данными пользователей',
        'default': [['yataxi', 'yango']],
        'group': 'chatterbox',
        'tags': [],
        'schema': {
            'type': 'array',
            'items': {
                'type': 'array',
                'items': {'type': 'string', 'minLength': 1},
            },
        },
    },
    {
        'name': 'STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES',
        'description': '',
        'group': 'chatterbox',
        'default': ['YANDEXTAXI'],
        'tags': [],
        'validators': [{'$sequence_of': ['$string']}],
        'schema': {'type': 'array', 'items': {'type': 'string'}},
    },
    {
        'name': 'DEVICENOTIFY_USER_TTL',
        'description': 'TTL пользователя при его неактивности',
        'group': 'devicenotify',
        'default': 90,
        'tags': ['by-service'],
        'validators': ['$integer', {'$gte': 1}, {'$lte': 36500}],
    },
    {
        'name': 'SOME_CONFIG_WITH_DEFINITIONS',
        'description': 'Some config with definitions',
        'group': 'devicenotify',
        'default': {'value': 90},
        'tags': ['by-service'],
        'schema': {
            'type': 'object',
            'required': ['value'],
            'properties': {
                'value': {'type': 'integer'},
                'release_date': {'type': 'string', 'format': 'date'},
            },
            'additionalProperties': False,
        },
    },
    {
        'name': 'CONFIG_WITH_BLOCKED_UPDATE_MAIN_VALUE',
        'description': 'Some config with definitions',
        'group': 'devicenotify',
        'default': {'value': 90},
        'tags': ['by-service', 'no-edit-without-service'],
        'schema': {
            'type': 'object',
            'required': ['value'],
            'properties': {'value': {'type': 'integer'}},
            'additionalProperties': False,
        },
    },
]


def get_config_with_value(
        default_value: Dict[str, Any], schema: Dict[str, Any],
):
    base_config = config_models.BaseConfig(
        name='TEST_SETTINGS',
        description='description',
        full_description='',
        wiki='',
        group='graph',
        default=default_value,
        tags=[],
        validator_declarations=[],
        schema=schema,
        maintainers=['dvasiliev89', 'serg-novikov'],
        turn_off_immediately=False,
    )
    return config_models.ConfigWithValue.from_base_config(
        base_config,
        default_value,
        'test edition',
        'TAXIBACKEND-1',
        None,
        None,
    )
