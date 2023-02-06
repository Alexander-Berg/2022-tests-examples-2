ID = 'id'
NAME = 'name'
SLUG = 'slug'
BUSINESS_TYPE = 'business_type'
CATEGORY_TYPE = 'category_type'
BRAND_TYPE = 'brand_type'
NOTIFY_EMAIL_PERSONAL_IDS = 'notify_email_personal_ids'
IS_STOCK_SUPPORTED = 'is_stock_supported'
IGNORE_SURGE = 'ignore_surge'
BIT_SETTINGS = 'bit_settings'
FAST_FOOD_NOTIFY_TIME_SHIFT = 'fast_food_notify_time_shift'
EDITORIAL_VERDICT = 'editorial_verdict'
EDITORIAL_DESCRIPTION = 'editorial_description'
IDS = 'ids'
BRANDS = 'brands'

DEFAULT_BRAND = {
    NAME: 'Default Name',
    SLUG: 'Default Name',
    BUSINESS_TYPE: 'store',
    CATEGORY_TYPE: 'client',
    BRAND_TYPE: 'not_restaurant',
    NOTIFY_EMAIL_PERSONAL_IDS: ['111', '222'],
    IS_STOCK_SUPPORTED: True,
    IGNORE_SURGE: True,
    BIT_SETTINGS: 2,
    FAST_FOOD_NOTIFY_TIME_SHIFT: 1,
    EDITORIAL_VERDICT: 'edit_verdict_text',
    EDITORIAL_DESCRIPTION: 'editorial_description_text',
}

# for search handle
SIMILARITY = 'similarity'
SUGGESTIONS = 'suggestions'
SUBSTRING_SEARCH = 'substring_search'
MODE = 'mode'
SHOW_DELETED = 'show_deleted'

# for pagination
PAGINATION = 'pagination'
PAGE_SIZE = 'page_size'
PAGE_NUMBER = 'page_number'
PAGE_COUNT = 'page_count'
ITEMS = 'items'
TOTAL_ITEMS = 'total_items'

# fer edit handle
SET_NOTIFY_EMAILS_TO_NULL = 'set_notify_emails_to_null'
SET_BIT_SETTINGS_TO_NULL = 'set_bit_settings_to_null'
SET_FAST_FOOD_NOTIFY_TIME_SHIFT_TO_NULL = (
    'set_fast_food_notify_time_shift_to_null'
)
SET_EDITORIAL_VERDICT_TO_NULL = 'set_editorial_verdict_to_null'
SET_EDITORIAL_DESCRIPTION_TO_NULL = 'set_editorial_description_to_null'

# for merge-brands handle
ACTUAL_ID = 'actual_id'
IDS_TO_MERGE = 'ids_to_merge'


def extend_default_brand(extend):
    default_copy = DEFAULT_BRAND.copy()
    default_copy.update(extend)
    return default_copy


def extend_brand_without_slug(extend):
    default_copy = DEFAULT_BRAND.copy()
    default_copy.update(extend)
    default_copy[SLUG] = None
    return default_copy
