# pylint: disable=protected-access, redefined-outer-name, too-many-arguments
# pylint: disable=too-many-locals, unused-variable, invalid-name
import datetime
import sys

import aiohttp
import pytest

from taxi.clients import crons
from taxi.logs import auto_log_extra
from taxi.maintenance import run
from taxi.maintenance import task
from taxi.maintenance import utils


@pytest.fixture
def get_do_stuff_module(stub, monkeypatch, mock):
    def _get():
        @mock
        @utils.lock_for(2 * 60)
        @utils.autoprolong
        async def do_stuff_fn(context, loop, log_extra=None):
            return

        module = stub(do_stuff=do_stuff_fn)
        module_path = 'some_package.some_module'
        monkeypatch.setitem(sys.modules, module_path, module)

        return module_path, module

    return _get


@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.parametrize('quiet', [True, False])
@pytest.mark.parametrize('debug', [True, False])
@pytest.mark.parametrize('rand_time', [0, 1])
@pytest.mark.parametrize('without_lock', [True, False])
@pytest.mark.parametrize('force_start', [True, False])
@pytest.mark.parametrize('task_disabled', [True, False])
@pytest.mark.mongodb_collections('distlock', 'cron_tasks')
def test_run(
        get_do_stuff_module,
        mock,
        patch,
        db,
        loop,
        quiet,
        debug,
        rand_time,
        without_lock,
        task_disabled,
        force_start,
):
    @patch('taxi.settings.is_test_environment')
    def _is_test_environment():
        return False

    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    async def send_mock(metric, value, timestamp):
        pass

    @patch('taxi.maintenance.run.is_task_disabled')
    async def _is_task_disabled(task, db, *, log_extra=None):
        return task_disabled

    @patch('taxi.clients.crons.CronsClient.lock_aquire')
    async def service_lock_aquire(
            task_name, task_run_id, now, till, log_extra=None,
    ):
        await db.distlock.insert_one({'_id': task_name, 'o': task_run_id})
        return True

    @patch('taxi.clients.crons.CronsClient.start')
    async def task_start(
            task_name,
            task_run_id,
            start_time,
            hostname=None,
            features=None,
            service=None,
    ):
        await db.cron_tasks.insert_one(
            {
                '_id': task_run_id,
                'start_time': datetime.datetime.utcnow(),
                'name': task_name,
                'status': 'in_progress',
                'end_time': None,
                'execution_time': None,
                'clock_time': None,
                'hostname': 'test-fqdn',
                'features': features,
                'service': service,
            },
        )

    @patch('taxi.clients.crons.CronsClient.finish')
    async def finish_task(
            task_name,
            task_run_id,
            start_time,
            end_time,
            execution_time,
            clock_time,
            status,
    ):
        await db.cron_tasks.update_one(
            {'_id': task_run_id},
            {
                '$set': {
                    'status': status,
                    'end_time': end_time,
                    'execution_time': execution_time,
                    'clock_time': clock_time,
                },
            },
        )

    module_path, do_stuff_module = get_do_stuff_module()

    task_name = module_path.replace('.', '-')
    run_name = task_name

    data = object()

    @mock
    async def setup_context(loop, db):
        return data

    argv = [module_path, '-t', str(rand_time)]
    if debug:
        argv.append('--debug')
    if quiet:
        argv.append('--quiet')
    if without_lock:
        argv.append('--without-lock')
    if force_start:
        argv.append('--force')

    run.run(setup_context, 'log-ident', argv, loop)

    if not force_start and task_disabled:
        assert do_stuff_module.do_stuff.call is None
        return

    do_stuff_call = do_stuff_module.do_stuff.call
    assert do_stuff_call is not None
    assert do_stuff_call['context'].data == data
    graphite_calls = send_mock.calls
    assert len(graphite_calls) == 2

    assert graphite_calls[0]['metric'] == (
        'cron.%s.execution_time' % task_name
    )
    assert graphite_calls[1]['metric'] == (
        'cron.%s.%s' % (task_name, task._Status.FINISHED)
    )
    assert len(setup_context.calls) == 1
    task_context = do_stuff_call['context']

    cron_task_doc = loop.run_until_complete(
        db.cron_tasks.find_one({'_id': task_context.id}),
    )

    expected_fields = {'name': task_name, 'status': task._Status.FINISHED}

    for key, value in expected_fields.items():
        assert cron_task_doc[key] == value

    assert cron_task_doc['end_time'] is not None
    assert cron_task_doc['execution_time'] is not None
    assert cron_task_doc['clock_time'] is not None
    lock_find = loop.run_until_complete(
        db.distlock.find_one({'_id': run_name}),
    )
    if without_lock:
        assert lock_find is None
    else:
        assert lock_find is not None


@pytest.fixture
def task_instance(get_do_stuff_module):
    module_path, _ = get_do_stuff_module()
    return task.Task(module_path)


@pytest.fixture
def disable_task(patch, db):
    async def _disable(on_host, in_db, _task_name):
        @patch('os.path.isfile')
        def is_file(path):
            if path == run.HOST_DISABLING_FILENAME:
                return on_host
            raise RuntimeError

        @patch('taxi.clients.crons.CronsClient.is_disabled')
        async def _is_disabled(task_name, *args, **kwargs):
            return {'is_enabled': not in_db or _task_name != task_name}

    return _disable


@pytest.mark.parametrize('on_host', [True, False])
@pytest.mark.parametrize('in_db', [True, False])
@pytest.mark.mongodb_collections('static')
async def test_is_task_disabled_on_host(
        task_instance, disable_task, on_host, in_db,
):
    await disable_task(on_host, in_db, task_instance.name)

    log_extra = auto_log_extra.get_log_extra()
    is_disabled = await run.is_task_disabled(
        task_instance, crons.CronsClient('', None), log_extra=log_extra,
    )
    assert is_disabled == (on_host or in_db)


@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.parametrize('enabled', [True, False])
@pytest.mark.parametrize('lock_aquire_fail', [True, False])
@pytest.mark.parametrize('lock_prolong_fail', [True, False])
@pytest.mark.parametrize('start_task_failed', [True, False])
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                CRON_SERVICE_USAGE={
                    'use_service_except_from_disabled': False,
                    'tasks_disabled_using_service': [],
                    'use_service_for_enabled': True,
                    'tasks_enabled_using_service': [
                        'some_package-some_module',
                    ],
                },
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                CRON_SERVICE_USAGE={
                    'use_service_except_from_disabled': False,
                    'tasks_disabled_using_service': [],
                    'use_service_for_enabled': True,
                    'tasks_enabled_using_service': [],
                },
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                CRON_SERVICE_USAGE={
                    'use_service_except_from_disabled': True,
                    'tasks_disabled_using_service': [
                        'some_package-some_module',
                    ],
                },
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                CRON_SERVICE_USAGE={
                    'use_service_except_from_disabled': True,
                    'tasks_disabled_using_service': [],
                },
            ),
        ),
    ],
)
def test_run_using_service(
        loop,
        mock,
        patch,
        get_do_stuff_module,
        enabled,
        lock_aquire_fail,
        lock_prolong_fail,
        start_task_failed,
):
    @patch('taxi.settings.is_test_environment')
    def _is_test_environment():
        return False

    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    async def send_mock(metric, value, timestamp):
        pass

    @patch('taxi.clients.crons.CronsClient.is_disabled')
    async def service_cron_is_disabled(task_name, log_extra=None):
        assert task_name == run_name
        return {'is_enabled': enabled}

    @patch('taxi.clients.crons.CronsClient.lock_aquire')
    async def service_lock_aquire(
            task_name, task_run_id, now, till, log_extra=None,
    ):
        assert task_name == run_name
        return not lock_aquire_fail

    @patch('taxi.clients.crons.CronsClient.lock_prolong')
    async def service_lock_prolong(
            task_name, task_run_id, till, log_extra=None,
    ):
        assert task_name == run_name
        return not lock_prolong_fail

    @patch('taxi.clients.crons.CronsClient.start')
    async def service_start_task(
            task_name,
            task_run_id,
            start_time,
            hostname=None,
            features=None,
            service=None,
    ):
        assert task_name == run_name
        if start_task_failed:
            raise aiohttp.ClientError

    @patch('taxi.clients.crons.CronsClient.finish')
    async def service_finish_task(
            task_name,
            task_run_id,
            start_time,
            end_time,
            execution_time,
            clock_time,
            status,
    ):
        assert task_name == run_name

    @patch('taxi.distlock.mongo.DistributedLock._do_acquire')
    async def mongo_lock_aquire(db, now, till):
        return not lock_aquire_fail

    @patch('taxi.distlock.mongo.DistributedLock._do_prolong')
    async def mongo_lock_prolong(db, till):
        return not lock_prolong_fail

    @patch('taxi.maintenance.task.TaskRunDoc.save')
    async def mongo_start_task():
        pass

    @patch('taxi.maintenance.task.TaskRunDoc.write_result')
    async def mongo_finish_task():
        pass

    module_path, do_stuff_module = get_do_stuff_module()

    _task_name = module_path.replace('.', '-')
    run_name = _task_name

    data = object()

    @mock
    async def setup_context(loop, db):
        return data

    argv = [module_path, '-t', '0']

    lock_aquired = enabled and not lock_aquire_fail

    if lock_aquired and start_task_failed:
        with pytest.raises(aiohttp.ClientError):
            run.run(setup_context, 'log-ident', argv, loop)
    else:
        run.run(setup_context, 'log-ident', argv, loop)

    assert service_cron_is_disabled.call is not None
    if not enabled:
        return

    assert service_lock_aquire.call is not None
    assert mongo_lock_aquire.call is None
    if lock_aquire_fail:
        return

    # anyway removing lock after finish
    assert bool(service_lock_prolong.call)
    if lock_prolong_fail:
        return

    assert service_start_task.call is not None
    assert mongo_start_task.call is None
    if start_task_failed:
        return

    assert service_finish_task.call is not None
    assert mongo_finish_task.call is None
    assert len(list(send_mock.calls)) == 2
