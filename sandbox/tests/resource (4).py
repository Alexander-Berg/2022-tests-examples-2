import time
import datetime as dt
import xmlrpclib

import pytest

from sandbox import common
from sandbox.yasandbox.database import mapping
from sandbox.yasandbox.manager import tests as manager_tests
from sandbox.yasandbox.api.xmlrpc import tests as xmlrpc_tests


@pytest.mark.usefixtures("server")
class TestResource(xmlrpc_tests.TestXmlrpcBase):
    def test__get_resource__with_absent_resource_id__returns_false(self, api_session):
        absent_resource = api_session.get_resource(507439011)
        assert absent_resource is False

    def test__get_resource__with_incorrect_id__exception_occurs(self, api_session):
        pytest.raises(xmlrpclib.Fault, api_session.get_resource, 'sdf')

    def test__last_resources(self, api_session, task_manager, resource_manager):
        resources = [
            self.create_resource(task_manager, dict(resource_type='TEST_TASK_RESOURCE')),
            self.create_resource(task_manager, dict(resource_type='TEST_TASK_RESOURCE')),
            self.create_resource(task_manager, dict(resource_type='TEST_TASK_RESOURCE_2')),
            self.create_resource(task_manager, dict(resource_type='TEST_TASK_RESOURCE_2')),
            self.create_resource(task_manager, dict(resource_type='TEST_TASK_RESOURCE_2'), mark_ready=False),
        ]

        resp = api_session.last_resources(('TEST_TASK_RESOURCE', 'TEST_TASK_RESOURCE_2'))
        assert len(resp) == 2
        assert resp[0]['id'] == resources[1].id
        assert resp[1]['id'] == resources[3].id

        resp = api_session.last_resources(('TEST_TASK_RESOURCE', 'TEST_TASK_RESOURCE_2'), None)
        assert len(resp) == 2
        assert resp[0]['id'] == resources[1].id
        assert resp[1]['id'] == resources[-1].id

    def test__last_resources_wrong_parameters(self, api_session, task_manager):
        with pytest.raises(xmlrpclib.Fault):
            api_session.last_resources([])

    def test__get_resource__with_fake_resource_id__returns_dict(self, api_session, task_manager):
        resource_id = self.create_resource(task_manager).id
        resource = api_session.get_resource(resource_id)
        assert isinstance(resource, dict)

    def test__get_resource__with_fake_resource_id__returned_id_is_correct(self, api_session, task_manager):
        resource_id = self.create_resource(task_manager).id
        resource = api_session.get_resource(resource_id)
        assert resource['id'] == resource_id

    def test__get_resource__with_fake_resource_id__all_fields_are_presented_in_the_returned_dict(
        self, api_session, task_manager
    ):
        resource_id = self.create_resource(task_manager).id
        resource = api_session.get_resource(resource_id)
        for key in xmlrpc_tests.RESOURCE_KEYS:
            assert key in resource

    def test__list_resources__attrs(self, api_session, task_manager):
        resource_1 = self.create_resource(
            task_manager,
            parameters={'attrs': {'attr_1': 'param_1', 'attr_2': 'param_2'}}
        )
        resource_2 = self.create_resource(
            task_manager,
            parameters={'attrs': {'attr_1': 'param_1', 'attr_3': 'param_3'}}
        )
        #
        ress = api_session.list_resources({
            'resource_type': 'TEST_TASK_RESOURCE', 'attr_name': 'attr_3',
        })
        assert ress[0]['id'] == resource_2.id
        #
        ress = api_session.list_resources({
            'resource_type': 'TEST_TASK_RESOURCE', 'attr_value': 'param_2',
        })
        assert ress[0]['id'] == resource_1.id
        #
        ress = api_session.list_resources({
            'resource_type': 'TEST_TASK_RESOURCE', 'any_attrs': {'attr_1': ''},
        })
        assert ress[0]['id'] == resource_2.id
        assert ress[1]['id'] == resource_1.id
        #
        ress = api_session.list_resources({
            'resource_type': 'TEST_TASK_RESOURCE', 'any_attrs': {'': 'param_1'},
        })
        assert ress[0]['id'] == resource_2.id
        assert ress[1]['id'] == resource_1.id
        #
        ress = api_session.list_resources({
            'resource_type': 'TEST_TASK_RESOURCE', 'any_attrs': {'attr_1': '', 'attr_2': ''},
        })
        assert ress[0]['id'] == resource_2.id
        assert ress[1]['id'] == resource_1.id
        #
        ress = api_session.list_resources({
            'resource_type': 'TEST_TASK_RESOURCE', 'all_attrs': {'attr_1': '', 'attr_2': ''},
        })
        assert ress[0]['id'] == resource_1.id

    def test__bulk_resource_fields(self, api_session, task_manager):
        resources = manager_tests._create_resources(task_manager, 10)
        res_ids = map(lambda r: str(r.id), resources)
        ret = api_session.bulk_resource_fields(res_ids, ['type', 'owner'])
        assert len(ret) == len(resources)
        assert set(ret.keys()) == set(res_ids)
        assert ret[str(resources[-1].id)][0] == str(resources[-1].type)
        assert ret[str(resources[0].id)][1] == resources[0].owner
        assert ret[str(resources[-1].id)][1] == resources[-1].owner

    def test__list_resource_types__returns_list(self, api_session):
        resource_types_list = api_session.list_resource_types()
        assert isinstance(resource_types_list, list)

    def test__list_resource_types__returns_nonempty_list(self, api_session):
        resource_types_list = api_session.list_resource_types()
        assert len(resource_types_list) > 0

    def test__get_resource__attr__with_exist_resource_name__returns_attrubutes_value(
        self, api_session, task_manager, resource_manager
    ):
        resource = self.create_resource(task_manager)
        resource.attrs = {'attr1': 3, 'attr2': 'test'}
        resource_manager.update(resource)
        assert str(api_session.get_resource(resource.id)['attrs']['attr1']) == str(3)
        assert str(api_session.get_resource(resource.id)['attrs']['attr2']) == str('test')

    def test__get_resource__attr__with_absent_resource_name__returns_empty_string(
        self, api_session, task_manager, resource_manager
    ):
        resource = self.create_resource(task_manager)
        resource.attrs = {'attr1': 3, 'attr2': 'test'}
        resource_manager.update(resource)
        assert not api_session.get_resource(resource.id)['attrs'].get('sdfdsf')

    def test__get_resource__attr__with_incorrect_resource_name__returns_empty_string(
        self, api_session, task_manager, resource_manager
    ):
        resource = self.create_resource(task_manager)
        resource.attrs = {'attr1': 3, 'attr2': 'test'}
        resource_manager.update(resource)
        assert not api_session.get_resource(resource.id)['attrs'].get('attr')

    def test__set_resource_attr__sets_exists_attribute_value(
        self, api_session, task_manager, resource_manager, api_session_login
    ):
        task = self.create_task(task_manager, owner=api_session_login)
        resource = self.create_resource(task_manager, task=task)
        resource.attrs = {'attr1': 3, 'attr2': 'test'}
        resource_manager.update(resource)
        assert api_session.get_resource(resource.id)['attrs'].get('attr1') == "3"
        api_session.set_resource_attr(resource.id, 'attr1', 'another_value')
        assert api_session.get_resource(resource.id)['attrs'].get('attr1') == 'another_value'

    def test__set_resource_attr__sets_new_attribute_value__returns_True(
        self, api_session, task_manager, resource_manager, api_session_login
    ):
        task = self.create_task(task_manager, owner=api_session_login)
        resource = self.create_resource(task_manager, task=task)
        resource.attrs = {'attr1': 3, 'attr2': 'test'}
        resource_manager.update(resource)
        assert not api_session.get_resource(resource.id)['attrs'].get('attr_new')
        api_session.set_resource_attr(resource.id, 'attr_new', 'another_value')
        assert api_session.get_resource(resource.id)['attrs'].get('attr_new') == 'another_value'

    def test__set_resource_attr__with_absent_resource_id(self, api_session):
        pytest.raises(xmlrpclib.Fault, api_session.set_resource_attr, 507439011, 'attr_new', 'another_value')

    def test__set_resource_attr__not_allowed(self, api_session, task_manager):
        task = self.create_task(task_manager)
        resource = self.create_resource(task_manager, task=task)
        #
        pytest.raises(xmlrpclib.Fault, api_session.set_resource_attr, resource.id, 'foo', 'boo')

    def test__drop_resource_attr(
        self, api_session, task_manager, resource_manager, api_session_login
    ):
        task = self.create_task(task_manager, owner=api_session_login)
        resource = self.create_resource(
            task_manager, task=task, parameters={'attrs': {'foo': 'boo'}})
        #
        assert api_session.get_resource(resource.id)['attrs'].get('foo') == 'boo'
        api_session.drop_resource_attr(resource.id, 'foo')
        assert not api_session.get_resource(resource.id)['attrs'].get('foo')

    def test__drop_resource_attr__not_allowed(self, api_session, task_manager):
        task = self.create_task(task_manager)
        resource = self.create_resource(
            task_manager, task=task, parameters={'attrs': {'foo': 'boo'}})
        #
        pytest.raises(xmlrpclib.Fault, api_session.drop_resource_attr, resource.id, 'foo')

    def test__drop_resource_attr__with_absent_resource_id__returns_False(self, api_session):
        pytest.raises(xmlrpclib.Fault, api_session.drop_resource_attr, 507439011, 'attr_new')

    def test__touch_resource__1(self, api_session, task_manager, resource_manager):
        resource = self.create_resource(task_manager)
        creation_time = dt.datetime.utcnow() - dt.timedelta(
            seconds=common.config.Registry().common.resources.touch_delay * 3
        )
        mapping.Resource.objects(id=resource.id).update(time__accessed=creation_time, time__created=creation_time)

        before_touch = time.time() - common.config.Registry().common.resources.touch_delay
        api_session.touch_resource(resource.id)
        resource = resource_manager.load(resource.id)
        assert time.mktime(creation_time.timetuple()) < before_touch < resource.last_usage_time

    def test__touch_resource__2(self, api_session):
        with pytest.raises(xmlrpclib.Fault):
            api_session.touch_resource(0)

    def test__touch_resource__3(self, api_session, task_manager, resource_manager):
        resource = self.create_resource(task_manager, mark_ready=False)
        for host in resource_manager.get_hosts(resource.id):
            resource_manager.remove_host(resource.id, host)
        resource_manager.delete_resource(resource.id)
        with pytest.raises(xmlrpclib.Fault):
            api_session.touch_resource(resource.id)

    def test__create_resource(self, api_session, api_su_session, task_manager, resource_manager):
        task = self.create_task(task_manager)
        res_id = api_su_session.create_resource({
            'task_id': task.id,
            'descr': 'new resource',
            'name': 'resource name',
            'type': 'TEST_TASK_RESOURCE',
            'arch': task.arch,
            'attrs': {'key_1': 'value_2'},
        })
        resource = resource_manager.load(res_id)
        assert resource.task_id == task.id
        assert str(resource.type) == 'TEST_TASK_RESOURCE'
        assert resource.arch == task.arch
        assert resource.owner == task.owner
        assert resource.attrs['key_1'] == 'value_2'
