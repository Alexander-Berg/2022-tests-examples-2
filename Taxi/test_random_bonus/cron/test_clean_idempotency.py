import datetime as dt
import uuid

import pytest

# pylint: disable=redefined-outer-name
from random_bonus.generated.cron import run_cron


NOW_UTC_ISO = '2020-10-31T21:00:00+00:00'


@pytest.mark.config(
    RANDOM_BONUS_CLEAN_IDEMPOTENCY_TOKENS_SETTINGS={
        'enabled': True,
        'days': 2,
    },
)
@pytest.mark.now(NOW_UTC_ISO)
async def test_clean_idempotency_keys(pgsql):
    now = dt.datetime.fromisoformat(NOW_UTC_ISO).astimezone(tz=dt.timezone.utc)
    fill_period = dt.timedelta(days=4)
    with pgsql['random_bonus_db'].cursor() as cursor:
        values = []
        for i in range(30):
            time = now - fill_period * i / 30.0
            values.append(f'(\'{uuid.uuid4().hex}\', \'{time}\'::TIMESTAMPTZ)')

        cursor.execute(
            f"""
            INSERT INTO random_bonus.idempotency_keys
              (key, event_at)
            VALUES
              {','.join(values)}
            ;
            """,
        )

    await run_cron.main(
        ['random_bonus.crontasks.clean_idempotency_tokens', '-t', '0'],
    )

    with pgsql['random_bonus_db'].cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM random_bonus.idempotency_keys;')
        assert cursor.fetchone()[0] == 16
