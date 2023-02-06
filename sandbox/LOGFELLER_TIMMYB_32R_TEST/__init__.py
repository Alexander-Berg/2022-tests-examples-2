from sandbox.projects.logfeller.common.environment import LogFellerEnvironment
from sandbox.projects.logfeller.common.task import LogFellerTask

import commands
import logging
import os

############################################################################


class LogfellerTimmyb32rTest(LogFellerTask):
    """task which parse logbroker-import-log"""

    def _get_parser_command(self):
        binary_path = LogFellerEnvironment.PARSER_PATH
        options = [
            "--yt-proxy %s" % "hume.yt.yandex.net",
            "--stream-ident %s" % "browser",
            "--stream-log-type %s" % "browser-yablocker-auto-log",
            "--chunk-splitter %s" % "line-break",
            "--parser %s" % "test-browser-yablocker-auto-log",
            "--record-formatter %s" % "native",
            "--resources %s" % "yt",
            "--input-chain-path %s" % "//home/logfeller/staging-area/browser/browser-yablocker-auto-log",
            "--output-chain-path %s" % "//home/logfeller/logs/browser-yablocker-auto-log/stream/5min",
            "--part-time-period  %d" % 300,
            "--part-close-timeout %d" % 300,
            "--dynamic-allocation",
            "--close-gaps",
            "--set-log-schema"
        ]
        return binary_path + " " + " ".join(options)

    def _prepare_environment(self):
        os.environ["YT_TOKEN"] = self._get_yt_token()
        os.environ["YT_POOL"] = "logfeller_ultrafast"
        os.environ["YT_SPEC"] = '{"mapper": {"memory_limit": 2147483648}, "data_size_per_job": 536870912, "job_io": {"table_writer": {"max_row_weight": 134217728}}}'
        os.environ["MR_RUNTIME"] = "YT"
        os.environ["YT_PROXY"] = "hume.yt.yandex.net"
        os.environ["YT_LOG_LEVEL"] = "DEBUG"

    def on_execute(self):
        self._prepare_environment()

        logging.info("logfeller parsing start")
        logging.info("timmyb32r output: " + self._get_parser_command())
        logging.info(commands.getstatusoutput(self._get_parser_command()))

        # from sandbox import sandboxsdk
        # import sys
        # sys.path.append(sandboxsdk.svn.Arcadia.get_arcadia_src_dir("arcadia:/arc/trunk/arcadia/logfeller/python/logfeller/infra/step/"))
        # from client import StepClient

        # logging.info('will try to send event')
        # sc = StepClient('step.sandbox.yandex-team.ru', self._get_step_token())
        # logging.info(sc.send_event('timmyb32r_logfeller_send_event_after_logfeller_parser', {'parameter1': 'value1'}))
        # logging.info('sent event')

############################################################################
