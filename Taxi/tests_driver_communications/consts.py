import datetime


DEFAULT_CUSTOM_FIELDS = [
    {
        'key': 'form_perm',
        'key_id': 'form_perm',
        'keyset': 'opteum_support_chat',
        'value': 'form_perm_me_group',
        'value_id': 'form_perm_me_group',
    },
]
CSAT_MARK = {
    'id': 'csat1',
    'question': 'how do you like support?',
    'created': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'actions': [
        {'id': 'mark1', 'type': 'rating', 'text': '1'},
        {'id': 'mark2', 'type': 'rating', 'text': '2'},
        {'id': 'mark3', 'type': 'rating', 'text': '3'},
        {'id': 'exit1', 'type': 'exit', 'text': 'problem not solved'},
    ],
}
CSAT_REASON = {
    'id': 'csat2',
    'question': 'select reason',
    'created': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'actions': [
        {'id': 'reason1', 'type': 'reason', 'text': 'liked Eugeny'},
        {'id': 'reason2', 'type': 'reason', 'text': 'good service'},
        {'id': 'exit2', 'type': 'exit', 'text': 'ok'},
        {'id': 'transition1', 'type': 'transition', 'text': 'change mark'},
    ],
}
CSAT_FINISH = {
    'id': 'csat3',
    'question': 'something else?',
    'created': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'actions': [
        {'id': 'exit2', 'type': 'exit', 'text': 'ok'},
        {'id': 'transition1', 'type': 'transition', 'text': 'change mark'},
        {'id': 'transition2', 'type': 'transition', 'text': 'change reason'},
    ],
}


DEFAULT = 'default'
TEXT_FEED = 'text_feed'
TEXT_DSAT = 'text_dsat'
TEXT_TITLE_FEED = 'text_title_feed'
TEXT_TITLE_FEED_VIEWED = 'text_title_feed_viewed'
TEXT_TITLE_IMAGE_PARENT = 'text_title_image_parent'
TEXT_REPLY = 'text_reply'
TEXT_TITLE_FEED_READ = 'text_title_feed_read'
TEXT_FEED_READ = 'text_feed_read'
TEXT_TITLE_IMAGE_FEED = 'text_title_image_feed'
FULLSCREEN_FEED = 'fullscreen_feed'
FULLSCREEN2_FEED = 'fullscreen_2_feed'
FULLSCREEN3_FEED = 'fullscreen_3_feed'
FULLSCREEN4_FEED = 'fullscreen_4_feed'
FULLSCREEN_READ_FEED = 'fullscreen_read_feed'
FULLSCREEN_VIEWED_FEED = 'fullscreen_viewed_feed'
REPLY_ON_DELETED = 'text_reply_on_deleted'
NO_META = 'no_meta'
VERY_OLD_MSG = 'very_old_msg'
MOCK_DRIVER_DIAGNOSTICS_HANDLER = (
    'driver-diagnostics/internal/driver-diagnostics/v1/categories/restrictions'
)

FEED_ID_MAP = {
    TEXT_FEED: 'f6dc672653aa443d9ecf48cc5ef4cb6d',
    TEXT_DSAT: 'dsat172653aa443d9ecf48cc5ef4cb6d',
    TEXT_TITLE_FEED: 'f6dc672653aa443d9ecf48cc5ef4cb6a',
    TEXT_TITLE_FEED_VIEWED: 'f6dc672653aa443d9ecf48cc5ef4cb6b',
    TEXT_TITLE_IMAGE_PARENT: 'f6dc672653aa443d9ecf48cc5ef4cb6e',
    TEXT_REPLY: 'f6dc672653aa443d9ecf48cc5ef4cbee',
    TEXT_TITLE_FEED_READ: 'f6dc672653aa443d9ecf48cc5ef4cb6c',
    TEXT_FEED_READ: 'f6dc672653aa443d9ecf48cc5ef4cb6f',
    TEXT_TITLE_IMAGE_FEED: 'f6dc672653aa443d9ecf48cc5ef4cb6x',
    FULLSCREEN_FEED: 'f6dc672653aa443d9ecf48cc5ef4cb6y',
    FULLSCREEN_READ_FEED: 'f6dc672653aa443d9ecf48cc5ef4cb6k',
    FULLSCREEN_VIEWED_FEED: 'f6dc672653aa443d9ecf48cc5ef4cb6z',
    FULLSCREEN2_FEED: 'f6dc672653aa443d9ecf48cc5ef4cb6m',
    FULLSCREEN3_FEED: 'fs3c672653aa443d9ecf48cc5ef4cb6m',
    FULLSCREEN4_FEED: 'fs4c672653aa443d9ecf48cc5ef4cb6m',
    REPLY_ON_DELETED: 'a6dc672653aa443d9ecf48cc5ef4cb6e',
    NO_META: 'f6dc672653aa443d9eaaaaaaaaaaaa',
    VERY_OLD_MSG: 'f6dc672653aa443d9eaaaaaaaaaaak',
}
