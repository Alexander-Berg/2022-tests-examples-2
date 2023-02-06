# pylint: disable=import-error
import datetime

import pytest


@pytest.mark.pgsql('trackstory-pgsql-db')
@pytest.mark.config(TRACKSTORY_ARCHIVE_TASK_ENABLED=False)
@pytest.mark.now('2019-09-11T13:42:15+0300')
async def test_archive_create_tasks_disabled(
        taxi_driver_trackstory_adv, pgsql,
):
    response = await taxi_driver_trackstory_adv.post(
        '/tests/archive/action', json={'action': 'create_tasks'},
    )

    assert response.status_code == 200

    db = pgsql['trackstory-pgsql-db']
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT hour
            FROM driver_trackstory.current_archive_process_hour
            WHERE id = 1;""",
    )
    data = cursor.fetchall()
    assert data == []


@pytest.mark.pgsql('trackstory-pgsql-db')
@pytest.mark.config(TRACKSTORY_ARCHIVE_TASK_ENABLED=True)
@pytest.mark.now('2019-09-11T13:42:15+0300')
async def test_archive_create_tasks_empty(taxi_driver_trackstory_adv, pgsql):
    response = await taxi_driver_trackstory_adv.post(
        '/tests/archive/action', json={'action': 'create_tasks'},
    )

    assert response.status_code == 200

    db = pgsql['trackstory-pgsql-db']
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT hour
            FROM driver_trackstory.current_archive_process_hour
            WHERE id = 1;""",
    )
    hour = cursor.fetchall()[0][0]
    assert hour == 435609

    # tasks created new one tasks with previous hour,
    # because there is no processing hour.
    cursor.execute(
        f"""SELECT partition_num, logbroker_offsets, time_created, is_finished
            FROM driver_trackstory.archive_process_tasks
            ORDER BY partition_num;""",
    )
    tasks = cursor.fetchall()
    assert len(tasks) == 10
    for i in range(0, 10):
        assert tasks[i][0] == i + 1
        assert tasks[i][1] == []
        # this is now in database, so don't check it
        assert isinstance(tasks[i][2], datetime.datetime)
        assert tasks[i][3] is None


@pytest.mark.pgsql('trackstory-pgsql-db', files=['created_tasks.sql'])
@pytest.mark.config(TRACKSTORY_ARCHIVE_TASK_ENABLED=True)
@pytest.mark.now('2019-09-11T13:42:15+0300')
async def test_archive_create_new_tasks_no_processing_hour(
        taxi_driver_trackstory_adv, pgsql,
):
    response = await taxi_driver_trackstory_adv.post(
        '/tests/archive/action', json={'action': 'create_tasks'},
    )

    assert response.status_code == 200

    db = pgsql['trackstory-pgsql-db']
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT hour
                FROM driver_trackstory.current_archive_process_hour
                WHERE id = 1;""",
    )
    hour = cursor.fetchall()[0][0]
    assert hour == 435609

    # tasks created new one tasks with previous hour,
    # because there is no processing hour.
    cursor.execute(
        f"""SELECT partition_num, logbroker_offsets, time_created, is_finished
            FROM driver_trackstory.archive_process_tasks
            ORDER BY partition_num;""",
    )
    tasks = cursor.fetchall()
    assert len(tasks) == 10
    for i in range(0, 10):
        assert tasks[i][0] == i + 1
        assert tasks[i][1] == []
        # this is now in database, so don't check it
        assert isinstance(tasks[i][2], datetime.datetime)
        assert tasks[i][3] is None


@pytest.mark.pgsql(
    'trackstory-pgsql-db', files=['created_tasks_with_hour.sql'],
)
@pytest.mark.config(TRACKSTORY_ARCHIVE_TASK_ENABLED=True)
@pytest.mark.now('2019-09-11T13:42:15+0300')
async def test_archive_not_create_tasks_processing_hour_exists(
        taxi_driver_trackstory_adv, pgsql,
):
    response = await taxi_driver_trackstory_adv.post(
        '/tests/archive/action', json={'action': 'create_tasks'},
    )

    assert response.status_code == 200

    db = pgsql['trackstory-pgsql-db']
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT hour
                FROM driver_trackstory.current_archive_process_hour
                WHERE id = 1;""",
    )
    hour = cursor.fetchall()[0][0]
    assert hour == 444

    # doesn't create tasks, they already exists.
    cursor.execute(
        f"""SELECT partition_num, logbroker_offsets, time_created, is_finished
            FROM driver_trackstory.archive_process_tasks
            ORDER BY partition_num;""",
    )
    tasks = cursor.fetchall()
    assert len(tasks) == 6
    for i in range(0, 6):
        assert tasks[i][0] == i + 1
        assert tasks[i][1] is None
        # this is now in database, so don't check it
        assert isinstance(tasks[i][2], datetime.datetime)
        assert tasks[i][3] is None


@pytest.mark.pgsql(
    'trackstory-pgsql-db',
    files=['created_tasks_with_not_all_processed_tasks.sql'],
)
@pytest.mark.config(TRACKSTORY_ARCHIVE_TASK_ENABLED=True)
@pytest.mark.now('2019-09-11T13:42:15+0300')
async def test_archive_not_create_tasks_processing_not_all_tasks_finished(
        taxi_driver_trackstory_adv, pgsql,
):
    response = await taxi_driver_trackstory_adv.post(
        '/tests/archive/action', json={'action': 'create_tasks'},
    )

    assert response.status_code == 200

    db = pgsql['trackstory-pgsql-db']
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT hour
                FROM driver_trackstory.current_archive_process_hour
                WHERE id = 1;""",
    )
    hour = cursor.fetchall()[0][0]
    assert hour == 444


@pytest.mark.pgsql('trackstory-pgsql-db', files=['all_tasks_finished.sql'])
@pytest.mark.config(TRACKSTORY_ARCHIVE_TASK_ENABLED=True)
@pytest.mark.now('2019-09-11T13:42:15+0300')
async def test_archive_create_tasks_all_tasks_finished(
        taxi_driver_trackstory_adv, pgsql,
):
    response = await taxi_driver_trackstory_adv.post(
        '/tests/archive/action', json={'action': 'create_tasks'},
    )

    assert response.status_code == 200

    # all tasks finished, updated next process hour and created tasks for it.
    db = pgsql['trackstory-pgsql-db']
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT hour
                FROM driver_trackstory.current_archive_process_hour
                WHERE id = 1;""",
    )
    hour = cursor.fetchall()[0][0]
    assert hour == 445

    cursor.execute(
        f"""SELECT partition_num, logbroker_offsets, time_created, is_finished
            FROM driver_trackstory.archive_process_tasks
            ORDER BY partition_num;""",
    )
    tasks = cursor.fetchall()
    assert len(tasks) == 10
    for i in range(0, 6):
        assert tasks[i][0] == i + 1
        assert tasks[i][1] == [
            {'offset': 123, 'topic_partition': 'rt-positions-sas'},
        ]
        # this is now in database, so don't check it
        assert isinstance(tasks[i][2], datetime.datetime)
        assert tasks[i][3] is None

    for i in range(6, 4):
        assert tasks[i][0] == i + 1
        assert tasks[i][1] == []
        # this is now in database, so don't check it
        assert isinstance(tasks[i][2], datetime.datetime)
        assert tasks[i][3] is None


@pytest.mark.pgsql(
    'trackstory-pgsql-db', files=['all_tasks_finished_next_now.sql'],
)
@pytest.mark.config(TRACKSTORY_ARCHIVE_TASK_ENABLED=True)
@pytest.mark.now('2019-09-11T13:42:15+0300')
async def test_archive_create_tasks_all_tasks_finished_next_hour_current(
        taxi_driver_trackstory_adv, pgsql,
):
    response = await taxi_driver_trackstory_adv.post(
        '/tests/archive/action', json={'action': 'create_tasks'},
    )

    assert response.status_code == 200

    # all tasks finished, but next hour is current,
    # so nothing to do, just wait.
    db = pgsql['trackstory-pgsql-db']
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT hour
                FROM driver_trackstory.current_archive_process_hour
                WHERE id = 1;""",
    )
    hour = cursor.fetchall()[0][0]
    assert hour == 435609

    cursor.execute(
        f"""SELECT partition_num, logbroker_offsets, time_created, is_finished
            FROM driver_trackstory.archive_process_tasks
            ORDER BY partition_num;""",
    )
    tasks = cursor.fetchall()
    assert len(tasks) == 6
    for i in range(0, 6):
        assert tasks[i][3] is None
        assert tasks[i][0] == i + 1
        assert tasks[i][1] is None
        # this is now in database, so don't check it
        assert isinstance(tasks[i][2], datetime.datetime)
