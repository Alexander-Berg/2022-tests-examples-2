import os
import sys
import json
import time
import random
import shutil
import subprocess as sp

import yaml
import pytest
import requests

import common.rest
import common.config
import common.types.task as ctt
import common.types.resource as ctr

import devbox.mapping
import devbox.bootstrap
from yasandbox.database import mapping
import yasandbox.api.json.batch


@pytest.fixture(scope="session")
def rest_session_prod():
    return common.rest.Client(common.rest.Client.DEFAULT_BASE_URL)


@pytest.fixture()
def imported_entities_collections():
    for model in (devbox.mapping.ImportedResource, devbox.mapping.ImportedTask):
        model.drop_collection()


@pytest.mark.skip(reason="Flaky")  # TODO: SANDBOX-6451
@pytest.mark.devbox
class TestCTL(object):
    @staticmethod
    def _run_ctl(sandbox_dir, tests_dir, *cmd_args, **kws):
        sandbox_exe = os.path.join(sandbox_dir, "devbox", "ctl_impl.py")
        env = os.environ.copy()
        env["PYTHONPATH"] = ':'.join(["/skynet", sandbox_dir])
        logpath = os.path.join(tests_dir, "logs", "devbox.log")

        cmd = [sys.executable, sandbox_exe] + map(str, cmd_args)
        runtime_dir = kws.get("runtime", tests_dir)
        if runtime_dir:  # use config from runtime_dir only, ignore any other one
            cmd += ["--runtime", runtime_dir]
            if runtime_dir != tests_dir:
                for key in ("SANDBOX_CONFIG", "SANDBOX_WEB_CONFIG"):
                    env.pop(key, None)

        with open(logpath, "a") as log:
            log.write("> executing command: {}\n".format(" ".join(cmd)))
            log.write("> env:\n")
            log.writelines(("> {}={}\n".format(variable, env[variable]) for variable in sorted(env)))
            log.flush()
            return_code = sp.Popen(cmd, env=env, stdout=log, stderr=log).wait()
            log.write("\n")
            if return_code:
                raise RuntimeError("Command exit code: {} (see {} for details)".format(return_code, logpath))

    @staticmethod
    def _load_config(sandbox_dir):
        base, override = (
            os.path.join(sandbox_dir, "etc", conf_file)
            for conf_file in (".settings.yaml", "settings.yaml")
        )
        with open(base, "r") as base_cfg, open(override, "r") as override_cfg:
            return common.config.Registry.query(
                data=yaml.load(override_cfg),
                base=yaml.load(base_cfg)
            )

    @pytest.mark.usefixtures("server", "task_controller", "imported_entities_collections")
    def test__add_resource(self, sandbox_dir, tests_dir, rest_session, rest_session_prod):
        sandbox_archives = rest_session_prod.resource.read(
            type="SANDBOX_ARCHIVE", state="READY", limit=1, order="-time.created",
            attrs=json.dumps({"type": "server-tests"}),
        )
        assert len(sandbox_archives["items"])

        prod_res_id = sandbox_archives["items"][0]["id"]
        res = rest_session_prod.resource[prod_res_id][:]

        self._run_ctl(sandbox_dir, tests_dir, "add_resource", "--id", prod_res_id)
        tids = mapping.Task.objects().scalar("id")
        assert len(tids) == 1, "Only one task is expected"

        def local_archives():
            return rest_session.resource.read(
                task_id=tids[0],
                type="SANDBOX_ARCHIVE",
                status=ctr.State.READY,
                attrs={"type": res["attributes"]["type"]},
                limit=10
            )["items"]

        first_response = local_archives()
        assert len(first_response) > 0, ("Expect at least one resource", first_response)
        assert res["skynet_id"] in [local_res["skynet_id"] for local_res in first_response], (res, first_response)

        self._run_ctl(sandbox_dir, tests_dir, "add_resource", "--id", prod_res_id)
        second_response = local_archives()
        assert len(second_response) == len(first_response)
        assert len(mapping.Task.objects().scalar("id")) == len(tids)

    @pytest.mark.usefixtures("server", "task_controller", "imported_entities_collections")
    def test__add_resource_preserving_id(self, sandbox_dir, tests_dir, rest_session, rest_session_prod):
        sandbox_archives = rest_session_prod.resource.read(
            type="SANDBOX_ARCHIVE", state="READY", limit=1, order="-time.created",
            attrs=json.dumps({"type": "server-tests"}),
        )
        assert len(sandbox_archives["items"])

        prod_res_id = sandbox_archives["items"][0]["id"]
        res = rest_session_prod.resource[prod_res_id][:]

        self._run_ctl(sandbox_dir, tests_dir, "add_resource", "--id", prod_res_id, "--preserve-id")
        tids = mapping.Task.objects().scalar("id")
        assert len(tids) == 1, "Only one task is expected"

        def local_archives():
            return rest_session.resource.read(
                task_id=tids[0],
                type="SANDBOX_ARCHIVE",
                status=ctr.State.READY,
                attrs={"type": res["attributes"]["type"]},
                limit=10
            )["items"]

        first_response = local_archives()
        assert len(first_response) > 0, ("Expect at least one resource", first_response)
        assert res["skynet_id"] in [local_res["skynet_id"] for local_res in first_response], (res, first_response)
        assert res["id"] in [local_res["id"] for local_res in first_response], (res, first_response)

        self._run_ctl(sandbox_dir, tests_dir, "add_resource", "--id", prod_res_id, "--preserve-id")
        second_response = local_archives()
        assert len(second_response) == len(first_response)
        assert len(mapping.Task.objects().scalar("id")) == len(tids)

    @pytest.mark.usefixtures("server", "task_controller", "imported_entities_collections")
    def test__repeated_cloning(self, sandbox_dir, tests_dir, test_task_2, rest_su_session, rest_session_prod):
        """
        :type sandbox_dir: str
        :type tests_dir: str
        :type test_task_2: projects.sandbox.test_task_2.TestTask2
        :type rest_su_session: common.rest.Client
        :type rest_session_prod: common.rest.Client
        """
        res_type = test_task_2.Parameters.dependent_resource.resource_type
        resources = rest_session_prod.resource.read(type=res_type, state=ctr.State.READY, limit=3)["items"]
        container_type = str(test_task_2.Parameters._container.resource_type)
        container_res = rest_session_prod.resource.read(
            type=container_type, state=ctr.State.READY, limit=1
        )["items"][0]
        assert resources, "No resources of type {} found in production".format(res_type)

        resource_ids = map(lambda _: _["id"], resources)
        task_id = rest_session_prod.task(
            type=test_task_2.type,
            custom_fields=[
                {
                    "name": test_task_2.Parameters.dependent_resource.name,
                    "value": random.choice(resource_ids),
                },
                {
                    "name": test_task_2.Parameters.dependent_resources.name,
                    "value": resource_ids,
                },
                {
                    "name": test_task_2.Parameters._container.name,
                    "value": container_res["id"]
                }
            ]
        )["id"]
        task_ids = map(lambda _: _["task"]["id"], resources) + [task_id]

        def check_all_objects_are_synced(delete_resources=False):
            local_tasks_ids = set(devbox.mapping.ImportedTask.objects(original_id__in=task_ids).scalar("local_id"))
            local_resources_ids = set(
                devbox.mapping.ImportedResource.objects(original_id__in=resource_ids).scalar("local_id")
            )

            assert len(local_tasks_ids) == len(set(task_ids))
            assert len(local_resources_ids) == len(set(resource_ids))
            for tid in local_tasks_ids:
                assert rest_su_session.task[tid][:]["status"] != ctt.Status.DELETED
            for rid in local_resources_ids:
                assert rest_su_session.resource[rid][:]["state"] == ctr.State.READY

            cid = mapping.Resource.objects(type=container_type).scalar("id").first()
            original_container_id = devbox.mapping.ImportedResource.objects(local_id=cid).scalar("original_id").first()
            assert original_container_id == container_res["id"]

            if delete_resources:
                reply = rest_su_session.batch.resources["delete"].update(list(local_resources_ids))
                assert all(_["status"] == yasandbox.api.json.batch.BatchResult.Status.SUCCESS for _ in reply)
                for rid in local_resources_ids:
                    assert rest_su_session.resource[rid][:]["state"] == ctr.State.DELETED

        # after this, local Sandbox database should contain all dependent resources and tasks they were produced by
        self._run_ctl(sandbox_dir, tests_dir, "clone_task", "--id", task_id)
        check_all_objects_are_synced(delete_resources=True)

        # this should re-sync removed resources
        self._run_ctl(sandbox_dir, tests_dir, "clone_task", "--id", task_id)
        check_all_objects_are_synced()

    @pytest.mark.usefixtures("imported_entities_collections")
    def test__setup(self, request, sandbox_copy_dir, tests_dir, sandbox_tasks_dir, host, devbox_port, mongo_uri):
        runtime_dir = os.path.join(os.path.dirname(sandbox_copy_dir), "runtime_data")
        os.mkdir(runtime_dir)
        bootstrap_environment = devbox.bootstrap.BootEnvironment(runtime_dir, sandbox_copy_dir)
        bootstrap_environment.prepare_serviceapi()

        self._run_ctl(
            sandbox_copy_dir, tests_dir, "setup", "-p", devbox_port, "--mongo-uri", mongo_uri,
            runtime=runtime_dir
        )

        keyfile_path = self._load_config(sandbox_copy_dir)["server"]["encryption_key"]
        assert len(common.utils.read_settings_value_from_file(keyfile_path, binary=True)) == 32

        def teardown():
            self._run_ctl(sandbox_copy_dir, tests_dir, "stop_server", runtime=runtime_dir)

        request.addfinalizer(teardown)

        self._run_ctl(sandbox_copy_dir, tests_dir, "start_server", runtime=runtime_dir)
        for _ in xrange(100):
            try:
                r = requests.get("http://{}:{}/{}".format(host, devbox_port, "http_check"))
                assert r.status_code == requests.codes.OK
            except requests.ConnectionError:
                time.sleep(.1)

    def test__config_modification(self, sandbox_dir, tests_dir, tmpdir):
        def config_has_value(config_path, key, value):
            with open(config_path, "rb") as f:
                config_dict = yaml.load(f)
            path = key.split(".")
            return reduce(lambda d, k: d[k], path, config_dict) == value

        config = os.path.join(tmpdir, "settings.yaml")
        shutil.copy(os.path.join(tests_dir, "etc", "settings.yaml"), config)

        for k, v in (
            ("top-key", "top-value"),
            ("this.id", "custom-id")
        ):
            self._run_ctl(sandbox_dir, tests_dir, "set", "--config", config, "--key", k, "--value", v)
            assert config_has_value(config, k, v)

        for k, v in (
            ("ab.so.lu.te", "non-sen-se"),
            ("client.tags", "LXC")
        ):
            with pytest.raises(RuntimeError):
                self._run_ctl(sandbox_dir, tests_dir, "set", "--config", config, "--key", k, "--value", v)
