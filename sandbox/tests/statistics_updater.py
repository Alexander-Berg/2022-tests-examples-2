import pytest
import random
import datetime as dt

import sandbox.common.utils as utils
import sandbox.common.config as config
import sandbox.yasandbox.controller as controller
import sandbox.yasandbox.database.mapping as mp
import sandbox.yasandbox.services.statistics_updater as updater


class TestStatisticsUpdater:

    _TASK_TYPES = ["TEST_TASK", "UNIT_TEST"]
    ENQUEUED_MINS_AGO_FORMER = 13
    EXECUTING_MINS_AGO_FORMER = 3
    ENQUEUED_MINS_AGO_LATTER = 2
    EXECUTING_MINS_AGO_LATTER = 1

    @classmethod
    def __emulate_task_execution(cls):
        res = []
        save_me = []
        now = dt.datetime.utcnow()
        settings = config.Registry().server.services.statistics_updater
        for task_type in cls._TASK_TYPES:
            eta = []
            history = []
            for x in xrange(2 * settings.history_len + 1):
                doc = mp.Task(type=task_type)
                save_me.append(doc)

                ttl = random.randint(1, 50)
                date = now - dt.timedelta(hours=(x + 1) % 2)
                save_me.append(mp.Audit(
                    task_id=doc.id,
                    status=mp.Task.Execution.Status.PREPARING,
                    date=date - dt.timedelta(seconds=ttl)
                ))

                status = random.choice(
                    updater.StatisticsUpdater.SUCCESS_STATUSES + updater.StatisticsUpdater.ERROR_STATUSES
                )
                save_me.append(mp.Audit(task_id=doc.id, status=status, date=date))
                if x % 2 == 0:
                    continue
                eta.append(ttl)
                suc = int(status in updater.StatisticsUpdater.SUCCESS_STATUSES)
                history.append(suc)
            res.append([task_type, sum(history), utils.percentile(sorted(eta), settings.percentile), history])
        map(lambda item: item.save(validate=False), save_me)
        return res

    @classmethod
    def __emulate_task_consequent_run(cls, task_type, now):
        task = mp.Task(type=task_type)
        # DRAFT, ASSIGNED, PREPARING, FINISHING, and final statuses are omitted here
        enqueue_date = now - dt.timedelta(minutes=cls.ENQUEUED_MINS_AGO_FORMER)
        enqueue_audit = mp.Audit(task_id=task.id, status=mp.Task.Execution.Status.ENQUEUED, date=enqueue_date)
        executing_date = now - dt.timedelta(minutes=cls.EXECUTING_MINS_AGO_FORMER)
        executing_audit = mp.Audit(task_id=task.id, status=mp.Task.Execution.Status.EXECUTING, date=executing_date)
        # e.g. switch to WAIT_TASK and then enqueue again
        enqueue_date = now - dt.timedelta(minutes=cls.ENQUEUED_MINS_AGO_LATTER)
        enqueue_audit2 = mp.Audit(task_id=task.id, status=mp.Task.Execution.Status.ENQUEUED, date=enqueue_date)
        executing_date = now - dt.timedelta(minutes=cls.EXECUTING_MINS_AGO_LATTER)
        executing_audit2 = mp.Audit(task_id=task.id, status=mp.Task.Execution.Status.EXECUTING, date=executing_date)

        to_save = [task, enqueue_audit, executing_audit, enqueue_audit2, executing_audit2]
        map(lambda item: item.save(validate=False), to_save)

    # noinspection PyUnusedLocal
    def test__tasks_weather(self, clean_task_audit, monkeypatch):
        now = dt.datetime.utcnow()
        task_history = self.__emulate_task_execution()
        st_updr = updater.StatisticsUpdater(stopping=lambda: False, logger=None, rwlock=None)
        monkeypatch.setattr(
            st_updr,
            "_date_bounds", lambda _: (now - dt.timedelta(minutes=1), now + dt.timedelta(minutes=1))
        )
        st_updr.save_tasks_weather(st_updr.collect_tasks_weather())
        for task_type, weather, eta, history in task_history:
            ret = mp.Weather.objects(type=task_type).first()
            assert ret is not None
            assert ret.data.history == history
            assert ret.data.weather == weather
            assert ret.data.eta == eta

    # noinspection PyUnusedLocal
    @pytest.mark.parametrize("date_gt_minutes", [2, 4])
    def test__collect_tasks_enqueue_time(self, clean_task_audit, monkeypatch, date_gt_minutes):
        @classmethod
        def mock_report_service_error(cls, comment, thread_name, lock_name=None, additional_recipients=None):
            pass
        now = dt.datetime.utcnow()
        self.__emulate_task_consequent_run("FOO_TASK_TYPE", now)

        upd = updater.StatisticsUpdater(stopping=lambda: False, logger=None, rwlock=None)
        monkeypatch.setattr(controller.Notification, "report_service_error", mock_report_service_error)
        monkeypatch.setattr(
            upd,
            "_date_bounds",
            lambda _: (now - dt.timedelta(minutes=date_gt_minutes), now + dt.timedelta(minutes=1))
        )
        result = upd.collect_tasks_enqueue_time()
        assert "FOO_TASK_TYPE" in result
        expected = self.ENQUEUED_MINS_AGO_LATTER - self.EXECUTING_MINS_AGO_LATTER
        # if 2nd EXECUTING is inside timeframe
        if date_gt_minutes >= self.EXECUTING_MINS_AGO_FORMER:
            expected += self.ENQUEUED_MINS_AGO_FORMER - self.EXECUTING_MINS_AGO_FORMER
        assert result["FOO_TASK_TYPE"] == expected * 60
