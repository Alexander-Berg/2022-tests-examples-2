import random
import datetime as dt

import mock
import pytest

from sandbox import sdk2
from sandbox.sdk2 import internal as sdk2_internal
from sandbox import common
from sandbox.agentr import types as atypes


@pytest.mark.agentr
class TestMetadataStorage(object):
    def test__fileserver_meta(self, agentr_service, agentr_session_maker, test_task_2):
        # the call to a non-existent task's command set doesn't fail
        assert agentr_service.fileserver_meta[0] is None

        with pytest.raises(NotImplementedError):
            agentr_service.fileserver_meta[0] = {}

        task = test_task_2(None)
        agentr_session = agentr_session_maker(task, 1)

        meta = atypes.FileServerMeta(
            ps_command="1",
            shell_command="2",
            cgroup="3",
            attach_command="4",
            pid=5,
        )

        # per-task metadata is set up and read successfully
        agentr_session.fileserver_meta = meta
        assert agentr_session.fileserver_meta == meta
        # on the contrary, general-purpose connection not tied to a task requires an identifier
        assert agentr_service.fileserver_meta[task.id] == meta

    def test__progress_meter_call_count(self, agentr_service, agentr_session_maker, test_task_2, monkeypatch):
        assert agentr_service.progress_meta.by_task(0) is None

        with pytest.raises(NotImplementedError):
            agentr_service.progress_meta.by_task()
        with pytest.raises(NotImplementedError):
            agentr_service.progress_meta.insert("whatever", {"abc": "def"})
        with pytest.raises(NotImplementedError):
            agentr_service.progress_meta.delete("uuid")

        # Can't call it outside of executing task's context (has to be sdk2, too).
        # This should produce something along the lines of "'NoneType' object has no attribute 'id'",
        # because sdk2.Task.current is not set yet
        with pytest.raises(AttributeError):
            sdk2.helpers.ProgressMeter("test")

        task = test_task_2(None)

        # oh boy, here we go
        monkeypatch.setattr(type(sdk2_internal.task.Task), "current", task)
        monkeypatch.setattr(sdk2.Task, "current", task)
        task.agentr = agentr_session_maker(task, 1)

        with mock.patch.object(task.agentr.progress_meta, "insert") as insert:
            meter = sdk2.helpers.ProgressMeter("test")
            assert insert.call_count == 0  # by default, nothing happens

            with mock.patch.object(meter, "UPDATE_PERIOD", dt.timedelta(seconds=3600)):
                with meter:
                    assert insert.call_count == 1  # instant update on first __enter__, no matter what
                    meter.add(10)
                    assert insert.call_count == 1

            updates = 10
            with mock.patch.object(meter, "UPDATE_PERIOD", dt.timedelta(seconds=0)):
                with meter:
                    assert insert.call_count == 2  # instant update (due to timedelta == 0)
                    for update_no in xrange(1, updates + 1):
                        meter.add(10)
                        assert insert.call_count == 2 + update_no

    def test__progress_meter_interaction(self, agentr_service, agentr_session_maker, test_task_2, monkeypatch):
        task = test_task_2(None)
        monkeypatch.setattr(type(sdk2_internal.task.Task), "current", task)
        monkeypatch.setattr(sdk2.Task, "current", task)
        task.agentr = agentr_session_maker(task, 1)

        monkeypatch.setattr(sdk2.helpers.ProgressMeter, "UPDATE_PERIOD", dt.timedelta(seconds=0))

        with sdk2.helpers.ProgressMeter("Running imaginary tests", minval=2, maxval=5) as meter:
            assert task.agentr.progress_meta.by_task()[0] == meter.current
            for _ in xrange(3):
                meter.add(1)
                assert task.agentr.progress_meta.by_task() == [meter.current]

            def formatter(m):
                return "{} items".format(m)

            with sdk2.helpers.ProgressMeter("Creating fixtures", maxval=100, formatter=formatter) as inner_meter:
                for _ in xrange(100):
                    inner_meter.add(1)
                    assert task.agentr.progress_meta.by_task() == [meter.current, inner_meter.current]

            # meters are removed from AgentR's database on scope exit
            assert task.agentr.progress_meta.by_task() == [meter.current]

        meters = [
            (
                dt.datetime.utcnow() + dt.timedelta(seconds=random.randint(1, 1000)),
                sdk2.helpers.ProgressMeter("Woop", maxval=i)
            )
            for i in xrange(11)
        ]
        for fake_start_time, meter in meters:
            meter.start_time = common.api.DateTime.encode(fake_start_time)

        # gonna cheat a little to avoid having 10 "with" blocks
        for _, meter in meters:
            meter.__enter__()

        expected_order = [meter.current for _, meter in sorted(meters)]
        assert task.agentr.progress_meta.by_task() == expected_order

        for _, meter in meters:
            meter.__exit__()

        assert task.agentr.progress_meta.by_task() is None

        new_task = test_task_2(None)
        monkeypatch.setattr(type(sdk2_internal.task.Task), "current", new_task)
        monkeypatch.setattr(sdk2.Task, "current", new_task)
        new_task.agentr = agentr_session_maker(new_task, 1)

        with sdk2.helpers.ProgressMeter("Running imaginary tests", minval=2, maxval=5) as meter:
            meter.add(2)
            assert len(new_task.agentr.progress_meta.by_task()) == 1

            # this should drop respective meters from agentr's database due to "ON DELETE CASCADE" trigger
            new_task.agentr.finished()
            assert new_task.agentr.progress_meta.by_task() is None
