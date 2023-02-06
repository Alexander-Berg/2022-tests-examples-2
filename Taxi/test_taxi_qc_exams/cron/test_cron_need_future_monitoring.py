# pylint: disable=redefined-outer-name
import typing

import pytest

from taxi.clients import juggler

from taxi_qc_exams.generated.cron import run_cron


@pytest.mark.filldb(qc_settings='no_exams')
@pytest.mark.config(
    QC_EXAMS_NEED_FUTURE_MONITORING={'dkk': dict(enabled=False)},
)
async def test_qc_settings_missing_exams(
        simple_secdist, monkeypatch, patch, patch_aiohttp_session,
):
    events: typing.List[dict] = []

    @patch('socket.gethostname')
    def gethostname():  # pylint: disable=unused-variable
        return 'test'

    @patch_aiohttp_session(juggler.JUGGLER_URL)
    def juggler_request(method, url, **kwargs):
        nonlocal events
        events = kwargs.get('json', {}).get('events', [])

    await run_cron.main(
        ['taxi_qc_exams.crontasks.need_future_monitoring', '-t', '0'],
    )

    calls = juggler_request.calls
    assert len(calls) == 1

    events = sorted(events, key=lambda k: k['service'])
    assert events == [
        dict(
            host='test',
            service='QcNeedFutureCheck',
            status='CRIT',
            description='QcSettings error: exams missing',
        ),
    ]


@pytest.mark.filldb(qc_settings='no_code')
@pytest.mark.config(
    QC_EXAMS_NEED_FUTURE_MONITORING={'dkk': dict(enabled=False)},
)
async def test_qc_settings_missing_code(
        simple_secdist, monkeypatch, patch, patch_aiohttp_session,
):
    events: typing.List[dict] = []

    @patch('socket.gethostname')
    def gethostname():  # pylint: disable=unused-variable
        return 'test'

    @patch_aiohttp_session(juggler.JUGGLER_URL)
    def juggler_request(method, url, **kwargs):
        nonlocal events
        events = kwargs.get('json', {}).get('events', [])

    await run_cron.main(
        ['taxi_qc_exams.crontasks.need_future_monitoring', '-t', '0'],
    )

    calls = juggler_request.calls
    assert len(calls) == 1

    events = sorted(events, key=lambda k: k['service'])
    assert events == [
        dict(
            host='test',
            service='QcNeedFutureCheck',
            status='CRIT',
            description='QcSettings error: code missing',
        ),
    ]


@pytest.mark.config(QC_EXAMS_NEED_FUTURE_MONITORING={})
async def test_config_exam_missing(
        simple_secdist, monkeypatch, patch, patch_aiohttp_session,
):
    events: typing.List[dict] = []

    @patch('socket.gethostname')
    def gethostname():  # pylint: disable=unused-variable
        return 'test'

    @patch_aiohttp_session(juggler.JUGGLER_URL)
    def juggler_request(method, url, **kwargs):
        nonlocal events
        events = kwargs.get('json', {}).get('events', [])

    await run_cron.main(
        ['taxi_qc_exams.crontasks.need_future_monitoring', '-t', '0'],
    )

    calls = juggler_request.calls
    assert len(calls) == 1

    events = sorted(events, key=lambda k: k['service'])
    assert events == [
        dict(
            host='test',
            service='QcNeedFutureCheck',
            status='CRIT',
            description='Monitoring config not specified: dkk',
        ),
    ]


@pytest.mark.config(
    QC_EXAMS_NEED_FUTURE_MONITORING={'dkk': dict(count_limit={})},
)
async def test_wrong_exam_config(
        simple_secdist, monkeypatch, patch, patch_aiohttp_session,
):
    events: typing.List[dict] = []

    @patch('socket.gethostname')
    def gethostname():  # pylint: disable=unused-variable
        return 'test'

    @patch_aiohttp_session(juggler.JUGGLER_URL)
    def juggler_request(method, url, **kwargs):
        nonlocal events
        events = kwargs.get('json', {}).get('events', [])

    await run_cron.main(
        ['taxi_qc_exams.crontasks.need_future_monitoring', '-t', '0'],
    )

    calls = juggler_request.calls
    assert len(calls) == 1

    events = sorted(events, key=lambda k: k['service'])
    assert events == [
        dict(
            host='test',
            service='QcDKKNeedFutureCheck',
            status='CRIT',
            description='Checking finish with exception',
        ),
        dict(
            host='test',
            service='QcNeedFutureCheck',
            status='OK',
            description='No qc_settings errors',
        ),
    ]


@pytest.mark.config(
    QC_EXAMS_NEED_FUTURE_MONITORING={'dkk': dict(enabled=False)},
)
async def test_exam_monitoring_disabled(
        simple_secdist, monkeypatch, patch, patch_aiohttp_session,
):
    events: typing.List[dict] = []

    @patch('socket.gethostname')
    def gethostname():  # pylint: disable=unused-variable
        return 'test'

    @patch_aiohttp_session(juggler.JUGGLER_URL)
    def juggler_request(method, url, **kwargs):
        nonlocal events
        events = kwargs.get('json', {}).get('events', [])

    await run_cron.main(
        ['taxi_qc_exams.crontasks.need_future_monitoring', '-t', '0'],
    )

    calls = juggler_request.calls
    assert len(calls) == 1

    events = sorted(events, key=lambda k: k['service'])
    assert events == [
        dict(
            host='test',
            service='QcDKKNeedFutureCheck',
            status='OK',
            description='Checking disabled',
        ),
        dict(
            host='test',
            service='QcNeedFutureCheck',
            status='OK',
            description='No qc_settings errors',
        ),
    ]


@pytest.mark.config(
    QC_EXAMS_NEED_FUTURE_MONITORING={'dkk': dict(enabled=True)},
)
async def test_missing_count_config(
        simple_secdist, monkeypatch, patch, patch_aiohttp_session,
):
    events: typing.List[dict] = []

    @patch('socket.gethostname')
    def gethostname():  # pylint: disable=unused-variable
        return 'test'

    @patch_aiohttp_session(juggler.JUGGLER_URL)
    def juggler_request(method, url, **kwargs):
        nonlocal events
        events = kwargs.get('json', {}).get('events', [])

    await run_cron.main(
        ['taxi_qc_exams.crontasks.need_future_monitoring', '-t', '0'],
    )

    calls = juggler_request.calls
    assert len(calls) == 1

    events = sorted(events, key=lambda k: k['service'])
    assert events == [
        dict(
            host='test',
            service='QcDKKNeedFutureCheck',
            status='CRIT',
            description='Nothing was checked',
        ),
        dict(
            host='test',
            service='QcNeedFutureCheck',
            status='OK',
            description='No qc_settings errors',
        ),
    ]


@pytest.mark.config(
    QC_EXAMS_NEED_FUTURE_MONITORING={
        'dkk': dict(enabled=True, count_limit=dict()),
    },
)
async def test_count_missing_levels(
        simple_secdist, monkeypatch, patch, patch_aiohttp_session,
):
    events: typing.List[dict] = []

    @patch('socket.gethostname')
    def gethostname():  # pylint: disable=unused-variable
        return 'test'

    @patch_aiohttp_session(juggler.JUGGLER_URL)
    def juggler_request(method, url, **kwargs):
        nonlocal events
        events = kwargs.get('json', {}).get('events', [])

    await run_cron.main(
        ['taxi_qc_exams.crontasks.need_future_monitoring', '-t', '0'],
    )

    calls = juggler_request.calls
    assert len(calls) == 1

    events = sorted(events, key=lambda k: k['service'])
    assert events == [
        dict(
            host='test',
            service='QcDKKNeedFutureCheck',
            status='OK',
            description='Checking successful',
        ),
        dict(
            host='test',
            service='QcDKKNeedFutureCountCheck',
            status='CRIT',
            description='Missing monitor threshold levels',
        ),
        dict(
            host='test',
            service='QcNeedFutureCheck',
            status='OK',
            description='No qc_settings errors',
        ),
    ]


@pytest.mark.config(
    QC_EXAMS_NEED_FUTURE_MONITORING={
        'dkk': {'enabled': True, 'count_limit': {'warning': 7, 'critical': 5}},
    },
)
async def test_count_wrong_levels(
        simple_secdist, monkeypatch, patch, patch_aiohttp_session,
):
    events: typing.List[dict] = []

    @patch('socket.gethostname')
    def gethostname():  # pylint: disable=unused-variable
        return 'test'

    @patch_aiohttp_session(juggler.JUGGLER_URL)
    def juggler_request(method, url, **kwargs):
        nonlocal events
        events = kwargs.get('json', {}).get('events', [])

    await run_cron.main(
        ['taxi_qc_exams.crontasks.need_future_monitoring', '-t', '0'],
    )

    calls = juggler_request.calls
    assert len(calls) == 1

    events = sorted(events, key=lambda k: k['service'])
    assert events == [
        dict(
            host='test',
            service='QcDKKNeedFutureCheck',
            status='OK',
            description='Checking successful',
        ),
        dict(
            host='test',
            service='QcDKKNeedFutureCountCheck',
            status='CRIT',
            description='Warning level is more than critical level',
        ),
        dict(
            host='test',
            service='QcNeedFutureCheck',
            status='OK',
            description='No qc_settings errors',
        ),
    ]


@pytest.mark.config(
    QC_EXAMS_NEED_FUTURE_MONITORING={
        'dkk': {'enabled': True, 'count_limit': {'critical': 5}},
    },
)
async def test_count_monitoring_crit(
        simple_secdist, monkeypatch, patch, patch_aiohttp_session,
):
    events: typing.List[dict] = []

    @patch('socket.gethostname')
    def gethostname():  # pylint: disable=unused-variable
        return 'test'

    @patch_aiohttp_session(juggler.JUGGLER_URL)
    def juggler_request(method, url, **kwargs):
        nonlocal events
        events = kwargs.get('json', {}).get('events', [])

    await run_cron.main(
        ['taxi_qc_exams.crontasks.need_future_monitoring', '-t', '0'],
    )

    calls = juggler_request.calls
    assert len(calls) == 1

    events = sorted(events, key=lambda k: k['service'])
    assert events == [
        dict(
            host='test',
            service='QcDKKNeedFutureCheck',
            status='OK',
            description='Checking successful',
        ),
        dict(
            host='test',
            service='QcDKKNeedFutureCountCheck',
            status='CRIT',
            description='More than 5 entities waiting for updates',
        ),
        dict(
            host='test',
            service='QcNeedFutureCheck',
            status='OK',
            description='No qc_settings errors',
        ),
    ]


@pytest.mark.config(
    QC_EXAMS_NEED_FUTURE_MONITORING={
        'dkk': {'enabled': True, 'count_limit': {'warning': 3, 'critical': 6}},
    },
)
async def test_count_monitoring_warn(
        simple_secdist, monkeypatch, patch, patch_aiohttp_session,
):
    events: typing.List[dict] = []

    @patch('socket.gethostname')
    def gethostname():  # pylint: disable=unused-variable
        return 'test'

    @patch_aiohttp_session(juggler.JUGGLER_URL)
    def juggler_request(method, url, **kwargs):
        nonlocal events
        events = kwargs.get('json', {}).get('events', [])

    await run_cron.main(
        ['taxi_qc_exams.crontasks.need_future_monitoring', '-t', '0'],
    )

    calls = juggler_request.calls
    assert len(calls) == 1

    events = sorted(events, key=lambda k: k['service'])
    assert events == [
        dict(
            host='test',
            service='QcDKKNeedFutureCheck',
            status='OK',
            description='Checking successful',
        ),
        dict(
            host='test',
            service='QcDKKNeedFutureCountCheck',
            status='WARN',
            description='More than 3 entities waiting for updates',
        ),
        dict(
            host='test',
            service='QcNeedFutureCheck',
            status='OK',
            description='No qc_settings errors',
        ),
    ]


@pytest.mark.config(
    QC_EXAMS_NEED_FUTURE_MONITORING={
        'dkk': {'enabled': True, 'count_limit': {'warning': 6}},
    },
)
async def test_count_monitoring_ok(
        simple_secdist, monkeypatch, patch, patch_aiohttp_session,
):
    events: typing.List[dict] = []

    @patch('socket.gethostname')
    def gethostname():  # pylint: disable=unused-variable
        return 'test'

    @patch_aiohttp_session(juggler.JUGGLER_URL)
    def juggler_request(method, url, **kwargs):
        nonlocal events
        events = kwargs.get('json', {}).get('events', [])

    await run_cron.main(
        ['taxi_qc_exams.crontasks.need_future_monitoring', '-t', '0'],
    )

    calls = juggler_request.calls
    assert len(calls) == 1

    events = sorted(events, key=lambda k: k['service'])
    assert events == [
        dict(
            host='test',
            service='QcDKKNeedFutureCheck',
            status='OK',
            description='Checking successful',
        ),
        dict(
            host='test',
            service='QcDKKNeedFutureCountCheck',
            status='OK',
            description='Entities that waiting for updates future in normal',
        ),
        dict(
            host='test',
            service='QcNeedFutureCheck',
            status='OK',
            description='No qc_settings errors',
        ),
    ]
