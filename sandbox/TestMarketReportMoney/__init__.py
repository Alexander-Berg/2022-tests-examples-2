# -*- coding: utf-8 -*-
import os
import os.path

from sandbox.common.types.misc import RamDriveType
from sandbox.projects import resource_types
from sandbox.projects.common import dolbilka
from sandbox.projects.common import file_utils as fu
from sandbox.sandboxsdk.channel import channel

import sandbox.projects.common.search.components.market_report as mr
import calc_money


MARKET_REPORT_SHOW_LOG_FILENAME = 'market-show-tskv.log'


class TestMarketReportMoney(mr.MarketReportFiringTask):

    type = 'TEST_MARKET_REPORT_MONEY'
    input_parameters = mr.REPORT_MONEY_PARAMS

    def on_enqueue(self):
        mr.MarketReportFiringTask.on_enqueue(self)
        if self.ctx[mr.RamdriveEnabled.name]:
            self.ramdrive = self.RamDrive(
                RamDriveType.TMPFS,
                self.ctx[mr.RamdriveSizeParameter.name] * 1024,
                None)
        self.ctx['out_result_resource_id'] = self.create_resource(
            self.descr, 'money_stats.json',
            resource_types.TEST_MARKET_REPORT_MONEY_RESULT_JSON).id

    def on_execute(self):
        plan = self.sync_resource(self.ctx[mr.Plan.name])
        report = self._get_prepare_report()

        self._set_up_dolbilka_ctx_params()
        d_executor = dolbilka.DolbilkaExecutor()
        d_executor.run_sessions(plan, report)

        # Extract money metrics from report show-log file
        show_log_path = os.path.join(self.report_logs_folder, MARKET_REPORT_SHOW_LOG_FILENAME)
        with open(show_log_path) as f:
            stats = calc_money.calc_money_metrics_from_show_log(f)
        self.ctx['money_records_analyzed_count'] = stats[0]
        self.ctx['money_stats'] = stats[1]
        self._write_results_to_resource(stats)

    def _set_up_dolbilka_ctx_params(self):
        # Долбилка будет задавать запрос и ждать, пока он выполнится
        self.ctx[dolbilka.DolbilkaExecutorMode.name] = dolbilka.DolbilkaExecutorMode.FINGER_MODE
        # Одновременное число запросов (см. выше — долбилка ждет завершеня каждого)
        self.ctx[dolbilka.DolbilkaMaximumSimultaneousRequests.name] = 5
        self.ctx[dolbilka.DolbilkaSessionsCount.name] = 1
        self.ctx[dolbilka.DolbilkaExecutorRequestsLimit.name] = self._get_requests_limit(desired_request_limits=50000)

    def _write_results_to_resource(self, stats):
        out_json_resource = channel.sandbox.get_resource(self.ctx['out_result_resource_id'])
        fu.json_dump(out_json_resource.path, stats, indent=4)


__Task__ = TestMarketReportMoney
