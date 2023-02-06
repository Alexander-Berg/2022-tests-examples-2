import datetime

import pytest

from taxi.util import dates

from taxi_qc_exams.crontasks import sync_job


async def process_batch(ctx, items, **kwargs) -> sync_job.ProcessResult:
    pass


async def get_cursor(ctx, data=None, **kwargs) -> sync_job.IterateResult:
    pass


async def get_bulk(ctx, items, **kwargs) -> list:
    pass


@pytest.mark.config(QC_JOB_SETTINGS={'job': {'enabled': 'off'}})
async def test_dont_start_off(cron_context, patch):
    job = sync_job.Sync(context=cron_context, job_name='job', job_type='test')

    @patch('taxi_qc_exams.crontasks.sync_job.logger.info')
    def mock_info(*args, **kwargs):
        pass

    await job.process(process_batch, get_cursor, get_bulk, None)
    info_calls = mock_info.calls
    assert len(info_calls) == 1
    assert info_calls[0]['args'] == ('Job %s is switched off', job.job_name)


@pytest.mark.config(QC_JOB_SETTINGS={'job': {'enabled': 'dry-run'}})
async def test_dont_start_without_settings(cron_context, patch):
    job = sync_job.Sync(context=cron_context, job_name='job', job_type='test')

    @patch('taxi_qc_exams.crontasks.sync_job.logger.error')
    def mock_error(*args, **kwargs):
        pass

    await job.process(process_batch, get_cursor, get_bulk, None)
    error_calls = mock_error.calls
    assert len(error_calls) == 1
    assert error_calls[0]['args'] == (
        'cursor sync settings are not specified',
    )


@pytest.mark.config(
    QC_JOB_SETTINGS={
        'job': {
            'enabled': 'dry-run',
            'clients': {'__default__': {'batch': 100, 'sleep': 0}},
            'cursor_sync': {
                'max_operations': 1,
                'sync_period': '1s',
                'lock_for': '1s',
                'retry_for': '1s',
                'sync_lag': '1s',
            },
        },
    },
)
async def test_start_garantee(cron_context, patch):
    job = sync_job.Sync(context=cron_context, job_name='job', job_type='test')

    @patch('test_taxi_qc_exams.cron.test_cron_sync_job.get_cursor')
    async def mock_get_cursor(*args, **kwargs):
        return sync_job.IterateResult(
            items=[],
            has_more=False,
            next_value={'test': 1},
            modified=datetime.datetime.utcnow(),
        )

    @patch('test_taxi_qc_exams.cron.test_cron_sync_job.process_batch')
    async def mock_process_batch(*args, **kwargs) -> sync_job.IterateResult:
        pass

    await job.process(process_batch, get_cursor, get_bulk, None)
    cursor_calls = mock_get_cursor.calls
    assert len(cursor_calls) == 1
    assert cursor_calls[0]['kwargs'].get('cursor') is None
    assert cursor_calls[0]['kwargs'].get('modified') is None

    process_calls = mock_process_batch.calls
    assert not process_calls

    job_data = await cron_context.mongo.qc_jobs_data.find_one(job.job_filter)
    assert not job_data['operations']['items']
    assert len(job_data['cursors']['items']) == 1
    assert job_data['cursors']['items'][0]['type'] == 'garantee'


@pytest.mark.config(
    QC_JOB_SETTINGS={
        'job': {
            'enabled': 'dry-run',
            'clients': {'__default__': {'batch': 100, 'sleep': 0}},
            'cursor_sync': {
                'max_operations': 1,
                'sync_period': '1s',
                'lock_for': '1s',
                'retry_for': '1s',
                'sync_lag': '10s',
            },
        },
    },
)
@pytest.mark.now('2020-01-01T00:00:00')
async def test_start_temp(cron_context, patch):
    job = sync_job.Sync(context=cron_context, job_name='job', job_type='test')

    sync_lag = dates.parse_duration_string(
        cron_context.config.QC_JOB_SETTINGS[job.job_name]['cursor_sync'][
            'sync_lag'
        ],
    )

    await cron_context.mongo.qc_jobs_data.update_one(
        job.job_filter,
        {
            '$currentDate': {'cursors.modified_ts': {'$type': 'timestamp'}},
            '$set': {
                'cursors.items': [
                    {
                        'id': '1',
                        'type': 'garantee',
                        'setup': datetime.datetime.utcnow(),
                        'value': {
                            'modified': datetime.datetime.utcnow() - sync_lag,
                        },
                    },
                ],
            },
        },
        upsert=True,
    )

    @patch('test_taxi_qc_exams.cron.test_cron_sync_job.get_cursor')
    async def mock_get_cursor(*args, **kwargs):
        return sync_job.IterateResult(
            items=[],
            has_more=False,
            next_value={'test': 1},
            modified=datetime.datetime.utcnow(),
        )

    @patch('test_taxi_qc_exams.cron.test_cron_sync_job.process_batch')
    async def mock_process_batch(*args, **kwargs) -> sync_job.IterateResult:
        pass

    await job.process(process_batch, get_cursor, get_bulk, None)
    cursor_calls = mock_get_cursor.calls
    assert len(cursor_calls) == 1
    assert cursor_calls[0]['kwargs'].get('cursor') is None
    assert (
        cursor_calls[0]['kwargs'].get('modified')
        == datetime.datetime.utcnow() - sync_lag / 2
    )

    process_calls = mock_process_batch.calls
    assert not process_calls

    job_data = await cron_context.mongo.qc_jobs_data.find_one(job.job_filter)
    assert not job_data['operations']['items']
    assert len(job_data['cursors']['items']) == 2
    assert job_data['cursors']['items'][0]['type'] == 'garantee'
    assert job_data['cursors']['items'][1]['type'] == 'temp'


@pytest.mark.config(
    QC_JOB_SETTINGS={
        'job': {
            'enabled': 'dry-run',
            'clients': {'__default__': {'batch': 100, 'sleep': 0}},
            'cursor_sync': {
                'max_operations': 1,
                'sync_period': '1s',
                'lock_for': '1s',
                'retry_for': '1s',
                'sync_lag': '10s',
            },
        },
    },
)
@pytest.mark.now('2020-01-01T00:00:00')
async def test_start_both_cursors(cron_context, patch):
    job = sync_job.Sync(context=cron_context, job_name='job', job_type='test')

    sync_lag = dates.parse_duration_string(
        cron_context.config.QC_JOB_SETTINGS[job.job_name]['cursor_sync'][
            'sync_lag'
        ],
    )

    await cron_context.mongo.qc_jobs_data.update_one(
        job.job_filter,
        {
            '$currentDate': {'cursors.modified_ts': {'$type': 'timestamp'}},
            '$set': {
                'cursors.items': [
                    {
                        'id': '1',
                        'type': 'garantee',
                        'value': {
                            'modified': datetime.datetime.utcnow() - sync_lag,
                        },
                    },
                ],
            },
        },
        upsert=True,
    )

    @patch('test_taxi_qc_exams.cron.test_cron_sync_job.get_cursor')
    async def mock_get_cursor(*args, **kwargs):
        return sync_job.IterateResult(
            items=[],
            has_more=False,
            next_value={'test': 1},
            modified=datetime.datetime.utcnow(),
        )

    @patch('test_taxi_qc_exams.cron.test_cron_sync_job.process_batch')
    async def mock_process_batch(*args, **kwargs) -> sync_job.IterateResult:
        pass

    await job.process(process_batch, get_cursor, get_bulk, None)
    cursor_calls = mock_get_cursor.calls
    assert len(cursor_calls) == 2
    assert (
        cursor_calls[0]['kwargs'].get('modified')
        == datetime.datetime.utcnow() - sync_lag / 2
    )
    assert (
        cursor_calls[1]['kwargs'].get('modified')
        == datetime.datetime.utcnow() - sync_lag
    )

    process_calls = mock_process_batch.calls
    assert not process_calls

    # после синка гарантированного курсора, временный удалился
    job_data = await cron_context.mongo.qc_jobs_data.find_one(job.job_filter)
    assert not job_data['operations']['items']
    assert len(job_data['cursors']['items']) == 1
    assert job_data['cursors']['items'][0]['type'] == 'garantee'
