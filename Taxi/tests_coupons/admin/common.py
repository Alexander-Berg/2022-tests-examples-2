import datetime


HEADERS = {'X-YaTaxi-Draft-Tickets': 'TAXIRATE-4'}

GOOD_SERVICES = ['taxi', 'grocery']
GOOD_CLASSES = ['econom', 'uberkids']
GOOD_APPLICATIONS = ['alice', 'iphone']
GOOD_PAYMENT_METHODS = ['cash', 'card']
EXTERNAL_META = {
    'arr': [50],
    'int': 7,
    'bool': True,
    'null_new': None,
    'obj': {'new_id': 888, 'id': 777},
    'str': 'deprecated',
    'str_new': 'new value',
}
BASIC_CHANGES = {
    'finish': '2020-08-08',
    'services': GOOD_SERVICES,
    'classes': GOOD_CLASSES,
    'cities': ['Уфа', 'Москва'],
    'external_meta': EXTERNAL_META,
}
ZONES = {'zones': ['himki', 'shodnya', 'ufa']}
CURRENCY = {'currency': 'RUB'}
EXTRA_EB_CHANGES = {
    'start': '2020-05-01',
    'descr': 'Text',
    'user_limit': 10,
    'payment_methods': GOOD_PAYMENT_METHODS,
    'creditcard_only': False,
    'applications': GOOD_APPLICATIONS,
    'bin_ranges': [['123456', '654321']],
    'bank_name': {'ru': 'МойБанк', 'en': 'MyBank'},
    'usage_per_promocode': True,
    'first_usage_by_classes': False,
    'first_usage_by_payment_methods': False,
}
EXTRA_FL_CHANGES = {
    'is_unique': False,
    'is_volatile': False,
    'value': 100,
    'country': 'rus',
    'for_support': True,
    'count': 1000,
    'percent': 77,
    'percent_limit_per_trip': False,
    'requires_activation_after': '2099-01-01',
}
EXTERNAL_BUDGET_CHANGES = dict(BASIC_CHANGES, **EXTRA_EB_CHANGES)
FIRST_LIMIT_CHANGES = dict(
    BASIC_CHANGES, **EXTRA_EB_CHANGES, **EXTRA_FL_CHANGES,
)

GOOD_CHANGES = {
    'basic': BASIC_CHANGES,
    'externalbudget': EXTERNAL_BUDGET_CHANGES,
    'firstlimit': FIRST_LIMIT_CHANGES,
}

HANDLE_MODES = ['check', 'apply']

DATE_FORMAT = '%Y-%m-%d'
DATE_FIELDS = {'start', 'finish', 'requires_activation_after', 'created'}
SKIP_FIELDS = {'series_id'}

CALCULATED = {
    'basic': ZONES,
    'externalbudget': ZONES,
    'firstlimit': dict(ZONES, **CURRENCY),
}

FIELDS_TO_SORT = {
    'applications',
    'cities',
    'classes',
    'payment_methods',
    'services',
    'zones',
}
PREFIXES_TO_SORT = {'data', 'diff.current', 'diff.new', 'update.$set'}
PATH_TO_SORT = {
    prefix + '.' + field
    for prefix in PREFIXES_TO_SORT
    for field in FIELDS_TO_SORT
}


def prepare_update_data(data, extra_data=None, without=None, fmt=DATE_FORMAT):
    """
    In order to check db changes,
    we prepare update data (for applying to old db-doc):
    1. Skip redundant fields
    2. Convert dates to datetime
    3. Add extra_data (calcutaled zones)
    4. Del 'without' (ignored) keys
    """

    def convert_date(value):
        return datetime.datetime.strptime(value, fmt)

    for skip_field in SKIP_FIELDS:
        data.pop(skip_field, None)
    for date_field in DATE_FIELDS:
        if date_field in data:
            data[date_field] = convert_date(data[date_field])
    if without:
        for key in without:
            data.pop(key, None)
    return dict(data, **(extra_data or {}))
