import collections

import pytest

import sandbox.common.types.misc as ctm
import sandbox.common.types.task as ctt
import sandbox.common.types.user as ctu
import sandbox.common.types.resource as ctr

from sandbox.yasandbox.database import mapping

from sandbox.yasandbox.controller import user as user_controller
from sandbox.yasandbox.controller import client as client_controller

from sandbox.yasandbox.manager import tests as manager_tests
from sandbox.tests.common.models import user as user_test_models


BRS = ctm.BatchResultStatus


class TestBatchOpResource(object):

    def test__resources_batch_marks(self, rest_session, rest_su_session, task_manager, resource_manager):
        task = manager_tests._create_task(task_manager)
        resources = [
            manager_tests._create_resource(
                task_manager, task=task, create_logs=False,
                parameters={"resource_filename": "resource_file{}".format(i)}
            ) for i in range(8)
        ]
        ids = [o.id for o in resources]
        ret = rest_session.batch.resources["do_not_remove"].update(ids)
        assert all(_["status"] == BRS.ERROR for _ in ret)

        ret = rest_su_session.batch.resources["do_not_remove"].update(ids)
        assert all(_["status"] == BRS.SUCCESS for _ in ret)
        assert all(resource_manager.get_attr(_id, "ttl") for _id in ids)

        ret = rest_su_session.batch.resources.backup.update(ids)
        assert all(_["status"] == BRS.SUCCESS for _ in ret)
        assert all(resource_manager.get_attr(_id, "backup_task") for _id in ids)

    def test__resource_batch_delete_restore(self, rest_su_session, task_manager, resource_manager, service_user):
        task = manager_tests._create_task(task_manager)
        resources = [
            manager_tests._create_resource(
                task_manager, task=task, create_logs=False,
                parameters={"resource_filename": "resource_file{}".format(i)}
            ) for i in range(4)
        ]
        ids = [o.id for o in resources]
        update_times = {o.id: o.last_updated_time for o in resources}
        ret = rest_su_session.batch.resources["delete"].update(ids)
        assert all(_["status"] == BRS.SUCCESS for _ in ret)
        ret = rest_su_session.resource.read(limit=100)
        assert all(o["time"]["updated"] != update_times[o["id"]] for o in ret["items"])
        assert all(res.is_deleted() for res in resource_manager.fast_load_list(ids))
        ret = rest_su_session.batch.resources.restore.update(ids)
        assert all(_["status"] == BRS.SUCCESS for _ in ret)
        assert task_manager.list_query(type="RESTORE_RESOURCE", hidden=True).count() == len(resources)


class TestBatchOpTask(object):

    @pytest.mark.usefixtures("server")
    def test__tasks_batch(self, task_manager, rest_session, rest_session_login, rest_session_group, client_manager):
        client_manager.create("__abc__", ncpu=8, ram=4096).save()

        task1 = manager_tests._create_task(
            task_manager, author=rest_session_login, owner=rest_session_login, type="TEST_TASK", host="__abc__"
        )
        task2 = manager_tests._create_task(
            task_manager, author=rest_session_login, owner=rest_session_group, type="TEST_TASK", host="__abc__"
        )
        task2.ctx["raise_exception_on_enqueue"] = True
        task_manager.update(task2)
        task3 = manager_tests._create_task(task_manager, type="TEST_TASK")

        ret = rest_session.batch.tasks.start.update([task1.id, task3.id])
        assert len(ret) == 2
        assert ret[0]["id"] == task1.id and ret[0]["status"] == BRS.SUCCESS, ret[0]
        assert ret[1]["status"] == BRS.ERROR and "not permitted to start task" in ret[1]["message"]

        ret = rest_session.batch.tasks.start.update([task2.id])
        assert len(ret) == 1
        assert ret[0]["id"] == task2.id and ret[0]["status"] == BRS.ERROR, ret[0]
        assert ret[0]["message"] == "Exception on enqueue."

        task1.reload().set_status(ctt.Status.ENQUEUED, force=True)
        task3.reload().set_status(ctt.Status.ENQUEUED, force=True)
        ret = rest_session.batch.tasks.stop.update([task1.id, task2.id, task3.id])
        assert len(ret) == 3
        assert ret[0]["id"] == task1.id and ret[0]["status"] == BRS.SUCCESS and ret[0]["message"], ret[0]
        assert ret[1]["status"] == BRS.WARNING and "cannot be stopped" in ret[1]["message"], ret[1]
        assert ret[2]["status"] == BRS.ERROR and "not permitted to stop task" in ret[2]["message"], ret[2]

        task1.reload().set_status(ctt.Status.STOPPING, force=True)
        ret = rest_session.batch.tasks["delete"].update([task1.id, task2.id, task3.id])
        assert len(ret) == 3
        assert ret[0]["status"] == BRS.WARNING and "cannot be deleted" in ret[0]["message"], ret[0]
        assert ret[1]["id"] == task2.id and ret[1]["status"] == BRS.SUCCESS and ret[1]["message"], ret[1]
        assert ret[2]["status"] == BRS.ERROR and "not permitted to delete task" in ret[2]["message"], ret[2]

        task_type, limit = ("TEST_TASK_2", ctu.DEFAULT_PRIORITY_LIMITS.api)
        task = rest_session.task(
            type=task_type,
            description="abcdef",
            owner=rest_session_group,
            requirements={"host": "__abc__"},
            priority=ctt.Priority(ctt.Priority.Class.USER, ctt.Priority.Subclass.HIGH)
        )
        rest_session.batch.tasks.start.update([task["id"]])
        audit = rest_session.task[task["id"]].audit[:]
        assert audit[-1]["status"] == ctt.Status.ENQUEUED
        lowered_priority = ctt.Priority.make(rest_session.task[task["id"]][:]["priority"])
        assert lowered_priority == limit

    @pytest.mark.usefixtures("server")
    def test__batch_start_permissions(
        self,
        rest_session, rest_session_login,
        rest_su_session, rest_su_session_login,
        rest_sudoer_session,
        task_manager,
    ):
        client_id = client_controller.Client.create("sandbox1234").id
        another_user_login = user_test_models.register_user("another-user")
        robot_login = user_test_models.register_robot("my-robot", [rest_session_login])
        group_name = user_controller.Group.create(
            mapping.Group(name="THE-GROUP", users=[rest_session_login, robot_login, another_user_login])
        ).name
        another_robot_login = user_test_models.register_robot("their-robot")
        another_group_name = user_controller.Group.create(
            mapping.Group(name="ANOTHER-GROUP", users=[another_robot_login, rest_su_session_login])
        ).name

        for test_case in (
            (rest_session, rest_session_login, group_name, BRS.SUCCESS),
            (rest_session, another_user_login, group_name, BRS.SUCCESS),  # TODO: Should be forbidden SANDBOX-9507
            (rest_session, robot_login, group_name, BRS.SUCCESS),
            (rest_session, another_robot_login, another_group_name, BRS.ERROR),
            (rest_sudoer_session, rest_session_login, group_name, BRS.SUCCESS),
            (rest_sudoer_session, another_robot_login, group_name, BRS.ERROR),
            (rest_su_session, rest_session_login, group_name, BRS.SUCCESS),
            (rest_su_session, another_robot_login, group_name, BRS.SUCCESS),  # Legacy permission, should be dropped
        ):
            rest_client, user, group, expected_status = test_case
            task = manager_tests._create_task(
                task_manager,
                author=user, owner=group, type="TEST_TASK", host=client_id,
            )
            response = rest_client.batch.tasks.start.update([task.id])
            assert response[0]["status"] == expected_status, (test_case, response)

    @pytest.mark.usefixtures("server")
    def test__batch_comments(self, task_manager, rest_session, rest_session_login):
        task_ids = [
            manager_tests._create_task(
                task_manager, "TEST_TASK", ctt.Status.EXECUTING,
                owner=rest_session_login, author=rest_session_login
            ).id for _ in range(3)
        ]

        comment = "Custom batch stop commentary test"
        rest_session.batch.tasks.stop.update({
            "id": task_ids,
            "comment": comment
        })

        for tid in task_ids:
            audit = rest_session.task.audit.read(id=tid)
            assert any(entry.get("message") == comment for entry in audit)

    @pytest.mark.usefixtures("server")
    def test__on_restart_policy_is_applied_on_task_restart(
        self, task_manager, resource_manager, rest_session, rest_session_login, client_manager
    ):
        client_manager.create("__abc__", ncpu=8, ram=4096).save()
        task = manager_tests._create_task(
            task_manager,
            author=rest_session_login,
            owner=rest_session_login,
            type="TEST_TASK",
            host="__abc__",
            status=ctt.Status.EXCEPTION,
        )
        resources = [
            manager_tests._create_resource(
                task_manager, task=task, create_logs=False, mark_ready=False,
                parameters={"resource_filename": "resource_file{}".format(i)}
            )
            for i in range(3)
        ]
        for res in resources:
            res.state = ctr.State.BROKEN
            resource_manager.update(res)

        rest_session.batch.tasks.start.update([task.id])
        assert task_manager.load(task.id).status == ctt.Status.ENQUEUING
        assert all(
            (
                _.type.restart_policy == ctr.RestartPolicy.DELETE and
                resource_manager.load(_.id).state == ctr.State.DELETED
            )
            for _ in resources
        )


class TestSchedulerBatchOps(object):

    @classmethod
    def _create_user(cls, user_name):
        user = mapping.User(login=user_name)
        user.save()
        user_controller.User.validated(user_name)
        return user

    @classmethod
    def _create_group(cls, group_name, users):
        return user_controller.Group.create(mapping.Group(name=group_name, users=users, email="email@"))

    def test__scheduler_ops(self, scheduler_controller, rest_session, rest_session_login):
        task_type = "TEST_TASK"
        another_user = self._create_user("another_user").login

        sch_ids = []
        for group_name in (
            another_user,
            self._create_group("GROUP1", [another_user]).name,
            self._create_group("GROUP2", [rest_session_login, another_user]).name,
        ):
            sch = scheduler_controller.create(task_type, group_name, another_user)
            sch_ids.append(sch.id)

        for operation in ("start", "stop", "delete"):
            resp = rest_session.batch.schedulers.__getattr__(operation).update(sch_ids)
            for ind, status in enumerate([BRS.ERROR, BRS.ERROR, BRS.SUCCESS]):
                assert resp[ind]["status"] == status, resp[ind]


class TestBucketBatchOps(object):
    ResourceParameter = collections.namedtuple("ResourceParameter", ("state", "mds"))

    def test__cleanup_ops(
        self, rest_session, rest_session2,
        task_manager, resource_manager,
        abc_simulator, s3_simulator
    ):
        bucket1, bucket2, bucket3 = "1", "2", "3"
        resources_parameters = [
            # Should be deleted
            self.ResourceParameter(ctr.State.DELETED, {"key": "1", "namespace": bucket1}),
            self.ResourceParameter(ctr.State.BROKEN, {"key": "2", "namespace": bucket1}),
            self.ResourceParameter(ctr.State.DELETED, {"key": "3", "namespace": bucket2}),
            # Should not be deleted
            self.ResourceParameter(ctr.State.DELETED, {}),
            self.ResourceParameter(ctr.State.DELETED, {"key": "4", "namespace": bucket3}),
            self.ResourceParameter(ctr.State.DELETED, {"key": "5", "namespace": None}),
            self.ResourceParameter(ctr.State.READY, {"key": "6", "namespace": bucket1}),
            self.ResourceParameter(ctr.State.NOT_READY, {"key": "7", "namespace": bucket1}),
        ]
        task = manager_tests._create_task(task_manager, status=ctt.Status.SUCCESS)
        resources = [
            manager_tests._create_resource(
                task_manager, task=task, create_logs=False,
                parameters={"resource_filename": "resource_file{}".format(i)},
            ) for i in range(len(resources_parameters))
        ]
        for i, resource in enumerate(resources):
            resource.state = resources_parameters[i].state
            if resources_parameters[i].mds:
                resource.mds = resources_parameters[i].mds
            resource_manager.update(resource)

        # Test bucket not exists
        s3_simulator.force_error_responses(404, methods=["GET"], counter=1)
        resp = rest_session.batch.buckets["cleanup"].update([bucket3])
        assert resp[0]["status"] == BRS.ERROR

        # Test unauthorized access
        resp = rest_session2.batch.buckets["cleanup"].update([bucket1])
        assert resp[0]["status"] == BRS.ERROR

        # Test resource filter
        resp = rest_session.batch.buckets["cleanup"].update([bucket1, bucket2])
        print(resp)
        assert resp[0]["status"] == BRS.SUCCESS
        assert resp[1]["status"] == BRS.SUCCESS
        for resource in resources[:3]:
            assert resource_manager.load(resource.id).force_cleanup is True
        for resource in resources[3:]:
            assert resource_manager.load(resource.id).force_cleanup is None
