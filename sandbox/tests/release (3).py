# coding: utf-8

import time
import pytest

from . import (
    _create_task,
    _create_resource,
    _create_real_resource,
)
from common import errors
import common.types.task as ctt
import common.types.resource as ctr
import yasandbox.database.mapping as mapping


@pytest.fixture()
def task(task_manager):
    t = _create_task(task_manager, status=ctt.Status.SUCCESS)
    _create_resource(task_manager, task=t)
    return t


class TestReleaseManager:
    """
    test case for release manager testing
    """
    def test__release_task(self, release_manager, task, releaser):
        # mark task for release
        released_task_id = release_manager.release_task(task.id, releaser, addresses_to=['ninja'], status="unstable")
        assert released_task_id == task.id

    def test__release_task__invalid_status(self, release_manager, task, releaser):
        # invalid release status raises exception
        with pytest.raises(errors.ReleaseError):
            release_manager.release_task(task.id, releaser, status='ivalid', addresses_to=['ninja'])

    def test__second_release_of_same_task(self, release_manager, task, releaser):
        # mark task for release
        release_manager.release_task(task.id, releaser, addresses_to=['ninja'], status="unstable")

        # release again
        with pytest.raises(errors.ReleaseError):
            release_manager.release_task(task.id, releaser, addresses_to=['ninja'], status="unstable")

    def test__list_releases(
        self, server, task_manager, release_manager, releaser, api_su_session, rest_su_session, monkeypatch,
        task_session, service_user, client_node_id, fake_agentr
    ):
        import common.rest
        import sandbox.executor.commands.task
        reload(sandbox.executor.commands.task)
        import sandboxsdk.channel
        monkeypatch.setattr(sandboxsdk.channel.channel.sandbox, 'server', api_su_session)
        monkeypatch.setattr(common.rest.Client, '__new__', classmethod(lambda *_, **__: rest_su_session))
        monkeypatch.delattr(common.rest.Client, '__init__')

        # create tasks
        tasks = [
            _create_task(task_manager, arch="freebsd", status=ctt.Status.SUCCESS),
            _create_task(task_manager, arch="linux", status=ctt.Status.SUCCESS),
        ]

        # create resources
        _create_real_resource(
            task_manager,
            {'resource_type': 'TEST_TASK_RESOURCE'}, task=tasks[0]
        )
        _create_real_resource(
            task_manager,
            {'resource_type': 'BASESEARCH_EXECUTABLE', 'resource_filename': 'unit_test_resource1'}, task=tasks[0]
        )
        _create_real_resource(
            task_manager,
            {'resource_type': 'SANDBOX_ARCHIVE', 'resource_filename': 'unit_test_resource2'}, task=tasks[1]
        )
        _create_real_resource(
            task_manager,
            {'resource_type': 'BASESEARCH_EXECUTABLE', 'resource_filename': 'unit_test_resource3'}, task=tasks[1]
        )
        _create_real_resource(
            task_manager,
            {'resource_type': 'SANDBOX_ARCHIVE', 'resource_filename': 'unit_test_resource4'}, task=tasks[1],
            mark_ready=False
        )
        # create releases
        TESTING_STATUS = release_manager.Status.TESTING
        CHANGELOG = ['meow']
        releases = []
        releases.append(release_manager.release_task(
            tasks[0].id, releaser,
            changelog=CHANGELOG, addresses_to=['ninja'], status="unstable", message_subject='subject'
        ))
        releases.append(release_manager.release_task(
            tasks[1].id, releaser,
            status=TESTING_STATUS, addresses_to=['test'], message_subject='subject'
        ))

        for i in xrange(len(tasks)):
            task = task_manager.load(tasks[i].id)
            task_session(rest_su_session, task.id)
            status, message = sandbox.executor.commands.task.ReleaseTask(
                task.id, 'log1',
                release_params=mapping.to_dict(task.release_params),
                agentr=fake_agentr(task)
            ).execute()
            assert status == ctt.Status.RELEASED
            task.set_status(status, message)

        # check all
        releases_list = release_manager.list_releases()
        assert len(releases_list) == 2
        assert len(releases_list[0]['resources']) == 2
        assert len(releases_list[1]['resources']) == 2
        # check specific type
        releases_list = release_manager.list_releases(
            resource_type='SANDBOX_ARCHIVE', resource_as_dict=True
        )
        assert releases_list[0]['resources'][0]['type_name'] == 'SANDBOX_ARCHIVE'
        # check specific task id
        releases_list = release_manager.list_releases(task_id=tasks[0].id)
        assert len(releases_list) == 1
        assert releases_list[0]['id'] == tasks[0].id
        assert str(releases_list[0]['resources'][0].type) == 'TEST_TASK_RESOURCE'
        # check status
        releases_list = release_manager.list_releases(release_status=TESTING_STATUS)
        assert releases_list[0]['id'] == tasks[1].id
        assert releases_list[0]['status'] == TESTING_STATUS
        # check arch
        releases_list = release_manager.list_releases(arch='linux')
        assert len(releases_list[0]['resources']) == 2
        assert len(releases_list[1]['resources']) == 1
        releases_list = release_manager.list_releases(arch='freebsd')
        assert len(releases_list[0]['resources']) == 1
        assert len(releases_list[1]['resources']) == 2
        releases_list = release_manager.list_releases(arch='any')
        assert len(releases_list[0]['resources']) == 1
        assert len(releases_list[1]['resources']) == 1
        # check changelog
        releases_list = release_manager.list_releases(task_id=tasks[0].id)
        assert releases_list[0]['changelog'] == CHANGELOG

    def test__list_releases__order_by(
        self, task_manager, release_manager, releaser, server, api_su_session, rest_su_session, monkeypatch,
        task_session, service_user, client_node_id, fake_agentr
    ):
        import common.rest
        import sandbox.executor.commands.task
        reload(sandbox.executor.commands.task)
        import sandboxsdk.channel
        monkeypatch.setattr(sandboxsdk.channel.channel.sandbox, 'server', api_su_session)
        monkeypatch.setattr(common.rest.Client, '__new__', classmethod(lambda *_, **__: rest_su_session))
        monkeypatch.delattr(common.rest.Client, '__init__')

        tasks = [
            _create_task(task_manager, status=ctt.Status.SUCCESS),
            _create_task(task_manager, status=ctt.Status.SUCCESS),
        ]
        _create_real_resource(task_manager, {'resource_type': 'TEST_TASK_RESOURCE'}, task=tasks[0])
        _create_real_resource(task_manager, {'resource_type': 'TEST_TASK_RESOURCE'}, task=tasks[1])

        release_manager.release_task(tasks[1].id, releaser, status="unstable", message_subject='subject')
        task = task_manager.load(tasks[1].id)
        task_session(rest_su_session, task.id)
        status, message = sandbox.executor.commands.task.ReleaseTask(
            task.id, 'log1',
            release_params=mapping.to_dict(task.release_params),
            agentr=fake_agentr(task)
        ).execute()
        assert status == ctt.Status.RELEASED
        task.set_status(status, message)
        time.sleep(1)
        release_manager.release_task(tasks[0].id, releaser, status="unstable", message_subject='subject')
        task = task_manager.load(tasks[0].id)
        task_session(rest_su_session, task.id)
        status, message = sandbox.executor.commands.task.ReleaseTask(
            task.id, 'log1',
            release_params=mapping.to_dict(task.release_params),
            agentr=fake_agentr(task)
        ).execute()
        assert status == ctt.Status.RELEASED
        task.set_status(status, message)

        ret = release_manager.list_releases()
        assert ret[0]['id'] == tasks[1].id
        assert ret[1]['id'] == tasks[0].id

        ret = release_manager.list_releases(order_by='-id')
        assert ret[0]['id'] == tasks[1].id
        assert ret[1]['id'] == tasks[0].id

        ret = release_manager.list_releases(order_by='-release__creation_time')
        assert ret[0]['id'] == tasks[0].id
        assert ret[1]['id'] == tasks[1].id

    def test__list_releases__deleted(
        self, task_manager, release_manager, releaser, server, api_su_session, rest_session,
        rest_su_session, monkeypatch, task_session, service_user, client_node_id, fake_agentr
    ):
        import common.rest
        import sandbox.executor.commands.task
        reload(sandbox.executor.commands.task)
        import sandboxsdk.channel
        monkeypatch.setattr(sandboxsdk.channel.channel.sandbox, 'server', api_su_session)
        monkeypatch.setattr(common.rest.Client, '__new__', classmethod(lambda *_, **__: rest_session))
        monkeypatch.delattr(common.rest.Client, '__init__')

        tasks = [
            _create_task(task_manager, status=ctt.Status.SUCCESS),
            _create_task(task_manager, status=ctt.Status.SUCCESS),
        ]
        _create_real_resource(task_manager, {'resource_type': 'TEST_TASK_RESOURCE'}, task=tasks[0])
        _create_real_resource(task_manager, {'resource_type': 'TEST_TASK_RESOURCE'}, task=tasks[1])
        release_manager.release_task(tasks[0].id, releaser, status="unstable", message_subject='subject')
        release_manager.release_task(tasks[1].id, releaser, status="unstable", message_subject='subject')

        for i in xrange(len(tasks)):
            task = task_manager.load(tasks[i].id)
            task_session(rest_session, task.id)
            status, message = sandbox.executor.commands.task.ReleaseTask(
                task.id, 'log1',
                release_params=mapping.to_dict(task.release_params),
                agentr=fake_agentr(task)
            ).execute()
            assert status == ctt.Status.RELEASED
            task.set_status(status, message)

        ret = release_manager.list_releases()
        assert len(ret) == 2

        ret = rest_su_session.batch.tasks['delete'].update([tasks[0].id])
        assert ret[0]['status'] == 'SUCCESS', ret
        ret = release_manager.list_releases()
        assert len(ret) == 1
        assert ret[0]['id'] == tasks[1].id

    def test__release_task2(self, task_manager, release_manager, releaser):
        # create finished task
        finished_task = _create_task(task_manager, status=ctt.Status.SUCCESS)
        _create_real_resource(
            task_manager,
            {'resource_type': 'TEST_TASK_RESOURCE'},
            task=finished_task,
        )
        # create not finished tasks
        not_finished_tasks = []
        for status in filter(
            lambda s: not ctt.Status.can_switch(s, ctt.Status.RELEASING),
            ctt.Status
        ):
            not_finished_tasks.append(_create_task(task_manager, status=status))
        try:
            release_manager.release_task(
                finished_task.id, releaser,
                addresses_to=['ninja'], status="unstable", message_subject='subject'
            )
        except errors.ReleaseError:
            pytest.fail('release_task raised ReleaseInternalException unexpectedly')
        for task in not_finished_tasks:
            try:
                release_manager.release_task(
                    task.id, 'user',
                    addresses_to=['ninja'], status="unstable", message_subject='subject'
                )
            except errors.ReleaseError as exc:
                if task.status == ctt.Status.RELEASING:
                    assert exc.message == 'Releasing of task #{} is already in progress'.format(task.id)
                else:
                    assert exc.message == 'Task #{} is not finished successfully'.format(task.id)

    def test__count_releases(
        self, task_manager, release_manager, releaser, server, api_su_session, rest_su_session, monkeypatch,
        task_session, service_user, client_node_id, fake_agentr
    ):
        import common.rest
        import sandbox.executor.commands.task
        reload(sandbox.executor.commands.task)
        import sandboxsdk.channel
        monkeypatch.setattr(sandboxsdk.channel.channel.sandbox, 'server', api_su_session)
        monkeypatch.setattr(common.rest.Client, '__new__', classmethod(lambda *_, **__: rest_su_session))
        monkeypatch.delattr(common.rest.Client, '__init__')

        # create tasks
        tasks = []
        for i in xrange(2):
            tasks.append(_create_task(task_manager, status=ctt.Status.SUCCESS))
        # create resources
        _create_real_resource(
            task_manager,
            {'resource_type': 'TEST_TASK_RESOURCE', 'resource_filename': 'unit_test_resource1'}, task=tasks[0]
        )
        _create_real_resource(
            task_manager,
            {'resource_type': 'TEST_TASK_RESOURCE_2', 'resource_filename': 'unit_test_resource2'}, task=tasks[0]
        )
        _create_real_resource(
            task_manager,
            {'resource_type': 'SANDBOX_ARCHIVE', 'resource_filename': 'unit_test_resource3'}, task=tasks[1]
        )
        _create_real_resource(
            task_manager,
            {'resource_type': 'SANDBOX_ARCHIVE', 'resource_filename': 'unit_test_resource4'}, task=tasks[1],
            mark_ready=False
        )
        # create releases
        TESTING_STATUS = release_manager.Status.TESTING
        CHANGELOG = ['meow']
        releases = []
        releases.append(release_manager.release_task(
            tasks[0].id, releaser,
            changelog=CHANGELOG, addresses_to=['ninja'], status="unstable", message_subject='subject'
        ))
        releases.append(release_manager.release_task(
            tasks[1].id, releaser,
            status=TESTING_STATUS, addresses_to=['test'], message_subject='subject'
        ))

        for i in xrange(len(tasks)):
            task = task_manager.load(tasks[i].id)
            task_session(rest_su_session, task.id)
            status, message = sandbox.executor.commands.task.ReleaseTask(
                task.id, 'log1',
                release_params=mapping.to_dict(task.release_params),
                agentr=fake_agentr(task)
            ).execute()
            assert status == ctt.Status.RELEASED
            task.set_status(status, message)

        # check all
        releases_count = release_manager.count_releases()
        assert releases_count == 2
        # check specific type
        releases_count = release_manager.count_releases(resource_type='SANDBOX_ARCHIVE')
        assert releases_count == 1
        # check specific task id
        releases_count = release_manager.count_releases(task_id=tasks[0].id)
        assert releases_count == 1
        # check status
        releases_count = release_manager.count_releases(release_status=TESTING_STATUS)
        assert releases_count == 1

    def test__unsuccessful_release_with_bad_resources(self, task_manager, resource_manager, release_manager, releaser):
        task1 = _create_task(task_manager, status=ctt.Status.SUCCESS)
        resource1 = _create_real_resource(task_manager, task=task1)
        resource_manager.delete_resource(resource1.id, ignore_last_usage_time=True)
        with pytest.raises(errors.ReleaseError):
            release_manager.release_task(task1.id, releaser, addresses_to=['ninja'], status="unstable")

        task2 = _create_task(task_manager, status=ctt.Status.SUCCESS)
        resource2 = _create_real_resource(task_manager, task=task2, mark_ready=False)
        resource2.state = ctr.State.BROKEN
        resource_manager.update(resource2)
        with pytest.raises(errors.ReleaseError):
            release_manager.release_task(task2.id, releaser, addresses_to=['ninja'], status="unstable")

    def test__successful_release_with_broken_unreleaseable_resources(
        self, task_manager, resource_manager, release_manager, releaser
    ):
        task = _create_task(task_manager, status=ctt.Status.SUCCESS)
        _create_real_resource(task_manager, task=task)

        res = _create_real_resource(
            task_manager, task=task,
            parameters={"resource_type": "TASK_LOGS", "resource_filename": "blah"}
        )
        assert not res.type.releaseable
        res.state = ctr.State.BROKEN
        resource_manager.update(res)
        release_manager.release_task(task.id, releaser, addresses_to=["ninja"], status="unstable")
