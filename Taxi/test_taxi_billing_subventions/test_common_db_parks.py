import datetime
import decimal

import pytest

from taxi_billing_subventions.common import db as common_db


class Config:
    def __init__(self, park_account_history_usage: str):
        # pylint: disable=invalid-name
        self.PARK_ACCOUNT_HISTORY_USAGE = park_account_history_usage


@pytest.mark.parametrize(
    'park_id, park_account_history_usage, expected_park_json',
    [
        ('1956789018', 'disable', 'park_1956789018.json'),
        ('400000004233', 'disable', 'park_400000004233.json'),
        ('400000057652', 'disable', 'park_400000057652.json'),
        (
            'with_account_history',
            'reconcile',
            'park_with_account_history.json',
        ),
        ('with_account_history', 'enable', 'park_with_account_history.json'),
    ],
)
@pytest.mark.filldb(parks='for_test_fetch_park')
async def test_fetch_park(
        db,
        load_py_json,
        park_id,
        park_account_history_usage,
        expected_park_json,
):
    expected_park = load_py_json(expected_park_json)

    park = await common_db.parks.fetch_park(
        database=db,
        config=Config(park_account_history_usage=park_account_history_usage),
        park_id=park_id,
        log_extra=None,
    )
    assert park == expected_park


async def test_fetch_park_not_found(db, load_json):
    with pytest.raises(common_db.parks.ParkNotFoundError):
        await common_db.parks.fetch_park(
            database=db,
            config=Config(park_account_history_usage='disable'),
            park_id='This park never existed',
            log_extra=None,
        )


@pytest.mark.filldb(parks='for_test_fetch_park')
@pytest.mark.parametrize(
    'check_at,expected',
    (
        ('2019-12-31T23:59:59+00:00', decimal.Decimal('1.18')),
        ('2020-01-01T12:00:00+00:00', decimal.Decimal('1.2')),
        ('2020-12-31T23:59:59+00:00', decimal.Decimal('1.2')),
        ('2021-01-01T12:00:00+00:00', None),
    ),
)
async def test_park_get_vat_at(db, check_at, expected):
    park = await common_db.parks.fetch_park(
        database=db,
        config=Config(park_account_history_usage='disable'),
        park_id='400000004233',
        log_extra=None,
    )
    now = datetime.datetime.fromisoformat(check_at)
    assert park.get_vat_at(now) == expected
