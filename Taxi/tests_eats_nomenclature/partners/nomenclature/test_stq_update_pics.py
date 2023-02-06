import pytest


QUEUE_NAME = 'eats_nomenclature_update_pics'
REQUEST_PICS_DATA = [
    {'source_url': 'url_1', 'status': 'updated', 'ava_url': 'processed_url_1'},
    {'source_url': 'url_2', 'status': 'error', 'error_text': 'some error 2'},
    {'source_url': 'url_3', 'status': 'error', 'error_text': 'some error 3'},
    {'source_url': 'url_4', 'status': 'updated', 'ava_url': 'processed_url_4'},
    {'source_url': 'url_5', 'status': 'updated', 'ava_url': 'processed_url_5'},
    {'source_url': 'url_6', 'status': 'updated', 'ava_url': 'processed_url_6'},
]


def processing_settings(
        max_retries_on_error=3,
        max_retries_on_busy=3,
        max_busy_time_in_ms=100000,
        retry_on_busy_delay_ms=1000,
):
    return {
        '__default__': {
            'max_retries_on_error': max_retries_on_error,
            'max_retries_on_busy': max_retries_on_busy,
            'max_busy_time_in_ms': max_busy_time_in_ms,
            'retry_on_busy_delay_ms': retry_on_busy_delay_ms,
            'insert_batch_size': 1000,
            'lookup_batch_size': 1000,
        },
    }


@pytest.mark.pgsql('eats_nomenclature', files=['fill_pictures.sql'])
async def test_pics_merge(pgsql, pics_enqueue):
    # check current data
    assert sql_get_pictures(pgsql) == {
        ('url_1', None, None),
        ('url_2', None, None),
        ('url_3', 'processed_url_3', None),
        ('url_4', None, 'some old error 4'),
        ('url_5', 'old_processed_url_5', None),
    }

    # upload new pics
    await pics_enqueue(REQUEST_PICS_DATA)

    # check merged data
    assert sql_get_pictures(pgsql) == {
        ('url_1', 'processed_url_1', None),
        ('url_2', None, 'some error 2'),
        # in case of error old processed url is not reset
        ('url_3', 'processed_url_3', 'some error 3'),
        ('url_4', 'processed_url_4', None),
        ('url_5', 'processed_url_5', None),
    }


@pytest.mark.config(
    EATS_NOMENCLATURE_PROCESSING=processing_settings(max_retries_on_error=2),
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_pictures.sql'])
async def test_stq_error_limit(task_enqueue_v2, taxi_config, testpoint):
    @testpoint('eats-nomenclature-update-pics::fail-while-processing')
    def task_testpoint(param):
        return {'inject_failure': True}

    max_retries_on_error = taxi_config.get('EATS_NOMENCLATURE_PROCESSING')[
        '__default__'
    ]['max_retries_on_error']
    task_id = '1'
    kwargs = {'items': []}

    for i in range(max_retries_on_error):
        await task_enqueue_v2(
            QUEUE_NAME,
            task_id=task_id,
            kwargs=kwargs,
            expect_fail=True,
            exec_tries=i,
        )

    # should succeed because of the error limit
    await task_enqueue_v2(
        QUEUE_NAME,
        task_id=task_id,
        kwargs=kwargs,
        expect_fail=False,
        exec_tries=max_retries_on_error,
    )

    assert task_testpoint.has_calls


def sql_get_pictures(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """
        select url, processed_url, processing_error
        from eats_nomenclature.pictures
        """,
    )
    return set(cursor)


def metrics_config(name, max_dead_tuples_):
    return {
        'EATS_NOMENCLATURE_METRICS': {
            '__default__': {
                'assortment_outdated_threshold_in_hours': 2,
                'max_dead_tuples': 1000000,
            },
            name: {
                'assortment_outdated_threshold_in_hours': 2,
                'max_dead_tuples': max_dead_tuples_,
            },
        },
    }


@pytest.fixture(name='pics_enqueue')
def _pics_enqueue(stq_runner):
    async def do_pics_enqueue(pictures, task_id='1', expect_fail=False):
        await stq_runner.eats_nomenclature_update_pics.call(
            task_id=task_id,
            args=[],
            kwargs={'items': pictures},
            expect_fail=expect_fail,
        )

    return do_pics_enqueue
