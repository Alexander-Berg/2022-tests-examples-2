# coding: utf-8

import time
import httplib
import datetime as dt
import aniso8601

import pytest

from sandbox import common
import sandbox.common.types.user as ctu
import sandbox.common.types.task as ctt

import sandbox.yasandbox.manager.tests
import sandbox.serviceq.types as qtypes
from sandbox.serviceq.tests.client import utils as qclient_utils


# noinspection PyMethodMayBeStatic
class TestAPISemaphore(object):
    @pytest.mark.usefixtures("gui_session", "serviceq")
    def test__semaphore_create(
        self, rest_noauth_session, rest_session, rest_session_login, rest_session_group,
        rest_su_session, rest_su_session_group, gui_session_login, semaphore_controller
    ):
        sem1_name = "semaphore1"
        sem2_name = "semaphore2"

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_noauth_session.semaphore.create(name=sem1_name, owner=rest_session_login)
        assert ex.value.status == httplib.UNAUTHORIZED

        for login in (rest_session_login, gui_session_login):
            with pytest.raises(rest_session.HTTPError) as ex:
                rest_session.semaphore.create(name=sem1_name, owner=login)
            assert ex.value.status == httplib.BAD_REQUEST
            with pytest.raises(rest_session.HTTPError) as ex:
                rest_session.semaphore.create(name=sem1_name, owner=rest_session_group, shared=[login])
            assert ex.value.status == httplib.BAD_REQUEST
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.semaphore.create(name=sem1_name, owner=rest_su_session_group)
        assert ex.value.status == httplib.FORBIDDEN

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.semaphore.create()
        assert ex.value.status == httplib.BAD_REQUEST

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.semaphore.create(name=sem1_name)
        assert ex.value.status == httplib.BAD_REQUEST

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.semaphore.create(owner=rest_session_group)
        assert ex.value.status == httplib.BAD_REQUEST

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.semaphore.create(name=sem1_name, owner=rest_session_group, capacity=-1)
        assert ex.value.status == httplib.BAD_REQUEST

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.semaphore.create(name=sem1_name, owner="")
        assert ex.value.status == httplib.BAD_REQUEST

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_su_session.semaphore.create(name=sem1_name, owner="")
        assert ex.value.status == httplib.BAD_REQUEST

        sem1 = rest_session.semaphore.create(name=sem1_name, owner=rest_session_group)
        assert sem1["name"] == sem1_name
        assert sem1["owner"] == rest_session_group
        assert sem1["shared"] == []
        assert sem1["capacity"] == 1
        assert sem1["value"] == 0
        assert sem1["tasks"] == []
        assert sem1["rights"] == ctu.Rights.WRITE
        assert sem1["time"] and sem1["time"]["created"] and sem1["time"]["updated"]

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.semaphore.create(name=sem1_name, owner=rest_session_group)
        assert ex.value.status == httplib.BAD_REQUEST

        common.itertools.progressive_waiter(
            0, 0.2, 10, lambda: bool(semaphore_controller.Model.objects.with_id(sem1["id"]))
        )
        doc = semaphore_controller.Model.objects.with_id(sem1["id"])
        for f in ("id", "name", "owner", "shared", "capacity"):
            assert doc[f] == sem1[f]
        assert doc["time"] and doc["time"]["created"] and doc["time"]["updated"]

        sem2 = rest_session.semaphore.create(
            name=sem2_name, owner=rest_session_group, shared=[rest_su_session_group], capacity=3
        )
        assert sem2["name"] == sem2_name
        assert sem2["owner"] == rest_session_group
        assert sem2["shared"] == [rest_su_session_group]
        assert sem2["capacity"] == 3
        assert sem2["value"] == 0
        assert sem2["tasks"] == []
        assert sem2["rights"] == ctu.Rights.WRITE
        assert sem2["time"] and sem2["time"]["created"] and sem2["time"]["updated"]

        common.itertools.progressive_waiter(
            0, 0.2, 10, lambda: bool(semaphore_controller.Model.objects.with_id(sem2["id"]))
        )
        doc = semaphore_controller.Model.objects.with_id(sem2["id"])
        for f in ("id", "name", "owner", "shared", "capacity"):
            assert doc[f] == sem2[f]
        assert doc["time"] and doc["time"]["created"] and doc["time"]["updated"]

    def test__semaphore_get(
        self, serviceq, rest_noauth_session, rest_session, rest_session_group,
        rest_su_session, rest_su_session_group, semaphore_controller
    ):
        sem_id, sem = serviceq.create_semaphore(dict(
            name="semaphore",
            owner=rest_su_session_group,
            shared=[rest_session_group],
            auto=True,
            capacity=3
        ))

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_su_session.semaphore[sem_id + 1].read()
        assert ex.value.status == httplib.NOT_FOUND

        got_sem = rest_su_session.semaphore[sem_id][:]
        assert got_sem["id"] == sem_id
        for f in ("name", "owner", "shared", "auto", "capacity"):
            assert getattr(sem, f) == got_sem[f]
        assert got_sem["rights"] == ctu.Rights.WRITE
        assert got_sem["tasks"] == []
        assert got_sem["time"] and got_sem["time"]["created"] and got_sem["time"]["updated"]

        sem = rest_session.semaphore[sem_id][:]
        assert sem["rights"] == ctu.Rights.READ

        sem = rest_noauth_session.semaphore[sem_id][:]
        assert sem["rights"] is None

    def test__semaphore_update(
        self, serviceq, rest_noauth_session, rest_session, rest_session_group, rest_session_login, gui_session_login,
        rest_su_session, rest_su_session_group, semaphore_controller
    ):
        sem1_id, sem1 = serviceq.create_semaphore(dict(
            name="semaphore1",
            owner=rest_su_session_group,
            shared=[rest_session_group],
            auto=True,
            capacity=3
        ))
        sem2_id, sem2 = serviceq.create_semaphore(dict(
            name="semaphore2",
            owner=rest_session_group,
            shared=[rest_su_session_group],
            capacity=5
        ))

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_su_session.semaphore[sem1_id + 2] = dict(capacity=2)
        assert ex.value.status == httplib.NOT_FOUND

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.semaphore[sem1_id] = dict(capacity=2)
        assert ex.value.status == httplib.FORBIDDEN

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.semaphore[sem2_id] = dict(owner=rest_su_session_group)
        assert ex.value.status == httplib.FORBIDDEN

        rest_session.semaphore[sem2_id] = dict(owner=rest_session_group)

        rest_su_session.semaphore[sem2_id] = dict(owner=rest_session_group)

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_noauth_session.semaphore[sem2_id] = dict(capacity=2)
        assert ex.value.status == httplib.UNAUTHORIZED

        for login in (rest_session_login, gui_session_login):
            with pytest.raises(rest_session.HTTPError) as ex:
                rest_session.semaphore[sem2_id] = dict(shared=[login])
            assert ex.value.status == httplib.BAD_REQUEST
            with pytest.raises(rest_session.HTTPError) as ex:
                rest_su_session.semaphore[sem2_id] = dict(shared=[login])
            assert ex.value.status == httplib.BAD_REQUEST

        doc = common.utils.progressive_waiter(
            0, 1, 5, lambda: semaphore_controller.Model.objects.with_id(sem2_id)
        )[0]
        assert doc

        time_updated = doc.time.updated
        time.sleep(0.01)
        data = rest_session.semaphore[sem2_id] = dict(shared=[rest_su_session_group, rest_session_group], capacity=7)

        assert common.utils.progressive_waiter(
            0, 1, 5, lambda: semaphore_controller.Model.objects.with_id(sem2_id).time.updated > time_updated
        )[0]

        doc.reload()
        for f in ("shared", "capacity"):
            assert doc[f] == data[f]

        rest_su_session.semaphore[sem2_id] = dict(owner=rest_su_session_group)
        assert common.utils.progressive_waiter(
            0, 1, 5, lambda: semaphore_controller.Model.objects.with_id(sem2_id).owner == rest_su_session_group
        )[0]

    def test__semaphore_delete(
        self, rest_noauth_session, rest_session, rest_session_group,
        rest_su_session, rest_su_session_group, semaphore_controller, serviceq, task_manager
    ):
        doc1 = semaphore_controller.create(dict(
            name="semaphore1",
            owner=rest_su_session_group,
            shared=[rest_session_group]
        ))
        doc2 = semaphore_controller.create(dict(
            name="semaphore2",
            owner=rest_session_group,
            shared=[rest_su_session_group]
        ))
        doc3 = semaphore_controller.create(dict(
            name="semaphore3",
            owner=rest_session_group
        ))
        doc4 = semaphore_controller.create(dict(
            name="semaphore4",
            owner=rest_session_group
        ))
        task = sandbox.yasandbox.manager.tests._create_task(task_manager, type="UNIT_TEST", status=ctt.Status.ENQUEUED)
        serviceq.push(
            task.id, 0, [(0, "host")], task_info=qtypes.TaskInfo(semaphores=ctt.Semaphores(doc4.name), owner=task.owner)
        )
        gen = qclient_utils.qpop(serviceq, "host")
        gen.next()
        qclient_utils.qcommit(gen)

        with pytest.raises(rest_session.HTTPError) as ex:
            del rest_su_session.semaphore[doc1.id + 4]
        assert ex.value.status == httplib.NOT_FOUND

        with pytest.raises(rest_session.HTTPError) as ex:
            del rest_session.semaphore[doc1.id]
        assert ex.value.status == httplib.FORBIDDEN

        with pytest.raises(rest_session.HTTPError) as ex:
            del rest_noauth_session.semaphore[doc1.id]
        assert ex.value.status == httplib.UNAUTHORIZED

        doc = common.utils.progressive_waiter(
            0, 1, 5, lambda: semaphore_controller.Model.objects.with_id(doc3.id)
        )[0]
        assert doc
        del rest_session.semaphore[doc3.id]
        assert common.utils.progressive_waiter(
            0, 1, 5, lambda: not semaphore_controller.Model.objects.with_id(doc3.id)
        )[0]

        doc = common.utils.progressive_waiter(
            0, 1, 5, lambda: semaphore_controller.Model.objects.with_id(doc2.id)
        )[0]
        assert doc
        del rest_su_session.semaphore[doc2.id]
        assert common.utils.progressive_waiter(
            0, 1, 5, lambda: not semaphore_controller.Model.objects.with_id(doc2.id)
        )[0]

        doc = common.utils.progressive_waiter(
            0, 1, 5, lambda: semaphore_controller.Model.objects.with_id(doc1.id)
        )[0]
        assert doc
        del rest_su_session.semaphore[doc1.id]
        assert common.utils.progressive_waiter(
            0, 1, 5, lambda: not semaphore_controller.Model.objects.with_id(doc2.id)
        )[0]

        with pytest.raises(rest_session.HTTPError) as ex:
            del rest_session.semaphore[doc4.id]
        assert ex.value.status == httplib.LOCKED

        with pytest.raises(rest_session.HTTPError) as ex:
            del rest_su_session.semaphore[doc4.id]
        assert ex.value.status == httplib.LOCKED

    @pytest.mark.usefixtures("serviceq")
    def test__semaphore_list(
        self, rest_noauth_session, rest_session, rest_session_group,
        rest_su_session, rest_su_session_group, semaphore_controller
    ):
        assert len(semaphore_controller.Model.objects) == 0
        doc1 = semaphore_controller.create(dict(
            name="semaphore1",
            owner=rest_su_session_group,
            shared=[rest_session_group]
        ))
        doc2 = semaphore_controller.create(dict(
            name="semaphore2",
            owner=rest_session_group,
            shared=[rest_su_session_group]
        ))
        doc3 = semaphore_controller.create(dict(
            name="Semaphore3",
            owner=rest_session_group
        ))
        doc4 = semaphore_controller.create(dict(
            name="semaphore4",
            owner=rest_session_group,
            shared=[rest_su_session_group, rest_session_group]
        ))
        assert common.utils.progressive_waiter(
            0, 1, 5, lambda: len(semaphore_controller.Model.objects) == 4
        )[0]

        assert rest_noauth_session.semaphore[:0]["total"] == 4
        assert rest_session.semaphore[:0]["total"] == 4
        assert rest_su_session.semaphore[:0]["total"] == 4

        assert rest_session.semaphore[dict(name="qwer"), : 4]["total"] == 0

        for doc in (doc1, doc2, doc3, doc4):
            data = rest_session.semaphore[dict(name=doc.name), : 4]
            assert data["total"] == 1
            item = data["items"][0]
            for f in ("id", "name", "owner", "shared", "capacity"):
                assert doc[f] == item[f], f
            assert item["time"] and item["time"]["created"] and item["time"]["updated"]

        data = rest_session.semaphore[dict(owner=rest_session_group), : 4: "id"]
        assert data["total"] == 3
        for item, doc in zip(data["items"], (doc2, doc3, doc4)):
            for f in ("id", "name", "owner", "shared", "capacity"):
                assert doc[f] == item[f], f
            assert item["time"] and item["time"]["created"] and item["time"]["updated"]

        data = rest_session.semaphore[dict(owner=rest_session_group), : 4: "name"]
        assert data["total"] == 3
        for item, doc in zip(data["items"], (doc3, doc2, doc4)):
            assert item["id"] == doc.id

        data = rest_session.semaphore[dict(owner=rest_session_group), : 4: "-name"]
        assert data["total"] == 3
        for item, doc in zip(data["items"], (doc4, doc2, doc3)):
            assert item["id"] == doc.id

        assert rest_session.semaphore[dict(shared="asdf"), : 4]["total"] == 0

        data = rest_session.semaphore[dict(shared=rest_session_group), : 4: "id"]
        assert data["total"] == 2
        for item, doc in zip(data["items"], (doc1, doc4)):
            assert item["id"] == doc.id

        data = rest_session.semaphore[dict(shared=rest_su_session_group), : 4: "id"]
        assert data["total"] == 2
        for item, doc in zip(data["items"], (doc2, doc4)):
            assert item["id"] == doc.id

    @pytest.mark.usefixtures("serviceq", "semaphore_controller")
    def test__semaphore_audit(
        self, rest_session, rest_su_session, rest_session_login, rest_su_session_login,
        rest_session_group, rest_su_session_group, client_node_id
    ):
        localhost = ("127.0.0.1", "::1")
        checkpoint1 = dt.datetime.utcnow()
        sem = rest_session.semaphore.create(name="semaphore", owner=rest_session_group)
        audit1 = rest_session.semaphore[sem["id"]].audit[:]
        assert len(audit1) == 1
        assert audit1[0].viewkeys() == {"author", "description", "source", "target", "time"}
        for k, v in {
            "author": rest_session_login,
            "description": "Created",
            "target": client_node_id
        }.iteritems():
            assert audit1[0][k] == v
        assert audit1[0]["source"] in localhost
        checkpoint2 = dt.datetime.utcnow()
        assert checkpoint1 < aniso8601.parse_datetime(audit1[0]["time"]).replace(tzinfo=None) < checkpoint2

        checkpoint1 = dt.datetime.utcnow()
        rest_su_session.semaphore[sem["id"]] = dict(shared=[rest_su_session_group, rest_session_group], capacity=7)
        audit2 = rest_session.semaphore[sem["id"]].audit[:]
        assert len(audit2) == 2
        assert audit2[0] == audit1[0]
        for k, v in {
            "author": rest_su_session_login,
            "description": "shared: []->{}, capacity: {}->{}".format(
                map(unicode, [rest_su_session_group, rest_session_group]), 1, 7
            ),
            "target": client_node_id
        }.iteritems():
            assert audit2[1][k] == v
        assert audit2[0]["source"] in localhost
        checkpoint2 = dt.datetime.utcnow()
        assert checkpoint1 < aniso8601.parse_datetime(audit2[1]["time"]).replace(tzinfo=None) < checkpoint2

        checkpoint1 = dt.datetime.utcnow()
        event = "Описание"
        rest_session.semaphore[sem["id"]] = dict(shared=[rest_session_group], event=event)
        audit3 = rest_session.semaphore[sem["id"]].audit[:]
        assert len(audit3) == 3
        assert audit3[0] == audit1[0]
        assert audit3[1] == audit2[1]
        for k, v in {
            "author": rest_session_login,
            "description": u"{} (shared: {}->{})".format(
                event.decode("utf-8"),
                map(unicode, [rest_su_session_group, rest_session_group]),
                map(unicode, [rest_session_group])
            ),
            "target": client_node_id
        }.iteritems():
            assert audit3[2][k] == v
        assert audit3[0]["source"] in localhost
        checkpoint2 = dt.datetime.utcnow()
        assert checkpoint1 < aniso8601.parse_datetime(audit3[2]["time"]).replace(tzinfo=None) < checkpoint2

        checkpoint1 = dt.datetime.utcnow()
        del rest_session.semaphore[sem["id"]]
        audit4 = rest_session.semaphore[sem["id"]].audit[:]
        assert len(audit4) == 4
        assert audit4[0] == audit1[0]
        assert audit4[1] == audit2[1]
        assert audit4[2] == audit3[2]
        for k, v in {
            "author": rest_session_login,
            "description": "Deleted",
            "target": client_node_id
        }.iteritems():
            assert audit4[3][k] == v
        assert audit4[0]["source"] in localhost
        checkpoint2 = dt.datetime.utcnow()
        assert checkpoint1 < aniso8601.parse_datetime(audit4[3]["time"]).replace(tzinfo=None) < checkpoint2

    @pytest.mark.usefixtures("serviceq", "semaphore_controller")
    def test__semaphore_groups(self, rest_session, rest_session_group):
        sems = [
            rest_session.semaphore.create(name="semaphore1", owner=rest_session_group),
            rest_session.semaphore.create(name="semaphore2", owner=rest_session_group),
            rest_session.semaphore.create(name="group/semaphore1", owner=rest_session_group),
            rest_session.semaphore.create(name="group/semaphore2", owner=rest_session_group),
            rest_session.semaphore.create(name="group/group/semaphore", owner=rest_session_group),
            rest_session.semaphore.create(name="group1/group/semaphore", owner=rest_session_group),
            rest_session.semaphore.create(name="group2/semaphore", owner=rest_session_group)
        ]

        data = rest_session.semaphore[:100:"id"]
        assert data["total"] == len(sems)
        assert [_["id"] for _ in data["items"]] == map(lambda _: _["id"], sems)
        assert data["groups"] == []

        data = rest_session.semaphore[dict(group="/"), :100:"id"]
        assert data["total"] == 2
        assert data["groups"] == ["group", "group1", "group2"]
        assert [_["id"] for _ in data["items"]] == map(lambda _: _["id"], sems[:2])

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.semaphore.read(dict(group="not_existent_group", limit=100))
        assert ex.value.status == httplib.BAD_REQUEST

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.semaphore.read(dict(group="group/not_existent_group", limit=100))
        assert ex.value.status == httplib.BAD_REQUEST

        data = rest_session.semaphore[dict(group="group"), :100:"id"]
        assert data["total"] == 2
        assert data["groups"] == ["group/group"]
        assert [_["id"] for _ in data["items"]] == map(lambda _: _["id"], sems[2:4])

        data = rest_session.semaphore[dict(group="group/group"), :100:"id"]
        assert data["total"] == 1
        assert data["groups"] == []
        assert data["items"][0]["id"] == sems[4]["id"]

        data = rest_session.semaphore[dict(group="group1"), :100:"id"]
        assert data["total"] == 0
        assert data["groups"] == ["group1/group"]

        data = rest_session.semaphore[dict(group="group2"), :100:"id"]
        assert data["total"] == 1
        assert data["groups"] == []
        assert data["items"][0]["id"] == sems[6]["id"]

        del rest_session.semaphore[sems[4]["id"]]
        data = rest_session.semaphore[dict(group="group"), :100:"id"]
        assert data["groups"] == []

        del rest_session.semaphore[sems[6]["id"]]
        data = rest_session.semaphore[dict(group="/"), :100:"id"]
        assert data["groups"] == ["group", "group1"]
