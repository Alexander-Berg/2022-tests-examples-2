import os
import json
import logging
import inspect
import getpass
import datetime as dt

import six
import pytest

from sandbox import conftest

from sandbox import common
from sandbox.common import config
import sandbox.common.types.user as ctu
import sandbox.common.types.task as ctt
import sandbox.common.types.client as ctc
import sandbox.common.types.resource as ctr

from sandbox.agentr import client as ar_client

from sandbox.yasandbox import controller
from sandbox.yasandbox.manager import tests as manager_tests
from sandbox.yasandbox.database import mapping

from sandbox import tests

TS = ctt.Status


@pytest.fixture()
def vault_record(api_session_login, test_task, vault_controller, server):
    """
    All tasks in tests below are run under `api_session_login`, hence the owner.
    Change it here, too, if necessary
    """
    vault_controller.create(mapping.Vault(
        owner=test_task.VaultItemOwner.default_value,
        name=test_task.VaultItemName.default_value,
        data=test_task.VaultItemExpected.default_value,
        allowed_users=[api_session_login]
    ))


class RetryTrigger(Exception):
    pass


class TestExecuteTaskMeta(type):
    def __new__(mcs, name, bases, namespace):
        for key, value in namespace.items():
            if key.startswith("test__"):
                namespace[key] = pytest.mark.usefixtures("s3_simulator")(value)
        return super(TestExecuteTaskMeta, mcs).__new__(mcs, name, bases, namespace)


@pytest.mark.test_tasks
class TestExecuteTask(six.with_metaclass(TestExecuteTaskMeta, object)):
    @staticmethod
    def _execute_task_cleanup(job_registry):
        for token, job in job_registry.items():
            for proc in tests.TaskSubproc.find_by_tags([token]):
                proc.kill()
            job_registry.pop(token, None)

    @staticmethod
    def _execute_task(
        task_id,
        rest_su_session, client_node_id,
        watchdog_timeout, wait_status=TS.SUCCESS, triggers=None, call_client_started=True, status_check_ticks=30,
        test_validate=False, test_drop=False, enqueue=False,
    ):
        import sandbox.client
        from sandbox.yasandbox import manager
        from sandbox.services.modules import tasks_enqueuer

        sandbox.client.system.UNPRIVILEGED_USER = common.os.User(getpass.getuser())
        sandbox.client.system.SERVICE_USER = common.os.User(getpass.getuser())

        pt = sandbox.client.pinger.PingSandboxServerThread()
        pt._service_threads = {}
        job_registry = sandbox.client.commands.Command.registry
        ar_client.Service(logging.getLogger("test_client")).reset()
        pt.stopped.clear()
        pt.rest = rest_su_session
        pt.node_id = client_node_id

        task_state_switcher = conftest.task_state_switcher(None, rest_su_session, None)
        te_th = tasks_enqueuer.TasksEnqueuer()

        # to avoid treating client as NEW and creating CLEANUP task
        client_uuid = manager.client_manager.load(client_node_id)["uuid"]
        pt._PingSandboxServerThread__client_uuid = lambda: client_uuid

        if enqueue:
            with common.rest.DispatchedClient as dispatch:
                dispatch(lambda *_, **__: pytest.fail("Undispatched REST client detected"))
                tw = controller.TaskWrapper(controller.Task.get(task_id))
                controller.TaskQueue.enqueue_task(tw)

        if call_client_started:
            pt._reset()
            while not pt._events.empty():
                pt._events.get()
        start = dt.datetime.now()

        tick = 0
        logger = logging.getLogger("task_#{}".format(task_id))
        logger.info("Executing task #%s loop till status %r with triggers %r", task_id, wait_status, triggers)
        while not pt.stopped.is_set() or not pt._events.empty() or job_registry:
            if not pt.stopped.is_set():
                task_state_switcher.tick()
                te_th.tick()

            tick += 1
            now = dt.datetime.now()
            if not job_registry and pt._events.empty():
                pt._timer.tick = 0.1
                pt._timer.idle = 0
                number_of_tokens = len(job_registry)
                pt._jobgetter(pt.rest)
                common.utils.progressive_waiter(0, .1, 1, lambda: len(job_registry) > number_of_tokens)

            if test_drop:
                tokens = job_registry.keys()
                if tokens:
                    job = job_registry[tokens[0]]

                    old_cleanup = job.platform.cleanup
                    cleanup_count = [0]

                    def new_cleanup():
                        old_cleanup()
                        cleanup_count[0] += 1

                    job.platform.cleanup = new_cleanup

                    pt._dropajob.put(job)
                    pt._jobdropper(pt.rest)

                    pt._dropajob.put(job)
                    pt._jobdropper(pt.rest)
                    pt.stop()

                    if cleanup_count[0] > 1:
                        pytest.fail("job's platform cleaned up {} times".format(cleanup_count[0]))

                    TestExecuteTask._execute_task_cleanup(job_registry)
                    return

            while not pt._events.empty():
                if test_validate and pt.rest.client[client_node_id].job[:]:
                    logger.debug("Processing client %r jobs validation.", client_node_id)
                    pt._validate_jobs()
                    if not pt.rest.client[client_node_id].job[:]:
                        pytest.fail("_validate_jobs killed a job")
                    test_validate = False
                pt._serve_events()
            if not tick % status_check_ticks:
                pt._status_report(pt.rest)

            while not pt._dropajob.empty():
                pt._jobdropper(pt.rest)

            if (now - start).total_seconds() > watchdog_timeout:
                pytest.fail('Watchdog timeout. Start time was: {}, current is: {}. Task: {}'.format(
                    start, now, rest_su_session.task[task_id][:]
                ))
            task_status = mapping.Task.objects(id=task_id).scalar("execution__status").next()
            logger.debug("Check task #%s in status '%s'", task_id, task_status)
            if task_status == TS.ENQUEUING:
                controller.TaskQueue.validate(logger=logger)
            if triggers:
                trigger = triggers.pop(task_status, None)
                if trigger is not None:
                    logger.info("Processing task #%s trigger for status '%s'", task_id, task_status)
                    try:
                        if len(inspect.getargspec(trigger).args) == 1:
                            if trigger(job_registry.itervalues().next()):
                                pt.stop()
                        else:
                            if trigger():
                                pt.stop()
                    except RetryTrigger:
                        triggers[task_status] = trigger
                    continue
            if not pt.stopped.is_set() and len(job_registry) == 0 and task_status not in (
                TS.ENQUEUING, TS.ENQUEUED, TS.ASSIGNED,
                TS.PREPARING, TS.EXECUTING,
                TS.FINISHING, TS.STOPPING,
                TS.WAIT_TASK, TS.WAIT_TIME,
                TS.RELEASING,
            ):
                pt.stop()

        logger.info("Task #%s loop finished with status %r", task_id, task_status)
        if test_drop:
            pytest.fail("test_drop was not performed")

        if wait_status:
            assert mapping.Task.objects.with_id(task_id).execution.status == wait_status

        TestExecuteTask._execute_task_cleanup(job_registry)

        return task_id

    def test__idle_job(self, server, client, client_node_id, rest_su_session, serviceq):
        import sandbox.client
        from sandbox.yasandbox import manager

        sandbox.client.system.UNPRIVILEGED_USER = common.os.User(getpass.getuser())
        sandbox.client.system.SERVICE_USER = common.os.User(getpass.getuser())

        pt = sandbox.client.pinger.PingSandboxServerThread()
        pt._service_threads = {}
        job_registry = sandbox.client.commands.Command.registry
        ar_client.Service(logging.getLogger("test_client")).reset()
        pt.stopped.clear()
        pt.rest = rest_su_session
        pt.node_id = client_node_id
        pt.need_cleanup = lambda: False
        pt.token = "service-auth-token"

        client_uuid = manager.client_manager.load(client_node_id)["uuid"]
        pt._PingSandboxServerThread__client_uuid = lambda: client_uuid

        pt._reset()
        while not pt._events.empty():
            pt._events.get()

        start = dt.datetime.now()
        subsequent_job = sandbox.client.commands.Command("IDLE")

        while not pt.stopped.is_set() or not pt._events.empty():
            now = dt.datetime.now()
            if not job_registry and pt._events.empty():
                pt._timer.idle = config.Registry().client.idle_time
                pt._jobgetter(pt.rest)
                if job_registry:
                    idle_job = job_registry[ctc.ServiceTokens.SERVICE_TOKEN]
                    idle_job.args["mds_token"] = None
                    assert idle_job.args["service_auth"] == pt.token
                    idle_job.on_terminate = lambda: subsequent_job
                    pt._timer.idle = 0

            while not pt._events.empty():
                pt._serve_events()

            if (now - start).total_seconds() > 60:
                pytest.fail('Watchdog timeout. Start time was: {}, current is: {}. Registry: {}'.format(
                    start, now, job_registry
                ))

            if not pt.stopped.is_set() and subsequent_job.status:
                assert subsequent_job.args["service_auth"] == pt.token
                pt.stop()

        TestExecuteTask._execute_task_cleanup(job_registry)

    def test__test_task(
        self, server, api_su_session, rest_su_session, rest_session, client, client_node_id,
        api_session_login, serviceq, test_task
    ):
        ctx_update = {
            test_task.LiveTime.name: .1,
            test_task.CreateResources.name: True,
            test_task.CreateResourceOnEnqueue.name: True,
            test_task.CreateSubtask.name: True,
            test_task.NumberOfSubtasks.name: 3,
            test_task.WaitTime.name: 1,
        }
        task_id = api_su_session.create_task({
            'type_name': test_task.type,
            'owner': api_session_login,
            'author': api_session_login,
            'execution_space': 1000,
            'ctx': ctx_update
        })

        ctx = rest_session.task[task_id].context[:]
        for p in test_task.input_parameters:
            if not p.dummy and p.name not in ctx_update.viewkeys():
                assert ctx[p.name] == p.default_value
            else:
                # What a beautiful product - dummy parameters have their own keys in task's context!
                assert p.name in ctx

        def check_enqueued():
            assert rest_session.task[task_id].context.read()['test_on_enqueue']

        def check_resources(task_id=task_id, state=ctr.State.NOT_READY, total=2):
            data = rest_session.resource.read(task_id=task_id, state=state, type="TEST_TASK_RESOURCE", limit=0)
            assert data["total"] == total, data

        def check_session():
            session = mapping.OAuthCache.objects(task_id=task_id).first()
            assert session is None

        def on_wait():
            check_session()
            return check_resources()

        self._execute_task(
            task_id, rest_su_session, client_node_id, 180, TS.SUCCESS,
            {
                TS.ASSIGNED: check_enqueued,
                TS.WAIT_TIME: on_wait,
                TS.WAIT_TASK: on_wait,
                TS.SUCCESS: check_session,
            },
            test_validate=True,
        )

        # check resources
        check_resources(state=ctr.State.READY, total=3)
        subtasks = rest_session.task.read(parent=task_id, limit=100)
        assert subtasks['total'] == ctx_update[test_task.NumberOfSubtasks.name]
        for subtask in subtasks['items']:
            assert subtask['status'] == ctt.Status.SUCCESS
        check_resources(task_id=subtasks['items'][0]['id'], state=ctr.State.READY, total=3)

    def test__jobdropper(
        self, server, api_su_session, rest_su_session, client, client_node_id,
        api_session_login, serviceq, test_task
    ):
        task_id = api_su_session.create_task({
            'type_name': test_task.type,
            'owner': api_session_login,
            'author': api_session_login,
            'ctx': {
                test_task.LiveTime.name: .1,
            }
        })
        self._execute_task(
            task_id, rest_su_session, client_node_id,
            60, TS.SUCCESS, test_drop=True
        )

    def test__wait_single_task(
        self, server, api_su_session, rest_su_session, client, client_node_id,
        api_session_login, serviceq, test_task
    ):
        task_id = api_su_session.create_task({
            'type_name': test_task.type,
            'owner': api_session_login,
            'author': api_session_login,
            'execution_space': 1000,
            'ctx': {
                test_task.LiveTime.name: .1,
                test_task.CreateResources.name: False,
                test_task.CreateSubtask.name: True,
                test_task.NumberOfSubtasks.name: 1,
                test_task.WaitTime.name: 1,
                test_task.WaitOnEnqueue.name: 1,
            }
        })

        def trigger():
            t = api_su_session.get_task(task_id)
            assert t
            assert json.loads(t['ctx'])['test_on_enqueue'] == 1
        self._execute_task(
            task_id, rest_su_session, client_node_id,
            180, TS.SUCCESS, {TS.ASSIGNED: trigger}
        )

    def test__check_author_inheritance(
        self, server, rest_su_session, client, client_node_id, api_session_login,
        serviceq, task_manager, anonymous_session, test_task
    ):
        task_id = anonymous_session.create_task({
            'type_name': test_task.type,
            'owner': api_session_login,
            'author': api_session_login,
            'execution_space': 1000,
            'ctx': {
                test_task.CreateResources.name: False,
                test_task.CreateIndependentTask.name: True
            }
        })

        self._execute_task(
            task_id, rest_su_session, client_node_id,
            180, TS.SUCCESS
        )

        task = task_manager.load(task_id)
        independent_task = task_manager.load(task.ctx['independent_task_id'])
        assert independent_task.author == ctu.ANONYMOUS_LOGIN

    def test__send_email_save_task_id(
        self, server, rest_su_session, client, client_node_id, api_session_login,
        serviceq, task_manager, anonymous_session, notification_controller, test_task
    ):
        email_recipient = 'test_recipient'
        task_id = anonymous_session.create_task({
            'type_name': test_task.type,
            'owner': api_session_login,
            'author': api_session_login,
            'execution_space': 1000,
            'ctx': {
                test_task.CreateResources.name: False,
                test_task.SendEmail.name: True,
                test_task.EmailRecipient.name: email_recipient
            }
        })

        self._execute_task(
            task_id, rest_su_session, client_node_id,
            180, TS.SUCCESS
        )

        task = task_manager.load(task_id)
        notification = notification_controller.load(task.ctx['email_notification_id'])

        assert notification.task_id == task_id

    def test__test_task__threading(
        self, server, api_su_session, rest_su_session, client, client_node_id,
        api_session_login, serviceq, test_task
    ):
        task_id = api_su_session.create_task({
            'type_name': test_task.type,
            'owner': api_session_login,
            'author': api_session_login,
            'execution_space': 1000,
            'ctx': {
                test_task.LiveTime.name: .1,
                'multi_threading': True
            }
        })
        self._execute_task(task_id, rest_su_session, client_node_id, 60)

    def test__test_task__exception(
        self, server, api_su_session, rest_su_session, client, client_node_id,
        api_session_login, serviceq, test_task
    ):
        task_id = api_su_session.create_task({
            'type_name': test_task.type,
            'owner': api_session_login,
            'author': api_session_login,
            'ctx': {
                test_task.LiveTime.name: .1,
                test_task.RaiseExceptionOnStart.name: True
            }
        })
        self._execute_task(
            task_id, rest_su_session, client_node_id,
            80, TS.EXCEPTION
        )

    def test__test_task__exception_on_invalid_context(
        self, server, api_su_session, rest_su_session, client, client_node_id,
        api_session_login, serviceq, test_task
    ):
        task_id = api_su_session.create_task({
            "type_name": test_task.type,
            "owner": api_session_login,
            "ctx": {
                test_task.LiveTime.name: .1,
                test_task.InvalidContextOnExecute.name: True
            }
        })
        self._execute_task(
            task_id, rest_su_session, client_node_id,
            80, TS.EXCEPTION
        )

    def test__test_task__failure(
        self, server, api_su_session, rest_su_session, client, client_node_id,
        api_session_login, serviceq, test_task
    ):
        task_id = api_su_session.create_task({
            'type_name': test_task.type,
            'owner': api_session_login,
            'author': api_session_login,
            'fail_on_any_error': True,
            'ctx': {
                test_task.LiveTime.name: .1,
                test_task.RaiseExceptionOnStart.name: True,
            }
        })
        self._execute_task(
            task_id, rest_su_session, client_node_id,
            80, TS.FAILURE
        )

    def test__test_task__timeout(
        self, server, api_su_session, rest_su_session, client, client_node_id,
        api_session_login, serviceq, test_task
    ):
        task_id = api_su_session.create_task({
            'type_name': test_task.type,
            'owner': api_session_login,
            'author': api_session_login,
            'ctx': {
                test_task.LiveTime.name: 10,
                'kill_timeout': 1
            }
        })
        self._execute_task(
            task_id, rest_su_session, client_node_id,
            80, TS.TIMEOUT
        )
        assert rest_su_session.task[task_id].context.read()["has_channel_task"]

    @pytest.mark.usefixtures("vault_record", "server", "client", "serviceq")
    def test__test_task__stop_on_execution(
        self, api_su_session, rest_su_session, client_node_id, api_session_login, test_task
    ):
        for ctx_key, cancel_status in (
            (test_task.PreparingLiveTime.name, TS.PREPARING),
            (test_task.LiveTime.name, TS.EXECUTING),
        ):
            task_id = api_su_session.create_task({
                "type_name": test_task.type,
                "owner": api_session_login,
                "ctx": {
                    ctx_key: 5,
                    test_task.CheckVault.name: True,
                }
            })

            def trigger():
                session = mapping.OAuthCache.client_sessions(client_node_id).first()
                assert session.validated > dt.datetime.utcnow() - dt.timedelta(minutes=1)
                controller.TaskWrapper(controller.Task.get(task_id)).stop()
                assert mapping.OAuthCache.objects.with_id(session.token).state == ctt.SessionState.ABORTED

            self._execute_task(
                task_id, rest_su_session, client_node_id,
                180, TS.STOPPED, {cancel_status: trigger},
                status_check_ticks=1
            )
            assert rest_su_session.task[task_id].context.read()["has_vault_key"]
            assert rest_su_session.task[task_id].context.read()["has_channel_task"]

        task_id = api_su_session.create_task({
            "type_name": test_task.type,
            "owner": api_session_login,
            "ctx": {
                test_task.LiveTime.name: 1,
                test_task.CheckVault.name: True,
            }
        })

        def trigger():
            assert mapping.OAuthCache.client_sessions(client_node_id).first().vault
            api_su_session.cancel_task(task_id)
            assert mapping.OAuthCache.client_sessions(client_node_id).first().vault

        self._execute_task(
            task_id, rest_su_session, client_node_id,
            180, TS.STOPPED, {TS.ASSIGNED: trigger}, False
        )
        assert rest_su_session.task[task_id].context.read()["has_vault_key"]
        assert rest_su_session.task[task_id].context.read()["has_channel_task"]

    @pytest.mark.usefixtures("vault_record")
    def test__test_task__stop_on_enqueue(
        self, server, api_su_session, rest_su_session, client, client_node_id,
        api_session_login, serviceq, test_task
    ):
        task_id = api_su_session.create_task({
            'type_name': test_task.type,
            'owner': api_session_login,
            'author': api_session_login,
            'ctx': {
                test_task.StopOnEnqueue.name: True,
                test_task.CheckVault.name: True,
            }
        })
        self._execute_task(
            task_id, rest_su_session, client_node_id,
            80, TS.STOPPED
        )
        assert rest_su_session.task[task_id].context.read()['has_vault_key']

    @pytest.mark.usefixtures("vault_record")
    def test__test_task__release(
        self, server, api_su_session, rest_su_session, client, client_node_id, api_session_login,
        api_su_session_login, serviceq, service_user, test_task
    ):
        task_params = {
            'type_name': test_task.type,
            'owner': api_session_login,
            'author': api_session_login,
            'ctx': {
                test_task.DependentResources.name: None,
                test_task.DependentResource.name: None,
                test_task.CreateResources.name: True,
                test_task.LiveTime.name: .1,
                test_task.CheckVault.name: True,
            }
        }
        task_id = api_su_session.create_task(task_params)
        release_status = 'stable'
        release_subject = 'subject'
        release_comments = 'comments'
        release_changelog = ['change1', 'change2', 'change3']
        release_params = {'param1': 1, 'param2': 2, 'param3': 3}
        self._execute_task(
            task_id, rest_su_session, client_node_id, 80, TS.RELEASED,
            {TS.SUCCESS: lambda: api_su_session.create_release(
                task_id, release_status, release_subject, release_comments,
                release_changelog, None, None, release_params
            ) and False}
        )
        task = api_su_session.get_task(task_id)
        assert task
        res = api_su_session.list_resources({
            'task_id': task_id,
            'resource_type': 'TEST_TASK_RESOURCE',
            'all_attrs': {'released': release_status}
        })
        assert len(res) == 2
        ctx = json.loads(task['ctx'])
        assert ctx['has_vault_key']
        assert ctx['has_channel_task']
        assert ctx['release_changelog'] == release_comments
        test_on_release = ctx['test_on_release']
        assert test_on_release['release_status'] == release_status
        assert test_on_release['release_subject'] == release_subject
        assert test_on_release['release_changelog_entry'] == release_changelog
        assert test_on_release['releaser'] == api_su_session_login
        assert test_on_release['release_comments'] == release_comments
        for k, v in release_params.iteritems():
            assert test_on_release[k] == v

        task_id = api_su_session.create_task(task_params)
        release_subject = 'die'
        self._execute_task(
            task_id, rest_su_session, client_node_id, 80, TS.NOT_RELEASED,
            {TS.SUCCESS: lambda: api_su_session.create_release(
                task_id, release_status, release_subject, release_comments,
                release_changelog, None, None, release_params
            ) and False}
        )
        res = api_su_session.list_resources({
            'task_id': task_id,
            'resource_type': 'TEST_TASK_RESOURCE',
            'all_attrs': {'released': None}
        })
        assert len(res) == 0
        res = api_su_session.list_resources({
            'task_id': task_id,
            'resource_type': 'TEST_TASK_RESOURCE'
        })
        assert len(res) == 2

        task_id = api_su_session.create_task(task_params)

        subscriber = 'fake'
        release_subject = 'Default'
        release_params['_release_subscriber'] = subscriber
        self._execute_task(
            task_id, rest_su_session, client_node_id, 80, TS.RELEASED,
            {TS.SUCCESS: lambda: api_su_session.create_release(
                task_id, release_status, release_subject, release_comments,
                release_changelog, None, None, release_params
            ) and False}
        )
        assert controller.Notification.count_inbox(user=subscriber, query={"subject": release_subject}) == 1

    def test__test_task_expire_on_releasing(
        self, server, api_su_session, rest_su_session, client, client_node_id,
        api_session_login, serviceq, service_user, test_task
    ):
        task_params = {
            "type_name": test_task.type,
            "owner": api_session_login,
            "ctx": {
                test_task.ReleasingLiveTime.name: 10,
            }
        }
        task_id = api_su_session.create_task(task_params)

        def on_success():
            assert mapping.OAuthCache.objects(task_id=task_id).first() is None
            api_su_session.create_release(task_id, "stable")

        def on_releasing():
            session = mapping.OAuthCache.objects(task_id=task_id).first()
            if session is None:
                raise RetryTrigger
            controller.OAuthCache.expire(session)

        self._execute_task(
            task_id, rest_su_session, client_node_id, 80, TS.NOT_RELEASED,
            {TS.SUCCESS: on_success, TS.RELEASING: on_releasing}
        )

    def test__test_task_timeout_on_releasing(
        self, request, server, api_su_session, rest_su_session, client, client_node_id,
        api_session_login, serviceq, test_task, json_api_url
    ):
        import sandbox.client
        old_init = sandbox.client.commands.task.ReleaseTaskCommand.__init__

        def overriding_timeout_init(self, *args, **kwargs):
            self.args["kill_timeout"] = 1
            super(sandbox.client.commands.task.ReleaseTaskCommand, self).__init__(*args, **kwargs)
        sandbox.client.commands.task.ReleaseTaskCommand.__init__ = overriding_timeout_init

        def restore_init():
            sandbox.client.commands.task.ReleaseTaskCommand.__init__ = old_init
        request.addfinalizer(restore_init)

        task_id = api_su_session.create_task({
            "type_name": test_task.type,
            "owner": api_session_login,
            "ctx": {
                test_task.ReleasingLiveTime.name: 60,
            }
        })

        def on_success():
            api_su_session.create_release(task_id, "stable")

        self._execute_task(
            task_id, rest_su_session, client_node_id,
            80, TS.NOT_RELEASED, {TS.SUCCESS: on_success}
        )

    def test__test_task__delete(
        self, server, api_su_session, rest_su_session, client, client_node_id,
        api_session_login, serviceq, test_task
    ):
        from sandbox.yasandbox import manager

        task_id = api_su_session.create_task({
            'type_name': test_task.type,
            'owner': api_session_login,
            'author': api_session_login,
            'ctx': {
                test_task.LiveTime.name: .1,
                test_task.NumberOfSubtasks.name: 3,
                test_task.CreateSubtask.name: True,
                test_task.CreateResources.name: False
            }
        })

        def delete_task():
            st = api_su_session.list_tasks({'parent_id': task_id, 'hidden': True})
            assert len(st) == 3
            manager.task_manager.load(st[0]['id']).set_status(TS.RELEASED, force=True)
            api_su_session.delete_task(task_id)

        self._execute_task(
            task_id, rest_su_session, client_node_id,
            180, TS.DELETED, {TS.SUCCESS: delete_task}
        )
        subtasks = api_su_session.list_tasks(
            {"parent_id": task_id, "hidden": True, "status": (ctt.Status.DELETED, ctt.Status.RELEASED)}
        )
        assert len(subtasks) == 3
        # for r in rest_su_session.task[task.id].resources.read()["items"]:
        for i, subtask in enumerate(subtasks):
            if i:
                assert subtask["status"] == TS.DELETED
            else:
                assert subtask["status"] == TS.RELEASED

    def test__test_task__delete_released(
        self, server, api_su_session, rest_su_session, client, client_node_id,
        api_session_login, serviceq, service_user, test_task
    ):
        task_id = api_su_session.create_task({
            'type_name': test_task.type,
            'owner': api_session_login,
            'author': api_session_login,
            'ctx': {
                test_task.LiveTime.name: .1
            }
        })
        release_status = 'stable'
        self._execute_task(
            task_id, rest_su_session, client_node_id, 180, TS.RELEASED,
            {TS.SUCCESS: lambda: api_su_session.create_release(task_id, release_status, 'subject') and False}
        )
        res = api_su_session.list_resources({
            'task_id': task_id,
            'resource_type': 'TEST_TASK_RESOURCE',
            'all_attrs': {'released': release_status}
        })
        assert len(res) == 2
        api_su_session.delete_task(task_id)
        self._execute_task(
            task_id, rest_su_session, client_node_id,
            180, TS.DELETED
        )
        res = api_su_session.list_resources({
            'task_id': task_id,
            'resource_type': 'TEST_TASK_RESOURCE',
            'all_attrs': {'released': None}
        })
        assert len(res) == 0
        res = api_su_session.list_resources({
            'task_id': task_id,
            'resource_type': 'TEST_TASK_RESOURCE'
        })
        assert len(res) == 2

    def test__test_task__delete_executing_task(
        self, server, api_su_session, rest_su_session, client, client_node_id,
        api_session_login, serviceq, test_task
    ):
        for ctx_key, task_status in (
            (test_task.PreparingLiveTime.name, TS.PREPARING),
            (test_task.LiveTime.name, TS.EXECUTING),
            (test_task.FinishingLiveTime.name, TS.FINISHING)
        ):
            task_id = api_su_session.create_task({
                'type_name': test_task.type,
                'owner': api_session_login,
                'author': api_session_login,
                'ctx': {test_task.LiveTime.name: 0, ctx_key: 5, test_task.CreateResources.name: False}
            })
            self._execute_task(
                task_id, rest_su_session, client_node_id,
                180, TS.DELETED,
                {task_status: lambda: api_su_session.delete_task(task_id) and False}
            )

    def test__test_task_timeout_on_timeout(
        self, server, api_su_session, rest_su_session, client, client_node_id,
        api_session_login, serviceq, monkeypatch, test_task
    ):
        task_id = api_su_session.create_task({
            'type_name': test_task.type,
            'owner': api_session_login,
            'author': api_session_login,
            'execution_space': 1000,
            'ctx': {
                test_task.LiveTime.name: 10,
                'kill_timeout': 1,
                test_task.BreakTime.name: 300
            }
        })
        monkeypatch.setattr(config.Registry().common.task.execution, "terminate_timeout", 1)
        self._execute_task(
            task_id, rest_su_session, client_node_id,
            180, TS.TIMEOUT
        )

    def test__test_task_with_empty_resource(
        self, server, api_su_session, rest_su_session, client, client_node_id,
        api_session_login, serviceq, test_task
    ):
        task_params = {
            'type_name': test_task.type,
            'owner': api_session_login,
            'author': api_session_login,
            'execution_space': 1000,
            'ctx': {
                test_task.LiveTime.name: 0,
                test_task.CreateEmptyResource.name: True
            }
        }
        self._execute_task(
            api_su_session.create_task(task_params), rest_su_session, client_node_id,
            80, TS.EXCEPTION
        )

        task_params['fail_on_any_error'] = True
        task_id = self._execute_task(
            api_su_session.create_task(task_params), rest_su_session, client_node_id,
            80, TS.FAILURE
        )
        for r in api_su_session.list_resources({"task_id": task_id}):
            if r["file_name"] == "empty_resource":
                assert r["state"] == ctr.State.BROKEN
            else:
                assert r["state"] == ctr.State.READY

    def test__test_task_expired_session(
        self, server, api_su_session, rest_su_session, client, client_node_id,
        api_session_login, serviceq, test_task
    ):
        for status, ctx in [
            (TS.PREPARING, {test_task.PreparingLiveTime.name: 15}),
            (TS.EXECUTING, {test_task.LiveTime.name: 15}),
        ]:
            task_id = api_su_session.create_task({
                "type_name": test_task.type,
                "owner": api_session_login,
                "execution_space": 1000,
                "ctx": ctx
            })

            def expire_session():
                session = mapping.OAuthCache.objects.get(task_id=task_id)
                controller.OAuthCache.expire(session)

            self._execute_task(
                task_id, rest_su_session, client_node_id,
                watchdog_timeout=80, wait_status=TS.TEMPORARY,
                triggers={status: expire_session},
            )

    def test__test_task_with_unavailable_resource(
        self, server, api_su_session, rest_su_session, client, client_node_id,
        api_session_login, task_manager, resource_manager, serviceq, test_task
    ):
        res = manager_tests._create_real_resource(task_manager, content="test")
        os.remove(res.abs_path())  # maintain READY status, but make the resource physically unavailable at all source
        task_params = {
            "type_name": test_task.type,
            "owner": api_session_login,
            "execution_space": 1000,
            "ctx": {
                test_task.DependentResource.name: res.id
            }
        }
        self._execute_task(
            api_su_session.create_task(task_params), rest_su_session, client_node_id,
            180, TS.NO_RES
        )

    def _sdk2_task(self, task_type, task_params, rest_su_session):
        with common.rest.DispatchedClient as dispatch:
            dispatch(lambda *_, **__: rest_su_session)
            return task_type(None, **task_params)

    def test__test_sdk2_task(
        self, server, rest_su_session, rest_su_session_group,
        client, client_node_id, serviceq, test_task_2
    ):
        task_params = {
            "owner": rest_su_session_group,
            "description": u"Test task",
            "live_time": .1,
            "create_sub_task": True,
            "number_of_subtasks": 1,
        }
        task = self._sdk2_task(test_task_2, task_params, rest_su_session)
        self._execute_task(
            task.id, rest_su_session, client_node_id,
            180, TS.SUCCESS, enqueue=True
        )
        assert rest_su_session.task[task.id][:]["status"] == TS.SUCCESS
        resources = sorted(filter(
            lambda _: _["type"] == "TEST_TASK_2_RESOURCE",
            rest_su_session.task[task.id].resources[:]["items"]
        ), key=lambda _: _["id"])
        assert len(resources) == 2
        res_attrs = {"test_attr": "42", "test_required_attr": "value"}
        assert resources[0]["attributes"] == res_attrs
        res_attrs.pop("test_attr")
        assert resources[1]["attributes"] == res_attrs
        # check number of REST requests caused by running a TEST_TASK_2 with subtask
        # update this number in case of further optimization (see SANDBOX-4528)
        assert rest_su_session.task[task.id].context[:]["__rest_request_count"] == 21
        intervals = rest_su_session.task[task.id][:]["intervals"]
        assert len(intervals["queue"]) == 2
        assert len(intervals["execute"]) == 2
        assert len(intervals["wait"]) == 1

    def test__test_sdk2_wait_time(
        self, server, rest_su_session, rest_su_session_group,
        client, client_node_id, serviceq, test_task_2
    ):
        task_params = {
            "owner": rest_su_session_group,
            "description": u"Test task",
            "live_time": .1,
            "wait_time": 1000,
        }
        task = self._sdk2_task(test_task_2, task_params, rest_su_session)
        self._execute_task(
            task.id, rest_su_session, client_node_id, 180, TS.SUCCESS, enqueue=True,
            triggers={TS.WAIT_TIME: lambda: rest_su_session.batch.tasks.start.update([task.id]) and False}
        )
        with pytest.raises(controller.TimeTrigger.NotExists):
            controller.TimeTrigger.get(task.id)

    def test__test_sdk2_resource_cast(
        self, server, rest_su_session, rest_su_session_group,
        client, client_node_id, serviceq
    ):
        import sandbox.sdk2.tests
        task_cls = sandbox.sdk2.tests.SubResourceTestTask

        task_params = {
            "owner": rest_su_session_group,
            "description": u"Test task",
        }
        task = self._sdk2_task(task_cls, task_params, rest_su_session)
        self._execute_task(
            task.id, rest_su_session, client_node_id,
            180, TS.SUCCESS, enqueue=True
        )
        task_info = rest_su_session.task[task.id][:]
        assert task_info["status"] == TS.SUCCESS
        assert rest_su_session.task[task.id].context[:]["rest_in_range"] == 0

    def test__test_sdk2_task_empty_resource(
        self, server, rest_su_session, rest_su_session_group,
        client, client_node_id, serviceq, test_task_2
    ):
        def run_task(params, expected_status):
            params.update({
                "owner": rest_su_session_group,
                "live_time": 0,
                "create_empty_resource": True,
            })
            task = self._sdk2_task(test_task_2, params, rest_su_session)
            self._execute_task(
                task.id, rest_su_session, client_node_id,
                180, expected_status, enqueue=True
            )

            for r in rest_su_session.task[task.id].resources.read()["items"]:
                if r["file_name"] == "empty_resource":
                    assert r["state"] == ctr.State.BROKEN
                else:
                    assert r["state"] == ctr.State.READY

        run_task({}, TS.EXCEPTION)
        run_task({"fail_on_any_error": True}, TS.FAILURE)

    def test__test_sdk2_task_broken_resources_on_reject(
        self, server, rest_su_session, rest_su_session_group,
        client, client_node_id, serviceq, test_task_2
    ):
        def run_task(params, expected_status, expected_resources_state):
            params.update({
                "owner": rest_su_session_group,
                "live_time": 0,
                "kill_executor": True,
                "create_empty_resource": True,
            })
            task = self._sdk2_task(test_task_2, params, rest_su_session)
            self._execute_task(
                task.id, rest_su_session, client_node_id,
                180, expected_status, enqueue=True
            )

            for r in rest_su_session.task[task.id].resources.read()["items"]:
                if r["type"] == "TASK_LOGS":
                    assert r["state"] == ctr.State.READY
                else:
                    assert r["state"] == expected_resources_state

        run_task({}, TS.TEMPORARY, ctr.State.NOT_READY)
        run_task({"fail_on_any_error": True}, TS.FAILURE, ctr.State.BROKEN)

    def test__test_sdk2_dependent_resources(
        self, server, rest_su_session, rest_su_session_group,
        client, client_node_id, serviceq, test_task_2, task_manager
    ):
        res = manager_tests._create_real_resource(
            task_manager, parameters={'resource_type': 'TEST_TASK_2_RESOURCE'}
        )
        task_params = {
            "owner": rest_su_session_group,
            "description": u"Test task",
            "live_time": .1,
            "dependent_resource": res.id,
        }
        task = self._sdk2_task(test_task_2, task_params, rest_su_session)
        self._execute_task(
            task.id, rest_su_session, client_node_id,
            180, TS.SUCCESS, enqueue=True
        )
        assert rest_su_session.task[task.id][:]["status"] == TS.SUCCESS

    def test__test_sdk2_on_create_on_save(
        self, server, rest_su_session, rest_su_session_group,
        client, client_node_id, serviceq
    ):
        import sandbox.sdk2.tests

        task_cls = sandbox.sdk2.tests.OnCreateOnSaveTestTask

        task_params = {
            "owner": rest_su_session_group,
            "description": u"Test task",
            "expected_value": 3,
            "expected_disk_space": 400,
        }

        task = self._sdk2_task(task_cls, task_params, rest_su_session)
        self._execute_task(
            task.id, rest_su_session, client_node_id,
            180, TS.SUCCESS, enqueue=True
        )
        task_info = rest_su_session.task[task.id][:]
        assert task_info["status"] == TS.SUCCESS
        assert task_info["output_parameters"]["output_ok"]
        assert task_info["output_parameters"]["on_save_rest_call_failed"]

    def test__test_sdk2_parent_resources(
        self, server, rest_su_session, rest_su_session_group,
        client, client_node_id, serviceq
    ):
        import sandbox.sdk2.tests

        task_cls = sandbox.sdk2.tests.ParentResourcesTestTask

        task_params = {
            "owner": rest_su_session_group,
            "description": u"Test task",
            "create_sub_task": True,
        }

        task = self._sdk2_task(task_cls, task_params, rest_su_session)
        self._execute_task(
            task.id, rest_su_session, client_node_id,
            180, TS.SUCCESS, enqueue=True
        )

        # check resource passed to subtask
        res = list(sandbox.sdk2.Resource.find(task=task, attrs={"test_attr": "0"}).limit(0))
        assert len(res) == 1
        assert res[0].state == ctr.State.READY

        # check resource created from subtask
        res = list(sandbox.sdk2.Resource.find(task=task, attr_name="from_task").limit(0))
        assert len(res) == 1
        assert res[0].state == ctr.State.READY

        # test changed description and tags
        task_info = rest_su_session.task[task.id][:]

        assert task_info["description"] == "New description"
        assert task_info["tags"] == ["NEW_TAG"]

        # tests that failed child task does not mark parent resource as broken
        task_params["fail_test"] = True
        task = self._sdk2_task(task_cls, task_params, rest_su_session)
        self._execute_task(
            task.id, rest_su_session, client_node_id,
            180, TS.SUCCESS, enqueue=True
        )

    def test__test_sdk2_on_enqueue_resource(
        self, server, rest_su_session, rest_su_session_group,
        client, client_node_id, serviceq
    ):
        import sandbox.sdk2.tests

        task_cls = sandbox.sdk2.tests.OnEnqueueResourceTestTask

        task_params = {
            "owner": rest_su_session_group,
            "description": u"Test task",
        }

        task = self._sdk2_task(task_cls, task_params, rest_su_session)
        self._execute_task(
            task.id, rest_su_session, client_node_id,
            180, TS.SUCCESS, enqueue=True
        )

        res = list(sandbox.sdk2.Resource["TEST_TASK_2_RESOURCE"].find(task=task).limit(0))
        assert len(res) == 1
        assert res[0].state == ctr.State.READY

    def test__test_sdk2_task_custom_logs(
        self, server, rest_su_session, rest_su_session_group,
        client, client_node_id, serviceq
    ):
        import sandbox.sdk2.tests
        task_cls = sandbox.sdk2.tests.TaskCustomLogsTestTask

        task_params = {
            "owner": rest_su_session_group,
            "description": u"Test task",
        }

        task = self._sdk2_task(task_cls, task_params, rest_su_session)
        self._execute_task(
            task.id, rest_su_session, client_node_id,
            180, TS.SUCCESS, enqueue=True
        )

        ctx = rest_su_session.task[task.id].context.read()

        # Resources subclassed from TaskLogs are expected to have sources BEFORE they become READY.
        assert ctx.get("non_log_sources") == []
        assert ctx.get("log_sources") == [client_node_id]

    def test__test_sdk2_context(
        self, server, rest_su_session, rest_su_session_group,
        client, client_node_id, serviceq
    ):
        import sandbox.sdk2.tests
        task_cls = sandbox.sdk2.tests.SaveContextTestTask

        task_params = {
            "owner": rest_su_session_group,
            "description": u"Test task",
            "live_time": 30,
            "kill_timeout": 15,
        }
        task = self._sdk2_task(task_cls, task_params, rest_su_session)
        self._execute_task(
            task.id, rest_su_session, client_node_id,
            180, TS.TIMEOUT, enqueue=True
        )
        task_info = rest_su_session.task[task.id][:]
        assert task_info["status"] == TS.TIMEOUT
        assert task_info["output_parameters"]["before_timeout_ok"]

    def test__test_sdk2_expired(
        self, server, rest_su_session, rest_su_session_group,
        client, client_node_id, serviceq
    ):
        import sandbox.sdk2.tests
        task_cls = sandbox.sdk2.tests.ExpiredTestTask

        task_params = {
            "owner": rest_su_session_group,
            "description": u"Test task",
            "expires_on_enqueue": 1,
        }

        task = self._sdk2_task(task_cls, task_params, rest_su_session)
        self._execute_task(
            task.id, rest_su_session, client_node_id,
            180, TS.EXPIRED, enqueue=True
        )

        del task_params["expires_on_enqueue"]
        task_params["expires_on_execute"] = 1

        task = self._sdk2_task(task_cls, task_params, rest_su_session)
        self._execute_task(
            task.id, rest_su_session, client_node_id,
            180, TS.EXPIRED, enqueue=True
        )

    def test__test_sdk2_vault_param(
        self, server, rest_su_session, rest_su_session_group,
        client, client_node_id, serviceq, vault_controller
    ):
        import sandbox.sdk2.tests
        task_cls = sandbox.sdk2.tests.VaultParamTask

        vault_name = "somename"
        vault_data = "some data"
        vault_controller.create(mapping.Vault(
            owner=rest_su_session_group,
            name=vault_name,
            data=vault_data,
        ))

        task_params = {
            "owner": rest_su_session_group,
            "description": u"Test task",
            "vault": vault_name,
            "expected_value": vault_data
        }

        task = self._sdk2_task(task_cls, task_params, rest_su_session)
        self._execute_task(
            task.id, rest_su_session, client_node_id,
            180, TS.SUCCESS, enqueue=True
        )
