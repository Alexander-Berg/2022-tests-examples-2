# -*- coding: utf-8 -*-

import os
import logging

from time import sleep, time
from pathlib2 import Path
from datetime import datetime
from multiprocessing import Manager, Process

# from projects.TestFrontMetricsLogs.modules import MetricComparator
from sandbox.projects.TestFrontMetricsLogs.modules import Tools
from sandbox.projects.TestFrontMetricsLogs.modules import Scenario

from sandbox import sdk2
from sandbox import sandboxsdk
import sandbox.common.types.task as ctt

# import sandbox.common.types.notification as CommonTypesNotification

HERMIONE_TASK = 'SANDBOX_CI_MARKET_HERMIONE'


class MarketFrontMetricsReport(sdk2.Resource):
    # __default_attribute__ = sdk2.parameters.String
    releasers = ["guest", "MARKET", "sildtm"]
    release_subscribers = ["sildtm"]
    releasable = False


class MarketFrontMetricsOutput(sdk2.Resource):
    # __default_attribute__ = sdk2.parameters.String
    releasers = ["guest", "MARKET", "sildtm"]
    release_subscribers = ["sildtm"]
    releasable = True


class TestFrontMetricsLogs(sdk2.Task):
    env = dict(os.environ)
    yt_host = "hahn.yt.yandex.net"
    yt_prefix = "//tmp/front_metrics/"
    yuid_to_scenario_map_file_name = "click_generation.log"
    front_logs_dir = "//logs/market-testing-access-log/stream/5min"
    BIN_DICT = {}
    received_binary = {}
    resources = None
    last_child_task_id = None
    REPORT_BACKEND = "msh02et.market.yandex.net"

    class Requirements(sdk2.Task.Requirements):
        environments = (
            sandboxsdk.environments.PipEnvironment('yandex-yt'),
            sandboxsdk.environments.PipEnvironment('yandex-yt-yson-bindings-skynet'),
        )

    class Parameters(sdk2.Task.Parameters):
        is_test = sdk2.parameters.Bool("Is test running?")

    def on_execute(self):
        # self.HermioneTaskExecution()  # also set self.Context.last_subtask_*
        import yt.wrapper as yt_client
        self.resources = Tools.ReceiveResource(self.env)

        # class HermioneExecutionData:
        #     def __init__(self, start, end, yuid_to_scenario):
        #         self.start = start
        #         self.end = end
        #         self.yuid_to_scenario = yuid_to_scenario

        # hermioneExecutionData = HermioneExecutionData(
        #     self.Context.last_subtask_start_time,
        #     self.Context.last_subtask_end_time,
        #     Tools.GetYUIDScenarioLogs(self.Context.last_subtask_id)
        # )
        # logsFromMachines = Tools.GetLogsFromMachines(hermioneExecutionData.yuid_to_scenario.keys(), self.REPORT_BACKEND)

        yt_client.update_config(self.GetYtClientConfig())
        self.SetYTEnvironment()

        # reportAccessLogf, reportShowLogf, clickAllLogf = self.RunLogfellerTransform(logsFromMachines)

        # logging.info("LOGFELLER ACCESS")
        # logging.info("\n".join(reportAccessLogf))
        # logging.info("LOGFELLER SHOWS")
        # logging.info("\n".join(reportShowLogf))
        # logging.info("LOGFELLER CLICKS")
        # logging.info("\n".join(clickAllLogf))
        # logging.info("LOGFELLER LOGS END!")

        current_date = datetime.strptime("2017-12-19", "%Y-%m-%d")  # datetime.now() # TODO
        #
        # self._UploadLogsToYt(yt_client, reportAccessLogf, reportShowLogf, clickAllLogf, hermioneExecutionData)
        scenarios = self._UploadLogsToYt(yt_client)
        # scenarios = self._UploadLogsToYt(yt_client, reportAccessLogf, reportShowLogf, clickAllLogf, hermioneExecutionData)
        #
        metrics_accumulator = Manager().dict()
        processPool = []
        for sc in scenarios:
            processPool.append(Process(target=self.ProcessScenario, args=(sc, current_date, metrics_accumulator)))
            processPool[-1].start()
        #
        for p in processPool:
            p.join()

        metrics_archive = "metrics_output.tar.gz"
        if not metrics_accumulator:
            raise RuntimeError("Not metrics were build for actual logs")
        Tools.RunProcess(["tar", "-czvf", metrics_archive] + metrics_accumulator.values(), self.env)

        self.CreateResource(metrics_archive, MarketFrontMetricsOutput)

        # released_metrics_path = self.resources.GetBinaryByType(MarketFrontMetricsOutput, release=True)
        # new_metrics_path = self.resources.GetBinaryByType(MarketFrontMetricsOutput, release=False)

        # report_file = "front_metric_report.html"
        # comparator = MetricComparator(
        #     released_metrics_path,
        #     new_metrics_path,
        #     report_file,
        #     hermioneExecutionData["yuid_to_scenario"]
        # )
        # comparator.Compare()

#         self.CreateResource(report_file, MarketFrontMetricsReport)
#         subject = "[FRONT_METRICS] success"
#         body = """
# Task url: https://sandbox.yandex-team.ru/task/{}/view
#                """.format(self.id)
#         if not comparator.MetricsAreEquals():
#             subject = "[FRONT_METRICS] failed"
#         self.Context.email_notification_id = self.server.notification(
#             subject=subject,
#             body=body,
#             recipients=["sildtm"],
#             transport=CommonTypesNotification.Transport.EMAIL,
#             urgent=False
#         )["id"]

    def RunLogfellerTransform(self, logsFromMachines):
        logging.info("=== Starting Logfeller Transform ... ===")
        argumentsMap = {"report_access": {"parser_name": "market-main-report-log",
                                          "stream_log_type": "market-main-report-log",
                                          "ident": "market-search",
                                          },
                        "report_show": {"parser_name": "market-new-shows-log",
                                        "stream_log_type": "market-shows-log",
                                        "ident": "market-search",
                                        },
                        "clicks": {"parser_name": "redir-log",
                                   "stream_log_type": "empty",  # эти поля ни на что не влияют
                                   "ident": "empty",   # эти поля ни на что не влияют
                                   },
                        }
        input_path = "input.txt"
        output_path = "output.txt"
        logsAfterLogfeller = {}
        for k, v in argumentsMap.items():
            with open("input.txt", "w") as input:
                if k == "report_access":
                    content = logsFromMachines.REPORT_ACCESS_LOGS
                elif k == "report_show":
                    content = logsFromMachines.SHOW_LOG
                elif k == "clicks":
                    content = logsFromMachines.CLICK_LOG
                else:
                    logging.info("UNKNOWN LOG TYPE")
                    continue
                logging.info("LOG TYPE = {} START".format(k))
                for line in content:
                    if len(line.strip()):
                        input.write(line + "\n")
                logging.info("LOG TYPE = {} DONE".format(k))
            Tools.RunLogfeller(self.env,
                               input_path,
                               self.resources.LOGFELLER_STDIN_PARSER,
                               v["parser_name"],
                               v["stream_log_type"],
                               v["ident"],
                               self.resources.LOGFELLER_CONF_PATH,
                               output_path
                               )
            logsAfterLogfeller[k] = open(output_path, "r").readlines()
        logging.info("=== End Logfeller Transform ... ===")

        return logsAfterLogfeller["report_access"], logsAfterLogfeller["report_show"], logsAfterLogfeller["clicks"]

    def HermioneTaskExecution(self):
        self.Context.last_subtask_start_time = self.Context.last_subtask_start_time or time()

        with self.memoize_stage.hermione_task_step:
            subtask = self.CreateAndRunMarketHermioneTask()
            self.Context.last_subtask_id = subtask.id
            raise sdk2.WaitTask([subtask], ctt.Status.Group.FINISH, wait_all=True)

        self.Context.last_subtask_end_time = time()
        logging.info("Subtask '{}' done.".format(HERMIONE_TASK))

    def CreateAndRunMarketHermioneTask(self):
        FRONT_HOST = "15092.market-exp-testing.yandex.ru"
        logging.info("Start execution of MarketHermione task")
        task_class = sdk2.Task[HERMIONE_TASK]
        subtask = task_class(task_class.current,
                             description="Run Market Hermione tests for task #%s (TEST_FRONT_METRICS_LOGS)" % self.id,
                             owner=self.owner,
                             # priority=self.priority,
                             project_git_base_ref="AUTOTESTMARKET-6384",
                             project_git_base_commit="",
                             project_git_merge_ref="",
                             project_git_merge_commit="",

                             project_github_owner="market",
                             project_github_repo="MarketNode",

                             project_build_context="testing",
                             build_platform="",

                             reuse_dependencies_cache=False,
                             reuse_artifacts_cache=False,
                             reuse_subtasks_cache=False,
                             reuse_task_cache=False,

                             webhook_urls=[],

                             related_task=0,

                             logging_paths={"MarketNode/spec/hermione/logs/uid_scenario.log": ""},

                             report_github_statuses=True,
                             project_github_commit="",
                             wait_tasks=[],
                             environ={
                                 "BACKEND_HOST": self.REPORT_BACKEND + ":17051",
                                 "hermione-suite-manager_case_filter": '{"issue": "AUTOTESTMARKET-6384"}'
                             },
                             scripts_git_url="ssh://git@github.yandex-team.ru/search-interfaces/ci.git",
                             scripts_git_ref="master",
                             statface_host="stat.yandex-team.ru",
                             stop_outdated_tasks=False,
                             base_url="https://" + FRONT_HOST,
                             build_artifacts_resources=408074912,
                             )
        subtask.enqueue()
        return subtask

    def ProcessScenario(self, scenario, current_date, metrics_accumulator):
        scenario.FilterEmptyTables()
        scenario.ConvertToScarab(self.resources.MARKET_CLICK2SCARAB,
                                 self.resources.MARKET_CPA_CLICK2SCARAB,
                                 self.resources.MARKET_FRONT_ACCESS2SCARAB,
                                 self.resources.MARKET_REPORT_ACCESS2SCARAB,
                                 self.resources.MARKET_REPORT_SHOW2SCARAB)

        scenario.BuildScarabSessions(self.yt_host,
                                     self.resources.CREATE_SCARAB_SESSIONS,
                                     self.resources.USER_TYPE_RESOLVER,
                                     self.resources.GEOHELPER)

        scenario.BuildOldStackSessions(self.resources.CREATE_SESSIONS,
                                       self.resources.USER_TYPE_RESOLVER,
                                       self.resources.GEOHELPER,
                                       self.resources.BLOCKSTAT_DICT,
                                       self.resources.BETA_LIST_RSRS,
                                       self.resources.DIRECT_PAGEIDS_RSRS,
                                       self.resources.DIRECT_RESOURCENO_DICT_RSRS,
                                       self.resources.DIRECT_ADS_DESCRIPTIONS_RSRS,
                                       current_date)

        scenario.MergeAndSortSessions(current_date)

        metric_file_path = scenario.BuildMetrics(self.resources.STAT_COLLECTOR,
                                                 self.resources.STAT_FETCHER,
                                                 self.resources.GEODATA,
                                                 self.resources.BLOCKSTAT_DICT,
                                                 self.resources.BROWSER_XML,
                                                 self.resources.PATHS_JSON,
                                                 current_date)

        metrics_accumulator[scenario.yuid] = metric_file_path

    def CreateResource(self, file_path, ResourceType):
        resource_data = sdk2.ResourceData(ResourceType(
            self, "", "was generated by TEST_FRONT_METRICS_LOGS", ttl=30
        ))
        resource_data.path.write_bytes(Path(file_path).read_bytes())
        resource_data.ready()

    def _UploadLogsToYt(self, yt_client):  # , accessLogsLogf, showLogsLogf, clickLogsLogf, hermioneExecutionData):
        # logging.info("UploadLogsToYt starting ...")
        # yuids = [str(x) for x in hermioneExecutionData.yuid_to_scenario.keys()]
        scenarios = []

        scenarios.append(Scenario(self.env, self.yt_prefix, "2213079481465198878", "pmanokhin_custom_scenario", self.GetYtClientConfig()))

        # for yuid in []:
        #     click_path = yuid + "/click_after_logfeller_all"
        #     yt_client.create("map_node", yuid, recursive=True, ignore_existing=True)
        #     yt_client.create("map_node", click_path, recursive=True, ignore_existing=True)
        #
        #     logs_for_yuid = filter(lambda x: yuid in x, accessLogsLogf)
        #     yt_client.write_table(yuid + "/access_logs_after_logfeller", logs_for_yuid, format="yson", raw=True, force_create=True)
        #
        #     logs_for_yuid = filter(lambda x: yuid in x, showLogsLogf)
        #     yt_client.write_table(yuid + "/show_logs_after_logfeller", logs_for_yuid, format="yson", raw=True, force_create=True)
        #
        #     logs_for_yuid = filter(lambda x: yuid in x, clickLogsLogf)
        #     yt_client.write_table(click_path + "/click_logs_after_logfeller", logs_for_yuid, format="yson", raw=True, force_create=True)
        #     logging.info("===== https://yt.yandex-team.ru/hahn/#page=navigation&path=//tmp/front_metrics/" + yuid + " DONE=====")
        #     scenarios.append(Scenario(self.env, self.yt_prefix, yuid, hermioneExecutionData.yuid_to_scenario[yuid], self.GetYtClientConfig()))

        # self._WriteFrontLogs(yt_client, hermioneExecutionData.yuid_to_scenario, hermioneExecutionData.start, hermioneExecutionData.end)

        # logging.info("UploadLogsToYt done.")
        return scenarios

    def _SetYtTableFormat(self, yt_client, table_path):
        yt_client.set(table_path + "/@_format", '''
                                    {
                                        "$attributes":
                                        {
                                            "escape_carriage_return": true,
                                            "has_subkey": true,
                                            "key_column_names": [],
                                            "subkey_column_names": []
                                        },
                                        "$value": "yamred_dsv"
                                    }
                                    ''', format="json")

    def _WriteFrontLogs(self, yt_client, yuid_to_scenario_map, start_time, end_time):
        logging.info("Receive front logs from yt 5-min tables ...")
        dst_table_name = "front_access.log"
        logs = []
        front_log_tables = self._GetTablesForTime(start_time, end_time)
        logging.info("Waiting for the following tables: {}".format(", ".join(front_log_tables)))
        for src_table_path in front_log_tables:
            self._WaitForTableAppear(yt_client, src_table_path)
            logs += self._GetLogsForYUIDs(yt_client, src_table_path, yuid_to_scenario_map.keys())
        logs_for_yuid = {}
        for lg in logs:
            logs_for_yuid.setdefault(lg["yandexuid"], []).append(lg)
        for yuid, logs in logs_for_yuid.items():
            table_path = "{}/{}".format(yuid, dst_table_name)
            yt_client.write_table(table_path, logs)
            self._SetYtTableFormat(yt_client, table_path)
        logging.info("Receive front logs done.")

    def _WaitForTableAppear(self, yt_client, table_path):
        logging.info("Wait for table: {}".format(table_path))
        wait_count = 180
        wait_interval = 10  # in second
        current_iteration = 0
        while current_iteration <= wait_count:
            current_iteration += 1
            logging.info("wait iteration: {}/{} ({} seconds each)".format(current_iteration, wait_count, wait_interval))
            if yt_client.exists(table_path):
                return
            sleep(wait_interval)
        raise RuntimeError(
            "The following table has not appear in {} minutes: {}".format(wait_count * wait_interval / 60, table_path)
        )

    def _GetLogsForYUIDs(self, yt_client, table_path, yuids):
        logs = []
        table_iterator = yt_client.read_table(table_path)
        for row in table_iterator:
            if row.get("yandexuid", None) in [str(x) for x in yuids]:
                logs.append(row)
        return logs

    def _GetTablesForTime(self, start_time, end_time):
        start_time = int(start_time)
        end_time = int(end_time)
        start_interval = start_time - (start_time % (5 * 60))
        end_interval = (end_time + 60 * 5) - ((end_time + 60 * 5) % (5 * 60))
        return [
            "{}/{}".format(self.front_logs_dir, datetime.fromtimestamp(i).isoformat())
            for i in xrange(start_interval, end_interval, 5 * 60)
        ]

    def SetYTEnvironment(self):
        self.env.update({"YT_TOKEN": sdk2.Vault.data(self.owner, 'yt_token')})
        self.env.update({"YT_PREFIX": self.yt_prefix})
        self.env.update({"MR_RUNTIME": "YT"})

    def GetYtClientConfig(self):
        return {
            "proxy": {"url": "hahn"},
            "token": sdk2.Vault.data(self.owner, 'yt_token'),
            "prefix": self.yt_prefix
        }
