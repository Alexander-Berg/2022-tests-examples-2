import datetime

import pytest

from taxi.billing.util import migration

_NEW_BILLING_MIGRATION = {
    'subventions': {
        'enabled': {
            'obninsk': [
                {
                    'since': '2019-06-13T15:00:00',
                    'till': '2019-06-18T16:00:00',
                },
            ],
            'kaluga': [{'since': '2019-06-13T00:00:00'}],
            '__default__': [
                {
                    'since': '3000-01-01T00:00:00',
                    'till': '9999-12-31T00:00:00',
                },
            ],
        },
        'disabled': {
            'kaluga': [
                {
                    'since': '2020-01-01T00:00:00',
                    'till': '2020-12-31T00:00:00',
                },
            ],
        },
    },
}


@pytest.mark.parametrize(
    'query,expected',
    [
        # kind is missing from config
        (
            migration.Migration.Query(
                'commissions', 'obninsk', datetime.datetime(2019, 6, 13),
            ),
            False,
        ),
        # zone is missing from config
        (
            migration.Migration.Query(
                'subventions', 'spb', datetime.datetime(2019, 6, 13),
            ),
            False,
        ),
        # enabled explicitly
        (
            migration.Migration.Query(
                'subventions', 'obninsk', datetime.datetime(2019, 6, 13, 15),
            ),
            True,
        ),
        # enabled via __default__
        (
            migration.Migration.Query(
                'subventions', 'spb', datetime.datetime(9999, 12, 31),
            ),
            True,
        ),
        # too early to be enabled
        (
            migration.Migration.Query(
                'subventions', 'obninsk', datetime.datetime(2019, 6, 12),
            ),
            False,
        ),
        # too late to be enabled
        (
            migration.Migration.Query(
                'subventions', 'obninsk', datetime.datetime(2019, 6, 19),
            ),
            False,
        ),
        # enabled via half-open interval
        (
            migration.Migration.Query(
                'subventions', 'kaluga', datetime.datetime(2019, 6, 13),
            ),
            True,
        ),
        # enabled via half-open interval in the distant future
        (
            migration.Migration.Query(
                'subventions', 'kaluga', datetime.datetime(2199, 1, 1),
            ),
            True,
        ),
        # disabled via half-open interval
        (
            migration.Migration.Query(
                'subventions', 'kaluga', datetime.datetime(2019, 6, 12),
            ),
            False,
        ),
        # disabled explicitly
        (
            migration.Migration.Query(
                'subventions', 'kaluga', datetime.datetime(2020, 5, 1),
            ),
            False,
        ),
    ],
)
@pytest.mark.nofilldb
def test_migration(query, expected):
    actual = migration.Migration(_NEW_BILLING_MIGRATION).is_enabled(
        query, log_extra=None,
    )
    assert expected is actual
