# coding: utf-8

import json
import time
import httplib
import logging
import xmlrpclib

import pytest

from sandbox import common
import sandbox.common.types.task as ctt

from sandbox.yasandbox import controller
from sandbox.yasandbox.database import mapping
import sandbox.yasandbox.proxy.task as proxy_task
import sandbox.yasandbox.api.xmlrpc.tests as xmlrpc_tests

logger = logging.getLogger(__name__)


@pytest.mark.usefixtures("server")
class TestTask(xmlrpc_tests.TestXmlrpcBase):
    SERIALIZE_FIELDS = proxy_task.Task.SERIALIZE_FIELDS | {"type_name", "url", "client_tags"}

    def test__create_task__with_default_parameters__returns_created_task_id(self, api_session, task_manager):
        data = self.default_task_fields.copy()
        task_id = api_session.create_task(data)
        assert task_manager.exists(task_id)

    def test__create_task__with_parameters(self, api_session, task_manager):
        additional_params = [
            ('ram', 'required_ram', 42 << 10),
            ('execution_space', 'execution_space', 42 << 20),
            ('tags', 'tags', ['TAG1', 'TAG2']),
        ]
        data = self.default_task_fields.copy()
        for param_name, _, value in additional_params:
            data[param_name] = value
        task_id = api_session.create_task(data)
        task = task_manager.load(task_id)
        for _, attr_name, value in additional_params:
            assert getattr(task, attr_name) == value

    def test__create_task__with_empty_task_type__raises_Fault_exception(self, api_session):
        data = self.default_task_fields.copy()
        data['type_name'] = ''
        pytest.raises(xmlrpclib.Fault, api_session.create_task, data)

    def test__create_task__with_incorrect_task_type__raises_Fault_exception(self, api_session):
        data = self.default_task_fields.copy()
        data['type_name'] = 'INCORRECT_TASK_TYPE'
        pytest.raises(xmlrpclib.Fault, api_session.create_task, data)

    def test__create_task__returns_same_type(self, api_session, task_manager):
        data = self.default_task_fields.copy()
        data['type_name'] = 'UNIT_TEST'
        task_id = api_session.create_task(data)
        task = task_manager.load(task_id)
        assert task.type == 'UNIT_TEST'

    def test__create_task__with_freebsd_arch__returns_task_id_with_freebsd_arch(self, api_session, task_manager):
        data = self.default_task_fields.copy()
        data['type_name'] = 'UNIT_TEST'
        data['arch'] = 'freebsd'
        task_id = api_session.create_task(data)
        task = task_manager.load(task_id)
        assert task.arch == 'freebsd'

    def test__create_task__with_linux_arch__returns_task_id_with_linux_arch(self, api_session, task_manager):
        data = self.default_task_fields.copy()
        data['type_name'] = 'UNIT_TEST'
        data['arch'] = 'linux'
        task_id = api_session.create_task(data)
        task = task_manager.load(task_id)
        assert task.arch == 'linux'

    def test__create_task_saveCtx(self, api_session, task_manager):
        import projects.sandbox.test_task
        data = self.default_task_fields.copy()
        data['type_name'] = 'TEST_TASK'
        data['arch'] = 'linux'
        data['ctx'] = {'dependent_resource_id': 100}
        data['ctx'].update({k: 0 for k in projects.sandbox.test_task.TestTask.CTX_CUSTOM})
        data['enqueue'] = False
        task_id = api_session.create_task(data)
        task = task_manager.load(task_id)
        assert task.arch == 'linux'
        for k, v in data['ctx'].iteritems():
            assert task.ctx.get(k) == v

    def test__create_task__default_context(self, api_session, task_manager):
        data = self.default_task_fields.copy()
        data['type_name'] = 'TEST_TASK'
        task_id = api_session.create_task(data)
        task = task_manager.load(task_id)
        defaults = proxy_task.Task().get_default_parameters()
        defaults.update(task.CTX_REDEFINES)
        for k, v in defaults.iteritems():
            assert task.ctx[k] == v, 'Default: {}: {}, actual: {}'.format(k, v, task.ctx[k])
        assert task.ctx['dependent_resource_id'] is None
        for k, v in task.CTX_CUSTOM.iteritems():
            assert task.ctx[k] == v, 'Custom: {}: {}, actual: {}'.format(k, v, task.ctx[k])

    def _enqueue_task(self, tid, task_manager):
        assert common.utils.progressive_waiter(
            .01, 3, 15,
            lambda: not task_manager.still_in_status(tid, ctt.Status.DRAFT)
        )[0]
        from sandbox.services.modules import tasks_enqueuer
        tasks_enqueuer.TasksEnqueuer().tick()
        assert common.utils.progressive_waiter(
            .01, 3, 15,
            lambda: not task_manager.still_in_status(tid, ctt.Status.ENQUEUING)
        )[0]

    @pytest.mark.usefixtures('resource_manager', 'dummy_client')
    def test__create_task__dep_resources(self, api_session, task_manager):
        data = self.default_task_fields.copy()
        data['type_name'] = 'TEST_TASK'
        res_task_id = api_session.create_task(data)
        self._enqueue_task(res_task_id, task_manager)
        res_task = task_manager.load(res_task_id)
        resource_id = self.create_real_resource(task_manager, task=res_task).id
        data.setdefault('ctx', {})['dependent_resource_id'] = resource_id
        task_id = api_session.create_task(data)
        self._enqueue_task(task_id, task_manager)
        deps = task_manager.list_dependencies(task_id)
        assert deps[0][0] == res_task.id
        assert deps[0][1][0] == resource_id
        task = task_manager.load(task_id)
        assert task.status == task.Status.ENQUEUED

    @pytest.mark.usefixtures('dummy_client')
    def test__create_task__dep_resources_wait_deps(
        self, task_state_switcher, api_session, task_manager, resource_manager
    ):
        data = self.default_task_fields.copy()
        data['type_name'] = 'TEST_TASK'
        res_task_id = api_session.create_task(data)
        res_task = task_manager.load(res_task_id)
        resource_id = self.create_real_resource(task_manager, task=res_task, mark_ready=False).id
        # First of all, update task type to allowed hosts cache
        data.setdefault('ctx', {})['dependent_resource_id'] = resource_id
        task_id = api_session.create_task(data)
        self._enqueue_task(task_id, task_manager)
        deps = task_manager.list_dependencies(task_id)
        assert deps[0][0] == res_task.id
        assert deps[0][1][0] == resource_id
        task = task_manager.load(task_id)
        assert task.status == task.Status.WAIT_RES
        res = resource_manager.load(resource_id)
        res.mark_ready()

        task_state_switcher.tick()
        assert task_manager.load(task_id).status == task.Status.ENQUEUED

    @pytest.mark.usefixtures('server', 'dummy_client')
    def test__create_task__wait_time(
        self, api_su_session, api_su_session2, task_session, task_manager, api_session_login, task_state_switcher
    ):
        data = self.default_task_fields.copy()
        data['type_name'] = 'TEST_TASK'
        data['owner'] = api_session_login
        task_id = api_su_session.create_task(data)
        self._enqueue_task(task_id, task_manager)
        task = task_manager.load(task_id)
        assert task.status == task.Status.ENQUEUED, task_id

        WAIT_TIMEOUT = 1

        token1 = task_session(api_su_session, task_id)
        # Can't create another session for this task
        with pytest.raises(mapping.NotUniqueError) as ex:
            task_session(api_su_session2, task_id)
        assert "task_id" in str(ex.value)

        # Call twice to ensure trigger is re-created
        for _ in range(2):
            api_su_session.wait_time(task_id, WAIT_TIMEOUT)

        # Drop the first session and re-create trigger with another
        mapping.OAuthCache.objects(token=token1).delete()

        with pytest.raises(xmlrpclib.ProtocolError) as ex:
            api_su_session.wait_time(task_id, WAIT_TIMEOUT)
        assert ex.value.errcode == httplib.FORBIDDEN

        token2 = task_session(api_su_session2, task_id)
        api_su_session2.wait_time(task_id, WAIT_TIMEOUT)
        mapping.OAuthCache.objects(token=token2).delete()

        task.set_status(task.Status.WAIT_TIME, force=True)
        mapping.TimeTrigger.objects(source=task_id).update(set__activated=True)

        task = task_manager.load(task_id)
        assert task.status == task.Status.WAIT_TIME
        time.sleep(WAIT_TIMEOUT)
        task_state_switcher.tick()
        task = task_manager.load(task_id)
        assert task.status == task.Status.ENQUEUED

    @pytest.mark.usefixtures('server', 'dummy_client')
    def test__create_task__wait_all_tasks(
        self, api_su_session, api_su_session2, task_session, task_manager, api_session_login, task_state_switcher
    ):
        data = self.default_task_fields.copy()
        data['type_name'] = 'TEST_TASK'
        data['owner'] = api_session_login
        task_id = api_su_session.create_task(data)
        self._enqueue_task(task_id, task_manager)
        task = task_manager.load(task_id)
        assert task.status == task.Status.ENQUEUED, task_id
        subtask1_id = api_su_session.create_task(data)
        self._enqueue_task(subtask1_id, task_manager)
        subtask1 = task_manager.load(subtask1_id)
        assert subtask1.status == task.Status.ENQUEUED
        subtask2_id = api_su_session.create_task(data)
        self._enqueue_task(subtask2_id, task_manager)
        subtask2 = task_manager.load(subtask2_id)
        assert subtask2.status == task.Status.ENQUEUED

        token1 = task_session(api_su_session, task_id)
        # Can't create another session for this task
        with pytest.raises(mapping.NotUniqueError) as ex:
            task_session(api_su_session2, task_id)
        assert "task_id" in str(ex.value)

        # Call twice to ensure trigger is re-created
        for _ in xrange(2):
            api_su_session.wait_tasks(
                task_id, [subtask1_id, subtask2_id], [task.Status.SUCCESS, task.Status.FAILURE], True
            )

        # Drop the first session and re-create trigger with another
        mapping.OAuthCache.objects(token=token1).delete()
        task_session(api_su_session2, task_id)
        api_su_session2.wait_tasks(
            task_id, [subtask1_id, subtask2_id], [task.Status.SUCCESS, task.Status.FAILURE], True
        )
        task.set_status(task.Status.WAIT_TASK, force=True)

        task = task_manager.load(task_id)
        assert task.status == task.Status.WAIT_TASK
        subtask1.set_status(task.Status.SUCCESS, force=True)
        task_state_switcher.tick()

        task = task_manager.load(task_id)
        assert task.status == task.Status.WAIT_TASK
        subtask2.set_status(task.Status.FAILURE, force=True)
        task_state_switcher.tick()
        task = task_manager.load(task_id)
        assert task.status == task.Status.ENQUEUED

    @pytest.mark.usefixtures('server', 'dummy_client')
    def test__create_task__wait_any_tasks(
        self, api_su_session, task_manager, api_su_session_login, task_state_switcher
    ):
        data = self.default_task_fields.copy()
        data['type_name'] = 'TEST_TASK'
        data['owner'] = api_su_session_login
        task_id = api_su_session.create_task(data)
        self._enqueue_task(task_id, task_manager)
        task = task_manager.load(task_id)
        assert task.status == task.Status.ENQUEUED
        subtask1_id = api_su_session.create_task(data)
        self._enqueue_task(subtask1_id, task_manager)
        subtask1 = task_manager.load(subtask1_id)
        assert subtask1.status == task.Status.ENQUEUED
        subtask2_id = api_su_session.create_task(data)
        self._enqueue_task(subtask2_id, task_manager)
        subtask2 = task_manager.load(subtask2_id)
        assert subtask2.status == task.Status.ENQUEUED

        api_su_session.wait_tasks(
            task_id, [subtask1_id, subtask2_id], [task.Status.SUCCESS, task.Status.FAILURE], False
        )
        task.set_status(task.Status.WAIT_TASK, force=True)

        task = task_manager.load(task_id)
        assert task.status == task.Status.WAIT_TASK
        subtask1.set_status(task.Status.SUCCESS, force=True)
        task_state_switcher.tick()
        task = task_manager.load(task_id)
        assert task.status == task.Status.ENQUEUED

        with pytest.raises(xmlrpclib.Fault) as ex:
            api_su_session.wait_tasks(
                task_id, [subtask1_id, subtask2_id], [task.Status.SUCCESS, task.Status.FAILURE], False
            )
        assert common.errors.NothingToWait.__name__ in str(ex.value)

        api_su_session.wait_tasks(
            task_id, [subtask2_id], [task.Status.SUCCESS, task.Status.FAILURE], False
        )
        task.set_status(task.Status.WAIT_TASK, force=True)

        task = task_manager.load(task_id)
        assert task.status == task.Status.WAIT_TASK
        subtask2.set_status(task.Status.FAILURE, force=True)
        task_state_switcher.tick()
        task = task_manager.load(task_id)
        assert task.status == task.Status.ENQUEUED

    def test__create_task__anonimous_user(self, anonymous_session, task_manager):
        data = self.default_task_fields.copy()
        data['priority'] = ('SERVICE', 'NORMAL')
        del data['owner']
        task_id = anonymous_session.create_task(data)
        #
        task = task_manager.load(task_id)
        assert task.author == controller.User.anonymous.login
        assert task.priority == task.Priority(
            task.Priority.Class.BACKGROUND,
            task.Priority.Subclass.LOW)

    def test__audit_of_create_task(self, api_session, task_manager):
        data = self.default_task_fields.copy()
        task_id = api_session.create_task(data)
        history = task_manager.get_history(task_id=task_id)
        first_note = history[0]
        assert first_note["status"] == ctt.Status.DRAFT
        assert first_note["event"] == "Created"
        assert first_note["request_id"] is not None
        assert first_note["remote_ip"] is not None

    def test__get_task__with_correct_task_id__returns_dict(self, api_session, task_manager):
        task = self.create_task(task_manager)
        getted_task = api_session.get_task(task.id)
        assert isinstance(getted_task, dict)
        getted_task = api_session.get_task(str(task.id))
        assert isinstance(getted_task, dict)

    def test__get_task__with_correct_task_id__all_fields_are_presented_in_the_returned_dict(
        self, api_session, task_manager
    ):
        task = self.create_task(task_manager)
        getted_task = api_session.get_task(task.id)
        assert set(self.SERIALIZE_FIELDS) == set(getted_task)

    def test__get_task__with_incorrect_id__returns_empty_dict(self, api_session):
        assert api_session.get_task('abcdefefacbdedabdfacedef') == {}

    def test__get_task__with_absent_task_id__returns_empty_dict(self, api_session):
        assert api_session.get_task(1234567890) == {}

    def test__get_task__with_incorrect_xml_symbol(self, api_session, task_manager):
        ctx = [("incorrect_symbol", u"broken ctx value \f"), ("cyrillic", u"слово русское")]
        info = u"another broken value \f словечко"
        task = self.create_task(task_manager, parameters={"ctx": dict(ctx)})
        task.set_info(info)
        task_manager.update(task)
        ret = api_session.get_task(task.id)
        assert isinstance(ret["ctx"], str)
        ret["ctx"] = json.loads(ret["ctx"])
        assert ret["info"].strip().endswith(info.replace("\f", "?"))
        for key, value in ctx:
            assert ret["ctx"][key] == value

    def test__get_task_status__for_just_created_task_via_manager__returns_NOT_READY(self, api_session, task_manager):
        expected_status = ctt.Status.DRAFT
        task = self.create_task(task_manager)
        real_status = api_session.get_task_status(task.id)
        assert expected_status == real_status

    @pytest.mark.usefixtures('dummy_client')
    def test__get_task_status__for_just_created_task_via_xmlrpc__returns_ENQUEUING(self, api_session, task_manager):
        data = self.default_task_fields.copy()

        import datetime as dt
        print dt.datetime.now()
        task_id = api_session.create_task(data)
        assert common.utils.progressive_waiter(
            .01, 3, 15,
            lambda: not task_manager.still_in_status(task_id, ctt.Status.DRAFT)
        )[0]
        from sandbox.services.modules import tasks_enqueuer
        tasks_enqueuer.TasksEnqueuer().tick()
        assert common.utils.progressive_waiter(
            .01, 3, 15,
            lambda: not task_manager.still_in_status(task_id, ctt.Status.ENQUEUING)
        )[0]
        real_status = api_session.get_task_status(task_id)
        assert real_status == ctt.Status.ENQUEUED, task_id

    def test__get_task_status__with_not_existent_task_id_12312132__returns_False(self, api_session):
        assert not api_session.get_task_status('18901234')

    def test__get_task_status__with_incorrect_task_id__returns_False(self, api_session):
        assert not api_session.get_task_status('abcdefefacbdedabdfacedef')

    def test__list_task_types__returns_list(self, api_session):
        task_types_list = api_session.list_task_types()
        assert isinstance(task_types_list, list)

    def test__list_task_types__returns_non_empty_list(self, api_session):
        task_types_list = api_session.list_task_types()
        assert len(task_types_list) > 0

    def test__bulk_task_fields__1(self, api_session, task_manager):
        ''' Check that bulk_task_fields return correct dict '''
        task = self.create_task(task_manager)
        task.ctx['foo'] = 'bar'
        task.ctx["dict"] = {"nested": "dict"}
        task.set_info("olol")
        task_manager.update(task)
        d = api_session.bulk_task_fields([task.id], ["ctx", "info", "timestamp", "updated"])[str(task.id)]
        assert isinstance(d[0], dict)
        assert isinstance(d[0]["dict"], dict)
        assert 'foo' in d[0]
        assert d[1].endswith("olol\n")
        # 'timestamp' and 'updated' values may be different when are initialized by default values on server side,
        # such difference may not be greater than 1.
        assert abs(d[2] - d[3]) < 2

    def test__bulk_task_fields__2(self, api_session):
        ''' Check for strict_mode = True '''
        pytest.raises(xmlrpclib.Fault, api_session.bulk_task_fields, [-1], ["ctx"], True)

    def test__set_task_priority__user(
        self, task_manager, api_session, api_session_group
    ):
        task = self.create_task(task_manager, owner=api_session_group)

        ret = api_session.get_task(task.id)
        assert ret['priority'] == ['BACKGROUND', 'LOW']

        api_session.set_task_priority(task.id, ('BACKGROUND', 'HIGH'))
        ret = api_session.get_task(task.id)
        assert ret['priority'] == ['BACKGROUND', 'HIGH']

        api_session.set_task_priority(task.id, ('SERVICE', 'NORMAL'))
        ret = api_session.get_task(task.id)
        assert ret['priority'] == ['SERVICE', 'NORMAL']

        pytest.raises(xmlrpclib.Fault, api_session.set_task_priority, task.id, ('USER', 'LOW'))

    def test__set_task_priority__super_user(self, api_session, api_su_session, task_manager, api_su_session_group):
        task = self.create_task(task_manager, owner=api_su_session_group)

        ret = api_su_session.get_task(task.id)
        assert ret['priority'] == ['BACKGROUND', 'LOW']

        api_su_session.set_task_priority(task.id, ('USER', 'HIGH'))
        ret = api_su_session.get_task(task.id)
        assert ret['priority'] == ['USER', 'HIGH']

    def test__set_task_priority__trusted_user(self, api_trusted_session, task_manager, api_trusted_session_group):
        task = self.create_task(task_manager, owner=api_trusted_session_group)

        ret = api_trusted_session.get_task(task.id)
        assert ret['priority'] == ['BACKGROUND', 'LOW']

        api_trusted_session.set_task_priority(task.id, ('SERVICE', 'HIGH'))
        ret = api_trusted_session.get_task(task.id)
        assert ret['priority'] == ['SERVICE', 'HIGH']

        pytest.raises(xmlrpclib.Fault, api_trusted_session.set_task_priority, task.id, ('USER', 'HIGH'))

    def test__set_task_priority__not_allowed(self, api_session, task_manager):
        task = self.create_task(task_manager)
        pytest.raises(xmlrpclib.Fault, api_session.set_task_priority, task.id, ('BACKGROUND', 'LOW'))

    def test__restart_task(self, api_session, task_manager, api_session_login):
        task = self.create_task(
            task_manager, author=api_session_login, parameters={"status": ctt.Status.TEMPORARY}
        )
        assert api_session.restart_task(task.id)
        assert not api_session.restart_task(task.id)

    def test__restart_task__not_allowed(self, api_session, task_manager):
        task = self.create_task(task_manager)
        pytest.raises(xmlrpclib.Fault, api_session.restart_task, task.id)

    def test__cancel_task(self, api_session, task_manager, api_session_login):
        task = self.create_task(
            task_manager, author=api_session_login, parameters={"status": ctt.Status.TEMPORARY}
        )
        api_session.cancel_task(task.id)

    def test__cancel_task__not_allowed(self, api_session, task_manager):
        task = self.create_task(task_manager)
        pytest.raises(xmlrpclib.Fault, api_session.cancel_task, task.id)
