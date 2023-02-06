# coding: utf-8
import urllib
import datetime as dt

import pytest
from . import (
    _create_task,
    _create_client,
    _create_resources,
    _create_fake_resource,
    _create_real_resource,
    _create_task_with_resources,
    _get_current_host_name,
)

from sandbox.common import errors
import sandbox.common.types.client as ctc
import sandbox.common.types.task as ctt
import sandbox.common.types.resource as ctr

from sandbox.yasandbox import controller
from sandbox.yasandbox.database import mapping

import os
import time
import stat
import urlparse


class TestResourceClass:
    """
        Unit tests for Resource class.
        Checking all major functions; creating, deleting resource objects, etc.
    """
    def test__is_dummy__returns_false_for_default_resource(self, resource_manager):
        assert not _create_fake_resource().is_dummy()

    def test__is_dummy__returns_false_for_not_dummy_resource(self, resource_manager):
        assert not _create_fake_resource({'dummy': False}).is_dummy()

    def test__is_dummy__returns_true_for_dummy_resource(self, resource_manager):
        assert _create_fake_resource({'dummy': True}).is_dummy()

    def test__abs_path__returns_absolute_path(self, resource_manager):
        derived_path = _create_fake_resource().abs_path()
        assert os.path.isabs(derived_path)

    def test__abs_path__returns_correct_path_by_id(self, resource_manager, tasks_dir):
        derived_path = _create_fake_resource({'task_id': 143860}).abs_path()
        expected_path = os.path.join(tasks_dir, '0', '6', '143860', 'resource')
        assert derived_path == expected_path

    def test__local_path__returns_local_path(self, resource_manager):
        derived_path = _create_fake_resource().local_path()
        assert not os.path.isabs(derived_path)

    def test__local_path__returns_correct_path_by_id(self, resource_manager):
        derived_path = _create_fake_resource({'task_id': 355241}).local_path()
        expected_path = os.path.join('1', '4', '355241', 'resource')
        assert derived_path == expected_path

    def test__task_path__returns_correct_task_path(self, resource_manager, tasks_dir):
        derived_path = _create_fake_resource({'task_id': 165382}).task_path()
        expected_path = os.path.join(tasks_dir, '2', '8', '165382')
        assert derived_path == expected_path

    def test__basename__returns_resource_for_default_resource(self, resource_manager):
        name = _create_fake_resource().basename()
        assert name == 'resource'

    def test__basename__returns_correct_name_for_custom_resource_name(self, resource_manager):
        name = _create_fake_resource({'file_name': 'ewwww.txt'}).basename()
        assert name == 'ewwww.txt'

    def test__get_host__returns_correct_hostname(self, client_manager, resource_manager, task_manager, client_node_id):
        _create_client(client_manager, client_node_id)
        resource = _create_real_resource(task_manager)
        assert resource.get_host() == client_node_id

    def test__md5sum__returns_correct_value_for_an_empty_file(self, resource_manager, task_manager):
        resource = _create_real_resource(task_manager)
        # compare with md5sum for an empty file
        assert 'd41d8cd98f00b204e9800998ecf8427e' == resource.md5sum()

    def test__is_ready__returns_true_if_resource_state_is_state_READY(self, resource_manager):
        resource = _create_fake_resource()
        resource.state = mapping.Resource.State.READY
        assert resource.is_ready()

    def test__is_ready__returns_false_if_resource_state_is_state_NOT_READY(self, resource_manager):
        resource = _create_fake_resource()
        resource.state = mapping.Resource.State.NOT_READY
        assert not resource.is_ready()

    def test__is_ready__returns_false_if_resource_state_is_state_BROKEN(self, resource_manager):
        resource = _create_fake_resource()
        resource.state = mapping.Resource.State.BROKEN
        assert not resource.is_ready()

    def test__is_ready__returns_false_if_resource_state_is_state_DELETED(self, resource_manager):
        resource = _create_fake_resource()
        resource.state = mapping.Resource.State.DELETED
        assert not resource.is_ready()

    def test__user_has_permission__with_superuser__returns_True(self, resource_manager, user_controller):
        user = user_controller.create(mapping.User(login='test_user', super_user=True))
        assert _create_fake_resource().user_has_permission(user.login)

    def test__user_has_permission__with_user__returns_False(self, resource_manager, user_controller):
        user = user_controller.create(mapping.User(login='test_user'))
        assert not _create_fake_resource().user_has_permission(user.login)

    def test__remote_path__returns_correct_remote_path(self, resource_manager, task_manager, tasks_dir):
        resource = _create_real_resource(task_manager)
        remote_path = resource.remote_path()
        local_path = resource.local_path()
        assert remote_path == os.path.join(tasks_dir, local_path)

    def test__remote_path__with_localhost_hostname__returns_correct_remote_path_for_localhost_hostname(
        self,
        resource_manager,
        task_manager,
        tasks_dir
    ):
        resource = _create_real_resource(task_manager)
        remote_path = resource.remote_path()
        local_path = resource.local_path()
        assert remote_path == os.path.join(tasks_dir, local_path)

    def test__remote_dirname__returns_correct_remote_dirname(self, resource_manager, task_manager, tasks_dir):
        resource = _create_real_resource(task_manager)
        remote_path = resource.remote_dirname()
        local_path = os.path.dirname(resource.local_path())
        assert remote_path == os.path.join(tasks_dir, local_path)

    @pytest.mark.parametrize("new_layout", [False, True])
    def test__http_url__returns_correct_path_to_a_resource(
        self, request, client, resource_manager, task_manager, new_layout
    ):
        do_cleanup = new_layout and ctc.Tag.NEW_LAYOUT not in client.tags
        if new_layout:
            client.update_tags([ctc.Tag.NEW_LAYOUT], client.TagsOp.ADD)

        def rollback():
            if do_cleanup:
                client.update_tags([ctc.Tag.NEW_LAYOUT], client.TagsOp.REMOVE)

        request.addfinalizer(rollback)

        task = _create_task(task_manager)
        internal_path, filename = "a b c/d e f", "ghi.txt"
        resource = _create_fake_resource({
            "file_name": os.path.join(internal_path, filename),
            "task_id": task.id
        })

        fileserver = client.get("system", {}).get("fileserver", "")

        if new_layout:
            resname = urllib.quote(filename)
            expected = os.path.join(fileserver, "resource", str(resource.id), resname)
        else:
            resname = urllib.quote(os.path.join(internal_path, filename))
            expected = os.path.join(fileserver, *(ctt.relpath(resource.task_id) + [resname]))
        assert resource.http_url(client) == expected
        assert " " not in resource.http_url(client)

    @pytest.mark.parametrize("new_layout", [False, True])
    def test__rsync_url__returns_correct_path_to_a_resource(
        self, request, client, resource_manager, task_manager, new_layout
    ):
        do_cleanup = new_layout and ctc.Tag.NEW_LAYOUT not in client.tags
        if new_layout:
            client.update_tags([ctc.Tag.NEW_LAYOUT], client.TagsOp.ADD)

        def rollback():
            if do_cleanup:
                client.update_tags([ctc.Tag.NEW_LAYOUT], client.TagsOp.REMOVE)

        request.addfinalizer(rollback)

        resource = _create_real_resource(task_manager)
        fileserver = client.get("system", {}).get("fileserver", "")
        resname = os.path.basename(resource.file_name)

        parsed = urlparse.urlparse(fileserver)
        rsync_base = parsed._replace(scheme="rsync", netloc=parsed.netloc.split(":")[0]).geturl()
        if new_layout:
            expected = os.path.join(rsync_base, "sandbox-resources", *(ctr.relpath(resource.id) + (resname, )))
        else:
            expected = os.path.join(rsync_base, "sandbox-tasks", *(ctt.relpath(resource.task_id) + [resname]))
        assert resource.rsync_url(client) == expected

    def test__local_dirname__returns_correct_path_by_id(self, resource_manager):
        getted_path = _create_fake_resource({'task_id': 358271}).local_dirname()
        expected_path = os.path.join('1', '7', '358271')
        assert getted_path == expected_path

    def test__abs_dirname__returns_absolute_path(self, resource_manager):
        getted_path = _create_fake_resource().abs_dirname()
        assert os.path.isabs(getted_path)

    def test__abs_dirname__returns_correct_path_by_id(self, resource_manager, tasks_dir):
        getted_path = _create_fake_resource({'task_id': 143725}).abs_dirname()
        expected_path = os.path.join(tasks_dir, '5', '2', '143725')
        assert getted_path == expected_path

    def test__title__returns_not_empty_string(self, resource_manager):
        resource = _create_fake_resource()
        assert isinstance(resource.title(), unicode)
        assert resource.title() != ''

    def test__formatted_time__returns_correct_time(self, resource_manager):
        resource = _create_fake_resource()
        expected_time_value = dt.datetime.now().strftime("%d-%m-%Y %H:%M")
        assert resource.formatted_time() == expected_time_value

    def test__is_local_available__returns_false_if_resource_file_does_not_exist(self, resource_manager):
        pytest.skip('Function Resource.is_local_available is removed.')
        fake_resource = _create_fake_resource({'task_id': 2432425111})
        assert not fake_resource.is_local_available()

    def test__is_local_available__returns_false_true_if_md5_checksum_is_incorrect(self, resource_manager,
                                                                                  task_manager):
        pytest.skip('Function Resource.is_local_available is removed.')
        real_resource = _create_real_resource(task_manager)
        with open(real_resource.abs_path(), 'w') as real_resource_file:
            real_resource_file.write('test test test')
        assert not real_resource.is_local_available()

    def test__is_local_available__returns_true_if_resource_file_exists(self, resource_manager, task_manager):
        pytest.skip('Function Resource.is_local_available is removed.')
        real_resource = _create_real_resource(task_manager)
        assert real_resource.is_local_available()

    def test__mark_host_to_delete__check_that_current_host_is_not_presented_in_get_hosts_list(self, resource_manager,
                                                                                              task_manager,
                                                                                              client_node_id):
        real_resource = _create_real_resource(task_manager)
        current_hostname = client_node_id
        real_resource.add_host()
        assert current_hostname in real_resource.get_hosts()
        real_resource.touch()
        assert current_hostname in real_resource.get_hosts()
        resource_manager.mark_host_to_delete(real_resource.id, current_hostname)
        assert current_hostname not in real_resource.get_hosts()
        real_resource.touch()
        assert current_hostname not in real_resource.get_hosts()
        assert current_hostname in real_resource.get_hosts(True)

    def test__mark_ready__raises_exception_if_resource_does_not_exist(self, resource_manager):
        fake_resource = _create_fake_resource({'task_id': 24325111})
        pytest.raises(Exception, fake_resource.mark_ready)

    def test__mark_ready__changed_time_was_set_correctly(self, resource_manager, task_manager):
        pytest.skip('Flash in the sky')
        real_resource = _create_real_resource(task_manager, mark_ready=False)
        real_resource.timestamp = 0
        real_resource.mark_ready()
        expected_time_value = dt.datetime.now().strftime("%d-%m-%Y %H:%M")
        assert real_resource.formatted_time() == expected_time_value

    def test__mark_broken__resource_state_is_state_BROKEN(self, resource_manager, task_manager):
        real_resource = _create_real_resource(task_manager)
        time_before = time.time()
        real_resource.mark_broken()
        time_after = time.time()
        assert time_before <= real_resource.last_updated_time <= time_after
        assert real_resource.state == mapping.Resource.State.BROKEN

    def test__mark_ready__resource_state_is_state_READY(self, resource_manager, task_manager):
        real_resource = _create_real_resource(task_manager, mark_ready=False)
        assert real_resource.state != mapping.Resource.State.READY
        time_before = time.time()
        real_resource.mark_ready()
        time_after = time.time()
        assert time_before <= real_resource.last_updated_time <= time_after
        assert real_resource.state == mapping.Resource.State.READY

    def test__mark_broken__with_is_ok_equal_False__resource_state_is_state_BROKEN(self, resource_manager,
                                                                                  task_manager):
        another_real_resource = _create_real_resource(task_manager)
        another_real_resource.mark_broken()
        assert another_real_resource.state == mapping.Resource.State.BROKEN

    def test__add_host__check_that_current_host_is_presented_in_get_hosts_list(self, resource_manager, task_manager,
                                                                               client_node_id):
        real_resource = _create_real_resource(task_manager)
        current_host = client_node_id
        real_resource.remove_host()
        assert current_host not in real_resource.get_hosts()
        real_resource.add_host()
        assert current_host in real_resource.get_hosts()

    def test__remove_host__removes_current_hosts_from_(self, resource_manager, task_manager):
        real_resource = _create_real_resource(task_manager)
        real_resource.remove_host()
        assert len(real_resource.get_hosts()) == 0

    def test__get_hosts__returns_list(self, resource_manager, task_manager):
        real_resource = _create_real_resource(task_manager)
        resource_hosts = real_resource.get_hosts()
        assert isinstance(resource_hosts, list)

    def test__get_hosts__returns_correct_hostname_in_list(self, resource_manager, task_manager, client_node_id):
        real_resource = _create_real_resource(task_manager)
        resource_hosts = real_resource.get_hosts()
        assert resource_hosts == [client_node_id]

    def test__share__with_broken_resource__raises_exception(self, resource_manager):
        pytest.skip('do not wait copier')
        fake_resource = _create_fake_resource()
        fake_resource.state = mapping.Resource.State.BROKEN
        pytest.raises(Exception, fake_resource.share)

    def test__share__with_not_ready_resource__raises_exception(self, resource_manager):
        pytest.skip('do not wait copier')
        fake_resource = _create_fake_resource()
        fake_resource.state = mapping.Resource.State.NOT_READY
        pytest.raises(Exception, fake_resource.share)

    def test__share__with_deleted_resource__raises_exception(self, resource_manager):
        pytest.skip('do not wait copier')
        fake_resource = _create_fake_resource()
        fake_resource.state = mapping.Resource.State.DELETED
        pytest.raises(Exception, fake_resource.share)

    def test__to_dict__returns_dict_object(self, resource_manager, task_manager):
        resource = _create_real_resource(task_manager)
        assert isinstance(resource.to_dict(), dict)

    def test__share__with_ready_resource__returns_not_empty_skynet_id(self, resource_manager, task_manager):
        pytest.skip('Random error "MetaTorrent tracker response not received"')
        real_resource = _create_real_resource(task_manager)
        real_resource.state = mapping.Resource.State.READY
        real_resource.share()
        assert isinstance(real_resource.skynet_id, str)
        assert real_resource.skynet_id != ''

    def test__path_intersection(self, task_manager):
        task = _create_task(task_manager)
        r = _create_real_resource(task_manager, {'resource_filename': 'a'}, task=task, mark_ready=False, make_dir=True)
        open(os.path.join(r.abs_path(), 'file'), 'w').close()
        r.mark_ready()
        pytest.raises(
            errors.TaskError,
            lambda: _create_real_resource(task_manager, {'resource_filename': 'a/a'}, task=task)
        )
        r = _create_real_resource(
            task_manager, {'resource_filename': 'b/b'}, task=task, mark_ready=False, make_dir=True
        )
        open(os.path.join(r.abs_path(), 'file'), 'w').close()
        r.mark_ready()
        try:
            r = _create_real_resource(
                task_manager, {'resource_filename': 'b/a'}, task=task, mark_ready=False, make_dir=True
            )
            open(os.path.join(r.abs_path(), 'file'), 'w').close()
            r.mark_ready()
        except errors.TaskError as exc:
            pytest.fail(str(exc))

    def test__removing_dup_resources(self, task_manager, resource_manager):
        from yasandbox.database import mapping
        task = _create_task(task_manager)
        common_params = dict(
            task_id=task.id,
            owner=task.owner,
            arch=task.arch,
            name="name",
            time=mapping.Resource.Time()
        )
        objects = [
            mapping.Resource(
                type="OTHER_RESOURCE",
                state=mapping.Resource.State.NOT_READY,
                path="path1",
                attributes=[mapping.Resource.Attribute(key="attr1", value="value1")],
                **common_params
            ).save(),
            mapping.Resource(
                type="OTHER_RESOURCE",
                state=mapping.Resource.State.NOT_READY,
                path="path1",
                attributes=[mapping.Resource.Attribute(key="attr1", value="value1")],
                **common_params
            ).save(),
            mapping.Resource(
                type="OTHER_RESOURCE",
                state=mapping.Resource.State.NOT_READY,
                path="path2",
                attributes=[mapping.Resource.Attribute(key="attr1", value="value1")],
                **common_params
            ).save(),
            mapping.Resource(
                type="OTHER_RESOURCE",
                state=mapping.Resource.State.READY,
                path="path3",
                attributes=[mapping.Resource.Attribute(key="attr1", value="value1")],
                **common_params
            ).save(),
            mapping.Resource(
                type="TEST_TASK_RESOURCE",
                state=mapping.Resource.State.NOT_READY,
                path="path4",
                **common_params
            ).save()
        ]
        resources = map(lambda _: resource_manager.load(_.id), objects)
        assert map(lambda _: _.id, resources) == map(lambda _: _.id, objects)
        resource_manager.update(resources[0])
        resources = filter(None, map(lambda _: resource_manager.load(_.id), objects))
        assert map(lambda _: _.id, resources) == filter(lambda _: _ != objects[1].id, map(lambda _: _.id, objects))

    def test__create_same_resource(self, task_manager):
        task = _create_task(task_manager)
        res1 = _create_real_resource(task_manager, {'resource_filename': 'a', 'attrs': {'a': 1, ' b': 2}}, task=task)
        res2 = _create_real_resource(task_manager, {'resource_filename': 'a', 'attrs': {'a ': 1, 'b': 2}}, task=task)
        assert res1.id == res2.id

    def test__create_same_resource_with_different_attrs(self, task_manager):
        task = _create_task(task_manager)
        _create_real_resource(task_manager, {'resource_filename': 'a', 'attrs': {'a': 1, 'b': 2}}, task=task)
        pytest.raises(
            errors.TaskError,
            lambda: _create_real_resource(task_manager, {'resource_filename': 'a', 'attrs': {'b': 2}}, task=task)
        )

    @pytest.mark.xfail(
        dt.datetime.now() < dt.datetime(2014, 10, 28),
        reason="Found bug in skybone on sharing this files structure."
    )
    def test__check_symlinks(self, task_manager):
        res1 = _create_real_resource(task_manager, {'resource_filename': 'a'}, mark_ready=False, make_dir=True)
        b_path = os.path.join(res1.abs_path(), 'b')
        os.makedirs(b_path)
        with open(os.path.join(b_path, 'file'), 'w') as fh:
            os.fchmod(
                fh.fileno(),
                stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP |
                stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH
            )
            fh.write("Hallo, World!")
        os.symlink(b_path, os.path.join(res1.abs_path(), 'c'))
        res1.mark_ready()
        res2 = _create_real_resource(task_manager, {'resource_filename': 'a'}, mark_ready=False, make_dir=True)
        os.symlink(os.path.join('..', 'b'), os.path.join(res2.abs_path(), 'c'))
        pytest.raises(errors.TaskError, res2.mark_ready)

    def test__check_resource_without_files(self, task_manager):
        res = _create_real_resource(task_manager, {'resource_filename': 'a'}, mark_ready=False, make_dir=True)
        b_path = os.path.join(res.abs_path(), 'b')
        os.makedirs(b_path)
        pytest.raises(errors.TaskError, res.mark_ready)
        c_path = os.path.join(b_path, 'c')
        os.makedirs(c_path)
        pytest.raises(errors.TaskError, res.mark_ready)
        open(os.path.join(c_path, 'file'), 'w').close()
        res.mark_ready()

    def test__decrease_ttl(self, task_manager):
        proxy_resource = _create_real_resource(task_manager, {"attrs": {"ttl": "10"}})
        resource = mapping.Resource.objects.with_id(proxy_resource.id)
        assert resource and resource.time.expires is not None
        # emulate work of service process `clean_resources`
        resource.time.expires = dt.datetime.now() + dt.timedelta(days=10)
        resource.save()

        controller.Resource.update(resource, {"attributes": {"ttl": "1"}}, None, None, False, True)

        resource = mapping.Resource.objects.with_id(proxy_resource.id)
        assert resource and resource.time.expires <= dt.datetime.now()


class TestResourceManager:
    """
        Unit tests for resource`s manager class.
        Checking its functions: creating, loading resources, getting resource objects by filters, listing releases, etc.
    """
    def test__create__returns_resource_with_correct_id(self, resource_manager, task_manager, client_manager):
        from yasandbox.proxy import resource as resource_proxy
        resource = resource_proxy.Resource(resource_id=0, name='test resource', file_name='resource_filename',
                                           file_md5='', resource_type='OTHER_RESOURCE',
                                           task_id=507439011,
                                           owner='unittester')
        resource = resource_manager.create(resource)
        assert resource.id > 0

    def test__load__with_correct_id__returns_correct_resource(self, resource_manager, task_manager, client_manager):
        resource = _create_real_resource(task_manager)
        loaded_resource = resource_manager.load(resource.id)
        assert resource.id == loaded_resource.id

    def test__load__with_incorrect_int_id__returns_None(self, resource_manager, task_manager, client_manager):
        loaded_resource = resource_manager.load(507439011)
        assert loaded_resource is None

    def test__load__with_incorrect_not_int_id___raises_SandboxInternalException(self, resource_manager, task_manager,
                                                                                client_manager):
        pytest.raises(errors.TaskError, resource_manager.load, 'sdfsd')

    def test__fast_load_list__with_few_resources(self, resource_manager, task_manager, client_manager):
        resources = _create_resources(task_manager, 10)
        resources_id = [r.id for r in resources]
        resources_id.sort(reverse=True)
        loaded_resources = resource_manager.fast_load_list(resources_id)
        assert len(loaded_resources) == len(resources)
        loaded_resources_ids = [res.id for res in loaded_resources]
        assert resources_id == loaded_resources_ids

    def test__update(self, resource_manager, task_manager, client_manager):
        resource = _create_real_resource(task_manager)
        resource.file_md5 = '1234567890'
        resource.attrs = {'test ': ' test'}
        resource_manager.update(resource)
        loaded_resource = resource_manager.load(resource.id)
        assert resource.file_md5 == loaded_resource.file_md5
        assert resource.attrs == {'test': 'test'}

    def test__list__by_resource_type(self, resource_manager, task_manager, client_manager):
        resources = _create_resources(task_manager, 10)
        _create_real_resource(task_manager, parameters={'resource_type': 'TEST_TASK_RESOURCE_2'})
        res2_list = resource_manager.list(resource_type='TEST_TASK_RESOURCE_2')
        res1_list = resource_manager.list(resource_type='TEST_TASK_RESOURCE')
        assert len(res2_list) == 1
        assert len(res1_list) == len(resources)

    def test__list__with_limit_and_offset_parameters(self, resource_manager, task_manager, client_manager):
        resources = _create_resources(task_manager, 10)
        _create_real_resource(task_manager, parameters={'resource_type': 'TEST_TASK_RESOURCE_2'})
        res_list = resource_manager.list(resource_type='TEST_TASK_RESOURCE', limit=5, offset=2)
        assert len(res_list) == 5
        assert res_list[0].id == resources[7].id

    def test_list_with_date(self, resource_manager, task_manager, client_manager):
        """
            Check for correct date filtering
        """
        for _ in range(2):
            _create_real_resource(task_manager, parameters={'resource_type': 'TEST_TASK_RESOURCE_2'})
        res_list = resource_manager.list(
            resource_type='TEST_TASK_RESOURCE_2',
            date=time.strftime("%Y-%m-%d", time.gmtime(time.time()))
        )
        assert len(res_list) == 2

    def test_list_with_bad_date(self, resource_manager, task_manager, client_manager):
        ''' Check for incorrect date filtering '''
        for i in range(1):
            r = _create_real_resource(task_manager, parameters={'resource_type': 'TEST_TASK_RESOURCE_2'})
            r.timestamp = int(time.time())
            resource_manager.update(r)
        res_list = resource_manager.list(
            resource_type='TEST_TASK_RESOURCE_2',
            date=(dt.datetime.now() - dt.timedelta(days=10)).strftime("%Y-%m-%d")
        )
        assert len(res_list) == 0

    def test__create_resource_returns_list_type(self, resource_manager, task_manager, client_manager):
        _create_resources(task_manager, 10)
        res_list = resource_manager.list(resource_type='INCORREST_RESOURCE_TYPE')
        assert len(res_list) == 0
        assert isinstance(res_list, list)

    def test__count_task_resources(self, resource_manager, task_manager, client_manager):
        RESOURCES_AMOUNT = 12
        _create_resources(task_manager, RESOURCES_AMOUNT)
        _create_real_resource(task_manager, parameters={'resource_type': 'TEST_TASK_RESOURCE_2'})
        res_count = resource_manager.count_task_resources(resource_type='TEST_TASK_RESOURCE')
        assert res_count == RESOURCES_AMOUNT
        res_count = resource_manager.count_task_resources()
        assert res_count == (RESOURCES_AMOUNT + 1) * 2  # *2 = RES+TASK_LOGS

    def test__list_task_resources__any_attrs(self, resource_manager, task_manager, client_manager):
        resource_1 = _create_real_resource(
            task_manager,
            parameters={'attrs': {'attr_1': 'param_1', 'attr_2': 'param_2', 'asdf': 'qwer'}})
        resource_2 = _create_real_resource(
            task_manager,
            parameters={'attrs': {'attr_1': 'param_1', 'attr_3': 'param_3', 'qwer': 'asdf'}})
        _create_real_resource(
            task_manager,
            parameters={'attrs': {'attr_1': 'param_1', 'attr_2': 'param_1', 'attr_3': 'param_2', 'attr_4': 'param_3'}})
        resources_list = resource_manager.list_task_resources(
            any_attrs={'attr_2': 'param_2', 'attr_3': 'param_3', None: None})
        assert len(resources_list) == 2
        assert resources_list[0].id == resource_2.id
        assert resources_list[1].id == resource_1.id
        resources_list = resource_manager.list_task_resources(
            any_attrs={'asdf': None})
        assert len(resources_list) == 1
        assert resources_list[0].id == resource_1.id
        resources_list = resource_manager.list_task_resources(
            any_attrs={None: 'asdf'})
        assert len(resources_list) == 1
        assert resources_list[0].id == resource_2.id

    def test__list_task_resources__all_attrs(self, resource_manager, task_manager, client_manager):
        resource_1 = _create_real_resource(
            task_manager,
            parameters={'attrs': {'attr_1': 'param_1', 'attr_2': 'param_2', 'attr_4': 'param_4', 'asdf': 'qwer'}})
        resource_2 = _create_real_resource(
            task_manager,
            parameters={'attrs': {'attr_1': 'param_1', 'attr_3': 'param_3', 'attr_4': 'param_4', 'qwer': 'asdf'}})
        _create_real_resource(
            task_manager,
            parameters={'attrs': {'attr_1': 'param_4', 'attr_3': 'param_1', 'attr_4': 'param_3'}})
        resources_list = resource_manager.list_task_resources(
            all_attrs={'attr_1': 'param_1', 'attr_4': 'param_4', None: None})
        assert len(resources_list) == 2
        assert resources_list[0].id == resource_2.id
        assert resources_list[1].id == resource_1.id
        resources_list = resource_manager.list_task_resources(
            all_attrs={'asdf': None})
        assert len(resources_list) == 1
        assert resources_list[0].id == resource_1.id
        resources_list = resource_manager.list_task_resources(
            all_attrs={None: 'asdf'})
        assert len(resources_list) == 1
        assert resources_list[0].id == resource_2.id

    def test__list_task_resources__returns_list(self, resource_manager, task_manager, client_manager):
        task = _create_task_with_resources(task_manager)
        resources_list = resource_manager.list_task_resources(task.id)
        assert isinstance(resources_list, list)

    def test__list_task_resources__with_task_without_resources__returns_empty_list(self, resource_manager,
                                                                                   task_manager, client_manager):
        task = _create_task(task_manager)
        resources_list = resource_manager.list_task_resources(task.id)
        assert isinstance(resources_list, list)
        assert len(resources_list) == 0

    def test__list_task_resources__with_absent_task_id__returns_empty_list(self, resource_manager, task_manager,
                                                                           client_manager):
        resources_list = resource_manager.list_task_resources(507439011)
        assert isinstance(resources_list, list)
        assert len(resources_list) == 0

    def test__list_task_resources__with_task_with_resources__returns_list_with_all_resources(self, resource_manager,
                                                                                             task_manager,
                                                                                             client_manager):
        task = _create_task_with_resources(task_manager, types=['TEST_TASK_RESOURCE',
                                                                'TEST_TASK_RESOURCE_2',
                                                                'TEST_TASK_RESOURCE'])
        resources_list = resource_manager.list_task_resources(task.id)
        assert isinstance(resources_list, list)
        assert len(resources_list) == 5

    def test__list_task_resources__with_filter_by_resource_type__returns_list_with_all_resources_of_this_type(
            self,
            resource_manager,
            task_manager,
            client_manager
    ):
        task = _create_task_with_resources(task_manager, types=['TEST_TASK_RESOURCE',
                                                                'TEST_TASK_RESOURCE_2',
                                                                'TEST_TASK_RESOURCE'])
        resources_list = resource_manager.list_task_resources(task.id, resource_type='TEST_TASK_RESOURCE')
        assert len(resources_list) == 3

    def test__bulk_fields(self, task_manager, resource_manager):
        resources = _create_resources(task_manager, 10)
        res_ids = map(lambda r: r.id, resources)
        ret = resource_manager.bulk_fields(res_ids, ['type', 'owner'])
        assert len(ret) == len(resources)
        assert set(map(mapping.ObjectId, ret.keys())) == set(res_ids)
        assert ret[resources[0].id][0] == resources[0].type
        assert ret[resources[-1].id][0] == resources[-1].type
        assert ret[resources[0].id][1] == resources[0].owner
        assert ret[resources[-1].id][1] == resources[-1].owner

    def test__list_task_dep_resources__with_task_with_one_dep_resource__returns_list_with_1_element(self,
                                                                                                    resource_manager,
                                                                                                    task_manager,
                                                                                                    client_manager):
        task = _create_task(task_manager)
        resource = _create_real_resource(task_manager)
        task_manager.register_dep_resource(task.id, resource.id)
        resources_list = resource_manager.list_task_dep_resources(task.id)
        assert len(resources_list) == 1
        assert resources_list[0].id == resource.id

    def test__list_task_dep_resources__with_task_without_dep_resources__returns_empty_list(self, resource_manager,
                                                                                           task_manager,
                                                                                           client_manager):
        task = _create_task(task_manager)
        resources_list = resource_manager.list_task_dep_resources(task.id)
        assert len(resources_list) == 0

    def test__remote_path__returns_correct_remote_path(self, resource_manager, task_manager, client_manager, tasks_dir):
        resource = _create_real_resource(task_manager)
        remote_path = resource.remote_path()
        local_path = resource.local_path()
        assert remote_path == os.path.join(tasks_dir, local_path)

    def test__get_dependent_tasks__with_res_and_2_tasks__returns_correct_list(self, resource_manager, task_manager,
                                                                              client_manager):
        task1 = _create_task(task_manager)
        task2 = _create_task(task_manager)
        resource = _create_real_resource(task_manager)
        task_manager.register_dep_resource(task1.id, resource.id)
        task_manager.register_dep_resource(task2.id, resource.id)
        tasks_list = resource_manager.get_dependent_tasks(resource.id)
        assert len(tasks_list) == 2
        assert task1.id in tasks_list
        assert task2.id in tasks_list

    def test__get_dependent_tasks__with_resource_without_dep_tasks__returns_empty_list(self, resource_manager,
                                                                                       task_manager, client_manager):
        resource = _create_real_resource(task_manager)
        resources_list = resource_manager.get_dependent_tasks(resource.id)
        assert len(resources_list) == 0

    def test__delete_resource(self, resource_manager, task_manager, client_manager):
        resource = _create_real_resource(task_manager)
        resource_manager.delete_resource(resource.id, ignore_last_usage_time=True)
        assert resource_manager.load(resource.id).state == mapping.Resource.State.DELETED

    def test__attributes(self, resource_manager, task_manager, client_manager):
        assert resource_manager.set_attr(507439011, 'a', 'b') is False
        assert resource_manager.get_attr(507439011, 'a') is None
        assert resource_manager.has_attr(507439011, 'a') is False
        assert resource_manager.drop_attr(507439011, 'a') is False
        resource = _create_real_resource(task_manager)
        resource_manager.set_attr(resource.id, ctr.ServiceAttributes.RELEASED, "specific_task")
        assert resource_manager.get_attr(resource.id, ctr.ServiceAttributes.RELEASED) == "specific_task"
        resource_manager.set_attr(resource.id, ctr.ServiceAttributes.TTL, 30)
        assert resource_manager.get_attr(resource.id, ctr.ServiceAttributes.TTL) == "30"
        assert resource_manager.has_attr(resource.id, "empty") is False
        resource_manager.drop_attr(resource.id, ctr.ServiceAttributes.TTL)
        assert resource_manager.has_attr(resource.id, ctr.ServiceAttributes.TTL) is False

    def test__backup(self, resource_manager, task_manager):
        resource1 = _create_real_resource(task_manager, {'resource_type': 'TEST_TASK_RESOURCE'})
        resource2 = _create_real_resource(task_manager, {'resource_type': 'SANDBOX_TASKS_ARCHIVE'})
        assert resource1.attrs.get(ctr.ServiceAttributes.BACKUP_TASK) is None
        assert resource2.attrs.get(ctr.ServiceAttributes.BACKUP_TASK) == "True"
        resource1 = resource_manager.load(resource1.id)
        resource2 = resource_manager.load(resource2.id)
        assert resource1.attrs.get(ctr.ServiceAttributes.BACKUP_TASK) is None
        assert resource2.attrs.get(ctr.ServiceAttributes.BACKUP_TASK) == "True"

    # hosts state

    def test__add_host(self, resource_manager, task_manager, client_manager):
        resource = _create_real_resource(task_manager)
        resource_manager.add_host(resource.id, 'host_1')
        hosts = resource_manager.get_hosts(resource.id)
        assert 'host_1' in hosts

    def test__remove_host(self, resource_manager, task_manager, client_manager):
        resource = _create_real_resource(task_manager)
        resource_manager.add_host(resource.id, 'host_1')
        resource_manager.remove_host(resource.id, 'host_1')
        hosts = resource_manager.get_hosts(resource.id)
        assert 'host_1' not in hosts

    def test__mark_host_to_delete__get_hosts(self, resource_manager, task_manager, client_manager):
        resource = _create_real_resource(task_manager)
        resource_manager.add_host(resource.id, 'host_1')
        resource_manager.mark_host_to_delete(resource.id, 'host_1')
        ok_hosts = resource_manager.get_hosts(resource.id, all=False)
        assert 'host_1' not in ok_hosts
        all_hosts = resource_manager.get_hosts(resource.id, all=True)
        assert 'host_1' in all_hosts

    def test__update_last_usage_time(self, resource_manager, task_manager, client_manager):
        resource = _create_real_resource(task_manager)
        resource_manager.mark_host_to_delete(resource.id, _get_current_host_name())
        lut_pre = resource.last_usage_time
        resource_manager.add_host(resource.id, _get_current_host_name())
        lut_post = resource.last_usage_time
        assert lut_pre <= lut_post

    # service

    @pytest.mark.usefixtures("client_manager", "resource_manager")
    def test__get_resources_to_remove(self, resource_manager, task_manager):
        resource_1 = _create_real_resource(task_manager)
        resource_2 = _create_real_resource(task_manager)
        resource_3 = _create_real_resource(task_manager)
        resource_manager.add_host(resource_1.id, 'host_1')
        resource_manager.add_host(resource_2.id, 'host_2')
        resource_manager.mark_host_to_delete(resource_1.id, 'host_1')
        resource_manager.mark_host_to_delete(resource_1.id, _get_current_host_name())
        resource_manager.mark_host_to_delete(resource_2.id, _get_current_host_name())
        resource_manager.mark_host_to_delete(resource_3.id, _get_current_host_name())
        res_to_remove = controller.Resource.resources_to_remove(_get_current_host_name())
        assert [r.id for r in res_to_remove] == [resource_3.id, resource_1.id, resource_2.id]

    # dependent

    def test__list_dependent__count_dependent(self, resource_manager, task_manager, client_manager):
        task_1 = _create_task(task_manager)
        task_2 = _create_task(task_manager)
        task_3 = _create_task(task_manager)
        resource = _create_real_resource(task_manager)
        task_manager.register_dep_resource(task_1.id, resource.id)
        task_manager.register_dep_resource(task_2.id, resource.id)
        # list
        tasks_list = resource_manager.get_dependent_tasks(resource.id)
        assert tasks_list == [task_2.id, task_1.id]
        # count
        task_manager.register_dep_resource(task_3.id, resource.id)
        dep_cnt = resource_manager.count_dependent(resource.id)
        assert dep_cnt == 3
