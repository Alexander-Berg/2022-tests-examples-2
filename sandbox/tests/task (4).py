# coding: utf8
from __future__ import print_function

import time
import uuid

import pytest
import random
import datetime as dt
import collections

from six.moves import http_client

from sandbox.common import rest as common_rest
import sandbox.common.types.misc as ctm
import sandbox.common.types.task as ctt
import sandbox.common.types.client as ctc
import sandbox.common.types.resource as ctr
import sandbox.common.types.notification as ctn

from sandbox.yasandbox.database import mapping
from sandbox.yasandbox.api.json import task as json_task
from sandbox.yasandbox.controller import task as task_controller
from sandbox.yasandbox.controller import user as user_controller
from sandbox.yasandbox.controller import scheduler as scheduler_controller

from sandbox.yasandbox.manager import tests as manager_tests
from sandbox.tests.common.models import user as user_test_models

_TS = ctt.Status


@pytest.fixture()
def _task(task_manager):
    task = manager_tests._create_task(task_manager, type="TEST_TASK")
    return task


@pytest.fixture()
def _no_code_task(task_manager):
    task = manager_tests._create_task(task_manager, type="NO_CODE_TASK")
    return task


def _logged_test_case(test_case_func, args, test_comment=""):  # type: (callable, iter, str) -> None
    try:
        test_case_func(*args)
    except BaseException:
        print(test_comment, args)
        raise


class TestRESTAPITask(object):

    def test__task_basic(self, rest_session):
        limit = 2
        ret = rest_session.task[:limit]
        assert isinstance(ret['items'], list)
        assert ret['offset'] == 0
        assert ret['limit'] == limit
        assert 'total' in ret

    def test__task_list_empty(self, rest_session):
        resp = rest_session.task.read(limit=0)
        assert not resp["items"]

    def test__task_list_advanced(self, rest_session, rest_su_session, gui_su_session_login, task_manager):
        task1 = manager_tests._create_task(task_manager, type="UNIT_TEST", status=_TS.DRAFT)
        task1.ctx = {"a": 1, "b": {"c": 2}}
        task_manager.update(task1)
        task2 = manager_tests._create_task(task_manager, type="TEST_TASK", status=_TS.FINISHING)
        task2.ctx = {"a": 3, "b": {"c": 4}}
        task3 = manager_tests._create_task(
            task_manager, type="TEST_TASK", author=gui_su_session_login,
            priority=task1.Priority(task1.Priority.Class.BACKGROUND, task1.Priority.Subclass.LOW)
        )
        task2.timestamp_start = task2.timestamp_finish = time.time()
        task2.set_status(_TS.SUCCESS)
        task_manager.update(task2)

        ret = rest_su_session.task[{'type': task1.type}, : 100]
        assert ret['total'] == 1
        assert ret['limit'] == 100
        assert len(ret['items']) == 1
        assert ret['items'][0]['type'] == task1.type
        assert ret['items'][0]['id'] == task1.id

        ret = rest_su_session.task[{'type': task2.type}, : 100]
        assert ret['total'] == 2
        assert len(ret['items']) == 2
        assert ret['items'][0]['type'] == task3.type
        assert ret['items'][0]['id'] == task3.id
        assert ret['items'][1]['id'] == task2.id

        ret = rest_su_session.task[{'type': task2.type}, : 100: '+id']
        assert ret['total'] == 2
        assert len(ret['items']) == 2
        assert ret['items'][0]['type'] == task2.type
        assert ret['items'][0]['id'] == task2.id
        assert ret['items'][1]['id'] == task3.id

        # Order by complex field name
        ret = rest_su_session.task[{'type': task2.type}, : 100: '+updated']
        assert ret['items'][0]['id'] == task3.id
        assert ret['items'][1]['id'] == task2.id

        ret = rest_su_session.task[{'author': task1.author}, : 100: '-id']
        assert ret['total'] == 2
        assert ret['items'][0]['type'] == task2.type
        assert ret['items'][0]['id'] == task2.id
        assert ret['items'][1]['id'] == task1.id

        ret = rest_su_session.task[{'status': ','.join((_TS.DRAFT, _TS.SUCCESS))}, : 100]
        assert ret['total'] == 3
        assert ret['items'][0]['id'] == task3.id
        assert ret['items'][1]['id'] == task2.id
        assert ret['items'][2]['id'] == task1.id

        ret = rest_su_session.task[{'status': ','.join((_TS.DRAFT, str(_TS.Group.FINISH)))}, : 100]
        assert ret['total'] == 3
        assert ret['items'][0]['id'] == task3.id
        assert ret['items'][1]['id'] == task2.id
        assert ret['items'][2]['id'] == task1.id

        ret = rest_su_session.task[{'status': ','.join((_TS.DRAFT, _TS.SUCCESS))}, : 2]
        assert ret['total'] == 3
        assert len(ret['items']) == 2
        assert ret['items'][0]['id'] == task3.id
        assert ret['items'][1]['id'] == task2.id

        ret = rest_su_session.task[{'status': ','.join((_TS.DRAFT, _TS.SUCCESS))}, 2: 1]
        assert ret['total'] == 3
        assert len(ret['items']) == 1
        assert ret['items'][0]['id'] == task1.id

        ret = rest_su_session.task[{'id': [task1.id, task2.id]}, : 10]
        assert ret['total'] == 2
        assert len(ret['items']) == 2
        assert set(o['id'] for o in ret['items']) == {task1.id, task2.id}

        ret = rest_su_session.task[{'id': task1.id}, : 10]
        assert ret['total'] == 1
        assert len(ret['items']) == 1
        assert ret['items'][0]['id'] == task1.id

        fields = ['status', 'description']
        ret_partial = rest_su_session.task[{'id': task1.id, 'fields': fields}, : 10]
        fields.append('id')
        assert ret['total'] == 1
        assert sorted(ret_partial['items'][0].keys()) == sorted(fields)
        assert all(ret_partial['items'][0][field] == ret['items'][0][field] for field in fields)

        field = 'DEADBEAF'
        ret_not_existing_field = rest_session.task[{'id': task1.id, 'fields': field}, : 10]
        assert ret_not_existing_field['items'][0][field] is None

        field = 'priority.class'
        ret = rest_session.task[{'id': task3.id, 'fields': field}, : 10]
        assert ret['items'][0][field] == task3.Priority.Class.val2str(task3.Priority.Class.BACKGROUND)

        ret = rest_session.task[{'fields': 'context.a,context.b.c,context.d'}, : 10: '+id']
        assert ret['total'] == 3
        assert ret['items'][0] == {'context.a': 1, 'context.b.c': 2, 'context.d': None, 'id': task1.id}
        assert ret['items'][1] == {'context.a': 3, 'context.b.c': 4, 'context.d': None, 'id': task2.id}
        assert ret['items'][2] == {'context.a': None, 'context.b.c': None, 'context.d': None, 'id': task3.id}

        ret = rest_session.task[{'fields': 'context'}, : 10: '+id']
        assert ret['total'] == 3
        assert all(r['context'] == t.ctx for r, t in zip(ret['items'], (task1, task2, task3)))

        task = rest_su_session.task.create(type='TEST_TASK_2', custom_fields=[dict(name='live_time', value=42)])
        ret_partial = rest_su_session.task[{'id': task['id'], 'fields': ['input_parameters']}, : 10]
        assert ret_partial['items'][0]['input_parameters'] is not None
        assert ret_partial['items'][0]['input_parameters']['live_time'] == 42

        ret_partial = rest_su_session.task[{'id': task['id'], 'fields': ['input_parameters.live_time']}, : 10]
        assert ret_partial['items'][0]['input_parameters.live_time'] == 42

        for descr, substr in zip([u'фыв', u'юникод и латиница в descr'], [u'ы', u'юникод']):
            task = manager_tests._create_task(task_manager, parameters={"descr": descr})
            ret = rest_session.task[{'desc_re': substr}, : 10]
            assert ret['total'] == 1 and ret['items'][0]['description'] == task.descr

    def test__task_list_with_priority_filter(self, task_manager, rest_session):
        pclass, psubclass = ctt.Priority.Class, ctt.Priority.Subclass
        user_high = ctt.Priority(pclass.USER, psubclass.HIGH)
        service_high = ctt.Priority(pclass.SERVICE, psubclass.HIGH)
        user_low = ctt.Priority(pclass.SERVICE, psubclass.LOW)

        amount = 3
        for _ in range(amount):
            manager_tests._create_task(task_manager, type="TEST_TASK", status=ctt.Status.DRAFT, priority=user_high)
        manager_tests._create_task(task_manager, type="TEST_TASK", status=ctt.Status.DRAFT, priority=service_high)

        ret_all_user_high = rest_session.task[{'priority': '{}:{}'.format(*user_high.__getstate__())}, : amount]
        assert len(ret_all_user_high['items']) == amount
        assert all(
            ctt.Priority().__setstate__(ret_all_user_high['items'][i]['priority']) == user_high
            for i in range(amount)
        )

        ret_single_srv_high = rest_session.task[{'priority': '{}:{}'.format(*service_high.__getstate__())}, : amount]
        assert len(ret_single_srv_high['items']) == 1

        ret_none_user_low = rest_session.task[{'priority': '{}:{}'.format(*user_low.__getstate__())}, : amount]
        assert len(ret_none_user_low['items']) == 0

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.task[{'priority': 'SERICE:LOW'}, : 1]
        assert ex.value.status == http_client.BAD_REQUEST

    def test__task_id_get(self, rest_su_session, task_manager):
        model, arch, cores = 'Meine supermodel', 'linux', 32
        task = manager_tests._create_task(task_manager, type="TEST_TASK", model=model, arch=arch, cores=cores)
        ret = rest_su_session.task[task.id][...]
        assert ret['id'] == task.id
        assert ret['owner'] == task.owner
        assert all(
            ret['requirements'][key] == value for key, value in
            zip(('cpu_model', 'platform', 'cores'), (model, arch, cores))
        )
        task = manager_tests._create_task(task_manager, type="TEST_TASK")
        ret = rest_su_session.task[task.id][...]
        assert ret['id'] == task.id

    def test__task_audit(self, rest_session, rest_session_login, _task, task_session, client_node_id):
        task_session(rest_session, _task.id, client_node_id, login=rest_session_login)
        rest_session.task.current.audit(message="1", status=ctt.Status.ENQUEUING)

        ret = rest_session.task.audit[{"id": str(_task.id)}][:]
        assert isinstance(ret, list) and len(ret) == 2
        assert all(audit["task_id"] == _task.id for audit in ret)

        _task.reload()
        update = dt.datetime.utcfromtimestamp(_task.updated)
        delta = dt.timedelta(seconds=2)
        ret = rest_session.task.audit[{"since": (update + delta).isoformat()}][:]
        assert isinstance(ret, list) and not ret
        ret = rest_session.task.audit[{"since": (update - delta).isoformat()}][:]
        assert isinstance(ret, list) and ret

    def test__task_external_audit(
        self,
        rest_session_login, rest_session, rest_session2, task_manager, task_session, client_node_id
    ):
        task = manager_tests._create_task(task_manager, type="TEST_TASK", author=rest_session_login)
        updated = task.updated
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session2.task[str(task.id)].audit(message="1")
        assert ex.value.status == http_client.FORBIDDEN
        rest_session.task[str(task.id)].audit(message="1")
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.task[str(task.id)].audit(message="2", status=ctt.Status.ENQUEUING)
        assert ex.value.status == http_client.FORBIDDEN

        task_session(rest_session, task.id, client_node_id, login=rest_session_login)
        rest_session.task[str(task.id)].audit(message="2")
        rest_session.task.current.audit(message="3")

        ret = rest_session.task.audit[{"id": str(task.id)}][:]

        assert isinstance(ret, list) and len(ret) == 4
        assert all(audit["task_id"] == task.id for audit in ret)

        a = ret[1]
        assert a["iface"] == ctt.RequestSource.API and a["message"] == "1" and not a.get("status")

        task.reload()
        assert int(updated) == int(task.updated)

    def test__list_audit_large_interval(self, rest_session):
        to = dt.datetime.utcnow()
        since = to - dt.timedelta(days=json_task.Task.LIST_AUDIT_MAX_INTERVAL.days + 1)
        with pytest.raises(common_rest.Client.HTTPError) as ex:
            rest_session.task.audit.read(since=since.isoformat(), to=to.isoformat())
        assert ex.value.status == http_client.BAD_REQUEST

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    def test__list_audit_by_ip(self, rest_session, test_task_2):
        task = test_task_2(None, description=u"Test Task")

        ret_1 = rest_session.task[task.id].audit.read()[0]
        ret_2 = rest_session.task.audit.read(remote_ip=ret_1["source"])

        assert ret_1["task_id"] in (r["task_id"] for r in ret_2)
        assert ret_1["request_id"] in (r["request_id"] for r in ret_2)

        for audit in ret_2:
            assert audit["source"] == ret_1["source"]

    def test__task_id_audit(self, rest_session, _task):
        ret = rest_session.task[_task.id].audit[:]
        assert isinstance(ret, list)
        assert isinstance(next(iter(ret)), dict)

    def test__task_id_queue(self, rest_session, _task):
        ret = rest_session.task[_task.id].queue[:]
        assert isinstance(ret, list)

    def test__task_id_context(self, rest_session, _task):
        ret = rest_session.task[_task.id].context[:]
        assert isinstance(ret, dict)

    def test__task_id_children(self, rest_session, _task):
        ret = rest_session.task[_task.id].children[:]
        assert ret == {"items": [], "limit": 0, "offset": 0, "total": 0}

    def test__task_id_dependant(self, rest_session, _task, task_manager):
        ret = rest_session.task[_task.id].dependant[:]
        assert isinstance(ret, list)

        parent_task = manager_tests._create_task(
            task_manager,
            type="TEST_TASK",
            status=ctt.Status.SUCCESS
        )

        resource = manager_tests._create_resource(
            task_manager,
            resource_type="SANDBOX_TASKS_BINARY",
            task=parent_task,
        )

        for _ in range(3):
            dependent_task = manager_tests._create_task(task_manager, type="TEST_TASK")
            task_manager.register_dep_resource(dependent_task.id, resource.id)

        assert len(rest_session.task[parent_task.id].dependant.read()) == 3
        assert len(rest_session.task[parent_task.id].dependant.read({"limit": 2})) == 2
        assert len(rest_session.task[parent_task.id].dependant.read({"limit": 2, "offset": 1})) == 2
        assert len(rest_session.task[parent_task.id].dependant.read({"limit": 1, "offset": 2})) == 1

    def test__task_id_custom_fields(self, rest_session, _task):
        ret = rest_session.task[_task.id].custom.fields[:]
        assert isinstance(ret, list)
        assert isinstance(next(iter(ret)), dict)
        assert (
            set(o.name for o in _task.input_parameters if not o.dummy) ==
            set(o["name"] for o in ret if o["type"] != "block")
        )

    def test__task_id_custom_footer(self, rest_session, _task, _no_code_task):
        ret = rest_session.task[_task.id].custom.footer[:]
        assert isinstance(ret, list)
        assert "helperName" in ret[0]
        assert "content" in ret[0]
        assert rest_session.task[_no_code_task.id].custom.footer.read() == []

    def test__task_id_resources(self, rest_session, _task, task_manager):
        resources_num = 2
        resources = [
            manager_tests._create_resource(
                task_manager,
                parameters={'resource_filename': 'unit_test_resource{}'.format(i)},
                task=_task,
                create_logs=False
            )
            for i in range(resources_num)
        ]
        ret = rest_session.task[_task.id].resources[:]
        assert ret['total'] == resources_num
        assert set(o['id'] for o in ret['items'] if o['type'] != 'TASK_LOGS') == set(o.id for o in resources)

    def test__task_id_requirements(self, rest_session, task_manager, resource_manager):
        task = manager_tests._create_task(task_manager, type="TEST_TASK", parameters={"descr": "moo"})
        ret = rest_session.task[task.id].requirements[:]
        assert ret['total'] == 0
        assert len(ret['items']) == 0

        resources_num = 2
        resources = [
            manager_tests._create_resource(
                task_manager,
                parameters={'resource_filename': 'unit_test_resource{}'.format(i)},
                create_logs=False
            )
            for i in range(resources_num)
        ]
        [task_manager.register_dep_resource(task.id, resource.id) for resource in resources]
        ret = rest_session.task[task.id].requirements[:]
        assert set(o['id'] for o in ret['items'] if o['type'] != 'TASK_LOGS') == set(o.id for o in resources)

    def test__create_task_w_context(self, task_manager, rest_session):
        new_task = rest_session.task(type='TEST_TASK', context={'exclusive_param': 'Value'})
        task = task_manager.load(new_task['id'])
        assert task.ctx['exclusive_param'] == 'Value'

    def test__create_task(self, task_manager, rest_session, rest_session_login, rest_su_session, rest_su_session_login):
        new_task = rest_session.task(type='TEST_TASK')
        assert new_task['status'] == 'DRAFT'
        assert new_task['author'] == rest_session_login

        task = task_manager.load(new_task['id'])

        assert new_task['author'] == rest_session_login
        assert new_task['id'] == task.id
        assert new_task['notifications'][0]['recipients'] == filter(None, [task.owner, task.author])
        assert new_task['notifications'][0]['transport'] == 'email'

        task.ctx['live_time'] = 20

        task.descr = "Test task with random {:x}".format(random.randrange(0xFFFFFFFF))
        task_manager.update(task)

        # Create a copy
        new_task = rest_su_session.task(source=task.id)
        loaded_task = task_manager.load(new_task['id'])
        assert loaded_task.ctx['live_time'] == task.ctx['live_time']
        assert task.id != new_task['id']
        assert task.descr == new_task['description']
        assert new_task['notifications'][0]['recipients'] == [rest_su_session_login]

    def test__create_task_group_not_exist(self, rest_session):
        with pytest.raises(rest_session.HTTPError) as exc:
            rest_session.task(type="TEST_TASK_2", owner="GROUP_NOT_EXISTING")
        assert exc.value.response.status_code == http_client.BAD_REQUEST
        reason = exc.value.response.json()["reason"]
        assert "exist" in reason and "GROUP_NOT_EXISTING" in reason

    @pytest.mark.parametrize("task_type", ["TEST_TASK", "TEST_TASK_2"])
    def test__create_task_using_scheduler(self, task_type, rest_session, rest_session_login):
        sch_author = user_test_models.register_user("scheduler-author")
        sch_author_group = user_controller.Group.create(mapping.Group(name="GROUP", users=[sch_author]))
        scheduler = scheduler_controller.Scheduler.create(task_type, sch_author_group.name, sch_author)

        new_task = rest_session.task(scheduler_id=scheduler.id)

        assert new_task["type"] == task_type
        assert new_task["scheduler"]["id"] == -scheduler.id
        assert new_task["author"] == rest_session_login
        assert new_task["owner"] == ""  # since task author is not in scheduler author's group

    @pytest.mark.parametrize("task_type", ["TEST_TASK", "TEST_TASK_2"])
    def test__create_task_with_full_data(self, task_manager, task_type, rest_session, rest_session_login):
        sdk2_task = task_type == "TEST_TASK_2"
        resource = manager_tests._create_resource(
            task_manager, parameters={"resource_filename": "unit_test_resource"}, create_logs=False,
            resource_type='TEST_TASK_2_RESOURCE' if sdk2_task else 'TEST_TASK_RESOURCE'
        )
        code_archive_resource = manager_tests._create_resource(
            task_manager, parameters={"resource_type": "SANDBOX_TASKS_ARCHIVE"}, create_logs=False
        )
        data = TestRESTAPITask._task_update_data("Description", rest_session_login, resource.id, sdk2_task=sdk2_task)
        data.update({
            "type": task_type,
            "tasks_archive_resource": code_archive_resource.id,
            "dump_disk_usage": False,
            "tcpdump_args": '"host ya.ru and port 443" -v',
            "tags": ["AAA", "BBB"],
            "hints": [1, "abCd", ""],
            "max_restarts": 42,
            "kill_timeout": 3600,
            "suspend_on_status": [ctt.Status.EXCEPTION],
            "score": 5,
            "notifications": [{
                "statuses": [ctt.Status.SUCCESS],
                "transport": "email",
                "recipients": [rest_session_login],
                "check_status": None,
                "juggler_tags": []
            }],
            "fail_on_any_error": True,
            "hidden": True,
            "priority": {
                "class": ctt.Priority.Class.BACKGROUND,
                "subclass": ctt.Priority.Subclass.LOW,
            },
            "context": {
                "foo": "bar",
                "baz": "quux",
            }
        })

        requirements = {
            "ram": 2 << 30,
            "cores": 32,
            "dns": ctm.DnsType.DNS64,
            "cpu_model": "chip",
        }
        if task_type == "TEST_TASK":
            data.update(se_tag="limit1")
            requirements.update({
                "platform": "linux",
            })
        data.update(requirements=requirements)

        new_task = rest_session.task(data)
        do_not_check = ["priority", "custom_fields", "context", "hints"]
        for field in data:
            if field in do_not_check:
                continue
            if isinstance(data[field], dict):
                for key in data[field].iterkeys():
                    assert new_task[field][key] == data[field][key], "field {!r}[{!r}] has different values".format(
                        field, key
                    )
            else:
                assert new_task[field] == data[field], "field {!r} has different values for task {!r}".format(
                    field,
                    new_task["id"]
                )
        assert ctt.Priority.make(data["priority"]) == ctt.Priority.make(new_task["priority"])
        # assert set(new_task["hints"]) == set(["1", "abCd"])

        sent = {f["name"]: f["value"] for f in data["custom_fields"]}

        parameters = rest_session.task[new_task["id"]].custom.fields.read()
        check_description = {
            "string_parameter": "Description for String parameter",
            "dict_of_strings": "Description for Dict parameter",
            "list_of_strings": "Description for List parameter",
        } if task_type == "TEST_TASK_2" else {}

        for p in parameters:
            if p["name"] in sent:
                assert p["value"] == sent[p["name"]]
            if p["name"] in check_description:
                assert p["description"] == check_description[p["name"]]

        context = rest_session.task[new_task["id"]].context.read()
        for k, v in data["context"].items():
            assert context[k] == v

        assert set(mapping.Task.objects.with_id(new_task["id"]).hints) == {"1", "abCd"}

    # FIXME: SANDBOX-4999: Validation temporarily turned off, due to tasks with invalid parameters
    @pytest.mark.xfail(run=False)
    def test__create_invalid_task(self, rest_session, rest_session_login):
        task = rest_session.task.create(
            type="TEST_TASK_2", owner=rest_session_login, custom_fields=[dict(name="_container", value="None")]
        )
        task_id = task["id"]
        assert rest_session.task[task_id][:]["status"] == ctt.Status.DRAFT
        result = rest_session.batch.tasks.start.update([task["id"]])
        assert rest_session.task[task_id][:]["status"] == ctt.Status.DRAFT
        error_message = "Invalid resource id(s): u'None'"
        assert result == [{"status": "ERROR", "message": error_message, "id": task_id}]
        assert error_message in rest_session.task[task_id].context[:]["__last_error_trace"]

    def test__copy_task_and_modify_fields(
        self, task_manager, rest_session, rest_session_login, rest_session_group
    ):
        assert rest_session_login != rest_session_group

        task = manager_tests._create_task(task_manager, "TEST_TASK", owner=rest_session_login)
        task_copy = rest_session.task(source=task.id, owner=rest_session_group, context={"live_time": 93})
        assert task.owner == rest_session_login and task_copy["owner"] == rest_session_group
        assert rest_session.task[task_copy["id"]].context.read()["live_time"] == 93

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    def test__copy_privileged_task(
        self, rest_session, rest_session_login, test_task_2
    ):
        task = test_task_2(None, description="Test task")
        mapping.Task.objects.filter(id=task.id).update(set__requirements__privileged=True)
        assert rest_session.task[task.id][:]["requirements"]["privileged"]

        task_copy = rest_session.task(source=task.id, owner=rest_session_login)
        assert not rest_session.task[task_copy["id"]][:]["requirements"]["privileged"]

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    @pytest.mark.parametrize("sdk", ["SDK1", "SDK2"])
    def test__copy_fields(self, sdk, task_manager, rest_session, rest_session_login, test_task_2):

        kill_timeout = 1234

        if sdk == "SDK1":
            task = manager_tests._create_task(
                task_manager, "TEST_TASK", author=rest_session_login, context={"kill_timeout": kill_timeout}
            )
        else:
            task = test_task_2(None, description="Test task", kill_timeout=kill_timeout)
            task.Parameters.tags = []
            task.save()

        notifications = [
            mapping.Task.Notification(statuses=[ctt.Status.EXCEPTION], transport="email", recipients=[task.author]),
            mapping.Task.Notification(statuses=[ctt.Status.RELEASED], transport="email", recipients=[task.author]),
        ]
        mapping.Task.objects(id=task.id).update_one(set__notifications=notifications)

        task_copy_id = rest_session.task(source=task.id)["id"]
        task_copy_model = mapping.Task.objects.with_id(task_copy_id)
        task_copy = task_controller.TaskWrapper(task_copy_model)

        # Notifications; make objects more diff-friendly first.
        notifications_copy = [_.to_mongo() for _ in task_copy_model.notifications]
        notifications = [_.to_mongo() for _ in notifications]
        assert notifications_copy == notifications

        # Time to kill
        assert task_copy.kill_timeout == kill_timeout

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    def test__add_remove_task_tag(
        self, task_manager, rest_session, rest_session_login, test_task_2
    ):
        task1 = manager_tests._create_task(task_manager, "TEST_TASK", owner=rest_session_login)
        task2 = test_task_2(None, description="Test task")
        task2.Parameters.tags = []
        task2.save()

        for task in (task1, task2):
            rest_session.task[task.id].tags(["test_tag"])
            rest_session.task[task.id].tags(["test_tag"])  # expect no effect since tag names are unique

            assert rest_session.task[task.id][:]["tags"] == ["TEST_TAG"]
            assert mapping.TaskTagCache.objects.filter(tag="TEST_TAG").first()

            rest_session.task[task.id].tags(["test_tag2"])
            assert rest_session.task[task.id][:]["tags"] == ["TEST_TAG", "TEST_TAG2"]
            assert mapping.TaskTagCache.objects.filter(tag="TEST_TAG2").first()

            del rest_session.task[task.id].tags["test_tag"]
            assert rest_session.task[task.id][:]["tags"] == ["TEST_TAG2"]

            rest_session.task[task.id].tags.delete(["test_tag3"])
            assert rest_session.task[task.id][:]["tags"] == ["TEST_TAG2"]

            mapping.TaskTagCache.objects.delete()

    @staticmethod
    def _task_update_data(description, group_name, resource_id, sdk2_task=False):
        return {
            'description': description,
            'fail_on_any_error': True,
            'owner': group_name,
            'priority': {'class': 'SERVICE', 'subclass': 'HIGH'},
            'custom_fields': [{"name": k, "value": v} for k, v in {
                'live_time': 5,
                'dependent_resource' if sdk2_task else 'dependent_resource_id': resource_id,
                'modify_resource': False,
                'wait_time': 1,
                'create_sub_task': True,
                'number_of_subtasks': 3,
                'check_vault': True,
                'vault_item_name': 'vault_item',
                'vault_item_owner': 'vault_owner',
                'create_resources': False,
                'test_get_arcadia_url': '',
                'raise_exception_on_start': False,
                'go_to_state': ctt.Status.SUCCESS,
                'ping_host_via_skynet': '',
            }.iteritems()],
        }

    def test__update_task(self, rest_su_session, task_manager, rest_su_session_login):
        task = manager_tests._create_task(
            task_manager, type="TEST_TASK", author=rest_su_session_login, parameters={"descr": "moo"}
        )
        task_id = task.id
        resource = manager_tests._create_resource(
            task_manager, parameters={"resource_filename": "unit_test_resource"}, create_logs=False)
        tasks_archive_resource = manager_tests._create_resource(
            task_manager, parameters={"resource_type": "SANDBOX_TASKS_BINARY"}, create_logs=False)
        group = user_controller.Group.create(
            mapping.Group(name='TEST', users=[rest_su_session_login], email='mail')
        )
        cpu_model, platform, description, ram, cores = 'chip', 'linux', 'Test description', 512 << 20, 32
        data = self._task_update_data(description, group.name, resource.id)
        data.update(
            requirements={
                'cpu_model': cpu_model, 'platform': platform, 'host': None, 'ram': ram, 'cores': cores
            },
            tasks_archive_resource=tasks_archive_resource.id,
            max_restarts=42,
            suspend_on_status=[ctt.Status.FAILURE],
            score=6
        )
        rest_su_session.task[task_id] = data

        task = task_manager.load(task_id)
        for key, value in ((p['name'], p['value']) for p in data['custom_fields']):
            assert task.ctx[key] == value, (key, task.ctx[key], value)
        assert task.tasks_archive_resource == tasks_archive_resource.id
        assert task.priority == task.Priority(task.Priority.Class.SERVICE, task.Priority.Subclass.HIGH)
        assert task.descr == description
        assert task.owner == group.name
        assert task.model == cpu_model
        assert task.cores == cores
        assert task.arch == platform
        assert task.required_ram == ram >> 20
        assert task.max_restarts == 42
        task_json = rest_su_session.task[task_id].read()
        assert tuple(task_json["suspend_on_status"]) == tuple(data["suspend_on_status"])
        assert task_json["score"] == 6

        rest_su_session.task[task_id] = update_data = {'description': 'New description'}
        task = task_manager.load(task_id)
        for key, value in ((p['name'], p['value']) for p in data['custom_fields']):
            assert task.ctx.get(key) == value, (key, task.ctx.get(key), value)
        assert task.priority == task.Priority(task.Priority.Class.SERVICE, task.Priority.Subclass.HIGH)
        assert task.descr == update_data['description']
        assert task.owner == group.name
        assert task.model == cpu_model
        assert task.cores == cores

        data['custom_fields'] = [{'name': 'create_sub_task', 'value': False}]
        rest_su_session.task[task_id] = data
        task = task_manager.load(task_id)
        assert 'number_of_subtasks' not in task.ctx

    def test__update_task_no_reqs(self, rest_su_session, task_manager, rest_su_session_login):
        task_id = manager_tests._create_task(
            task_manager, type="TEST_TASK", author=rest_su_session_login, parameters={"descr": "moo"}
        ).id
        resource = manager_tests._create_resource(
            task_manager, parameters={"resource_filename": "unit_test_resource"}, create_logs=False)
        group = user_controller.Group.create(
            mapping.Group(name='TEST', users=[rest_su_session_login], email='mail')
        )
        description = 'Test description'
        data = self._task_update_data(description, group.name, resource.id)
        custom_fields = data.pop('custom_fields')
        rest_su_session.task[task_id] = data
        rest_su_session.task[task_id].custom.fields = custom_fields

        task = task_manager.load(task_id)
        for key, value in ((p['name'], p['value']) for p in custom_fields):
            assert task.ctx.get(key) == value, (key, task.ctx.get(key), value)
        assert task.priority == task.Priority(task.Priority.Class.SERVICE, task.Priority.Subclass.HIGH)
        assert task.descr == description
        assert task.owner == group.name

    def test__update_task_client_tags(self, rest_session):
        data = rest_session.task.create(type="TEST_TASK_2")
        payload = {
            "requirements": {
                "client_tags": str(ctc.Tag.SERVER)
            }
        }
        rest_session.task[data["id"]] = payload
        new_data = rest_session.task[data["id"]][:]
        assert new_data["requirements"]["client_tags"] == str(ctc.Tag.SERVER)

    @pytest.mark.parametrize("task_type", ["TEST_TASK", "TEST_TASK_2"])
    def test__update_container_resource(self, rest_session, task_manager, task_type):
        data = rest_session.task.create(type=task_type)
        container_resource = manager_tests._create_real_resource(
            task_manager, {"resource_type": "LXC_CONTAINER"}
        )
        set_update = {
            "requirements": {
                "container_resource": container_resource.id
            }
        }
        reset_update = {
            "requirements": {
                "container_resource": None
            }
        }
        assert data["requirements"]["container_resource"] is None
        rest_session.task[data["id"]] = set_update
        new_data = rest_session.task[data["id"]][:]
        assert new_data["requirements"]["container_resource"] == container_resource.id
        rest_session.task[data["id"]] = reset_update
        new_data = rest_session.task[data["id"]][:]
        assert new_data["requirements"]["container_resource"] is None

    def test__invalid_client_tags(self, rest_session):

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.task.create(type="TEST_TASK_2", requirements={"client_tags": "foobar"})
        assert ex.value.status == http_client.BAD_REQUEST

        data = rest_session.task.create(type="TEST_TASK_2")

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.task[data["id"]].update(requirements={"client_tags": "foobar"})
        assert ex.value.status == http_client.BAD_REQUEST

    @pytest.mark.parametrize("task_type", ["TEST_TASK", "TEST_TASK_2"])
    def test__update_task_notifications(self, rest_session, rest_session_login, task_type):
        data = rest_session.task.create(type=task_type)
        task_id = data["id"]
        update = {
            "notifications": [
                {
                    "statuses": [ctt.Status.SUCCESS],
                    "transport": ctn.Transport.TELEGRAM,
                    "recipients": [rest_session_login],
                }
            ]
        }
        rest_session.task[task_id] = update
        new_data = rest_session.task[task_id][:]
        assert new_data["notifications"][0]["transport"] == ctn.Transport.TELEGRAM
        assert new_data["notifications"][0]["statuses"] == [ctt.Status.SUCCESS]

        update["notifications"][0]["statuses"] = ["PAUSED"]
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.task[task_id] = update
        assert ex.value.status == http_client.BAD_REQUEST

        data = rest_session.task.create(type=task_type)
        task_id = data["id"]
        test_tag = "test_tag"
        update = {
            "notifications": [
                {
                    "statuses": [ctt.Status.SUCCESS],
                    "transport": ctn.Transport.JUGGLER,
                    "recipients": ["host=test.host&service=test_service"],
                    "check_status": "OK",
                    "juggler_tags": [test_tag]
                }
            ]
        }
        rest_session.task[task_id] = update
        new_data = rest_session.task[task_id][:]
        assert new_data["notifications"][0]["transport"] == ctn.Transport.JUGGLER
        assert new_data["notifications"][0]["statuses"] == [ctt.Status.SUCCESS]
        assert new_data["notifications"][0]["check_status"] == ctn.JugglerStatus.OK
        assert new_data["notifications"][0]["juggler_tags"] == [test_tag]
        assert new_data["notifications"][0]["recipients"] == ["host=test.host&service=test_service"]

    def test__update_non_existent_task(self, rest_session, task_manager):
        task_id = 42
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.task[task_id] = {'owner': 'TEST'}
        assert ex.value.status == http_client.NOT_FOUND

    def test__update_tasks_no_perms(self, rest_session, task_manager):
        task_id = manager_tests._create_task(task_manager, type="TEST_TASK", parameters={"descr": "moo"}).id
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.task[task_id] = {}
        assert ex.value.status == http_client.FORBIDDEN

    def test__update_tasks_empty_data(self, rest_su_session, task_manager):
        task_id = manager_tests._create_task(task_manager, type="TEST_TASK", parameters={"descr": "moo"}).id
        rest_su_session.task[task_id] = {}

    def test__update_non_existent_owner(self, rest_session, rest_session_login, task_manager):
        task_id = manager_tests._create_task(
            task_manager, type="TEST_TASK", author=rest_session_login, parameters={"descr": "moo"}
        ).id

        owner = "NONE_EXISTS_GROUP"

        with pytest.raises(ValueError):
            user_controller.Group.get(owner)

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.task[task_id] = {"owner": owner}
        assert ex.value.status == http_client.BAD_REQUEST

    def test__update_description_in_BREAK(self, rest_session, rest_session_login, task_manager):
        task = manager_tests._create_task(
            task_manager, type="TEST_TASK", parameters={"descr": "moo"}, status=_TS.FAILURE, author=rest_session_login
        )

        assert task_manager.load(task.id).status == _TS.FAILURE

        rest_session.task[task.id] = {'description': u'фу'}
        assert task_manager.load(task.id).descr == u'фу'

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.task[task.id] = {'description': u'баз', 'z': 1}
        assert ex.value.status == http_client.BAD_REQUEST

    def test__update_description_in_EXECUTE(self, rest_session, rest_session_login, task_manager):
        task = manager_tests._create_task(
            task_manager, type="TEST_TASK", parameters={"descr": "moo"}, status=_TS.TEMPORARY, author=rest_session_login
        )

        assert task_manager.load(task.id).status == _TS.TEMPORARY

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.task[task.id] = {"description": u"бар"}
        assert ex.value.status == http_client.BAD_REQUEST

    def test__set_owner(
        self, rest_su_session, rest_su_session_login, rest_session, rest_session_login,
    ):
        task_id = rest_session.task.create({"type": "TEST_TASK"})["id"]
        group1 = user_controller.Group.create(mapping.Group(name="GROUP_WITHOUT_SU_1", users=[rest_session_login])).name
        group2 = user_controller.Group.create(mapping.Group(name="GROUP_WITHOUT_SU_2", users=[rest_session_login])).name
        su_group = user_controller.Group.create(mapping.Group(name="SU_GROUP", users=[rest_su_session_login])).name

        assert group1 not in user_controller.Group.get_user_groups(rest_su_session_login)
        assert group2 not in user_controller.Group.get_user_groups(rest_su_session_login)
        assert su_group not in user_controller.Group.get_user_groups(rest_session_login)

        def _test(rest_client, group_name, response_code):
            payload = {"owner": group_name}
            if response_code >= http_client.BAD_REQUEST:
                with pytest.raises(common_rest.Client.HTTPError) as err:
                    rest_client.task[task_id].update(payload)
                assert err.value.status == response_code
            else:
                rest_client.task[task_id].update(payload)
                assert mapping.Task.objects.with_id(task_id).owner == group_name

        for test_case, test_comment in (
            ((rest_session, group1, http_client.NO_CONTENT), rest_session_login),
            ((rest_session, group2, http_client.NO_CONTENT), rest_session_login),
            ((rest_session, su_group, http_client.FORBIDDEN), rest_session_login),
            ((rest_su_session, group1, http_client.NO_CONTENT), rest_su_session_login),
            ((rest_su_session, group2, http_client.NO_CONTENT), rest_su_session_login),
            ((rest_su_session, su_group, http_client.FORBIDDEN), rest_su_session_login),
        ):
            _logged_test_case(_test, test_case, test_comment)

    def test__update_someone_else_task(self, rest_su_session, rest_su_session_login, rest_session, rest_session_login):
        robot_login = user_test_models.register_robot("robot", [rest_session_login])
        someone_else = user_test_models.register_user("someone_else")
        group1 = user_controller.Group.create(mapping.Group(name="G1", users=[rest_session_login, robot_login])).name
        group2 = user_controller.Group.create(mapping.Group(name="G2", users=[robot_login, someone_else])).name
        task_id = rest_session.task.create({"type": "TEST_TASK"})["id"]

        def _test(user_name, group_name, response_code):
            mapping.Task.objects(id=task_id).update(author=user_name, owner=group_name)

            for payload in (
                {},
                {"owner": group_name},
            ):
                new_description = " ".join([user_name, group_name, str(uuid.uuid4())])
                payload["description"] = new_description

                if response_code >= http_client.BAD_REQUEST:
                    with pytest.raises(common_rest.Client.HTTPError) as err:
                        rest_session.task[task_id].update(payload)
                    assert err.value.status == response_code
                else:
                    rest_session.task[task_id].update(payload)
                    assert mapping.Task.objects.with_id(task_id).description == new_description

        for test_case in (
            (rest_session_login, group1, http_client.NO_CONTENT),
            (robot_login, group1, http_client.NO_CONTENT),
            (rest_su_session_login, group1, http_client.NO_CONTENT),
            (robot_login, group2, http_client.FORBIDDEN),
            (someone_else, group2, http_client.FORBIDDEN),
        ):
            _logged_test_case(_test, test_case)

    def test__set_author(self, rest_session, rest_session_login, rest_su_session, rest_su_session_login):
        robot_in_group_login = user_test_models.register_robot("robot-in-group", [rest_session_login])
        other_robot_login = user_test_models.register_robot("robot-not-in-group", [rest_session_login])
        other_user_login = user_test_models.register_user("other-user")

        group = user_controller.Group.create(
            mapping.Group(name="GROUP", users=[rest_session_login, robot_in_group_login, other_user_login])
        )

        TestDescr = collections.namedtuple("TestDescr", ["author", "owner", "return_code"])

        def _try_create_task(rest_client, current_login, td):  # type: (common_rest.Client, str, TestDescr) -> None
            payload = {
                "type": "TEST_TASK",
                "author": td.author,
                "owner": td.owner,
            }

            if td.return_code >= http_client.BAD_REQUEST:
                with pytest.raises(common_rest.Client.HTTPError) as exc:
                    rest_client.task.create(payload)
                assert exc.value.status == td.return_code
            else:
                resp = rest_client.task.create(payload)
                assert resp["author"] == (td.author or current_login)
                assert resp["owner"] == td.owner

        for test_descr in (
            TestDescr(None, None, http_client.OK),
            TestDescr(None, group.name, http_client.OK),
            TestDescr(rest_session_login, group.name, http_client.OK),
            TestDescr(robot_in_group_login, None, http_client.OK),
            TestDescr(robot_in_group_login, group.name, http_client.OK),
            TestDescr(other_robot_login, None, http_client.OK),
            TestDescr(other_robot_login, group.name, http_client.FORBIDDEN),
            TestDescr(other_user_login, None, http_client.FORBIDDEN),
            TestDescr(other_user_login, group.name, http_client.FORBIDDEN),
        ):
            _logged_test_case(_try_create_task, [rest_session, rest_session_login, test_descr])

        for test_descr in (
            TestDescr(rest_session_login, group.name, http_client.OK),
            TestDescr(robot_in_group_login, group.name, http_client.OK),
            TestDescr(other_robot_login, group.name, http_client.FORBIDDEN),
            TestDescr(other_user_login, group.name, http_client.OK),
        ):
            _logged_test_case(_try_create_task, [rest_su_session, rest_su_session_login, test_descr])

        tid = rest_su_session.task.create({"type": "TEST_TASK"})["id"]
        rest_su_session.task[tid].update({"author": rest_session_login})
        resp = rest_su_session.task[tid].read()
        assert resp["author"] == rest_su_session_login

    def test__current_context(self, rest_session, rest_session_login, task_manager, task_session):
        task = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=_TS.EXECUTING, author=rest_session_login
        )
        task_session(rest_session, task.id, login=rest_session_login)
        test_none = None
        test_str = u"test_str"
        test_int = 15
        test_float = 30.5
        test_arr = [u"ab", 3, 90.8]
        test_dict = {
            "test1": [u"arr", 24, 0.6],
            "test2": u"test_str",
            "3": u"some_value"
        }
        rest_session.task.current.context.value.update(key="test_none", value=test_none)
        rest_session.task.current.context.value.update(key="test_str", value=test_str)
        rest_session.task.current.context.value.update(key="test_int", value=test_int)
        rest_session.task.current.context.value.update(key="test_float", value=test_float)
        rest_session.task.current.context.value.update(key="test_arr", value=test_arr)
        rest_session.task.current.context.value.update(key="test_dict", value=test_dict)

        context = rest_session.task[task.id].context.read()

        def rec_check(d1, d2):
            assert type(d1) == type(d2)
            if isinstance(d1, list):
                assert len(d1) == len(d2)
                for i, v in enumerate(d1):
                    rec_check(v, d2[i])
                return
            if isinstance(d1, dict):
                assert frozenset(d1.keys()) == frozenset(d2.keys())
                for k, v in d1.iteritems():
                    rec_check(v, d2[k])
                return
            assert d1 == d2

        rec_check(context["test_none"], test_none)
        rec_check(context["test_str"], test_str)
        rec_check(context["test_int"], test_int)
        rec_check(context["test_float"], test_float)
        rec_check(context["test_arr"], test_arr)
        rec_check(context["test_dict"], test_dict)

    def test__create_audit(self, rest_session, rest_session_login, task_manager, task_session, client_node_id):
        task = manager_tests._create_task(task_manager, type="TEST_TASK", status=_TS.DRAFT, author=rest_session_login)
        task_session(rest_session, task.id, login=rest_session_login)
        message = "Test status switching"

        rest_session.task.current.audit({"status": _TS.ENQUEUING, "message": message})
        audit = rest_session.task[task.id].audit[:]
        assert len(audit) == 2
        assert audit[0]["status"] == _TS.DRAFT
        assert audit[1]["status"] == _TS.ENQUEUING
        assert audit[1]["message"] == message
        assert audit[1]["iface"] == ctt.RequestSource.TASK

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.task.current.audit({"expected_status": _TS.DRAFT, "status": _TS.EXECUTING})
        assert ex.value.status == http_client.CONFLICT
        assert ex.value.response.json()["reason"].startswith("Expected task status")

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.task.current.audit({"status": _TS.EXECUTING})
        assert ex.value.status == http_client.BAD_REQUEST
        assert ex.value.response.json()["reason"].startswith("Cannot switch task")

        rest_session.task.current.audit({"expected_status": _TS.ENQUEUING, "status": _TS.EXECUTING, "force": True})
        audit = rest_session.task[task.id].audit[:]
        assert len(audit) == 3
        assert audit[-1]["status"] == _TS.EXECUTING

        rest_session.task.current.audit({"status": _TS.EXCEPTION, "force": True})
        audit = rest_session.task[task.id].audit[:]
        assert len(audit) == 4
        assert audit[-1]["status"] == _TS.EXCEPTION

        rest_session.task.current.audit({"status": _TS.EXECUTING, "force": True})
        audit = rest_session.task[task.id].audit[:]
        assert len(audit) == 5
        assert audit[-1]["status"] == _TS.EXECUTING

        task.ctx = {"fail_on_any_error": True}
        task_manager.update(task)

        rest_session.task.current.audit({"status": _TS.EXCEPTION, "force": True, "message": message})
        audit = rest_session.task[task.id].audit[:]
        assert len(audit) == 6
        assert audit[-1]["status"] == _TS.FAILURE
        assert audit[-1]["message"] == "{}. Switched to {} instead of {}.".format(message, _TS.FAILURE, _TS.EXCEPTION)
        assert audit[-1]["iface"] == ctt.RequestSource.TASK

        waiting_task = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=_TS.STOPPING, author=rest_session_login
        )
        task_session(rest_session, waiting_task.id, login=rest_session_login)
        wait_targets = {"tasks": [1, 3]}
        rest_session.task.current.audit({
            "status": _TS.WAIT_TASK,
            "force": True,
            "message": message,
            "wait_targets": wait_targets})
        audit = rest_session.task[waiting_task.id].audit[:]
        print(audit[-1])
        assert len(audit[-1]["wait_targets"]["tasks"]) == len(wait_targets["tasks"])
        for index in range(0, len(wait_targets["tasks"])):
            assert audit[-1]["wait_targets"]["tasks"][index] == wait_targets["tasks"][index]

    def test__get_current(self, rest_session, rest_session_login, task_manager, task_session):
        task = manager_tests._create_task(
            task_manager, type="TEST_TASK", status=ctt.Status.DRAFT, author=rest_session_login
        )
        with pytest.raises(common_rest.Client.HTTPError):
            rest_session.task.current.read()
        task_session(rest_session, task.id, login=rest_session_login)
        data = rest_session.task.current[:]
        assert data["id"] == task.id
        assert data["status"] == task.status

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    def test__output_parameters(
        self, rest_session, rest_session_login, task_manager, test_task_2, task_session
    ):
        task = test_task_2(None, owner=rest_session_login, description=u"Test task")
        task_session(rest_session, task.id, login=rest_session_login)
        task.current = task

        with common_rest.DispatchedClient as dispatch:
            dispatch(lambda *_, **__: rest_session)
            # makes the request automatically
            task.Parameters.result = 123
            task.Parameters.head = 321

        # repeated request is allowed
        rest_session.task.current.output.update([{"name": "result", "value": 123}])

        # test we can't set output to a different value
        with pytest.raises(AttributeError):
            task.Parameters.result = 456

        # or via JSON API
        with pytest.raises(common_rest.Client.HTTPError) as ex:
            rest_session.task.current.output.update([{"name": "result", "value": 456}])
        assert ex.value.status == http_client.FORBIDDEN
        assert ex.value.response.json()["reason"].startswith("Output parameter")

        for any_param in (False, True):
            assert rest_session.task.read(
                output_parameters=dict(result=321), any_params=any_param, limit=1
            )["total"] == 0
            assert rest_session.task.read(
                output_parameters=dict(result=123), any_params=any_param, limit=1
            )["total"] == 1
            assert rest_session.task.read(
                output_parameters=dict(result=321, head=321), any_params=any_param, limit=1
            )["total"] == int(any_param)
            assert rest_session.task.read(
                output_parameters=dict(result=123, head=321), any_params=any_param, limit=1
            )["total"] == 1

        data = rest_session.task.current.output[:]
        found = False
        for item in data:
            if item["name"] == "result":
                assert item["value"] == 123
                found = True
        assert found

    def test__log_nodes(
        self, rest_session, task_manager,
    ):
        task = manager_tests._create_task(task_manager, status=ctt.Status.EXECUTING)
        resource = manager_tests._create_real_resource(
            task_manager, {"resource_type": "TASK_LOGS"}, task=task, mark_ready=True
        )

        res = rest_session.task[task.id][:]["logs"]
        assert len(filter(lambda _: _["node_type"] == "file", res)) == 2

        mapping.Resource.objects(id=resource.id).update(set__state=ctr.State.NOT_READY)
        res = rest_session.task[task.id][:]
        # during task execution, API reply only contains links to tail and execution_dir
        for key, node_type, cnt in (("tails", "tail", 2), ("logs", "file", 0)):
            assert len(filter(lambda _: _["node_type"] == node_type, res[key])) == cnt

    def test__task_set_priority(self, rest_session, rest_session_login, rest_su_session, task_manager):
        task = manager_tests._create_task(
            task_manager,
            author=rest_session_login, owner=rest_session_login, status=ctt.Status.ENQUEUED, type='TEST_TASK'
        )
        prio = ctt.Priority(ctt.Priority.Class.BACKGROUND, ctt.Priority.Subclass.LOW)
        assert rest_session.task[task.id][:]["priority"] == prio.as_dict()

        prio = ctt.Priority(ctt.Priority.Class.SERVICE, ctt.Priority.Subclass.NORMAL)
        rest_session.task[task.id] = {"priority": prio.as_dict()}
        assert rest_session.task[task.id][:]["priority"] == prio.as_dict()

        prio = ctt.Priority(ctt.Priority.Class.USER, ctt.Priority.Subclass.NORMAL)
        with pytest.raises(common_rest.Client.HTTPError) as ex:
            rest_session.task[task.id] = {"priority": prio.as_dict()}
        assert ex.value.status == http_client.BAD_REQUEST

        rest_su_session.task[task.id] = {"priority": prio.as_dict()}
        assert rest_session.task[task.id][:]["priority"] == prio.as_dict()

    def test__task_serialization_deserialization(self, test_task_2):
        task = test_task_2(None, json_parameter={"qwe": 123})

        tw = task_controller.TaskWrapper(task_controller.Task.get(task.id))
        assert task.Parameters.json_parameter == tw._task().Parameters.json_parameter

    def test__get_scheduler(self, rest_session_login, task_session, rest_session, test_task_2, serviceq):

        task = test_task_2(None)

        task_data = rest_session.task[task.id].read()
        assert "scheduler" not in task_data

        scheduler = scheduler_controller.Scheduler.create(
            "TEST_TASK_2", owner=rest_session_login, author=rest_session_login,
        )
        sch_task = scheduler_controller.Scheduler.create_new_task(scheduler)

        task_session(rest_session, sch_task["id"], login=rest_session_login)
        sch_task_data = rest_session.task[sch_task.id].read()
        assert sch_task_data["scheduler"]["id"] == scheduler.id

    def test__task_with_ramdrive(self, rest_session):

        size_mib = 42
        ramdrive = {"size": size_mib << 20, "type": "tmpfs"}  # size in bytes

        # Create task with ramdrive
        task = rest_session.task.create(type='TEST_TASK_2', requirements={"ramdrive": ramdrive})
        task_id = task["id"]
        data = rest_session.task[task_id].read()

        assert data["requirements"]["ramdrive"] == ramdrive
        assert mapping.Task.objects.get(id=task_id).requirements.ramdrive.size == size_mib

        size_mib = 84
        ramdrive = {"size": size_mib << 20, "type": "tmpfs"}  # size in bytes

        # Update task with ramdrive
        rest_session.task[task_id].update(requirements={"ramdrive": ramdrive})
        data = rest_session.task[task_id].read()

        assert data["requirements"]["ramdrive"] == ramdrive
        assert mapping.Task.objects.get(id=task_id).requirements.ramdrive.size == size_mib

    def test__initialization_from_on_create(self, rest_session, task_manager):
        data = rest_session.task.create(
            type="TEST_TASK_2"
        )
        assert data["input_parameters"]["initialized_from_on_create"] == 0

        data = rest_session.task.create(
            type="TEST_TASK_2",
            custom_fields=[
                dict(name=k, value=v)
                for k, v in dict(initialized_from_on_create=123).iteritems()
            ]
        )
        assert data["input_parameters"]["initialized_from_on_create"] == 123

        data = rest_session.task.create(
            type="TEST_TASK_2",
            custom_fields=[
                dict(name=k, value=v)
                for k, v in dict(set_custom_parameter_from_on_create=42, initialized_from_on_create=123).iteritems()
            ]
        )
        assert data["input_parameters"]["initialized_from_on_create"] == 42

        tasks_resource1 = manager_tests._create_real_resource(task_manager, {"resource_type": "SANDBOX_TASKS_BINARY"})
        tasks_resource2 = manager_tests._create_real_resource(task_manager, {"resource_type": "SANDBOX_TASKS_BINARY"})

        data = rest_session.task.create(
            type="TEST_TASK_2"
        )
        assert data["requirements"]["tasks_resource"] is None

        data = rest_session.task.create(
            type="TEST_TASK_2",
            requirements=dict(tasks_resource=tasks_resource1.id)
        )
        assert data["requirements"]["tasks_resource"] == tasks_resource1.id

        data = rest_session.task.create(
            type="TEST_TASK_2",
            requirements=dict(tasks_resource=tasks_resource1.id),
            custom_fields=[
                dict(name=k, value=v)
                for k, v in dict(set_tasks_resource_from_on_create=tasks_resource2.id).iteritems()
            ]
        )
        assert data["requirements"]["tasks_resource"] == tasks_resource2.id

    def test__create_task__resource_parameter_with_duplicated_resources(
        self, rest_session, rest_session_login, task_manager
    ):
        res1 = manager_tests._create_resource(
            task_manager, parameters={"resource_filename": "unit_test_resource"}, create_logs=False
        )
        res2 = manager_tests._create_resource(
            task_manager, parameters={"resource_filename": "unit_test_resource"}, create_logs=False
        )
        for dependent_resources in ([res1.id, res2.id, res1.id], [res2.id, res1.id, res1.id]):
            data = rest_session.task.create(
                type="TEST_TASK",
                custom_fields=[dict(name="dependent_resources", value=dependent_resources)]
            )
            assert rest_session.task[data["id"]].context[:]["dependent_resources"] == dependent_resources

            data = rest_session.task.create(
                type="TEST_TASK_2",
                custom_fields=[dict(name="dependent_resources", value=dependent_resources)]
            )
            params = data["input_parameters"]
            assert params["dependent_resources"] == dependent_resources

    def test__versioned_task_id_get(self, task_manager, json_api_url):
        model, arch, cores = "Test model", "linux", 32
        task = manager_tests._create_task(task_manager, type="TEST_TASK", model=model, arch=arch, cores=cores)
        client = common_rest.Client(json_api_url, version=100500)
        ret = client.task[task.id].read()
        assert ret["id"] == task.id
        assert ret["owner"] == task.owner
        assert all(
            ret["requirements"][key] == value for key, value in
            zip(("cpu_model", "platform", "cores"), (model, arch, cores))
        )

    @pytest.mark.parametrize("task_type", ["TEST_TASK", "TEST_TASK_2"])
    def test__create_task_with_container_parameter(self, task_manager, rest_session, rest_session_login, task_type):
        container_res1 = manager_tests._create_resource(
            task_manager, parameters={"resource_filename": "container", "attrs": {"platform": "linux"}},
            create_logs=False, resource_type="LXC_CONTAINER"
        )
        container_res2 = manager_tests._create_resource(
            task_manager, parameters={"resource_filename": "container", "attrs": {"platform": "linux"}},
            create_logs=False, resource_type="LXC_CONTAINER"
        )
        container_res3 = manager_tests._create_resource(
            task_manager, parameters={"resource_filename": "container", "attrs": {"platform": "linux"}},
            create_logs=False, resource_type="LXC_CONTAINER"
        )
        task = rest_session.task.create(
            type=task_type, owner=rest_session_login, custom_fields=[dict(name="_container", value=container_res1.id)]
        )
        task_id = task["id"]

        assert rest_session.task[task_id][:]["requirements"]["container_resource"] == container_res1.id
        container_field = filter(lambda _: _["name"] == "_container", rest_session.task[task_id].custom.fields[:])[0]
        assert int(container_field["value"]) == container_res1.id

        rest_session.task[task_id] = dict(custom_fields=[dict(name="_container", value=container_res2.id)])
        assert rest_session.task[task_id][:]["requirements"]["container_resource"] == container_res2.id
        container_field = filter(lambda _: _["name"] == "_container", rest_session.task[task_id].custom.fields[:])[0]
        assert int(container_field["value"]) == container_res2.id

        rest_session.task[task_id].custom.fields = [dict(name="_container", value=container_res3.id)]
        assert rest_session.task[task_id][:]["requirements"]["container_resource"] == container_res3.id
        container_field = filter(lambda _: _["name"] == "_container", rest_session.task[task_id].custom.fields[:])[0]
        assert int(container_field["value"]) == container_res3.id

    @pytest.mark.parametrize("task_type", ["TEST_TASK", "TEST_TASK_2"])
    def test__create_task_with_container_requirement(self, task_manager, rest_session, rest_session_login, task_type):
        container_res1 = manager_tests._create_resource(
            task_manager, parameters={"resource_filename": "container", "attrs": {"platform": "linux"}},
            create_logs=False, resource_type="LXC_CONTAINER"
        )
        container_res2 = manager_tests._create_resource(
            task_manager, parameters={"resource_filename": "container", "attrs": {"platform": "linux"}},
            create_logs=False, resource_type="LXC_CONTAINER"
        )
        task = rest_session.task.create(
            type=task_type, owner=rest_session_login, requirements={"container_resource": container_res1.id}
        )
        task_id = task["id"]

        assert rest_session.task[task_id][:]["requirements"]["container_resource"] == container_res1.id
        container_field = filter(lambda _: _["name"] == "_container", rest_session.task[task_id].custom.fields[:])[0]
        assert int(container_field["value"]) == container_res1.id

        rest_session.task[task_id] = dict(requirements={"container_resource": container_res2.id})
        assert rest_session.task[task_id][:]["requirements"]["container_resource"] == container_res2.id
        container_field = filter(lambda _: _["name"] == "_container", rest_session.task[task_id].custom.fields[:])[0]
        assert int(container_field["value"]) == container_res2.id

    @pytest.mark.parametrize("task_type", ["TEST_TASK", "TEST_TASK_2"])
    def test__create_task_with_container_requirement_and_parameter(
        self, task_manager, rest_session, rest_session_login, task_type
    ):
        container_res1 = manager_tests._create_resource(
            task_manager, parameters={"resource_filename": "container", "attrs": {"platform": "linux"}},
            create_logs=False, resource_type="LXC_CONTAINER"
        )
        container_res2 = manager_tests._create_resource(
            task_manager, parameters={"resource_filename": "container", "attrs": {"platform": "linux"}},
            create_logs=False, resource_type="LXC_CONTAINER"
        )
        container_res3 = manager_tests._create_resource(
            task_manager, parameters={"resource_filename": "container", "attrs": {"platform": "linux"}},
            create_logs=False, resource_type="LXC_CONTAINER"
        )
        task = rest_session.task.create(
            type=task_type, owner=rest_session_login, requirements={"container_resource": container_res1.id}
        )
        task_id = task["id"]

        assert rest_session.task[task_id][:]["requirements"]["container_resource"] == container_res1.id
        container_field = filter(lambda _: _["name"] == "_container", rest_session.task[task_id].custom.fields[:])[0]
        assert int(container_field["value"]) == container_res1.id

        rest_session.task[task_id] = dict(
            requirements={"container_resource": container_res2.id},
            custom_fields=[dict(name="_container", value=container_res3.id)]
        )
        assert rest_session.task[task_id][:]["requirements"]["container_resource"] == container_res3.id
        container_field = filter(lambda _: _["name"] == "_container", rest_session.task[task_id].custom.fields[:])[0]
        assert int(container_field["value"]) == container_res3.id

    def test__wait_output_parameters(
        self, task_manager, rest_session, rest_session_login, task_session
    ):
        task1 = rest_session.task.create(type="TEST_TASK_2", custom_fields=[dict(name="live_time", value=42)])
        task2 = rest_session.task.create(type="TEST_TASK_2", custom_fields=[dict(name="live_time", value=42)])
        task3 = rest_session.task.create(type="TEST_TASK_2", custom_fields=[dict(name="live_time", value=42)])
        task_session(rest_session, task2["id"], login=rest_session_login)
        rest_session.task.current.trigger.output.create(targets={task1["id"]: "result"}, wait_all=True)
        triggers = list(mapping.TaskOutputTrigger.objects())
        assert len(triggers) == 1
        trigger = triggers[0]
        assert trigger["source"] == task2["id"]
        assert len(trigger.targets) == 1
        assert trigger.targets[0].target == task1["id"]
        assert trigger.targets[0].field == "result"

        mp_task3 = mapping.Task.objects.with_id(task3["id"])
        mp_task3.parameters.output = [mapping.Task.Parameters.Parameter(key="result", value=0)]
        mp_task3.save()

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.task.current.trigger.output.create(targets={task3["id"]: "result"}, wait_all=True)
        assert ex.value.status == http_client.NOT_ACCEPTABLE
