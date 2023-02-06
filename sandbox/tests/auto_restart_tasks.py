import datetime as dt
import functools

import pytest

from sandbox.common import itertools as common_itertools
import sandbox.common.types.task as ctt

from sandbox.services import modules
from sandbox.yasandbox import controller
from sandbox.yasandbox.database import mapping


@pytest.fixture
def auto_restart_tasks(server, service_user):
    service = modules.AutoRestartTasks()
    service.oauth_token = service_user
    return service


class TestAutoRestartTasks(object):

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    @pytest.mark.parametrize("sdk", ("sdk1", "sdk2"))
    def test__restart_multiple(self, server, serviceq, auto_restart_tasks, task_manager, rest_session_login,
                               test_task_2, sdk):

        params = {"owner": rest_session_login, "author": rest_session_login}

        task_factories = {
            "sdk1": functools.partial(task_manager.create, "UNIT_TEST", **params),
            "sdk2": functools.partial(test_task_2, None, **params),
        }

        task_ids = []

        for i in xrange(5):
            task = task_factories[sdk]()
            task_ids.append(str(task.id))

            task = controller.TaskWrapper(mapping.Task.objects.with_id(task.id))
            task.set_status(ctt.Status.TEMPORARY, force=True)

        for status in mapping.Task.objects(id__in=task_ids).fast_scalar("execution__status"):
            assert status in ctt.Status.TEMPORARY

        auto_restart_tasks.tick()

        for status in mapping.Task.objects(id__in=task_ids).fast_scalar("execution__status"):
            assert status in ctt.Status.Group.QUEUE

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    def test__restart_valid_session(self, server, serviceq, auto_restart_tasks, task_session, rest_session, test_task_2,
                                    rest_session_login):

        params = {"owner": rest_session_login, "author": rest_session_login}
        task = test_task_2(None, **params)

        task_session(rest_session, task.id, login=rest_session_login)
        task.current = task

        task = controller.TaskWrapper(mapping.Task.objects.with_id(task.id))
        task.set_status(ctt.Status.TEMPORARY, force=True)

        status = mapping.Task.objects.fast_scalar("execution__status").get(id=task.id)
        assert status == ctt.Status.TEMPORARY

        auto_restart_tasks.tick()

        status = mapping.Task.objects.fast_scalar("execution__status").get(id=task.id)
        assert status == ctt.Status.TEMPORARY  # task was not restarted

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    def test__do_not_restart_early(self, server, serviceq, auto_restart_tasks, rest_session_login, test_task_2):

        params = {"owner": rest_session_login, "author": rest_session_login}
        task = test_task_2(None, **params)

        interval = 60  # custom delay to make sure it will not be over during a test run

        mapping.Task.objects.with_id(task.id).update(
            set__execution__time__finished=dt.datetime.utcnow() - dt.timedelta(seconds=interval / 2),
            set__execution__auto_restart__interval=interval,
            set__execution__auto_restart__left=1,
        )

        task = controller.TaskWrapper(mapping.Task.objects.with_id(task.id))
        task.set_status(ctt.Status.TEMPORARY, force=True)

        status = mapping.Task.objects.fast_scalar("execution__status").get(id=task.id)
        assert status == ctt.Status.TEMPORARY

        auto_restart_tasks.tick()

        status = mapping.Task.objects.fast_scalar("execution__status").get(id=task.id)
        assert status == ctt.Status.TEMPORARY  # task was not restarted: too early

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    @pytest.mark.parametrize("sdk", ("sdk1", "sdk2"))
    def test__no_restarts_left(self, server, serviceq, auto_restart_tasks, rest_session_login, test_task_2, sdk,
                               task_manager):

        params = {"owner": rest_session_login, "author": rest_session_login}
        task_factories = {
            "sdk1": functools.partial(task_manager.create, "UNIT_TEST", **params),
            "sdk2": functools.partial(test_task_2, None, **params),
        }

        task = task_factories[sdk]()

        interval = 60  # custom delay to make sure it will not be over during a test run

        mapping.Task.objects.with_id(task.id).update(
            set__execution__auto_restart__interval=interval,
            set__execution__auto_restart__left=2,
        )

        for _ in xrange(3):

            task = controller.TaskWrapper(mapping.Task.objects.with_id(task.id))
            task.set_status(ctt.Status.TEMPORARY, force=True)

            mapping.Task.objects.with_id(task.id).update(
                set__execution__auto_restart__interval=interval,
                set__execution__time__finished=dt.datetime.utcnow() - dt.timedelta(seconds=interval * 3),
            )
            auto_restart_tasks.tick()
            common_itertools.progressive_waiter(
                0, 0.1, 10,
                lambda: mapping.Task.objects.fast_scalar("execution__status").with_id(task.id) != ctt.Status.ENQUEUING
            )

        status = mapping.Task.objects.fast_scalar("execution__status").get(id=task.id)
        assert status == ctt.Status.EXCEPTION  # no restarts left
