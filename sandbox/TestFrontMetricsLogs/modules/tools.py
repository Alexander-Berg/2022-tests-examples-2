# -*- coding: utf-8 -*-

import re
import json
import logging
import urllib2
# import subprocess

from sandbox import sdk2
from sandbox.sandboxsdk.svn import Arcadia
from sandbox.sandboxsdk.copy import RemoteCopy
from sandbox.sandboxsdk.process import run_process

from sandbox.projects import resource_types

# from sandbox.common.types.misc import NotExists


class Tools:
    @staticmethod
    def RunProcess(cmd, env, input=None, output=None, shell=None):
        # process = run_process(cmd,
        #                       wait=True,
        #                       outs_to_pipe=True,
        #                       check=False,
        #                       stdin=subprocess.PIPE if input else None,
        #                       stdout=subprocess.PIPE if output else None,
        #                       shell=False if shell is None else shell,
        #                       environment=env)
        cmdStr = " ".join([str(x) for x in cmd])
        cmdStr = "{} > error.log 2>&1".format(cmdStr)
        try:
            run_process('{}'.format(cmdStr), shell=True)
        except:
            errors = open("error.log").readlines()
            logging.info("=== LAST EXECUTION COMMAND '{}' ERRORS ... ===".format(cmdStr))
            logging.info(",".join(errors))

    @staticmethod
    def RunLogfeller(env, source_path, logfeller_path, parser_name, stream_log_type, stream_ident, config_path, out_path):
        run_process('cat {} | {} --parser {} --stream-log-type {} --stream-ident {} --splitter line-break --configs {} | sed "s/$/;/" > {}'.format(
            source_path, logfeller_path, parser_name, stream_log_type, stream_ident, config_path, out_path
        ), shell=True)
        # cmd = [
        #     "cat", source_path, "|",
        #     logfeller_path,
        #     "--stream-ident", stream_ident,
        #     "--stream-log-type", stream_log_type,
        #     "--parser", parser,
        #     "--splitter", "line-break",
        #     "--configs", config_path,
        #     ">", out_path
        # ]
        # Tools.RunProcess(cmd, env, shell=True)

    @staticmethod
    def RunStatCollector(env, outNode, inTable, binPath, configPath, geodataPath, blockstatPath, browserPath,
                         pathesPath, date):
        tmpPathesPath = pathesPath + ".tmp"

        with open(pathesPath) as f:
            pathes = json.load(f)

        for k in pathes.keys():
            pathes[k] = {"yt": {"path": [k + "_not_exists_path"]}}

        pathes["user_sessions_market"]["yt"]["path"] = [inTable]

        with open(tmpPathesPath, "w") as f:
            json.dump(pathes, f)

        Tools.RunProcess([
            binPath,
            "-s", "hahn",
            "-c", configPath,
            "-t", date.strftime("%Y%m%d"),
            "-g", geodataPath,
            "-d", blockstatPath,
            "-u", browserPath,
            "-o", outNode,
            "-y", tmpPathesPath,
            "-soft"
        ], env)

    @staticmethod
    def RunStatFetcher(env, outFile, inNode, binPath, configPath, date):
        Tools.RunProcess([
            binPath,
            "-s", "hahn",
            "-c", configPath,
            "-clean",
            "-json",
            "-t", date.strftime("%Y%m%d"),
            "-T", date.strftime("%Y%m%d"),
            "-g", "24",
            "-r", outFile,
            "-dir", inNode,
            "-d"
        ], env)

    @staticmethod
    def GetLogsFromMachines(yuids, reportUrl="msh02et.market.yandex.net"):
        logging.info("=== GetLogsFromMachines Starting ... ===")
        logging.info("yuids: " + ", ".join(yuids))

        class LogsFromMachines:
            def __init__(self, yuid_list, report_access_logs, show_log, click_log):
                self.YUIDS_LIST = yuid_list
                self.REPORT_ACCESS_LOGS = report_access_logs  # to logfeller process only
                self.SHOW_LOG = show_log  # to logfeller process only
                self.CLICK_LOG = click_log  # logfeller & mstat process

        def _AskLog(host, logPath, yuids):
            filterPattern = "\|".join(yuids)
            providerUrl = \
                "http://{}:3131/cgi-bin/file_content_receiver.py?file_path={}&last_lines_count=10000000&filter_pattern={}" \
                    .format(host, logPath, filterPattern)
            logging.info("url to ask log: {}".format(providerUrl))
            nonEmptyLogEntries = filter(bool, urllib2.urlopen(providerUrl).read().split('\n'))
            return nonEmptyLogEntries

        def _AskClickLog(yuids):
            providerUrl = "http://clickd01ht.market.yandex.net:3131/cgi-bin/file_content_receiver.py?file_path=/var/log/clickdaemon2/redir2.log&last_lines_count=1000000&filter_pattern={}"\
                .format("\|".join([str(y) for y in yuids]))
            logging.info("url to ask log: {}".format(providerUrl))
            filteredEntries = urllib2.urlopen(providerUrl).read().decode('utf-8').split('\n')
            logging.info("CLICK LOG COUNTING")
            logging.info(len(filteredEntries))
            return filteredEntries

        def GetReportAccessLogs(report_host, yuids):
            logs = _AskLog(report_host, "/var/log/search/market-access.log", yuids)
            return logs

        def GetReportShowTskvLogs(report_host, yuids):
            logs = _AskLog(report_host, "/var/log/search/market-show-tskv.log", yuids)
            return logs

        def GetClickLog(yuids):
            logs = _AskClickLog(yuids)
            return logs

        logging.info("backend host: " + reportUrl)
        if not yuids:
            raise ValueError('Empty yuids value passed')

        logging.info("=== GetLogsFromMachines Done ... ===")

        return LogsFromMachines(
            yuids,
            GetReportAccessLogs(reportUrl, yuids),
            GetReportShowTskvLogs(reportUrl, yuids),
            GetClickLog(yuids)
        )

    @staticmethod
    def GetYUIDScenarioLogs(task_id):
        response = urllib2.urlopen("https://proxy.sandbox.yandex-team.ru/last/TASK_LOGS?task_id={}".format(task_id),
                                   timeout=5)
        log_resource_id = re.findall('.*<a href="/(\d{6,20})/">(\d{6,20})</a>.*', response.read())[0][0]

        logging.info("hermione log resource id: {}".format(log_resource_id))

        scenario_url = "https://proxy.sandbox.yandex-team.ru/{}/uid_scenario.log".format(log_resource_id)
        logging.info("link: {}".format(scenario_url))
        uid_scenario = urllib2.urlopen(scenario_url, timeout=5).read()
        yuid_scenario_json = json.loads(uid_scenario)
        return yuid_scenario_json

    @staticmethod
    def FileNameFromPath(table_path):
        return table_path.split("/")[-1]

    class ReceiveResource:
        def __init__(self, env):
            self.received_binary = {}
            self.GEOHELPER = self._RemoteCopy('rsync://veles02/Berkanavt/geodata/geohelper')
            self.USER_TYPE_RESOLVER = self._RemoteCopy('rsync://veles02/Berkanavt/geodata/user_type_resolver')
            from projects.geobase.Geodata5BinStable import resource as gbr
            self.GEODATA = self.GetBinaryByType(gbr.GEODATA5BIN_STABLE)
            self.CREATE_SCARAB_SESSIONS = self._RemoteCopy(
                'rsync://veles02/Berkanavt/sessions/bin/create_scarab_sessions')
            self.CREATE_SESSIONS = self._RemoteCopy('rsync://veles02/Berkanavt/sessions/bin/create_sessions')
            self.STAT_COLLECTOR = self._RemoteCopy('rsync://veles/Berkanavt/ab_testing/bin/stat_collector')
            self.STAT_FETCHER = self._RemoteCopy('rsync://veles/Berkanavt/ab_testing/bin/stat_fetcher')
            self.MARKET_CLICK2SCARAB = self._RemoteCopy('rsync://veles02/Berkanavt/sessions/bin/market_clicks2scarab')
            self.MARKET_CPA_CLICK2SCARAB = self._RemoteCopy(
                'rsync://veles02/Berkanavt/sessions/bin/market_cpa_clicks2scarab')
            self.MARKET_FRONT_ACCESS2SCARAB = self._RemoteCopy(
                'rsync://veles02/Berkanavt/sessions/bin/market_access2scarab')
            self.MARKET_REPORT_ACCESS2SCARAB = self._RemoteCopy(
                'rsync://veles02/Berkanavt/sessions/bin/market_main_report2scarab')
            self.MARKET_REPORT_SHOW2SCARAB = self._RemoteCopy(
                'rsync://veles02/Berkanavt/sessions/bin/market_shows2scarab')

            self.PATHS_JSON = './paths.json'
            Arcadia.export('arcadia:/arc/trunk/arcadia/quality/ab_testing/paths_to_tables_lib/paths.json',
                           self.PATHS_JSON)

            self.BROWSER_XML = self.GetBinaryByType(resource_types.UATRAITS_BROWSER_XML)
            self.BLOCKSTAT_DICT = self._RemoteCopy('rsync://veles02/Berkanavt/statdata/blockstat.dict')
            self.BETA_LIST_RSRS = self._RemoteCopy('rsync://veles02/Berkanavt/quality_data/beta_list.txt')
            self.DIRECT_PAGEIDS_RSRS = self._RemoteCopy('rsync://veles02/Berkanavt/statdata/direct_pageids')
            self.DIRECT_RESOURCENO_DICT_RSRS = self._RemoteCopy(
                'rsync://veles02/Berkanavt/statdata/direct_resourceno_dict')
            self.DIRECT_ADS_DESCRIPTIONS_RSRS = self._RemoteCopy(
                'rsync://veles02/Berkanavt/statdata/direct_ads_descriptions')
            self.LOGFELLER_STDIN_PARSER = self.GetBinaryById(384329430)
            self.LOGFELLER_CONF_PATH = "./parser_configs"
            Arcadia.export('arcadia:/arc/trunk/arcadia/logfeller/configs/parsers', self.LOGFELLER_CONF_PATH)

        def GetBinaryById(self, resource_id):
            resource = sdk2.Resource[resource_id]
            resource_path = str(sdk2.ResourceData(resource).path.resolve())
            return resource_path

        def GetBinaryByType(self, resource_type, release=False, attrs=None):
            query_attrs = None
            if release:
                query_attrs = {"released": "stable"}
            if attrs is not None:
                query_attrs.update(attrs)
            binkey = str(resource_type) + str(release)
            if binkey in self.received_binary.keys():
                logging.info("resource will be taken fron cache:\n {}".format(binkey))
                resource_path = self.received_binary[binkey]
                logging.info(resource_type.__class__.__name__ + " path: " + resource_path)
                return resource_path

            if query_attrs is not None:
                resource = sdk2.Resource.find(resource_type, attrs=query_attrs).first()
            else:
                resource = sdk2.Resource.find(resource_type).first()

            logging.info(resource_type.__class__.__name__ + " resource: " + str(resource))
            resource_path = str(sdk2.ResourceData(resource).path.resolve())
            logging.info(resource_type.__class__.__name__ + " path: " + resource_path)
            self.received_binary[binkey] = resource_path
            return resource_path

        def _RemoteCopy(self, src):
            synced_path = "./{}".format(Tools.FileNameFromPath(src))
            RemoteCopy(src, synced_path)
            logging.info("saved: {} -> {}".format(src, synced_path))
            return synced_path
