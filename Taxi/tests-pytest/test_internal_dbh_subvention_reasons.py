import collections
import datetime

import pytest

from taxi.core import async
from taxi.internal import dbh
from taxi.util import decimal

_CalcRuleInfo = collections.namedtuple(
    '_CalcRuleInfo', [
        'id',
        'sum',
        'type',
        'is_fake',
        'is_holded',
        'display_in_taximeter',
        'decline_reasons'
    ]
)


@pytest.inline_callbacks
def fetch_subvention_reasons_by_order_id(
        order_id, result_id='fake_id', pop_updated=True):
    result = yield dbh.subvention_reasons.Doc.find_one_by_order_id(order_id)
    result._id = result_id  # generated randomly each time
    if pop_updated:
        result.pop('updated')  # done in mongo, can not change it
    async.return_value(result)


@pytest.mark.parametrize(
    'order_proc_dict,calc_dict_rules,expected_doc', [
        (
            # order_proc_dict
            {
                '_id': 'fake_order_proc',
                'created': '2017-08-03T00:00:00',
                'performer': {
                    'alias_id': 'fake_alias_id',
                    'driver_id': 'fake_driver_id',
                    'candidate_index': 0
                },
                'candidates': [{
                    'driver_id': 'fake_driver_id',
                    'alias_id': 'fake_alias_id',
                }],
                'aliases': [{
                    'id': 'fake_alias_id',
                    'due': '2017-08-03T00:00:00'
                }]
            },
            # calc_dict_rules
            [
                {
                    'id': 'fake_id',
                    'sum': '135.6',
                    'type': 'test_type',
                    'is_fake': True,
                    'sub_commission': False,
                    'is_bonus': False,
                    'is_once': True,
                    'decline_reasons': [
                        {
                            'key': 'test_key',
                            'reason': 'fake reason',
                            'minimum': 25,
                            'value': 46
                        },
                        {
                            'key': 'other_test_key',
                            'reason': 'just because'
                        }
                    ]
                }
            ],
            # expected_doc
            {
                'subvention_calc_rules': [
                    {
                        'id': 'fake_id',
                        'sum': '135.6',
                        'type': 'test_type',
                        'is_fake': True,
                        'sub_commission': False,
                        'is_bonus': False,
                        'is_once': True,
                        'decline_reasons': [
                            {
                                'key': 'test_key',
                                'reason': 'fake reason',
                                'minimum': 25,
                                'value': 46
                            },
                            {
                                'key': 'other_test_key',
                                'reason': 'just because'
                            }
                        ]
                    }
                ],
                '_id': 'fake_id',
                'order_id': 'fake_order_proc',
                'due': '2017-08-03T00:00:00',
                'driver_id': 'fake_driver_id',
                'alias_id': 'fake_alias_id',
                'tickets': [],
                'is_fraud': False,
                'version': 1,
                'is_calculated': False,
            }
    ),
])
@pytest.inline_callbacks
def test_add_by_order_proc(order_proc_dict, calc_dict_rules,
                           expected_doc):
    all_subvention_reasons = yield dbh.subvention_reasons.Doc.find_many()
    assert not all_subvention_reasons
    order_proc = dbh.order_proc.Doc(order_proc_dict)
    yield dbh.subvention_reasons.Doc.add_by_order_proc(
        order_proc, calc_dict_rules
    )
    result = yield fetch_subvention_reasons_by_order_id(order_proc.pk)
    assert dict(result) == expected_doc, result


@pytest.mark.parametrize(
    'order_id,bonus_values,expected_bonus,expected_details', [
        (
            'fake_order_id1',
            [('reason_1', '3000')],
            decimal.Decimal('3000'),
            {'reason_1': '3000'}
        ),
        (
            'fake_order_id2',
            [('reason_1', '2000'), ('reason_2', '4000')],
            decimal.Decimal('6000'),
            {'reason_1': '2000', 'reason_2': '4000'}
        ),
        (
            'fake_order_id2',
            [('reason_1', '2000'), ('reason_1', '4000')],
            decimal.Decimal('4000'),
            {'reason_1': '4000'}
        ),
        ('fake_order_id3', [], decimal.Decimal('0'), {})
])
@pytest.inline_callbacks
def test_subvention_bonus(order_id, bonus_values,
                          expected_bonus, expected_details):
    all_subvention_reasons = yield dbh.subvention_reasons.Doc.find_many()
    assert not all_subvention_reasons
    order_proc = dbh.order_proc.Doc({
        '_id': order_id,
        'created': '2017-08-03T00:00:00',
        'performer': {
            'alias_id': 'fake_alias_id',
            'driver_id': 'fake_driver_id',
            'candidate_index': 0
        },
        'candidates': [{
            'driver_id': 'fake_driver_id',
            'alias_id': 'fake_alias_id',
        }],
        'aliases': [{
            'id': 'fake_alias_id',
            'due': '2017-08-03T00:00:00'
        }]
    })
    yield dbh.subvention_reasons.Doc.add_by_order_proc(order_proc, [])
    for bonus_reason, bonus_value in bonus_values:
        yield dbh.subvention_reasons.Doc.set_subvention_bonus(
            order_id, bonus_reason, bonus_value
        )
    result = yield fetch_subvention_reasons_by_order_id(order_proc.pk)
    assert len(result.subvention_bonus) == len(bonus_values)
    bonus, details = result.subvention_bonus_value_details
    assert bonus == expected_bonus
    assert details == expected_details


_NOT_FOUND = object()


@pytest.mark.filldb(
    subvention_reasons='for_test_on_clear',
)
@pytest.mark.parametrize(
    'order_id,version,rule_ids,holded_rule_ids,fraud_order_ids,exception,expected_result', [
        (
                'full_clear_order_id',
                None,
                ['guarantee_200_rule_id'],
                ['guarantee_200_rule_id'],
                {'fraud_order_id'},
                None,
                [
                    _CalcRuleInfo(
                        id=u'guarantee_200_rule_id',
                        sum=200,
                        type=u'guarantee',
                        is_fake=False,
                        is_holded=False,
                        display_in_taximeter=True,
                        decline_reasons=[],
                    )
                ]
        ),
        # race condition
        (
                'full_clear_order_id',
                1,
                ['guarantee_200_rule_id'],
                ['guarantee_200_rule_id'],
                set(),
                dbh.exceptions.RaceCondition,
                [
                    _CalcRuleInfo(
                        id=u'guarantee_200_rule_id',
                        sum=200,
                        type=u'guarantee',
                        is_fake=True,
                        is_holded=True,
                        display_in_taximeter=False,
                        decline_reasons=[{
                            u'reason': u'holded',
                            u'key': u'holded',
                            u'till': datetime.datetime(2018, 1, 25, 20, 51)
                        }],
                    )
                ]
        ),
        (
                'partial_clear_order_id',
                None,
                ['add_30_rule_id'],
                ['add_30_rule_id', 'add_60_rule_id'],
                set(),
                None,
                [
                    _CalcRuleInfo(
                        id=u'add_30_rule_id',
                        sum=30,
                        type=u'add',
                        is_fake=False,
                        is_holded=False,
                        display_in_taximeter=True,
                        decline_reasons=[],
                    ),
                    _CalcRuleInfo(
                        id=u'add_60_rule_id',
                        sum=60,
                        type=u'add',
                        is_fake=True,
                        is_holded=True,
                        display_in_taximeter=False,
                        decline_reasons=[
                            {
                                u'reason': u'holded',
                                u'key': u'holded',
                                u'till': datetime.datetime(2018, 2, 1),
                            },
                        ],
                    )
                ]
        ),
        (
                'fraud_order_id',
                None,
                ['guarantee_200_rule_id'],
                ['guarantee_200_rule_id'],
                {'fraud_order_id'},
                None,
                [
                    _CalcRuleInfo(
                        id=u'guarantee_200_rule_id',
                        sum=200,
                        type=u'guarantee',
                        is_fake=True,
                        is_holded=False,
                        display_in_taximeter=False,
                        decline_reasons=[
                            {
                                u'reason': u'holded_fraud',
                                u'key': u'holded_fraud',
                                u'till': datetime.datetime(2018, 1, 25, 20, 51),
                            }
                        ],
                    )
                ]
        ),
        (
                'deleted_order_id',
                None,
                ['guarantee_200_rule_id'],
                ['guarantee_200_rule_id'],
                {'fraud_order_id'},
                None,
                _NOT_FOUND,
        ),
        (
                'already_unholded_order_id',
                None,
                ['guarantee_200_rule_id'],
                ['guarantee_200_rule_id'],
                {'fraud_order_id'},
                None,
                [
                    _CalcRuleInfo(
                        id=u'guarantee_200_rule_id',
                        sum=200,
                        type=u'guarantee',
                        is_fake=False,
                        is_holded=False,
                        display_in_taximeter=True,
                        decline_reasons=[],
                    )
                ]
        ),
        (
                'hanging_holded_order_id',
                None,
                ['guarantee_200_rule_id'],
                ['guarantee_200_rule_id'],
                {'fraud_order_id'},
                None,
                [
                    _CalcRuleInfo(
                        id=u'guarantee_200_rule_id',
                        sum=200,
                        type=u'guarantee',
                        is_fake=False,
                        is_holded=False,
                        display_in_taximeter=True,
                        decline_reasons=[],
                    ),
                    _CalcRuleInfo(
                        id=u'guarantee_300_rule_id',
                        sum=300,
                        type=u'guarantee',
                        is_fake=False,
                        is_holded=False,
                        display_in_taximeter=False,
                        decline_reasons=[],
                    )

                ]
        )
    ]
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_on_clear(
        order_id, version, rule_ids, holded_rule_ids, fraud_order_ids, exception, expected_result):
    try:
        subvention_reason_before = yield dbh.subvention_reasons.Doc.find_one_by_order_id(order_id)
    except dbh.subvention_reasons.NotFound:
        subvention_reason_by_order_id = {}
        rule_ids_by_order_id = {}
        holded_rule_ids_by_order_id = {}
    else:
        if version is not None:
            subvention_reason_before.version = version
        subvention_reason_by_order_id = {
            subvention_reason_before.order_id: subvention_reason_before,
        }
        rule_ids_by_order_id = {
            order_id: rule_ids,
        }
        holded_rule_ids_by_order_id = {
            order_id: holded_rule_ids,
        }
    if exception is not None:
        with pytest.raises(exception):
            yield dbh.subvention_reasons.Doc.on_clear(
                subvention_reason_by_order_id=subvention_reason_by_order_id,
                rule_ids_by_order_id=rule_ids_by_order_id,
                holded_rule_ids_by_order_id=holded_rule_ids_by_order_id,
                fraud_order_ids=fraud_order_ids,
            )
    else:
        yield dbh.subvention_reasons.Doc.on_clear(
            subvention_reason_by_order_id=subvention_reason_by_order_id,
            rule_ids_by_order_id=rule_ids_by_order_id,
            holded_rule_ids_by_order_id=holded_rule_ids_by_order_id,
            fraud_order_ids=fraud_order_ids,
        )
    try:
        subvention_reason_after = yield dbh.subvention_reasons.Doc.find_one_by_order_id(order_id)
    except dbh.subvention_reasons.NotFound:
        assert expected_result is _NOT_FOUND
    else:
        actual_calc_rule_infos = _get_calc_rules_info(subvention_reason_after)
        _assert_different_ids(actual_calc_rule_infos)
        assert (
            sorted(expected_result, key=_by_id)
            == sorted(actual_calc_rule_infos, key=_by_id)
        )


def _by_id(rule):
    return rule.id


def _get_calc_rules_info(subvention_reason):
    """
    :type subvention_reason: taxi.internal.dbh.subvention_reasons.Doc
    :rtype: _CalcRuleInfo
    """
    result = []
    for calc_rule in subvention_reason.subvention_calc_rules:
        info = _make_calc_rule_info(calc_rule)
        result.append(info)
    return result


def _make_calc_rule_info(calc_rule):
    return _CalcRuleInfo(
        id=calc_rule.id,
        sum=calc_rule.sum,
        type=calc_rule.type,
        is_fake=calc_rule.is_fake,
        is_holded=calc_rule.is_holded,
        display_in_taximeter=calc_rule.display_in_taximeter,
        decline_reasons=calc_rule.decline_reasons,
    )


def _assert_different_ids(infos):
    """
    :type infos: list[_CalcRuleInfo]
    """
    counter = collections.Counter(one_info.id for one_info in infos)
    for rule_id, count in counter.iteritems():
        msg = 'got {} rules with id (expected 1)'.format(count, rule_id)
        assert count == 1, msg
