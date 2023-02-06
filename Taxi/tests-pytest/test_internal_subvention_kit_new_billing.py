import datetime

import pytest

from taxi import config
from taxi.internal.subvention_kit import new_billing

_migration = {
    'subventions': {
        'enabled': {
            'obninsk': [
                {
                    'first_date': '2019-06-13',
                    'last_date': '2019-06-18'
                }
            ],
            'kaluga': [
                {
                    'first_date': '2019-06-13',
                }
            ],
            '__default__': [
                {
                    'first_date': '3000-01-01',
                    'last_date': '9999-12-31',
                }
            ]
        },
        'disabled': {
            'kaluga': [
                {
                    'first_date': '2020-01-01',
                    'last_date': '2020-12-31',
                }
            ]
        }
    }
}


@pytest.mark.parametrize('query,expected', [
    # kind is missing from config
    (
        new_billing.Query('commissions', 'obninsk', datetime.date(2019, 6, 13)),
        False,
    ),
    # zone is missing from config
    (
        new_billing.Query('subventions', 'spb', datetime.date(2019, 6, 13)),
        False,
    ),
    # enabled explicitly
    (
        new_billing.Query('subventions', 'obninsk', datetime.date(2019, 6, 13)),
        True,
    ),
    # enabled via __default__
    (
        new_billing.Query('subventions', 'spb', datetime.date(9999, 12, 31)),
        True,
    ),
    # too early to be enabled
    (
        new_billing.Query('subventions', 'obninsk', datetime.date(2019, 6, 12)),
        False,
    ),
    # too late to be enabled
    (
        new_billing.Query('subventions', 'obninsk', datetime.date(2019, 6, 19)),
        False,
    ),
    # enabled via half-open interval
    (
        new_billing.Query('subventions', 'kaluga', datetime.date(2019, 6, 13)),
        True,
    ),
    # enabled via half-open interval in the distant future
    (
        new_billing.Query('subventions', 'kaluga', datetime.date(2199, 1, 1)),
        True,
    ),
    # disabled via half-open interval
    (
        new_billing.Query('subventions', 'kaluga', datetime.date(2019, 6, 12)),
        False,
    ),
    # disabled explicitly
    (
        new_billing.Query('subventions', 'kaluga', datetime.date(2020, 5, 1)),
        False,
    ),
])
@pytest.mark.config(
    NEW_BILLING_MIGRATION=_migration,
)
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_migration(query, expected):
    raw_config = yield config.NEW_BILLING_MIGRATION.get()
    actual = new_billing.Migration(raw_config).is_enabled(query)
    assert expected is actual
