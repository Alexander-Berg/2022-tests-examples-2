import datetime


async def test_updated_created_fields(pgsql):
    cursor = pgsql['plus'].cursor()
    cursor.execute('SELECT created_at, updated_at from plus.user_settings')
    result = list((row[0], row[1]) for row in cursor)

    tzinfo = datetime.timezone(datetime.timedelta(hours=3))
    expected_created = datetime.datetime(2021, 6, 14, 20, 5, 17, tzinfo=tzinfo)
    expected_updated = datetime.datetime(2021, 6, 15, 20, 5, 17, tzinfo=tzinfo)
    assert result == [(expected_created, expected_updated)]
