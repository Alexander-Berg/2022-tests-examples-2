import copy
import datetime

import pytest

from taxi.core import async
from taxi.core import db
from taxi.internal import dbh
from taxi.internal.subvention_kit import personal_subventions


_NOW = datetime.datetime(2017, 5, 12, 14, 33)


def _make_personal_doc(
        unique_driver_id, rule_id, start, end, driver_profiles, tickets,
        created):
    doc = dbh.personal_subventions.Doc()
    doc.unique_driver_id = unique_driver_id
    doc.rule_id = rule_id
    doc.start = start
    doc.end = end
    doc.driver_profiles = []
    for clid_uuid, db_id, locale in driver_profiles:
        profile_embed = doc.driver_profiles.new()
        profile_embed.driver_profile_id = clid_uuid.split('_', 1)[1]
        profile_embed.db_id = db_id
        profile_embed.locale = locale
    doc.tickets = tickets
    doc.created = created
    doc.phones = []
    return doc


def _make_rule_doc(rule_id):
    doc = dbh.subvention_rules.Doc()
    doc._id = rule_id
    return doc


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(
    personal_subventions='for_test_update_with_drivers',
    personal_subvention_rules='for_test_update_with_drivers',
)
@pytest.mark.parametrize(
    'driver_infos, ticket, expected_num_added, expected_doc', [
        # nothing to be done
        (
            [],
            'TAXIRATE-1',
            0,
            None,
        ),
        # add one
        (
            [
                personal_subventions.DriverInfo(
                    unique_driver_id='some_unique_driver_id',
                    rule_id='some_rule_id',
                    start=datetime.datetime(2016, 1, 1),
                    end=datetime.datetime(2019, 1, 1),
                    ids=[
                        personal_subventions.DriverId(
                            driver_profile_id='9234',
                            db_id='some_db_id',
                            locale='ru',
                        )
                    ],
                    phones=[],
                ),
            ],
            'TAXIRATE-2',
            1,
            _make_personal_doc(
                unique_driver_id='some_unique_driver_id',
                rule_id='some_rule_id',
                start=datetime.datetime(2016, 1, 1),
                end=datetime.datetime(2019, 1, 1),
                driver_profiles=[('1234_9234', 'some_db_id', 'ru')],
                tickets=['TAXIRATE-2'],
                created=_NOW,
            )
        ),
    ])
@pytest.inline_callbacks
def test_update_with_drivers(
        driver_infos, ticket, expected_num_added, expected_doc):
    num_before = yield _get_num_personal_subventions()
    ids_before = yield _get_ids_of_personal_subventions()
    yield personal_subventions.update_with_driver_infos(driver_infos, ticket)
    num_after = yield _get_num_personal_subventions()
    assert (num_after - num_before) == expected_num_added

    if expected_doc is not None:
        assert expected_num_added == 1
        ids_after = yield _get_ids_of_personal_subventions()
        doc_id = (set(ids_after) - set(ids_before)).pop()
        actual_doc = yield dbh.personal_subventions.Doc.find_one_by_id(doc_id)
        del actual_doc._id
        assert isinstance(actual_doc.updated, datetime.datetime)
        del actual_doc.updated
        assert actual_doc == expected_doc


@pytest.mark.filldb(
    personal_subventions='for_test_find_rules_by_unique_driver_ids',
    subvention_rules='for_test_find_rules_by_unique_driver_ids',
    personal_subvention_rules='for_test_find_rules_by_unique_driver_ids',
)
@pytest.mark.parametrize(
    'unique_driver_ids,period_begin,period_end,expected_rules', [
        (
            ['some_unique_driver_id'],
            _NOW,
            datetime.datetime(3000, 1, 1),
            {
                'some_unique_driver_id': [
                    _make_rule_doc('personal_rule_id'),
                ]
            }
        ),
        (
            ['some_unique_driver_id', 'another_unique_driver_id'],
            _NOW,
            datetime.datetime(3000, 1, 1),
            {
                'some_unique_driver_id': [
                    _make_rule_doc('personal_rule_id'),
                ],
                'another_unique_driver_id': [
                    _make_rule_doc('personal_rule_id'),
                ],
            }
        ),
        (
            ['some_unique_driver_id', 'another_unique_driver_id'],
            _NOW,
            _NOW,
            {
                'some_unique_driver_id': [
                    _make_rule_doc('personal_rule_id'),
                ],
                'another_unique_driver_id': [
                    _make_rule_doc('personal_rule_id'),
                ],
            }
        ),
        (
            ['some_unique_driver_id', 'another_unique_driver_id'],
            datetime.datetime(2000, 1, 1),
            datetime.datetime(2017, 5, 1),
            {
                'some_unique_driver_id': [
                    _make_rule_doc('personal_rule_id'),
                    _make_rule_doc('personal_expired_rule_id'),
                ],
                'another_unique_driver_id': [
                    _make_rule_doc('personal_rule_id'),
                ],
            }
        ),
        (
            ['some_unique_driver_id'],
            datetime.datetime(2017, 1, 1, 1),
            datetime.datetime(3000, 1, 1),
            {
                'some_unique_driver_id': [
                    _make_rule_doc('personal_expired_rule_id'),
                    _make_rule_doc('personal_rule_id'),
                ],
            }
        )
    ]
)
@pytest.inline_callbacks
def test_find_rules_by_unique_driver_ids(
        unique_driver_ids, period_begin, period_end, expected_rules):
    actual_rules = yield personal_subventions.find_rules_by_unique_driver_ids(
        unique_driver_ids=unique_driver_ids,
        period_begin=period_begin,
        period_end=period_end,
        is_once_bonus=False,
        use_archive=True,
    )
    assert _sorted_by_rule_id(actual_rules) == _sorted_by_rule_id(expected_rules)


def _sorted_by_rule_id(rules_by_unique_driver_id):
    result = copy.deepcopy(rules_by_unique_driver_id)
    for rules in result.itervalues():
        rules.sort(key=lambda rule: rule.pk)
    return result


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(
    archive_personal_subventions='for_test_do_archive',
    personal_subventions='for_test_do_archive',
)
@pytest.mark.parametrize('max_age, expected_ids, expected_archive_ids', [
    (
        datetime.timedelta(days=1),
        ['active_id'],
        ['old_id', 'fresh_id', 'archived_id'],
    ),
    (
        datetime.timedelta(days=3),
        ['active_id', 'fresh_id'],
        ['old_id', 'archived_id'],
    ),
])
@pytest.inline_callbacks
def test_do_archive(
    max_age, expected_ids, expected_archive_ids):
    yield personal_subventions.do_archive(max_age)
    actual_ids = yield _get_ids_of_personal_subventions()
    actual_archive_ids = yield _get_ids_of_archive_personal_subventions()
    assert set(actual_ids) == set(expected_ids)
    assert set(actual_archive_ids) == set(expected_archive_ids)


@async.inline_callbacks
def _get_num_personal_subventions():
    count = yield db.personal_subventions.count()
    async.return_value(count)


@async.inline_callbacks
def _get_ids_of_personal_subventions():
    ids = yield db.personal_subventions.distinct('_id')
    async.return_value(ids)


@async.inline_callbacks
def _get_ids_of_archive_personal_subventions():
    ids = yield db.archive_personal_subventions.distinct('_id')
    async.return_value(ids)


@async.inline_callbacks
def _get_personal_subventions_data():
    personal = yield dbh.personal_subventions.Doc.find_many()
    result = {
        ps.pk: {
            dbh.personal_subventions.Doc.end: ps.end,
            dbh.personal_subventions.Doc.tickets: ps.tickets,
        }
        for ps in personal
    }
    async.return_value(result)


@pytest.mark.now("2017-05-12T14:33:00.0")
@pytest.mark.filldb(
    archive_personal_subvention_rules='for_test_do_archive_of_rules',
    personal_subvention_rules='for_test_do_archive_of_rules',
)
@pytest.mark.parametrize('max_age, expected_ids, expected_archive_ids', [
    (
        datetime.timedelta(days=1),
        ['active_id'],
        ['old_id', 'fresh_id', 'archived_id'],
    ),
    (
        datetime.timedelta(days=3),
        ['active_id', 'fresh_id'],
        ['old_id', 'archived_id'],
    ),
])
@pytest.inline_callbacks
def test_do_archive_of_rules(
    max_age, expected_ids, expected_archive_ids):
    yield personal_subventions.do_archive_of_rules(max_age)
    actual_ids = yield _get_ids_of_personal_subvention_rules()
    actual_archive_ids = yield _get_ids_of_archive_personal_subvention_rules()
    assert set(actual_ids) == set(expected_ids)
    assert set(actual_archive_ids) == set(expected_archive_ids)


@async.inline_callbacks
def _get_ids_of_personal_subvention_rules():
    ids = yield db.personal_subvention_rules.distinct('_id')
    async.return_value(ids)


@async.inline_callbacks
def _get_ids_of_archive_personal_subvention_rules():
    ids = yield db.archive_personal_subvention_rules.distinct('_id')
    async.return_value(ids)
