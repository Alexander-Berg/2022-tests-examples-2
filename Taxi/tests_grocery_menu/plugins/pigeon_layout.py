CATEGORY_LEGACY_ID = 'virtual-category-id-{}'
CATEGORY_ALIAS = 'category-alias-{}'

GROUP_LEGACY_ID = 'group-id-{}'
GROUP_ALIAS = 'group-alias-{}'

LONG_TITLE = 'long-title-{}'
SHORT_TITLE = 'short-title-{}'
DEFAULT_META = {'test-key': 'test-value'}
DEEPLINK = 'deep-link-{}'
SPECIAL_CATEGORY = 'special-category-{}'


def format_pigeon_category(category_id, subcategories=None):
    if subcategories is None:
        subcategories = []
    return {
        'id': category_id,
        'legacyId': CATEGORY_LEGACY_ID.format(category_id),
        'alias': CATEGORY_ALIAS.format(category_id),
        'longTitleTankerKey': {
            'keyset': 'test-keyset',
            'key': LONG_TITLE.format(category_id),
        },
        'shortTitleTankerKey': {
            'keyset': 'test-keyset',
            'key': SHORT_TITLE.format(category_id),
        },
        'meta': DEFAULT_META,
        'deeplink': DEEPLINK.format(category_id),
        'specialCategory': SPECIAL_CATEGORY.format(category_id),
        'subcategories': [
            {'id': 10 * category_id + i, 'alias': subcat}
            for i, subcat in enumerate(subcategories)
        ],
    }


def format_pigeon_group(group_id):
    return {
        'id': group_id,
        'legacyId': GROUP_LEGACY_ID.format(group_id),
        'alias': GROUP_ALIAS.format(group_id),
        'longTitleTankerKey': {
            'keyset': 'test-keyset',
            'key': LONG_TITLE.format(group_id),
        },
        'shortTitleTankerKey': {
            'keyset': 'test-keyset',
            'key': SHORT_TITLE.format(group_id),
        },
        'meta': DEFAULT_META,
    }
