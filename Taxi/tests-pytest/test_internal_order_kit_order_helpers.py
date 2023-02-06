import pytest
import dateutil.parser

from taxi import config
from taxi.conf import settings
from taxi.core import async
from taxi.internal import dbh
from taxi.internal.order_kit import const
from taxi.internal.order_kit import brand_helpers
from taxi.internal.order_kit import order_helpers


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('config_enabled', [True, False])
@pytest.mark.parametrize('order_doc,ustc,expected_need_to_get', [
    # no feedback, need in complete
    ({'taxi_status': 'complete'}, False, True),
    # empty feedback, need in complete
    ({'feedback': {}, 'taxi_status': 'complete'}, False, True),
    # some feedback, don't need in complete
    (
        {'feedback': {'msg': 'some comment'}, 'taxi_status': 'complete'},
        False,
        False,
    ),
    # some feedback, but user switched to card, need
    (
        {
            'feedback': {'msg': 'some comment'},
            'taxi_status': 'complete',
            'ustc': True,
        },
        True,
        True,
    ),
    # feedback saved after switch to card, don't need
    (
        {
            'feedback': {'msg': 'some comment', 'iac': True},
            'taxi_status': 'complete',
            'ustc': True,
        },
        True,
        False,
    ),
    # no feedback, need in non-complete
    ({'taxi_status': 'driving'}, False, True),
    # empty feedback, need in non-complete
    ({'feedback': {}, 'taxi_status': 'driving'}, False, True),
    # some feedback, need in non-complete
    (
        {'feedback': {'msg': 'some comment'}, 'taxi_status': 'driving'},
        False,
        True,
    ),
    (
        {'feedback': {'msg': 'some comment'}, 'taxi_status': 'driving'},
        False,
        True,  # not switched to card, not complete -- last case
    ),
    (
        {'feedback': {'msg': 'some comment', 'iac': True},
         'taxi_status': 'driving'},
        False,
        True,  # not switched to card, not complete -- last case
    ),
    (
        {'feedback': {'msg': 'some comment', 'iac': True},
         'taxi_status': 'complete'},
        False,
        False,  # complete and feedback is not empty
    ),
    (
        {'feedback': {'msg': 'some comment', 'iac': False},
         'taxi_status': 'driving'},
        True,
        True,  # switched to card and not is_after_complete
    ),
])
@pytest.inline_callbacks
def test_need_to_get_user_feedback(monkeypatch, patch, config_enabled,
                                   order_doc, ustc, expected_need_to_get):
    retrieved = []

    @patch('taxi.external.passenger_feedback.retrieve')
    @async.inline_callbacks
    def retrieve(order_id, **kwargs):
        retrieved.append(order_id)
        feedback = order_doc.get('feedback', {})
        new_style_feedback = {}
        if 'msg' in feedback:
            new_style_feedback['msg'] = feedback['msg']
        if 'iac' in feedback:
            new_style_feedback['is_after_complete'] = feedback['iac']

        yield async.return_value(new_style_feedback)

    class DummyConf(object):
        @staticmethod
        def get():
            return config_enabled

    monkeypatch.setattr(config, 'USE_FEEDBACK_API_FOR_NOTIFY', DummyConf)

    actual_need_to_get = yield order_helpers.need_to_get_user_feedback(
        'order_id', order_doc, ustc
    )
    assert actual_need_to_get == expected_need_to_get

    if config_enabled:
        assert retrieved == ['order_id']
    else:
        assert retrieved == []


@pytest.mark.parametrize('order_doc,expected_currency', [
    (
        {},
        'RUB',
    ),
    (
        {
            'performer': {},
            'billing_contract': {
                'is_set': True,
                'currency': 'USD',
                'currency_rate': '2'
            }
        },
        'USD',
    )
])
@pytest.mark.filldb(_fill=False)
def test_get_contract_currency(order_doc, expected_currency):
    currency = order_helpers.get_contract_currency(order_doc)
    assert currency == expected_currency


@pytest.mark.parametrize('order_doc,expected', [
    (
        {
        },
        {
            'currency': 'RUB',
            'currency_rate': '1',
            'acquiring_percent': '0.02',
        }
    ),
    (
        {
            'performer': {
                'tariff': {
                    'currency': 'KZT'
                }
            }
        },
        {
            'currency': 'KZT',
            'currency_rate': '1',
            'acquiring_percent': '0.02',
        }
    ),
    (
        {
            'billing_contract': {
                'is_set': True,
                'currency': 'USD',
                'currency_rate': '30.00',
                'acquiring_percent': '0.02',
            }
        },
        {
            'is_set': True,
            'currency': 'USD',
            'currency_rate': '30.00',
            'acquiring_percent': '0.02',
        }
    ),
])
def test_get_billing_contract(order_doc, expected):
    result = order_helpers._get_billing_contract(order_doc)
    assert result == expected


@pytest.mark.parametrize('order_doc', [
    {
        'billing_contract': {

        }
    },
    {
        'billing_contract': {
            'is_set': False
        }
    },
])
def test_get_billing_contract_failure(order_doc):
    with pytest.raises(order_helpers.NoBillingContractSetError):
        order_helpers._get_billing_contract(order_doc)


@pytest.mark.fill(_fill=False)
@pytest.mark.asyncenv('blocking')
@pytest.mark.parametrize('order_proc,currency_excepted',
    [
        (
            {'candidates': [], 'performer': {'park_id': None}},
            'DEFCUR'
        ),
        (
            {
                'candidates': [
                    {'tariff_currency': 'CURR1'},
                    {'tariff_currency': 'CURR2'},
                    {'tariff_currency': 'CURR3'},
                ],
                'performer': {
                    'candidate_index': 2, 'park_id': 'A', 'presetcar': False
                }
            },
            'CURR3',
        ),
    ]
)
def test_get_currency(monkeypatch, order_proc, currency_excepted):
    monkeypatch.setattr(settings, 'DEFAULT_CURRENCY', 'DEFCUR')

    order_proc_doc = dbh.order_proc.Doc(order_proc)
    assert order_helpers.get_currency(order_proc_doc) == currency_excepted


@pytest.mark.parametrize('order_proc_doc',
[
    (
        {
            'order': {
                'cost': 900,
                'coupon': {
                    'percent': 75,
                    'valid': True,
                    'limit': 800,
                    'was_used': True
                },
                'current_prices': {}
            },
            'candidates': [
                {
                    'driver_id': 'parkid_driverid',
                    'alias_id': 'alias1',
                    'ci': 'category_id',
                    'tariff_class': 'econom'
                }
            ],
            'aliases': [{'id': 'alias1'}],
            'performer': {
                'park_id': 'parkid',
                'uuid': 'driverid',
                'candidate_index': 0,
            }
        }
    )
])
@pytest.mark.parametrize('multipliers,expected_value,final_cost_meta,was_used', [
    (
        None,
        675,  # 900 * 0.75
        {},
        True
    ),
    (
        [('ya_plus', 0.9, True)],
        750,  # 900 / 0.9 * 0.75
        {},
        True
    ),
    (
        [('ya_plus', 0.9, True), ('personal_wallet', 0.9, True)],
        800,  # 900 / 0.9 / 0.9 * 0.75 limit 800
        {},
        True
    ),
    (
        None,
        123,
        {'user': {'use_cost_includes_coupon': 1, 'coupon_value': 123}},
        True
    ),
    (
        None,
        0,
        {'user': {'use_cost_includes_coupon': 1, 'coupon_value': 123}},
        False
    )
])
def test_get_coupon_value(order_proc_doc, multipliers, expected_value,
                          final_cost_meta, was_used):
    order_proc_doc = order_proc_doc.copy()
    order_proc_doc['order']['coupon']['was_used'] = was_used
    order_proc_doc['order']['current_prices'][
        'final_cost_meta'] = final_cost_meta

    if multipliers:
        order_proc_doc['price_modifiers'] = {'items': [{
            'type': 'multiplier',
            'reason': reason,
            'value': value,
            'tariff_categories': ['econom'],
            'pay_subventions': pay_subvention
        } for reason, value, pay_subvention in multipliers
        ]}
    order_proc = dbh.order_proc.Doc(order_proc_doc)
    assert order_helpers.get_coupon_value(order_proc) == expected_value


@pytest.mark.parametrize('new_cost,coupon_value,expected_response', [
    (300, 0, (300, 0)),
    (300, 200, (100, 200)),
    (300, 500, (0, 500)),
])
@pytest.mark.filldb(_fill=False)
def test_cost_with_coupon(patch, new_cost, coupon_value, expected_response):
    ORDER_DOC = {}

    @patch('taxi.internal.order_kit.order_helpers.get_coupon_value_deprecated')
    def get_coupon_value_deprecated(order_doc, *args, **kwargs):
        assert order_doc == ORDER_DOC
        return coupon_value

    assert order_helpers.get_cost_with_coupon(
        ORDER_DOC, new_cost
    ) == expected_response


@pytest.mark.parametrize('expected_response,final_cost_meta', [
    (123 - 50, None),
    (123 - 50, {'user': {}, 'driver': {}}),
    (123 - 50, {'user': {'coupon_value': 100, 'order_cost_includes_coupon': 0}, 'driver': {}}),
    (123 - 50, {'user': {'coupon_value': 100}, 'driver': {}}),
    (123, {'user': {'coupon_value': 100, 'use_cost_includes_coupon': 1}, 'driver': {}}),
])
@pytest.mark.filldb(_fill=False)
def test_ride_cost_with_coupon_from_pricing(patch, expected_response, final_cost_meta):
    ORDER_PROC_DOC = {'order': {'cost': 123, 'coupon': {'was_used': True}}}
    if final_cost_meta is not None:
        ORDER_PROC_DOC['order']['current_prices'] = {'final_cost_meta': final_cost_meta}

    @patch('taxi.internal.order_kit.order_helpers.get_coupon_value')
    def get_coupon_value_deprecated(order_doc, *args, **kwargs):
        return 50

    order_proc = dbh.order_proc.Doc(ORDER_PROC_DOC)

    assert order_helpers.get_ride_cost(order_proc) == expected_response


@pytest.mark.parametrize('order_doc',
[
    (
        {
            'cost': 900,
            'coupon': {
                'percent': 75,
                'valid': True,
                'limit': 800,
                'was_used': True
            },
            'performer': {
                'tariff': {
                    'class': 'econom'
                }
            }
        }
    )
])
@pytest.mark.parametrize('multipliers,expected_value', [
    (
        None,
        675  # 900 * 0.75
    ),
    (
        [('ya_plus', 0.9, True)],
        750  # 900 / 0.9 * 0.75
    )
])
def test_get_coupon_value_deprecated(order_doc, multipliers, expected_value):
    if multipliers:
        order_doc = order_doc.copy()
        order_doc['price_modifiers'] = {'items': [{
               'type': 'multiplier',
               'reason': reason,
               'value': value,
               'tariff_categories': ['econom'],
               'pay_subventions': pay_subvention
            } for reason, value, pay_subvention in multipliers
        ]}
    assert order_helpers.get_coupon_value_deprecated(order_doc) == expected_value


@pytest.mark.now('2010-11-11T11:11:11.111')
@pytest.mark.parametrize('payment_type,debt,status_updated,user_init,expect', [
    (const.CASH, False, '2010-11-11T11:11:11.111', True, True),
    (const.CASH, False, '2000-11-11T11:11:11.111', False, True),
    (const.CASH, False, '2000-11-11T11:11:11.111', True, False),
    (const.CARD, True, '2010-11-11T11:11:11.111', True, True),
    (const.CORP, True, '2010-11-11T11:11:11.111', True, False),
])
@pytest.inline_callbacks
def test_can_be_paid_by_card(payment_type, debt, status_updated, user_init,
                             expect):
    order = dbh.orders.Doc({
        dbh.orders.Doc.payment_tech: {
            dbh.orders.Doc.payment_tech.type.key: payment_type,
            dbh.orders.Doc.payment_tech.debt.key: debt,
        },
        dbh.orders.Doc.status_updated: dateutil.parser.parse(status_updated),
    })

    result = yield order_helpers.can_be_paid_by_card(order, user_init)
    assert result == expect


@pytest.mark.parametrize('decision,expect', [
    (order_helpers.DECISION_REFUND, True),
    (order_helpers.DECISION_CHARGE, True),
    ('whatever', False),
])
def test_price_set_manually(decision, expect):
    pt = dbh.orders.Doc.payment_tech
    order = dbh.orders.Doc({
        pt: {
            pt.history.key: [
                {
                    pt.history.decision.key: decision,
                }
            ]
        }
    })
    assert order_helpers.price_set_manually(order) == expect


@pytest.mark.parametrize('driver_tags,zone,category,expected_timeout', [
    (   # no tags, have zone and category
        [],
        'krasnogorsk',
        'econom',
        120,
    ),
    (   # no tags, have zone and category
        [],
        'moscow',
        'business',
        13,
    ),
    (   # no tags, no zone and category
        [],
        'unknown_zone_must_use_global_default',
        '',
        10,
    ),
    (   # no tags, have zone, no category
        [],
        'moscow',
        'unknown_category_must_use_zone_default',
        11,
    ),
    (   # one tag matched, have zone and category
        ['tag0', 'tag_mismatch'],
        'moscow',
        'econom',
        30,
    ),
    (   # one tag matched, no zone and category
        ['tag0', 'tag_mismatch'],
        'unknown_zone_must_use_global_default_if_there_were_no_tags',
        '',
        30,
    ),
    (   # one tag matched, no zone and category
        ['tag_mismatch', 'tag1'],
        'unknown_zone_must_use_global_default_if_there_were_no_tags',
        '',
        40,
    ),
    (   # all tags matched (use max), have zone and category
        ['tag0', 'tag1'],
        'krasnogorsk',
        'econom',
        40,
    ),
    (   # tags mismatched, have zone and category
        ['tag_mismatch'],
        'krasnogorsk',
        'business',
        180,
    ),
    (   # tags mismatched, no zone and category
        ['tag_mismatch'],
        'unknown_zone_must_use_global_default',
        '',
        10,
    ),
])
@pytest.mark.config(
    DA_OFFER_TIMEOUT_BY_TARIFF={
        "__default__": {
            "__default__": 10
        },
        "krasnogorsk": {
            "__default__": 60,
            "econom": 120,
            "business": 180
        },
        "moscow": {
            "__default__": 11,
            "econom": 12,
            "business": 13
        },
    },
    ENABLE_DRIVER_TAGS_FETCHING=True,
    DA_OFFER_TIMEOUT_BY_TAGS={
        "tag0": 30,
        "tag1": 40,
    },
)
@pytest.inline_callbacks
def test_get_offer_timeout(driver_tags, zone, category, expected_timeout):
    timeout = yield order_helpers.get_offer_timeout(
        zone, category, driver_tags
    )
    assert timeout == expected_timeout

APPLICATION_MAP_BRAND_DEFAULT = {
    '__default__': 'yataxi',
    'android': 'yataxi',
    'iphone': 'yataxi',
    'uber_android': 'yauber',
    'uber_iphone': 'yauber',
    'yango_android': 'yango',
    'yango_iphone': 'yango',
    'vezet_android': 'vezet',
    'vezet_iphone': 'vezet',
    'callcenter': 'yataxi',
    'vezet_call_center': 'vezet',
}

APPLICATION_BRAND_CATEGORIES_SETS_DEFAULT = {
    '__default__': [
        'econom',
        'comfort'
    ],
    'yauber': [
        'uberx',
        'uberselect'
    ],
    'vezet': [
        'vezeteconom'
    ]
}


@pytest.mark.config(
    APPLICATION_MAP_BRAND=APPLICATION_MAP_BRAND_DEFAULT,
    APPLICATION_BRAND_CATEGORIES_SETS=APPLICATION_BRAND_CATEGORIES_SETS_DEFAULT
)
@pytest.mark.parametrize('expected',
        (
            {
                'econom': set(['yataxi', 'yango']),
                'comfort': set(['yataxi', 'yango']),
                'uberx': set(['yauber']),
                'uberselect': set(['yauber']),
                'vezeteconom': set(['vezet']),
            },
        )
)
@pytest.inline_callbacks
def test_get_categories_to_brands_map(expected):
    categories_to_brands_map = yield brand_helpers.get_categories_to_brands_map()
    assert categories_to_brands_map == expected


@pytest.mark.parametrize('order_doc,expected', [
    ({}, []),
    ({'experiments': ['a', 'b']}, ['a', 'b']),
])
@pytest.mark.filldb(_fill=False)
def test_get_experiments(order_doc, expected):
    assert order_helpers.get_experiments(order_doc) == expected
