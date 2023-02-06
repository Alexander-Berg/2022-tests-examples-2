# -*- coding: utf-8 -*-

import sandbox.projects.TestReportUnit as Unit

import sandbox.common.types.client as ctc


class TestReportUnitCoverageByCommit(Unit.TestReportUnit):
    """
        Показывает как изменилось покрытие модулей, которые изменились после коммита.
    """

    type = 'TEST_REPORT_UNIT_COVERAGE_BY_COMMIT'

    execution_space = 5500
    input_parameters = []
    client_tags = ctc.Tag.LINUX_PRECISE

    for item in Unit.TestReportUnit.input_parameters:
        if item.name in (Unit.Selector.name, Unit.DefaultUpperSearchParams.ReportCoreParameter.name, Unit.ProveParams.name, Unit.PathToTest.name, Unit.PerlJobs.name, Unit.CoverageForCommit.name):
            continue
        input_parameters.append(item)

    def on_execute(self):
        self.ctx[Unit.Selector.name] = 'svn'
        self.ctx[Unit.ProveParams.name] = ''
        self.ctx[Unit.PathToTest.name] = ''
        self.ctx[Unit.PerlJobs.name] = ''
        self.ctx[Unit.CoverageForCommit.name] = True

        super(TestReportUnitCoverageByCommit, self).on_execute()

    def run_tests(self, prove_param, path_to_test, report_path, timeout=600):
        return

    def make_resource(self):
        return


__Task__ = TestReportUnitCoverageByCommit
