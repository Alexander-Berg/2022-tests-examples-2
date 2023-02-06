# coding: utf-8

import time
import datetime
import collections

import pytest

from sandbox import common

import sandbox.common.types.task as ctt
import sandbox.common.types.client as ctc

from sandbox.yasandbox.database import mapping

import sandbox.serviceq.types as qtypes

from . import _create_task, _create_real_resource, _create_client


class TestTaskClass:
    def test__copied_from1(self, task_manager, tasks_dir):
        """ Проверяем, что возвращается id скопированного таска """
        task = _create_task(task_manager, "UNIT_TEST", owner="user", parent_id=0, host="just_host")
        new_task = _create_task(task_manager, "UNIT_TEST", owner="user", parent_id=0, host="just_host")
        new_task.init_as_copy(task)
        task_manager.update(new_task)
        assert new_task.copied_from() == task.id

    def test__copied_from2(self, task_manager, tasks_dir):
        """ Проеряем, что у нескопированного таска метод возвращает None """
        task = _create_task(task_manager, "UNIT_TEST", owner="user", parent_id=0, host="just_host")
        assert task.copied_from() is None

    def test__copied_from3(self, server, task_manager, tasks_dir):
        import random
        import projects.sandbox.test_task
        import yasandbox.proxy.task

        data = {
            "arch": "linux",
            "model": "E312xx",
            "host": "host",
            "ram": 12345,
            "owner": "testbox",
            "author": "testbox",
            "task_type": "TEST_TASK",
            "parameters": {"ctx": {"dependent_resource_id": 100}}
        }
        data["parameters"]["ctx"].update({k: 0 for k in projects.sandbox.test_task.TestTask.CTX_CUSTOM})
        task = task_manager.create(**data)
        task_cpy = task_manager.load(task.id)
        assert task.arch == task_cpy.arch == "linux"
        assert task_cpy.ctx == task.ctx
        for k, v in data["parameters"]["ctx"].iteritems():
            assert task.ctx.get(k) == v

        defaults = yasandbox.proxy.task.Task().get_default_parameters()
        defaults.update(task.CTX_REDEFINES)
        for k, v in defaults.iteritems():
            assert task.ctx[k] == v, "Default: {}: {}, actual: {}".format(k, v, task.ctx[k])

        for k in task.CTX_REDEFINES:
            task.ctx[k] = random.randrange(1024)
        task_manager.update(task)

        task_cpy = task_manager.create(**data)
        task_cpy.init_as_copy(task)
        for param in ("arch", "model", "host", "required_ram", "owner", "author", "type"):
            assert getattr(task, param) == getattr(task_cpy, param)

        for k, v in defaults.iteritems():
            assert task.ctx[k] == task_cpy.ctx[k], "Default: {}: {}, actual: {}".format(k, task.ctx[k], task_cpy.ctx[k])


def _gen_custom_class(name, fields):
    """
    returns a class instance with immutable fields

    :param name: string name of the class
    :param fields: dict of field name to field value
    """
    return collections.namedtuple(name, fields.keys())(*fields.values())


class TestTaskManager:
    default_request = _gen_custom_class("request", {
        "user": _gen_custom_class(
            "user",
            {
                "login": "user",
                "super_user": False,
            }
        ),
        "owner": "OTHER",
    })

    def test__safe_xmlrpc_in_get_bulk_fields(self, task_manager):
        """ Test safe_xmlrpc in get_bulk_fields """
        task = _create_task(task_manager, "UNIT_TEST", owner="user")
        task.ctx[1] = 100  # this won"t serialize to xmlrpc
        task.ctx["foo"] = "bar"
        task_manager.update(task)
        task = task_manager.load(task.id)
        d = task_manager.get_bulk_fields([task.id], ["ctx"], safe_xmlrpc=True)
        assert 1 not in d[str(task.id)][0]
        assert "foo" in d[str(task.id)][0]

    def test__updated_on_state_switch(self, task_manager):
        task = _create_task(task_manager, "UNIT_TEST", owner="user")
        created = int(task.timestamp)
        assert task.updated - created < 2
        task_manager.update(task)
        assert task.updated - created < 2
        task = task_manager.load(task.id)
        assert task.updated - created < 2
        time.sleep(1)  # Need this to differ between creation and update time
        task.set_status(task.Status.DELETED)
        task_manager.update(task)
        assert task.timestamp < task.updated
        task = task_manager.load(task.id)
        assert task.timestamp < task.updated

    def test__create__creates_task_with_correct_fields(self, task_manager):
        task = _create_task(task_manager, "UNIT_TEST", owner="user", parent_id=0)
        assert task.owner == "user"
        assert task.host == ""
        assert task.id > 0
        assert task.parent_id == 0

    def test__create_with_good_get_default_parameters(self, task_manager):
        import common.projects_handler
        from sandbox import projects
        import sandboxsdk.task

        class GoodTaskMod(object):
            class GoodTask(sandboxsdk.task.SandboxTask):
                type = "GOOD_TASK"

                def get_default_parameters(self):
                    self.ctx["foo"] = "bar"

        projects.TYPES["GOOD_TASK"] = common.projects_handler.TaskTypeLocation(
            "GoodTaskMod", GoodTaskMod.GoodTask, None)
        projects.__dict__["GoodTaskMod"] = GoodTaskMod
        task = _create_task(task_manager, "GOOD_TASK", owner="user")
        assert "foo" in task.ctx and task.ctx["foo"] == "bar"
        assert task.status == task.Status.DRAFT
        projects.TYPES.pop("GOOD_TASK")
        projects.__dict__.pop("GoodTaskMod")

    def test__create_with_bad_get_default_parameters(self, task_manager):
        import common.projects_handler
        from sandbox import projects
        import sandboxsdk.task

        class BadTaskMod(object):
            class BadTask(sandboxsdk.task.SandboxTask):
                type = "BAD_TASK"

                def initCtx(self):
                    raise Exception("Exception in get_default_parameters")

        projects.TYPES["BAD_TASK"] = common.projects_handler.TaskTypeLocation(
            "BadTaskMod", BadTaskMod.BadTask, None)
        projects.__dict__["BadTaskMod"] = BadTaskMod
        task = _create_task(task_manager, "BAD_TASK", owner="user")
        assert task.status == ctt.Status.DRAFT
        projects.TYPES.pop("BAD_TASK")
        projects.__dict__.pop("BadTaskMod")

    def test__create__creates_subtask_with_correct_fields(self, task_manager):
        parent_task = _create_task(task_manager)
        task = _create_task(task_manager, "UNIT_TEST", owner="user2", parent_id=parent_task.id, host="")
        assert task.owner == "user2"
        assert task.host == ""
        assert task.parent_id == parent_task.id

    def test__create__creates_subtask_with_inherited_hidden_field(self, task_manager):
        parent_task = _create_task(task_manager, hidden=True)
        task = _create_task(task_manager, "UNIT_TEST", owner="user2", parent_id=parent_task.id, host="")
        assert task.owner == "user2"
        assert task.host == ""
        assert task.parent_id == parent_task.id

    def test__create__returns_task_with_default_type_for_unknown_task_type(self, task_manager):
        task = _create_task(task_manager, "UNEXISTING_TASK", owner="user3")
        assert task.type == "UNEXISTING_TASK"

    def test__task_manager_list_with_and_without_ctx(self, task_manager):
        tasks = {}
        for i in range(10):
            task = _create_task(task_manager, owner="user1", host="host1", parameters={"ctx": {"internal_id": i}})
            tasks[task.id] = task

        tasks_ = task_manager.list()
        assert len(tasks) == len(tasks_)
        for task in tasks_:
            assert task.id in tasks
            assert task.ctx == tasks[task.id].ctx

        tasks_ = task_manager.list(load_ctx=False)
        assert len(tasks) == len(tasks_)
        for task in tasks_:
            assert task.id in tasks
            assert task.ctx == {}

    def test__list__parent_id__int(self, task_manager):
        import yasandbox.proxy.task
        #
        task = _create_task(task_manager)
        sub_task_1 = _create_task(task_manager, parent_id=task.id)
        sub_task_2 = _create_task(task_manager, parent_id=task.id)
        #
        ret = task_manager.list(parent_id=task.id, order_by="+id")
        assert isinstance(ret, list)
        assert len(ret) == 2
        assert isinstance(ret[0], yasandbox.proxy.task.Task)
        assert ret[0].parent_id == ret[1].parent_id == task.id
        assert ret[0].id == sub_task_1.id
        assert ret[1].id == sub_task_2.id

    def test__list__parent_id__list(self, task_manager):
        import yasandbox.proxy.task
        #
        task_1 = _create_task(task_manager)
        task_2 = _create_task(task_manager)
        sub_task_1_1 = _create_task(task_manager, parent_id=task_1.id)
        sub_task_1_2 = _create_task(task_manager, parent_id=task_1.id)
        sub_task_2_1 = _create_task(task_manager, parent_id=task_2.id)
        sub_task_2_2 = _create_task(task_manager, parent_id=task_2.id)
        #
        ret = task_manager.list(parent_id=[task_1.id, task_2.id], order_by="+id")
        assert isinstance(ret, list)
        assert len(ret) == 4
        assert isinstance(ret[0], yasandbox.proxy.task.Task)
        assert ret[0].parent_id == ret[1].parent_id == task_1.id
        assert ret[2].parent_id == ret[3].parent_id == task_2.id
        assert ret[0].id == sub_task_1_1.id
        assert ret[1].id == sub_task_1_2.id
        assert ret[2].id == sub_task_2_1.id
        assert ret[3].id == sub_task_2_2.id

    def test__list__created(self, task_manager):
        now = datetime.datetime.utcnow() - datetime.timedelta(seconds=1)
        next_second = datetime.datetime.utcnow() + datetime.timedelta(seconds=1)
        task = _create_task(task_manager)
        ret = task_manager.list(created=(now, next_second))
        assert ret[0].id == task.id

    def test__list__created__invalid_bound(self, task_manager):
        now = datetime.datetime.utcnow() - datetime.timedelta(seconds=1)
        prev_second = datetime.datetime.utcnow() - datetime.timedelta(seconds=2)
        _create_task(task_manager)
        ret = task_manager.list(created=(prev_second, now))
        assert not ret

    def test__list__updated(self, task_manager):
        now = datetime.datetime.utcnow() - datetime.timedelta(seconds=1)
        next_second = datetime.datetime.utcnow() + datetime.timedelta(seconds=1)
        task = _create_task(task_manager)
        ret = task_manager.list(updated=(now, next_second))
        assert ret[0].id == task.id

    def test__list__updated__invalid_bound(self, task_manager):
        now = datetime.datetime.utcnow() - datetime.timedelta(seconds=1)
        prev_second = datetime.datetime.utcnow() - datetime.timedelta(seconds=2)
        _create_task(task_manager)
        ret = task_manager.list(updated=(prev_second, now))
        assert not ret

    def test__list__author_query(self, task_manager):
        authors_list = [("ninja", 3), ("dude", 2), ("jagger", 0)]
        for author, amount in authors_list:
            tasks = [_create_task(task_manager, author=author, owner=author).id for _ in range(amount)]
            assert tasks == task_manager.list(author=author, order_by="+id", load=False)

    def test__exists__returns_true_for_correct_task_id(self, task_manager):
        tsk = _create_task(task_manager, "UNIT_TEST", owner="user")
        assert task_manager.exists(tsk.id)

    def test__exists__returns_false_for_incorrect_task_id(self, task_manager):
        assert not task_manager.exists("1234567890123456789")

    def test__stop__task_in_WAIT_states(self, task_manager):
        for status in ctt.Status.Group.WAIT:
            if status == ctt.Status.WAIT_MUTEX:
                continue
            task = _create_task(task_manager, owner="user", status=status)
            task.stop()
            assert task.status == ctt.Status.STOPPING

    def test__stop__task_in_EXECUTE_states(self, task_manager, client_manager):
        client_manager.load("just_host", True)
        for status in (
            ctt.Status.PREPARING,
            ctt.Status.EXECUTING,
            ctt.Status.TEMPORARY
        ):
            task = _create_task(task_manager, owner="user", status=status)
            task.host = "just_host"
            task_manager.update(task)
            task.stop()
            task = task_manager.load(task.id)
            assert task.status == ctt.Status.STOPPING
            assert task.lock_host == ""

    def test__stop__task_with_subtasks(self, task_manager, client_manager, test_task_2):
        parent_task = _create_task(task_manager, owner="user", status=ctt.Status.EXECUTING)
        sdk1_subtask = _create_task(task_manager, parent_id=parent_task.id, owner="user", status=ctt.Status.EXECUTING)
        sdk2_subtask = test_task_2(None)
        mapping.Task.objects(
            id=sdk2_subtask.id
        ).update(
            set__parent_id=parent_task.id,
            set__execution__status=ctt.Status.EXECUTING
        )
        parent_task.stop()
        subtasks = sorted(
            mapping.Task.objects(id__in=[sdk1_subtask.id, sdk2_subtask.id]).scalar("id", "execution__status")
        )
        assert subtasks == sorted([
            (sdk1_subtask.id, ctt.Status.STOPPING),
            (sdk2_subtask.id, ctt.Status.STOPPING)
        ])

    def test__restart__with_task_in_non_restartable_state__returns_False(self, task_manager):
        for status in ctt.Status:
            if not all((
                ctt.Status.can_switch(status, ctt.Status.ENQUEUING),
                status not in ctt.Status.Group.WAIT
            )):
                task = _create_task(task_manager, author="user", status=status)
                task.host = "just_host"
                task_manager.update(task)
                assert not task.restart(request=self.default_request)

    def test__restart__with_task_in_STOPPED_state__returns_True_and_task_go_to_ENQUEUING(self, task_manager):
        task = _create_task(task_manager, author="user", status=ctt.Status.STOPPED)
        task.host = "just_host"
        task_manager.update(task)
        assert task.restart(request=self.default_request)
        task = task_manager.load(task.id)
        assert task.status == ctt.Status.ENQUEUING

    def test__stat__with_task_in_restartable_state__returns_True_and_task_go_to_ENQUEUING(self, task_manager):
        for status in ctt.Status:
            if all((
                ctt.Status.can_switch(status, ctt.Status.ENQUEUING),
                status not in ctt.Status.Group.WAIT,
            )):
                task = _create_task(task_manager, author="user", owner="OTHER", status=status)
                task.host = "just_host"
                task_manager.update(task)
                assert task.restart(request=self.default_request)

                task = task_manager.load(task.id)
                assert task.status == ctt.Status.ENQUEUING

    def test__stat__with_task_in_restartable_state_and_wrong_user__raises_AuthorizationError(self, task_manager):
        for status in (ctt.Status.DRAFT, ctt.Status.STOPPED, ctt.Status.EXCEPTION):
            task = _create_task(task_manager, owner="user", status=status)
            task.host = "just_host"
            task_manager.update(task)
            with pytest.raises(common.errors.AuthorizationError):
                task.restart(request=_gen_custom_class(
                    "request", {
                        "user": _gen_custom_class(
                            "user",
                            {
                                "login": "wrong_user",
                                "super_user": False,
                            }
                        ),
                        "owner": "other_owner",
                    }
                ))

            task = task_manager.load(task.id)
            assert task.status not in (ctt.Status.ENQUEUING, ctt.Status.ENQUEUED)

    def test__load__with_correct_task_id__returns_correct_task_object(self, task_manager):
        task1 = _create_task(task_manager, owner="user1", host="host1")
        task1.enqueue = 1
        task1.descr = "Task1 descr"
        task1.info = "Task1 info"
        task1.hidden = 1
        task1.ctx["key1"] = "value1"
        task1.ctx["key2"] = 2
        task1.ctx["key3"] = {"a": "b", "c": 1.2, "d": {"x": "yyy"}}
        task_manager.update(task1)
        result1 = task_manager.load(task1.id)
        assert result1.timestamp > time.time() - 10
        task1.set_status(ctt.Status.EXECUTING, force=True)

        task2 = _create_task(task_manager, type="UNIT_TEST", owner="user2", host="host2")
        task2.parent_id = task1.id
        task_manager.update(task2)
        task2.set_status(ctt.Status.EXCEPTION, force=True)

        # run tests
        result1 = task_manager.load(task1.id)
        assert result1.timestamp > time.time() - 10
        assert result1.status == ctt.Status.EXECUTING
        assert result1.descr == "Task1 descr"
        assert result1.info == "Task1 info"
        assert result1.hidden == 1
        assert result1.parent_id is None
        assert result1.ctx["key1"] == "value1"
        assert result1.ctx["key2"] == 2
        assert result1.ctx["key3"]["d"]["x"] == "yyy"

        task_manager.load(task2.id)
        assert task2.info == ""
        assert task2.status == ctt.Status.EXCEPTION
        assert task2.hidden == 0
        assert task2.parent_id == task1.id

    def test__load__with_incorrect_task_id__returns_None(self, task_manager):
        assert task_manager.load("abcdefefacbdedabdfacedef") is None

    def test__load__with_absent_task_id__returns_None(self, task_manager):
        assert task_manager.load(507439011) is None

    def test__list_not_ready_tasks_dependencies(self, task_manager):
        task_1 = _create_task(task_manager)
        task_2 = _create_task(task_manager)
        task_res = _create_task(task_manager)
        res_11 = _create_real_resource(task_manager, mark_ready=False, task=task_res)
        res_12 = _create_real_resource(task_manager, mark_ready=False, task=task_res)
        res_21 = _create_real_resource(task_manager, mark_ready=False, task=task_res)
        res_22 = _create_real_resource(task_manager, mark_ready=False, task=task_res)
        task_manager.register_dep_resource(task_1.id, res_11.id)
        task_manager.register_dep_resource(task_1.id, res_12.id)
        task_manager.register_dep_resource(task_2.id, res_21.id)
        task_manager.register_dep_resource(task_2.id, res_22.id)
        deps = task_manager.list_not_ready_tasks_dependencies([task_1.id, task_2.id])
        deps_bench = {task_1.id: {res_11.id, res_12.id}, task_2.id: {res_21.id, res_22.id}}
        assert deps == deps_bench

    def test__clients_with_compatibility_info(self, task_manager, client_manager, serviceq):
        import yasandbox.controller
        clients = [_create_client(client_manager, "test_host{}".format(i)) for i in range(3)]
        tasks = [_create_task(task_manager) for _ in range(5)]
        yasandbox.controller.TaskQueue.qclient.sync(
            [
                (
                    task.id,
                    p,
                    [(i, c.hostname) for i, c in enumerate(clients)],
                    qtypes.TaskInfo(type=task.type, owner=task.owner)
                )
                for p, task in enumerate(tasks)
            ]
        )
        for i, task in enumerate(tasks):
            comp_clients = yasandbox.controller.TaskWrapper(task.mapping()).clients_with_compatibility_info()
            assert [
                (c[0], c[1]["queue"]) for c in comp_clients
            ] == [
                (c.hostname, [len(tasks) - i, len(tasks)]) for c in clients
            ]

    def test__list_with_descr(self, task_manager):
        task = _create_task(task_manager, parameters={"descr": "test task descr"})
        tt = task_manager.list(descr_mask="test")
        assert tt[0].descr == task.descr

    def test__audit(self, task_manager):
        task = _create_task(task_manager, author="Ninja")
        statuses = [task.Status.ENQUEUING, task.Status.ENQUEUED]
        for status in statuses:
            task.set_status(status, event="Testing status change: {}".format(status))
            time.sleep(0.01)
        statuses = [task.Status.DRAFT] + statuses
        history = task_manager.task_status_history(task.id)
        assert len(history) == len(statuses)
        for x in range(len(statuses)):
            note = history[x]
            assert note.status == statuses[x]
            if x < len(statuses) - 1:
                assert note.date < history[x + 1].date
            assert note.content == "Testing status change: {}".format(statuses[x]) if x != 0 else "Created"
            if note.author is not None:
                assert note.author == "Ninja"

    @pytest.mark.usefixtures("task_controller", "sdk2_dispatched_rest_su_session")
    def test__task_type_filter_by_client_tag_for_multios(self, task_manager, client_manager, monkeypatch):
        from sandbox.projects.sandbox import test_task
        import sandbox.yasandbox.proxy.client

        from sandbox.yasandbox import controller
        from sandbox.services.modules import hosts_cache_updater

        host_cache_updater = hosts_cache_updater.HostsCacheUpdater()
        monkeypatch.setattr(host_cache_updater, "api", common.rest.DispatchedClient())
        c = sandbox.yasandbox.proxy.client.Client("test_client", ncpu=8, ram=4096).save()

        c.update_tags([ctc.Tag.GENERIC, ctc.Tag.LINUX_LUCID, ctc.Tag.CORES16], c.TagsOp.SET)
        task_class = test_task.TestTask
        task = controller.TaskWrapper(_create_task(task_manager, type=task_class.type, host="").mapping())
        monkeypatch.setattr(task_class, "client_tags", ctc.Tag.LINUX_PRECISE)
        task.model.requirements.client_tags = ctc.Tag.LINUX_PRECISE
        allowed_hosts = controller.TaskQueue.task_hosts_list(task.model)[0]
        assert not allowed_hosts

        monkeypatch.setattr(task_class, "client_tags", ctc.Tag.LINUX_LUCID)
        task.model.requirements.client_tags = ctc.Tag.LINUX_LUCID
        del task.effective_client_tags
        del task.model.__effective_client_tags__
        allowed_hosts = controller.TaskQueue.task_hosts_list(task.model)[0]
        assert len(allowed_hosts) == 1
        assert sandbox.yasandbox.proxy.client.Client.restore(allowed_hosts[0]) == c

        c.update_tags([ctc.Tag.GENERIC, ctc.Tag.LXC, ctc.Tag.CORES16], c.TagsOp.SET)
        host_cache_updater.tick()

        for tag in ctc.Tag.Group.OS:
            task.model.requirements.client_tags = tag
            del task.effective_client_tags
            del task.model.__effective_client_tags__
            allowed_hosts = controller.TaskQueue.task_hosts_list(task.model)[0]
            if tag in ctc.Tag.Group.LINUX:
                assert len(allowed_hosts) == 1, tag
                assert sandbox.yasandbox.proxy.client.Client.restore(allowed_hosts[0]) == c, tag
            else:
                assert not allowed_hosts
