import pytest

YANDEX_UID = 'some_yandex_uid'

GOAL_ID = '111'
GOAL_NAME = 'goal_name'
GOAL_TITLE = 'goal_title'
GOAL_ICON_LINK = 'goal_icon_link'
GOAL_PAGE_ICON_LINK = 'goal_page_icon_link'
GOAL_LEGAL_TEXT = 'goal_legal_text'
PROGRESS_BAR_COLOR = '#FFC0CB'
CATALOG_TEXT = 'catalog_text_tanker'
GROUP_TEXT = 'group_text_tanker'
CATALOG_LINK = 'catalog_link'
CATALOG_PICTURE_LINK = 'catalog_picture_link'

GOAL_PUSH_INFO = {
    'finish_title_tanker_key': 'goal_finish_push_title',
    'finish_message_tanker_key': 'goal_finish_push_message',
}
GOAL_DISPLAY_INFO = {
    'push_info': GOAL_PUSH_INFO,
    'goal_info': {
        'title_tanker_key': GOAL_TITLE,
        'icon_link': GOAL_ICON_LINK,
        'goal_page_icon_link': GOAL_PAGE_ICON_LINK,
        'legal_text': GOAL_LEGAL_TEXT,
        'progress_bar_color': PROGRESS_BAR_COLOR,
        'catalog_text': CATALOG_TEXT,
        'group_text': GROUP_TEXT,
        'catalog_link': CATALOG_LINK,
        'catalog_picture_link': CATALOG_PICTURE_LINK,
    },
}
GOAL_CREATED = '2020-01-27T15:00:00+03:00'
GOAL_UPDATED = '2020-01-27T15:00:00+03:00'
GOAL_STARTS = '2021-08-25T12:00:00+00:00'
GOAL_EXPIRES = '2021-10-25T12:00:00+00:00'
GOAL_REWARD_USED_AT = '2021-09-25T12:00:00+00:00'
GOAL_REWARD_SWAP_AT = '2021-09-25T10:00:00+00:00'
GOAL_COMPLETE_AT = '2021-09-01T12:00:00+00:00'

GOAL_REWARD_PROMOCODE_SERIES = 'promo_series'
GOAL_REWARD_PROMOCODE_TYPE = 'promocode'
GOAL_REWARD_PROMOCODE = {
    'type': GOAL_REWARD_PROMOCODE_TYPE,
    'extra': {'promocode_series': GOAL_REWARD_PROMOCODE_SERIES},
}

DEFAULT_SKUS = ['some_sku_id_1']
GOAL_REWARD_SKU_TYPE = 'sku'
GOAL_REWARD_SKU = {
    'type': GOAL_REWARD_SKU_TYPE,
    'extra': {'skus': DEFAULT_SKUS},
}
GOAL_REWARD_SKU_PICTURE_TEMPLATE = 'image/pic.jpg'

EXTERNAL_VENDOR_TEXT = 'external_vendor_text_tanker_key'
EXTERNAL_VENDOR_PICTURE_LINK = 'external_vendor_picture_link'
EXTERNAL_VENDOR_COMPLETED_TEXT = 'external_vendor_completed_text_tanker_key'
EXTERNAL_VENDOR_MORE_INFO = 'external_vendor_more_info_link'
GOAL_REWARD_EXTERNAL_VENDOR_TYPE = 'external_vendor'
GOAL_REWARD_EXTERNAL_VENDOR = {
    'type': GOAL_REWARD_EXTERNAL_VENDOR_TYPE,
    'extra': {
        'text': EXTERNAL_VENDOR_TEXT,
        'picture_link': EXTERNAL_VENDOR_PICTURE_LINK,
        'completed_text': EXTERNAL_VENDOR_COMPLETED_TEXT,
        'more_info': EXTERNAL_VENDOR_MORE_INFO,
    },
}

ORDERS_COUNT_GOAL_TYPE = 'orders_count'
ORDERS_TOTAL_SUM_GOAL_TYPE = 'orders_total_sum'
SKUS_COUNT_GOAL_TYPE = 'skus_count'
GOAL_STATUS = 'enabled'
ORDER_COUNT_ARG_TYPE = 'order_count'
TOTAL_SUM_ARG_TYPE = 'total_sum'
SKUS_COUNT_ARG_TYPE = 'skus_count'
SKUS_TOTAL_SUM_ARG_TYPE = 'skus_total_sum'
GOAL_ORDER_COUNT_ARGS = {ORDER_COUNT_ARG_TYPE: 10}
GOAL_TOTAL_SUM_ARGS = {TOTAL_SUM_ARG_TYPE: '1000', 'currency_code': 'RUB'}
GOAL_SKUS = ['sku1', 'sku2']
GOAL_SKUS_COUNT_ARGS = {'skus': GOAL_SKUS, SKUS_COUNT_ARG_TYPE: 10}
GOAL_SKUS_TOTAL_SUM_ARGS = {
    'skus': GOAL_SKUS,
    SKUS_TOTAL_SUM_ARG_TYPE: '1000',
    'currency_code': 'RUB',
}
GOAL_ARGS = {
    ORDERS_COUNT_GOAL_TYPE: GOAL_SKUS_COUNT_ARGS,
    ORDERS_TOTAL_SUM_GOAL_TYPE: GOAL_TOTAL_SUM_ARGS,
    SKUS_COUNT_GOAL_TYPE: GOAL_SKUS_COUNT_ARGS,
    SKUS_TOTAL_SUM_ARG_TYPE: GOAL_SKUS_TOTAL_SUM_ARGS,
}

GOAL_MARKETING_TAGS = ['one', 'two']

GOAL_PROGRESS_ID = '12345'
GOAL_PROGRESS_PROGRESS = {'order_count': 1}
GOAL_PROGRESS_STATUS = 'in_progress'


EATS_USER_ID = 'eats-user-id'
PERSONAL_PHONE_ID = 'personal-phone-id'
USER_INFO = (
    f'eats_user_id={EATS_USER_ID}, personal_phone_id={PERSONAL_PHONE_ID}'
)

PROGRESS_TEXT_ARG = 'remaining_progress'
TITLE_ARG = 'target_value'

TITLE_TRANSLATED = 'заголовок %(target_value)s'
LEGAL_TEXT_TRANSLATED = 'юридический текст'
PROGRESS_TEXT_TRANSLATED = 'прогресс %(remaining_progress)s'
REMAINING_TIME_DAYS_TRANSLATED = '%(days)s дня'
REMAINING_TIME_HOURS_TRANSLATED = '%(hours)s часа'
REMAINING_TIME_LESS_THAN_HOUR_TRANSLATED = 'меньше часа'
PROMOCODE_VALUE_TEXT_TRANSLATED = '-%(value)s'
ORDERS_COUNT_COMPLETED_TRANSLATED = 'order_count %(target_value)s'
ORDERS_TOTAL_SUM_COMPLETED_TRANSLATED = 'orders_total_sum %(target_value)s'
SKUS_TOTAL_SUM_COMPLETED_TRANSLATED = 'skus_total_sum %(target_value)s'
SKUS_COUNT_COMPLETED_TRANSLATED = 'skus_count %(target_value)s'
EXTERNAL_VENDOR_TEXT_TRANSLATED = 'external vendor text translated'
EXTERNAL_VENDOR_COMPLETED_TEXT_TRANSLATED = (
    'external vendor completed text translated'
)

CATALOG_TEXT_TRANSLATED = 'catalog_text_translated'
GROUP_TEXT_TRANSLATED = 'group_text_translated'

GROCERY_GOALS_TRANSLATIONS = pytest.mark.translations(
    grocery_goals={
        'remaining_time_days': {'ru': REMAINING_TIME_DAYS_TRANSLATED},
        'remaining_time_hours': {'ru': REMAINING_TIME_HOURS_TRANSLATED},
        'remaining_time_less_than_hour': {
            'ru': REMAINING_TIME_LESS_THAN_HOUR_TRANSLATED,
        },
        GOAL_TITLE: {'ru': TITLE_TRANSLATED},
        GOAL_LEGAL_TEXT: {'ru': LEGAL_TEXT_TRANSLATED},
        'order_total_sum_progress_text': {'ru': PROGRESS_TEXT_TRANSLATED},
        'order_count_progress_text': {'ru': PROGRESS_TEXT_TRANSLATED},
        'skus_count_progress_text': {'ru': PROGRESS_TEXT_TRANSLATED},
        'skus_total_sum_progress_text': {'ru': PROGRESS_TEXT_TRANSLATED},
        'promocode_value_text': {'ru': PROMOCODE_VALUE_TEXT_TRANSLATED},
        'orders_count_completed_progress_text': {
            'ru': ORDERS_COUNT_COMPLETED_TRANSLATED,
        },
        'orders_total_sum_completed_progress_text': {
            'ru': ORDERS_TOTAL_SUM_COMPLETED_TRANSLATED,
        },
        'skus_count_completed_progress_text': {
            'ru': SKUS_COUNT_COMPLETED_TRANSLATED,
        },
        'skus_total_sum_completed_progress_text': {
            'ru': SKUS_TOTAL_SUM_COMPLETED_TRANSLATED,
        },
        EXTERNAL_VENDOR_TEXT: {'ru': EXTERNAL_VENDOR_TEXT_TRANSLATED},
        EXTERNAL_VENDOR_COMPLETED_TEXT: {
            'ru': EXTERNAL_VENDOR_COMPLETED_TEXT_TRANSLATED,
        },
        CATALOG_TEXT: {'ru': CATALOG_TEXT_TRANSLATED},
        GROUP_TEXT: {'ru': GROUP_TEXT_TRANSLATED},
    },
)

PROGRESS_TEXT_NOT_STARTED = PROGRESS_TEXT_TRANSLATED % (
    {PROGRESS_TEXT_ARG: GOAL_ORDER_COUNT_ARGS[ORDER_COUNT_ARG_TYPE]}
)
PROGRESS_TEXT = PROGRESS_TEXT_TRANSLATED % (
    {
        PROGRESS_TEXT_ARG: (
            GOAL_ORDER_COUNT_ARGS[ORDER_COUNT_ARG_TYPE]
            - GOAL_PROGRESS_PROGRESS[ORDER_COUNT_ARG_TYPE]
        ),
    }
)
TITLE_TEXT = TITLE_TRANSLATED % (
    {TITLE_ARG: GOAL_ORDER_COUNT_ARGS[ORDER_COUNT_ARG_TYPE]}
)

COMPLETED_PROGRESS_TEXT = ORDERS_COUNT_COMPLETED_TRANSLATED % (
    {TITLE_ARG: GOAL_ORDER_COUNT_ARGS[ORDER_COUNT_ARG_TYPE]}
)


def get_args_value(goal_args):
    if ORDER_COUNT_ARG_TYPE in goal_args:
        return goal_args[ORDER_COUNT_ARG_TYPE]
    if TOTAL_SUM_ARG_TYPE in goal_args:
        return goal_args[TOTAL_SUM_ARG_TYPE]
    if SKUS_COUNT_ARG_TYPE in goal_args:
        return goal_args[SKUS_COUNT_ARG_TYPE]
    if SKUS_TOTAL_SUM_ARG_TYPE in goal_args:
        return goal_args[SKUS_TOTAL_SUM_ARG_TYPE]
    return None


def get_typed_args_value(goal_args, goal_progress=None):
    if ORDER_COUNT_ARG_TYPE in goal_args:
        result = (
            int(goal_args[ORDER_COUNT_ARG_TYPE])
            - int(goal_progress[ORDER_COUNT_ARG_TYPE])
            if goal_progress
            else goal_args[ORDER_COUNT_ARG_TYPE]
        )
        return str(result)
    if TOTAL_SUM_ARG_TYPE in goal_args:
        result = (
            int(goal_args[TOTAL_SUM_ARG_TYPE])
            - int(goal_progress[TOTAL_SUM_ARG_TYPE])
            if goal_progress
            else goal_args[TOTAL_SUM_ARG_TYPE]
        )
        return '$SIGN$' + str(result) + '$CURRENCY$'
    if SKUS_COUNT_ARG_TYPE in goal_args:
        result = (
            int(goal_args[SKUS_COUNT_ARG_TYPE])
            - int(goal_progress[SKUS_COUNT_ARG_TYPE])
            if goal_progress
            else goal_args[SKUS_COUNT_ARG_TYPE]
        )
        return str(result)
    if SKUS_TOTAL_SUM_ARG_TYPE in goal_args:
        result = (
            int(goal_args[SKUS_TOTAL_SUM_ARG_TYPE])
            - int(goal_progress[SKUS_TOTAL_SUM_ARG_TYPE])
            if goal_progress
            else goal_args[SKUS_TOTAL_SUM_ARG_TYPE]
        )
        return '$SIGN$' + str(result) + '$CURRENCY$'
    return None
