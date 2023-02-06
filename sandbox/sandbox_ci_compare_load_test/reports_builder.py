# -*- coding: utf-8 -*-

from sandbox.projects.sandbox_ci.sandbox_ci_compare_load_test.reports_creator import HermioneReportsCreator
from sandbox.projects.sandbox_ci.sandbox_ci_compare_load_test.reports_creator import CpuReportsCreator
from sandbox.projects.sandbox_ci.sandbox_ci_compare_load_test.reports_creator import ContainersReportsCreator


class ReportsBuilder(object):
    def __init__(self, task):
        self._reports = {}
        self._reports_creators = [
            HermioneReportsCreator(),
            CpuReportsCreator(task),
            ContainersReportsCreator(task)
        ]

    @property
    def reports(self):
        return self._reports

    def add_reports(self, subtask):
        for creator in self._reports_creators:
            reports_key = '<h3>{} {}</h3>'.format(subtask.get_task_key(), creator.title)
            report = creator.get_report(subtask)
            self._add_report(report, reports_key)

    def _add_report(self, report, reports_key):
        if self._reports.get(reports_key):
            self._reports[reports_key] += report
        else:
            self._reports[reports_key] = report
