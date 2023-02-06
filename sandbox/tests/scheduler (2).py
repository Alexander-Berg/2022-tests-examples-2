import pytest
import datetime as dt

import sandbox.common.types.task as ctt
import sandbox.common.types.scheduler as cts

from sandbox.yasandbox import controller
from sandbox.services.modules import scheduler
from sandbox.yasandbox.database import mapping


@pytest.fixture(autouse=True)
def mock_abc_validation(monkeypatch):
    def validate_abc(*args, **kwargs):
        return True
    monkeypatch.setattr(controller.Group, 'validate_abc', validate_abc)


@pytest.fixture()
def test_user():
    login = "_test_user"
    mapping.User(login=login).save()
    controller.user.User.validated(login)
    return login


@pytest.fixture()
def test_owner(group_controller, test_user):
    group_name = "_TEST_GROUP"
    group_mockup = mapping.Group(name=group_name, users=[test_user], email="mail")
    group_controller.create(group_mockup)
    return group_name


@pytest.fixture()
def valid_scheduler_list(test_user, test_owner):
    return (
        ("TEST_TASK_2", test_user, test_user),
        ("TEST_TASK_2", test_owner, test_user),
    )


@pytest.fixture()
def invalid_scheduler_list(test_user, test_owner):
    TEST_BAD_USER = "user_does_not_exist"
    TEST_BAD_OWNER = "owner_does_not_exist"
    return (
        ("TEST_TASK_2", TEST_BAD_USER, test_user),
        ("TEST_TASK_2", TEST_BAD_OWNER, test_user),
        ("TEST_TASK_2", test_user, TEST_BAD_USER),
        ("TEST_TASK_2", TEST_BAD_USER, TEST_BAD_USER),
        ("TEST_TASK_2", test_owner, TEST_BAD_USER),
    )


called = {}


def calltracker(func):
    def wrapper(*args, **kwargs):
        print(called)
        called[func.__name__] = called[func.__name__] + 1 if func.__name__ in called else 1
        return func(*args, **kwargs)
    return wrapper


def _patch_scheduler(s, blink=0, failed=0):
    s.blink_notification_interval = dt.timedelta(seconds=blink)
    s.notification_interval = dt.timedelta(seconds=failed)
    s._revival_message = calltracker(s._revival_message)
    s._task_fail_message = calltracker(s._task_fail_message)
    return s


class TestSchedulerModule(object):

    def test__check_author_to_owner_coherence(
        self, scheduler_controller, valid_scheduler_list, invalid_scheduler_list
    ):
        valid_scheds = [scheduler_controller.create(*sched) for sched in valid_scheduler_list]
        invalid_scheds = [scheduler_controller.create(*sched) for sched in invalid_scheduler_list]
        mapping.Scheduler.objects().update(set__status=cts.Status.WATCHING)

        scheduler.Scheduler().check_author_to_owner_coherence()
        scheds = dict(mapping.Scheduler.objects().fast_scalar("id", "status"))

        # all bad schedulers are stopped
        for sched in invalid_scheds:
            assert sched.id in scheds and scheds[sched.id] == cts.Status.STOPPED
        # all good schedulers continue to work
        for sched in valid_scheds:
            assert sched.id in scheds and scheds[sched.id] != cts.Status.STOPPED

    def test__check_not_send_message_on_task_ok(self, scheduler_controller, test_task_2, test_user, test_owner):
        sched = scheduler_controller.create("TEST_TASK_2", test_user, test_owner)
        task = test_task_2(None)
        mapping.Task.objects(id=task.id).update(
            set__time__updated=dt.datetime.utcnow() + dt.timedelta(1),
            set__scheduler=sched.id,
            set__execution__status=ctt.Status.FAILURE
        )

        # task ok, last_notification is in the past
        sched_cls = _patch_scheduler(scheduler.Scheduler(), 100, 100)
        mapping.Scheduler.objects(id=sched.id).update(
            set__last_notification_time=dt.datetime.utcnow()
        )
        sched_cls._process_scheduler(sched.id)
        assert not called
        called.clear()

    def test__check_not_send_message_on_task_blink(self, scheduler_controller, test_task_2, test_user, test_owner):
        sched = scheduler_controller.create("TEST_TASK_2", test_user, test_owner)
        task = test_task_2(None)
        mapping.Task.objects(id=task.id).update(
            set__time__updated=dt.datetime.utcnow(),
            set__scheduler=sched.id,
            set__execution__status=ctt.Status.FAILURE
        )

        # task ok, last_notification is in the future, blink is not over
        sched_cls = _patch_scheduler(scheduler.Scheduler(), 100, 100)
        mapping.Scheduler.objects(id=sched.id).update(
            set__last_notification_time=dt.datetime.utcnow() + dt.timedelta(hours=100)
        )
        sched_cls._process_scheduler(sched.id)
        assert not called
        called.clear()

    def test__check_send_message_on_task_revival(self, scheduler_controller, test_task_2, test_user, test_owner):
        sched = scheduler_controller.create("TEST_TASK_2", test_user, test_owner)
        task = test_task_2(None)
        mapping.Task.objects(id=task.id).update(
            set__time__updated=dt.datetime.utcnow(),
            set__scheduler=sched.id,
            set__execution__status=ctt.Status.FAILURE
        )

        # task ok, last_notification is in the future, blink is over
        sched_cls = _patch_scheduler(scheduler.Scheduler(), 0, 0)
        mapping.Scheduler.objects(id=sched.id).update(
            set__last_notification_time=dt.datetime.utcnow() + dt.timedelta(hours=100)
        )
        sched_cls._process_scheduler(sched.id)
        assert "_revival_message" in called
        called.clear()

    def test__check_send_message_on_task_fail(self, scheduler_controller, test_task_2, test_user, test_owner):
        sched = scheduler_controller.create("TEST_TASK_2", test_user, test_owner)
        task = test_task_2(None)
        mapping.Task.objects(id=task.id).update(
            set__time__updated=dt.datetime.utcnow(),
            set__scheduler=sched.id,
            set__execution__status=ctt.Status.SUCCESS
        )

        # task fail, last_notification is in the past, blink is over
        sched_cls = _patch_scheduler(scheduler.Scheduler(), 0, 100)
        mapping.Scheduler.objects(id=sched.id).update(
            set__last_notification_time=dt.datetime.utcnow() - dt.timedelta(hours=100)
        )
        sched_cls._monitor_task_on_failed_start(controller.Scheduler.load(sched.id))
        assert "_task_fail_message" in called
        called.clear()

    def test__check_not_send_message_on_task_fail_blink(
        self, scheduler_controller, test_task_2, test_user, test_owner
    ):
        sched = scheduler_controller.create("TEST_TASK_2", test_user, test_owner)
        task = test_task_2(None)
        mapping.Task.objects(id=task.id).update(
            set__time__updated=dt.datetime.utcnow(),
            set__scheduler=sched.id,
            set__execution__status=ctt.Status.SUCCESS
        )

        # task fail, last_notification is in the future, blink is not over
        sched_cls = _patch_scheduler(scheduler.Scheduler(), 100, 100)
        mapping.Scheduler.objects(id=sched.id).update(
            set__last_notification_time=dt.datetime.utcnow() - dt.timedelta(1),
        )
        sched_cls._monitor_task_on_failed_start(controller.Scheduler.load(sched.id))
        assert not called
        called.clear()

    def test__check_not_send_message_on_task_fail_wait_next(
        self, scheduler_controller, test_task_2, test_user, test_owner
    ):
        sched = scheduler_controller.create("TEST_TASK_2", test_user, test_owner)
        task = test_task_2(None)
        mapping.Task.objects(id=task.id).update(
            set__time__updated=dt.datetime.utcnow(),
            set__scheduler=sched.id,
            set__execution__status=ctt.Status.SUCCESS
        )

        # task fail, last_notification is in the future, blink is not over
        sched_cls = _patch_scheduler(scheduler.Scheduler(), 0, 100)
        mapping.Scheduler.objects(id=sched.id).update(
            set__last_notification_time=dt.datetime.utcnow() + dt.timedelta(hours=100),
        )
        sched_cls._monitor_task_on_failed_start(controller.Scheduler.load(sched.id))
        assert not called
        called.clear()
