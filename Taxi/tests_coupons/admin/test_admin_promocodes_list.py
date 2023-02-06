import pytest

from tests_coupons import util


HEADERS = {
    'X-Yandex-Uid': '75170007',
    'User-Agent': 'Opera/9.99 (Windows NT 0.0; EN)',
}


FIELDS_TO_SORT = [
    'applications',
    'classes',
    'cities',
    'payment_methods',
    'services',
    'zones',
]

COUPONS_EDITABLE_FIELDS = {
    'default': ['services'],
    'first_limit_coupon': ['services', 'value'],
    'external_budget_coupon': ['services', 'user_limit'],
}


@pytest.mark.parametrize(
    'headers', [None, HEADERS],  # headers are optional for now
)
@pytest.mark.parametrize(
    'params,url,expected_indexes',
    [
        ({}, 'list', [0, 1]),
        ({'series_id': 'qwe'}, 'list', [0]),
        ({'series_ids': 'sery'}, 'list', [1]),
        ({'country': 'rus'}, 'list', [1]),
        ({'city': 'Тель-Авив'}, 'list', [0]),
        ({'service': 'lavka'}, 'list', [1]),
        ({'service': 'taxi'}, 'list', [1]),  # explicit only
        ({'service': 'eda'}, 'list', []),
        ({'for_support': 1}, 'list', [1]),
        ({'description': 'TesT'}, 'list', [0]),
        ({'active': 1}, 'list', [1]),
        ({'active_from': '2015-05-01T00:00:00+0300'}, 'list', [0, 1]),
        ({'active_to': '2015-05-01T00:00:00+0300'}, 'list', [0]),
        (
            {'active': 1, 'active_from': '2015-05-01T00:00:00+0300'},
            'list',
            [1],
        ),
        ({'offset': 1}, 'list', [1]),
        ({'limit': 1}, 'list', [0]),
        ({'offset': 1, 'limit': 1}, 'list', [1]),
        ({}, 'support_list', [1]),
        ({'series_id': 'qwe'}, 'support_list', []),
        ({'series_id': '1qwert'}, 'support_list', [0]),
        ({'series_ids': 'sery'}, 'support_list', [1]),
        ({'series_ids': '1qwert,sery'}, 'list', [0, 1]),
        ({'city': 'Тель-Авив'}, 'support_list', []),
        ({'country': 'rus'}, 'support_list', [1]),
        ({'active_from': '2015-05-01T00:00:00+0300'}, 'support_list', [1]),
        ({'offset': 1}, 'support_list', []),
        ({'limit': 1}, 'support_list', [1]),
    ],
)
@pytest.mark.now('2016-12-01T12:00:00.0')
@pytest.mark.config(COUPONS_EDITABLE_FIELDS=COUPONS_EDITABLE_FIELDS)
async def test_admin_promocodes_list(
        taxi_coupons, params, url, headers, expected_indexes,
):
    docs = [
        {
            'series_id': '1qwert',
            'services': ['taxi'],  # default service for none
            'is_unique': True,
            'start': '2015-01-01',
            'finish': '2016-01-01',
            'descr': 'test',
            'cities': ['Иерусалим', 'Тель-Авив'],
            'zones': ['jerusalem', 'tel_aviv_festival'],
            'creator': 'migration_script',
            'value': 122,
            'is_volatile': True,
            'created': '2015-04-13T14:14:20+0300',
            'external_budget': True,
            'external_meta': {
                'arr_key': [],
                'int_key': 0,
                'obj_key': {'id': 0},
                'null_key': None,
                'str_key': 'value',
            },
            'user_limit': 2,
            'currency': 'ILS',
            'creditcard_only': False,
            'country': 'isr',
            'applications': ['uber_android', 'uber_iphone'],
            'bin_ranges': [['426102', '426102'], ['426114', '426114']],
            'payment_methods': ['card', 'googlepay'],
            'percent': 50,
            'percent_limit_per_trip': True,
            'usage_per_promocode': True,
            'requires_activation_after': '2017-01-01',
            'first_usage_by_classes': True,
            'first_usage_by_payment_methods': True,
            'for_support': False,
            'editable_fields': COUPONS_EDITABLE_FIELDS['first_limit_coupon'],
            'bank_name': {'ru': 'Банка', 'en': 'Bank'},
            'ticket': 'TAXIRATE-20',
            'gen_info': [
                {
                    'created': '2015-09-11T14:05:23+0300',
                    'count': 100,
                    'status': 'completed',
                    'error_message': '',
                },
                {
                    'created': '2015-09-05T18:21:11+0300',
                    'count': 10000,
                    'status': 'failed',
                    'error_message': (
                        'unable to safely generate promocodes: '
                        'series name too long or you want too many codes'
                    ),
                },
            ],
        },
        {
            'series_id': 'sery',
            'services': ['lavka', 'taxi'],
            'is_unique': False,
            'start': '2016-11-01',
            'finish': '2016-12-01',
            'descr': 'descr',
            'creator': 'login',
            'used_count': 77,
            'value': 250,
            'created': '2016-10-01T13:00:00+0300',
            'classes': ['econom', 'uberkids'],
            'user_limit': 1,
            'payment_methods': ['card'],
            'for_support': True,
            'currency': 'RUB',
            'country': 'rus',
            'first_limit': 1,
            'count': 99,
            'creditcard_only': True,
            'uniques_count': 800,
            'gen_info': [],
            'first_usage_by_classes': False,
            'editable_fields': COUPONS_EDITABLE_FIELDS['first_limit_coupon'],
            'first_usage_by_payment_methods': False,
            'percent_limit_per_trip': False,
            'is_volatile': False,
            'usage_per_promocode': False,
            'external_budget': False,
        },
    ]

    response = await taxi_coupons.get(
        f'/admin/promocodes/{url}/', params=params, headers=headers,
    )
    assert response.status_code == 200

    expected_json = {'items': [docs[i] for i in expected_indexes]}

    paths_to_sort = {'items.' + field for field in FIELDS_TO_SORT}
    response_json = util.sort_json(response.json(), paths_to_sort)

    assert response_json == expected_json
