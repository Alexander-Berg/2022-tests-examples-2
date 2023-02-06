import datetime

import pytest

from taxi.internal import dbh


@pytest.mark.filldb(
    personal_subvention_rules='for_test_find_day_ride_count_thresholds',
)
@pytest.mark.parametrize(
    'zone_name,period_begin,period_end,expected_thresholds', [
        (
            'moscow',
            datetime.datetime(2017, 5, 28, 21),
            datetime.datetime(2017, 5, 29, 21),
            {7: 53, 1: 34},
        ),
    ]
)
@pytest.inline_callbacks
def test_find_day_ride_count_thresholds(
        zone_name, period_begin, period_end, expected_thresholds):
    actual_thresholds = (
        yield dbh.personal_subvention_rules.Doc.find_day_ride_count_thresholds(
            zone_name=zone_name,
            period_begin=period_begin,
            period_end=period_end,
        )
    )
    assert actual_thresholds == expected_thresholds


@pytest.mark.filldb(
    archive_personal_subvention_rules='for_test_find_many_by_ids',
    personal_subvention_rules='for_test_find_many_by_ids',
)
@pytest.mark.parametrize('rule_ids,use_archive,expected_ids', [
    (
        ['some_rule_id', 'archive_rule_id'], False,
        ['some_rule_id'],
    ),
    # archive also has some_rule_id, we deduplicate it
    (
        ['some_rule_id', 'archive_rule_id'], True,
        ['some_rule_id', 'archive_rule_id'],
    ),
])
@pytest.inline_callbacks
def test_find_many_by_ids(rule_ids, use_archive, expected_ids):
    rules = yield dbh.personal_subvention_rules.Doc.find_many_by_ids(
        rule_ids=rule_ids,
        use_archive=use_archive,
    )
    actual_ids = sorted(one_rule.pk for one_rule in rules)
    assert actual_ids == sorted(expected_ids)


@pytest.mark.filldb(
    personal_subvention_rules='for_test_unapproved_rule_is_not_notified'
)
@pytest.inline_callbacks
def test_unapproved_rule_is_not_notified():
    with pytest.raises(dbh.personal_subvention_rules.NotFound):
        yield dbh.personal_subvention_rules.Doc.find_one_to_notify_on()


@pytest.mark.filldb(
    personal_subvention_rules='for_test_approved_rule_is_notified'
)
@pytest.inline_callbacks
def test_approved_rule_is_notified():
    rule = yield dbh.personal_subvention_rules.Doc.find_one_to_notify_on()
    assert rule.pk == 'approved_rule_pk'


@pytest.mark.filldb(
    personal_subvention_rules='for_test_mark_as_notified'
)
@pytest.inline_callbacks
def test_mark_as_notified():
    rule = yield dbh.personal_subvention_rules.Doc.find_one_by_id(
        'some_notified_rule_id')
    updated_rule = yield rule.mark_as_notified()
    assert not updated_rule.needs_notification
    assert updated_rule.updated


@pytest.mark.filldb(
    personal_subvention_rules='for_test_save_send_sms_task_id'
)
@pytest.inline_callbacks
def test_save_send_sms_task_id():
    rule = yield dbh.personal_subvention_rules.Doc.find_one_by_id(
        'some_without_sms_task_rule_id'
    )
    sms_task_id = 'some_sms_task_id'
    updated_rule = yield rule.save_send_sms_task_id(sms_task_id)
    assert updated_rule.send_sms_task_id == sms_task_id
    assert updated_rule.updated


@pytest.mark.parametrize(
    ('data', 'model_class',), [
    (
        {},
        dbh.subvention_rules.GenericRule,
    ),
    (
        {
            'is_once': True,
            'dayridecount': [[7]],
            'hour': range(24),
        },
        dbh.subvention_rules.GenericRule,
    ),
    (
        {
            'is_once': True,
            'dayridecount': [[7]],
            'hour': [16],
        },
        dbh.subvention_rules.stateful_rule.StatefulRule,
    ),
])
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_rule_model_class(data, model_class):
    assert dbh.subvention_rules.Doc(data).model_class() == model_class
