import time
import pytest
import httplib
import requests

import common.types.task as types_task
import common.types.resource as types_resource
import yasandbox.database.mapping as mapping


class TestRelease(object):
    def test__list_releases(
        self, json_api_url, gui_su_session, releaser, task_manager, release_manager,
        server, client_node_id, api_su_session, rest_su_session, task_session, monkeypatch, service_user, fake_agentr
    ):
        import common.rest
        import sandbox.executor.commands.task
        reload(sandbox.executor.commands.task)
        import yasandbox.manager
        import yasandbox.manager.tests
        import sandboxsdk.channel
        monkeypatch.setattr(sandboxsdk.channel.channel.sandbox, "server", api_su_session)
        monkeypatch.setattr(common.rest.Client, "__new__", classmethod(lambda *_, **__: rest_su_session))
        monkeypatch.delattr(common.rest.Client, "__init__")

        tasks = [
            yasandbox.manager.tests._create_task(task_manager, status=types_task.Status.SUCCESS),
            yasandbox.manager.tests._create_task(task_manager, status=types_task.Status.SUCCESS)
        ]
        yasandbox.manager.tests._create_real_resource(
            task_manager, {"resource_type": "TEST_TASK_RESOURCE"}, task=tasks[0])
        yasandbox.manager.tests._create_real_resource(
            task_manager, {"resource_type": "TEST_TASK_RESOURCE"}, task=tasks[1])

        release_manager.release_task(tasks[0].id, releaser, status="unstable", message_subject="subject")
        task = yasandbox.manager.task_manager.load(tasks[0].id)
        task_session(rest_su_session, task.id)
        status, message = sandbox.executor.commands.task.ReleaseTask(
            task.id, 'log1',
            release_params=mapping.to_dict(task.release_params),
            agentr=fake_agentr(task)
        ).execute()
        assert status == types_task.Status.RELEASED
        task.set_status(status, message)

        time.sleep(1)
        creation_ts = time.time()

        release_manager.release_task(tasks[1].id, releaser, status="unstable", message_subject="subject")
        task = yasandbox.manager.task_manager.load(tasks[1].id)
        task_session(rest_su_session, task.id)
        status, message = sandbox.executor.commands.task.ReleaseTask(
            task.id, 'log1',
            release_params=mapping.to_dict(task.release_params),
            agentr=fake_agentr(task)
        ).execute()
        assert status == types_task.Status.RELEASED
        task.set_status(status, message)

        time.sleep(1)

        ret = requests.get(
            json_api_url + "/release/list",
            headers=gui_su_session,
        ).json()
        assert len(ret) == 2
        assert ret[0]["id"] == tasks[1].id
        assert ret[1]["id"] == tasks[0].id

        tt = time.time()
        ret = requests.get(
            json_api_url + "/release/list?creation_ts_gte={}&creation_ts_lte={}".format(
                int(creation_ts), int(tt)),
            headers=gui_su_session,
        ).json()
        assert len(ret) == 1
        assert ret[0]["id"] == tasks[1].id


class TestRESTAPIRelease(object):
    def test__task_release(
        self, task_manager, client_node_id, rest_su_session, rest_su_session_login, api_su_session,
        monkeypatch, releaser, task_session, service_user, fake_agentr
    ):
        import common.rest
        import sandbox.executor.commands.task
        reload(sandbox.executor.commands.task)
        import yasandbox.manager
        import yasandbox.manager.tests
        import sandboxsdk.channel
        monkeypatch.setattr(sandboxsdk.channel.channel.sandbox, "server", api_su_session)
        monkeypatch.setattr(common.rest.Client, "__new__", classmethod(lambda *_, **__: rest_su_session))
        monkeypatch.delattr(common.rest.Client, "__init__")

        task = yasandbox.manager.tests._create_task(
            task_manager,
            type="TEST_TASK",
            status=types_task.Status.SUCCESS,
            parameters={"description": "qwer"}
        )
        task.descr = "Task description"
        yasandbox.manager.task_manager.update(task)
        resource = yasandbox.manager.tests._create_resource(
            task_manager, {"resource_type": "TEST_TASK_RESOURCE"}, task=task)

        assert rest_su_session.release[:100] == {"items": [], "limit": 100, "offset": 0, "total": 0}

        assert pytest.raises(
            rest_su_session.HTTPError,
            lambda: rest_su_session.release[task.id][:]
        ).value.status == httplib.NOT_FOUND
        release = {
            "task_id": task.id,
            "subject": "Test release",
            "message": "Message to test release."
        }
        with pytest.raises(rest_su_session.HTTPError) as ex:
            rest_su_session.release(release)
        assert ex.value.status == httplib.BAD_REQUEST and "type" in str(ex.value)

        release_type = list(common.types.task.ReleaseStatus)[0]
        release.update(type=release_type)
        rest_su_session.release(release)
        ret = rest_su_session.task[task.id][:]
        assert ret["status"] == types_task.Status.RELEASING

        task = yasandbox.manager.task_manager.load(task.id)
        task_session(rest_su_session, task.id)
        status, message = sandbox.executor.commands.task.ReleaseTask(
            task.id, 'log1',
            release_params=mapping.to_dict(task.release_params),
            agentr=fake_agentr(task)
        ).execute()
        assert status == types_task.Status.RELEASED
        task.set_status(status, message)
        task = yasandbox.manager.task_manager.load(task.id)
        ret = rest_su_session.release[:100]
        assert ret["limit"] == 100
        assert ret["offset"] == 0
        assert ret["total"] == 1
        items = ret["items"]
        assert len(items) == 1
        item = items[0]
        assert item["created"]
        assert item["task_id"] == task.id
        assert item["type"] == release_type
        assert item["subject"] == release["subject"]
        assert item["author"] == rest_su_session_login

        ret = rest_su_session.release[task.id][:]
        assert ret["created"]
        assert ret["task_id"] == task.id
        assert ret["type"] == release_type
        assert ret["subject"] == release["subject"]
        assert ret["author"] == rest_su_session_login
        assert ret["message"] == release["message"]
        assert ret["resources"] == [{
            "resource_id": resource.id,
            "type": resource.type.name,
            "description": resource.name,
            "releasers": filter(lambda _: _ != releaser, resource.type.releasers)
        }]

    @pytest.mark.parametrize(
        'resource_state',
        (types_resource.State.BROKEN, types_resource.State.DELETED),
    )
    def test__task_release__bad_resource(
        self, task_manager, resource_manager, rest_su_session, api_su_session, monkeypatch, resource_state,
    ):
        import common.rest
        import sandbox.executor.commands.task
        reload(sandbox.executor.commands.task)
        import yasandbox.manager.tests
        import sandboxsdk.channel
        monkeypatch.setattr(sandboxsdk.channel.channel.sandbox, "server", api_su_session)
        monkeypatch.setattr(common.rest.Client, "__new__", classmethod(lambda *_, **__: rest_su_session))
        monkeypatch.delattr(common.rest.Client, "__init__")

        task = yasandbox.manager.tests._create_task(task_manager, type="TEST_TASK", status=types_task.Status.SUCCESS)
        yasandbox.manager.tests._create_real_resource(task_manager, task=task)
        resource = yasandbox.manager.tests._create_real_resource(task_manager, task=task)
        resource.state = resource_state
        resource_manager.update(resource)

        release = {
            "task_id": task.id,
            "subject": "Test release",
            "message": "Message to test release.",
            "type": list(common.types.task.ReleaseStatus)[0],
        }
        with pytest.raises(rest_su_session.HTTPError) as ex:
            rest_su_session.release(release)
        assert ex.value.status == httplib.BAD_REQUEST
        assert "are broken/deleted" in str(ex.value)
