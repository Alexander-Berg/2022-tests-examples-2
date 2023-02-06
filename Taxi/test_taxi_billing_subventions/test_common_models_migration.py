import datetime

import pytest

from taxi_billing_subventions.common import models

_NEW_BILLING_MIGRATION = {
    'subventions': {
        'enabled': {
            'obninsk': [
                {'first_date': '2019-06-13', 'last_date': '2019-06-18'},
            ],
            'kaluga': [{'first_date': '2019-06-13'}],
            '__default__': [
                {'first_date': '3000-01-01', 'last_date': '9999-12-31'},
            ],
        },
        'disabled': {
            'kaluga': [
                {'first_date': '2020-01-01', 'last_date': '2020-12-31'},
            ],
        },
    },
}


@pytest.mark.parametrize(
    'query,expected',
    [
        # kind is missing from config
        (
            models.Migration.Query(
                'commissions', 'obninsk', datetime.date(2019, 6, 13),
            ),
            False,
        ),
        # zone is missing from config
        (
            models.Migration.Query(
                'subventions', 'spb', datetime.date(2019, 6, 13),
            ),
            False,
        ),
        # enabled explicitly
        (
            models.Migration.Query(
                'subventions', 'obninsk', datetime.date(2019, 6, 13),
            ),
            True,
        ),
        # enabled via __default__
        (
            models.Migration.Query(
                'subventions', 'spb', datetime.date(9999, 12, 31),
            ),
            True,
        ),
        # too early to be enabled
        (
            models.Migration.Query(
                'subventions', 'obninsk', datetime.date(2019, 6, 12),
            ),
            False,
        ),
        # too late to be enabled
        (
            models.Migration.Query(
                'subventions', 'obninsk', datetime.date(2019, 6, 19),
            ),
            False,
        ),
        # enabled via half-open interval
        (
            models.Migration.Query(
                'subventions', 'kaluga', datetime.date(2019, 6, 13),
            ),
            True,
        ),
        # enabled via half-open interval in the distant future
        (
            models.Migration.Query(
                'subventions', 'kaluga', datetime.date(2199, 1, 1),
            ),
            True,
        ),
        # disabled via half-open interval
        (
            models.Migration.Query(
                'subventions', 'kaluga', datetime.date(2019, 6, 12),
            ),
            False,
        ),
        # disabled explicitly
        (
            models.Migration.Query(
                'subventions', 'kaluga', datetime.date(2020, 5, 1),
            ),
            False,
        ),
    ],
)
@pytest.mark.nofilldb
def test_migration(query, expected):
    actual = models.Migration(_NEW_BILLING_MIGRATION).is_enabled(
        query, log_extra=None,
    )
    assert expected is actual
