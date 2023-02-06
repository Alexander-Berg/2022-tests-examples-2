# -*- coding: utf-8 -*-

import os
import json

from sandbox.projects import resource_types
from sandbox.sandboxsdk.paths import copy_path
from sandbox.sandboxsdk.process import run_process
from sandbox.sandboxsdk.errors import SandboxTaskFailureError

import sandbox.common.types.client as ctc

import sandbox.projects.TestReportUnit as Unit


class TestReportUnitCoverage(Unit.TestReportUnit):
    """
        Покрытие тестами report-а.
    """

    type = 'TEST_REPORT_UNIT_COVERAGE'

    client_tags = ctc.Tag.LINUX_PRECISE
    execution_space = 20000

    input_parameters = []
    for item in Unit.TestReportUnit.input_parameters:
        if item.name in (Unit.ProveParams.name, Unit.PerlJobs.name, Unit.CoverageForCommit.name, Unit.CoverageEmail.name):
            continue
        input_parameters.append(item)

    unit_tap_folder = 'coverage'
    unit_tap_convert = False
    resource_type = resource_types.TEST_REPORT_UNIT_COVERAGE
    min_coverage = 10

    def on_execute(self):
        self.ctx[Unit.ProveParams.name] = "--exec 'y-local-env perl -d:NYTProf -MYxWeb::Test' -v -r --merge --timer"
        self.ctx[Unit.PerlJobs.name] = True
        self.ctx[Unit.CoverageForCommit.name] = False
        self.ctx[Unit.CoverageEmail.name] = False
        super(TestReportUnitCoverage, self).on_execute()

        sub_coverage = self.ctx['coverage'].get('subroutine', 0)
        if sub_coverage < self.min_coverage:
            raise SandboxTaskFailureError('The very small sub coverage %s (need >= %s).' % (sub_coverage, self.min_coverage))

    def setup_env(self, apache_bundle_path):
        super(TestReportUnitCoverage, self).setup_env(apache_bundle_path)

        os.environ.pop("PERL_TEST_HARNESS_DUMP_TAP", "")
        # os.environ["NYTPROF"]  = "addpid=1:calls=0:stmts=0:slowops=0:file=%s" % os.path.join(self.abs_path(), self.tap_arch_folder(), 'nytprof.out')
        os.environ["NYTPROF"] = "addpid=1:slowops=0:sigexit=1"

    def run_tests(self, prove_param, path_to_test, report_path, timeout=600):
        # увеличить таймаут, выполнение тестов с включенным Devel::CoverNYTProf занимает ~ 10 минут
        super(TestReportUnitCoverage, self).run_tests(prove_param, path_to_test, report_path, timeout=7200)

        cover_db = os.path.join(self.abs_path(), self.tap_arch_folder())
        # объединяем статистику
        run_process(['y-local-env perl %s %s' % (os.path.join(self.ctx["perl_bin"], 'nytprofmerge'), 'nytprof.out.*')],
                          work_dir=report_path, timeout=3600, shell=True, check=True, log_prefix='nytprofmerge', outputs_to_one_file=False)
        # удалить файлы nytprof.out.*
        run_process(['rm nytprof.out.*'],
                          work_dir=report_path, timeout=600, shell=True, check=True, log_prefix='remove')
        # создаем статистику по покрытию (html)
        run_process(['y-local-env perl %s -f %s' % (os.path.join(self.ctx["perl_bin"], 'nytprofhtml'), 'nytprof-merged.out')],
                          work_dir=report_path, timeout=3600, shell=True, check=True, log_prefix='nytprofhtml', outputs_to_one_file=False)
        # покрытие (json)
        obj = run_process(['y-local-env perl scripts/dev/test/parse_nytprof.pl %s' % 'nytprof-merged.out'],
                          work_dir=report_path, timeout=600, shell=True, check=True, log_prefix='cover_json', outputs_to_one_file=False)
        if not os.path.exists(obj.stdout_path) or not os.path.getsize(obj.stdout_path):
            raise SandboxTaskFailureError('Coverage output %s is empty.' % obj.stdout_path)

        f = open(obj.stdout_path, 'r')
        json_data = json.loads(f.read())
        f.close()

        # перемещаем nytprof-merged.out и директорию nytprof в директорию ресурса
        run_process(['mv nytprof* %s' % cover_db],
                    work_dir=report_path, timeout=600, shell=True, check=True, log_prefix='remove')
        copy_path(obj.stdout_path, os.path.join(cover_db, 'nytprof.json'))

        self.ctx['coverage'] = {}
        for name in json_data['Total']:
            self.ctx['coverage'][name] = float(json_data['Total'][name]["percent"])


__Task__ = TestReportUnitCoverage
