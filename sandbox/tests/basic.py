# coding: utf-8
import os
import stat
import uuid
import shutil
import hashlib
import logging
import tarfile
import threading as th

import py
import yaml
import pytest
import requests

import api.copier

from sandbox import common
import sandbox.common.types.client as ctc
import sandbox.common.types.task as ctt
import sandbox.common.types.misc as ctm
import sandbox.common.types.resource as ctr

import sandbox.common.joint.errors

from sandbox.agentr import utils
from sandbox.agentr import types
from sandbox.agentr import errors
from sandbox.agentr import client

from sandbox.yasandbox import controller as ctrl
from sandbox.yasandbox.manager import tests as manager_tests


class BaseTestSuit(object):
    NEW_LAYOUT = False

    @classmethod
    def _real_resource(
        cls, tmpdir, task_manager, resource_manager, task, dir=True, keep_src=False, content=None, **kwargs
    ):
        res = manager_tests._create_resource(task_manager, task=task, create_logs=False, parameters=kwargs)
        src = py.path.local(tmpdir).join(res.file_name)
        content = content or uuid.uuid4().hex
        if dir:
            src.ensure(dir=1)
            src.join("file").write(content)
        else:
            src.ensure(file=1)
            src.write(content)

        job = api.copier.Copier().createExEx
        job = job([res.file_name], cwd=tmpdir) if cls.NEW_LAYOUT else job([src.basename], cwd=src.dirname)
        res.skynet_id = job.wait().resid()
        res.size = common.fs.check_resource_data(str(src))
        res.file_md5 = "" if dir else hashlib.md5(content).hexdigest()
        resource_manager.update(res)
        if not keep_src:
            # AgentR currently determines resource existence on a host by file existence
            py.path.local(res.abs_path()).remove()
        return res, src

    @pytest.mark.usefixtures("rest_su_session", "s3_simulator")
    def test__cleanup(
        self,
        agentr, rest_session, rest_session_login, task_session, client_manager, task_manager, resource_manager, tmpdir
    ):
        manager_tests._create_client(client_manager, common.config.Registry().this.id)
        task = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.EXECUTING, author=rest_session_login
        )

        deleted_res, _ = self._real_resource(
            tmpdir, task_manager, resource_manager, task,
            resource_type="TEST_TASK_RESOURCE", resource_filename="dir1", resource_desc="Deleted resource"
        )
        removable_res, src = self._real_resource(
            tmpdir, task_manager, resource_manager, task,
            resource_type="TEST_TASK_RESOURCE", resource_filename="dir2", resource_desc="Many sources"
        )
        ctrl.Resource.hard_add_host(removable_res.id, "source1")
        ctrl.Resource.hard_add_host(removable_res.id, "source2")
        unremovable_res, src = self._real_resource(
            tmpdir, task_manager, resource_manager, task,
            resource_type="TEST_TASK_RESOURCE", resource_filename="dir3", resource_desc="Single source"
        )

        token = task_session(rest_session, task.id, rest_session_login)
        agentr.call("task_session", token, 1).wait()
        assert py.path.local(agentr.call("resource_sync", deleted_res.id).wait()).check(dir=1)
        assert py.path.local(agentr.call("resource_sync", removable_res.id).wait()).check(dir=1)
        assert py.path.local(agentr.call("resource_sync", unremovable_res.id).wait()).check(dir=1)

        assert agentr.call("resource_meta", deleted_res.id).wait()
        assert agentr.call("resource_meta", removable_res.id).wait()
        assert agentr.call("resource_meta", unremovable_res.id).wait()
        agentr.call("task_finished").wait()

        deleted_res.state = ctr.State.DELETED
        resource_manager.update(deleted_res)

        removable_but_locked_res, src = self._real_resource(
            tmpdir, task_manager, resource_manager, task,
            resource_type="TEST_TASK_RESOURCE", resource_filename="dir4", resource_desc="Many sources"
        )
        ctrl.Resource.hard_add_host(removable_but_locked_res.id, "source1")
        ctrl.Resource.hard_add_host(removable_but_locked_res.id, "source2")

        agentr.call("task_session", token, 2).wait()
        assert py.path.local(agentr.call("resource_sync", removable_but_locked_res.id).wait()).check(dir=1)
        assert agentr.call("resource_meta", removable_but_locked_res.id).wait()

        cleanup = types.CleanupResult(*agentr.call("cleanup").wait())
        assert cleanup == types.CleanupResult(ctc.RemovableResources.DELETED, 1, 1)
        assert not agentr.call("resource_meta", deleted_res.id).wait()
        assert agentr.call("resource_meta", removable_res.id).wait()
        assert agentr.call("resource_meta", unremovable_res.id).wait()
        assert agentr.call("resource_meta", removable_but_locked_res.id).wait()

        cleanup = types.CleanupResult(*agentr.call("cleanup").wait())
        assert cleanup == types.CleanupResult(ctc.RemovableResources.EXTRA, 1, 1)
        assert not agentr.call("resource_meta", deleted_res.id).wait()
        assert not agentr.call("resource_meta", removable_res.id).wait()
        assert agentr.call("resource_meta", unremovable_res.id).wait()
        assert agentr.call("resource_meta", removable_but_locked_res.id).wait()

        agentr.call("task_finished").wait()

        agentr.call("task_session", token, 3).wait()
        cleanup = types.CleanupResult(*agentr.call("cleanup").wait())
        assert cleanup == types.CleanupResult(ctc.RemovableResources.EXTRA, 1, 1)
        assert agentr.call("resource_meta", unremovable_res.id).wait()
        assert not agentr.call("resource_meta", removable_but_locked_res.id).wait()

        assert not agentr.call("cleanup").wait()
        agentr.call("task_finished").wait()
        # Test cleanup service command without session
        agentr.call("cleanup").wait()


@pytest.mark.agentr
class TestBasic(BaseTestSuit):
    @staticmethod
    def _task_dir_chmod(node, allow_write=True):
        nodes = [node]
        for i in range(3):
            node = py.path.local(node.dirname)
            nodes.append(node)
        for node in reversed(nodes):
            if allow_write:
                node.ensure(dir=1)
                node.chmod(node.stat().mode | stat.S_IWUSR)
            elif node.check():
                node.chmod(node.stat().mode & ~stat.S_IWUSR)

    def test__ping(self, agentr):
        agentr.ping()  # Perform protocol ping
        assert agentr.call("ping", 42).wait() == 42  # Call server method named "ping"

    def test__session(self, agentr, rest_session, rest_session_login, task_manager, task_session):
        task = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.DRAFT, author=rest_session_login
        )
        agentr.call("freeze").wait()
        agentr.call("ease").wait()
        agentr.call("freeze").wait()
        token = task_session(rest_session, task.id, rest_session_login)
        df = types.DiskSpaceInfo(*agentr.call("df").wait())
        agentr.call("task_session", token, 1, 57573434).wait()
        df2 = types.DiskSpaceInfo(*agentr.call("df").wait())
        assert not df.locked and df2.locked == 57573434
        with pytest.raises(errors.TaskInProgress):
            agentr.call("ease").wait()
        agentr.call("task_session", token, 1).wait()
        assert types.DiskSpaceInfo(*agentr.call("df").wait()).locked == 57573434
        agentr.stop()  # Disconnect explicitly instead of finishing task session.
        with pytest.raises(errors.TaskInProgress):
            agentr.call("ease").wait()
        with pytest.raises(errors.NoTaskSession):
            agentr.call("task_finished").wait()
        agentr.call("task_session", token, 1).wait()
        agentr.call("task_finished").wait()
        agentr.call("ease").wait()

    def test__register_executor(self, agentr, rest_session, rest_session_login, task_manager, task_session):
        task = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.DRAFT, author=rest_session_login
        )
        token = task_session(rest_session, task.id, rest_session_login)
        agentr.call("task_session", token, 1).wait()
        agentr.call("register_executor").wait()
        assert agentr.call("executor_pid_getter").wait() == os.getpid()

    @pytest.mark.usefixtures("s3_simulator")
    def test__resource_create(self, agentr, rest_session, rest_session_login, task_manager, task_session):
        task = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.DRAFT, author=rest_session_login
        )
        token = task_session(rest_session, task.id, rest_session_login)
        agentr.call("task_session", token, 1).wait()

        taskdir = py.path.local(task.abs_path())
        src = taskdir.join("d1", "d2", "r1", "file")
        resource1 = agentr.call(
            "resource_register",
            src.strpath, "TEST_TASK_RESOURCE", "Test Resource 1", None, {"foo": "bar", "zoo": 1},
            depth=None,
        ).wait()
        assert resource1["arch"] == ctm.OSFamily.ANY
        assert resource1["state"] == ctr.State.NOT_READY
        assert resource1["type"] == "TEST_TASK_RESOURCE"
        assert resource1["file_name"] == "d1/d2/r1/file"
        assert resource1["description"] == "Test Resource 1"
        assert resource1["attributes"] == {"foo": "bar", "zoo": "1"}

        with pytest.raises(errors.InvalidResource) as ex:
            agentr.call("resource_complete", resource1["id"]).wait()
        assert "does not exist" in str(ex)

        resource1_dup = agentr.call(
            "resource_register",
            src.strpath, "TEST_TASK_RESOURCE", "Test Resource 1", None, {"foo": "bar", "zoo": 1},
            depth=None,
        ).wait()
        resource1_dup["id"] == resource1["id"]
        src.ensure(file=1)
        src.write(uuid.uuid4().hex)

        # resource1_bad_dup = resource1.copy()
        # resource1_bad_dup["id"] = resource1["id"] + 1
        # resource1_bad_dup["attributes"] = {"foo": "bar", "zoo": -1}
        # with pytest.raises(errors.InvalidResource) as ex:
        #     agentr.call("resource_register_meta", src.strpath, resource1_bad_dup).wait()

        resource1_upd = resource1.copy()
        resource1_upd["attributes"] = {"foo": "bar", "zoo": -1}
        agentr.call("resource_register_meta", src.strpath, resource1).wait()

        src = taskdir.join("d1", "d2", "r2", "file")
        src2 = src
        resource2 = agentr.call(
            "resource_register",
            src.dirpath().relto(taskdir), "TEST_TASK_RESOURCE", "Test Resource 2", None, {"foo": "bar", "zoo": 2},
            depth=None,
        ).wait()

        with pytest.raises(ValueError) as ex:
            agentr.call(
                "resource_register",
                src.dirpath().relto(taskdir), "TEST_TASK_RESOURCE", "Test Resource 3", None, {"foo": "bar", "zoo": 3},
                depth=4
            ).wait()
        assert "Depth 4 unacceptable" in str(ex)

        for tmp_path in ("tmp", "tmp/", "tmp/a", "tmp/a/b"):
            with pytest.raises(errors.InvalidData) as ex:
                agentr.call(
                    "resource_register", taskdir.join(tmp_path).strpath, "TEST_TASK_RESOURCE", "Resource 3", None, {},
                ).wait()
            assert "temporary directory" in str(ex)

        src.ensure(file=1)
        src.write(uuid.uuid4().hex)

        agentr.call("resource_complete", resource1["id"]).wait()
        resource1 = rest_session.resource[resource1["id"]][:]
        compare_keys = {"state", "file_name", "skynet_id", "md5"}
        assert resource1["state"] == ctr.State.READY
        assert resource1["file_name"] == "d1/d2/r1/file"
        assert resource1["skynet_id"]
        assert resource1["md5"]
        agentr_meta = agentr.call("resource_meta", resource1["id"]).wait()
        assert {k: resource1[k] for k in compare_keys} == {k: agentr_meta[k] for k in compare_keys}

        with pytest.raises(errors.InvalidResource) as ex:
            agentr.call(
                "resource_register",
                src2.join("r3").strpath, "TEST_TASK_RESOURCE", "Test Resource 3", None, {"foo": "bar", "zoo": 3},
                depth=None
            ).wait()
        assert "has intersection" in str(ex)

        src3 = taskdir.join("d1", "d3", "d4", "r3", "file")
        resource3 = agentr.call(
            "resource_register",
            src3.strpath, "TEST_TASK_RESOURCE", "Test Resource 3", None, {"foo": "bar", "zoo": 3},
            depth=None,
        ).wait()
        src3.dirpath().ensure(dir=1)
        src3.write(uuid.uuid4().hex)

        src4 = taskdir.join("d3", "d2", "d1", "file")
        resource4 = agentr.call(
            "resource_register",
            src4.strpath, "TEST_TASK_RESOURCE", "Test Resource 4", None, {"foo": "bar", "zoo": 4},
            depth=None
        ).wait()
        src4.dirpath().ensure(dir=1)

        with pytest.raises(errors.InvalidResource) as ex:
            agentr.call("resource_complete", resource4["id"]).wait()
        assert "does not exist" in str(ex)

        resource4 = agentr.call(
            "resource_register",
            src4.strpath, "TEST_TASK_RESOURCE", "Test Resource 4", None, {"foo": "bar", "zoo": 4},
            depth=None
        ).wait()
        src4.write(uuid.uuid4().hex)

        agentr.call("task_finished").wait()
        resource2 = rest_session.resource[resource2["id"]][:]
        assert resource2["state"] == ctr.State.READY
        assert resource2["file_name"] == "d1/d2/r2"
        assert resource2["skynet_id"]
        assert resource2["md5"] is None

        resource3 = rest_session.resource[resource3["id"]][:]
        assert resource3["state"] == ctr.State.READY
        assert resource3["file_name"] == "d1/d3/d4/r3/file"
        assert resource3["skynet_id"]
        assert resource3["md5"]

        resource4 = rest_session.resource[resource4["id"]][:]
        assert resource4["state"] == ctr.State.READY
        assert resource4["file_name"] == "d3/d2/d1/file"
        assert resource4["skynet_id"]
        assert resource4["md5"]

    def test__resource_sync(
        self,
        agentr, rest_session, rest_session_login, task_session, client_manager, task_manager, resource_manager, tmpdir
    ):
        manager_tests._create_client(client_manager, common.config.Registry().this.id)
        task = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.EXECUTING, author=rest_session_login
        )
        task2 = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.SUCCESS, author=rest_session_login
        )
        resource, src = self._real_resource(
            tmpdir, task_manager, resource_manager, task2,
            resource_type="TEST_TASK_RESOURCE", resource_filename="dir",
        )
        with pytest.raises(errors.NoTaskSession):
            agentr.call("resource_sync", resource.id).wait()

        token = task_session(rest_session, task.id, rest_session_login)
        agentr.call("task_session", token, 1).wait()
        path = agentr.call("resource_sync", resource.id).wait()
        assert py.path.local(path).check(dir=1)
        assert py.path.local(path).join("file").check(file=1)
        # Delete source and call it once again - it should be available in cache
        src.remove()
        agentr.call("resource_sync", resource.id).wait()
        agentr.call("task_finished").wait()

    def test__resource_sync_sync(
        self,
        agentr, rest_session, rest_session_login, task_session, client_manager, task_manager, resource_manager, tmpdir
    ):
        manager_tests._create_client(client_manager, common.config.Registry().this.id)
        task = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.EXECUTING, author=rest_session_login
        )
        task2 = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.SUCCESS, author=rest_session_login
        )
        resource, src = self._real_resource(
            tmpdir, task_manager, resource_manager, task2,
            resource_type="TEST_TASK_RESOURCE", resource_filename="dir",
        )
        token = task_session(rest_session, task.id, rest_session_login)
        agentr.call("task_session", token, 1).wait()
        for job in [agentr.call("resource_sync", resource.id) for _ in range(10)]:
            assert py.path.local(job.wait()).check(dir=1)

        # Delete source and call it once again - it should be available in cache
        src.remove()
        for job in [agentr.call("resource_sync", resource.id) for _ in range(10)]:
            assert py.path.local(job.wait()).check(dir=1)
        agentr.call("task_finished").wait()

    def test__resource_sync_async(
        self,
        agentr, rest_session, rest_session_login, task_session,
        client_manager, task_manager, resource_manager, tmpdir
    ):
        manager_tests._create_client(client_manager, common.config.Registry().this.id)
        task = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.EXECUTING, author=rest_session_login
        )
        task2 = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.SUCCESS, author=rest_session_login
        )
        dst = py.path.local(common.config.Registry().client.tasks.data_dir).join(*(ctt.relpath(task2.id)))
        self._task_dir_chmod(dst)
        dst.join("d1/d2/d3/d4/d5").ensure(dir=1)
        resources = [
            self._real_resource(
                tmpdir, task_manager, resource_manager, task2, dir=False,
                resource_type="TEST_TASK_RESOURCE", resource_filename="d1/d2/d3/d4/d5/f" + str(i),
            )
            for i in range(0, 6)
        ]

        dst.remove(rec=1)
        self._task_dir_chmod(dst, False)
        token = task_session(rest_session, task.id, rest_session_login)
        agentr.call("task_session", token, 1).wait()
        jobs = [agentr.call("resource_sync", res.id) for res, _ in resources]
        rets = map(lambda _: _.wait(), jobs)
        for _ in rets:
            assert py.path.local(_).check(file=1)

        # Delete sources and call it once again - it should be available in cache
        map(lambda _: _[1].remove(), resources)
        jobs = [agentr.call("resource_sync", res.id) for res, _ in resources]
        map(lambda _: _.wait(), jobs)
        agentr.call("task_finished").wait()

    def test__register_log(self, agentr, rest_session, rest_session_login, task_manager, task_session, tmpdir):
        task = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.DRAFT, author=rest_session_login
        )
        agentr.call("freeze").wait()
        agentr.call("ease").wait()
        agentr.call("freeze").wait()
        token = task_session(rest_session, task.id, rest_session_login)
        agentr.call("task_session", token, 1).wait()
        with pytest.raises(errors.PushClientUnavailable):
            agentr.call("register_log", "no matter").wait()
        statbox_log_dir = py.path.local(tmpdir).ensure(dir=1)
        config_path = common.config.Registry().agentr.statbox_push_client.config
        with open(config_path, "w") as f:
            f.write(yaml.dump(
                {
                    "files": [
                        {"log_type": types.LogType.TASK, "int_dir": str(statbox_log_dir)}
                    ]
                }
            ))
        log_to_push = py.path.local(task.abs_path()).join("test.log")
        log_to_push.write("trash")
        agentr.call("register_log", str(log_to_push)).wait()
        agentr.call("task_finished").wait()
        assert statbox_log_dir.join("{}_{}".format(task.id, log_to_push.basename)).read() == log_to_push.read()

    def test__deblock(self, agentr):
        db = agentr.call("test_deblock", 3)
        for i in range(10):
            with common.utils.Timer() as t:
                agentr.call("ping", i).wait()
                assert float(t) < 1
        db.wait()

    def test__disk_usage_last(
        self, agentr, rest_session, rest_session_login, task_session,
        client_manager, task_manager, resource_manager, tmpdir, tasks_dir
    ):
        def du(path):
            return utils.get_disk_usage(path, True)[1]

        manager_tests._create_client(client_manager, common.config.Registry().this.id)
        main_task = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.EXECUTING, author=rest_session_login
        )
        payload = uuid.uuid4().hex
        # create resource belonging to the other task
        resource, src = self._real_resource(
            tmpdir, task_manager, resource_manager, None, dir=False, content=payload * 10 ** 5,
            keep_src=True, resource_type="TEST_TASK_RESOURCE", resource_filename="res0")
        # remove that resource to check synchronization
        py.path.local(resource.abs_path()).remove()

        # register main_task as dependent from this resource
        task_manager.register_dep_resource(main_task.id, resource.id)

        src_size = du(str(src))
        tasks_dir_usage_start = du(tasks_dir)  # supposed to be 0
        assert tasks_dir_usage_start == 0

        # create copy of rest_session and associate it with main_task to not spoil rest_session
        rest_session2 = rest_session.copy()
        token = task_session(rest_session2, main_task.id, rest_session_login)

        agentr.call("task_session", token, 1).wait()
        # tell agentr to synchronize resource via skynet
        assert resource.skynet_id
        restored_res_path = agentr.call("resource_sync", resource.id).wait()
        assert restored_res_path
        agentr.call("df").wait()
        agentr.call("task_finished").wait()

        result = rest_session.task[main_task.id][:]["results"]["disk_usage"]
        assert all(metric in result for metric in ("last", "max"))

        tasks_dir_usage_end = du(tasks_dir)
        # resource must arrive to main_task_dir due to synchronization
        tasks_dir_delta = tasks_dir_usage_end - tasks_dir_usage_start
        assert tasks_dir_delta > 0

        # ideally it could be 0, but actually agentr.log also arrived for main_task
        extra_files_size = tasks_dir_delta - src_size
        assert abs(extra_files_size - result["last"]) < (200 << 10), (tasks_dir_delta, src_size, result["last"])

    @pytest.mark.usefixtures("agentr")
    def test__reconnect_after_fork(
        self,
        rest_session, rest_session_login, task_session, client_manager, task_manager, resource_manager, tmpdir
    ):
        manager_tests._create_client(client_manager, common.config.Registry().this.id)
        task = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.EXECUTING, author=rest_session_login
        )
        task2 = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.SUCCESS, author=rest_session_login
        )
        resource, src = self._real_resource(
            tmpdir, task_manager, resource_manager, task2,
            resource_type="TEST_TASK_RESOURCE", resource_filename="dir",
        )

        token = task_session(rest_session, task.id, rest_session_login)
        agentr = client.Session(token, 1, 0, logging.getLogger())

        pid = os.fork()
        if pid:  # Parent
            rc = os.waitpid(pid, 0)
            assert not rc[1]
        else:
            agentr.resource_sync(resource.id)
            os._exit(0)

        path = resource.abs_path()
        assert py.path.local(path).check(dir=1)
        assert py.path.local(path).join("file").check(file=1)
        # Delete source and call it once again - it should be available in cache
        src.remove()
        agentr.resource_sync(resource.id)
        agentr.finished()

    @pytest.mark.usefixtures("agentr")
    def test__meta_save_load(self, rest_session, rest_session_login, task_manager, task_session):
        task = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.EXECUTING, author=rest_session_login
        )
        token = task_session(rest_session, task.id, rest_session_login)
        agentr = client.Session(token, 1, 0, logging.getLogger())

        word = u"йцукен"
        meta = [word, word.encode("utf-8")]
        agentr.meta = meta
        for s in agentr.meta:
            assert isinstance(s, unicode)
            assert s == word

    @pytest.mark.usefixtures("resource_manager", "client_manager", "client", "s3_simulator")
    def test__resource_complete(self, agentr, rest_session, rest_session_login, task_session, task_manager):
        parent = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.WAIT_TASK, author=rest_session_login
        )
        task = manager_tests._create_task(
            task_manager, type="TEST_TASK", parent_id=parent.id, status=ctt.Status.EXECUTING, author=rest_session_login
        )
        token = task_session(rest_session, task.id, rest_session_login)
        agentr.call("task_session", token, 1).wait()

        parentdir = py.path.local(parent.abs_path())
        taskdir = py.path.local(task.abs_path())
        src = py.path.local(taskdir).join("dir")

        rid = agentr.call(
            "resource_register",
            src.strpath, "TEST_TASK_RESOURCE", "Test Resource 1", None, {"foo": "bar"},
        ).wait()["id"]
        src.ensure(dir=1)
        src.join("file").write(uuid.uuid4().hex)
        agentr.call("resource_complete", rid).wait()

        assert src.check(dir=1) and src.join("file").check(file=1)

        src = py.path.local(taskdir).join("dir1", "dir2")
        rid = agentr.call(
            "resource_register",
            src.strpath + ".not_existing", "TEST_TASK_RESOURCE", "Test Resource 2", None, {"zoo": 1},
        ).wait()["id"]

        meta = agentr.call(
            "resource_update",
            rid, src.strpath, "Test Resource 21", None, {"zoo": 1, "bar": "foo"}
        ).wait()
        smeta = rest_session.resource[rid][:]
        assert smeta["description"] == meta["description"]
        assert smeta["attributes"] == {"zoo": "1", "bar": "foo"}
        assert smeta["file_name"] == meta["file_name"]
        assert smeta["arch"] == meta["arch"]

        src.ensure(dir=1)
        src.join("file").write(uuid.uuid4().hex)
        agentr.call("resource_complete", rid).wait()

        smeta = rest_session.resource[rid][:]
        assert smeta["description"] == meta["description"]
        assert smeta["attributes"] == {"zoo": "1", "bar": "foo"}
        assert smeta["file_name"] == meta["file_name"]
        assert smeta["arch"] == meta["arch"]

        dst = py.path.local(taskdir).join("dir1")
        assert dst.check(dir=1) and dst.stat().mode & stat.S_IWUSR
        assert src.check(dir=1) and src.join("file").check(file=1)

        src = py.path.local(taskdir).join("dir3", "dir4")
        rid = agentr.call(
            "resource_register",
            src.dirname, "TEST_TASK_RESOURCE", "Test Parent Resource 1", None, {}, for_parent=True
        ).wait()["id"]
        src.ensure(dir=1)
        src.join("file").write(uuid.uuid4().hex)
        agentr.call("resource_complete", rid).wait()

        dst = py.path.local(parentdir).join("dir3")
        assert dst.check(dir=1) and dst.stat().mode & stat.S_IRUSR and not dst.stat().mode & stat.S_IWUSR
        dst = dst.join("dir4")
        assert dst.check(dir=1) and dst.stat().mode & stat.S_IRUSR and not dst.stat().mode & stat.S_IWUSR
        dst = dst.join("file")
        assert dst.check(file=1) and dst.stat().mode & stat.S_IRUSR and not dst.stat().mode & stat.S_IWUSR
        assert src.join("..").check(link=1) and src.join("file").check(file=1)

        src = py.path.local(taskdir).join("file4")
        parent_resource = manager_tests._create_resource(
            task_manager, mark_ready=False, task=parent, create_logs=False,
            parameters={
                "resource_desc": "Test Parent Resource 2",
                "resource_filename": src.basename,
                "resource_type": "TEST_TASK_RESOURCE",
                "attrs": {"parent_resource": "2"},
            }
        )
        # Strange method to register existent resource - try to register
        rid = agentr.call(
            "resource_register",
            src.strpath, str(parent_resource.type), parent_resource.name, None, parent_resource.attrs, for_parent=True
        ).wait()["id"]
        src.ensure(file=1)
        src.write(uuid.uuid4().hex)
        agentr.call("resource_complete", rid).wait()

        dst = py.path.local(parentdir).join("file4")
        assert dst.check(file=1) and dst.stat().mode & stat.S_IRUSR and not dst.stat().mode & stat.S_IWUSR
        assert src.check(link=1)

        src = py.path.local(taskdir).join("dir5", "dir6", "dir7")
        resource = agentr.call(
            "resource_register",
            src.dirname, "TEST_TASK_RESOURCE", "Test Parent Resource 3", None, {},
            for_parent=True, depth=None,
        ).wait()
        assert resource["file_name"] == "dir5/dir6"

        src.ensure(dir=1)
        src.join("file").write(uuid.uuid4().hex)
        agentr.call("resource_complete", resource["id"]).wait()

        dst = py.path.local(parentdir).join("dir5")
        assert dst.check(dir=1) and dst.stat().mode & stat.S_IRUSR and not dst.stat().mode & stat.S_IWUSR
        dst = dst.join("dir6")
        assert dst.check(dir=1) and dst.stat().mode & stat.S_IRUSR and not dst.stat().mode & stat.S_IWUSR
        dst = dst.join("dir7")
        assert dst.check(dir=1) and dst.stat().mode & stat.S_IRUSR and not dst.stat().mode & stat.S_IWUSR
        dst = dst.join("file")
        assert dst.check(file=1) and dst.stat().mode & stat.S_IRUSR and not dst.stat().mode & stat.S_IWUSR
        assert src.join("..").check(link=1) and src.join("file").check(file=1)

    @pytest.mark.usefixtures("resource_manager", "client_manager", "client")
    def test__resource_complete_sync_mds(
        self, agentr, rest_session, rest_session_login, task_session, task_manager, s3_simulator
    ):
        """Checks happy path for resource_complete with S3 simulator"""
        # assign
        task = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.EXECUTING, author=rest_session_login
        )
        token = task_session(rest_session, task.id, rest_session_login)
        agentr.call("task_session", token, 1).wait()

        taskdir = py.path.local(task.abs_path())

        # act
        src = py.path.local(taskdir).join("dir")
        rid = agentr.call(
            "resource_register",
            src.strpath, "TEST_TASK_RESOURCE", "Test Resource 1", None, {"sync_upload_to_mds": True},
        ).wait()["id"]
        src.ensure(dir=1)
        file_path = src.join("file")
        file_data = uuid.uuid4().hex
        file_path.write(file_data)
        agentr.call("resource_complete", rid).wait()

        # assert
        resource = rest_session.resource[rid][:]
        mds_key = resource["mds"].pop("key")
        assert resource["state"] == ctr.State.READY
        assert resource["multifile"] is True
        assert resource["executable"] is False
        assert resource["mds"] == dict(
            namespace=ctr.DEFAULT_S3_BUCKET, url=common.mds.s3_link(mds_key), backup_url=""
        )
        meta = requests.get(common.mds.s3_link(str(rid))).json()[2:]
        meta.sort()
        assert len(meta) == 2
        assert meta == [
            dict(common.mds.schema.MDSFileMeta.create(
                path=os.path.dirname(file_path.relto(taskdir)), type=ctr.FileType.DIR
            )),
            dict(common.mds.schema.MDSFileMeta.create(
                path=file_path.relto(taskdir), type=ctr.FileType.FILE, size=file_path.size(),
                md5=hashlib.md5(file_data).hexdigest(), sha1_blocks=[hashlib.sha1(file_data).hexdigest()],
                mime="text/plain", offset=tarfile.BLOCKSIZE * 2
            ))
        ]
        offset = meta[1]["offset"]
        size = meta[1]["size"]
        assert requests.get(common.mds.s3_link(mds_key)).content[offset:offset + size] == file_path.read()

    @pytest.mark.usefixtures("resource_manager", "client_manager", "client")
    def test__resource_complete_mds_big_file(
        self, agentr, rest_session, rest_session_login, task_session, task_manager, s3_simulator
    ):
        """Check resource_complete with big file"""
        # assign
        task = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.EXECUTING, author=rest_session_login
        )
        token = task_session(rest_session, task.id, rest_session_login)
        agentr.call("task_session", token, 1).wait()
        taskdir = py.path.local(task.abs_path())

        file_path = py.path.local(taskdir).join("big_file")
        rid = agentr.call(
            "resource_register",
            file_path.strpath, "TEST_TASK_RESOURCE", "Test Resource 2", None, {"sync_upload_to_mds": True},
        ).wait()["id"]
        bucket_stats = common.mds.S3.bucket_stats(ctr.DEFAULT_S3_BUCKET)
        free_space = bucket_stats["max_size"] - bucket_stats["used_space"]
        file_path.write("*" * (free_space + 1))
        with pytest.raises(sandbox.common.joint.errors.ServerError) as ex:
            agentr.call("resource_complete", rid).wait()
        assert ex.value.args[0] == "Bucket {} has insufficient free space {} to upload {}".format(
            ctr.DEFAULT_S3_BUCKET, common.format.size2str(free_space), common.format.size2str(free_space + 1)
        )

    @pytest.mark.usefixtures("resource_manager", "client_manager", "client")
    def test__resource_complete_mds_zero_length(
        self, agentr, rest_session, rest_session_login, task_session, task_manager, s3_simulator
    ):
        """Check resource_complete with files with zero length"""
        # assign
        task = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.EXECUTING, author=rest_session_login
        )
        token = task_session(rest_session, task.id, rest_session_login)
        agentr.call("task_session", token, 1).wait()
        taskdir = py.path.local(task.abs_path())

        src = py.path.local(taskdir).join("dir10")
        src_basename = src.basename
        rid = agentr.call(
            "resource_register",
            src.strpath, "TEST_TASK_RESOURCE", "Test Resource 4", None, {"sync_upload_to_mds": True},
        ).wait()["id"]
        src.ensure(dir=1)
        files = {}
        for i in range(1, 6):
            file_path = src.join("file{}".format(i))
            file_path.write("" if i == 3 else "123")
            files[i] = file_path
        agentr.call("resource_complete", rid).wait()
        resource = rest_session.resource[rid][:]
        mds_url = resource["mds"]["url"]
        mds_meta_url = mds_url[:mds_url.rfind("/")]
        mds_meta = sorted(
            (
                {"path": _["path"], "type": _["type"]}
                for _ in requests.get(mds_meta_url).json()
            ),
            key=lambda _: _["path"]
        )
        assert mds_meta == [
            {"type": ctr.FileType.DIR, "path": ""},
            {"type": ctr.FileType.DIR, "path": src_basename},
            {"type": ctr.FileType.TARDIR, "path": src_basename + ".tar"},
            {"type": ctr.FileType.FILE, "path": src_basename + "/file1"},
            {"type": ctr.FileType.FILE, "path": src_basename + "/file2"},
            {"type": ctr.FileType.TOUCH, "path": src_basename + "/file3"},
            {"type": ctr.FileType.FILE, "path": src_basename + "/file4"},
            {"type": ctr.FileType.FILE, "path": src_basename + "/file5"},
        ]

    @pytest.mark.usefixtures("resource_manager", "client_manager", "client")
    def test__resource_complete_sync_mds_tar(
        self, agentr, rest_session, rest_session_login, task_session, task_manager, s3_simulator
    ):
        # assign
        task = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.EXECUTING, author=rest_session_login
        )
        token = task_session(rest_session, task.id, rest_session_login)
        agentr.call("task_session", token, 1).wait()
        taskdir = py.path.local(task.abs_path())
        src_ = py.path.local(taskdir).join("dir11")
        src_.ensure(dir=1)
        for i in range(1, 6):
            file_path = src_.join("file{}".format(i))
            file_path.write("" if i == 3 else "123")

        for pack_tar, dir_name, ext in (
            (True, "dir3", ".tar"),
            (common.mds.compression.base.CompressionType.TAR, "dir4", ".tar"),
            (common.mds.compression.base.CompressionType.TGZ, "dir5", ".tgz"),
        ):
            # act
            src = py.path.local(taskdir).join(dir_name)
            src_basename = src.basename
            rid = agentr.call(
                "resource_register",
                src.strpath, "TEST_TASK_RESOURCE", "Test Resource", None,
                {"sync_upload_to_mds": True, "pack_tar": pack_tar},
            ).wait()["id"]
            shutil.copytree(src_.strpath, src.strpath)
            agentr.call("resource_complete", rid).wait()
            # assert
            resource = rest_session.resource[rid][:]
            assert resource["state"] == ctr.State.READY
            assert resource["file_name"] == src_basename + ext
            assert resource["multifile"] == False
            s3_url = resource["mds"]["url"]
            s3_meta_url = s3_url.rsplit("/", 1)[0]
            mds_meta = sorted(
                (
                    {"path": _["path"], "type": _["type"], "offset": False if _.get("offset") is None else True}
                    for _ in requests.get(s3_meta_url).json()
                ),
                key=lambda _: _["path"]
            )
            assert mds_meta == [
                {"type": ctr.FileType.DIR, "path": "", "offset": False},
                {"type": ctr.FileType.DIR, "path": src_basename, "offset": False},
                {"type": ctr.FileType.FILE, "path": resource["file_name"], "offset": False},
                {"type": ctr.FileType.FILE, "path": src_basename + "/file1", "offset": True},
                {"type": ctr.FileType.FILE, "path": src_basename + "/file2", "offset": True},
                {"type": ctr.FileType.TOUCH, "path": src_basename + "/file3", "offset": False},
                {"type": ctr.FileType.FILE, "path": src_basename + "/file4", "offset": True},
                {"type": ctr.FileType.FILE, "path": src_basename + "/file5", "offset": True},
            ]
            assert requests.get(s3_url + ".index").status_code == (
                requests.codes.OK
                if pack_tar == common.mds.compression.base.CompressionType.TGZ else
                requests.codes.NOT_FOUND
            )

    @pytest.mark.usefixtures("resource_manager", "client_manager", "client")
    def test__resource_complete_sync_mds_retries_429(
        self, agentr, rest_session, rest_session_login, task_session, task_manager, s3_simulator
    ):
        """Check that resource_complete gets over temporarily overloaded S3 (which returns 429 TooManyRequests)"""
        # assign
        task = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.EXECUTING, author=rest_session_login
        )
        token = task_session(rest_session, task.id, rest_session_login)
        agentr.call("task_session", token, 1).wait()

        taskdir = py.path.local(task.abs_path())

        file_path = py.path.local(taskdir).join("file")
        rid = agentr.call(
            "resource_register",
            file_path.strpath, "TEST_TASK_RESOURCE", "Test Resource 2", None, {"sync_upload_to_mds": True},
        ).wait()["id"]
        file_path.write(uuid.uuid4().hex)

        # act
        s3_simulator.force_error_responses(429, timer=20)
        agentr.call("resource_complete", rid).wait()

        # assert
        resource = rest_session.resource[rid][:]
        mds_key = resource["mds"].pop("key")
        assert resource["state"] == ctr.State.READY
        assert resource["multifile"] is False
        assert resource["executable"] is False
        assert resource["mds"] == dict(
            namespace=ctr.DEFAULT_S3_BUCKET, url=common.mds.s3_link(mds_key), backup_url=""
        )
        assert requests.get(common.mds.s3_link(mds_key)).content == file_path.read()

    @pytest.mark.usefixtures("resource_manager", "client_manager", "client")
    def test__resource_complete_sync_mds_chmod(
        self, agentr, rest_session, rest_session_login, task_session, task_manager, s3_simulator
    ):
        """Check resource_complete for file with 755 mode, i.e. write permission only for user"""
        # assign
        task = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.EXECUTING, author=rest_session_login
        )
        token = task_session(rest_session, task.id, rest_session_login)
        agentr.call("task_session", token, 1).wait()

        taskdir = py.path.local(task.abs_path())

        # act
        file_path = py.path.local(taskdir).join("file2")
        rid = agentr.call(
            "resource_register",
            file_path.strpath, "TEST_TASK_RESOURCE", "Test Resource 3", None, {"sync_upload_to_mds": True},
        ).wait()["id"]
        file_path.write(uuid.uuid4().hex)
        file_path.chmod(0o755)
        # act & assert
        agentr.call("resource_complete", rid).wait()

    @pytest.mark.usefixtures("resource_manager", "client_manager", "client", "s3_simulator")
    def test__resource_complete_async_mds(self, agentr, rest_session, rest_session_login, task_session, task_manager):
        task = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.EXECUTING, author=rest_session_login
        )
        token = task_session(rest_session, task.id, rest_session_login)
        agentr.call("task_session", token, 1).wait()

        taskdir = py.path.local(task.abs_path())

        src = py.path.local(taskdir).join("dir")
        rid = agentr.call(
            "resource_register",
            src.strpath, "TEST_TASK_RESOURCE", "Test Resource 1", None, {"sync_upload_to_mds": False},
        ).wait()["id"]
        src.ensure(dir=1)
        file_path = src.join("file")
        file_data = uuid.uuid4().hex
        file_path.write(file_data)
        agentr.call("resource_complete", rid).wait()

        assert common.utils.progressive_waiter(0, 0.1, 60, lambda: rest_session.resource[rid][:]["mds"])[0]

        resource = rest_session.resource[rid][:]
        mds_key = resource["mds"].pop("key")
        assert resource["state"] == ctr.State.READY
        assert resource["multifile"] is True
        assert resource["executable"] is False
        assert resource["mds"] == dict(
            namespace=ctr.DEFAULT_S3_BUCKET, url=common.mds.s3_link(mds_key), backup_url=""
        )
        mds_url = resource["mds"]["url"]
        mds_meta_url = mds_url[:mds_url.rfind("/")]
        meta = requests.get(mds_meta_url).json()[2:]
        meta.sort(key=lambda _: _["path"])
        assert len(meta) == 2

        assert meta == [
            dict(common.mds.schema.MDSFileMeta.create(
                path=os.path.dirname(file_path.relto(taskdir)), type=ctr.FileType.DIR
            )),
            dict(common.mds.schema.MDSFileMeta.create(
                path=file_path.relto(taskdir), type=ctr.FileType.FILE, size=file_path.size(),
                md5=hashlib.md5(file_data).hexdigest(), sha1_blocks=[hashlib.sha1(file_data).hexdigest()],
                mime="text/plain", offset=tarfile.BLOCKSIZE * 2
            ))
        ]
        tar_data = requests.get(mds_url).content
        assert tar_data[meta[1]["offset"]:meta[1]["offset"] + meta[1]["size"]] == file_path.read()

        # resource with zero length file
        src = py.path.local(taskdir).join("dir2")
        rid = agentr.call(
            "resource_register",
            src.strpath, "TEST_TASK_RESOURCE", "Test Resource 2", None, {"sync_upload_to_mds": False},
        ).wait()["id"]
        src.ensure(dir=1)
        for i in range(1, 6):
            file_path = src.join("file{}".format(i))
            file_path.write("" if i == 3 else "123")
        agentr.call("resource_complete", rid).wait()
        assert common.utils.progressive_waiter(0, 0.1, 60, lambda: rest_session.resource[rid][:]["mds"])[0]
        resource = rest_session.resource[rid][:]
        mds_url = resource["mds"]["url"]
        mds_meta_url = mds_url[:mds_url.rfind("/")]
        meta = requests.get(mds_meta_url).json()
        mds_meta = sorted(({"path": _["path"], "type": _["type"]} for _ in meta), key=lambda _: _["path"])
        assert mds_meta == [
            {"type": ctr.FileType.DIR, "path": ""},
            {"type": ctr.FileType.DIR, "path": "dir2"},
            {"type": ctr.FileType.TARDIR, "path": "dir2.tar"},
            {"type": ctr.FileType.FILE, "path": "dir2/file1"},
            {"type": ctr.FileType.FILE, "path": "dir2/file2"},
            {"type": ctr.FileType.TOUCH, "path": "dir2/file3"},
            {"type": ctr.FileType.FILE, "path": "dir2/file4"},
            {"type": ctr.FileType.FILE, "path": "dir2/file5"},
        ]

        # test pack_tar
        src_ = src
        for pack_tar, dir_name, ext in (
            (True, "dir3", ".tar"),
            (common.mds.compression.base.CompressionType.TAR, "dir4", ".tar"),
            (common.mds.compression.base.CompressionType.TGZ, "dir5", ".tgz"),
        ):
            src = py.path.local(taskdir).join(dir_name)
            src_basename = src.basename
            rid = agentr.call(
                "resource_register",
                src.strpath, "TEST_TASK_RESOURCE", "Test Resource", None,
                {"sync_upload_to_mds": False, "pack_tar": pack_tar},
            ).wait()["id"]
            shutil.copytree(src_.strpath, src.strpath)
            agentr.call("resource_complete", rid).wait()
            assert common.utils.progressive_waiter(0, 0.1, 60, lambda: rest_session.resource[rid][:]["mds"])[0]
            resource = rest_session.resource[rid][:]
            assert resource["state"] == ctr.State.READY
            assert resource["file_name"] == src_basename + ext
            assert resource["multifile"] == False
            s3_url = resource["mds"]["url"]
            s3_meta_url = s3_url.rsplit("/", 1)[0]
            mds_meta = sorted(
                (
                    {"path": _["path"], "type": _["type"], "offset": False if _.get("offset") is None else True}
                    for _ in requests.get(s3_meta_url).json()
                ),
                key=lambda _: _["path"]
            )
            assert mds_meta == [
                {"type": ctr.FileType.DIR, "path": "", "offset": False},
                {"type": ctr.FileType.DIR, "path": src_basename, "offset": False},
                {"type": ctr.FileType.FILE, "path": resource["file_name"], "offset": False},
                {"type": ctr.FileType.FILE, "path": src_basename + "/file1", "offset": True},
                {"type": ctr.FileType.FILE, "path": src_basename + "/file2", "offset": True},
                {"type": ctr.FileType.TOUCH, "path": src_basename + "/file3", "offset": False},
                {"type": ctr.FileType.FILE, "path": src_basename + "/file4", "offset": True},
                {"type": ctr.FileType.FILE, "path": src_basename + "/file5", "offset": True},
            ]
            assert requests.get(s3_url + ".index").status_code == (
                requests.codes.OK
                if pack_tar == common.mds.compression.base.CompressionType.TGZ else
                requests.codes.NOT_FOUND
            )

    @pytest.mark.usefixtures("agentr")
    def test__coredumps(self, task_session, rest_session, rest_session_login, task_manager):
        task = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.EXECUTING, author=rest_session_login
        )
        token = task_session(rest_session, task.id, rest_session_login)
        logger = logging.getLogger()
        agentr_ses = client.Session(token, 1, 0, logger)
        agentr_srv = client.Service(logger)

        assert agentr_ses.coredumps == {}

        config = common.config.Registry()
        pid = os.getpid()
        coredump_filename = ".".join(("test", str(pid), "9"))
        assert agentr_ses.register_process(pid) == pid
        assert agentr_ses.register_process(pid) == pid
        assert agentr_srv.register_coredump(1, coredump_filename, 1) == os.path.join(
            config.client.tasks.coredumps_dir, coredump_filename
        )
        coredump_path = agentr_srv.register_coredump(pid, coredump_filename, pid)
        assert coredump_path == task.abs_path(coredump_filename)
        coredumps = {}
        t = th.Thread(target=lambda: coredumps.update(agentr_ses.coredumps))
        t.start()
        t.join(timeout=1)
        assert not coredumps
        py.path.local(coredump_path).write_binary("data")
        t.join(timeout=1)
        assert coredumps == {pid: coredump_path}


@pytest.mark.agentr
class TestNewLayout(BaseTestSuit):
    NEW_LAYOUT = True

    def test__restore_links(
        self,
        new_layout_agentr, rest_session, rest_session_login, task_session,
        client_manager, task_manager, resource_manager, tmpdir
    ):
        config = common.config.Registry()

        manager_tests._create_client(
            client_manager, config.this.id,
            tags=(ctc.Tag.GENERIC, ctc.Tag.NEW_LAYOUT)
        )
        task = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.EXECUTING, author=rest_session_login
        )
        resource, src = self._real_resource(
            tmpdir, task_manager, resource_manager, task,
            resource_type="TEST_TASK_RESOURCE", resource_filename="dir",
        )

        token = task_session(rest_session, task.id, rest_session_login)
        new_layout_agentr.call("task_session", token, 1).wait()
        new_layout_agentr.call("resource_sync", resource.id).wait()

        sympath = py.path.local(config.client.dirs.data).join("resources", *ctr.relpath(resource.id))
        assert sympath.check(dir=1)

        sympath.remove()
        new_layout_agentr.call("restore_links").wait()
        assert sympath.check(dir=1)

    @pytest.mark.usefixtures("s3_simulator")
    def test__resource_complete(
        self,
        new_layout_agentr, rest_session, rest_session_login, task_session,
        client_manager, task_manager, resource_manager
    ):
        config = common.config.Registry()

        manager_tests._create_client(
            client_manager, config.this.id,
            tags=(ctc.Tag.GENERIC, ctc.Tag.NEW_LAYOUT)
        )
        parent = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.WAIT_TASK, author=rest_session_login
        )
        task = manager_tests._create_task(
            task_manager, type="TEST_TASK", parent_id=parent.id, status=ctt.Status.EXECUTING, author=rest_session_login
        )
        token = task_session(rest_session, task.id, rest_session_login)
        new_layout_agentr.call("task_session", token, 1).wait()

        taskdir = py.path.local(task.abs_path())
        src = py.path.local(taskdir).join("dir")

        rid = new_layout_agentr.call(
            "resource_register",
            src.strpath, "TEST_TASK_RESOURCE", "Test Resource 1", None, {"foo": "bar"},
        ).wait()["id"]
        src.ensure(dir=1)
        src.join("file").write(uuid.uuid4().hex)
        new_layout_agentr.call("resource_complete", rid).wait()

        res_root = py.path.local(config.client.dirs.data).join("resources")
        sympath = res_root.join(*ctr.relpath(rid))
        assert sympath.check(link=1) and sympath.join("dir", "file").check(file=1)
        assert src.check(link=1) and src.join("file").check(file=1)

        src = py.path.local(taskdir).join("dir1", "dir2")
        rid = new_layout_agentr.call(
            "resource_register",
            src.strpath, "TEST_TASK_RESOURCE", "Test Resource 2", None, {"zoo": 1},
            depth=0,
        ).wait()["id"]
        src.ensure(dir=1)
        src.join("file").write(uuid.uuid4().hex)
        new_layout_agentr.call("resource_complete", rid).wait()

        sympath = res_root.join(*ctr.relpath(rid))
        assert sympath.check(link=1) and sympath.join("dir2", "file").check(file=1)
        assert py.path.local(taskdir).join("dir1").check(dir=1) and src.check(link=1) and src.join("file").check(file=1)

        src = py.path.local(taskdir).join("file3")
        rid = new_layout_agentr.call(
            "resource_register",
            src.strpath, "TEST_TASK_RESOURCE", "Test Parent Resource 1", None, {}, for_parent=True
        ).wait()["id"]
        src.ensure(file=1)
        src.write(uuid.uuid4().hex)
        new_layout_agentr.call("resource_complete", rid).wait()

        sympath = res_root.join(*ctr.relpath(rid))
        assert sympath.check(link=1) and sympath.join("file3").check(file=1)
        assert py.path.local(taskdir).join("file3").check(file=1) and src.check(link=1)

        src = py.path.local(taskdir).join("file4")
        parent_resource = manager_tests._create_resource(
            task_manager, mark_ready=False, task=parent, create_logs=False,
            parameters={
                "resource_desc": "Test Parent Resource 2",
                "resource_filename": src.basename,
                "resource_type": "TEST_TASK_RESOURCE",
                "attrs": {"parent_resource": "2"},
            }
        )
        # Strange method to register existent resource - try to register
        rid = new_layout_agentr.call(
            "resource_register",
            src.strpath, str(parent_resource.type), parent_resource.name, None, parent_resource.attrs, for_parent=True
        ).wait()["id"]
        src.ensure(file=1)
        src.write(uuid.uuid4().hex)
        new_layout_agentr.call("resource_complete", rid).wait()

        sympath = res_root.join(*ctr.relpath(rid))
        assert sympath.check(link=1) and sympath.join("file4").check(file=1)
        assert py.path.local(taskdir).join("file4").check(file=1) and src.check(link=1)

        src3 = taskdir.join("d1", "d2", "d3", "r3", "file")
        resource3 = new_layout_agentr.call(
            "resource_register",
            src3.strpath, "TEST_TASK_RESOURCE", "Test Resource 3", None, {"foo": "bar", "zoo": 3},
            depth=2
        ).wait()
        src3.dirpath().ensure(dir=1)
        src3.write(uuid.uuid4().hex)

        src4 = taskdir.join("d3", "d2", "d1", "file")
        resource4 = new_layout_agentr.call(
            "resource_register",
            src4.strpath, "TEST_TASK_RESOURCE", "Test Resource 4", None, {"foo": "bar", "zoo": 4},
            depth=None
        ).wait()
        src4.dirpath().ensure(dir=1)
        src4.write(uuid.uuid4().hex)

        src5 = taskdir.join("r5", "d2", "d1", "file")
        resource5 = new_layout_agentr.call(
            "resource_register",
            src5.strpath, "TEST_TASK_RESOURCE", "Test Resource 5", None, {"foo": "bar", "zoo": 5},
            depth=0
        ).wait()
        src5.dirpath().ensure(dir=1)
        src5.write(uuid.uuid4().hex)

        src6 = taskdir.join("r6", "d2", "d1", "file")
        with pytest.raises(ValueError):
            new_layout_agentr.call(
                "resource_register",
                src5.strpath, "TEST_TASK_RESOURCE", "Test Resource 6", None, {"foo": "bar", "zoo": 6},
                depth=4
            ).wait()
        with pytest.raises(ValueError):
            new_layout_agentr.call(
                "resource_register",
                src5.strpath, "TEST_TASK_RESOURCE", "Test Resource 6", None, {"foo": "bar", "zoo": 6},
                depth=100500
            ).wait()
        resource6 = new_layout_agentr.call(
            "resource_register",
            src6.strpath, "TEST_TASK_RESOURCE", "Test Resource 6", None, {"foo": "bar", "zoo": 6},
            depth=3
        ).wait()
        src6.dirpath().ensure(dir=1)
        src6.write(uuid.uuid4().hex)

        resource6 = rest_session.resource[new_layout_agentr.call("resource_complete", resource6["id"]).wait()["id"]][:]
        assert resource6["state"] == ctr.State.READY
        assert resource6["file_name"] == "r6/d2/d1/file"
        assert resource6["skynet_id"]
        assert src6.check(link=1)
        dst = res_root.join(*(ctr.relpath(resource6["id"]))).join("r6", "d2", "d1", "file")
        assert py.path.local(src6.readlink()).realpath() == dst.realpath()
        assert dst.check(file=1)

        new_layout_agentr.call("task_finished").wait()

        resource3 = rest_session.resource[resource3["id"]][:]
        assert resource3["state"] == ctr.State.READY
        assert resource3["file_name"] == "d3/r3/file"
        assert resource3["skynet_id"]
        assert resource3["md5"]
        assert src3.check(link=1)
        dst = res_root.join(*(ctr.relpath(resource3["id"]))).join("d3", "r3", "file")
        assert py.path.local(src3.readlink()).realpath() == dst.realpath()
        assert dst.check(file=1)

        resource4 = rest_session.resource[resource4["id"]][:]
        assert resource4["state"] == ctr.State.READY
        assert resource4["file_name"] == "d3/d2/d1/file"
        assert resource4["skynet_id"]
        assert resource4["md5"]
        assert src4.check(link=1)
        dst = res_root.join(*(ctr.relpath(resource4["id"]))).join("d3", "d2", "d1", "file")
        assert py.path.local(src4.readlink()).realpath() == dst.realpath()
        assert dst.check(file=1)

        resource5 = rest_session.resource[resource5["id"]][:]
        assert resource5["state"] == ctr.State.READY
        assert resource5["file_name"] == "file"
        assert resource4["skynet_id"]
        assert resource4["md5"]
        assert src5.check(link=1)
        dst = res_root.join(*(ctr.relpath(resource5["id"]))).join("file")
        assert py.path.local(src5.readlink()).realpath() == dst.realpath()
        assert dst.check(file=1)
