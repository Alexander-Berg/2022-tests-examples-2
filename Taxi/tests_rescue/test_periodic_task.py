INSERT_APPLICATION1 = (
    'INSERT INTO rescue.application '
    '(park_id, driver_profile_id, order_id, '
    ' longtitude, latitude, st_ticket)'
    ' VALUES (\'db_id\', \'uuid\', \'order_id1\', 50.0, 50.0, \'ST-1\')'
)
INSERT_APPLICATION2 = (
    'INSERT INTO rescue.application '
    '(park_id, driver_profile_id, order_id, '
    ' longtitude, latitude, st_ticket)'
    ' VALUES (\'db_id\', \'uuid\', \'order_id2\', 50.0, 50.0, \'ST-1\')'
)
INSERT_APPLICATION3 = (
    'INSERT INTO rescue.application '
    '(park_id, driver_profile_id, order_id, '
    ' longtitude, latitude, st_ticket)'
    ' VALUES (\'db_id\', \'uuid\', \'order_id3\', 50.0, 50.0, \'ST-1\')'
)
INSERT_MEDIA1 = (
    'INSERT INTO rescue.media '
    '(order_id, media_id, attach_id, content_type)'
    ' VALUES (\'order_id1\', \'1\', \'1\', \'some_content_type\')'
)
INSERT_MEDIA2 = (
    'INSERT INTO rescue.media '
    '(order_id, media_id, attach_id, content_type)'
    ' VALUES (\'order_id2\', \'2\', \'2\', \'some_content_type\')'
)
INSERT_MEDIA3 = (
    'INSERT INTO rescue.media '
    '(order_id, media_id, attach_id, content_type)'
    ' VALUES (\'order_id2\', \'3\', \'3\', \'some_content_type\')'
)
UPDATE_CREATION = (
    'UPDATE rescue.application SET created = NOW() - INTERVAL \'181 days\''
)


async def test_periodic_task(taxi_rescue, pgsql, taxi_config):
    cursor = pgsql['rescue'].cursor()
    cursor.execute(INSERT_APPLICATION1)  # 1 media
    cursor.execute(INSERT_APPLICATION2)  # 2 media
    cursor.execute(INSERT_APPLICATION3)  # 0 media
    cursor.execute(INSERT_MEDIA1)
    cursor.execute(INSERT_MEDIA2)
    cursor.execute(INSERT_MEDIA3)
    cursor.execute(UPDATE_CREATION)
    await taxi_rescue.run_periodic_task(
        'periodic-task-sos-application-deletion',
    )
    cursor.execute('SELECT * from rescue.application')
    result = list(row for row in cursor)
    assert not result
    cursor.execute('SELECT * from rescue.media')
    result = list(row for row in cursor)
    assert not result


async def test_periodic_task_new_media(taxi_rescue, pgsql, taxi_config):
    cursor = pgsql['rescue'].cursor()
    cursor.execute(INSERT_APPLICATION1)  # 1 media
    cursor.execute(INSERT_APPLICATION2)  # 2 media
    cursor.execute(INSERT_APPLICATION3)  # 0 media
    cursor.execute(INSERT_MEDIA1)
    cursor.execute(INSERT_MEDIA2)
    cursor.execute(INSERT_MEDIA3)
    await taxi_rescue.run_periodic_task(
        'periodic-task-sos-application-deletion',
    )
    cursor.execute('SELECT count(*) from rescue.application')
    result = list(row for row in cursor)[0][0]
    assert result == 3
    cursor.execute('SELECT count(*) from rescue.media')
    result = list(row for row in cursor)[0][0]
    assert result == 3
