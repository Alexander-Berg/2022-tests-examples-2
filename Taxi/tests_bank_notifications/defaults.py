import uuid


CONSUMER_KEY = 'consumer'
BUID_KEY = 'buid'
EVENTS_KEY = 'events'
ALL_KEY = 'ALL'

CONSUMER = 'test_consumer'
BUID = '11111111-e14e-4e64-8de3-407b0b3b735a'
UID = 'test_uid'
BUID2 = '22222222-e14e-4e64-8de3-407b0b3b735a'
UID2 = 'test_uid2'

EVENT_TYPE_KEY = 'event_type'
DEFAULTS_GROUP_KEY = 'defaults_group'
PRIORITY_KEY = 'priority'
TITLE_KEY = 'title'
DESCRIPTION_KEY = 'description'
ACTION_KEY = 'action'
MERGE_KEY_KEY = 'merge_key'
MERGE_KEY = 'test_merge_key'
OTHER_MERGE_KEY = 'test_merge_key2'
EXPERIMENT_KEY = 'experiment'
KEY_KEY = 'key'
ARGS_KEY = 'args'
PAYLOAD_KEY = 'payload'

EVENT_TYPE = 'MAIN_SCREEN'
EVENT_TYPE2 = 'MAIN_SCREEN_PROMO'
EVENT_TYPE_BELL = 'BELL'
DEFAULTS_GROUP = 'test_defaults_group'
DEFAULTS_GROUP_NOT_CLOSABLE = 'test_defaults_group_not_closable'
PRIORITY = 100
TITLE = 'test_title'
TITLE_WITH_ARG = 'test_title_with_arg'
DESCRIPTION = 'test_description'
DESCRIPTION_WITH_ARG = 'test_description_with_arg'
ACTION = 'test_action'

EVENT_IDS_KEY = 'event_ids'
MARK_TYPE_KEY = 'mark_type'

MARK_TYPE = 'READ'
CONSUMER_TYPE = 'CONSUMER'
BUID_TYPE = 'BUID'

DARK_KEY = 'DARK'
LIGHT_KEY = 'LIGHT'
SYSTEM_KEY = 'SYSTEM'

DEFAULTS_GROUP_CONFIG_NAME = 'BANK_NOTIFICATIONS_DEFAULTS_GROUPS_4'

DEFAULT_THEMES = {
    'dark': {
        'background': {'color': 'FF112233'},
        'title_text_color': 'FF112233',
    },
    'light': {
        'background': {'color': 'FF112233'},
        'title_text_color': 'FF112233',
    },
}

PAYLOAD = {
    'data': {'key': {'subkey': 'data'}},
    'light': {'background': {'color': 'FF112233'}, 'key': 'data'},
    '1': {'background': {'2': 3}, 'key': 4444},
}


def gen_uuid():
    return str(uuid.uuid4())


DEFAULT_UUID = '5ab2ece9-89b4-4cfb-a42a-93fb77bb9f0c'


def auth_headers():
    return {
        'X-Yandex-UID': UID,
        'X-Yandex-BUID': BUID,
        'X-YaBank-SessionUUID': 'session',
        'X-YaBank-PhoneID': 'phone_id',
        'X-Ya-User-Ticket': 'user_ticket',
    }
