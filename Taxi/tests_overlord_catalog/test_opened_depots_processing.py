import datetime

import pytest

from . import experiments
from . import models


def _check_events(processing, depot_ids, shift=0):
    events = list(processing.events(scope='grocery', queue='processing_tasks'))
    assert len(events) == shift + len(depot_ids)

    events = events[shift:]

    depot_id_to_event = {}
    for event in events:
        depot_id_to_event[event.payload['depot_id']] = event

    for depot_id in depot_ids:
        event = depot_id_to_event[str(depot_id)]

        assert event.payload['reason'] == 'opened_depot'
        assert event.payload['depot_id'] == str(depot_id)
        assert event.payload['is_create'] is True
        assert event.payload['item_id'] == 'de-%s' % str(depot_id)


def _check_no_events(processing, shift=0):
    events = list(processing.events(scope='grocery', queue='processing_tasks'))
    events = events[shift:]

    assert not events


def _insert_ts_updated(pgsql, time):
    pg_db = pgsql['overlord_catalog']
    cursor = pg_db.cursor()

    cursor.execute(
        f"""INSERT INTO catalog.distlock_periodic_updates
                  VALUES (\'opened-depots-processing\', '{time}')
                  ON CONFLICT (task_id) DO UPDATE SET updated = '{time}'""",
    )


ENABLED_OPENED_DEPOTS_PROCESSING = pytest.mark.config(
    OVERLORD_CATALOG_OPENED_DEPOTS_PROCESSING={
        'enabled': True,
        'period_seconds': 3600,
        'limit': 3,
    },
)


@ENABLED_OPENED_DEPOTS_PROCESSING
@pytest.mark.now('2021-01-01T12:00:00+0300')
@pytest.mark.suspend_periodic_tasks('opened-depots-processing-periodic')
async def test_basic(taxi_overlord_catalog, pgsql, overlord_db, processing):
    depot_id = 123456
    not_opened_depot_id = 467832
    already_processed_depot_id = 321342

    models.OpenedDepotsProcessing(
        pgsql, depot_id=str(already_processed_depot_id), processed=True,
    )

    with overlord_db as db:
        db.add_depot(depot_id=depot_id, open_ts='2020-05-25T17:43:45+00:00')
        db.add_depot(
            depot_id=already_processed_depot_id,
            open_ts='2020-04-25T17:43:45+00:00',
        )
        db.add_depot(depot_id=not_opened_depot_id)

    opened_depots_processing = models.OpenedDepotsProcessing(
        pgsql, depot_id=str(depot_id), insert_in_pg=False,
    )

    opened_depots_processing.update()
    assert opened_depots_processing.processed is None

    await taxi_overlord_catalog.run_periodic_task(
        'opened-depots-processing-periodic',
    )

    _check_events(processing, [depot_id])

    opened_depots_processing.update()
    assert opened_depots_processing.processed is True

    await taxi_overlord_catalog.run_periodic_task(
        'opened-depots-processing-periodic',
    )

    _check_no_events(processing, shift=1)

    opened_depots_processing.update()
    assert opened_depots_processing.processed is True


@ENABLED_OPENED_DEPOTS_PROCESSING
@pytest.mark.now('2021-01-01T12:00:00+0300')
@pytest.mark.suspend_periodic_tasks('opened-depots-processing-periodic')
async def test_several_opened_depots(
        taxi_overlord_catalog, pgsql, overlord_db, processing,
):
    depot_ids = [123456, 478921, 128391]

    with overlord_db as db:
        for depot_id in depot_ids:
            db.add_depot(
                depot_id=depot_id, open_ts='2020-05-25T17:43:45+00:00',
            )

    await taxi_overlord_catalog.run_periodic_task(
        'opened-depots-processing-periodic',
    )

    for depot_id in depot_ids:
        opened_depots_processing = models.OpenedDepotsProcessing(
            pgsql, depot_id=str(depot_id), insert_in_pg=False,
        )
        opened_depots_processing.update()
        assert opened_depots_processing.processed is True

    _check_events(processing, depot_ids=depot_ids)

    await taxi_overlord_catalog.run_periodic_task(
        'opened-depots-processing-periodic',
    )
    _check_no_events(processing, shift=len(depot_ids))


@ENABLED_OPENED_DEPOTS_PROCESSING
@pytest.mark.now('2021-01-01T12:00:00+0300')
@pytest.mark.suspend_periodic_tasks('opened-depots-processing-periodic')
async def test_limit_depots(
        taxi_overlord_catalog, pgsql, overlord_db, processing,
):
    depot_ids = [123456, 478921, 128391, 56271]

    with overlord_db as db:
        for depot_id in depot_ids:
            db.add_depot(
                depot_id=depot_id, open_ts='2020-05-25T17:43:45+00:00',
            )

    await taxi_overlord_catalog.run_periodic_task(
        'opened-depots-processing-periodic',
    )

    events = list(processing.events(scope='grocery', queue='processing_tasks'))
    assert len(events) == 3


@ENABLED_OPENED_DEPOTS_PROCESSING
@pytest.mark.now('2021-01-01T12:00:00+0300')
@pytest.mark.suspend_periodic_tasks('opened-depots-processing-periodic')
async def test_processing_error(
        taxi_overlord_catalog, pgsql, overlord_db, processing, mockserver,
):
    depot_id = 12345

    with overlord_db as db:
        db.add_depot(depot_id=depot_id, open_ts='2020-05-25T17:43:45+00:00')

    opened_depots_processing = models.OpenedDepotsProcessing(
        pgsql, depot_id=str(depot_id), insert_in_pg=False,
    )

    @mockserver.json_handler(
        '/processing/v1/grocery/processing_tasks/create-event',
    )
    def mock_processing(request):
        return mockserver.make_response(status=500)

    await taxi_overlord_catalog.run_periodic_task(
        'opened-depots-processing-periodic',
    )

    assert mock_processing.times_called == 3

    opened_depots_processing.update()
    assert opened_depots_processing.processed is None


@ENABLED_OPENED_DEPOTS_PROCESSING
@pytest.mark.suspend_periodic_tasks('opened-depots-processing-periodic')
async def test_time_limit_depots(
        taxi_overlord_catalog, pgsql, overlord_db, processing, mocked_time,
):
    _insert_ts_updated(pgsql, '2021-01-01T1:00:00+0000')

    mocked_time.set(
        datetime.datetime.fromisoformat('2021-01-24T06:00:00+00:00'),
    )
    await taxi_overlord_catalog.invalidate_caches()

    depot_ids = [123456, 478921]

    with overlord_db as db:
        for depot_id in depot_ids:
            db.add_depot(
                depot_id=depot_id, open_ts='2021-01-23T17:43:45+00:00',
            )

    await taxi_overlord_catalog.run_periodic_task(
        'opened-depots-processing-periodic',
    )

    events = list(processing.events(scope='grocery', queue='processing_tasks'))
    assert not events

    _insert_ts_updated(pgsql, '2021-01-01T1:00:00+0000')
    mocked_time.set(
        datetime.datetime.fromisoformat('2021-01-24T08:00:00+00:00'),
    )
    await taxi_overlord_catalog.invalidate_caches()

    await taxi_overlord_catalog.run_periodic_task(
        'opened-depots-processing-periodic',
    )

    events = list(processing.events(scope='grocery', queue='processing_tasks'))
    assert len(events) == 2


@ENABLED_OPENED_DEPOTS_PROCESSING
@experiments.overlord_catalog_opened_depots_params
@pytest.mark.suspend_periodic_tasks('opened-depots-processing-periodic')
async def test_time_limit_experiments_depots(
        taxi_overlord_catalog, pgsql, overlord_db, processing, mocked_time,
):
    _insert_ts_updated(pgsql, '2021-01-01T1:00:00+0000')
    mocked_time.set(
        datetime.datetime.fromisoformat('2021-01-24T15:00:00+00:00'),
    )
    await taxi_overlord_catalog.invalidate_caches()

    depot_ids = [123456, 478921, 654321]

    with overlord_db as db:
        for depot_id in depot_ids:
            db.add_depot(
                depot_id=depot_id, open_ts='2021-01-23T17:43:45+00:00',
            )

    await taxi_overlord_catalog.run_periodic_task(
        'opened-depots-processing-periodic',
    )

    events = list(processing.events(scope='grocery', queue='processing_tasks'))
    assert not events

    _insert_ts_updated(pgsql, '2021-01-01T1:00:00+0000')
    mocked_time.set(
        datetime.datetime.fromisoformat('2021-01-24T17:00:00+00:00'),
    )
    await taxi_overlord_catalog.invalidate_caches()

    await taxi_overlord_catalog.run_periodic_task(
        'opened-depots-processing-periodic',
    )

    events = list(processing.events(scope='grocery', queue='processing_tasks'))
    assert len(events) == 1


@ENABLED_OPENED_DEPOTS_PROCESSING
@pytest.mark.suspend_periodic_tasks('opened-depots-processing-periodic')
async def test_day_limit_depots(
        taxi_overlord_catalog, pgsql, overlord_db, processing, mocked_time,
):
    _insert_ts_updated(pgsql, '2021-01-01T1:00:00+0000')

    mocked_time.set(
        datetime.datetime.fromisoformat('2021-01-24T10:00:00+00:00'),
    )
    await taxi_overlord_catalog.invalidate_caches()

    depot_ids = [123456, 478921]

    with overlord_db as db:
        for depot_id in depot_ids:
            db.add_depot(
                depot_id=depot_id, open_ts='2021-01-24T17:43:45+00:00',
            )

    await taxi_overlord_catalog.run_periodic_task(
        'opened-depots-processing-periodic',
    )

    events = list(processing.events(scope='grocery', queue='processing_tasks'))
    assert not events

    _insert_ts_updated(pgsql, '2021-01-01T1:00:00+0000')
    mocked_time.set(
        datetime.datetime.fromisoformat('2021-01-25T10:00:00+00:00'),
    )
    await taxi_overlord_catalog.invalidate_caches()

    await taxi_overlord_catalog.run_periodic_task(
        'opened-depots-processing-periodic',
    )

    events = list(processing.events(scope='grocery', queue='processing_tasks'))
    assert len(events) == 2


@ENABLED_OPENED_DEPOTS_PROCESSING
@pytest.mark.now('2021-01-01T10:00:00+0600')
@pytest.mark.suspend_periodic_tasks('opened-depots-processing-periodic')
async def test_timezone(taxi_overlord_catalog, pgsql, overlord_db, processing):
    with overlord_db as db:
        db.add_depot(
            depot_id=123456,
            open_ts='2020-05-25T17:43:45+00:00',
            timezone='Asia/Almaty',
        )
        db.add_depot(depot_id=478921, open_ts='2020-05-25T17:43:45+00:00')

    await taxi_overlord_catalog.run_periodic_task(
        'opened-depots-processing-periodic',
    )

    events = list(processing.events(scope='grocery', queue='processing_tasks'))
    assert len(events) == 1
