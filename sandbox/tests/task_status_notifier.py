import datetime as dt

import mock
import pytest

import sandbox.common.types.notification as ctn
import sandbox.common.types.task as ctt
from sandbox.services.modules import task_status_notifier as tsn
from sandbox.yasandbox import controller
from sandbox.yasandbox.database import mapping

TS = ctt.Status

STATUSES = [TS.DRAFT, TS.ENQUEUING, TS.ENQUEUED, TS.ASSIGNED, TS.PREPARING, TS.EXECUTING, TS.FINISHING]

EMAILS = {"email1", "email2"}


GROUPS = {
    "G1": {
        "email": "",
        "users": ["group1_user1", "group1_user2"]
    },
    "G2": {
        "email": "group2_email",
        "users": ["group2_user1", "group2_user2"]
    },
    "G3": {
        "email": "group3_email1 group3_email2",
        "users": ["group3_user1", "group3_user2"]
    }
}

GROUPS_EMAILS = {"group3_email1", "group3_email2", "group2_email", "group1_user1", "group1_user2"}


@pytest.fixture()
def initialize_groups(initialize, user_controller, group_controller):

    for group_name, group_info in GROUPS.iteritems():
        group_users = group_info["users"]

        for login in group_users:
            user_controller.Model(login=login).save()
            user_controller.validated(login)

        group_controller.create(group_controller.Model(name=group_name, users=group_users, email=group_info["email"]))


class TestTaskStatusNotifier(object):

    def test__no_state(self, task_status_notifier):
        notifier = tsn.Notifier(task_status_notifier)

        with pytest.raises(AssertionError):
            notifier.notify()

        with pytest.raises(AssertionError):
            notifier.collect_garbage()

    def test__stopping(self, task_status_notifier):

        with tsn.Notifier(task_status_notifier) as notifier:
            raise notifier.Stopping  # no exception is expected outside context manager

    def test__exception(self, task_status_notifier):

        with pytest.raises(ValueError):
            with tsn.Notifier(task_status_notifier):
                raise ValueError

    def test__stopping_while_working(self, notification_trigger_controller, task_status_notifier):

        trigger_model = notification_trigger_controller.Model

        trigger_model(source=40000, statuses=STATUSES, transport=ctn.Transport.EMAIL, recipients=EMAILS).save()

        with tsn.Notifier(task_status_notifier) as notifier:
            notifier._service._stop_requested.set()
            notifier.notify()  # no exception is expected outside context manager

        with tsn.Notifier(task_status_notifier) as notifier:
            notifier._service._stop_requested.set()
            notifier.collect_garbage()  # no exception is expected outside context manager

    def test__save_context(self, task_status_notifier):

        with tsn.Notifier(task_status_notifier) as notifier:

            st = dt.datetime.utcnow().replace(microsecond=0) - dt.timedelta(hours=42, minutes=42)
            ids = {42, 43}

            notifier.state.last_check_time = st
            notifier.state.last_gc_time = st
            notifier.state.checked_audit_ids = ids

            notifier.save_context()

            task_status_notifier_model = mapping.Service.objects.with_id(task_status_notifier.name)

            assert task_status_notifier_model.context["last_check_time"] == st
            assert task_status_notifier_model.context["last_gc_time"] == st
            assert set(task_status_notifier_model.context["checked_audit_ids"]) == ids

    def test__save_context_on_exit(self, task_status_notifier):

        with tsn.Notifier(task_status_notifier) as notifier:
            time_before = dt.datetime.utcnow().replace(microsecond=0) - dt.timedelta(hours=42, minutes=42)
            ids = {42, 43}

            notifier.state.last_check_time = time_before
            notifier.state.last_gc_time = time_before
            notifier.state.checked_audit_ids = ids

        task_status_notifier_model = mapping.Service.objects.with_id(task_status_notifier.name)

        assert task_status_notifier_model.context["last_check_time"] == time_before
        assert task_status_notifier_model.context["last_gc_time"] == time_before
        assert set(task_status_notifier_model.context["checked_audit_ids"]) == ids

    def test__gc_non_existent(self, task_status_notifier, notification_trigger_controller):

        trigger_model = notification_trigger_controller.Model

        trigger_ids = []

        for i, st in enumerate(STATUSES):
            tr = trigger_model(source=40000 + i, statuses=[st], transport=ctn.Transport.EMAIL, recipients=EMAILS).save()
            trigger_ids.append(tr.id)

        with tsn.Notifier(task_status_notifier) as notifier:
            # Prevents flakiness when creation date of triggers is too close to start time
            notifier._start_time += dt.timedelta(minutes=1)
            notifier.collect_garbage()

        assert not trigger_model.objects.filter(id__in=trigger_ids).count()

    def test__gc_idle(self, task_status_notifier, task_manager, notification_trigger_controller):

        trigger_model = notification_trigger_controller.Model

        task = task_manager.create("UNIT_TEST", owner="user", author="user")
        task.set_status(TS.ENQUEUING)

        # Prepare triggers
        trigger_ids = []
        for st in STATUSES:
            tr = trigger_model(source=task.id, statuses=[st], transport=ctn.Transport.EMAIL, recipients=EMAILS).save()
            trigger_ids.append(tr.id)

        # Case 1, task is active and recent: triggers must NOT be collected
        task.set_status(TS.ENQUEUING)

        with tsn.Notifier(task_status_notifier) as notifier:
            notifier.collect_garbage()

        assert trigger_model.objects.filter(id__in=trigger_ids).count()

        # Case 2, task is idle for a long time: triggers MUST be collected
        task.set_status(TS.EXCEPTION)
        mapping.Task.objects.filter(id=task.id).update_one(set__time__updated=dt.datetime(2017, 1, 1))

        with tsn.Notifier(task_status_notifier) as notifier:
            notifier.collect_garbage()

        assert not trigger_model.objects.filter(id__in=trigger_ids).count()

    def test__collect_after_notify(self, task_status_notifier, task_manager, notification_trigger_controller):

        trigger_model = notification_trigger_controller.Model

        task = task_manager.create("UNIT_TEST", owner="user", author="user")

        # Prepare triggers
        trigger_ids = []
        for st in (TS.DRAFT, TS.EXCEPTION, TS.ENQUEUED):
            tr = trigger_model(source=task.id, statuses=[st], transport=ctn.Transport.EMAIL, recipients=EMAILS).save()
            trigger_ids.append(tr.id)

        task.set_status(TS.ENQUEUING)
        task.set_status(TS.EXCEPTION)

        with tsn.Notifier(task_status_notifier) as notifier:
            notifier.notify()

        # Used triggers are removed while unused ones are still there
        assert list(trigger_model.objects.filter(id__in=trigger_ids).scalar("statuses")) == [["ENQUEUED"]]

    @pytest.mark.parametrize(("recipients", "send_to"), [(EMAILS, EMAILS), (list(GROUPS), GROUPS_EMAILS)])
    def test_notify(
            self, task_status_notifier, task_manager, notification_trigger_controller, monkeypatch, initialize_groups,
            recipients, send_to
    ):

        trigger_model = notification_trigger_controller.Model

        task = task_manager.create("UNIT_TEST", owner="user", author="user")

        trigger_model(source=task.id, statuses=STATUSES, transport=ctn.Transport.EMAIL, recipients=recipients).save()

        for status in STATUSES[1:]:
            task.set_status(status)

        mock_controller = mock.Mock()
        monkeypatch.setattr(controller.Notification, "save", mock_controller)

        with tsn.Notifier(task_status_notifier) as notifier:
            notifier.notify()

        assert len(mock_controller.mock_calls) == len(STATUSES)
        assert all([set(kwargs["send_to"]) == send_to for _, args, kwargs in mock_controller.mock_calls])

    @pytest.mark.parametrize(
        ("last_gc", "gc_call_count"),
        [
            (lambda: dt.datetime(2017, 1, 1), 1),
            (lambda: dt.datetime.utcnow(), 0),
        ]
    )
    def test__tick(self, task_status_notifier, monkeypatch, last_gc, gc_call_count):

        notify_mock = mock.Mock()
        monkeypatch.setattr(tsn.Notifier, "notify", notify_mock)

        gc_mock = mock.Mock()
        monkeypatch.setattr(tsn.Notifier, "collect_garbage", gc_mock)

        task_status_notifier.tick_once_with_context({
            "last_check_time": dt.datetime(2017, 1, 1),
            "last_gc_time": last_gc(),
            "checked_audit_ids": set()
        })

        assert notify_mock.call_count == 1
        assert gc_mock.call_count == gc_call_count
