import json
import uuid
import mock
import decimal
import inspect

import pytest
import httplib
import threading as th

import sandbox.common.types.task as ctt
import sandbox.common.types.notification as ctn

from sandbox import sdk2
from sandbox.sdk2 import internal
from sandbox.serviceq import types as qtypes
from sandbox.common import itertools as common_itertools

from sandbox.yasandbox.database import mapping
from sandbox.yasandbox import controller

from sandbox.serviceq.tests.client import utils as qclient_utils


# noinspection PyMethodMayBeStatic
class TestDraft(object):

    @pytest.mark.usefixtures("server")
    def test__task_init(self, monkeypatch):
        model = mapping.Task(
            type="TEST_TASK_2",
            author="guest",
            parameters=mapping.Task.Parameters(
                input=[mapping.Task.Parameters.Parameter(key="test_get_arcadia_url", value="upyachka")]
            )
        )
        controller.TaskWrapper(model).init_model()
        model.save()

        def cast(*_):
            assert False

        for _, param_cls in inspect.getmembers(sdk2.parameters, inspect.isclass):
            if issubclass(param_cls, internal.parameters.Parameter) and hasattr(param_cls, "cast"):
                monkeypatch.setattr(param_cls, "cast", classmethod(cast))

        task = sdk2.Task.from_model(model)

        assert model.type == task.type.name
        assert task.Parameters.client_tags == task.type.Parameters.client_tags.default
        assert task.Parameters.owner == task.type.Parameters.owner.default
        assert task.Parameters.description == task.type.Parameters.description.default
        assert task.Parameters.radio_group == task.type.Parameters.radio_group.default
        assert task.Parameters.test_get_arcadia_url == "upyachka"

        task = sdk2.Task[model.id]

        assert task.id == model.id
        assert model.type == task.type.name
        assert task.Parameters.client_tags == task.type.Parameters.client_tags.default
        assert task.Parameters.owner == task.type.Parameters.owner.default
        assert task.Parameters.description == task.type.Parameters.description.default
        assert task.Parameters.radio_group == task.type.Parameters.radio_group.default
        assert task.Parameters.test_get_arcadia_url == "upyachka"

    @pytest.mark.parametrize("task_type", ["TEST_TASK", "TEST_TASK_2"])
    @pytest.mark.usefixtures("server")
    def test__common_params(self, task_type):

        model = mapping.Task(
            type=task_type,
            author="guest",
            owner="guest",
            description="Some description",
        )
        controller.TaskWrapper(model).init_model()
        model.save()

        task = sdk2.Task[model.id]

        assert task.owner == model.owner
        assert task.Parameters.priority == model.priority
        assert task.Parameters.description == model.description

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    def test__notifications(self, rest_session_login, test_task_2):
        task_params = {
            "owner": rest_session_login,
            "description": u"Test task",
        }

        task0 = test_task_2(None, **task_params)
        task0.Parameters.notifications = []
        task0.save()

        task1 = test_task_2(None, **task_params)
        task1.Parameters.notifications = sdk2.Notification(
            statuses=[ctt.Status.Group.FINISH],
            recipients=["guest"],
            transport=ctn.Transport.EMAIL
        )
        task1.save()

        juggler_recipient = "host=test.host&service=test_service"
        test_tag = "test_tag"
        task2 = test_task_2(None, **task_params)
        task2.Parameters.notifications = [
            sdk2.Notification(
                statuses=[ctt.Status.WAIT_TASK, ctt.Status.Group.FINISH],
                recipients=["aaa", "bbb"],
                transport=ctn.Transport.EMAIL,
            ),
            sdk2.Notification(
                statuses=[ctt.Status.Group.WAIT],
                recipients=["ccc"],
                transport=ctn.Transport.TELEGRAM,
            ),
            sdk2.Notification(
                statuses=[ctt.Status.Group.EXECUTE],
                recipients=[juggler_recipient],
                transport=ctn.Transport.JUGGLER,
                check_status=ctn.JugglerStatus.OK,
                juggler_tags=[test_tag]
            ),
        ]
        task2.save()

        nt0 = sdk2.Task[task0.id].Parameters.notifications
        nt1 = sdk2.Task[task1.id].Parameters.notifications
        nt2 = sdk2.Task[task2.id].Parameters.notifications

        assert len(nt0) == 0
        assert len(nt1) == 1
        assert set(nt1[0].statuses) == ctt.Status.Group.expand(ctt.Status.Group.FINISH)
        assert (nt1[0].recipients, nt1[0].transport) == (["guest"], ctn.Transport.EMAIL)
        assert len(nt2) == 3
        assert set(nt2[0].statuses) == ctt.Status.Group.expand([ctt.Status.Group.FINISH, ctt.Status.WAIT_TASK])
        assert (set(nt2[0].recipients), nt2[0].transport) == ({"aaa", "bbb"}, ctn.Transport.EMAIL)
        assert set(nt2[1].statuses) == ctt.Status.Group.expand(ctt.Status.Group.WAIT)
        assert (nt2[1].recipients, nt2[1].transport) == (["ccc"], ctn.Transport.TELEGRAM)
        assert set(nt2[2].statuses) == ctt.Status.Group.expand(ctt.Status.Group.EXECUTE)
        assert nt2[2].recipients == [juggler_recipient]
        assert nt2[2].juggler_tags == [test_tag]

    def _compare_tasks(self, tasks, query):
        assert set(t.id for t in tasks) == set(t.id for t in query)

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    def test__find(self, task_controller, rest_session_login, test_task_2):
        task_params = {
            "owner": rest_session_login,
            "description": u"Test task",
            "string_parameter": u"Test task"
        }
        task0 = test_task_2(None, privileged=True, **task_params)
        task0.Parameters.tags = ["zzz"]
        task0.save()

        task1 = test_task_2(None, wait_time=5, **task_params)
        task1.Parameters.tags = ["aaa", "bbb"]
        task1.save()

        task2 = test_task_2(
            None, wait_time=5, privileged=True,
            send_email_to_recipient=True, email_recipient="foo",
            **task_params
        )
        task2.Parameters.description = "Something else"
        task2.Parameters.string_parameter = "Something else"
        task2.Parameters.tags = ["bbb", "ccc"]
        task2.save()

        ids = [t.id for t in (task0, task1, task2)]
        query1 = sdk2.Task.find(
            id=ids, status=ctt.Status.DRAFT,
            input_parameters={"string_parameter": u"Test task"}
        ).limit(len(ids))
        self._compare_tasks([task0, task1], query1)

        query2 = sdk2.Task.find(
            id=ids, type=test_task_2,
            input_parameters={"wait_time": 5, "string_parameter": u"Test task"}
        ).limit(len(ids))
        self._compare_tasks([task1], query2)

        query3 = sdk2.Task.find(
            id=ids,
            input_parameters={"privileged": True, "wait_time": 5, "email_recipient": "foo"}
        ).limit(len(ids))
        self._compare_tasks([task2], query3)

        query4 = sdk2.Task.find(
            id=ids,
            input_parameters={"privileged": True, "email_recipient": "foo"},
            any_params=True
        ).limit(len(ids))
        self._compare_tasks([task0, task2], query4)

        task_controller.Model.objects(id=task0.id).update(set__execution__status=ctt.Status.ENQUEUED)

        query5 = list(sdk2.Task.find(id=ids).limit(len(ids)).order(-sdk2.Task.status, -sdk2.Task.id))
        assert query5[0].id == task0.id
        assert query5[1].id == task2.id
        assert query5[2].id == task1.id

        # search by tags
        self._compare_tasks([task1, task2], sdk2.Task.find(tags=["bbb"]).limit(len(ids)))
        self._compare_tasks([task0, task1], sdk2.Task.find(tags=["zzz", "aaa"]).limit(len(ids)))
        self._compare_tasks([], sdk2.Task.find(tags=["yyy"]).limit(len(ids)))
        self._compare_tasks([task1], sdk2.Task.find(tags=["bbb", "aaa"], all_tags=True).limit(len(ids)))

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    def test__on_save(self, rest_session_login, test_task_2, monkeypatch):
        import yasandbox.controller
        task_params = {
            "owner": rest_session_login,
            "description": u"Test task",
        }
        task0 = test_task_2(None, **task_params)
        task0.save()

        tw = yasandbox.controller.TaskWrapper(yasandbox.controller.Task.get(task0.id))

        def on_save_notifications(self_):
            self_.Parameters.notifications = [
                sdk2.Notification(
                    statuses=[ctt.Status.WAIT_TASK, ctt.Status.Group.FINISH],
                    recipients=["aaa", "bbb"],
                    transport=ctn.Transport.EMAIL,
                ),
                sdk2.Notification(
                    statuses=[ctt.Status.Group.WAIT],
                    recipients=["ccc"],
                    transport=ctn.Transport.TELEGRAM,
                ),
            ]

        monkeypatch.setattr(test_task_2, "on_save", on_save_notifications)
        tw.on_save()
        tw.save()

        nt = sdk2.Task[task0.id].reload().Parameters.notifications

        assert len(nt) == 2
        assert set(nt[0].statuses) == ctt.Status.Group.expand([ctt.Status.Group.FINISH, ctt.Status.WAIT_TASK])
        assert (set(nt[0].recipients), nt[0].transport) == ({"aaa", "bbb"}, ctn.Transport.EMAIL)
        assert set(nt[1].statuses) == ctt.Status.Group.expand(ctt.Status.Group.WAIT)
        assert (nt[1].recipients, nt[1].transport) == (["ccc"], ctn.Transport.TELEGRAM)

    def test__sdk1_params(self, rest_session_login, test_task_2, sdk2_dispatched_rest_session):
        from projects.sandbox.test_task_21 import TestTask21, EXCLUDE_PARAMETERS

        task_params = {
            "owner": rest_session_login,
            "description": u"Test task",
            "create_sub_task": True
        }
        task0 = test_task_2(None, **task_params)
        task1 = sdk2.Task[TestTask21.type](None, **task_params)

        params0 = [
            p for p in sdk2_dispatched_rest_session.task[task0.id].custom.fields[:]
            if p["name"] not in EXCLUDE_PARAMETERS
        ]
        params1 = sdk2_dispatched_rest_session.task[task1.id].custom.fields[:]

        assert len(params0) == len(params1)

        skip_value_check = set()
        for i in xrange(len(params0)):
            p0, p1 = params0[i], params1[i]
            assert p0["name"] == p1["name"]
            if p0["name"] in skip_value_check or p0.get("output"):
                continue
            assert p0 == p1
            sub_fields = p0.get("sub_fields")
            if sub_fields:
                for check, fields in sub_fields.items():
                    if str(p0["value"]).lower() != check:
                        skip_value_check.update(fields)

    def test__sdk2_params(self, rest_session_login, test_task_2, sdk2_dispatched_rest_session):
        task_params = {
            "owner": rest_session_login,
            "description": u"Test task",
            "json_parameter": {"key": "value"}
        }
        task = test_task_2(None, **task_params)
        assert task.Parameters.json_parameter == {"key": "value"}

        json_parameter_str = json.dumps(task_params["json_parameter"])
        task_params["json_parameter"] = json_parameter_str
        task = test_task_2(None, **task_params)
        assert task.Parameters.json_parameter == json_parameter_str
        with pytest.raises(TypeError):
            task.Parameters.json_parameter = {"key": decimal.Decimal(1.5)}

        task_params["json_parameter"] = {"key": decimal.Decimal(1.5)}
        with pytest.raises(TypeError):
            test_task_2(None, **task_params)

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session", "task_controller", "serviceq")
    def test__hints(self, rest_session_login, local_host_client):
        from . import TaskWithHintedParameters
        task = TaskWithHintedParameters(
            None,
            owner=rest_session_login,
            description="Test task",
            hinted=124,
            hint_on_enqueue="enqueued",
            hint_for_output="output",
            hints=["aaa"]
        )
        assert task.hints == {"aaa", "124"}

        task._sdk_server.task[task.id].hints(["rest"])
        assert set(task._sdk_server.task[task.id][:]["hints"]) == {"124", "aaa", "rest"}

        task.Parameters.hinted = 420
        task.save()
        assert set(task._sdk_server.task[task.id][:]["hints"]) == {"420", "aaa", "rest"}

        task.enqueue()
        assert set(task._sdk_server.task[task.id][:]["hints"]) == {"420", "aaa", "rest", "enqueued", "output"}
        task.reload()
        assert task.hints == {"420", "aaa", "rest", "enqueued", "output"}

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session", "task_controller")
    def test__caches(self, rest_session_login):
        from . import MaybeCachesTask, NoCachesTask
        maybe_caches_task = MaybeCachesTask(
            None,
            owner=rest_session_login,
            description="Maybe caches task"
        )
        no_caches_task = NoCachesTask(
            None,
            owner=rest_session_login,
            description="No caches task"
        )
        assert maybe_caches_task.Requirements.Caches.__getstate__() is None
        assert no_caches_task.Requirements.Caches.__getstate__() == {}
        rest = maybe_caches_task._sdk_server
        assert rest.task[maybe_caches_task.id][:]["requirements"].get("caches", None) is None
        assert rest.task[no_caches_task.id][:]["requirements"].get("caches") == {}

    def test__sdk2_scheduler(self, rest_session, rest_session_login, scheduler_controller, test_task_2):
        # No scheduler
        task = test_task_2(None)
        assert task.scheduler is None

        # Via API
        scheduler = scheduler_controller.create("TEST_TASK_2", owner=rest_session_login, author=rest_session_login)
        task_data = rest_session.task(scheduler_id=scheduler["id"])
        task = sdk2.Task[task_data["id"]]
        assert task.scheduler == -scheduler.id

        # Via model
        task_model = mapping.Task.objects.with_id(task.id)
        task = sdk2.Task.from_model(task_model)
        assert task.scheduler == -scheduler.id


# noinspection PyMethodMayBeStatic
class TestContext(object):
    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    def test__mangling(self, test_task_2):
        task = test_task_2(None)

        class TestTask2(object):
            def __init__(self):
                task.Context.__qwer = 123

            @property
            def value(self):
                return task.Context.__qwer

        class C(object):
            def __init__(self):
                task.Context.__asdf = 321

            @property
            def value(self):
                return task.Context.__asdf

        assert TestTask2().value == 123
        assert C().value == 321
        assert task.Context.__values__["__qwer"] == 123
        assert "__asdf" not in task.Context.__values__
        assert task.Context.__values__["_C__asdf"] == 321

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    def test__init(self, rest_session_login, test_task_2):
        task_params = {
            "owner": rest_session_login,
            "description": u"Test task",
            "foobar": "quux"
        }
        task = test_task_2(None, **task_params)
        assert task.Context.foobar == "quux"

        # test that context works even when task is restored from server
        sdk2.Task.__cache__.pop(task.id, None)
        task2 = sdk2.Task[task.id]
        assert task2.Context.foobar == "quux"


# noinspection PyMethodMayBeStatic
class TestRequirements(object):
    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    def test__semaphores(self, test_task_2):
        with pytest.raises(ValueError):
            ctt.Semaphores()
        with pytest.raises(ValueError):
            ctt.Semaphores([""])
        with pytest.raises(ValueError):
            ctt.Semaphores([("sem", 0)])
        with pytest.raises(ValueError):
            ctt.Semaphores([("sem", -1)])
        with pytest.raises(ValueError):
            ctt.Semaphores(["sem"], "")
        with pytest.raises(ValueError):
            ctt.Semaphores(["sem"], release=[])
        with pytest.raises(ValueError):
            ctt.Semaphores(["sem"], "qwer")
        with pytest.raises(ValueError):
            ctt.Semaphores(["sem"], ["qwer"])
        with pytest.raises(ValueError):
            ctt.Semaphores(["sem"], ["SUCCESS", "qwer"])

        sems = ctt.Semaphores(["sem1"])

        task = test_task_2(None)

        task.Requirements.semaphores = sems
        task.save()

        task = sdk2.Task[task.id]
        assert task.Requirements.semaphores == sems

        sems = ctt.Semaphores(["sem1", ("sem2", 10)], release="SUCCESS")

        task.Requirements.semaphores = sems
        task.save()

        task = sdk2.Task[task.id]
        assert task.Requirements.semaphores == sems

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    def test__create_with_requirements(self, test_task_2):
        req = {"disk_space": 123456, "ram": 654321, "cores": 10}
        task = test_task_2(None, __requirements__=req)
        task.reload()

        assert task.Requirements.disk_space == req["disk_space"]
        assert task.Requirements.ram == req["ram"]
        assert task.Requirements.cores == req["cores"]

        with pytest.raises(AttributeError):
            test_task_2(None, __requirements__={"foo": True})

    @staticmethod
    def __create_task(test_task_2, task_controller, semaphores):
        task = test_task_2(None)
        task.Requirements.semaphores = semaphores
        task.save()
        task_controller.Model.objects(id=task.id).update(set__execution__status=ctt.Status.ENQUEUED)
        return sdk2.Task[task.id]

    @pytest.mark.usefixtures("server", "sdk2_dispatched_rest_session", "semaphore_controller")
    def test__semaphores_simple(self, serviceq, test_task_2, task_controller, rest_session, gui_session):
        import yasandbox.controller

        ui_rest_session = rest_session.copy() << rest_session.HEADERS(gui_session)

        sem_id = serviceq.create_semaphore(dict(name="test_sem", owner="QWER", capacity=0))[0]
        tasks = [self.__create_task(test_task_2, task_controller, ctt.Semaphores(["test_sem"])) for _ in xrange(3)]
        for task in tasks:
            serviceq.push(
                task.id, 0, [(0, "host")],
                task_info=qtypes.TaskInfo(semaphores=task.Requirements.semaphores, owner=task.owner)
            )
        tids = [_.id for _ in tasks]
        assert serviceq.semaphore_values([sem_id]) == [0]
        assert serviceq.semaphore_waiters(tids) == []
        assert {_["status"] for _ in rest_session.task[{"limit": len(tasks)}]["items"]} == {ctt.Status.ENQUEUED}
        assert {_["status"] for _ in ui_rest_session.task[{"limit": len(tasks)}]["items"]} == {ctt.Status.ENQUEUED}
        assert not list(qclient_utils.qpop(serviceq, "host"))
        assert sorted(serviceq.semaphore_waiters(tids)) == tids
        assert {_["status"] for _ in rest_session.task[{"limit": len(tasks)}]["items"]} == {ctt.Status.ENQUEUED}
        assert {_["status"] for _ in ui_rest_session.task[{"limit": len(tasks)}]["items"]} == {ctt.Status.WAIT_MUTEX}
        assert rest_session.task[tasks[0].id].read()["status"] == ctt.Status.ENQUEUED
        assert ui_rest_session.task[tasks[0].id].read()["status"] == ctt.Status.WAIT_MUTEX

        serviceq.update_semaphore(sem_id, dict(capacity=2))
        assert {_["status"] for _ in rest_session.task[{"limit": len(tasks)}]["items"]} == {ctt.Status.ENQUEUED}
        assert {_["status"] for _ in ui_rest_session.task[{"limit": len(tasks)}]["items"]} == {ctt.Status.WAIT_MUTEX}
        assert len(list(qclient_utils.qpop(serviceq, "host"))) == 2
        assert {_["status"] for _ in rest_session.task[{"limit": len(tasks)}]["items"]} == {ctt.Status.ENQUEUED}
        assert {_["status"] for _ in ui_rest_session.task[{"limit": len(tasks)}]["items"]} == {ctt.Status.WAIT_MUTEX}
        gen = qclient_utils.qpop(serviceq, "host")
        tid1 = gen.next()[0]
        qclient_utils.qcommit(gen)
        assert serviceq.semaphore_values([sem_id]) == [1]
        assert set(serviceq.semaphore_waiters(tids)) == set(tids) - {tid1}
        assert {_["status"] for _ in rest_session.task[{"limit": len(tasks)}]["items"]} == {ctt.Status.ENQUEUED}
        assert {_["status"] for _ in ui_rest_session.task[{"limit": len(tasks)}]["items"]} == {
            ctt.Status.ENQUEUED, ctt.Status.WAIT_MUTEX
        }
        gen = qclient_utils.qpop(serviceq, "host")
        tid2 = gen.next()[0]
        qclient_utils.qcommit(gen)
        assert serviceq.semaphore_values([sem_id]) == [2]
        assert set(serviceq.semaphore_waiters(tids)) == set(tids) - {tid1, tid2}
        assert not list(qclient_utils.qpop(serviceq, "host"))
        assert {_["status"] for _ in rest_session.task[{"limit": len(tasks)}]["items"]} == {ctt.Status.ENQUEUED}
        assert {_["id"]: _["status"] for _ in ui_rest_session.task[{"limit": len(tasks)}]["items"]} == {
            _.id: ctt.Status.ENQUEUED if _.id in (tid1, tid2) else ctt.Status.WAIT_MUTEX
            for _ in tasks
        }
        assert len(ui_rest_session.task.read(status=ctt.Status.WAIT_MUTEX, limit=100)["items"]) == 1
        items = ui_rest_session.task.read(status=[ctt.Status.WAIT_MUTEX, ctt.Status.ENQUEUED], limit=100)["items"]
        assert len(items) == 3

        # tests for /trunk/arcadia/sandbox/yasandbox/api/json/task.py:Task.list
        assert len(rest_session.task.read(semaphore_waiters=sem_id, limit=100)["items"]) == 1
        assert len(rest_session.task.read(semaphore_acquirers=sem_id, limit=100)["items"]) == 2
        # intersections
        assert len(rest_session.task.read(id=(tid1, tid2), semaphore_acquirers=sem_id, limit=100)["items"]) == 2
        assert len(rest_session.task.read(id=tid1, semaphore_acquirers=sem_id, limit=100)["items"]) == 1
        assert len(rest_session.task.read(id=tids, semaphore_acquirers=sem_id, limit=100)["items"]) == 2
        assert len(rest_session.task.read(id=tids, semaphore_waiters=sem_id, limit=100)["items"]) == 1

        assert ui_rest_session.task.read(status=ctt.Status.ENQUEUED, limit=100)["items"] == items
        yasandbox.controller.TaskWrapper(task_controller.get(tid1)).set_status(ctt.Status.SUCCESS, force=True)
        assert {_["status"] for _ in rest_session.task[{"limit": len(tasks)}]["items"]} == {
            ctt.Status.ENQUEUED, ctt.Status.SUCCESS
        }
        assert {_["id"]: _["status"] for _ in ui_rest_session.task[{"limit": len(tasks)}]["items"]} == {
            tid1: ctt.Status.SUCCESS,
            tid2: ctt.Status.ENQUEUED,
            next(iter(set(tids) - {tid1, tid2})): ctt.Status.WAIT_MUTEX
        }
        assert serviceq.semaphore_values([sem_id]) == [1]
        gen = qclient_utils.qpop(serviceq, "host")
        tid3 = gen.next()[0]
        qclient_utils.qcommit(gen)
        assert serviceq.semaphore_values([sem_id]) == [2]
        assert not list(qclient_utils.qpop(serviceq, "host"))
        yasandbox.controller.TaskWrapper(task_controller.get(tid2)).set_status(ctt.Status.SUCCESS, force=True)
        assert serviceq.semaphore_values([sem_id]) == [1]
        yasandbox.controller.TaskWrapper(task_controller.get(tid3)).set_status(ctt.Status.SUCCESS, force=True)
        assert serviceq.semaphore_values([sem_id]) == [0]
        yasandbox.controller.TaskWrapper(task_controller.get(tid3)).set_status(ctt.Status.RELEASED, force=True)
        assert serviceq.semaphore_values([sem_id]) == [0]

    @pytest.mark.usefixtures("server", "sdk2_dispatched_rest_session", "semaphore_controller")
    def test__two_semaphores(self, serviceq, test_task_2, task_controller):
        import yasandbox.controller

        sem1_id, _ = serviceq.create_semaphore(dict(name="test_sem1", owner="QWER", capacity=2))
        sem2_id, _ = serviceq.create_semaphore(dict(name="test_sem2", owner="QWER", capacity=2))

        task1 = self.__create_task(test_task_2, task_controller, ctt.Semaphores([("test_sem1", 1), ("test_sem2", 1)]))
        serviceq.push(
            task1.id, 0, [(0, "host")],
            task_info=qtypes.TaskInfo(semaphores=task1.Requirements.semaphores, owner=task1.owner)
        )
        task2 = self.__create_task(test_task_2, task_controller, ctt.Semaphores([("test_sem1", 1), ("test_sem2", 2)]))
        serviceq.push(
            task2.id, 0, [(0, "host")],
            task_info=qtypes.TaskInfo(semaphores=task2.Requirements.semaphores, owner=task2.owner)
        )
        assert serviceq.semaphore_values([sem1_id, sem2_id]) == [0, 0]
        gen = qclient_utils.qpop(serviceq, "host")
        tid = gen.next()[0]
        qclient_utils.qcommit(gen)
        assert tid == task1.id
        assert not list(qclient_utils.qpop(serviceq, "host"))
        assert serviceq.semaphore_values([sem1_id, sem2_id]) == [1, 1]
        common_itertools.progressive_waiter(
            0, 0.2, 10, lambda: bool(mapping.Task.objects.with_id(task1.id).acquired_semaphore)
        )
        yasandbox.controller.TaskWrapper(task_controller.get(task1.id)).set_status(ctt.Status.SUCCESS, force=True)
        assert serviceq.semaphore_values([sem1_id, sem2_id]) == [0, 0]
        gen = qclient_utils.qpop(serviceq, "host")
        tid = gen.next()[0]
        qclient_utils.qcommit(gen)
        assert tid == task2.id
        assert not list(qclient_utils.qpop(serviceq, "host"))
        assert serviceq.semaphore_values([sem1_id, sem2_id]) == [1, 2]

    @pytest.mark.usefixtures("server", "sdk2_dispatched_rest_session", "semaphore_controller")
    def test__partial_semaphore_acquire(self, serviceq, test_task_2, task_controller):
        sem1_id, _ = serviceq.create_semaphore(dict(name="test_sem1", owner="OWNER", capacity=2))
        sem2_id, _ = serviceq.create_semaphore(dict(name="test_sem2", owner="OWNER", capacity=2))

        task1 = self.__create_task(test_task_2, task_controller, ctt.Semaphores([("test_sem1", 1), ("test_sem2", 1)]))
        serviceq.push(
            task1.id, 0, [(0, "host1"), (1, "host2")],
            task_info=qtypes.TaskInfo(semaphores=task1.Requirements.semaphores, owner="OWNER")
        )
        task2 = self.__create_task(test_task_2, task_controller, ctt.Semaphores([("test_sem1", 1), ("test_sem2", 2)]))
        serviceq.push(
            task2.id, 0, [(1, "host1"), (0, "host2")],
            task_info=qtypes.TaskInfo(semaphores=task2.Requirements.semaphores, owner="OWNER")
        )
        host_info = qtypes.HostInfo(
            capabilities=qtypes.ComputingResources(disk_space=1),
            free=qtypes.ComputingResources(),
        )

        assert list(serviceq.task_to_execute_it("host1", host_info)) == [[task2.id, 1], [task1.id, 0]]
        assert list(serviceq.task_to_execute_it("host2", host_info)) == [[task1.id, 1], [task2.id, 0]]

        tte1 = serviceq.task_to_execute("host1", host_info)
        tte1_it = serviceq.task_to_execute_it("host1", host_info)
        tte2 = serviceq.task_to_execute("host2", host_info)
        tte2_it = serviceq.task_to_execute_it("host2", host_info)
        tte1.next()
        tte2.next()

        item1 = tte1_it.send(None)
        assert item1 == [task2.id, 1]
        item2 = tte2_it.send(None)
        assert item2 == [task1.id, 1]

        assert tte2.send((item2[0], uuid.uuid4().hex)) == qtypes.QueueIterationResult.ACCEPTED

        assert list(serviceq.task_to_execute_it("host1", host_info)) == []

        assert tte1.send((item1[0], uuid.uuid4().hex)) == qtypes.QueueIterationResult.SKIP_TASK

        assert serviceq.semaphore_values([sem1_id, sem2_id]) == [1, 1]

    @pytest.mark.usefixtures("server", "sdk2_dispatched_rest_session")
    def test__auto_semaphores(self, serviceq, test_task_2, task_controller, semaphore_controller):
        task = self.__create_task(
            test_task_2, task_controller, ctt.Semaphores([("test_sem1", 1, 1), ("test_sem2", 2, 7)])
        )
        assert semaphore_controller.Model.objects.count() == 0
        sem0_id, _ = serviceq.create_semaphore(dict(name="test_sem0", owner="QWER", capacity=2))
        serviceq.push(
            task.id, 0, [(0, "host")],
            task_info=qtypes.TaskInfo(semaphores=task.Requirements.semaphores, owner=task.owner)
        )
        assert common_itertools.progressive_waiter(
            0, 1, 5, lambda: len(list(semaphore_controller.Model.objects)) == 3
        )[0]

        sems = list(semaphore_controller.Model.objects)
        assert len(sems) == 3

        assert sems[0].id == sem0_id
        assert sems[0].name == "test_sem0"
        assert sems[0].owner == "QWER"
        assert sems[0].auto is False
        assert sems[0].capacity == 2

        assert sems[1].name == "test_sem1"
        assert sems[1].owner == task.owner
        assert sems[1].auto is True
        assert sems[1].capacity == 1

        assert sems[2].name == "test_sem2"
        assert sems[2].owner == task.owner
        assert sems[2].auto is True
        assert sems[2].capacity == 7

    @pytest.mark.usefixtures("server", "sdk2_dispatched_rest_session", "semaphore_controller")
    def test__concurent_semaphores(self, serviceq, test_task_2, task_controller):
        num_tasks = 2

        sem_id = serviceq.create_semaphore(dict(name="test_sem", owner="QWER", capacity=num_tasks))[0]
        tasks = [
            self.__create_task(test_task_2, task_controller, ctt.Semaphores(["test_sem"]))
            for _ in xrange(num_tasks)
        ]
        tids = sorted(t.id for t in tasks)
        hosts = [(0, "host{}".format(i)) for i in xrange(num_tasks)]
        for i, task in enumerate(tasks):
            serviceq.push(
                task.id, 0, hosts,
                task_info=qtypes.TaskInfo(semaphores=task.Requirements.semaphores, owner="O{}".format(i))
            )

        got_tids = []

        def getajob(host):
            job_id = uuid.uuid4().hex
            host_info = qtypes.HostInfo(
                capabilities=qtypes.ComputingResources(disk_space=1),
                free=qtypes.ComputingResources(),
            )
            task_to_execute = serviceq.task_to_execute(host, host_info)
            task_to_execute_it = serviceq.task_to_execute_it(host, host_info)
            try:
                task_to_execute.next()
            except StopIteration:
                return
            result = None
            while True:
                item = task_to_execute_it.send(result)
                if item is None:
                    task_to_execute.send((None, None))
                    task_to_execute.send(task_to_execute_it.wait())
                    break
                tid, score = item
                result = task_to_execute.send((tid, job_id))
                if result != qtypes.QueueIterationResult.ACCEPTED:
                    continue
                task_to_execute_it.send(result)
                task_to_execute.send((None, None))
                task_to_execute.send(task_to_execute_it.wait())
                got_tids.append(tid)
                break

        threads = [th.Thread(target=getajob, args=(h[1],)) for h in hosts]
        map(lambda _: _.start(), threads)
        map(lambda _: _.join(5), threads)
        assert len(got_tids) == num_tasks
        assert sorted(got_tids) == tids
        assert serviceq.semaphore_values([sem_id]) == [num_tasks]
        assert sorted([_[0] for _ in serviceq.semaphore_tasks(sem_id)]) == tids

        threads = [
            th.Thread(
                target=lambda _: (
                    task_controller.Model.objects(id=_).update_one(set__execution__status=ctt.Status.SUCCESS),
                    serviceq.release_semaphores(_, ctt.Status.ENQUEUED, ctt.Status.SUCCESS)
                ),
                args=(_,)
            )
            for _ in got_tids
        ]
        map(lambda _: _.start(), threads)
        map(lambda _: _.join(5), threads)
        assert serviceq.semaphore_values([sem_id]) == [0]
        assert sorted([_[0] for _ in serviceq.semaphore_tasks(sem_id)]) == []

    @pytest.mark.usefixtures("server", "sdk2_dispatched_rest_session", "semaphore_controller")
    def test__semaphores_changed_on_enqueue(self, serviceq, test_task_2, task_controller):
        sem1_id, _ = serviceq.create_semaphore(dict(name="test_sem1", owner="QWER", capacity=1))
        sem2_id, _ = serviceq.create_semaphore(dict(name="test_sem2", owner="QWER", capacity=1))
        task = self.__create_task(test_task_2, task_controller, None)

        serviceq.push(task.id, 0, [(0, "host")], task_info=qtypes.TaskInfo(
            semaphores=ctt.Semaphores(["test_sem1"]), owner="QWER"
        ))

        job_id = uuid.uuid4().hex
        gen = qclient_utils.qpop(serviceq, "host", job_id=job_id)
        assert gen.next()[0] == task.id
        qclient_utils.qcommit(gen)
        assert serviceq.semaphore_values([sem1_id, sem2_id]) == [1, 0]

        serviceq.execution_completed(job_id)
        serviceq.push(task.id, 0, [(0, "host")], task_info=qtypes.TaskInfo(
            semaphores=ctt.Semaphores(["test_sem2"]), owner="QWER"
        ))

        gen = qclient_utils.qpop(serviceq, "host")
        assert gen.next()[0] == task.id
        qclient_utils.qcommit(gen)
        assert serviceq.semaphore_values([sem1_id, sem2_id]) == [0, 1]

    @pytest.mark.usefixtures("server", "sdk2_dispatched_rest_session", "semaphore_controller")
    def test__semaphores_duplication(self, serviceq, test_task_2, task_controller):
        serviceq.create_semaphore(dict(name="test_sem", owner="QWER", capacity=1))
        task = self.__create_task(test_task_2, task_controller, ctt.Semaphores([("test_sem",), ("test_sem",)]))
        serviceq.push(
            task.id, 0, [(0, "host")],
            task_info=qtypes.TaskInfo(semaphores=task.Requirements.semaphores, owner=task.owner)
        )
        gen = qclient_utils.qpop(serviceq, "host")
        gen.next()
        qclient_utils.qcommit(gen)  # does not raise QSemaphoreConflict

    @pytest.mark.usefixtures("server", "sdk2_dispatched_rest_session", "semaphore_controller")
    def test__semaphores_release_despite_status(
        self, serviceq, test_task_2, task_controller, rest_session, task_session
    ):
        sem_id, _ = serviceq.create_semaphore(dict(name="test_sem", owner="QWER", capacity=1))
        task = self.__create_task(test_task_2, task_controller, ctt.Semaphores([("test_sem",)]))
        serviceq.push(
            task.id, 0, [(0, "host")],
            task_info=qtypes.TaskInfo(semaphores=task.Requirements.semaphores, owner=task.owner)
        )
        gen = qclient_utils.qpop(serviceq, "host")
        gen.next()
        qclient_utils.qcommit(gen)

        assert serviceq.semaphore_values([sem_id]) == [1]

        with pytest.raises(rest_session.HTTPError) as ex:
            sdk2.Requirements.semaphores.release()
        assert ex.value.status == httplib.FORBIDDEN

        task_session(rest_session, task.id)
        sdk2.Requirements.semaphores.release()

        assert serviceq.semaphore_values([sem_id]) == [0]

        mapping.Task.objects(id=task.id).update_one(set__execution__status=ctt.Status.SUCCESS),
        assert serviceq.release_semaphores(task.id, ctt.Status.ENQUEUED, ctt.Status.SUCCESS) is False

        assert serviceq.semaphore_values([sem_id]) == [0]

        # attempt to release semaphores on the task, which has not acquired them
        assert serviceq.release_semaphores(task.id + 1, None, None) is False

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    def test__disk_space(self, test_task_2):
        task = test_task_2(None)
        orig_disk_space = task.Requirements.disk_space
        task.Requirements.disk_space = orig_disk_space
        assert task.Requirements.disk_space == orig_disk_space

        task.Requirements.disk_space = 100
        task.save()
        assert sdk2.Task[task.id].Requirements.disk_space == 100

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    def test__porto_layers(self, task_manager):
        from . import PortoTask
        import yasandbox.manager.tests

        porto_layer_res = yasandbox.manager.tests._create_resource(
            task_manager, parameters={"resource_type": "BASE_PORTO_LAYER"}, create_logs=False
        )

        task = PortoTask(None)
        task.reload()
        assert [r.id for r in task.Requirements.porto_layers] == [porto_layer_res.id]

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    def test__tasks_resource(self, task_manager):
        from . import TaskWithTasksResourceRequirement
        import yasandbox.manager.tests

        task_binary_res1 = yasandbox.manager.tests._create_resource(
            task_manager, parameters={"resource_type": "SANDBOX_TASKS_BINARY"}, create_logs=False
        )
        task_binary_res2 = yasandbox.manager.tests._create_resource(
            task_manager, parameters={"resource_type": "SANDBOX_TASKS_BINARY"}, create_logs=False
        )

        task = TaskWithTasksResourceRequirement(None).reload()
        tasks_resource = task.Requirements.tasks_resource
        assert tasks_resource and tasks_resource.id == task_binary_res2.id

        task.Requirements.tasks_resource = task_binary_res1.id
        task.save().reload()
        tasks_resource = task.Requirements.tasks_resource
        assert tasks_resource and tasks_resource.id == task_binary_res1.id

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    def test__container_resource(self, task_manager):
        from . import (
            DummyTask,
            TaskWithContainerResourceRequirement,
            TaskWithContainerResourceParameter,
            TaskWithWrongDefaultContainerResourceRequirement
        )
        import yasandbox.manager.tests

        attrs = {"released": ctt.ReleaseStatus.STABLE, "platform": sdk2.parameters.Container.platform}
        container_res1 = yasandbox.manager.tests._create_resource(
            task_manager, parameters={"resource_type": "LXC_CONTAINER", "attrs": attrs}, create_logs=False,
        )
        container_res2 = yasandbox.manager.tests._create_resource(
            task_manager, parameters={"resource_type": "LXC_CONTAINER", "attrs": attrs}, create_logs=False
        )

        task_without_container = DummyTask(None).reload()
        task_with_container_req = TaskWithContainerResourceRequirement(None).reload()

        req = task_without_container.Requirements
        assert req.container_resource is None

        req = task_with_container_req.Requirements
        assert req.container_resource and req.container_resource.id == container_res2.id

        # TODO: [SANDBOX-6188] remove after all SDK2 tasks will be fixed
        task_with_container_param = TaskWithContainerResourceParameter(None).reload()
        req = task_with_container_param.Requirements
        param = task_with_container_param.Parameters
        assert req.container_resource and req.container_resource.id == container_res2.id
        assert param.container_resource and param.container_resource.id == container_res2.id

        task_without_container.Requirements.container_resource = sdk2.Resource[container_res2.id]
        task_without_container.save().reload()
        task_with_container_req.Requirements.container_resource = sdk2.Resource[container_res1.id]
        task_with_container_req.save().reload()

        req = task_without_container.Requirements
        assert req.container_resource and req.container_resource.id == container_res2.id

        req = task_with_container_req.Requirements
        assert req.container_resource and req.container_resource.id == container_res1.id

        with pytest.raises(ValueError):
            assert TaskWithWrongDefaultContainerResourceRequirement.Requirements.container_resource.default

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    def test__tasks_client_tags(self, test_task_2):
        task = test_task_2(None)
        task.Requirements.client_tags = ""  # expect valid assignment
        task.save()


# noinspection PyMethodMayBeStatic
class TestDeduplication(object):
    @pytest.mark.usefixtures("sdk2_dispatched_rest_session", "task_controller")
    def test__auto_deduplication(self, test_task_2):
        task0 = test_task_2(None)
        uniqueness = dict(key="")
        task1 = test_task_2(None, uniqueness=uniqueness)
        task2 = test_task_2(None, uniqueness=uniqueness)
        assert task0.id != task1.id
        assert task1.id == task2.id

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session", "task_controller")
    def test__auto_deduplication_with_params(self, test_task_2):
        task0 = test_task_2(None)
        uniqueness = dict(key="")
        task1 = test_task_2(None, uniqueness=uniqueness)
        task2 = test_task_2(None, uniqueness=uniqueness, description="Other description")
        task2_1 = test_task_2(None, uniqueness=uniqueness, description="Description")
        task2_2 = test_task_2(None, uniqueness=uniqueness, description="Description")
        task3 = test_task_2(None, uniqueness=uniqueness, live_time=123457)
        task3_1 = test_task_2(None, uniqueness=uniqueness, live_time=123456)
        task3_2 = test_task_2(None, uniqueness=uniqueness, live_time=123456)
        task4 = test_task_2(None, uniqueness=uniqueness, description="Description", live_time=123456)
        assert len({task0.id, task1.id, task2.id, task2_1.id, task3.id, task3_1.id, task4.id}) == 7
        assert task2_1.id == task2_2.id
        assert task3_1.id == task3_2.id

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session", "task_controller")
    def test__custom_deduplication(self, test_task_2):
        task0 = test_task_2(None)
        task1 = test_task_2(None, uniqueness=dict(key=""))
        task2_1 = test_task_2(None, uniqueness=dict(key="123"))
        task2_2 = test_task_2(None, uniqueness=dict(key="123"), description="Description", live_time=123456)
        task3_1 = test_task_2(None, uniqueness=dict(key="321"))
        task3_2 = test_task_2(None, uniqueness=dict(key="321"), description="Description", live_time=123456)
        assert len({task0.id, task1.id, task2_1.id, task3_1.id}) == 4
        assert task2_1.id == task2_2.id
        assert task3_1.id == task3_2.id

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session", "task_controller")
    def test__deduplication_on_copy(self, test_task_2):
        task1 = test_task_2(None, uniqueness=dict(key="123"))
        task2 = test_task_2(None, uniqueness=dict(key="321"))
        task3 = test_task_2(None)

        data = task1._sdk_server.task(source=task1.id, uniqueness=dict(key="123"))
        assert data["id"] == task1.id

        data = task1._sdk_server.task(source=task1.id, uniqueness=dict(key="321"))
        assert data["id"] == task2.id

        data = task1._sdk_server.task(source=task1.id, uniqueness=dict(key="666"))
        task_id = data["id"]
        assert task_id not in (task1.id, task2.id, task3.id)

        data = task1._sdk_server.task(source=task1.id)
        assert data["id"] not in (task1.id, task2.id, task3.id, task_id)

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session", "task_controller", "serviceq")
    def test__deduplication_by_statuses(self, test_task_2, rest_session_group):
        task0 = test_task_2(None)
        for key in ("", "123"):
            uniqueness = dict(key=key, excluded_statuses=[str(ctt.Status.Group.QUEUE)])
            task1 = test_task_2(None, uniqueness=uniqueness, owner=rest_session_group)
            assert task1.id != task0.id
            task1.enqueue()
            task2 = test_task_2(None, uniqueness=uniqueness, owner=rest_session_group)
            assert task2.id != task0.id
            assert task2.id != task1.id
            task2.delete()
            task3 = test_task_2(None, uniqueness=uniqueness, owner=rest_session_group)
            assert task2.id == task3.id
            task4 = test_task_2(None, uniqueness=dict(key=key), owner=rest_session_group)
            assert task4.id != task0.id
            assert task3.id != task4.id
            assert task1.id == task4.id
            task5 = test_task_2(
                None,
                uniqueness=dict(key=key, excluded_statuses=[ctt.Status.DRAFT, ctt.Status.DELETED]),
                owner=rest_session_group
            )
            assert task5.id != task0.id
            assert task5.id == task1.id
            assert task5.id != task2.id


class TestReport(object):
    @pytest.mark.usefixtures("task_controller")
    def test__task_report(self, sdk2_dispatched_rest_session):
        first_task = sdk2.tests.ReportTestTask(None)
        second_task = sdk2.tests.ReportInheritanceTestTask(None)
        third_task = sdk2.tests.TaskWithOnlyFooter(None)

        reports = sdk2_dispatched_rest_session.task[first_task.id][:]["reports"]
        assert reports and len(reports) == len(sdk2.tests.ReportTestTask.__reports__)
        assert sorted([_["label"] for _ in reports]) == sorted([
            "hidden_later",
            "hidden_later_v2",
            "demo",
            "label",
            "header",
            "footer",
        ])

        other_reports = sdk2_dispatched_rest_session.task[second_task.id][:]["reports"]
        assert other_reports and len(other_reports) == len(sdk2.tests.ReportInheritanceTestTask.__reports__)
        assert sorted([_["label"] for _ in other_reports]) == sorted([
            "label",
            "header",
            "footer",
            "demo",
        ])

        assert sdk2_dispatched_rest_session.task[second_task.id].reports.demo[:][0]["content"] == "Overridden"

        data = sdk2_dispatched_rest_session.task[third_task.id][:]["reports"]
        assert len(data) == 1 and data[0]["label"] == "footer"


class TestCache(object):
    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    def test__reload_task(self, task_controller, test_task_2):
        task = test_task_2(None)

        task_via_find = sdk2.Task.find(id=task.id).first()
        task_by_id = sdk2.Task[task.id]
        assert task_via_find is task
        assert task_via_find is task_by_id

        task_controller.Model.objects(id=task.id).update(set__execution__status=ctt.Status.ENQUEUED)
        assert task_by_id.status == ctt.Status.DRAFT
        task_by_id.reload()
        assert task_by_id.status == ctt.Status.ENQUEUED

        # noinspection PyUnresolvedReferences
        with mock.patch.object(test_task_2, "__new__", wraps=test_task_2.__new__) as mk:
            task2 = test_task_2(None)
            task2_id = task2.id
            del task2
            task2_by_id = sdk2.Task[task2_id]
            assert task2_id == task2_by_id.id
            assert mk.call_count == 2


class TestOutput(object):
    @pytest.mark.usefixtures("serviceq")
    def test__output_reset_on_restart(
        self, sdk2_dispatched_rest_session, rest_session_login, task_session, task_controller
    ):
        task = sdk2.tests.TaskWithOutputParameters(None, owner=rest_session_login)
        task_session(sdk2_dispatched_rest_session, task.id, login=rest_session_login)
        task.__current_task__ = task
        task.current = task

        for param_name in ("output1", "output2", "output3"):
            assert getattr(task.Parameters, param_name) == 0
            setattr(task.Parameters, param_name, 1)
            setattr(task.Parameters, param_name, 1)
            with pytest.raises(AttributeError):
                setattr(task.Parameters, param_name, 2)

        task_controller.Model.objects(id=task.id).update(set__execution__status=ctt.Status.TEMPORARY)
        tw = controller.TaskWrapper(task_controller.get(task.id))
        tw.restart()
        task.reload()
        task.__current_task__ = task
        task.current = task

        assert task.Parameters.output1 == 1
        assert task.Parameters.output2 == 1
        assert task.Parameters.output3 == 0

        for param_name in ("output1", "output2"):
            with pytest.raises(AttributeError):
                setattr(task.Parameters, param_name, 2)
        task.Parameters.output3 = 2
