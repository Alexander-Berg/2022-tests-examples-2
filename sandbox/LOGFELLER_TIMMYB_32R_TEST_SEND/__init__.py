from sandbox import sdk2

import commands
import logging
import os

############################################################################

lxc_container = 599493573
stream_log_type = 'browser-yablocker-auto-log'

############################################################################


class LogfellerTimmyb32rTestSend():
    """task which parse logbroker-import-log"""

    class Parameters(sdk2.Task.Parameters):
        _container = sdk2.parameters.Container(
            "Environment container resource",
            default_value=lxc_container,
            required=True
        )

    def _prepare_environment(self):
        os.environ["YT_TOKEN"] = self._get_yt_token()
        os.environ["YT_POOL"] = "logfeller_ultrafast"
        os.environ["YT_SPEC"] = '{"mapper": {"memory_limit": 2147483648}, "data_size_per_job": 536870912, "job_io": {"table_writer": {"max_row_weight": 134217728}}}'
        os.environ["MR_RUNTIME"] = "YT"
        os.environ["YT_PROXY"] = "hume.yt.yandex.net"
        os.environ["YT_LOG_LEVEL"] = "DEBUG"

    def on_execute(self):
        self._prepare_environment()

        logging.info('will try to exec command')
        logging.info(commands.getstatusoutput('logfeller-update-reactor-artifacts --ultrafast --log ' + stream_log_type + ' --cluster hume --token_path ./step_secret --period 5min'))
        logging.info('executed command')

############################################################################
