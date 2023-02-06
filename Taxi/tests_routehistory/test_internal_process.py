import asyncio

THIS_HOST = 'mock_hostname_override'


def _sample_data(**kwargs):
    data = {'from': 0, 'to': 10}
    data.update(**kwargs)
    return data


def _sample_process(data=None, **kwargs):
    if data is None:
        data = _sample_data()
    process = {
        'id': 'sample_process',
        'host': 'some_host',
        'version': 0,
        'period_ms': 100000,
        'period_exc_ms': 0,
        'max_attempts': 3,
        'state': 'created',
        'type': 'test',
        'data': data,
    }
    process.update(**kwargs)
    return process


async def test_process_sample(taxi_routehistory, routehistory_internal):
    # Add new process to db
    await routehistory_internal.call(
        'DbAddProcess', _sample_process(host=THIS_HOST, state='running'),
    )
    # Sync with db
    await taxi_routehistory.run_periodic_task('process_sync_state')
    # Make sure the DB is not changed yet
    result = await routehistory_internal.call('DbGetProcesses', None)
    assert result == [_sample_process(host=THIS_HOST, state='running')]
    # Do an iteration
    await taxi_routehistory.run_periodic_task('process_sample_process')
    # Make sure the DB is still unchanged
    result = await routehistory_internal.call('DbGetProcesses', None)
    assert result == [_sample_process(host=THIS_HOST, state='running')]
    # Do another iteration
    await taxi_routehistory.run_periodic_task('process_sample_process')
    # Sync with db
    await taxi_routehistory.run_periodic_task('process_sync_state')
    # Verify db state
    result = await routehistory_internal.call('DbGetProcesses', None)
    assert result == [
        _sample_process(
            host=THIS_HOST,
            state='running',
            version=1,
            data=_sample_data(counter=2),
        ),
    ]
    # Update db
    result = await routehistory_internal.call(
        'DbUpdateProcesses',
        [
            _sample_process(
                host=THIS_HOST,
                state='running',
                version=1,
                data=_sample_data(counter=9),
            ),
        ],
    )
    assert result == ['sample_process']
    # Sync with db
    await taxi_routehistory.run_periodic_task('process_sync_state')
    # Do another iteration
    await taxi_routehistory.run_periodic_task('process_sample_process')
    # Sync with db
    await taxi_routehistory.run_periodic_task('process_sync_state')
    # Verify db state
    result = await routehistory_internal.call('DbGetProcesses', None)
    assert result == [
        _sample_process(
            host=THIS_HOST,
            state='done',
            version=3,
            data=_sample_data(counter=10),
        ),
    ]


async def test_process_phone_history(
        taxi_routehistory, routehistory_internal, load_json,
):
    await routehistory_internal.call(
        'WritePhoneHistory', load_json('records_for_migration.json'),
    )
    await routehistory_internal.call(
        'DbAddProcess',
        {
            'id': 'reader',
            'host': THIS_HOST,
            'version': 0,
            'period_ms': 1,
            'period_exc_ms': 0,
            'max_attempts': 3,
            'state': 'running',
            'type': 'phone_history_reader',
            'data': {
                'iterator': {
                    'shard_number': 5,
                    'is_portal_uid': True,
                    'last_created': '2025-01-01T10:00:00+0000',
                },
                'limit': 2,
                'pg_options': {
                    'execute_ms': 1000,
                    'statement_ms': 1000,
                    'host_type_probabilities': [0, 0, 1],
                },
                'buffer': 'buffer_name',
                'max_buffer_size': 3,
                'shard_keys': [[0, 100]],
            },
        },
    )
    await routehistory_internal.call(
        'DbAddProcess',
        {
            'id': 'writer',
            'host': THIS_HOST,
            'version': 0,
            'period_ms': 1,
            'period_exc_ms': 0,
            'max_attempts': 3,
            'state': 'running',
            'type': 'phone_history_writer',
            'data': {
                'shard': 5,
                'min_records_hint': 10,
                'limit': 1,
                'db_timeout_ms': 1000,
                'buffer': 'buffer_name',
                'written': 0,
                'reader_processes': ['reader'],
                'mode': 'noop',
            },
        },
    )
    await taxi_routehistory.run_periodic_task('process_sync_state')
    await asyncio.sleep(0.5)
    await taxi_routehistory.run_periodic_task('process_sync_state')
    await asyncio.sleep(0.5)
    await taxi_routehistory.run_periodic_task('process_sync_state')
    result = await routehistory_internal.call('DbGetProcesses', None)
    assert result == [
        {
            'id': 'reader',
            'data': {
                'buffer': 'buffer_name',
                'pg_options': {
                    'execute_ms': 1000,
                    'statement_ms': 1000,
                    'host_type_probabilities': [0, 0, 1],
                },
                'iterator': {
                    'approx_total': 0,
                    'done': True,
                    'is_portal_uid': False,
                    'original_last_created': '2025-01-01T10:00:00+00:00',
                    'last_created': '2021-03-01T00:00:00+00:00',
                    'last_order_id': '7b58f6cd7d05453ed45572b09216c35c',
                    'processed': 2,
                    'shard_number': 5,
                    'skipped': 0,
                },
                'limit': 2,
                'max_buffer_size': 3,
                'shard_keys': [[0, 100]],
            },
            'host': THIS_HOST,
            'max_attempts': 3,
            'period_exc_ms': 0,
            'period_ms': 1,
            'state': 'done',
            'type': 'phone_history_reader',
            'version': 1,
        },
        {
            'id': 'writer',
            'data': {
                'buffer': 'buffer_name',
                'db_timeout_ms': 1000,
                'limit': 1,
                'min_records_hint': 10,
                'mode': 'noop',
                'reader_processes': ['reader'],
                'shard': 5,
                'written': 2,
            },
            'host': THIS_HOST,
            'max_attempts': 3,
            'period_exc_ms': 0,
            'period_ms': 1,
            'state': 'done',
            'type': 'phone_history_writer',
            'version': 2,
        },
    ]


async def test_process_db(routehistory_internal):
    # Create two processes
    await routehistory_internal.call('DbAddProcess', _sample_process())
    await routehistory_internal.call(
        'DbAddProcess', _sample_process(id='sample_process2'),
    )
    # Get the first one
    result = await routehistory_internal.call(
        'DbGetProcesses', ['sample_process'],
    )
    assert result == [_sample_process()]
    # Now get both
    result = await routehistory_internal.call('DbGetProcesses', None)
    assert result == [_sample_process(), _sample_process(id='sample_process2')]
    # Get non-existent
    result = await routehistory_internal.call(
        'DbGetProcesses', ['non_existent'],
    )
    assert result == []
    # Attempt to add an existing process
    await routehistory_internal.call_exc('DbAddProcess', _sample_process())
    # Update the second process
    result = await routehistory_internal.call(
        'DbUpdateProcesses',
        [_sample_process(id='sample_process2', state='paused')],
    )
    assert result == ['sample_process2']
    # Try to update with old version
    result = await routehistory_internal.call(
        'DbUpdateProcesses',
        [_sample_process(id='sample_process2', state='running')],
    )
    assert result == []
    # Try to update with the correct version
    result = await routehistory_internal.call(
        'DbUpdateProcesses',
        [_sample_process(id='sample_process2', state='running', version=1)],
    )
    assert result == ['sample_process2']
    # Try to pause with a dedicated api
    await routehistory_internal.call('DbPauseProcess', 'sample_process2')
    # Try to pause when already paused
    await routehistory_internal.call_exc('DbPauseProcess', 'sample_process2')
    # Ensure version after our pause calls
    result = await routehistory_internal.call(
        'DbGetProcesses', ['sample_process2'],
    )
    assert result[0]['version'] == 3
    # Delete the first process
    await routehistory_internal.call('DbDeleteProcess', 'sample_process')
    # Get all processes, ensure that only the second one is still there
    result = await routehistory_internal.call('DbGetProcesses', None)
    assert len(result) == 1
    assert result[0]['id'] == 'sample_process2'
    # Attempt to delete already-deleted process
    await routehistory_internal.call_exc('DbDeleteProcess', 'sample_process')
