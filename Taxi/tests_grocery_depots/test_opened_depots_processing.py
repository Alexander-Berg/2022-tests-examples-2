import datetime

import pytest

# from . import experiments
# from . import models


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
    pg_db = pgsql['grocery_depots']
    cursor = pg_db.cursor()

    cursor.execute(
        f"""INSERT INTO depots.distlock_periodic_updates
                  VALUES (\'opened-depots-processing\', '{time}')
                  ON CONFLICT (task_id) DO UPDATE SET updated = '{time}'""",
    )


GROCERY_DEPOTS_OPENED_DEPOTS_PARAMS = pytest.mark.experiments3(
    name='grocery_depots_opened_depots_params',
    consumers=['grocery-depots/opened-depots'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'One depot',
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'depot_id',
                    'arg_type': 'string',
                    'value': '123456',
                },
            },
            'value': {'enabled': True, 'start': 19, 'end': 21},
        },
        {
            'title': 'Another depot',
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'depot_id',
                    'arg_type': 'string',
                    'value': '654321',
                },
            },
            'value': {'enabled': False, 'start': 12, 'end': 14},
        },
    ],
    default_value={'enabled': True, 'start': 10, 'end': 15},
    is_config=True,
)


ENABLED_OPENED_DEPOTS_PROCESSING = pytest.mark.config(
    GROCERY_DEPOTS_OPENED_DEPOTS_PROCESSING={
        'enabled': True,
        'period_seconds': 3600,
        'limit': 3,
    },
)


class OpenedDepotsProcessing:
    UPSERT_SQL = """
    INSERT INTO depots_wms.opened_depots_processing (
        depot_id,
        processed
    )
    VALUES (
        %s, %s
    )
    ON CONFLICT(depot_id)
    DO UPDATE SET
        depot_id = EXCLUDED.depot_id,
        processed = EXCLUDED.processed
    ;
    """

    SELECT_SQL = """
    SELECT
        depot_id,
        processed
    FROM depots_wms.opened_depots_processing
    WHERE depot_id = %s;
    """

    def __init__(self, pgsql, depot_id, processed=None, insert_in_pg=True):
        self.pg_db = pgsql['grocery_depots']
        self.depot_id = depot_id
        self.processed = processed

        if insert_in_pg:
            self._update_db()

    def _update_db(self):
        cursor = self.pg_db.cursor()

        cursor.execute(self.UPSERT_SQL, [self.depot_id, self.processed])

    def update(self):
        cursor = self.pg_db.cursor()
        cursor.execute(self.SELECT_SQL, [self.depot_id])
        result = cursor.fetchone()

        if result:
            (self.depot_id, self.processed) = result
        else:
            self.processed = None


@ENABLED_OPENED_DEPOTS_PROCESSING
@pytest.mark.now('2021-01-01T12:00:00+0300')
@pytest.mark.suspend_periodic_tasks('opened-depots-processing-periodic')
@pytest.mark.pgsql('grocery_depots', files=['test_basic.sql'])
async def test_basic(taxi_grocery_depots, pgsql, processing):
    depot_id = 123456
    already_processed_depot_id = 321342

    OpenedDepotsProcessing(
        pgsql, depot_id=str(already_processed_depot_id), processed=True,
    )

    opened_depots_processing = OpenedDepotsProcessing(
        pgsql, depot_id=str(depot_id), insert_in_pg=False,
    )

    opened_depots_processing.update()
    assert opened_depots_processing.processed is None

    await taxi_grocery_depots.run_periodic_task(
        'opened-depots-processing-periodic',
    )

    _check_events(processing, [depot_id])

    opened_depots_processing.update()
    assert opened_depots_processing.processed is True

    await taxi_grocery_depots.run_periodic_task(
        'opened-depots-processing-periodic',
    )

    _check_no_events(processing, shift=1)

    opened_depots_processing.update()
    assert opened_depots_processing.processed is True


@pytest.mark.pgsql('grocery_depots', files=['test_several_opened_depots.sql'])
@ENABLED_OPENED_DEPOTS_PROCESSING
@pytest.mark.now('2021-01-01T12:00:00+0300')
@pytest.mark.suspend_periodic_tasks('opened-depots-processing-periodic')
async def test_several_opened_depots(taxi_grocery_depots, pgsql, processing):
    depot_ids = [123456, 478921, 128391]

    await taxi_grocery_depots.run_periodic_task(
        'opened-depots-processing-periodic',
    )

    for depot_id in depot_ids:
        opened_depots_processing = OpenedDepotsProcessing(
            pgsql, depot_id=str(depot_id), insert_in_pg=False,
        )
        opened_depots_processing.update()
        assert opened_depots_processing.processed is True

    _check_events(processing, depot_ids=depot_ids)

    await taxi_grocery_depots.run_periodic_task(
        'opened-depots-processing-periodic',
    )
    _check_no_events(processing, shift=len(depot_ids))


@pytest.mark.pgsql('grocery_depots', files=['test_limit_depots.sql'])
@ENABLED_OPENED_DEPOTS_PROCESSING
@pytest.mark.now('2021-01-01T12:00:00+0300')
@pytest.mark.suspend_periodic_tasks('opened-depots-processing-periodic')
async def test_limit_depots(taxi_grocery_depots, pgsql, processing):
    await taxi_grocery_depots.run_periodic_task(
        'opened-depots-processing-periodic',
    )

    events = list(processing.events(scope='grocery', queue='processing_tasks'))
    assert len(events) == 3


@pytest.mark.pgsql('grocery_depots', files=['test_processing_error.sql'])
@ENABLED_OPENED_DEPOTS_PROCESSING
@pytest.mark.now('2021-01-01T12:00:00+0300')
@pytest.mark.suspend_periodic_tasks('opened-depots-processing-periodic')
async def test_processing_error(taxi_grocery_depots, pgsql, mockserver):
    depot_id = 12345

    opened_depots_processing = OpenedDepotsProcessing(
        pgsql, depot_id=str(depot_id), insert_in_pg=False,
    )

    @mockserver.json_handler(
        '/processing/v1/grocery/processing_tasks/create-event',
    )
    def mock_processing(request):
        return mockserver.make_response(status=500)

    await taxi_grocery_depots.run_periodic_task(
        'opened-depots-processing-periodic',
    )

    assert mock_processing.times_called == 3

    opened_depots_processing.update()
    assert opened_depots_processing.processed is None


@pytest.mark.pgsql('grocery_depots', files=['test_time_limit_depots.sql'])
@ENABLED_OPENED_DEPOTS_PROCESSING
@pytest.mark.suspend_periodic_tasks('opened-depots-processing-periodic')
async def test_time_limit_depots(
        taxi_grocery_depots, pgsql, processing, mocked_time,
):
    _insert_ts_updated(pgsql, '2021-01-01T1:00:00+0000')

    mocked_time.set(
        datetime.datetime.fromisoformat('2021-01-24T06:00:00+00:00'),
    )
    await taxi_grocery_depots.invalidate_caches()

    await taxi_grocery_depots.run_periodic_task(
        'opened-depots-processing-periodic',
    )

    events = list(processing.events(scope='grocery', queue='processing_tasks'))
    assert not events

    _insert_ts_updated(pgsql, '2021-01-01T1:00:00+0000')
    mocked_time.set(
        datetime.datetime.fromisoformat('2021-01-24T08:00:00+00:00'),
    )
    await taxi_grocery_depots.invalidate_caches()

    await taxi_grocery_depots.run_periodic_task(
        'opened-depots-processing-periodic',
    )

    events = list(processing.events(scope='grocery', queue='processing_tasks'))
    assert len(events) == 2


@pytest.mark.pgsql(
    'grocery_depots', files=['test_time_limit_experiments_depots.sql'],
)
@ENABLED_OPENED_DEPOTS_PROCESSING
@GROCERY_DEPOTS_OPENED_DEPOTS_PARAMS
@pytest.mark.suspend_periodic_tasks('opened-depots-processing-periodic')
async def test_time_limit_experiments_depots(
        taxi_grocery_depots, pgsql, processing, mocked_time,
):
    _insert_ts_updated(pgsql, '2021-01-01T1:00:00+0000')
    mocked_time.set(
        datetime.datetime.fromisoformat('2021-01-24T15:00:00+00:00'),
    )
    await taxi_grocery_depots.invalidate_caches()

    await taxi_grocery_depots.run_periodic_task(
        'opened-depots-processing-periodic',
    )

    events = list(processing.events(scope='grocery', queue='processing_tasks'))
    assert not events

    _insert_ts_updated(pgsql, '2021-01-01T1:00:00+0000')
    mocked_time.set(
        datetime.datetime.fromisoformat('2021-01-24T17:00:00+00:00'),
    )
    await taxi_grocery_depots.invalidate_caches()

    await taxi_grocery_depots.run_periodic_task(
        'opened-depots-processing-periodic',
    )

    events = list(processing.events(scope='grocery', queue='processing_tasks'))
    assert len(events) == 1


@pytest.mark.pgsql('grocery_depots', files=['test_day_limit_depots.sql'])
@ENABLED_OPENED_DEPOTS_PROCESSING
@pytest.mark.suspend_periodic_tasks('opened-depots-processing-periodic')
async def test_day_limit_depots(
        taxi_grocery_depots, pgsql, processing, mocked_time,
):
    _insert_ts_updated(pgsql, '2021-01-01T1:00:00+0000')

    mocked_time.set(
        datetime.datetime.fromisoformat('2021-01-24T10:00:00+00:00'),
    )
    await taxi_grocery_depots.invalidate_caches()

    await taxi_grocery_depots.run_periodic_task(
        'opened-depots-processing-periodic',
    )

    events = list(processing.events(scope='grocery', queue='processing_tasks'))
    assert not events

    _insert_ts_updated(pgsql, '2021-01-01T1:00:00+0000')
    mocked_time.set(
        datetime.datetime.fromisoformat('2021-01-25T10:00:00+00:00'),
    )
    await taxi_grocery_depots.invalidate_caches()

    await taxi_grocery_depots.run_periodic_task(
        'opened-depots-processing-periodic',
    )

    events = list(processing.events(scope='grocery', queue='processing_tasks'))
    assert len(events) == 2


@pytest.mark.pgsql('grocery_depots', files=['test_timezone.sql'])
@ENABLED_OPENED_DEPOTS_PROCESSING
@pytest.mark.now('2021-01-01T10:00:00+0600')
@pytest.mark.suspend_periodic_tasks('opened-depots-processing-periodic')
async def test_timezone(taxi_grocery_depots, pgsql, processing):
    await taxi_grocery_depots.run_periodic_task(
        'opened-depots-processing-periodic',
    )

    events = list(processing.events(scope='grocery', queue='processing_tasks'))
    assert len(events) == 1
