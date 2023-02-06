import json
import time
import uuid
import pytest
import httplib
import calendar
import requests
import operator
import datetime as dt
import functools as ft

from sandbox import common
import sandbox.common.types.user as ctu
import sandbox.common.types.task as ctt
import sandbox.common.types.client as ctc

from sandbox.yasandbox.manager import tests
from sandbox.yasandbox.database import mapping
from sandbox.yasandbox.services import update_sandbox_resources
from sandbox.yasandbox.controller import user as user_controller

from sandbox.serviceq import types as qtypes

CLIENT_AGE_SANDBOX_6720 = 17


@pytest.fixture()
def ready_client(client_manager, rest_su_session):
    client_id = "test_client"
    client = client_manager.create(client_id)
    client["uuid"] = "c9c769c1c5314740ac350d5a022897c7"
    client.save()
    client_state = TestClient._client_data(client_id)
    # avoid treating this client as NEW and creating CLEANUP task
    client_state["uuid"] = client["uuid"]
    rest_su_session.client[client_id](client_state)
    # avoid receiving RESET command
    client_manager.load(client_id).next_service_command(reset=True)
    return client


class TestClient(object):
    @staticmethod
    def _client_data(hostname=None, tags=None, unique_id=None):
        if hostname is None:
            hostname = "test__client"
        if tags is None:
            tags = (ctc.Tag.GENERIC, ctc.Tag.POSTEXECUTE, ctc.Tag.LINUX_PRECISE)

        return {
            "cpu": "E5645",
            "ncpu": 24,
            "ram": 67553460224,
            "disk": {
                "free_space": 17354981376,
                "status": "critical",
                "total_space": 903376535552
            },
            "dc": "iva",
            "fileserver": "http://{}.search.yandex.net:13578/".format(hostname),
            "fqdn": "{}.search.yandex.net".format(hostname),
            "os": {"name": "linux", "version": "3.18.19-24"},
            "platform": "linux_ubuntu_12.04_precise",
            "root": True,
            "lxc": False,
            "tags": map(str, ctc.Tag.filter(tags)),
            "age": 42,
            "tasks_dir": "/place/tasks_dir",
            "uuid": unique_id if unique_id else uuid.uuid4().hex
        }

    def test__client(self, rest_session, client_manager):
        client = client_manager.create('test_client')
        ret = rest_session.client[:1]
        assert ret['items'][0]['id'] == client.hostname
        ret = rest_session.client[client.hostname][...]
        assert ret['id'] == client.hostname

        assert not client.pending_service_commands()
        _RC = ctc.ReloadCommand
        map(
            client.reload,
            (
                _RC.CLEANUP, _RC.RESTART, _RC.RESET, _RC.SHUTDOWN, _RC.REBOOT,
                _RC.RESTART, _RC.CLEANUP, _RC.RESET, _RC.POWEROFF
            )
        )
        assert sorted(client.pending_service_commands()) == sorted(_RC)
        for cmd in _RC:
            assert client.next_service_command(True).command == cmd
        assert not client_manager.load('test_client').pending_service_commands()

    def test__client_free_space(self, rest_session, rest_su_session, ready_client):
        # Check that server doesn't return negative free_space values
        client_state = self._client_data(ready_client.hostname, unique_id=ready_client["uuid"])
        client_state["disk"]["free_space"] = -1
        rest_su_session.client[ready_client.hostname](client_state)

        ret = rest_session.client[ready_client.hostname][...]
        assert ret["disk"]["free_space"] == 0

    def test__clients_list(self, rest_session, client_manager):
        clients = [client_manager.create('test_client_{}'.format(i)) for i in range(3)]
        update_ts = calendar.timegm(dt.datetime.utcnow().timetuple())
        up_clients = [
            client_manager.create('test_client_alive_{}'.format(i), update_ts=update_ts)
            for i in range(2)]
        client_num = len(clients) + len(up_clients)
        ret = rest_session.client[0:client_num]
        assert ret['total'] == client_num
        assert ret['items'][0] == requests.get(ret['items'][0]['url']).json()
        assert set(o['id'] for o in ret['items'] if o['alive']) == set(cl.hostname for cl in up_clients)
        assert all(o['alive'] for o in ret['items'] if 'alive' in o['id'])

        limited = rest_session.client[1:3]
        assert set(o['id'] for o in limited['items']) == set(
            cl.hostname for cl in sorted(clients + up_clients, key=operator.attrgetter('hostname'))[1:4])
        assert limited['total'] == client_num
        ret_alive = rest_session.client[{'alive': True}, : 10]
        assert set(o['id'] for o in ret_alive['items']) == set(cl.hostname for cl in up_clients)

        ret_dead = rest_session.client[{'alive': False}, : 10]
        assert set(o['id'] for o in ret_dead['items']) == set(cl.hostname for cl in clients)

        ret_busy = rest_session.client[{'busy': True}, : 10]
        assert not ret_busy['items']
        ret_not_busy = rest_session.client[{'busy': False}, : 10]
        assert ret['items'] == ret_not_busy['items']

    def test__busy_clients(self, oauth_controller, rest_session, task_manager, client_manager):
        task1 = tests._create_task(task_manager, type="UNIT_TEST", status=ctt.Status.DRAFT)
        task2 = tests._create_task(task_manager, type="TEST_TASK", status=ctt.Status.FINISHING)
        free_clients = [client_manager.create('test_client_{}'.format(i)) for i in range(3)]
        busy_clients = []
        for task in (task1, task2):
            c = client_manager.create('test_busy_{}'.format(task.id))
            # Emulate task sessions
            oauth_controller.Model(
                token=uuid.uuid4().hex,
                login=task.author,
                source="{}:{}".format(ctu.TokenSource.CLIENT, c.hostname),
                ttl=3600,
                app_id=str(task.id),
                task_id=task.id,
                state=str(ctt.SessionState.ACTIVE),
            ).save()
            busy_clients.append(c)
        ret_busy = rest_session.client[{'busy': True}, : 10]
        assert set(o['id'] for o in ret_busy['items']) == set(cl.hostname for cl in busy_clients)
        assert set(o['task']['task_id'] for o in ret_busy['items']) == {task1.id, task2.id}
        assert set(t['id'] for o in ret_busy['items'] for t in o['tasks']) == {task1.id, task2.id}
        ret = rest_session.client[:10]
        assert set(o['id'] for o in ret['items']) == set(cl.hostname for cl in free_clients + busy_clients)
        ret_free = rest_session.client[{'busy': False}, : 10]
        assert set(o['id'] for o in ret_free['items']) == set(cl.hostname for cl in free_clients)

    def test__clients_arch(self, rest_session, client_manager):
        client_manager.create('test_client_windows', arch='windows')
        client_linux = client_manager.create(
            'test_client_linux',
            info={'system': {'platform': 'Linux-3.2.0-68-virtual-x86_64-with-Ubuntu-12.04-precise'}})
        ret = rest_session.client[:100]
        assert len(ret['items']) == 2

        ret = rest_session.client[{'platform': 'linux_ubuntu_12.04_precise', 'limit': 100}]
        assert len(ret['items']) == 1
        assert ret['items'][0]['id'] == client_linux.hostname

        client_linux_multi = client_manager.create(
            'test_client_linux',
            info={'system': {
                'platform': 'Linux-3.2.0-68-virtual-x86_64-with-Ubuntu-12.04-precise',
                'lxc': True
            }}
        )
        client_linux_multi.update_tags([ctc.Tag.LXC], client_linux_multi.TagsOp.ADD)
        mapping.Service.objects(
            name=update_sandbox_resources.UpdateSandboxResources.__name__
        ).update(
            set__context={"resources": {"lxc_res": [["linux_ubuntu_10.04_lucid", {}]]}},
            upsert=True
        )

        ret = rest_session.client[{'platform': 'linux_ubuntu_10.04_lucid'}, : 100]
        assert len(ret['items']) == 1
        assert ret['items'][0]['id'] == client_linux_multi.hostname
        assert 'linux_ubuntu_10.04_lucid' in ret['items'][0]['platforms']

    def test__client_comment(self, rest_session, rest_su_session, client_manager):
        client = client_manager.create('test-client')
        ret = rest_session.client[:1]
        assert ret['items'][0]['msg'] == ''
        import random
        comment = 'This client is dead, with random seed: {}'.format(random.randint(20000, 42000))

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.client[client.hostname].comment = comment
        assert ex.value.status == httplib.FORBIDDEN

        rest_su_session.client[client.hostname].comment = comment
        ret = rest_su_session.client[client.hostname][:]
        assert json.loads(ret['msg']) == comment

    def test__client_ping(self, task_manager, client_manager, rest_session, rest_su_session, service_user, serviceq):
        cid = "test__client_ping"
        initial_tags = (ctc.Tag.GENERIC, ctc.Tag.POSTEXECUTE, ctc.Tag.LINUX_PRECISE, ctc.Tag.INTEL_E5645, ctc.Tag.HDD)
        additional_tags = (ctc.Tag.NEW, )
        data = self._client_data(cid, initial_tags)
        data.pop("uuid")
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.client[cid](data)
        assert ex.value.status == httplib.FORBIDDEN
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_su_session.client[cid](data)
        assert ex.value.status == httplib.BAD_REQUEST, "UUID should" in ex.value.response
        data["uuid"] = uuid.uuid4().hex
        assert rest_su_session.client[cid](data) != rest_su_session.NO_CONTENT
        ret = rest_su_session.client[cid][:]
        keys = set(data.keys()) - {"tags"}
        for k in keys:
            v = data[k]
            if k in ("root", "age", "tasks_dir"):
                assert k not in ret
            elif isinstance(v, dict):
                for kk, vv in v.iteritems():
                    assert ret[k][kk] == vv, (kk, vv, ret[k])
            elif isinstance(v, list):
                assert sorted(ret[k]) == sorted(v)
            else:
                assert ret[k] == v, (k, v, ret)

        assert all(g not in ret["tags"] for g in ctc.Tag.Group)
        assert sorted(ret["tags"]) == sorted(map(str, additional_tags + initial_tags))  # NEW is added automatically

        data["disk"]["free_space"] = 0
        data["tags"].append(str(ctc.Tag.IPV6))
        assert rest_su_session.client[cid](data) == rest_su_session.NO_CONTENT
        ret = rest_su_session.client[cid][:]
        assert ret["disk"]["free_space"] == 0
        assert str(ctc.Tag.IPV6) in ret["tags"]

        client = client_manager.load(cid)
        client.update_tags([ctc.Tag.NEW], client.TagsOp.REMOVE)  # allow for enqueuing tasks on this client
        assert str(ctc.Tag.NEW) not in rest_su_session.client[cid][:]["tags"]

        task_type = "UNIT_TEST"

        # UUID change
        data["uuid"] = uuid.uuid4().hex
        assert rest_su_session.client[cid](data) != rest_su_session.NO_CONTENT
        assert rest_su_session.client[cid](data) == rest_su_session.NO_CONTENT

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_su_session.client[cid + "X"](data)
        assert ex.value.status == httplib.BAD_REQUEST, "already assigned" in ex.value.response

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_su_session.client[cid].job(-1)
        assert ex.value.status == httplib.BAD_REQUEST, "Protocol version" in ex.value.response

        # Check that CLEANUP_2 tasks were created for new clients
        cleanup_tasks = list(mapping.Task.objects.all())
        assert len(cleanup_tasks) == 2
        assert all(t.type == "CLEANUP_2" for t in cleanup_tasks)
        # Wait until they're enqueued
        iteration = 0
        max_iterations = 10
        while (any(t.execution.status != ctt.Status.ENQUEUED for t in mapping.Task.objects.all()) and
               iteration < max_iterations):
            time.sleep(1)
            iteration += 1
        assert (iteration != max_iterations,
                "Not all tasks are in status ENQUEUED: {}"
                .format({t.id: t.execution.status for t in mapping.Task.objects.all()}))

        # And remove them all, they are not needed in this test
        for t in mapping.Task.objects.all():
            t.delete()
            serviceq.push(t.id, None, None)

        # Task registration
        def job_get_data():
            return dict(
                age=CLIENT_AGE_SANDBOX_6720,
                disk_free=0,
                tokens=[uuid.uuid4().hex],
                free=dict(cores=0, ram=0)
            )

        assert rest_su_session.client[cid].job(job_get_data())[0]["command"] == ctc.ReloadCommand.RESET

        assert rest_su_session.client[cid].job(job_get_data()) == rest_su_session.NO_CONTENT

        task1 = tests._create_task(task_manager, type=task_type, status=ctt.Status.ENQUEUED, host="")
        serviceq.push(task1.id, 0, [(0, cid)], task_info=qtypes.TaskInfo(None, None, None, task1.owner))

        assert rest_su_session.client[cid].job(job_get_data()) == rest_su_session.NO_CONTENT  # No disk space

        def job_get_data():
            return dict(
                age=CLIENT_AGE_SANDBOX_6720,
                disk_free=117354981376,
                tokens=[uuid.uuid4().hex],
                free=dict(cores=0, ram=0)
            )

        getajob_data = job_get_data()
        job1 = rest_su_session.client[cid].job(getajob_data)[0]
        assert job1["command"] == str(ctt.Status.Group.EXECUTE)
        assert job1["task_id"] == task1.id
        assert mapping.OAuthCache.objects.with_id(job1["id"]).task_id == task1.id

        expected = [{"id": job1["id"], "state": str(ctt.SessionState.ACTIVE), "options": None}]
        assert rest_su_session.client[cid].job[:] == expected

        # Return the same job for the same session token
        res = rest_su_session.client[cid].job(
            {"age": CLIENT_AGE_SANDBOX_6720, "disk_free": 117354981376, "tokens": [job1["id"]]}
        )[0]
        assert res == job1

        # Task reset on client start
        assert rest_su_session.client[cid](data) == rest_su_session.NO_CONTENT
        assert rest_su_session.client[cid].job[:] == rest_su_session.RESET
        assert rest_su_session.client[cid].job(job_get_data())[0]["command"] == ctc.ReloadCommand.RESET

        jsort = ft.partial(sorted, key=lambda _: _["id"])
        # Register first job

        serviceq.push(task1.id, 0, [(0, cid)], task_info=qtypes.TaskInfo(None, None, None, task1.owner))
        job1 = rest_su_session.client[cid].job(job_get_data())[0]
        expected = [{"id": job1["id"], "state": str(ctt.SessionState.ACTIVE), "options": None}]
        assert rest_su_session.client[cid].job[:] == expected
        assert rest_su_session.client[cid].job(job_get_data()) == rest_su_session.NO_CONTENT  # No new tasks

        # Register second job
        task2 = tests._create_task(task_manager, type=task_type, status=ctt.Status.ENQUEUED, host="")
        serviceq.push(task2.id, 0, [(0, cid)], task_info=qtypes.TaskInfo(None, None, None, task2.owner))
        job2 = rest_su_session.client[cid].job(job_get_data())[0]
        jobs = [
            {"id": job1["id"], "state": str(ctt.SessionState.ACTIVE), "options": None},
            {"id": job2["id"], "state": str(ctt.SessionState.ACTIVE), "options": None},
        ]
        data["jobs"] = jobs
        assert job2["command"] == str(ctt.Status.Group.EXECUTE)
        assert job2["task_id"] == task2.id
        assert jsort(rest_su_session.client[cid].job[:]) == jsort(jobs)
        assert rest_su_session.client[cid].update(data) == rest_su_session.NO_CONTENT

        # Suspend job session
        jobs2 = [
            {"id": job1["id"], "state": str(ctt.SessionState.ACTIVE), "options": None},
            {"id": job2["id"], "state": str(ctt.SessionState.SUSPENDED), "options": None},
        ]
        data2 = data.copy()
        data2["jobs"] = jobs2
        task2.status = ctt.Status.ASSIGNED
        task2.set_status(ctt.Status.SUSPENDED, force=True)
        assert rest_su_session.client[cid].update(data) == rest_su_session.RESET
        assert jsort(rest_su_session.client[cid].job[:]) == jsort(jobs2)
        assert rest_su_session.client[cid].update(data2) == rest_su_session.NO_CONTENT

        task2.set_status(ctt.Status.ASSIGNED, force=True)
        assert rest_su_session.client[cid].update(data2) == rest_su_session.RESET
        assert jsort(rest_su_session.client[cid].job[:]) == jsort(jobs)
        assert rest_su_session.client[cid].update(data) == rest_su_session.NO_CONTENT

        rest_su_session.client[cid].job.delete(
            token=job2["id"], reject=True, reason="Test re-enqueue"
        )
        assert mapping.Task.objects.with_id(task2.id).execution.status == ctt.Status.ENQUEUING

        from sandbox.services.modules import tasks_enqueuer
        tasks_enqueuer.TasksEnqueuer().tick()

        data["jobs"] = [{"id": job1["id"], "state": str(ctt.SessionState.ACTIVE), "options": None}]
        assert rest_su_session.client[cid].update(data) == rest_su_session.NO_CONTENT

        while serviceq.validate()[0] != [task2.id]:
            time.sleep(1)

        # Finish first job
        rest_su_session.client[cid].job.delete(
            token=job1["id"], reject=True, reason="Test re-enqueue"
        )
        assert rest_su_session.client[cid].update(data) == rest_su_session.RESET
        tasks_enqueuer.TasksEnqueuer().tick()

        while set(serviceq.validate()[0]) != {task1.id, task2.id}:
            time.sleep(1)

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_su_session.client[cid].job.delete(token=job1["id"])
        assert ex.value.status == httplib.NOT_FOUND
        assert rest_su_session.client[cid].job[:] == []

        # Reload test. Cleanup invalidated sessions first.
        data["jobs"] = []
        assert rest_su_session.client[cid](data) == rest_su_session.NO_CONTENT
        assert rest_su_session.client[cid].job(job_get_data())[0]["command"] == ctc.ReloadCommand.RESET

        # Register first job
        job1 = rest_su_session.client[cid].job(job_get_data())[0]
        expected = [{"id": job1["id"], "state": str(ctt.SessionState.ACTIVE), "options": None}]
        assert rest_su_session.client[cid].job[:] == expected

        rest_su_session.batch.clients.reload = [cid]
        # No new tasks - reload pending
        assert rest_su_session.client[cid].job(job_get_data()) == rest_su_session.NO_CONTENT
        rest_su_session.client[cid].job.delete(token=job1["id"])

        # Take "reload" job
        assert rest_su_session.client[cid].job(job_get_data())[0]["command"] == ctc.ReloadCommand.RESTART
        assert rest_su_session.client[cid].job[:] == []
        job2 = rest_su_session.client[cid].job(job_get_data())[0]
        # The second job can be processed now
        expected = [{"id": job2["id"], "state": str(ctt.SessionState.ACTIVE), "options": None}]
        assert rest_su_session.client[cid].job[:] == expected

        # Unlock tasks from host and drop their sessions in client update if task is not executing on the host
        data["jobs"] = []
        mapping.OAuthCache.objects.filter(token=job2["id"]).update(
            set__validated=dt.datetime.utcnow() - dt.timedelta(minutes=15)
        )
        rest_su_session.client[cid] = data
        assert mapping.Task.objects.with_id(task2.id).lock_host == ""

    def test__client_get_multiple_jobs_at_once(self, rest_su_session, task_manager, serviceq, ready_client):
        client_id = ready_client.hostname
        tasks = []
        for _ in range(3):
            task = tests._create_task(task_manager, type="UNIT_TEST", status=ctt.Status.ENQUEUED, host=client_id)
            tasks.append(task)
            serviceq.push(task.id, 0, [(0, client_id)], task_info=qtypes.TaskInfo(None, None, None, task.owner))
        jobs_ids = [uuid.uuid4().hex for _ in range(len(tasks))]
        jobs = rest_su_session.client[client_id].job(
            dict(age=CLIENT_AGE_SANDBOX_6720, disk_free=10 ** 12, tokens=jobs_ids, free=dict(cores=0, ram=0))
        )
        assert [(j["task_id"], j["id"]) for j in jobs] == zip([t.id for t in tasks], jobs_ids)

    def test__client_drop_session_on_task_delete(self, rest_su_session, task_manager, serviceq, ready_client):
        client_id = ready_client.hostname

        for reject in (True, False):
            # create new task and enqueue it
            task = tests._create_task(task_manager, type="UNIT_TEST", status=ctt.Status.ENQUEUED, host=client_id)
            serviceq.push(task.id, 0, [(0, client_id)], task_info=qtypes.TaskInfo(None, None, None, task.owner))
            # acquire job and advance task to REALEXECUTE status
            job = rest_su_session.client[client_id].job(
                dict(
                    age=CLIENT_AGE_SANDBOX_6720,
                    disk_free=10 ** 12,
                    tokens=[uuid.uuid4().hex],
                    free=dict(cores=0, ram=0)
                )
            )[0]
            task = task_manager.load(task.id)
            assert task.status == ctt.Status.ASSIGNED
            task.set_status(ctt.Status.PREPARING)
            # finally delete task
            task.delete()
            assert mapping.Task.objects.with_id(task.id).execution.status == ctt.Status.DELETED
            # session should be aborted
            assert mapping.OAuthCache.objects.get(task_id=task.id).aborted
            # and client job should be in ABORTED state
            expected = [{"id": job["id"], "state": str(ctt.SessionState.ABORTED), "options": None}]
            assert rest_su_session.client[client_id].job.read() == expected
            # reporting job as finished should delete session and do nothing else
            rest_su_session.client[client_id].job.delete(
                token=job["id"], reject=reject, reason="For testing purposes"
            )
            assert mapping.Task.objects.with_id(task.id).execution.status == ctt.Status.DELETED
            assert mapping.OAuthCache.objects(task_id=task.id).first() is None

    @pytest.mark.usefixtures("resource_manager")
    def test__client_job_drop(self, rest_su_session, task_manager, serviceq, ready_client):
        def job_get_data():
            return dict(
                age=CLIENT_AGE_SANDBOX_6720,
                disk_free=10 ** 12,
                tokens=[uuid.uuid4().hex],
                free=dict(cores=0, ram=0)
            )

        client_id = ready_client.hostname
        client_state = self._client_data(hostname=client_id, unique_id=ready_client["uuid"])

        tasks_archive_resource = tests._create_resource(task_manager, {"resource_type": "SANDBOX_TASKS_ARCHIVE"})
        task = tests._create_task(task_manager, type="UNIT_TEST", status=ctt.Status.ENQUEUED, host=client_id)

        serviceq.push(task.id, 0, [(0, client_id)], task_info=qtypes.TaskInfo(None, None, None, task.owner))
        job = rest_su_session.client[client_id].job(job_get_data())[0]
        assert job != common.rest.Client.NO_CONTENT
        rest_su_session.client[client_id].job.delete(
            token=job["id"], reject=True, reason="Test re-enqueue"
        )
        assert mapping.Task.objects.with_id(task.id).execution.status == ctt.Status.ENQUEUING
        from sandbox.services.modules import tasks_enqueuer
        tasks_enqueuer.TasksEnqueuer().tick()

        assert rest_su_session.client[client_id].job[:] == []
        while serviceq.validate()[0] != [task.id]:
            time.sleep(1)

        rest_su_session.client[client_id].update(client_state)
        job = rest_su_session.client[client_id].job(job_get_data())[0]
        assert job != common.rest.Client.NO_CONTENT
        mapping.Task.objects.filter(id=task.id).update(set__execution__status=ctt.Status.FINISHING)
        rest_su_session.client[client_id].job.delete(
            token=job["id"], reject=True, reason="Test FINISHING -> TEMPORARY"
        )
        assert mapping.Task.objects.with_id(task.id).execution.status == ctt.Status.TEMPORARY

        for status in (ctt.Status.STOPPING, ctt.Status.ENQUEUED):
            task = tests._create_task(
                task_manager, type="UNIT_TEST", status=status, host=client_id,
                parameters={"tasks_archive_resource": tasks_archive_resource.id},
            )
            serviceq.push(task.id, 0, [(0, client_id)], task_info=qtypes.TaskInfo(None, None, None, task.owner))
            job = rest_su_session.client[client_id].job(job_get_data())[0]
            assert job != common.rest.Client.NO_CONTENT
            rest_su_session.client[client_id].job.delete(
                token=job["id"], reject=True, reason="Test *ING -> EXCEPTION"
            )
            assert mapping.Task.objects.with_id(task.id).execution.status == ctt.Status.EXCEPTION

    def test__invalid_task_session_after_expire(
        self, task_manager, rest_session, rest_session_login, task_session, client_node_id
    ):
        task = tests._create_task(task_manager, type="UNIT_TEST", status=ctt.Status.ENQUEUED)
        task_session(rest_session, task.id, client_node_id, login=rest_session_login)

        rest_session.task.current.audit(message="Session is valid", status=ctt.Status.ENQUEUED)

        user_controller.OAuthCache.expire(mapping.OAuthCache.objects.get(task_id=task.id))

        with pytest.raises(rest_session.SessionExpired):
            rest_session.task.current.audit(message="Session is invalid", status=ctt.Status.ENQUEUED)

    def test__client_not_released_on_expire(self, rest_su_session, task_manager, ready_client):
        client_id = ready_client.hostname
        client_job_request = dict(age=CLIENT_AGE_SANDBOX_6720, disk_free=10 ** 12, tokens=[uuid.uuid4().hex])

        # create new task and enqueue it
        task = tests._create_task(task_manager, type="UNIT_TEST", status=ctt.Status.RELEASING, host=client_id)
        # acquire job and expire session
        job = rest_su_session.client[client_id].job(client_job_request)[0]
        user_controller.OAuthCache.expire(mapping.OAuthCache.objects.get(task_id=task.id))
        # reporting job as finished should switch task to NOT_RELEASED
        rest_su_session.client[client_id].job.delete(token=job["id"], reject=True, reason="session expired")
        assert mapping.Task.objects.with_id(task.id).execution.status == ctt.Status.NOT_RELEASED

    def test__client_get_job_from_session_while_reloading(
        self, rest_su_session, task_manager, serviceq, ready_client
    ):
        client_id = ready_client.hostname
        client_job_request = dict(
            age=CLIENT_AGE_SANDBOX_6720,
            disk_free=10 ** 12,
            tokens=[uuid.uuid4().hex],
            free=dict(cores=0, ram=0)
        )

        # create new task and enqueue it
        task = tests._create_task(task_manager, type="UNIT_TEST", status=ctt.Status.ENQUEUED, host=client_id)
        serviceq.push(task.id, 0, [(0, client_id)], task_info=qtypes.TaskInfo(None, None, None, task.owner))
        # acquire job and "reload" the client
        jobs1 = rest_su_session.client[client_id].job(client_job_request)
        ready_client.reload(ctc.ReloadCommand.RESET)
        assert ready_client.pending_service_commands()
        # take the same job again
        jobs2 = rest_su_session.client[client_id].job(client_job_request)
        # it should be the same jobs
        assert jobs1 == jobs2

    def test__client_service_resources(self, task_manager, rest_session, resource_manager, client_manager, settings):
        client = client_manager.create("test_client")
        storage_hosts = [client_manager.create(settings.server.storage_hosts[_]) for _ in range(2)]

        task = tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.SUCCESS, host=client.hostname
        )
        resource = tests._create_resource(
            task_manager,
            parameters={"resource_filename": "unit_test_resource"},
            task=task,
            create_logs=False
        )
        resource_manager.add_host(resource.id, client.hostname)
        for storage_client in storage_hosts:
            resource_manager.add_host(resource.id, storage_client.hostname)
        res = rest_session.client[client.hostname].service.resources.read(kind=ctc.RemovableResources.EXTRA)
        assert len(res) == 1
        assert res[0] == resource.id

        resource_manager.mark_host_to_delete(resource.id, client.hostname)
        res = rest_session.client[client.hostname].service.resources.read(kind=ctc.RemovableResources.DELETED)
        assert len(res) == 1
        assert res[0] == resource.id

    def test__client_change_user_tags(
        self, rest_session, rest_session_login, rest_session2, rest_session_login2, client_manager, group_controller
    ):
        client = client_manager.create('test_client')
        user_tag = "USER_TEST"
        user_group = "TGROUP"
        group_controller.Model(
            name=user_group, users=[rest_session_login], user_tags=[group_controller.Model.UserTag(name=user_tag)]
        ).save()
        assert rest_session.client[client.hostname].tags.user(user_tag) == rest_session.NO_CONTENT
        assert user_tag in mapping.Client.objects.with_id(client.hostname).tags

        user_tag2 = "USER_TEST2"
        user_group2 = "TGROUP2"
        group_controller.Model(
            name=user_group2, users=[rest_session_login2], user_tags=[group_controller.Model.UserTag(name=user_tag2)]
        ).save()
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.client[client.hostname].tags.user(user_tag2)
        assert ex.value.status == httplib.FORBIDDEN
        assert user_tag2 not in mapping.Client.objects.with_id(client.hostname).tags

        assert rest_session2.client[client.hostname].tags.user(user_tag2) == rest_session.NO_CONTENT
        assert user_tag2 in mapping.Client.objects.with_id(client.hostname).tags

        json_client = rest_session.client.read(limit=1, fields=["user_tags"])
        assert user_group in json_client["items"][0]["user_tags"]["allowed"]
        assert user_group2 in json_client["items"][0]["user_tags"]["others"]
        assert len(json_client["items"][0]["user_tags"]["allowed"]) == 1
        assert len(json_client["items"][0]["user_tags"]["others"]) == 1
        assert user_tag in json_client["items"][0]["user_tags"]["allowed"][user_group]
        assert user_tag2 in json_client["items"][0]["user_tags"]["others"][user_group2]

        rest_session.client[client.hostname].tags.user[user_tag].delete()
        assert user_tag not in mapping.Client.objects.with_id(client.hostname).tags
