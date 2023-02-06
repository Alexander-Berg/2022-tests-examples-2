import mock
import pytest
import random
import datetime as dt

from sandbox.deploy import juggler

import sandbox.common.types.task as ctt

from sandbox.yasandbox import controller
from sandbox.yasandbox.database import mapping

import sandbox.services.modules.task_status_checker


@pytest.fixture
def task_status_checker():
    service = sandbox.services.modules.task_status_checker.TaskStatusChecker()
    # noinspection PyProtectedMember
    service.load_service_state()
    return service


class TestTaskStatusChecker(object):

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session", "clean_task_audit")
    def test__wrong_task_status_notification(self, task_status_checker, monkeypatch, test_task_2):
        monkeypatch.setattr(controller.Notification, "save", mock.Mock())
        task1 = test_task_2(None)
        task1.save()
        task2 = test_task_2(None)
        task2.save()

        task_status_checker.check_audit_consistency()
        assert not controller.Notification.save.called

        now = dt.datetime.utcnow()
        mapping.Task.objects(id=task1.id).update(
            set__execution__status=ctt.Status.STOPPING,
            set__time__updated=now
        )
        mapping.Task.objects(id=task2.id).update(
            set__execution__status=ctt.Status.FINISHING,
            set__time__updated=now
        )

        task_status_checker.check_audit_consistency()
        assert not controller.Notification.save.called

        mapping.Task.objects(id=task1.id).update(
            set__time__updated=now - dt.timedelta(seconds=task_status_checker.MAX_STATUS_SWITCH_DELAY)
        )
        mapping.Task.objects(id=task2.id).update(
            set__time__updated=now - dt.timedelta(seconds=task_status_checker.MAX_STATUS_SWITCH_DELAY)
        )

        task_status_checker.check_audit_consistency()
        assert controller.Notification.save.call_count == 2

        controller.Notification.save.reset_mock()
        task_status_checker.check_audit_consistency()
        assert not controller.Notification.save.called

        task_status_checker.context.pop("sent_warnings")
        mapping.Audit(task_id=task1.id, status=ctt.Status.STOPPING).save()
        task_status_checker.check_audit_consistency()
        assert controller.Notification.save.call_count == 1

        controller.Notification.save.reset_mock()
        task_status_checker.context.pop("sent_warnings")
        mapping.Audit(task_id=task2.id, status=ctt.Status.FINISHING).save()
        task_status_checker.check_audit_consistency()
        assert not controller.Notification.save.called

    def _ensure_check(self, checker, check, ok=False, warn=False, crit=False):
        checker.check_session_consistency()

        assert check.ok.called == ok
        assert check.warning.called == warn
        assert check.critical.called == crit

        check.ok.reset_mock()
        check.warning.reset_mock()
        check.critical.reset_mock()

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session", "clean_task_audit")
    def test__session_consistency_notification(self, task_status_checker, monkeypatch, test_task_2):
        monkeypatch.setattr(controller.Notification, "save", mock.Mock())
        monkeypatch.setattr(juggler.TaskSessionConsistency, "ok", mock.Mock())
        monkeypatch.setattr(juggler.TaskSessionConsistency, "warning", mock.Mock())
        monkeypatch.setattr(juggler.TaskSessionConsistency, "critical", mock.Mock())
        task1 = test_task_2(None)
        task1.save()
        task2 = test_task_2(None)
        task2.save()

        self._ensure_check(task_status_checker, juggler.TaskSessionConsistency, ok=True)

        now = dt.datetime.utcnow()
        mapping.Task.objects(id=task1.id).update(
            set__execution__status=ctt.Status.ENQUEUED,
            set__time__updated=now
        )
        mapping.Task.objects(id=task2.id).update(
            set__execution__status=ctt.Status.FINISHING,
            set__time__updated=now
        )
        self._ensure_check(task_status_checker, juggler.TaskSessionConsistency, ok=True)

        check_delay = task_status_checker.MAX_STATUS_WITHOUT_SESSION_DELAY
        for t in (task1, task2):
            mapping.Task.objects(id=t.id).update(set__time__updated=now - dt.timedelta(seconds=check_delay))

        self._ensure_check(task_status_checker, juggler.TaskSessionConsistency, warn=True)

        session = mapping.OAuthCache(
            task_id=task2.id, created=now - dt.timedelta(seconds=check_delay * 2), ttl=check_delay + 1,
            token="qwerty", login="guest", source="client:",
        ).save()
        self._ensure_check(task_status_checker, juggler.TaskSessionConsistency, ok=True)

        session.ttl = 1
        session.save()
        self._ensure_check(task_status_checker, juggler.TaskSessionConsistency, warn=True)

        mapping.Task.objects(id=task1.id).update(set__execution__status=ctt.Status.PREPARING)
        self._ensure_check(task_status_checker, juggler.TaskSessionConsistency, crit=True)

        mapping.Task.objects(id=task1.id).update(set__execution__status=ctt.Status.TEMPORARY)
        self._ensure_check(task_status_checker, juggler.TaskSessionConsistency, warn=True)

    @pytest.mark.usefixtures("clean_task_audit")
    def test__no_warning_if_tasks_ok(self, task_status_checker, monkeypatch, test_task_2):
        monkeypatch.setattr(juggler.TasksTransientStatuses, "ok", mock.Mock())
        monkeypatch.setattr(juggler.TasksTransientStatuses, "warning", mock.Mock())
        monkeypatch.setattr(juggler.TasksTransientStatuses, "critical", mock.Mock())
        task1 = test_task_2(None)
        task1.save()

        task_status_checker.check_stalled_transient_statuses()

        self._ensure_check(task_status_checker, juggler.TasksTransientStatuses, ok=True)

    @pytest.mark.usefixtures("clean_task_audit")
    def test__check_stalled_transient_statuses(self, task_status_checker, monkeypatch, test_task_2):
        monkeypatch.setattr(juggler.TasksTransientStatuses, "ok", mock.Mock())
        monkeypatch.setattr(juggler.TasksTransientStatuses, "warning", mock.Mock())
        monkeypatch.setattr(juggler.TasksTransientStatuses, "critical", mock.Mock())
        task1 = test_task_2(None)
        task1.save()

        now = dt.datetime.utcnow()
        bad_status = random.choice(task_status_checker.STATUSES_TO_CHECK)
        mapping.Task.objects(id=task1.id).update(
            set__execution__status=bad_status,
            set__time__updated=now - dt.timedelta(seconds=(task_status_checker.MAX_TIME_IN_TRANSIENT_STATUS_CRIT + 1))
        )

        task_status_checker.check_stalled_transient_statuses()

        self._ensure_check(task_status_checker, juggler.TasksTransientStatuses, crit=True)
