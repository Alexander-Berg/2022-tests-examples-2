# coding: utf-8

import pytest
from six.moves import cPickle
import datetime as dt

import sandbox.common.types.notification as ctn
import sandbox.common.types.task as ctt
import sandbox.common.types.scheduler as cts

from sandbox.yasandbox.database import mapping
from sandbox.yasandbox.controller import task as task_controller
from sandbox.yasandbox.api.json import scheduler as scheduler_api


def _task_context(scheduler):
    return cPickle.loads(scheduler.context) if scheduler.context else {}


def _user(login="_test_user"):
    import yasandbox.controller.user as controller

    mapping.User(login=login).save()
    controller.User.validated(login)
    return login


@pytest.fixture()
def test_user():
    return _user()


class TestSchedulerController(object):

    TASK_TYPES = ["TEST_TASK", "TEST_TASK_2"]

    @pytest.mark.parametrize("task_type", TASK_TYPES)
    def test_base_operations1(self, task_type, scheduler_controller, test_user):
        sch1 = scheduler_controller.create(task_type, test_user, test_user)
        sch2 = scheduler_controller.load(sch1.id)
        assert sch1.type == sch2.type
        assert sch1.owner == sch2.owner == test_user
        assert sch1.author == sch2.author == test_user
        assert _task_context(sch1) == _task_context(sch2)

        scheduler_controller.delete(sch1)
        sch3 = scheduler_controller.load(sch1.id)
        assert sch3.status == "DELETED"

    @pytest.mark.parametrize("task_type", TASK_TYPES)
    def test_base_operations2(self, task_type, scheduler_controller, test_user):
        test_user2 = _user("__TEST_USER2")
        sch1 = scheduler_controller.create(task_type, test_user, test_user)
        sch2 = scheduler_controller.create(task_type, test_user2, test_user2)

        sch1.description = "description of test #1"
        sch1.status = "STOPPED"

        task_controller.TaskWrapper(sch1).update_context({"param1": "aaa", "param2": "bbb"}, save=False)

        sch2.description = "description of test #2"
        sch2.status = "STOPPED"
        task_controller.TaskWrapper(sch2).update_context({"param1": 12, "param2": 34, "param3": 56}, save=False)

        scheduler_controller.save(sch1)
        scheduler_controller.save(sch2)

        s1 = scheduler_controller.load(sch1.id)
        s2 = scheduler_controller.load(sch2.id)
        assert sch1.owner == s1.owner
        assert sch2.owner == s2.owner
        assert _task_context(sch1) == _task_context(s1)
        assert _task_context(sch2) == _task_context(s2)

        schedulers = list(mapping.Scheduler.objects(type=task_type).order_by("-id"))

        assert sch1.type == schedulers[1].type
        assert sch1.owner == schedulers[1].owner
        assert _task_context(sch1)
        assert _task_context(sch1) == _task_context(schedulers[1])
        assert sch2.type == schedulers[0].type
        assert sch2.owner == schedulers[0].owner
        assert _task_context(sch2)
        assert _task_context(sch2) == _task_context(schedulers[0])

        assert mapping.Scheduler.objects(type=task_type).count() == 2
        assert mapping.Scheduler.objects(owner=test_user).count() == 1
        assert mapping.Scheduler.objects(owner=test_user2).count() == 1

        scheduler_controller.delete(sch1)
        scheduler_controller.delete(sch2)

        sch_1 = scheduler_controller.load(sch1.id)
        sch_2 = scheduler_controller.load(sch2.id)
        assert sch_1.status == "DELETED"
        assert sch_2.status == "DELETED"

    @pytest.mark.parametrize("task_type", TASK_TYPES)
    def test__get_notification(self, task_type, scheduler_controller, test_user):
        scheduler = scheduler_controller.create(task_type, test_user, test_user)
        address, subject, body = scheduler_controller.get_notification(scheduler)
        assert test_user in address
        assert str(scheduler.id) in subject
        scheduler_controller.delete(scheduler)
        scheduler = scheduler_controller.load(scheduler.id)
        address, subject, body = scheduler_controller.get_notification(scheduler)
        assert "DELETED" in subject

    @pytest.mark.parametrize("task_type", TASK_TYPES)
    def test__scheduler_restore(self, task_type, scheduler_controller, test_user):
        scheduler = scheduler_controller.create(task_type, test_user, test_user)
        restored = scheduler_controller.load(scheduler.id)
        assert scheduler.id == restored.id
        assert scheduler.author == restored.author == test_user
        assert mapping.Scheduler().id == scheduler.id + 1

    @pytest.mark.parametrize("task_type", TASK_TYPES)
    def test__scheduler_state_switch(self, task_type, scheduler_controller, test_user):
        scheduler = scheduler_controller.create(task_type, test_user, test_user)
        scheduler.plan.start_mode = cts.StartMode.IMMEDIATELY
        assert scheduler.status == cts.Status.STOPPED
        scheduler_controller.restart(scheduler)
        assert scheduler.status == cts.Status.WATCHING
        assert scheduler_controller.load(scheduler.id).status == cts.Status.WATCHING

    @pytest.mark.usefixtures("task_controller")
    @pytest.mark.parametrize("task_type", TASK_TYPES)
    def test__scheduler_next_run__weekly_immediately(self, task_type, scheduler_controller, test_user):
        scheduler = scheduler_controller.create(task_type, test_user, test_user)
        scheduler.plan = mapping.Scheduler.Plan(
            repetition=cts.Repetition.WEEKLY,
            days_of_week=127,
        )
        tomorrow = dt.datetime.utcnow() + dt.timedelta(days=1)
        scheduler_controller.restart(scheduler)
        assert mapping.Task.objects(scheduler=scheduler.id).count() == 1
        assert tomorrow <= scheduler.time.next_run <= tomorrow + dt.timedelta(minutes=1)

    @pytest.mark.parametrize("task_type", TASK_TYPES)
    def test__scheduler_task_creation(self, task_type, scheduler_controller, test_user):
        scheduler = scheduler_controller.create(task_type, test_user, test_user)

        custom_fields = {"go_to_state": "EXCEPTION"}
        notification = {"statuses": ["EXCEPTION"], "transport": "email", "recipients": ["foobar"]}

        scheduler_api.Scheduler._update_scheduler(
            scheduler,
            {
                "task": {
                    "custom_fields": [{"name": n, "value": v} for n, v in custom_fields.items()],
                    "notifications": [notification],
                }
            },
        )
        scheduler.reload()

        task = task_controller.TaskWrapper(scheduler_controller.create_new_task(scheduler))
        for field_name, field_value in custom_fields.items():
            assert task.input_parameters_values.get(field_name) == field_value

        assert len(task.model.notifications) == 1
        n0 = task.model.notifications[0]
        assert n0.statuses == notification["statuses"]
        assert n0.transport == notification["transport"]
        assert n0.recipients == notification["recipients"]

    def test__scheduler_next_run(self, scheduler_controller, test_user):
        scheduler = scheduler_controller.create(self.TASK_TYPES[0], test_user, test_user)
        now = dt.datetime.utcnow()
        now = now - dt.timedelta(microseconds=now.microsecond)
        start_time = now - dt.timedelta(days=4, hours=6, minutes=3)
        scheduler.plan = mapping.Scheduler.Plan(
            start_mode=cts.StartMode.IMMEDIATELY,
            repetition=cts.Repetition.INTERVAL,
            interval=60 * 60,
            start_time=start_time,
        )

        next_run = scheduler_controller.get_next_task_creation_time(scheduler, manual=True)
        assert now <= next_run < now + dt.timedelta(seconds=2)

        scheduler.plan.start_mode = cts.StartMode.SET

        next_run = scheduler_controller.get_next_task_creation_time(scheduler)
        assert next_run == now - dt.timedelta(minutes=3) + dt.timedelta(seconds=scheduler.plan.interval)

        task_model = scheduler_controller.create_new_task(scheduler, enqueue_task=False)
        task_start_time = start_time + dt.timedelta(days=2, hours=2, minutes=20)
        task_model.time.created = task_model.time.updated = task_start_time
        task_model.execution.status = ctt.Status.FAILURE
        task_model.save()

        next_run = scheduler_controller.get_next_task_creation_time(scheduler)
        assert next_run == now - dt.timedelta(minutes=3) + dt.timedelta(seconds=scheduler.plan.interval)

        scheduler.plan.retry = cts.Retry.INTERVAL
        scheduler.plan.retry_interval = 5 * 60

        next_run = scheduler_controller.get_next_task_creation_time(scheduler)
        assert next_run == task_start_time + dt.timedelta(seconds=scheduler.plan.retry_interval)

        next_run = scheduler_controller.get_next_task_creation_time(scheduler, manual=True)
        assert next_run == now - dt.timedelta(minutes=3) + dt.timedelta(seconds=scheduler.plan.interval)

        scheduler.plan.repetition = cts.Repetition.WEEKLY
        scheduler.plan.days_of_week = 127  # all days

        next_run = scheduler_controller.get_next_task_creation_time(scheduler)
        assert next_run == task_start_time + dt.timedelta(seconds=scheduler.plan.retry_interval)

        next_run = scheduler_controller.get_next_task_creation_time(scheduler, manual=True)
        assert next_run == now + dt.timedelta(days=1) - dt.timedelta(hours=6, minutes=3)

        scheduler.plan.retry = cts.Retry.NO

        next_run = scheduler_controller.get_next_task_creation_time(scheduler)
        assert next_run == now + dt.timedelta(days=1) - dt.timedelta(hours=6, minutes=3)

    def test__scheduler__juggler_notification_trigger(self, scheduler_controller, test_user):
        scheduler = scheduler_controller.create('TEST_TASK', test_user, test_user)

        notification = {
            "statuses": [cts.Status.DELETED],
            "transport": ctn.Transport.JUGGLER,
            "recipients": ["host=test.host&service=test_service"],
            "juggler_tags": ["test_tag"],
        }
        scheduler_api.Scheduler._update_scheduler(
            scheduler,
            {
                "scheduler_notifications": [notification],
            },
        )
        scheduler_controller.delete(scheduler)

        triggered_notifications = mapping.Notification.objects()
        assert len(triggered_notifications) == 1
        triggered_notification = triggered_notifications[0]
        assert triggered_notification.transport == notification["transport"]
        assert triggered_notification.send_to == notification["recipients"]
        assert triggered_notification.juggler_tags == notification["juggler_tags"]
