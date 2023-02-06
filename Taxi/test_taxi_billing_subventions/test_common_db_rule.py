import contextlib
import datetime as dt
import inspect
import logging

import pytest
import pytz

from taxi_billing_subventions.common import db as db_module
from taxi_billing_subventions.common import intervals
from taxi_billing_subventions.common import models
from taxi_billing_subventions.common import type_aliases as cta
from taxi_billing_subventions.common.db.rule import _converters


@pytest.mark.now('2018-05-09T20:00:00')
@pytest.mark.parametrize(
    'rule_json, initiator_json, zone_json, expected_rule_docs_json',
    [
        (
            'daily_guarantee_rule.json',
            'initiator.json',
            'zone.json',
            'expected_daily_guarantee_docs.json',
        ),
        (
            'dense_geo_booking_rule.json',
            'initiator.json',
            'zone.json',
            'expected_dense_geo_booking_rule_docs.json',
        ),
        (
            'sparse_geo_booking_rule.json',
            'initiator.json',
            'zone.json',
            'expected_sparse_geo_booking_rule_docs.json',
        ),
    ],
)
@pytest.mark.nofilldb()
def test_doc_converter(
        rule_json,
        initiator_json,
        zone_json,
        expected_rule_docs_json,
        load_py_json_dir,
):
    rule: models.Rule
    rule, expected_docs, initiator, zone = load_py_json_dir(
        'test_doc_converter',
        rule_json,
        expected_rule_docs_json,
        initiator_json,
        zone_json,
    )
    converter = db_module.rule.DocConverter(initiator, zone)
    actual_docs = converter.to_rule_docs(rule)
    assert expected_docs == actual_docs


@pytest.mark.parametrize(
    'rule_docs_json, expected_rule_json',
    [('rule_docs.json', 'expected_daily_guarantee_rule.json')],
)
@pytest.mark.nofilldb()
def test_convert_to_daily_guarantee_rule(
        rule_docs_json, expected_rule_json, load_py_json_dir,
):
    # pylint: disable=invalid-name
    expected_rule: models.DailyGuaranteeRule
    rule_docs, expected_rule = load_py_json_dir(
        'test_convert_to_daily_guarantee_rule',
        rule_docs_json,
        expected_rule_json,
    )
    actual_rule = _converters.convert_to_daily_guarantee_rule(
        rule_docs, {'moscow': pytz.timezone('Europe/Moscow')},
    )
    assert actual_rule == expected_rule


@pytest.mark.parametrize(
    'doc_json, expected_rule_json',
    [
        ('doc.json', 'single_order_rule.json'),
        ('guarantee_doc.json', 'single_order_guarantee_rule.json'),
    ],
)
@pytest.mark.nofilldb()
def test_convert_to_single_order_rule(
        doc_json, expected_rule_json, load_py_json_dir,
):
    # pylint: disable=invalid-name
    expected_rule: models.SingleOrderRule
    doc, expected_rule = load_py_json_dir(
        'test_convert_to_single_order_rule', doc_json, expected_rule_json,
    )
    actual_rule = _converters.convert_to_single_order_rule(
        doc, {'moscow': pytz.timezone('Europe/Moscow')}, 1000,
    )
    assert expected_rule.bonus_calculator == actual_rule.bonus_calculator
    assert expected_rule == actual_rule


@pytest.mark.parametrize(
    'doc_json, expected_rule_json', [('doc.json', 'discount_rule.json')],
)
@pytest.mark.nofilldb()
def test_convert_to_discount_rule(
        doc_json, expected_rule_json, load_py_json_dir,
):
    doc, expected_rule = load_py_json_dir(
        'test_convert_to_discount_rule', doc_json, expected_rule_json,
    )
    actual_rule = _converters.convert_to_discount_rule(
        doc, {'moscow': pytz.timezone('Europe/Moscow')},
    )
    assert expected_rule == actual_rule


@pytest.mark.parametrize(
    'docs_json, expected_rule_json', [('docs.json', 'goal_rule.json')],
)
@pytest.mark.nofilldb()
def test_convert_to_goal_rule(docs_json, expected_rule_json, load_py_json_dir):
    expected_rule: models.GoalRule
    docs, expected_rule = load_py_json_dir(
        'test_convert_to_goal_rule', docs_json, expected_rule_json,
    )
    actual_rule = _converters.convert_to_goal_rule(
        docs, {'moscow': pytz.timezone('Europe/Moscow')},
    )
    assert expected_rule == actual_rule


@pytest.mark.parametrize('docs_json', ['docs.json', 'discount_doc.json'])
@pytest.mark.nofilldb()
def test_convert_to_single_order_goal_rule_error(docs_json, load_py_json_dir):
    # pylint: disable=invalid-name
    docs = load_py_json_dir(
        'test_convert_to_single_order_goal_rule_error', docs_json,
    )
    with pytest.raises(_converters.ConvertError):
        _converters.convert_to_single_order_goal_rule(
            docs, {'moscow': pytz.timezone('Europe/Moscow')}, priority=1000,
        )


@pytest.mark.parametrize(
    'docs_json, expected_rule_json',
    [('docs.json', 'single_order_goal_rule.json')],
)
@pytest.mark.nofilldb()
def test_convert_to_single_order_goal_rule(
        docs_json, expected_rule_json, load_py_json_dir,
):
    # pylint: disable=invalid-name
    expected_rule: models.SingleOrderRule
    docs, expected_rule = load_py_json_dir(
        'test_convert_to_single_order_goal_rule',
        docs_json,
        expected_rule_json,
    )
    actual_rule = _converters.convert_to_single_order_goal_rule(
        docs, {'moscow': pytz.timezone('Europe/Moscow')}, priority=1000,
    )
    assert expected_rule == actual_rule


@pytest.mark.parametrize(
    'order_json, expected_rules_json, expectation',
    [
        ('order.json', 'rules.json', contextlib.nullcontext()),
        (
            'old_order.json',
            'rules.json',
            pytest.raises(_converters.ConvertError),
        ),
    ],
)
@pytest.mark.filldb(subvention_rules='for_test_fetch_default_rules')
async def test_fetch_default_rules(
        order_json, expected_rules_json, expectation, db, load_py_json_dir,
):
    order: models.doc.Order
    order, expected_rules = load_py_json_dir(
        'test_fetch_default_rules', order_json, expected_rules_json,
    )
    with expectation:
        actual_rules = await db_module.rule.fetch_default_rules(
            database=db,
            zone_name=order.zone_name,
            due_interval=intervals.singleton(order.due),
            tzinfo=order.tzinfo,
            active_week_days=[order.local_due.isoweekday()],
            log_extra=None,
        )
        assert _sorted_by_identity_id(
            expected_rules,
        ) == _sorted_by_identity_id(actual_rules)


@pytest.mark.parametrize('order_json', ['order.json'])
@pytest.mark.filldb(
    personal_subvention_rules='for_test_fetch_personal_rules_'
    'returns_empty_list_if_no_mappings',
    personal_subventions='for_test_fetch_personal_rules_'
    'returns_empty_list_if_no_mappings',
)
# pylint: disable=invalid-name
async def test_fetch_personal_rules_returns_empty_list_if_no_mappings(
        order_json, db, load_py_json_dir,
):
    order: models.doc.Order = load_py_json_dir(
        'test_fetch_personal_rules/returns_empty_list_if_no_mappings',
        order_json,
    )
    actual_rules = await db_module.rule.fetch_personal_rules_by_order(
        database=db, order=order, log_extra=None,
    )
    assert not actual_rules


@pytest.fixture
async def log_test(loop, patched_syslog_handler):
    log_settings = {
        'logger_names': ['taxi_billing_subventions'],
        'ident': 'log_extra',
        'log_level': logging.INFO,
        'log_format': '',
    }
    from taxi.logs import log
    log.init_logger(**log_settings)
    yield patched_syslog_handler
    log.cleanup_logger(log_settings['logger_names'])


@pytest.mark.parametrize(
    'order_json, expected_rules_json',
    [
        ('order_at_mapping_start.json', 'rules_at_mapping_start.json'),
        ('order_at_mapping_end.json', 'rules_at_mapping_end.json'),
        ('order_before_mapping_start.json', 'rules_before_mapping_start.json'),
        ('order_before_mapping_end.json', 'rules_before_mapping_end.json'),
    ],
)
@pytest.mark.filldb(
    personal_subvention_rules='for_test_fetch_personal_rules_'
    'respects_mapping_time_interval',
    personal_subventions='for_test_fetch_personal_rules_'
    'respects_mapping_time_interval',
)
# pylint: disable=invalid-name
async def test_fetch_personal_rules_respects_mapping_time_interval(
        order_json, expected_rules_json, db, load_py_json_dir,
):
    order: models.doc.Order
    order, expected_rules = load_py_json_dir(
        'test_fetch_personal_rules/respects_mapping_time_interval',
        order_json,
        expected_rules_json,
    )
    actual_rules = await db_module.rule.fetch_personal_rules_by_order(
        database=db, order=order, log_extra=None,
    )
    assert _sorted_by_identity_id(actual_rules) == _sorted_by_identity_id(
        expected_rules,
    )


@pytest.mark.parametrize(
    'order_json, expected_rules_json',
    [
        ('order_at_rule_start.json', 'rules_at_rule_start.json'),
        ('order_at_rule_end.json', 'rules_at_rule_end.json'),
        ('order_before_rule_start.json', 'rules_before_rule_start.json'),
        ('order_before_rule_end.json', 'rules_before_rule_end.json'),
    ],
)
@pytest.mark.filldb(
    personal_subvention_rules='for_test_fetch_personal_rules_'
    'respects_rule_time_interval',
    personal_subventions='for_test_fetch_personal_rules_'
    'respects_rule_time_interval',
)
# pylint: disable=invalid-name
async def test_fetch_personal_rules_respects_rule_time_interval(
        order_json, expected_rules_json, db, load_py_json_dir,
):
    order: models.doc.Order
    order, expected_rules = load_py_json_dir(
        'test_fetch_personal_rules/respects_rule_time_interval',
        order_json,
        expected_rules_json,
    )
    actual_rules = await db_module.rule.fetch_personal_rules_by_order(
        database=db, order=order, log_extra=None,
    )
    assert _sorted_by_identity_id(expected_rules) == _sorted_by_identity_id(
        actual_rules,
    )


@pytest.mark.parametrize(
    'order_json, expected_rules_json', [('order.json', 'rules.json')],
)
@pytest.mark.filldb(
    personal_subvention_rules='for_test_fetch_personal_rules_ignores_hours',
    personal_subventions='for_test_fetch_personal_rules_ignores_hours',
)
# pylint: disable=invalid-name
async def test_fetch_personal_rules_ignores_hours(
        order_json, expected_rules_json, db, load_py_json_dir,
):
    order: models.doc.Order
    order, expected_rules = load_py_json_dir(
        'test_fetch_personal_rules/ignores_hours',
        order_json,
        expected_rules_json,
    )
    actual_rules = await db_module.rule.fetch_personal_rules_by_order(
        database=db, order=order, log_extra=None,
    )
    assert _sorted_by_identity_id(actual_rules) == _sorted_by_identity_id(
        expected_rules,
    )


def _sorted_by_identity_id(rules):
    return sorted(rules, key=_by_identity_id)


def _by_identity_id(rule):
    return rule.identity.id


@pytest.mark.parametrize(
    'utc_now, expected_rule_ids',
    [
        (
            dt.datetime(2018, 5, 12, tzinfo=pytz.utc),
            ['geo_booking_id_2', 'geo_booking_id_3'],
        ),
        (dt.datetime(2018, 5, 21, tzinfo=pytz.utc), []),
    ],
)
@pytest.mark.filldb(subvention_rules='for_test_fetch_geo_booking_rules')
async def test_fetch_geo_booking_rules(
        db, utc_now: cta.TZInfo, expected_rule_ids,
):
    rules = await db_module.rule.fetch_geo_booking_rules(
        db, intervals.at_least(utc_now), {'moscow': pytz.UTC},
    )
    actual_rule_ids = sorted([rule.identity.group_id for rule in rules])
    assert expected_rule_ids == actual_rule_ids


@pytest.mark.parametrize(
    'ref_str, expected_rule_json',
    [
        ('subvention_agreement/1/default/_id/some_id', 'default_rule.json'),
        (
            'subvention_agreement/1/default/group_id/goal_rule_group_id',
            'default_goal.json',
        ),
        (
            'subvention_agreement/1/personal/_id/p_some_id',
            'personal_rule.json',
        ),
        (
            'subvention_agreement/1/personal/group_id/p_goal_rule_group_id',
            'personal_goal.json',
        ),
    ],
)
@pytest.mark.filldb(
    subvention_rules='for_test_fetch_rule_by_agreement_ref',
    personal_subvention_rules='for_test_fetch_rule_by_agreement_ref',
)
# pylint: disable=invalid-name
async def test_fetch_rule_by_agreement_ref(
        ref_str, expected_rule_json, db, load_py_json_dir,
):
    tzinfo_by_zone = {'moscow': pytz.timezone('Europe/Moscow')}
    expected_rule = load_py_json_dir(
        'test_fetch_rule_by_agreement_ref', expected_rule_json,
    )
    ref = models.AgreementRef.from_str(ref_str)
    actual_rule = await db_module.rule.fetch_rule_by_agreement_ref(
        database=db,
        agreement_ref=ref,
        tzinfo_by_zone=tzinfo_by_zone,
        log_extra=None,
    )
    assert expected_rule == actual_rule


@pytest.mark.parametrize(
    'doc_id, expected_rule_or_error',
    [
        ('5dc45e833fd694916ab26be1', 'driver_fix_rule.json'),
        ('5dc45e833fd694916ab26be0', RuntimeError),
    ],
)
@pytest.mark.filldb(subvention_rules='for_test_fetch_driver_fix_rule_by_id')
async def test_fetch_driver_fix_rule_by_id(
        db, load_py_json_dir, doc_id, expected_rule_or_error,
):
    tzinfo_by_zone = {'moscow': pytz.timezone('Europe/Moscow')}
    fun = db_module.rule.fetch_driver_fix_rule_by_id(
        database=db, doc_id=doc_id, tzinfo_by_zone=tzinfo_by_zone,
    )
    if inspect.isclass(expected_rule_or_error):
        with pytest.raises(expected_rule_or_error):
            await fun
    else:
        expected_rule = load_py_json_dir(
            'test_fetch_driver_fix_rule_by_id', expected_rule_or_error,
        )
        actual_rule = await fun
        assert actual_rule == expected_rule


@pytest.mark.parametrize(
    'key, as_of, expected_rules_json',
    [
        (
            {
                'zone_name': 'moscow',
                'profile_tariff_classes': ('econom', 'comfort'),
                'profile_payment_type_restrictions': 'online',
                'tags': ('driver_fix_cheap',),
            },
            dt.datetime(2018, 5, 11, tzinfo=dt.timezone.utc),
            'driver_fix_rules.json',
        ),
    ],
)
@pytest.mark.filldb(subvention_rules='for_test_fetch_driver_fix_rules_by_key')
async def test_fetch_driver_fix_rules_by_key(
        db, load_py_json_dir, key, as_of, expected_rules_json,
):
    tzinfo_by_zone = {'moscow': pytz.timezone('Europe/Moscow')}
    actual_rules = await db_module.rule.fetch_driver_fix_rules_by_key(
        database=db,
        key=models.DriverFixRuleKey(**key),
        as_of=as_of,
        tzinfo_by_zone=tzinfo_by_zone,
    )
    expected_rules = load_py_json_dir(
        'test_fetch_driver_fix_rules_by_key', expected_rules_json,
    )
    assert actual_rules == expected_rules


@pytest.mark.parametrize(
    'rule, tzinfo, expected_start, expected_end',
    [
        # legacy logic
        (
            {
                '_id': 'p_personal',
                'group_id': '',
                'dayridecount_days': 5,
                'start': dt.datetime(2020, 5, 31, 20),
                'end': dt.datetime(2020, 6, 1, 20),
            },
            pytz.timezone('Europe/Moscow'),
            dt.datetime(2020, 5, 27, 20, tzinfo=dt.timezone.utc),
            dt.datetime(2020, 6, 1, 20, tzinfo=dt.timezone.utc),
        ),
        (
            {
                '_id': 'p_personal',
                'group_id': '',
                'dayridecount_days': 5,
                'start': dt.datetime(2020, 5, 27, 20),
                'end': dt.datetime(2020, 6, 1, 20),
            },
            pytz.timezone('Europe/Moscow'),
            dt.datetime(2020, 5, 27, 20, tzinfo=dt.timezone.utc),
            dt.datetime(2020, 6, 1, 20, tzinfo=dt.timezone.utc),
        ),
        # if end - start != 1 then we use start as is
        (
            {
                '_id': 'p_personal',
                'group_id': '',
                'dayridecount_days': 5,
                'start': dt.datetime(1999, 1, 1, 20),
                'end': dt.datetime(2020, 6, 1, 20),
            },
            pytz.timezone('Europe/Moscow'),
            dt.datetime(1999, 1, 1, 20, tzinfo=dt.timezone.utc),
            dt.datetime(2020, 6, 1, 20, tzinfo=dt.timezone.utc),
        ),
    ],
)
def test_get_dates_range(rule, tzinfo, expected_start, expected_end):
    # pylint: disable=protected-access
    start, end = db_module.rule._converters._get_dates_range(rule, tzinfo)
    assert start == expected_start
    assert end == expected_end
