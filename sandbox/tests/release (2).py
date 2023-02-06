import pytest
import xmlrpclib

import common.types.task
import common.types.resource
import yasandbox.database.mapping as mapping

import yasandbox.manager.tests
import yasandbox.api.xmlrpc.tests


@pytest.mark.usefixtures("server")
class TestRelease(yasandbox.api.xmlrpc.tests.TestXmlrpcBase):
    def test_empty_release(self, api_session):
        res = api_session.list_releases({'task_id': -1})
        assert [] == res

    def test__create_release__no_task(self, task_manager, api_session):
        pytest.raises(xmlrpclib.Fault, api_session.create_release, 1)

    def test__create_release__non_finished_task(self, task_manager, api_session):
        task = yasandbox.manager.tests._create_task(
            task_manager,
            status=common.types.task.Status.FAILURE,
        )

        pytest.raises(xmlrpclib.Fault, api_session.create_release, task.id)

    def test__create_release__invalid_release_status(self, task_manager, api_session):
        task = yasandbox.manager.tests._create_task(
            task_manager,
            status=common.types.task.Status.SUCCESS,
        )

        pytest.raises(xmlrpclib.Fault, api_session.create_release, task.id, 'non-stable')

    def test__create_release__no_resources(self, task_manager, api_session):
        task = yasandbox.manager.tests._create_task(
            task_manager,
            status=common.types.task.Status.SUCCESS,
        )

        pytest.raises(xmlrpclib.Fault, api_session.create_release, task.id)

    def test__create_release__access_denied(self, task_manager, api_session):
        task = yasandbox.manager.tests._create_task(
            task_manager,
            status=common.types.task.Status.SUCCESS,
        )
        yasandbox.manager.tests._create_real_resource(
            task_manager,
            {'resource_type': 'TEST_TASK_RESOURCE_2'},
            task=task,
        )

        pytest.raises(xmlrpclib.Fault, api_session.create_release, task.id)

    def test__create_release__already_released(self, task_manager, api_session):
        task = yasandbox.manager.tests._create_task(
            task_manager,
            status=common.types.task.Status.SUCCESS,
        )
        yasandbox.manager.tests._create_real_resource(
            task_manager,
            {'resource_type': 'TEST_TASK_RESOURCE'},
            task=task,
        )

        api_session.create_release(task.id)
        pytest.raises(xmlrpclib.Fault, api_session.create_release, task.id)

    def test__create_release(
        self, task_manager, api_session, api_session_login, api_su_session,
        rest_su_session, monkeypatch, task_session, service_user, client_node_id, fake_agentr
    ):
        import common.rest
        import sandbox.executor.commands.task
        reload(sandbox.executor.commands.task)
        import sandboxsdk.channel
        monkeypatch.setattr(sandboxsdk.channel.channel.sandbox, 'server', api_su_session)
        monkeypatch.setattr(common.rest.Client, '__new__', classmethod(lambda *_, **__: rest_su_session))
        monkeypatch.delattr(common.rest.Client, '__init__')

        task = yasandbox.manager.tests._create_task(
            task_manager,
            status=common.types.task.Status.SUCCESS,
        )
        res = yasandbox.manager.tests._create_real_resource(
            task_manager,
            {'resource_type': 'TEST_TASK_RESOURCE'},
            task=task,
        )

        ret = api_session.create_release(task.id, 'stable', 'subject')
        assert ret == task.id

        task = yasandbox.manager.task_manager.load(task.id)
        task_session(rest_su_session, task.id)
        status, message = sandbox.executor.commands.task.ReleaseTask(
            task.id, 'log1',
            release_params=mapping.to_dict(task.release_params),
            agentr=fake_agentr(task)
        ).execute()
        assert status == common.types.task.Status.RELEASED
        task.set_status(status, message)

        ret = api_session.list_releases()
        assert ret[0]['task_id'] == task.id
        assert ret[0]['author'] == api_session_login
        assert ret[0]['resources'][0]['id'] == res.id

    def test__list_broken_releases(
        self, task_manager, api_session, api_session_login, api_su_session,
        rest_su_session, monkeypatch, task_session, service_user, client_node_id, fake_agentr
    ):
        import common.rest
        import sandbox.executor.commands.task
        reload(sandbox.executor.commands.task)
        import sandboxsdk.channel
        monkeypatch.setattr(sandboxsdk.channel.channel.sandbox, 'server', api_su_session)
        monkeypatch.setattr(common.rest.Client, '__new__', classmethod(lambda *_, **__: rest_su_session))
        monkeypatch.delattr(common.rest.Client, '__init__')

        task = yasandbox.manager.tests._create_task(
            task_manager,
            status=common.types.task.Status.SUCCESS,
        )
        res = yasandbox.manager.tests._create_real_resource(
            task_manager,
            {'resource_type': 'TEST_TASK_RESOURCE'},
            task=task,
        )

        ret = api_session.create_release(task.id, 'stable', 'subject')
        assert ret == task.id

        task = yasandbox.manager.task_manager.load(task.id)
        task_session(rest_su_session, task.id)
        status, message = sandbox.executor.commands.task.ReleaseTask(
            task.id, 'log1',
            release_params=mapping.to_dict(task.release_params),
            agentr=fake_agentr(task)
        ).execute()
        assert status == common.types.task.Status.RELEASED
        task.set_status(status, message)

        ret = api_session.list_releases(dict(resource_type=str(res.type)))
        assert ret[0]['task_id'] == task.id
        assert ret[0]['author'] == api_session_login
        assert ret[0]['resources'][0]['id'] == res.id

        mapping.Resource.objects(id=res.id).update(set__state=common.types.resource.State.BROKEN)
        ret = api_session.list_releases(dict(resource_type=str(res.type)))
        assert not len(ret)

        ret = api_session.list_releases(dict(resource_type=str(res.type), include_broken=True))
        assert len(ret) == 1
        assert ret[0]['task_id'] == task.id
        assert ret[0]['resources'][0]['id'] == res.id
        assert ret[0]['resources'][0]['state'] == res.State.BROKEN
