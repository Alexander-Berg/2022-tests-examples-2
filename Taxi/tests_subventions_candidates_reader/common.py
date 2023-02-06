import dataclasses

PERIODIC_TASK_SCHEDULER = 'candidate-readers-scheduler.task'
PERIODIC_TASK_SUBVENTION_LOADER = 'subvention-loader.task'

# periodic tasks which should be run synchronously
PERIODIC_TASKS = [PERIODIC_TASK_SCHEDULER, PERIODIC_TASK_SUBVENTION_LOADER]


def get_published_messages_by_zones(logbroker):
    zone_msgs = dict()
    for msg in logbroker.publish['data']:
        geoarea = msg['geoarea']
        zone_msgs.setdefault(geoarea, [])
        zone_msgs[geoarea].append(msg)
    return zone_msgs


def _format_time(time):
    return time.strftime('%Y-%m-%dT%H:%M:%S.%f')


def get_postgres_cursor(pgsql):
    return pgsql['subventions-candidates-reader'].cursor()


@dataclasses.dataclass
class ReaderTask:
    geoarea: str
    processing_type: str


DEFAULT_TAGS_BASED_READER_TASKS = [
    ReaderTask('subv_zone1', 'tags_based'),
    ReaderTask('subv_zone2', 'tags_based'),
]

DEFAULT_WORKMODE_BASED_READER_TASKS = [
    ReaderTask('subv_zone1', 'workmode_based'),
    ReaderTask('subv_zone2', 'workmode_based'),
]


def init_reader_tasks(pgsql, reader_tasks):
    if reader_tasks == []:
        return

    last_taken = '1970-01-01T00:00:00.0Z'
    values = [
        '(\'{}\',\'{}\',\'{}\')'.format(
            task.geoarea, task.processing_type, last_taken,
        )
        for task in reader_tasks
    ]

    cursor = get_postgres_cursor(pgsql)
    cursor.execute('TRUNCATE TABLE subventions_candidates_reader.reader_tasks')
    cursor.execute(
        """
        INSERT INTO subventions_candidates_reader.reader_tasks(
            geoarea,processing_type,last_taken)
        VALUES {}
        """.format(
            ','.join(values),
        ),
    )


async def run_scheduler(
        taxi_subventions_candidates_reader, pgsql, reader_tasks,
):
    init_reader_tasks(pgsql, reader_tasks)
    await taxi_subventions_candidates_reader.run_periodic_task(
        PERIODIC_TASK_SCHEDULER,
    )


async def run_subvention_loader(taxi_subventions_candidates_reader):
    await taxi_subventions_candidates_reader.run_periodic_task(
        PERIODIC_TASK_SUBVENTION_LOADER,
    )
