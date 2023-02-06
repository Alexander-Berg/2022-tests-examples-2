import pytest
import httplib
import xmlrpclib

from sandbox.common import rest
from sandbox.common import errors as common_errors
from sandbox.common import itertools as common_it
from sandbox.common.types import task as ctt
from sandbox.common.types import resource as ctr

from sandbox.yasandbox.manager import tests
from sandbox.yasandbox.database import mapping

from sandbox.sandboxsdk import channel
from sandbox.sandboxsdk import sandboxapi


@pytest.fixture()
def sandboxapi_instance(server, api_session):
    channel.channel.sandbox.server.transport.auth = api_session.transport.auth
    return sandboxapi.Sandbox(
        url=server.url,
        auth=api_session.transport.auth,
    )


@pytest.fixture()
def sandboxapi_instance_su(server, api_su_session):
    channel.channel.sandbox.server.transport.auth = api_su_session.transport.auth
    return sandboxapi.Sandbox(
        url=api_su_session.url,
        auth=api_su_session.transport.auth,
    )


@pytest.fixture()
def sandboxapi_instance_trusted(api_trusted_session):
    channel.channel.sandbox.server.transport.auth = api_trusted_session.transport.auth
    return sandboxapi.Sandbox(
        url=api_trusted_session.url,
        auth=api_trusted_session.transport.auth,
    )


@pytest.fixture()
def sandboxapi_instance_rest(sdk2_dispatched_rest_session):
    return sandboxapi.SandboxRest()


class TestSandboxAPI:
    def test___to_id(self):
        class B:
            pass

        class C:
            id = 12

        b = B()
        c = C()

        cls = sandboxapi.Sandbox
        assert cls._to_id(12) == 12
        assert cls._to_id('12') == 12
        assert cls._to_id(C) == 12
        assert cls._to_id(c) == 12
        pytest.raises(sandboxapi.SandboxAPIValidateException, cls._to_id, None)
        pytest.raises(sandboxapi.SandboxAPIValidateException, cls._to_id, '')
        pytest.raises(sandboxapi.SandboxAPIValidateException, cls._to_id, '12a')
        pytest.raises(sandboxapi.SandboxAPIValidateException, cls._to_id, B)
        pytest.raises(sandboxapi.SandboxAPIValidateException, cls._to_id, b)

    def test__ping(self, sandboxapi_instance):
        assert sandboxapi_instance.ping()

    ########################################
    # task
    ########################################

    def test__list_task_types(self, sandboxapi_instance):
        ret = sandboxapi_instance.list_task_types()
        assert isinstance(ret, list)
        assert len(ret) > 0
        assert 'TEST_TASK' in ret

    def test__list_tasks(self, sandboxapi_instance, task_manager, serviceq):
        task = tests._create_task(
            task_manager,
            type='TEST_TASK',
            status=ctt.Status.DRAFT,
        )

        ret = sandboxapi_instance.list_tasks(task_type='TEST_TASK', status='NOT_READY')
        assert isinstance(ret, list)
        assert ret[0].id == task.id

    def test__get_task(self, sandboxapi_instance, task_manager, serviceq):
        assert not sandboxapi_instance.get_task(1)

        task = tests._create_task(
            task_manager,
            status=ctt.Status.DRAFT,
        )

        ret = sandboxapi_instance.get_task(task.id)
        assert isinstance(ret, sandboxapi.SandboxTask)
        assert ret.id == task.id
        assert ret.type == task.type

    def test__create_task(self, sandboxapi_instance, api_session_login, serviceq):
        ret = sandboxapi_instance.create_task('TEST_TASK', api_session_login, 'new task', enqueue=False)
        assert isinstance(ret, sandboxapi.SandboxTask)
        assert ret.type == 'TEST_TASK'
        assert ret.owner == api_session_login
        assert ret.description == 'new task'
        assert ret.priority == ['BACKGROUND', 'LOW']

    def test__create_task__user(self, sandboxapi_instance, api_session_group, serviceq):
        ret = sandboxapi_instance.create_task(
            'TEST_TASK', api_session_group, 'new task', priority=('SERVICE', 'NORMAL'), enqueue=False
        )
        assert ret.priority == ['SERVICE', 'NORMAL']

        ret = sandboxapi_instance.create_task(
            'TEST_TASK', api_session_group, 'new task', priority=('USER', 'HIGH'), enqueue=False
        )
        assert ret.priority == ['SERVICE', 'HIGH']

    def test__owner_match(self, sandboxapi_instance, serviceq, rest_session):
        with pytest.raises(rest_session.HTTPError) as ex:
            sandboxapi_instance.create_task('TEST_TASK', 'SOME_GROUP', 'new task', enqueue=False)
        assert ex.value.status == httplib.BAD_REQUEST

    def test__task_gsid(
        self, sandboxapi_instance, api_session_login, task_manager,
        serviceq, task_session, rest_session, monkeypatch
    ):
        ret = sandboxapi_instance.create_task(
            "TEST_TASK", api_session_login, "new task",
            context={"GSID": "TEST:1"}, priority=(ctt.Priority.Class.SERVICE, ctt.Priority.Subclass.LOW), enqueue=False
        )
        task_session(rest_session, ret.id, api_session_login)
        task = task_manager.load(ret.id)
        monkeypatch.setattr(channel.channel.sandbox, "_sdk_server", rest_session)
        subt = task.create_subtask("TEST_TASK", "new subtask", enqueue=False)
        assert subt.ctx["__GSID"] == "TEST:1 SB:TEST_TASK:{} USER:{} SB:TEST_TASK:{} USER:{}".format(
            ret.id, api_session_login, subt.id, api_session_login
        )

    def test__create_task__super_user(self, sandboxapi_instance_su, api_su_session_login, serviceq):
        ret = sandboxapi_instance_su.create_task(
            'TEST_TASK', api_su_session_login, 'new task', priority=('USER', 'HIGH'), enqueue=False
        )
        assert ret.priority == ['USER', 'HIGH']

    def test__create_task__trusted_user(self, sandboxapi_instance_trusted, api_trusted_session_group, serviceq):
        ret = sandboxapi_instance_trusted.create_task(
            'TEST_TASK', api_trusted_session_group, 'new task', priority=('SERVICE', 'HIGH'), enqueue=False
        )
        assert ret.priority == ['SERVICE', 'HIGH']

        ret = sandboxapi_instance_trusted.create_task(
            'TEST_TASK', api_trusted_session_group, 'new task', priority=('USER', 'HIGH'), enqueue=False
        )
        assert ret.priority == ['SERVICE', 'HIGH']

    def test__wait_task(self, sandboxapi_instance, task_manager):
        task = tests._create_task(
            task_manager,
            status=ctt.Status.DRAFT,
        )
        pytest.raises(
            sandboxapi.SandboxAPIException,
            sandboxapi_instance.wait_task,
            task.id, timeout=0,
        )
        for status in (
            ctt.Status.ENQUEUING,
            ctt.Status.ENQUEUED,
            ctt.Status.ASSIGNED,
            ctt.Status.PREPARING,
            ctt.Status.EXECUTING,
            ctt.Status.STOPPING,
            ctt.Status.WAIT_TASK,
            ctt.Status.ENQUEUING,
            ctt.Status.ENQUEUED,
            ctt.Status.ASSIGNED,
            ctt.Status.PREPARING,
            ctt.Status.EXECUTING,
            ctt.Status.FINISHING
        ):
            task.set_status(status)
            pytest.raises(
                sandboxapi.SandboxAPIException,
                sandboxapi_instance.wait_task,
                task.id, timeout=0,
            )
        task.set_status(ctt.Status.SUCCESS)
        task_manager.update(task)
        assert sandboxapi_instance.wait_task(task.id, timeout=0)

        task = tests._create_task(
            task_manager,
            status=ctt.Status.DRAFT,
        )
        pytest.raises(
            sandboxapi.SandboxAPIException,
            sandboxapi_instance.wait_task,
            task.id, timeout=0,
        )
        for status in (
            ctt.Status.ENQUEUING,
            ctt.Status.ENQUEUED,
            ctt.Status.ASSIGNED,
            ctt.Status.PREPARING,
            ctt.Status.EXECUTING,
            ctt.Status.STOPPING,
            ctt.Status.WAIT_TASK,
            ctt.Status.ENQUEUING,
            ctt.Status.ENQUEUED,
            ctt.Status.ASSIGNED,
            ctt.Status.PREPARING,
            ctt.Status.EXECUTING,
            ctt.Status.FINISHING
        ):
            task.set_status(status)
            pytest.raises(
                sandboxapi.SandboxAPIException,
                sandboxapi_instance.wait_task,
                task.id, timeout=0,
            )
        task.set_status(ctt.Status.FAILURE)
        task_manager.update(task)
        assert not sandboxapi_instance.wait_task(task.id, timeout=0)

    def test__set_task_context_value(self, sandboxapi_instance_su, task_session, task_manager, monkeypatch):
        task = tests._create_task(
            task_manager,
            status=ctt.Status.SUCCESS,
        )
        monkeypatch.setattr(channel.channel, "task", task)
        task_session(channel.channel.rest.server, task.id, "test", login="test")
        sandboxapi_instance_su.set_task_context_value(task.id, 'foo', 'boo')
        ret = sandboxapi_instance_su.get_task(task.id)
        assert 'foo' in ret.ctx
        assert ret.ctx['foo'] == 'boo'

    def test__set_task_priority__user(self, sandboxapi_instance, task_manager, api_session_group):
        task = tests._create_task(
            task_manager,
            status=ctt.Status.SUCCESS,
            owner=api_session_group
        )

        ret = sandboxapi_instance.get_task(task.id)
        assert ret.priority == ['BACKGROUND', 'LOW']

        sandboxapi_instance.set_task_priority(task.id, ('BACKGROUND', 'HIGH'))
        ret = sandboxapi_instance.get_task(task.id)
        assert ret.priority == ['BACKGROUND', 'HIGH']

        sandboxapi_instance.set_task_priority(task.id, ('SERVICE', 'NORMAL'))
        ret = sandboxapi_instance.get_task(task.id)
        assert ret.priority == ['SERVICE', 'NORMAL']

        pytest.raises(xmlrpclib.Fault, sandboxapi_instance.set_task_priority, task.id, ('USER', 'LOW'))

    def test__set_task_priority__super_user(
            self, sandboxapi_instance_su, task_manager, gui_su_session_login):
        task = tests._create_task(
            task_manager,
            status=ctt.Status.SUCCESS,
            owner=gui_su_session_login
        )

        ret = sandboxapi_instance_su.get_task(task.id)
        assert ret.priority == ['BACKGROUND', 'LOW']

        sandboxapi_instance_su.set_task_priority(task.id, ('USER', 'HIGH'))
        ret = sandboxapi_instance_su.get_task(task.id)
        assert ret.priority == ['USER', 'HIGH']

    def test__set_task_priority__trusted_user(
            self, sandboxapi_instance_trusted, task_manager, api_trusted_session_group
    ):
        task = tests._create_task(
            task_manager,
            status=ctt.Status.SUCCESS,
            owner=api_trusted_session_group
        )

        ret = sandboxapi_instance_trusted.get_task(task.id)
        assert ret.priority == ['BACKGROUND', 'LOW']

        sandboxapi_instance_trusted.set_task_priority(task.id, ('SERVICE', 'HIGH'))
        ret = sandboxapi_instance_trusted.get_task(task.id)
        assert ret.priority == ['SERVICE', 'HIGH']

        pytest.raises(xmlrpclib.Fault, sandboxapi_instance_trusted.set_task_priority, task.id, ('USER', 'HIGH'))

    def test__list_resource_types(self, sandboxapi_instance):
        ret = sandboxapi_instance.list_resource_types()
        assert isinstance(ret, list)
        assert len(ret) > 0
        assert 'TEST_TASK_RESOURCE' in ret

    @staticmethod
    def __compare_resource_lists(list1, list2):
        assert len(list1) == len(list2)
        for i in xrange(len(list1)):
            for attr in (
                'arch', 'attributes', 'complete', 'description', 'file_md5',
                'file_name', 'host', 'id', 'owner', 'path', 'proxy_url',
                'size', 'skynet_id', 'status', 'task_id', 'timestamp', 'type', 'url',
            ):
                assert getattr(list1[i], attr) == getattr(list2[i], attr)

    def test__list_resources(
            self, sandboxapi_instance, sandboxapi_instance_rest, task_manager, resource_manager
    ):
        assert not sandboxapi_instance.list_resources()

        task = tests._create_task(
            task_manager,
            status=ctt.Status.SUCCESS,
        )
        res = tests._create_real_resource(
            task_manager,
            {'resource_type': 'TEST_TASK_RESOURCE'},
            task=task,
        )

        ret = sandboxapi_instance.list_resources(resource_type='TEST_TASK_RESOURCE')
        ret2 = sandboxapi_instance_rest.list_resources(resource_type='TEST_TASK_RESOURCE')

        assert isinstance(ret, list)
        assert isinstance(ret[0], sandboxapi.SandboxResource)
        assert ret[0].id == res.id

        self.__compare_resource_lists(ret, ret2)

    def test__list_resources__task_id(self, sandboxapi_instance, task_manager, resource_manager):
        assert not sandboxapi_instance.list_resources(task_id=1, hidden=True)

        task = tests._create_task(
            task_manager,
            status=ctt.Status.SUCCESS,
        )
        res = tests._create_real_resource(
            task_manager,
            {'resource_type': 'TEST_TASK_RESOURCE'},
            task=task,
        )

        ret = sandboxapi_instance.list_resources(task_id=task.id, hidden=True)
        assert isinstance(ret, list)
        assert isinstance(ret[0], sandboxapi.SandboxResource)
        assert len(ret) == 2
        assert ret[0].id == res.id
        assert ret[0].type == str(res.type)

    def test__list_resources__last_with_attr(self, sandboxapi_instance, task_manager, resource_manager):
        task = tests._create_task(
            task_manager,
            status=ctt.Status.SUCCESS,
        )
        res = tests._create_real_resource(
            task_manager,
            {'resource_type': 'TEST_TASK_RESOURCE', 'attrs': {'foo': 'boo'}},
            task=task,
        )
        # get last
        ret = sandboxapi_instance.list_resources(
            resource_type='TEST_TASK_RESOURCE', any_attrs={'foo': None})
        assert ret[0].id == res.id
        ret = sandboxapi_instance.list_resources(
            resource_type='TEST_TASK_RESOURCE', any_attrs={'foo': 'boo'})
        assert ret[0].id == res.id
        ret = sandboxapi_instance.list_resources(
            resource_type='TEST_TASK_RESOURCE', any_attrs={'foo': None, '_foo': None})
        assert ret[0].id == res.id
        ret = sandboxapi_instance.list_resources(
            resource_type='TEST_TASK_RESOURCE', all_attrs={'foo': None, '_foo': None})
        assert not ret
        ret = sandboxapi_instance.list_resources(
            resource_type='TEST_TASK_RESOURCE', any_attrs={'_foo': 'boo'})
        assert not ret

    def test__list_resources__order_by(self, sandboxapi_instance, task_manager, resource_manager):
        task = tests._create_task(
            task_manager,
            status=ctt.Status.SUCCESS,
        )
        res1 = tests._create_real_resource(
            task_manager,
            {
                'resource_type': 'TEST_TASK_RESOURCE',
                'resource_desc': 'res 1',
                'resource_filename': 'res_1',
            },
            task=task,
        )
        res2 = tests._create_real_resource(
            task_manager,
            {
                'resource_type': 'TEST_TASK_RESOURCE',
                'resource_desc': 'res 2',
                'resource_filename': 'res_2',
            },
            task=task,
        )

        ret = sandboxapi_instance.list_resources(
            resource_type='TEST_TASK_RESOURCE', order_by='-id')
        assert ret[0].id == res2.id
        assert ret[1].id == res1.id

        ret = sandboxapi_instance.list_resources(
            resource_type='TEST_TASK_RESOURCE', order_by='+id')
        assert ret[0].id == res1.id
        assert ret[1].id == res2.id

    def test__get_resource(self, sandboxapi_instance, task_manager, resource_manager):
        assert not sandboxapi_instance.get_resource(1)

        task = tests._create_task(
            task_manager,
            status=ctt.Status.SUCCESS,
        )
        res = tests._create_real_resource(
            task_manager,
            {'resource_type': 'TEST_TASK_RESOURCE'},
            task=task,
        )

        ret = sandboxapi_instance.get_resource(res.id)
        assert isinstance(ret, sandboxapi.SandboxResource)
        assert ret.id == res.id
        assert ret.type == str(res.type)

    def test__delete_resource(self, sandboxapi_instance_su, task_manager):
        task = tests._create_task(
            task_manager,
            status=ctt.Status.SUCCESS,
        )
        res = tests._create_real_resource(
            task_manager,
            {'resource_type': 'TEST_TASK_RESOURCE'},
            task=task,
        )

        sandboxapi_instance_su.delete_resource(res.id)
        ret = sandboxapi_instance_su.get_resource(res.id)
        assert ret.status == 'READY'

        sandboxapi_instance_su.delete_resource(res.id, ignore_last_usage_time=True)
        ret = sandboxapi_instance_su.get_resource(res.id)
        assert ret.status == 'DELETED'

    def test__resource_attributes(self, sandboxapi_instance, task_manager, api_session_login):
        task = tests._create_task(
            task_manager,
            status=ctt.Status.SUCCESS,
            owner=api_session_login
        )
        res = tests._create_real_resource(
            task_manager,
            {'resource_type': 'TEST_TASK_RESOURCE'},
            task=task,
        )
        # set
        sandboxapi_instance.set_resource_attribute(res.id, 'foo', 'boo')
        ret = sandboxapi_instance.get_resource(res.id)
        assert 'foo' in ret.attributes
        # get
        ret = sandboxapi_instance.get_resource_attribute(res.id, 'foo')
        assert ret == 'boo'
        # drop
        sandboxapi_instance.drop_resource_attribute(res.id, 'foo')
        ret = sandboxapi_instance.get_resource(res.id)
        assert 'foo' not in ret.attributes

    def test__get_resource_hosts(self, sandboxapi_instance_su, task_manager, client_node_id):
        task = tests._create_task(
            task_manager,
            status=ctt.Status.SUCCESS,
        )
        res = tests._create_real_resource(
            task_manager,
            {'resource_type': 'TEST_TASK_RESOURCE'},
            task=task,
        )

        ret = sandboxapi_instance_su.get_resource_hosts(res.id)
        assert client_node_id in ret

    ########################################
    # release
    ########################################

    def test__list_releases(
        self, sandboxapi_instance, server, client_node_id, api_su_session, rest_su_session,
        task_manager, release_manager, releaser, monkeypatch, task_session, service_user,
        sandboxapi_instance_rest, fake_agentr
    ):
        import sandbox.executor.commands.task
        reload(sandbox.executor.commands.task)
        monkeypatch.setattr(channel.channel.sandbox, 'server', api_su_session)
        monkeypatch.setattr(rest.Client, '__new__', classmethod(lambda *_, **__: rest_su_session))
        monkeypatch.delattr(rest.Client, '__init__')

        task = tests._create_task(
            task_manager,
            status=ctt.Status.SUCCESS,
        )
        res = tests._create_real_resource(
            task_manager,
            {'resource_type': 'TEST_TASK_RESOURCE'},
            task=task,
        )
        release_manager.release_task(task.id, releaser, status='stable', message_subject='subject')
        task.reload()
        task_session(rest_su_session, task.id)
        status, message = sandbox.executor.commands.task.ReleaseTask(
            task.id, 'log1',
            release_params=mapping.to_dict(task.release_params),
            agentr=fake_agentr(task)
        ).execute()
        assert status == ctt.Status.RELEASED
        task.set_status(status, message)

        ret = sandboxapi_instance.list_releases(resource_type='TEST_TASK_RESOURCE')
        ret2 = sandboxapi_instance_rest.list_releases(resource_type='TEST_TASK_RESOURCE')
        assert isinstance(ret, list)
        assert isinstance(ret[0], sandboxapi.SandboxRelease)
        assert ret[0].task_id == task.id
        assert ret[0].resources[0].id == res.id

        assert len(ret) == len(ret2)
        for i in xrange(len(ret)):
            for attr in (
                'status', 'task_id', 'owner', 'timestamp', 'id', 'subject'
            ):
                assert getattr(ret[i], attr) == getattr(ret2[i], attr)

            self.__compare_resource_lists(ret[i].resources, ret2[i].resources)

    def test__list_releases__task_id(
        self, sandboxapi_instance, server, client_node_id, api_su_session, rest_su_session,
        task_manager, release_manager, releaser, monkeypatch, task_session, service_user, fake_agentr
    ):
        import sandbox.executor.commands.task
        reload(sandbox.executor.commands.task)
        monkeypatch.setattr(channel.channel.sandbox, 'server', api_su_session)
        monkeypatch.setattr(rest.Client, '__new__', classmethod(lambda *_, **__: rest_su_session))
        monkeypatch.delattr(rest.Client, '__init__')

        task = tests._create_task(
            task_manager,
            status=ctt.Status.SUCCESS,
        )
        res = tests._create_real_resource(
            task_manager,
            {'resource_type': 'TEST_TASK_RESOURCE'},
            task=task,
        )
        release_manager.release_task(task.id, releaser, status='stable', message_subject='subject')
        task.reload()
        task_session(rest_su_session, task.id)
        status, message = sandbox.executor.commands.task.ReleaseTask(
            task.id, 'log1',
            release_params=mapping.to_dict(task.release_params),
            agentr=fake_agentr(task)
        ).execute()
        assert status == ctt.Status.RELEASED
        task.set_status(status, message)

        ret = sandboxapi_instance.list_releases(task_id=task.id)
        assert isinstance(ret, list)
        assert isinstance(ret[0], sandboxapi.SandboxRelease)
        assert ret[0].task_id == task.id
        assert ret[0].resources[0].id == res.id

    ########################################
    # client
    ########################################

    def test__list_clients(self, sandboxapi_instance, client_manager):
        client = client_manager.create('test_client')
        ret = sandboxapi_instance.list_clients()
        assert isinstance(ret, list)
        assert isinstance(ret[0], dict)
        assert ret[0]['hostname'] == client.hostname


class TestTaskCreation(object):
    def create_task_by_xml_rpc(
        self,
        sandboxapi_instance,
        task_type,
        owner,
        description,
        parent_task_id=None,
        context=None,
        host=None,
        model=None,
        arch=None,
        priority=None,
        important=False,
        execution_space=None,
        parameters=None,
        enqueue=True
    ):
        owner = str(owner)
        if not context:
            context = {}
        description = str(description)
        task_parameters = {
            'type_name': task_type,
            'descr': description,
            'owner': owner,
            'ctx': context
        }
        if arch:
            task_parameters['arch'] = str(arch)
        if host:
            task_parameters['host'] = str(host)
        if model:
            task_parameters['model'] = str(model)
        if priority:
            task_parameters['priority'] = priority
        if parent_task_id:
            task_parameters['parent_id'] = sandboxapi_instance._to_id(parent_task_id)
        if important:
            task_parameters['important'] = True
        if execution_space is not None:
            task_parameters['execution_space'] = int(execution_space)
        if parameters:
            task_parameters.update(parameters)
        task_parameters['enqueue'] = False
        task_id = sandboxapi_instance.server.create_task(task_parameters)
        if enqueue:
            if not common_it.progressive_waiter(
                0.01, 5, 180, lambda: sandboxapi_instance.server.enqueue_task(task_id)
            )[0]:
                raise common_errors.TaskNotEnqueued("Task #{} is not enqueued".format(task_id))

        return sandboxapi_instance.get_task(task_id)

    def test__compare_skd_task_creation(
        self, sandboxapi_instance, api_session_login, task_manager, serviceq, task_session, rest_session, monkeypatch,
        resource_manager
    ):
        resource = mapping.Resource(
            type="SANDBOX_TASKS_ARCHIVE",
            name="test_resource",
            state=ctr.State.READY,
            path="test_path",
            task_id=6,
            owner="guest",
            arch="any",
            time=mapping.Resource.Time(),
        ).save()

        def recursive_dict_check(d1, d2, deep=0):
            assert type(d1) == type(d2)
            if isinstance(d1, dict):
                if deep != 0:
                    assert len(d1) == len(d2)
                for k, v in d1.iteritems():
                    if k in removed_context_fields:
                        continue
                    assert k in d2
                    recursive_dict_check(v, d2[k], deep + 1)
            elif isinstance(d1, list) or isinstance(d1, tuple):
                assert len(d1) == len(d2)
                for i in range(len(d1)):
                    recursive_dict_check(d1[i], d2[i], deep + 1)
            else:
                assert d1 == d2

        parameters = {
            "task_type": "TEST_TASK",
            "owner": api_session_login,
            "description": "new task",
            "context": {"GSID": "TEST:1", "copy_of": 35, "__sandbox_field": "test"},
            "host": "test_host",
            "model": "test_model",
            "arch": "osx",
            "priority": ("SERVICE", "LOW"),
            "important": True,
            "execution_space": 1000000,
            "parameters": {
                "tags": ["tag1"],
                "ram": 10000,
                "fail_on_any_error": True,
                "tasks_archive_resource": resource.id,
                "wait_on_enqueue": 10
            },
            "enqueue": False
        }
        removed_context_fields = {
            "inherit_notifications",
            "mark_as_urgent",
            "dict_of_strings_choices",
            "vault_item_expected",
            "email_recipient",
            "vault_item_owner",
            "notificationblock",
            "number_of_subtasks",
            "resourcesblock",
            "miscblock",
            "subtasksblock",
            "lifeblock",
            "subversionblock",
            "vault_item_name",
            "__GSID"
        }
        task1 = self.create_task_by_xml_rpc(
            sandboxapi_instance, **parameters
        )
        task2 = sandboxapi_instance.create_task(**parameters)
        recursive_dict_check(task1.ctx, task2.ctx)
        for field in ("model", "arch", "priority", "important", "owner"):
            assert getattr(task1, field) == getattr(task2, field)

        assert task1.model == task2.model

        model1 = mapping.Task.objects.with_id(task1.id)
        model2 = mapping.Task.objects.with_id(task2.id)
        assert model1.requirements.host == model2.requirements.host
        assert model1.author == model2.author
        assert model1.requirements.disk_space == model2.requirements.disk_space
        assert model1.requirements.ram == model2.requirements.ram
