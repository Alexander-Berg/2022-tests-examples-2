# -*- coding: utf-8 -*-

from sandbox.projects.sandbox_ci.sandbox_ci_compare_load_test.reports_creator.base import BaseReportsCreator


class CpuReportsCreator(BaseReportsCreator):
    def __init__(self, task):
        super(CpuReportsCreator, self).__init__(task)
        self._reports_base_url = 'https://grafana.qatools.yandex-team.ru/d/qEPP-Kekk/server-health'

    @property
    def title(self):
        return 'grafana'

    def get_report(self):
        task = self._task

        hosts = task.quota.get_hosts(task.grid_url, 10)
        reports_links = map(lambda h: self._format_link(self._reports_base_url, h, {'var-servername': h.replace('.', '_')}), hosts)

        return self._format_reports_info('CPU usage', reports_links)
