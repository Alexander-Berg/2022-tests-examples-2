# -*- coding: utf-8 -*-

from sandbox.projects.sandbox_ci.sandbox_ci_compare_load_test.reports_creator import BaseReportsCreator


class HermioneReportsCreator(BaseReportsCreator):
    @property
    def title(self):
        return 'tests'

    def get_report(self, test_subtask):
        return test_subtask.get_tests_reports()
