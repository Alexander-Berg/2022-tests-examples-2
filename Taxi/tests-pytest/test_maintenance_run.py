import collections
import json
import logging

import pytest

from taxi.core import arequests
from taxi.core import async
from taxi.core import db
from taxi.external import crons
from taxi.internal import dbh

from taxi_maintenance import run


@pytest.fixture
def get_do_stuff_module(stub, mock):
    def _get(partitioned):
        @mock
        @async.inline_callbacks
        def do_stuff_fn(start_time, log_extra=None, *args, **kwargs):
            yield

        module = stub(
            do_stuff=do_stuff_fn,
            AUTOPROLONG=True,
            LOCK_TIME=2 * 60,
            REQUIRES_PARTITION=partitioned,
        )
        module_path = 'some_package.some_module'
        return module_path, module

    return _get


@pytest.yield_fixture(autouse=True)
def cleanup_logger():
    yield
    logger = logging.getLogger()
    while logger.handlers:
        handler = logger.handlers[0]
        logger.removeHandler(handler)


@pytest.mark.config(
    CRON_SERVICE_USAGE={
        'use_service_except_from_disabled': False,
        'tasks_disabled_using_service': [],
        'use_service_for_enabled': False,
        'tasks_enabled_using_service': [],
    }
)
@pytest.mark.parametrize('quiet', [True, False])
@pytest.mark.parametrize('debug', [True, False])
@pytest.mark.parametrize('rand_time', [0, 1])
@pytest.mark.parametrize('without_lock', [True, False])
@pytest.mark.parametrize('task_disabled', [True, False])
@pytest.mark.parametrize('force_start', [True, False])
@pytest.mark.parametrize('partitioned', [True, False])
@pytest.inline_callbacks
def test_run(
        patch,
        get_do_stuff_module,
        quiet, debug, rand_time, without_lock,
        task_disabled, force_start, partitioned
):

    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    def send_mock(metric, value, timestamp):
        pass

    @patch('taxi_maintenance.run.CommandRunner._is_disabled')
    @async.inline_callbacks
    def _is_task_disabled(command, use_service, log_extra=None):
        yield
        if force_start:
            async.return_value(False)
        async.return_value(task_disabled)

    module_path, do_stuff_module = get_do_stuff_module(partitioned)
    full_task_name = 'taxi_maintenance.stuff.{}'.format(module_path)
    lock_name = full_task_name + ('@0/1' if partitioned else '')

    @patch('importlib.import_module')
    def import_mock(name, package=None):
        return do_stuff_module

    argv = [module_path, '-t', str(rand_time)]
    if debug:
        argv.append('--debug')
    if quiet:
        argv.append('--quiet')
    if without_lock:
        argv.append('--without-lock')
    if force_start:
        argv.append('--force')
    if partitioned:
        argv.append('--partition')
        argv.append('0/1')

    yield run.main(argv)

    if not force_start and task_disabled:
        assert do_stuff_module.do_stuff.call is None
        async.return_value()

    do_stuff_call = do_stuff_module.do_stuff.call
    assert do_stuff_call is not None
    graphite_calls = send_mock.calls
    assert len(graphite_calls) == 2

    assert graphite_calls[0]['metric'] == (
        'cron.%s.execution_time' % module_path
    )
    assert graphite_calls[1]['metric'] == (
        'cron.%s.%s' % (module_path, dbh.cron_tasks.STATUS_FINISHED)
    )
    task_log_extra = do_stuff_call['kwargs']['log_extra']

    cron_task_doc = yield db.cron_tasks.find_one({
        '_id': task_log_extra['_link']
    })

    expected_fields = {
        'name': full_task_name,
        'status': dbh.cron_tasks.STATUS_FINISHED,
    }

    for key, value in expected_fields.items():
        assert cron_task_doc[key] == value

    assert cron_task_doc['end_time'] is not None
    assert cron_task_doc['execution_time'] is not None
    assert cron_task_doc['clock_time'] is not None
    lock_find = yield db.distlock.find_one({
        '_id': lock_name,
    })

    if without_lock:
        assert lock_find is None
    else:
        assert lock_find is not None


@pytest.mark.config(
    CRON_SERVICE_USAGE={
        'use_service_except_from_disabled': True,
        'tasks_disabled_using_service': [],
    }
)
@pytest.mark.parametrize('enabled', [True, False])
@pytest.mark.parametrize('lock_aquire_fail', [True, False])
@pytest.mark.parametrize('lock_prolong_fail', [True, False])
@pytest.mark.parametrize('start_task_failed', [True, False])
@pytest.mark.parametrize('partitioned', [True, False])
@pytest.inline_callbacks
def test_run_using_service(
        areq_request, patch,
        get_do_stuff_module,
        enabled, lock_aquire_fail, lock_prolong_fail, start_task_failed,
        partitioned,
):

    crons_service_calls_count = collections.defaultdict(int)

    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    def send_mock(metric, value, timestamp):
        pass

    @areq_request
    def crons_mock(method, url, *args, **kwargs):
        assert url.startswith('http://')
        if 'enabled' not in url:
            assert full_task_name in url
        else:
            assert module_path in url

        if 'enabled' in url:
            assert method == 'GET'
            crons_service_calls_count['enabled'] += 1
            return areq_request.response(200, body=json.dumps({
                'is_enabled': enabled
            }))
        if 'aquire' in url:
            assert method == 'POST'
            crons_service_calls_count['lock_aquire'] += 1
            return areq_request.response(
                423 if lock_aquire_fail else 200,
            )
        if 'prolong' in url:
            assert method == 'POST'
            crons_service_calls_count['lock_prolong'] += 1
            return areq_request.response(
                404 if lock_prolong_fail else 200,
            )
        if 'start' in url:
            assert method == 'POST'
            crons_service_calls_count['task_start'] += 1
            return areq_request.response(
                409 if start_task_failed else 200,
                body=json.dumps({
                    'message': 'failed to start task',
                    'code': 'fail'
                }) if start_task_failed else None,
            )
        if 'finish' in url:
            assert method == 'POST'
            crons_service_calls_count['task_finish'] += 1
            return areq_request.response(200)

        assert False, 'unknown url request'

    module_path, do_stuff_module = get_do_stuff_module(partitioned)
    full_task_name = 'taxi_maintenance.stuff.{}'.format(module_path)

    @patch('importlib.import_module')
    def import_mock(name, package=None):
        return do_stuff_module

    argv = [module_path, '-t', '0']
    if partitioned:
        argv.append('--partition')
        argv.append('0/1')

    # wont fail any way, just fallback on direct mongo usage
    yield run.main(argv)

    assert crons_service_calls_count['enabled'] == 1
    if not enabled:
        return

    assert crons_service_calls_count['lock_aquire'] == 1
    if lock_aquire_fail:
        return

    assert crons_service_calls_count['task_start'] == 1
    if start_task_failed:
        return

    assert crons_service_calls_count['lock_prolong'] == 1
    if lock_prolong_fail:
        return

    assert crons_service_calls_count['task_finish'] == 1

    assert len(list(send_mock.calls)) == 2


@pytest.mark.config(
    CRON_SERVICE_USAGE={
        'use_service_except_from_disabled': True,
        'tasks_disabled_using_service': [],
    }
)
@pytest.mark.parametrize('service_network_error', [True, False])
@pytest.mark.parametrize('service_unknown_error', [True, False])
@pytest.inline_callbacks
def test_graceful_degradation(
        patch,
        get_do_stuff_module, crons_service_errors_mock,
        service_network_error, service_unknown_error,
):
    service_mocks, mongo_mocks = crons_service_errors_mock(
        service_network_error, service_unknown_error,
    )

    module_path, do_stuff_module = get_do_stuff_module(False)

    @patch('importlib.import_module')
    def import_mock(name, package=None):
        return do_stuff_module

    argv = [module_path, '-t', '0']
    yield run.main(argv)

    if service_network_error or service_unknown_error:
        for mock in mongo_mocks.values():
            assert len(mock.calls) == 1

    for mock in service_mocks.values():
        assert len(mock.calls) == 1


@pytest.fixture
def crons_service_errors_mock(patch):
    def _accept(network_error, unknown_service_error):
        @patch('taxi.external.crons.is_enabled')
        @async.inline_callbacks
        def is_enabled_mock(*args, **kwargs):
            yield
            if network_error:
                raise arequests.BaseError
            if unknown_service_error:
                raise crons.BaseError
            else:
                async.return_value(True)

        @patch('taxi.external.crons.lock_aquire')
        @async.inline_callbacks
        def lock_aquire_mock(*args, **kwargs):
            yield
            if network_error:
                raise arequests.BaseError
            if unknown_service_error:
                raise crons.BaseError
            else:
                async.return_value(True)

        @patch('taxi.external.crons.lock_prolong')
        @async.inline_callbacks
        def lock_prolong_mock(*args, **kwargs):
            yield
            if network_error:
                raise arequests.BaseError
            if unknown_service_error:
                raise crons.BaseError
            else:
                async.return_value(True)

        @patch('taxi.external.crons.start')
        @async.inline_callbacks
        def start_mock(*args, **kwargs):
            yield
            if network_error:
                raise arequests.BaseError
            if unknown_service_error:
                raise crons.BaseError

        @patch('taxi.external.crons.finish')
        @async.inline_callbacks
        def finish_mock(*args, **kwargs):
            yield
            if network_error:
                raise arequests.BaseError
            if unknown_service_error:
                raise crons.BaseError

        @patch('taxi_maintenance.run._is_task_enabled')
        @async.inline_callbacks
        def is_task_enabled_mongo(*args, **kwargs):
            yield
            async.return_value(True)

        @patch('taxi.internal.distlock.acquire')
        @async.inline_callbacks
        def lock_acquire_mongo(*args, **kwargs):
            yield
            async.return_value(True)

        @patch('taxi.internal.distlock.prolong')
        @async.inline_callbacks
        def lock_prolong_mongo(*args, **kwargs):
            yield
            async.return_value(True)

        @patch('taxi.internal.dbh.cron_tasks.Doc.insert_task')
        @async.inline_callbacks
        def save_task_mongo(*args, **kwargs):
            yield

        @patch('taxi.internal.dbh.cron_tasks.Doc.save_updates')
        @async.inline_callbacks
        def update_task_mongo(*args, **kwargs):
            yield

        service_mocks = {
            'is_enabled': is_enabled_mock,
            'lock_aquire': lock_aquire_mock,
            'lock_prolong': lock_prolong_mock,
            'start': start_mock,
            'finish': finish_mock,
        }
        mongo_mocks = {
            'is_enabled': is_task_enabled_mongo,
            'lock_aquire': lock_acquire_mongo,
            'lock_prolong': lock_prolong_mongo,
            'start': save_task_mongo,
            'finish': update_task_mongo,
        }
        return service_mocks, mongo_mocks

    return _accept
