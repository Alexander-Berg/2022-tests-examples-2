# -*- coding: utf-8 -*-

import logging
from sandbox.projects.TestFrontMetricsLogs.modules.tools import Tools


class Scenario:
    def __init__(self, env, yt_prefix, yuid, scenario_id, yt_client_config):
        self.env = env
        self.yt_prefix = yt_prefix
        self.yuid = yuid
        self.scenario_id = scenario_id
        self.cpc_clicks_table = "click_external.log"
        self.cpa_clicks_table = "click_cpa_all_external.log"
        self.front_access_table = "front_access.log"
        self.report_access_table = "report_access.log"
        self.report_show_table = "report_show_tskv_external.log"
        self.scarab_table_suffix = "_scarab"

        from yt.wrapper import YtClient
        self.yt_cli = YtClient(proxy=yt_client_config["proxy"]["url"], token=yt_client_config["token"])

    def FilterEmptyTables(self):
        logging.info("=== FilterEmptyTables starting for yuid: {} ...".format(self.yuid))
        for table in (self.cpc_clicks_table, self.cpa_clicks_table, self.front_access_table, self.report_access_table, self.report_show_table):
            logging.debug("checking table {} for yuid={}: init".format(table, self.yuid))
            table_exists = True
            try:
                logging.debug("checking table {} for yuid={}: let's try!".format(table, self.yuid))
                row_count = int(self.yt_cli.get("{}/@row_count".format(self._GetRelativeTablePath(table)), format="json"))
                logging.debug("checking table {} for yuid={}: try success!".format(table, self.yuid))
                if row_count == 0:
                    logging.debug("checking table {} for yuid={}: row_count=0".format(table, self.yuid))
                    table_exists = False
                else:
                    logging.debug("checking table {} for yuid={}: row_count != 0!!!!! row_count='{}' with type '{}'".format(table, self.yuid, row_count, str(type(row_count))))

            except Exception:
                logging.debug("checking table {} for yuid={}: try failed, exception=(".format(table, self.yuid))
                table_exists = False

            logging.debug("checking table {} for yuid={}: table_exist={}".format(table, self.yuid, table_exists))
            if table_exists:
                logging.debug("checking table {} for yuid={}: continue?".format(table, self.yuid))
                continue

            logging.debug("checking table {} for yuid={}: no continue!".format(table, self.yuid))
            logging.warning("=== FILTERING: Fail to find or row_count=0 for table: {}. Ignore it in future.".format(
                self._GetRelativeTablePath(table)))
            if table == self.cpc_clicks_table:
                self.cpc_clicks_table = None
            if table == self.cpa_clicks_table:
                self.cpa_clicks_table = None
            if table == self.front_access_table:
                self.front_access_table = None
            if table == self.report_access_table:
                self.report_access_table = None
            if table == self.report_show_table:
                self.report_show_table = None
            tables_state = "-".join([str(x) for x in (self.cpc_clicks_table, self.cpa_clicks_table, self.front_access_table, self.report_access_table, self.report_show_table)])
            logging.debug("checking table {} for yuid={}: tables state: {}".format(table, self.yuid, tables_state))

        logging.info("=== FilterEmptyTables for yuid: {} DONE.".format(self.yuid))

    def ConvertToScarab(self, cpc_converter, cpa_converter, front_access_converter, report_access_converter, report_show_converter):
        logging.info("=== ConvertToScarab starting for yuid: {} ...".format(self.yuid))
        for table_name, converter in (
                (self.cpc_clicks_table, cpc_converter),
                (self.cpa_clicks_table, cpa_converter),
                (self.front_access_table, front_access_converter),
                (self.report_access_table, report_access_converter),
                (self.report_show_table, report_show_converter)):
            if not table_name:
                continue
            Tools.RunProcess([
                converter,
                "--input", self._GetStrictTablePath(table_name),
                "--output", "{}{}".format(self._GetStrictTablePath(table_name), self.scarab_table_suffix)  # _GetScarabTable() нельзя, поскольку strict path
            ], self.env)
        logging.info("=== ConvertToScarab for yuid: {} DONE.".format(self.yuid))

    def BuildScarabSessions(self, server, scarab_session_builder, user_type_resolver, geohelper):
        logging.info("=== Build Scarab Sessions starting  for yuid: {}...".format(self.yuid))
        for table_name in self._GetAllNonEmptyTables():
            self._BuildScarabSessionsForTable(table_name, server, scarab_session_builder, user_type_resolver, geohelper)
        logging.info("=== Build Scarab Sessions for yuid: {} DONE.".format(self.yuid))

    def BuildOldStackSessions(self, session_builder, user_type_resolver, geohelper,
                              blockstat_dict, sessions_beta_list, sessions_direct_pageids,
                              sessions_direct_resourceno_dict, sessions_direct_ads_decriptions, date):
        logging.info("=== Build Old Stack Sessions starting for yuid: {} ...".format(self.yuid))
        for table in self._GetAllNonEmptyTables():
            strict_table_path = self._GetStrictTablePath(table)
            binaryEnv = self.env
            binaryEnv.update({"YT_PREFIX": "{}{}/".format(self.yt_prefix, self.yuid)})
            try:
                Tools.RunProcess([
                    session_builder,
                    "-server", "hahn",
                    "-user_type_resolver", user_type_resolver,
                    "-geohelper", geohelper,
                    "-create", self._GetBuilderForTable(table),
                    "-date", date.strftime("%Y-%m-%d"),
                    "-strict_source_path", self._GetStrictTablePath(table),
                    "-bsdict", blockstat_dict,
                    "-beta_list", sessions_beta_list,
                    "-direct_pageids", sessions_direct_pageids,
                    "-direct_resourceno_dict", sessions_direct_resourceno_dict,
                    "-direct_ads_descriptions", sessions_direct_ads_decriptions,
                    "-v",
                    "-dont_separate_yandex_staff",
                ], binaryEnv)
                logging.info("old stack session ready for table: " + strict_table_path)
            except Exception as e:
                logging.error("fail to build old stack session for table: " + strict_table_path + "\n" + e.message)

        logging.info("=== Build Old Stack Sessions for yuid: {} DONE.".format(self.yuid))
        return

    def MergeAndSortSessions(self, date):
        logging.info("=== MergeAndSortSession starting for yuid: {} ...".format(self.yuid))
        src_all_sessions = []
        src_error_sessions = []

        dst_all_session = self._GetRelativeTablePath(self._GetResultAllSessionTable())
        dst_error_session = self._GetRelativeTablePath(self._GetResultErrorSessionTable())

        self.yt_cli.create("map_node", self._GetRelativeTablePath(self._GetResultSessionFolder()), recursive=True,
                           ignore_existing=True)
        for table in self._GetScarabNonEmptyTables():
            src_all_sessions = src_all_sessions + [self._GetRelativeTablePath(self._GetScarabSessionTable(table, x)) for
                                                   x in ("external", "internal", "staff", "skips")]
            src_error_sessions.append(self._GetRelativeTablePath(self._GetScarabSessionTable(table, "errors")))

        for table in self._GetAllNonEmptyTables():
            src_all_sessions.append(self._GetRelativeTablePath(self._GetOldStackSessionTable(table, date)))
            src_error_sessions.append(self._GetRelativeTablePath(self._GetOldStackSessionTable(table, date)))

        for srcs, dst in ((src_all_sessions, dst_all_session), (src_error_sessions, dst_error_session)):
            if len(srcs) > 0:
                logging.info("starting for merge to '{}' the following tables:\n".format(dst) + "\n".join(srcs))
                self.yt_cli.run_merge(srcs, dst)
                logging.info("merge done.")
                self.yt_cli.run_sort(dst_all_session, sort_by=["key", "subkey"])
                logging.info("sorted done.")
            else:
                logging.warning("No {} sessions for yuid='{}'".format(dst, self.yuid))
        logging.info("=== MergeAndSortSession for yuid: {} DONE.".format(self.yuid))

    def BuildMetrics(self, stat_collector_path, stat_fetcher_path, geodata_path, blockstat_path, browser_path,
                     paths_json, date):
        logging.info("=== BuildMetrics starting for yuid: {} ...".format(self.yuid))
        collector_config_path = 'sc_conf.txt'
        with open(collector_config_path, 'wt') as f:
            f.write('[task]\nname=\nexperiment=0')

        collector_output = "{}{}/collector_tmp_output".format(self.yt_prefix, self.yuid)
        Tools.RunStatCollector(
            self.env,
            collector_output,
            self._GetStrictTablePath(self._GetResultAllSessionTable()),
            stat_collector_path,
            collector_config_path,
            geodata_path,
            blockstat_path,
            browser_path,
            paths_json,
            date
        )

        metric_file_path = "{}-metrics.txt".format(self.scenario_id)
        Tools.RunStatFetcher(
            self.env,
            metric_file_path,
            collector_output,
            stat_fetcher_path,
            collector_config_path,
            date
        )
        logging.info("=== BuildMetrics for yuid: {} DONE.".format(self.yuid))
        return metric_file_path

    def _GetAllNonEmptyTables(self):
        return [x for x in (
            self.cpc_clicks_table, self.cpa_clicks_table, self.front_access_table, self.report_access_table,
            self.report_show_table) if x]

    def _GetScarabNonEmptyTables(self):
        return self._GetAllNonEmptyTables()

    def _GetResultAllSessionTable(self):
        return "{}/all_session".format(self._GetResultSessionFolder())

    def _GetResultErrorSessionTable(self):
        return "{}/error_session".format(self._GetResultSessionFolder())

    def _GetResultSessionFolder(self):
        return "result_sessions"

    def _GetBuilderForTable(self, table):
        tablename_to_builder_map = {
            self.cpc_clicks_table: "market_clicks_log",
            self.cpa_clicks_table: "market-cpa-clicks-log",
            self.front_access_table: "market_access_log",
            self.report_access_table: "market_main_report_log",
            self.report_show_table: "market_shows_log",
        }
        return tablename_to_builder_map[table]

    def _GetOldStackSessionTable(self, table, date):
        tablename_to_session_folder_map = {
            self.cpc_clicks_table: "market-clicks-log",
            self.cpa_clicks_table: "market-cpa-clicks-log",
            self.front_access_table: "market-access-log",
            self.report_access_table: "market-main-report-log",
            self.report_show_table: "market-shows-log",
        }
        return "user_sessions/build/logs/{}/1d/{}/raw/sessions".format(
            tablename_to_session_folder_map[table],
            date.strftime("%Y-%m-%d")
        )

    def _BuildScarabSessionsForTable(self, table_name, server, scarab_session_builder_path, user_type_resolver_path,
                                     geohelper_path):
        Tools.RunProcess([
            scarab_session_builder_path,
            "-server", server,
            "-user-type-resolver", user_type_resolver_path,
            "-geo-helper", geohelper_path,
            "-input", self._GetStrictTablePath(self._GetScarabTable(table_name)),
            "-external-users", self._GetStrictTablePath(self._GetScarabSessionTable(table_name, "external")),
            "-internal-servers", self._GetStrictTablePath(self._GetScarabSessionTable(table_name, "internal")),
            "-staff-users", self._GetStrictTablePath(self._GetScarabSessionTable(table_name, "staff")),
            "-skips", self._GetStrictTablePath(self._GetScarabSessionTable(table_name, "skips")),
            "-errors", self._GetStrictTablePath(self._GetScarabSessionTable(table_name, "errors")),
            "-log-name", self._GetStrictTablePath(self._GetScarabSessionTable(table_name, "log"))
        ], self.env)

    def _GetScarabTable(self, table_name):
        return "{}{}".format(table_name, self.scarab_table_suffix)

    def _GetScarabSessionTable(self, table_name, session_type):
        return "{}{}_{}".format(table_name, self.scarab_table_suffix, session_type)

    def _GetRelativeTablePath(self, table):
        return "{}{}/{}".format(self.yt_prefix, self.yuid, table)

    def _GetStrictTablePath(self, table_name):
        return "{}{}/{}".format(self.yt_prefix, self.yuid, table_name)
