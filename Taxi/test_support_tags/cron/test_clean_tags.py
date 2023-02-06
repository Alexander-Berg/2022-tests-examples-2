import datetime

import pytest

from support_tags.generated.cron import run_cron


@pytest.mark.now('2021-01-01T00:00:00')
async def test_clean_tag(pgsql):
    with pgsql['support_tags'].cursor() as cursor:
        cursor.execute('SELECT * FROM support_tags.tags')
        records = cursor.fetchall()

    records_not_for_del = set()
    for record in records:
        if not is_old_record(created=record[3], ttl=record[5]):
            records_not_for_del.add(record)
    assert len(records_not_for_del) != len(records)

    await run_cron.main(['support_tags.crontasks.clean_tags', '-t', '0'])

    with pgsql['support_tags'].cursor() as cursor:
        cursor.execute('SELECT * FROM support_tags.tags')
        records = cursor.fetchall()

    assert set(records) == set(records_not_for_del)


def is_old_record(created, ttl):
    if ttl:
        return (
            created + datetime.timedelta(seconds=ttl)
            < datetime.datetime.utcnow()
        )
    return False
