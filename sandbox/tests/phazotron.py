import os
import json

import pytest
import subprocess32 as sp

import sandbox.common.types.task as ctt
import sandbox.common.types.resource as ctr

from sandbox import sdk2

from sandbox.tests import tasks as tasks_tests
from sandbox.yasandbox.manager import tests as manager_tests

TS = ctt.Status


def stop_task(cmd):
    from sandbox.yasandbox import manager
    t = manager.task_manager.load(cmd.task_id)
    t.set_status(TS.STOPPED, force=True)
    manager.task_manager.update(t)
    cmd.cancel()


@pytest.mark.test_tasks
class TestPhazotron(object):
    @pytest.mark.usefixtures("server", "client", "agentr", "resource_manager", "s3_simulator")
    def test__test_synchrophazotron(
        self, task_manager, api_session_login, rest_su_session, client_node_id, test_task
    ):
        task = manager_tests._create_task(
            task_manager, type=test_task.type, author=api_session_login, parameters={test_task.LiveTime.name: 15},
            status=ctt.Status.ENQUEUING, host=client_node_id
        )

        def executing_trigger(cmd):
            try:
                resource = manager_tests._create_resource(
                    task_manager, task=task,
                    parameters={"resource_type": "TEST_TASK_RESOURCE", "resource_filename": "file"}
                )

                synchrophazotron_path = task.path("synchrophazotron")
                assert os.path.exists(synchrophazotron_path)

                output = sp.check_output([synchrophazotron_path, str(resource.id)], stderr=sp.STDOUT).strip()
                assert output == resource.abs_path()

                meta = dict(
                    path="file_path",
                    type="TEST_TASK_RESOURCE",
                    description="Resource created via synchrophazotron",
                    attributes=dict(a="b", c=1),
                    chupakabra="blablabla",
                )
                with open(os.path.join(task.abs_path(), meta["path"]), "w") as fh:
                    fh.write(repr(meta))

                p = sp.Popen([synchrophazotron_path, "-"], stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.STDOUT)
                stdout, _ = p.communicate(json.dumps(meta))

                resource = sdk2.Resource[int(stdout.strip())]
                assert resource.type == meta["type"]
                assert resource.path.name == meta["path"]
                assert resource.description == meta["description"]
                assert resource.state == ctr.State.READY
                assert resource.a == "b"
                assert resource.c == "1"
            finally:
                stop_task(cmd)
            return True

        tasks_tests.TestExecuteTask._execute_task(
            task.id, rest_su_session, client_node_id,
            120, None, {TS.EXECUTING: executing_trigger}
        )
