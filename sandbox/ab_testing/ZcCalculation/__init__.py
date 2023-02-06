# coding: utf-8
import argparse
import datetime
import json
import logging
import os
import re
import shutil
import tarfile
import tempfile
import time

import sandbox.common.types.resource as ctr
import sandbox.common.types.task as ctt

from sandbox import sdk2
from sandbox.common.errors import TaskFailure
from sandbox.common.utils import classproperty
from sandbox.projects.ab_testing.resource_types import (
    ZC_CPM_V2_YA_PACKAGE,
    ZC_RESULT,
    ZC_YA_PACKAGE,
)
from sandbox.projects.common import file_utils as fu
from sandbox.projects.common import solomon
from sandbox.projects.resource_types import OTHER_RESOURCE
from sandbox.sdk2.helpers import subprocess as sp

import zc_calculation as zc


class LastBinaryResource(sdk2.parameters.Resource):
    state = (ctr.State.READY,)
    required = True

    @classproperty
    def default_value(cls):
        return sdk2.Resource.find(
            cls.resource_type,
            state=cls.state
        ).first()


class CpcCalculation(sdk2.Task):

    class Requirements(sdk2.Requirements):
        cores = 10
        ram = 65536
        disk_space = 10 * 1024

        class Caches(sdk2.Requirements.Caches):
            pass

    class Parameters(sdk2.Task.Parameters):
        kill_timeout = 3 * 24 * 60 * 60

        with sdk2.parameters.Group("Calculation parameters") as calculation_parameters:
            token = sdk2.parameters.Vault(
                "YT token",
                description="\"name\" or \"owner:name\" for extracting from Vault",
                required=True
            )

            zc_cpc_package_resource = LastBinaryResource(
                "Resource with ZC CPC binary",
                resource_type=ZC_YA_PACKAGE,
                required=True
            )

            cpc_config = sdk2.parameters.JSON(
                "ZC CPC Config",
                required=True
            )

            common_environment = sdk2.parameters.Dict(
                "Environment variables",
                required=True
            )

        with sdk2.parameters.Output():
            result = sdk2.parameters.JSON("CPC calculation result", default="{}")
            testids = sdk2.parameters.List("testids list")
            start_date = sdk2.parameters.String("Start date")
            end_date = sdk2.parameters.String("End date")

    def on_execute(self):
        """
        Main Sandbox function
        """
        logging.info("Starting CPC calculation")

        # save testids and start/end date
        self.Parameters.testids = _get_raw_testids(self.Parameters.cpc_config["exp_ids"])
        self.Parameters.start_date = self.Parameters.cpc_config["start_date"]
        self.Parameters.end_date = self.Parameters.cpc_config["end_date"]

        # run cpc
        output = self._run_cpc_calculation()
        self.Parameters.result = json.dumps(zc.parse_cpc_result(output))

    def _run_cpc_calculation(self):
        """
        Returns:
            str: returns output of cpc calculation
        """
        path_root = os.getcwd()
        path_bin = os.path.join(path_root, "bin")
        files = {
            "zc_cpc": os.path.join(path_bin, "Berkanavt/ab_testing/bin/zc"),
            "cpc_config": os.path.join(path_root, "cpc_config.json"),
            "cpc_result": os.path.join(path_root, "cpc_result.txt"),
        }

        logging.info("Download binary")
        path_tar = str(sdk2.ResourceData(self.Parameters.zc_cpc_package_resource).path)
        _download_binaries(path_bin, path_tar)

        if "mappers" in self.Parameters.cpc_config and "exp_ids" in self.Parameters.cpc_config:
            self.Parameters.cpc_config.pop("exp_ids")

        logging.info("Save CPC config")
        with open(files["cpc_config"], "w") as f:
            json.dump(self.Parameters.cpc_config, f)

        cmd = [
            files["zc_cpc"],
            "--config-json", files["cpc_config"]
        ]

        return _run_task_binaries(task=self,
                                  cmd=cmd,
                                  result_file=files["cpc_result"],
                                  result_resource_name="cpc_result")


class CpmCalculation(sdk2.Task):

    class Parameters(sdk2.Task.Parameters):
        kill_timeout = 3 * 24 * 60 * 60

        with sdk2.parameters.Group("Calculation parameters") as calculation_parameters:
            token = sdk2.parameters.Vault(
                "YT token",
                description="\"name\" or \"owner:name\" for extracting from Vault",
                required=True
            )

            zc_cpm_v2_package_resource = LastBinaryResource(
                "Resource with ZC CPM_V2 binary",
                resource_type=ZC_CPM_V2_YA_PACKAGE,
                required=True
            )

            cpm_args = sdk2.parameters.String(
                "Args for cpm binary",
                required=True
            )

            common_environment = sdk2.parameters.Dict(
                "Environment variables",
                required=True
            )

        with sdk2.parameters.Output():
            result = sdk2.parameters.JSON("CPM calculation result", default="{}")
            testids = sdk2.parameters.List("testids list")
            start_date = sdk2.parameters.String("Start date")
            end_date = sdk2.parameters.String("End date")

    def on_execute(self):
        """
        Main Sandbox function
        """
        logging.info("Starting CPM calculation")

        # save testids and start/end date
        parser = argparse.ArgumentParser()
        parser.add_argument("--range", type=lambda dates: dates.split(".."))
        parser.add_argument("--experiments", type=lambda exps: _get_raw_testids(exps.split(",")))
        args, _ = parser.parse_known_args(self.Parameters.cpm_args.split())
        self.Parameters.testids = args.experiments
        self.Parameters.start_date, self.Parameters.end_date = args.range

        # run cpm
        output = self._run_cpm_calculation()
        self.Parameters.result = json.dumps(zc.parse_cpm_result(output))

    def _run_cpm_calculation(self):
        """
        Returns:
            str: returns output of cpm calculation
        """
        path_root = os.getcwd()
        path_bin = os.path.join(path_root, "bin")
        files = {
            "zc_cpm_v2": os.path.join(
                path_bin,
                "Berkanavt/ab_testing/bin/zc_calculator_v2/bin/reach_zc_calculator"
            ),
            "cpm_result": os.path.join(path_root, "cpm_result.txt"),
            "cpm_progress": os.path.join(path_root, 'cpm_progress.txt'),
            "cpm_state": os.path.join(path_root, 'cpm_state.json'),
        }

        logging.info("Download binaries")
        path_tar = str(sdk2.ResourceData(self.Parameters.zc_cpm_v2_package_resource).path)
        _download_binaries(path_bin, path_tar)

        cmd = [files["zc_cpm_v2"]] + self.Parameters.cpm_args.split()

        return _run_task_binaries(task=self,
                                  cmd=cmd,
                                  result_file=files["cpm_result"],
                                  result_resource_name="cpm_result")


class ZcCalculation(sdk2.Task):

    class Context(sdk2.Task.Context):
        subtask_name_to_subtask_id = {}

    class Parameters(sdk2.Task.Parameters):
        kill_timeout = 3 * 24 * 60 * 60

        with sdk2.parameters.Group("Solomon parameters") as solomon_parameters:
            oauth_token_secret_id = sdk2.parameters.YavSecret(
                label="OAuth token secret id",
                default_value="sec-01fm4xssew9dq5yq82ygx9z666"
            )
            oauth_token_key = sdk2.parameters.String("OAuth token key", default_value="robot-eksperimentus.solomon.token")
            solomon_project = sdk2.parameters.String("Project", default_value="ab_zc_monitoring")
            solomon_cluster = sdk2.parameters.String("Cluster", default_value="prod")
            solomon_service = sdk2.parameters.String("Service", default_value="zc_calculation")


        with sdk2.parameters.Group("Main parameters") as main_parameters:
            token = sdk2.parameters.Vault(
                "YT token",
                description="\"name\" or \"owner:name\" for extracting from Vault",
                required=True,
                default="AB-TESTING:yt-token"
            )

            yt_pool = sdk2.parameters.String(
                "yt pool",
                required=False,
                default_value="abt-prod-ems"
            )

            yt_proxy = sdk2.parameters.String(
                "yt proxy",
                required=False,
                default_value="hahn",
            )

            calc_cpc = sdk2.parameters.Bool(
                "Calculate CPC",
                default=False
            )

            calc_cpm = sdk2.parameters.Bool(
                "Calculate CPM",
                default=False
            )

            test_result = sdk2.parameters.JSON(
                "If not empty, do nothing and return this json",
                required=False,
                default={}
            )

        with sdk2.parameters.Group("CPC parameters") as cpc_parameters:
            zc_cpc_package_resource = LastBinaryResource(
                "Resource with ZC CPC binary",
                resource_type=ZC_YA_PACKAGE,
                required=False
            )

            cpc_config = sdk2.parameters.JSON(
                "ZC CPC Config",
                required=False
            )

        with sdk2.parameters.Group("CPM parameters") as cpm_parameters:
            zc_cpm_v2_package_resource = LastBinaryResource(
                "Resource with ZC CPM_V2 binary",
                resource_type=ZC_CPM_V2_YA_PACKAGE,
                required=False
            )

            cpm_args = sdk2.parameters.String(
                "Args for cpm binary",
                required=False
            )

    def on_execute(self):
        """
        Main Sandbox function
        """
        self.events_table = "//home/abt/zc_monitoring/events_" + datetime.datetime.today().strftime('%Y%m%d')
        self.yt_token = self.Parameters.token.data()
        self.solomon_token = self.Parameters.oauth_token_secret_id.data()[self.Parameters.oauth_token_key]

        if self.Parameters.test_result:
            self._send_event("test")
            self._save_result(self.Parameters.test_result, "zc_result.json")
            return

        self._send_event("run")

        with self.memoize_stage.create_children:
            subtasks = self._run_subtasks()

            self.Context.subtask_name_to_subtask_id = {
                subtask_name: subtask.id for subtask_name, subtask in subtasks.items()
            }

            wait_statuses = [
                ctt.Status.Group.FINISH,
                ctt.Status.Group.FAIL_ON_ANY_ERROR,
                ctt.Status.Group.BREAK
            ]
            raise sdk2.WaitTask(subtasks.values(), wait_statuses, wait_all=True)

        zc_result, task_results = self._get_subtasks_results()
        self._save_result(zc_result, "zc_result.json")

        if self._has_failure_tasks(task_results):
            self._send_event("failure")
        elif not self._has_vals(zc_result):
            self._send_event("empty_result")

        self._send_event("finish")

    def _run_subtasks(self):
        subtask_name_to_task = {}

        common_environment = {
            "YT_PREFIX": "//",
            "MR_RUNTIME": "YT",
            "YT_PROXY": self.Parameters.yt_proxy,
        }
        if self.Parameters.yt_pool:
            common_environment["YT_POOL"] = self.Parameters.yt_pool

        if self.Parameters.calc_cpc:
            logging.info("Create CPC Calculation task")
            cpc_task = CpcCalculation(
                self,
                description="Child of {} for CPC Calculation".format(self.id),
                owner=self.owner,
                zc_cpc_package_resource=self.Parameters.zc_cpc_package_resource,
                cpc_config=self.Parameters.cpc_config,
                common_environment=common_environment,
                token=self.Parameters.token,
                __requirements__={"tasks_resource": self.Requirements.tasks_resource}
            )
            subtask_name_to_task["CPC"] = cpc_task

            logging.info("enqueue CPC Calculation task")
            cpc_task.enqueue()
            self._send_event("run_cpc")

        if self.Parameters.calc_cpm:
            logging.info("Create CPM Calculation task")
            cpm_task = CpmCalculation(
                self,
                description="Child of {} for CPM Calculation".format(self.id),
                owner=self.owner,
                zc_cpm_v2_package_resource=self.Parameters.zc_cpm_v2_package_resource,
                cpm_args=self.Parameters.cpm_args,
                common_environment=common_environment,
                token=self.Parameters.token,
                __requirements__={"tasks_resource": self.Requirements.tasks_resource}
            )
            subtask_name_to_task["CPM"] = cpm_task

            logging.info("enqueue CPM Calculation task")
            cpm_task.enqueue()
            self._send_event("run_cpm")

        return subtask_name_to_task

    def _get_subtasks_results(self):
        zc_result = zc.get_default_empty_zc_result()
        task_results = {}

        for subtask_name, subtask_id in self.Context.subtask_name_to_subtask_id.items():
            testids = sdk2.Task[subtask_id].Parameters.testids
            start_date = sdk2.Task[subtask_id].Parameters.start_date
            end_date = sdk2.Task[subtask_id].Parameters.end_date
            subtask_result = json.loads(sdk2.Task[subtask_id].Parameters.result)

            zc_result["task"]["testids"] = testids
            zc_result["task"]["start"] = start_date
            zc_result["task"]["finish"] = end_date
            zc_result["data"]["testids"] = testids

            zc.add_group_to_zc_result(group_result=subtask_result,
                                      group_name=subtask_name,
                                      zc_result=zc_result)

            if sdk2.Task[subtask_id].status != ctt.Status.SUCCESS:
                zc.add_empty_metric_to_the_last_group(metric_name="FAILED",
                                                      zc_result=zc_result)

            task_results[subtask_id] = sdk2.Task[subtask_id].status

        return zc_result, task_results

    def _save_result(self, zc_result, result_file):
        """
        Args:
            zc_result (dict): save this dict as json
            result_file (str): file name
        """
        path_to_result_file = os.path.join(os.getcwd(), result_file)
        logging.info("Writing result to {}.. ".format(path_to_result_file))
        with open(path_to_result_file, "w") as f:
            json.dump(zc_result, f)

        _save_file_to_resource(self, path_to_result_file, ZC_RESULT, "result")

    def _has_failure_tasks(self, task_results):
        failure_results = set(list(ctt.Status.Group.FAIL_ON_ANY_ERROR) + list(ctt.Status.Group.BREAK))
        current_results = set(task_results.values())
        return bool(failure_results.intersection(current_results))

    def _has_vals(self, j_obj):
        if isinstance(j_obj, dict):
            if "val" in j_obj:
                return True
            return self._has_vals(j_obj.values())
        if isinstance(j_obj, list):
            for o in j_obj:
                if self._has_vals(o):
                    return True
        return False

    def _send_event(self, event):
        sensors = [
            {
                "labels": {"name": event},
                "ts": int(time.time()),
                "type": "GAUGE",
                "value": 1,
            }
        ]
        self._send_to_solomon(sensors)
        # self._send_event_to_yt(event) # USEREXP-13656

    def _send_to_solomon(self, sensors):
        params = {
            "project": self.Parameters.solomon_project,
            "cluster": self.Parameters.solomon_cluster,
            "service": self.Parameters.solomon_service,
        }
        logging.info("push to Solomon: sensors %s", sensors)
        solomon.push_to_solomon_v2(self.solomon_token, params, sensors)

    def _send_event_to_yt(self, event):

        import yt.wrapper as yt
        yt_client = yt.YtClient(proxy=self.Parameters.yt_proxy, token=self.yt_token)

        if not yt_client.exists(self.events_table):
            schema = [
                {'name': 'timestamp', 'required': True, 'sort_order': 'ascending', 'type': 'int64', 'type_v3': 'int64'},
                {'name': 'task_id', 'required': True, 'type': 'int64', 'type_v3': 'int64'},
                {'name': 'event_type', 'required': True, 'type': 'string', 'type_v3': 'string'}]
            yt_client.create("table", self.events_table, attributes={
                "schema": schema,
                "dynamic": False,
                "expiration_time": int(time.time() + 365 * 24 * 60 * 60) * 1000})

        data = [{
            "timestamp": int(time.time() * 1000),
            "task_id": self.id,
            "event_type": event
        }]
        table = yt.TablePath(self.events_table, append=True)
        json_format = yt.JsonFormat(attributes={'encode_utf8': False})
        yt_client.write_table(table, data, format=json_format)


class ZcMonitoring(sdk2.Task):

    class Context(sdk2.Task.Context):
        subtask_id = None

    class Parameters(sdk2.Task.Parameters):
        kill_timeout = 3 * 24 * 60 * 60

        with sdk2.parameters.Group("Solomon parameters") as solomon_parameters:
            oauth_token_secret_id = sdk2.parameters.YavSecret(
                label="OAuth token secret id",
                default_value="sec-01fm4xssew9dq5yq82ygx9z666"
            )
            oauth_token_key = sdk2.parameters.String("OAuth token key", default_value="robot-eksperimentus.solomon.token")
            solomon_project = sdk2.parameters.String("Project", default_value="ab_flow")
            solomon_cluster = sdk2.parameters.String("Cluster", default_value="production")
            solomon_service = sdk2.parameters.String("Service", default_value="ab_zc_daily")
            solomon_ts = sdk2.parameters.Integer("Timestamp", required=False)

        with sdk2.parameters.Group("Testids parameters") as testids_parameters:
            testids = sdk2.parameters.String("Testids (comma separated)", required=True)

        with sdk2.parameters.Group("Dates parameters") as dates_parameters:
            date_start = sdk2.parameters.String("Start date (YYYYMMDD)", default_value="")
            date_end = sdk2.parameters.String("End date (YYYYMMDD)", default_value="")

    def on_execute(self):
        with self.memoize_stage.create_children:
            subtask = self._run_subtask()
            self.Context.subtask_id = subtask.id
            wait_statuses = [
                ctt.Status.Group.FINISH,
                ctt.Status.Group.FAIL_ON_ANY_ERROR,
                ctt.Status.Group.BREAK
            ]
            raise sdk2.WaitTask([subtask], wait_statuses, wait_all=True)

        resource = sdk2.Resource[ZC_RESULT.name].find(task_id=self.Context.subtask_id).first()
        data = sdk2.ResourceData(resource)
        zc_result = json.load(open(str(data.path), 'r'))

        if not self.Parameters.solomon_ts:
            ts = time.mktime(datetime.date.today().timetuple())
        else:
            ts = self.Parameters.solomon_ts

        self._send_to_solomon(zc_result, ts)

    def _run_subtask(self):
        logging.info("Create ZC Calculation task")
        cpc_config = self._get_cpc_config()
        zc_task = ZcCalculation(
            self,
            description="Child of {} for ZC Calculation".format(self.id),
            owner=self.owner,
            token="AB-TESTING:yt-token",
            yt_pool="abt-prod-ems",
            yt_proxy="hahn",
            calc_cpc=True,
            cpc_config=cpc_config,
            __requirements__={"tasks_resource": self.Requirements.tasks_resource}
        )
        logging.info("enqueue ZC Calculation task")
        zc_task.enqueue()
        return zc_task

    def _get_cpc_config(self):
        if not self.Parameters.date_start:
            date_start = datetime.datetime.strftime(datetime.date.today() - datetime.timedelta(days=5), "%Y%m%d")
        else:
            date_start = self.Parameters.date_start
        assert len(date_start) == 8

        if not self.Parameters.date_end:
            date_end = datetime.datetime.strftime(datetime.datetime.strptime(date_start, "%Y%m%d") + datetime.timedelta(days=2), "%Y%m%d")
        else:
            date_end = self.Parameters.date_end
        assert len(date_end) == 8

        testids = ["ab" + testid.strip() for testid in self.Parameters.testids.split(",")]

        return {
            "exp_ids": testids,
            "work_dir": "//home/abt/tmp",
            "start_date": date_start,
            "end_date": date_end,
            "log_type": "search",
        }

    def _send_to_solomon(self, zc_result, ts):
        """
        Args:
            zc_result (dict): send the dict to Solomon
            ts (int): timestamp to send
        """
        assert "data" in zc_result
        assert "testids" in zc_result["data"]
        assert "metrics" in zc_result["data"]

        testids = zc_result["data"]["testids"]
        metrics = zc_result["data"]["metrics"]

        sensors = []

        for metric in metrics:
            assert len(metrics[metric]) == len(testids)
            assert "val" in metrics[metric][0]
            control_value = float(metrics[metric][0]["val"])
            for counter, metric_data in enumerate(metrics[metric]):
                testid = testids[counter]
                assert "val" in metric_data
                value = float(metric_data["val"])
                sensors.append({
                    "labels": {"testid": testid, "metric": metric},
                    "value": value,
                    "ts": ts,
                })

                if counter > 0:
                    delta = value - control_value
                    sensors.append({
                        "labels": {"testid": testid, "metric": metric + "_delta"},
                        "value": delta,
                        "ts": ts,
                    })

        oauth_token = self.Parameters.oauth_token_secret_id.data()[self.Parameters.oauth_token_key]

        params = {
            "project": self.Parameters.solomon_project,
            "cluster": self.Parameters.solomon_cluster,
            "service": self.Parameters.solomon_service,
        }

        logging.info("push to Solomon: sensors %s", sensors)

        solomon.push_to_solomon_v2(oauth_token, params, sensors)


def _run_task_binaries(task, cmd, result_file, result_resource_name):
    """
    Args:
        task (sdk2.Task):
        cmd (list[str]): command to run
        result_file (str): path to result file
        result_resource_name (str): name of result resource

    Returns:
        str: output of binary
    """
    logging.info("Saving token")
    token_file = os.path.join(os.getcwd(), "token")
    with open(token_file, "w") as f:
        os.chmod(token_file, 0o600)
        f.write(task.Parameters.token.data())

    task_environment = task.Parameters.common_environment
    task_environment.update({
        "YT_TOKEN_PATH": token_file,
        "YQL_TOKEN_PATH": token_file,
        "AB_TOKEN_PATH": token_file,
        "ARCANUM_TOKEN_PATH": token_file,
        "SOLOMON_TOKEN_PATH": token_file,
    })

    try:
        output = _run_cmd(cmd, env=task_environment, stderr=sp.STDOUT)
    except sp.CalledProcessError as e:
        raise RuntimeError("command {} failed with code {} and output:\n\n{}".format(
            e.cmd, e.returncode, e.output,
        ))

    logging.info("Save binary output to {}".format(result_file))
    with open(result_file, "w") as f:
        f.write(output.decode("utf-8"))

    _save_file_to_resource(task=task,
                           path_to_file=result_file,
                           resource=OTHER_RESOURCE,
                           resource_name=result_resource_name)

    return output


def _save_file_to_resource(task, path_to_file, resource, resource_name):
    """
    Args:
        task (sdk2.Task):
        path_to_file (str): save this file to the resource
        resource (AbstractResource):
        resource_name (str):
    """
    logging.info("Creating {} resource..".format(resource_name))

    resource_data = sdk2.ResourceData(
        resource(task, resource_name, path_to_file)
    )
    resource_data.path.write_bytes(fu.read_file(path_to_file))
    resource_data.ready()

    logging.info("Resource {} created".format(resource_name))


def _run_cmd(cmd, env=None, **kwargs):
    """
    Args:
        cmd (list[str]):
        env (dict or None): environment variables
        **kwargs (dict): other args

    Returns:
        str: cmd output
    """
    logging.debug("Run cmd=%s with env=%s", cmd, env)
    return sp.check_output(cmd, env=env, **kwargs)


def _download_binaries(path_bin, path_tar):
    """
    Args:
        path_bin (str): path to binary
        path_tar (str): path to tar
    """
    logging.info("Downloading binaries to: %s", path_bin)

    logging.debug("Path to tar: %s", path_tar)

    with tarfile.open(path_tar) as tar:
        path_tmp = tempfile.mkdtemp()

        try:
            path_deb = None

            for member in tar.getmembers():
                if member.name.endswith(".deb"):
                    logging.debug("Found deb-package in tar: %s", member.name)

                    path_deb = os.path.join(path_tmp, member.name)

                    logging.debug("Extracting deb-package as: %s", path_deb)

                    tar.extract(member, path_tmp)
                    break

            if path_deb is None:
                raise TaskFailure("No deb package found in resource")

            cmd = ["dpkg", "-x", path_deb, path_bin]

            _run_cmd(cmd)
        finally:
            shutil.rmtree(path_tmp)


def _get_raw_testids(exp_lst):
    """
    Args:
        exp_list (list): list of testids with prefixies ("ab", "pcode", ...)

    Returns:
        list: list of testids without prefixies
    """

    result = []
    for exp in exp_lst:
        exp_clean = re.search(r'\d+', exp).group(0)
        result.append(exp_clean)
    return result
