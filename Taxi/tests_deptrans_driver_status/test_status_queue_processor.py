import pytest

JOB_NAME = 'status-queue-processor'


async def wait_iteration(taxi_deptrans_driver_status, testpoint, enabled):
    @testpoint(JOB_NAME + '-started')
    def task_started(arg):
        pass

    @testpoint(JOB_NAME + '-finished')
    def task_finished(arg):
        pass

    async with taxi_deptrans_driver_status.spawn_task(JOB_NAME):
        started = await task_started.wait_call()
        assert started['arg']['mode'] == enabled

        finished = await task_finished.wait_call()
        assert finished['arg']['mode'] == enabled


@pytest.mark.pgsql('deptrans_driver_status', files=['status_queue.sql'])
@pytest.mark.config(
    DEPTRANS_DRIVER_STATUS_QUEUE_PROCESSOR_SETTINGS={
        'enabled': False,
        'job-throttling-delay-ms': 1000,
        'statuses-batch-size': 10,
    },
)
async def test_disabled(taxi_deptrans_driver_status, testpoint, pgsql):
    await wait_iteration(taxi_deptrans_driver_status, testpoint, False)
    cursor = pgsql['deptrans_driver_status'].cursor()
    cursor.execute('SELECT * FROM deptrans.status_queue')
    assert len(list(cursor)) == 3


@pytest.mark.parametrize(
    'session_status,session_deny_reason,expected_tags',
    [
        pytest.param('NO_WAYBILL', None, {'no_waybill': {}}, id='no waybill'),
        pytest.param('SESSION_OPENED', None, None, id='session opened'),
        pytest.param('SESSION_CLOSED', None, None, id='session closed'),
        pytest.param(
            'SESSION_DENIED',
            'DRIVER_INVALID',
            {'driver_invalid': {'ttl': 10}},
            id='driver invalid',
        ),
        pytest.param(
            'SESSION_DENIED',
            'DRIVER_BLOCKED',
            {'driver_blocked': {'ttl': 10}},
            id='driver blocked',
        ),
        pytest.param(
            'SESSION_DENIED',
            'LICENSE_PLATE_INVALID',
            {'license_plate_invalid': {}},
            id='license invalid',
        ),
        pytest.param(
            'SESSION_DENIED',
            'MEDICAL_CHECKUP_NOT_PASSED',
            {'medical_checkup_not_passed': {}},
            id='medical checkup',
        ),
        pytest.param(
            'SESSION_DENIED',
            'TECHNICAL_CHECKUP_NOT_PASSED',
            {'technical_checkup_not_passed': {}},
            id='technical checkup',
        ),
        pytest.param(
            'SESSION_DENIED',
            'UNKNOWN_ERROR',
            {'unknown_error': {}},
            id='unknown error',
        ),
    ],
)
@pytest.mark.pgsql(
    'deptrans_driver_status',
    files=[
        'status_queue.sql',
        'deptrans_profiles.sql',
        'session_statuses_for_offline_profile.sql',
    ],
)
@pytest.mark.config(
    DEPTRANS_DRIVER_STATUS_QUEUE_PROCESSOR_SETTINGS={
        'enabled': True,
        'job-throttling-delay-ms': 1,
        'statuses-batch-size': 2,
    },
    DEPTRANS_DRIVER_STATUS_SESSION_TAGS={
        '__default__': [],
        'NO_WAYBILL': [{'name': 'no_waybill'}],
        'SESSION_DENIED_DRIVER_INVALID': [
            {'name': 'driver_invalid', 'ttl': 10},
        ],
        'SESSION_DENIED_DRIVER_BLOCKED': [
            {'name': 'driver_blocked', 'ttl': 10},
        ],
        'SESSION_DENIED_LICENSE_PLATE_INVALID': [
            {'name': 'license_plate_invalid'},
        ],
        'SESSION_DENIED_MEDICAL_CHECKUP_NOT_PASSED': [
            {'name': 'medical_checkup_not_passed'},
        ],
        'SESSION_DENIED_TECHNICAL_CHECKUP_NOT_PASSED': [
            {'name': 'technical_checkup_not_passed'},
        ],
        'SESSION_DENIED_UNKNOWN_ERROR': [{'name': 'unknown_error'}],
    },
)
async def test_ok(
        taxi_deptrans_driver_status,
        testpoint,
        pgsql,
        deptrans_ais_krt,
        personal,
        mockserver,
        session_status,
        session_deny_reason,
        expected_tags,
):
    @mockserver.json_handler('/tags/v1/assign')
    def _assign(request):
        if expected_tags:
            tags = request.json['entities'][0]['tags']
            assert expected_tags == tags

        return {}

    deptrans_ais_krt.set_session_status(session_status)
    deptrans_ais_krt.set_session_deny_reason(session_deny_reason)

    await wait_iteration(taxi_deptrans_driver_status, testpoint, True)
    cursor = pgsql['deptrans_driver_status'].cursor()
    cursor.execute('SELECT * FROM deptrans.status_queue')
    assert len(list(cursor)) == 1

    assert deptrans_ais_krt.driver_status.times_called == 2

    cursor.execute(
        'SELECT session_status, session_deny_reason '
        'FROM deptrans.session_statuses',
    )
    for row in cursor:
        assert row == (session_status, session_deny_reason)


@pytest.mark.config(
    DEPTRANS_DRIVER_STATUS_QUEUE_PROCESSOR_SETTINGS={
        'enabled': True,
        'job-throttling-delay-ms': 1,
        'statuses-batch-size': 5,
    },
)
@pytest.mark.parametrize(
    'sessions_count',
    [
        pytest.param(
            0,
            marks=pytest.mark.pgsql(
                'deptrans_driver_status', files=['status_queue.sql'],
            ),
            id='without deptrans id',
        ),
        pytest.param(
            3,
            marks=pytest.mark.pgsql(
                'deptrans_driver_status',
                files=[
                    'status_queue.sql',
                    'deptrans_profiles.sql',
                    'session_statuses.sql',
                ],
            ),
            id='status doesnt change',
        ),
        pytest.param(
            0,
            marks=pytest.mark.pgsql(
                'deptrans_driver_status',
                files=['status_queue_without_profiles.sql'],
            ),
            id='invalid driver profile',
        ),
    ],
)
async def test_skip_data(
        taxi_deptrans_driver_status,
        testpoint,
        pgsql,
        tags,
        deptrans_ais_krt,
        personal,
        sessions_count,
):
    await wait_iteration(taxi_deptrans_driver_status, testpoint, True)
    cursor = pgsql['deptrans_driver_status'].cursor()
    cursor.execute('SELECT * FROM deptrans.status_queue')
    assert not list(cursor)

    cursor.execute('SELECT * FROM deptrans.session_statuses')
    assert len(list(cursor)) == sessions_count

    assert deptrans_ais_krt.driver_status.times_called == 0
