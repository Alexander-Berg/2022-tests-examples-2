# -*- coding: utf-8 -*-

import logging
import os
import json
import re
import requests
import xml.etree.ElementTree as ET
import psutil

from sandbox import sdk2
import sandbox.common
from sandbox.sandboxsdk import parameters as sp
from sandbox.sandboxsdk.svn import Arcadia
from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk import paths
from sandbox.sandboxsdk import process
from sandbox.sandboxsdk.errors import SandboxTaskFailureError

import sandbox.projects.release_machine.input_params as rm_params

from sandbox.projects import resource_types
from sandbox.projects.common.search.components import DefaultUpperSearchParams
from sandbox.projects.common.search import bugbanner as bb
from sandbox.projects.common.search import bugbanner2 as bb2
from sandbox.projects.common.testenv import xml_to_json
from sandbox.projects.common import decorators
from sandbox.projects.common import error_handlers as eh
from sandbox.projects.common import utils
from sandbox.projects.common import file_utils
from sandbox.projects.release_machine import rm_notify
from sandbox.projects.report.common import ApacheBundleParameter, Project
from sandbox.common.fs import chmod_for_path
from sandbox.sandboxsdk import environments

import sandbox.projects.sandbox.resources
from sandbox.projects.common import apihelpers


class ArcadiaUrl(sp.SandboxArcadiaUrlParameter):
    name = 'svn_url'
    description = 'Arcadia url for report:'
    default_value = sp.SandboxArcadiaUrlParameter.default_value + '/web/report@HEAD'


class ArcadiaUrlFrozen(object):
    name = 'svn_url_frozen'


class ProveParams(sp.SandboxStringParameter):
    name = 'prove_param'
    description = 'Additional parameters for prove:'
    default_value = (
        "--formatter YxWeb::Test::TAP::Formatter --exec 'y-local-env perl -MYxWeb::Test' -j12 -r --merge --timer"
    )


class PathToTest(sp.SandboxStringParameter):
    name = 'path_to_test'
    description = 'Path to tests:'
    default_value = './t/'


class DataRuntime(sp.ResourceSelector):
    name = 'data_runtime'
    description = 'DataRuntime'
    resource_type = resource_types.REPORT_DATA_RUNTIME


class CoverageForCommit(sp.SandboxBoolParameter):
    name = 'coverage_for_commit'
    description = 'check coverage for commit'
    default = False


class CoverageEmail(sp.SandboxBoolParameter):
    name = 'coverage_email'
    description = 'Send email to commit author if coverage error:'


class Selector(sp.SandboxSelectParameter):
    name = 'selector'
    choices = [('svn', 'svn'), ('package', 'package')]
    sub_fields = {
        'svn': [ArcadiaUrl.name, CoverageForCommit.name, CoverageEmail.name],
        'package': [DefaultUpperSearchParams.ReportCoreParameter.name]
    }
    default_value = choices[0][1]
    description = 'Get report from:'


class PerlJobs(sp.SandboxBoolParameter):
    name = 'jobs'
    description = 'Number of jobs setup automatically(overwrite prove -j):'


class CheckoutReport(sp.SandboxBoolParameter):
    name = 'checkout_report'
    description = 'Checkout report instead of using cache'
    default_value = True


class EnvAddition(sp.SandboxStringParameter):
    name = 'env_addition'
    description = 'ENV param(key1=val1 key2=val2...)'
    default_value = ''


class RtccBundle(sp.LastReleasedResource):
    name = 'rtcc_bundle'
    description = 'Config for upper'
    resource_type = resource_types.RTCC_BUNDLE


class ContainerLxc(sp.Container):
    description = 'lxc container:'

    @property
    def default_value(self):
        res = apihelpers.get_last_resource_with_attribute(
            sandbox.projects.sandbox.resources.LXC_CONTAINER,
            attribute_name='report',
            attribute_value='1',
        )
        return res.id if res else None


@rm_notify.notify2()
class TestReportUnit(bb.BugBannerTask, object):
    """
        Прогон юнит-тестов report'a.
    """

    type = 'TEST_REPORT_UNIT'

    environment = (
        environments.SvnEnvironment(),
    )

    input_parameters = [
        Selector,
        ArcadiaUrl,
        CoverageForCommit,
        CoverageEmail,
        DefaultUpperSearchParams.ReportCoreParameter,
        ApacheBundleParameter,
        DataRuntime,
        ProveParams,
        PathToTest,
        PerlJobs,
        EnvAddition,
        RtccBundle,
        ContainerLxc,
        rm_params.ReleaseNum,
        rm_params.ComponentName,
        CheckoutReport,
    ]

    execution_space = 5000

    unit_tap_folder = 'unit'
    unit_tap_convert = True
    resource_type = resource_types.TEST_REPORT_UNIT

    @staticmethod
    def is_svn(self):
        return self.ctx[Selector.name] == 'svn'

    @staticmethod
    def freeze_svn_url(self):
        if TestReportUnit.is_svn(self):
            svn_url = self.ctx[ArcadiaUrl.name]
            if not svn_url:
                raise SandboxTaskFailureError('Cannot execute task. "svn_url" parameter is not specified.')

            if ArcadiaUrlFrozen.name not in self.ctx:
                self.ctx[ArcadiaUrlFrozen.name] = Arcadia.freeze_url_revision(svn_url)

    @staticmethod
    def run_and_read(program, work_dir, timeout=600, fail_on_empty=True):
        obj = process.run_process(
            [program],
            work_dir=work_dir,
            timeout=timeout,
            shell=True,
            check=True,
            log_prefix='run_and_read',
            outputs_to_one_file=False
        )
        if fail_on_empty and not os.path.exists(obj.stdout_path) or not os.path.getsize(obj.stdout_path):
            raise SandboxTaskFailureError('File %s is empty.' % obj.stdout_path)

        f = open(obj.stdout_path, "r")
        data = f.read()
        f.close()
        return data

    @staticmethod
    def expand_resource(res_id, dest):
        """
           Притягивает ресурс res_id на машину и распаковывает его в директорию dest.
        """
        utils.sync_resource(res_id)
        resource = channel.sandbox.get_resource(res_id)
        if not resource:
            raise SandboxTaskFailureError('Cannot execute task. Can\'t find resource by id %s.' % res_id)

        logging.info(
            'resource: id=%s, file_name=%s, path=%s, attributes=%s',
            resource.id, resource.file_name, resource.path, resource.attributes
        )

        # создаем директорию для ресурса и распаковывем архив из локального ресурса
        paths.remove_path(dest)
        if os.path.isdir(resource.path):
            paths.copy_path(resource.path, dest)
        elif os.path.isfile(resource.path):
            paths.make_folder(dest, delete_content=True)
            tar_params = None
            if os.path.basename(resource.path).endswith('.tar'):
                tar_params = "-xf"
            elif os.path.basename(resource.path).endswith('.tar.gz'):
                tar_params = "-xzf"

            if tar_params:
                process.run_process(
                    ['tar -C %s --strip-components=1 %s %s' % (dest, tar_params, resource.path)],
                    shell=True, log_prefix='tar'
                )
            else:
                sp.copy_path(resource.path, dest)
        else:
            raise SandboxTaskFailureError("Can operate only with files and directories. src=%s" % resource.path)

        # выдаем права на запись, потому что в ресурсах права только на чтение
        chmod_for_path(dest, 'ug+w')

        return resource

    @staticmethod
    def get_apache(res_id, dest, env_vars=None):
        upper_res = TestReportUnit.expand_resource(res_id, dest)
        # добавить в PATH путь к y-local-env
        os.environ["PATH"] = "%s:%s" % (os.path.join(os.path.realpath(dest), "bin"), os.environ["PATH"])

        src = os.path.join(dest, '.perl.conf.1')
        link_name = '.perl.conf'

        if not env_vars:
            # .perl.conf -> apache_bundle/.perl.conf.1
            if os.path.exists(link_name):
                os.remove(link_name)
            os.symlink(src, link_name)
        else:
            # copy apache_bundle/.perl.conf.1 into .perl.conf
            # and rewrite some vars
            # YX_PID_FILE ./apache_bundle/httpd.pid
            # PID_FILE ./apache_bundle/httpd.pid
            # LOCK_FILE ./apache_bundle/accept.lock
            # YX_LOG_DIR /usr/local/www/logs

            # '^(YX_PID_FILE|...) '
            prog = re.compile('^(' + '|'.join(env_vars.keys()) + ') ')

            fread = open(src, 'r')
            fwrite = open(link_name, 'w')

            for line in fread:
                res = prog.search(line)
                if res:
                    line = res.group(0) + env_vars.pop(res.group(1)) + '\n'
                fwrite.write(line)

            for key in env_vars:
                fwrite.write("%s %s \n" % (key, env_vars[key]))

            fread.close()
            fwrite.close()

        return upper_res

    @staticmethod
    def get_upper_config(res_id, dest='upper_conf', link_prefix='conf', project='WEB', is_beta=1):
        # получить upper_conf
        TestReportUnit.expand_resource(res_id, dest)
        # создать симлинки
        # projects.ReportDataRuntimeItem.Project список доступных
        project_config = Project.upper_config[project]
        prefix = os.path.join('hamster' if is_beta else 'production', project_config, 'vla')
        paths.make_folder(link_prefix, delete_content=True)

        # создать симлинк на request.json из dest(upper_conf) в директорию link_prefix(conf)
        src = os.path.join("../", dest, prefix, 'request.json')
        link_name = os.path.join(link_prefix, 'request.json')
        os.symlink(src, link_name)

    @staticmethod
    def get_report_from_svn(ctx, svn_url, directory):
        paths.remove_path(directory)
        # no VCS cache mode
        if utils.get_or_default(ctx, CheckoutReport):
            Arcadia.checkout(svn_url, directory)
        else:
            arcadia_src_dir = Arcadia.get_arcadia_src_dir(svn_url)
            if not arcadia_src_dir:
                raise SandboxTaskFailureError('Cannot get repo for url {0}'.format(svn_url))
            logging.info("svn cache: %s", arcadia_src_dir)
            paths.copy_path(arcadia_src_dir, directory)

        # локализация
        process.run_process(
            ['REPORT_DIR=`pwd` y-local-env ./scripts/l10n/build.pl -p serp'],
            work_dir=directory, timeout=100, shell=True, check=True, log_prefix='build', outputs_to_one_file=False
        )

    @staticmethod
    def get_report(self, report_path):
        """
        This method is used from other sandbox tasks, please don't remove @staticmethod
        without refactoring of all that code.
        """
        TestReportUnit.freeze_svn_url(self)

        svn_url = ''
        report_revision = 0
        report_dir = ''

        if TestReportUnit.is_svn(self):
            svn_url = self.ctx[ArcadiaUrlFrozen.name]
            if not svn_url:
                raise SandboxTaskFailureError('Cannot execute task. "svn_url" parameter is not specified.')

            report_revision = Arcadia.parse_url(svn_url).revision
            report_dir = "%s-svn-%s" % (report_path, report_revision)
        else:
            report_dir = "%s-sandbox-%s" % (report_path, self.ctx[DefaultUpperSearchParams.ReportCoreParameter.name])

        paths.remove_path(report_path)
        # симлинк на report
        os.symlink(report_dir, report_path)

        # получить репорт из пакета либо вытянуть из svn
        if TestReportUnit.is_svn(self):
            TestReportUnit.get_report_from_svn(self.ctx, svn_url, report_dir)
        else:
            TestReportUnit.expand_resource(
                res_id=self.ctx[DefaultUpperSearchParams.ReportCoreParameter.name],
                dest=report_dir,
            )

    @staticmethod
    @decorators.retries(max_tries=3, delay=30, backoff=2)
    def download_file(path, url):
        logging.info("Downloading %s", url)
        r = requests.get(url, timeout=120)
        eh.ensure(r.content, "Downloaded zero-sized file, seems to be an error. ")
        file_utils.write_file(path, r.content)
        logging.info("Downloaded %s of %s bytes size, written to %s", url, len(r.content), path)

    @staticmethod
    def _get_last_released_resource(resource_type, attrs=None):
        if attrs is None:
            attrs = {'released': 'stable'}

        logging.info('Searching last released resource of type %s with attrs %s', resource_type, attrs)
        return sdk2.Resource.find(
            type=resource_type,
            attrs=attrs,
        ).order(-sdk2.Resource.id).first()

    def on_execute(self):
        self.add_bugbanner(bb2.Banners.Report)

        check_coverage = self.is_svn(self) and self.ctx[CoverageForCommit.name]
        apache_bundle_resource_id = self.ctx[ApacheBundleParameter.name]
        data_runtime_resource_id = self.ctx[DataRuntime.name]
        prove_param = self.ctx[ProveParams.name]
        path_to_test = self.ctx[PathToTest.name] or PathToTest.default_value
        upper_conf_id = self.ctx[RtccBundle.name]
        self.ctx['tests_type'] = 'unit'

        self.freeze_svn_url(self)

        # настроить количесво процессов в зависимости от количества ядер процессора
        if self.ctx[PerlJobs.name]:
            jobs = int(self.client_info['ncpu'])
            # количество процессов должно влазить в память, берем максимальный размер чайлда 4GB
            jobs_mem1 = int((psutil.virtual_memory().available >> 30) / 4)
            jobs_mem2 = int(int(self.client_info['physmem']) / 4294967296)
            logging.info("mem1: {} mem2: {}".format(jobs_mem1, jobs_mem2))
            if jobs_mem1 < jobs:
                jobs = jobs_mem1
            prove_param = "%s -j%s" % (prove_param, jobs)
        # не перезапускать задачу если она перешла в состояние UNKNOWN
        # self.ctx["do_not_restart"] = True

        # пути
        working_dir = self.abs_path()
        report_path = 'report'
        apache_bundle_path = 'apache_bundle'

        logging.info(
            "workind_dir=%s, report_path=%s, apache_bundle_path=%s",
            working_dir, report_path, apache_bundle_path
        )

        # получить apache_bundle
        self.get_apache(apache_bundle_resource_id, apache_bundle_path)

        # выставляем переменные окружения
        self.setup_env(apache_bundle_path)
        logging.info("env=%s", os.environ)

        # получить репорт из пакета либо вытянуть из svn
        self.get_report(self, report_path)

        # получить data.runtime
        self.get_data_runtime(data_runtime_resource_id, 'data.runtime', self.runtime_version_for_report(report_path))

        # получить upper_conf
        self.get_upper_config(upper_conf_id)

        # узнать путь к перловым программам (prove, cover, etc)
        obj = process.run_process(
            ['y-local-env perl -e \'(my $p=$ENV{PERL}) =~ s!/perl$!!; print $p\''],
            work_dir=report_path, timeout=10, shell=True, check=False, log_prefix='perl_bin', outputs_to_one_file=False
        )
        if not os.path.exists(obj.stdout_path) or not os.path.getsize(obj.stdout_path):
            raise SandboxTaskFailureError('Can not find path to perl bin directory.')
        with open(obj.stdout_path, "r") as fd:
            self.ctx["perl_bin"] = fd.read()

        # запускаем тесты
        self.run_tests(prove_param, path_to_test, report_path)

        # создаем ресурс юнит тестов
        self.make_resource()

        # проверяем покрытие
        self.compare_coverage(check_coverage, report_path)

    @staticmethod
    def runtime_version_for_report(report_path):
        '''
        находит версию данных для репорта
        '''
        js_data = json.loads(TestReportUnit.run_and_read('y-local-env perl scripts/make.pl --environment', report_path))
        return js_data.get("version_report", "unknown")

    @staticmethod
    def runtime_revision(report_path):
        '''
        находит версию данных для репорта
        '''
        prog = "y-local-env perl ./scripts/make.pl --mode revision_dataruntime"
        rv = TestReportUnit.run_and_read(prog, report_path, fail_on_empty=False).strip()
        if not rv:
            logging.error("%s return empty result" % prog)

        return rv

    def get_data_runtime(self, res_id, dest, version=None, revision=None):
        resource = channel.sandbox.get_resource(res_id)
        if not resource:
            raise SandboxTaskFailureError('Cannot execute task. Can\'t find DataRuntime resource by id %s.' % res_id)

        logging.info(
            'data_runtime_resource: id=%s, file_name=%s, path=%s, attributes=%s',
            resource.id, resource.file_name, resource.path, resource.attributes
        )

        if version:
            version = str(version)
            # r45.1 r77.HEAD trunk
            got_version = str(resource.attributes["version"])
            if version != got_version:
                raise SandboxTaskFailureError(
                    'Cannot execute task. Expect version of dataruntme:%s but got:%s.' % (version, got_version)
                )

        if revision:
            revision = str(revision)
            got_revision = str(resource.attributes["revision"])
            if revision != got_revision:
                raise SandboxTaskFailureError(
                    'Cannot execute task. Expect revision of dataruntme:%s but got:%s.' % (revision, got_revision)
                )

        resource = self.expand_resource(res_id, dest)
        return resource

    def cleanup(self):
        return

    def _run_tests(self, prove_param, path_to_test, report_path, timeout=600):
        obj = process.run_process(
            ['y-local-env perl %s %s %s' % (os.path.join(self.ctx["perl_bin"], 'prove'), prove_param, path_to_test)],
            work_dir=report_path, timeout=timeout, shell=True, check=False,
            log_prefix='unit_test', outputs_to_one_file=False
        )

        if not os.path.exists(obj.stdout_path) or not os.path.getsize(obj.stdout_path):
            raise SandboxTaskFailureError('Unit test output %s is empty.' % obj.stdout_path)

    def run_tests(self, prove_param, path_to_test, report_path, timeout=600):
        self._run_tests(prove_param, path_to_test, report_path, timeout)

    def setup_env(self, apache_bundle_path):
        working_dir = self.abs_path()
        unit_tap_folder = self.tap_arch_folder()

        paths.make_folder(unit_tap_folder, delete_content=True)
        env = {}
        if self.ctx[EnvAddition.name]:
            for part in self.ctx[EnvAddition.name].split():
                (k, v) = part.split("=", 1)
                env[k] = v

        # PERL_TEST_HARNESS_DUMP_TAP - имя директории, в которую будет записана копия TAP-а,
        # а также JUnit, если использовать форматер JUnit
        env["PERL_TEST_HARNESS_DUMP_TAP"] = os.path.join(working_dir, unit_tap_folder)

        for key, value in env.items():
            if os.environ.get(key):
                os.environ[key] = "%s:%s" % (value, os.environ[key])
            else:
                os.environ[key] = value

    def tap_arch_folder(self):
        return "%s/%s" % (self.unit_tap_folder, self.client_info['arch'])

    def compare_coverage(self, check_coverage, report_path):
        if not check_coverage:
            return

        self.freeze_svn_url(self)
        svn_url = self.ctx[ArcadiaUrlFrozen.name]
        res_path = 'coverage_error.json'
        # создаем ресурс для покрытия
        if not self.ctx.get('test_report_unit_coverage_resource_id'):
            resource = self.create_resource(
                description=self.descr,
                resource_path=res_path,
                resource_type=resource_types.TEST_REPORT_UNIT_COVERAGE_BY_COMMIT,
                arch=None,
                attributes={'arch': self.client_info['arch']}
            )
            logging.info('Create resource %s id: %s', resource_types.TEST_REPORT_UNIT_COVERAGE_BY_COMMIT, resource.id)
            self.ctx['test_report_unit_coverage_resource_id'] = resource.id

        report_dir = os.path.basename(os.path.realpath(report_path))
        prev_report_dir = "%s-svn-prev" % report_path
        report_revision = int(Arcadia.info(svn_url)['commit_revision'])
        prev_svn_url = Arcadia.replace(svn_url, revision=report_revision - 1)

        # выкачиваем из svn предыдущую версию репорта
        self.get_report_from_svn(self.ctx, prev_svn_url, prev_report_dir)
        # сравниваем покрытие двух ревизий
        error = self.coverage_dif(report_dir, prev_report_dir, report_path)
        if error:
            arc_info = Arcadia.info(svn_url)

            mail_to = '%s@yandex-team.ru' % arc_info['author']
            mail_cc = 'serp-core-tests@yandex-team.ru'
            mail_subject = 'Report unit tests - coverage errors'
            mail_body = ''
            for item in error:
                mail_body += "%s\n" % item

            mail_body += "commit author: %s\n" % arc_info['author']
            mail_body += "commit revision: %s" % arc_info['commit_revision']

            logging.info(
                "\nmail_to: %s\nmail_cc: %s\nmail_subject: %s\n\nmail_body: %s\n",
                mail_to, mail_cc, mail_subject, mail_body
            )
            if self.ctx[CoverageEmail.name]:
                channel.sandbox.send_email(
                    mail_to, mail_cc, mail_subject, mail_body, content_type='text/plain', charset='utf-8'
                )

        self.ctx['coverage_errors'] = len(error)
        f = open(res_path, 'w')
        f.write(json.dumps(error))
        f.close()

    def coverage_dif(self, report_dir, prev_report_dir, report):
        error = []
        # получить json с именами тестов для запуска и именами модулей для проверки покрытия
        obj = process.run_process(
            [
                'y-local-env %s/scripts/dev/test/find_module_for_coverage.pl --path=%s --prev_path=%s' % (
                    report, report_dir, prev_report_dir
                )
            ],
            timeout=600, shell=True, check=True, log_prefix='find_module_for_coverage.pl', outputs_to_one_file=False
        )
        if not os.path.exists(obj.stdout_path) or not os.path.getsize(obj.stdout_path):
            raise SandboxTaskFailureError("Hasn't got output %s." % obj.stdout_path)

        f = open(obj.stdout_path, "r")
        data = json.loads(f.read())
        f.close()

        # удалить YxNews
        for k in data.keys():
            for k2 in data[k].keys():
                if data[k][k2]['rel_path'].startswith('lib/YxNews/'):
                    data[k].pop(k2)

        tests = []
        modules = []
        for name in data['current']:
            item = data['current'][name]
            if not item['exists'] and not item['test']['exists']:
                continue

            if item['exists'] and item['test']['exists']:
                tests.append(item['test']['rel_path'])
                modules.append(item['rel_path'])
            elif not item['exists']:
                error.append('Can not find module %s for tests %s' % (item['rel_path'], item['test']['rel_path']))
            elif not item['test']['exists']:
                error.append(
                    'Can not find tests in the directory %s for module %s' % (
                        item['test']['rel_path'], item['rel_path']
                    )
                )

        prev_tests = []
        for name in data['prev']:
            item = data['prev'][name]
            if item['exists'] and item['test']['exists']:
                prev_tests.append(item['test']['rel_path'])

        if tests:
            os.environ.pop("PERL_TEST_HARNESS_DUMP_TAP", "")
            os.environ["NYTPROF"] = "addpid=1:stmts=0:slowops=0"
            prove_param = "--exec 'y-local-env perl -d:NYTProf -MYxWeb::Test' --merge --timer"

            path_to_test = ' '.join(tests)
            json_data = self.get_cover_json(report, report_dir, prove_param, path_to_test)

            json_data_prev = {}
            if prev_tests:
                path_to_test = ' '.join(prev_tests)
                json_data_prev = self.get_cover_json(report, prev_report_dir, prove_param, path_to_test)

            preffix = os.path.join(self.abs_path(), report)
            for filename in modules:
                abs_path = os.path.join(preffix, filename)
                if not json_data.get(abs_path):
                    error.append("Tests doesn't load file %s" % filename)
                    continue

                for criterion, value in json_data[abs_path].items():
                    percent = float(value['percent'])

                    default = {criterion: {'percent': 0}}
                    struct = json_data_prev.setdefault(abs_path, default)
                    prev_percent = float(struct[criterion]['percent'])

                    if percent < prev_percent:
                        error.append(
                            "Coverage by {0} in the file {1} was decreased. Was: {2}%. Now: {3}%.".format(
                                criterion, filename, prev_percent, percent
                            )
                        )
                    elif percent == 0:
                        error.append("Coverage in %s for %s is zero." % (filename, criterion))

        return error

    def get_cover_json(self, report, report_dir, prove_param, path_to_test):
        paths.remove_path(report)
        # симлинк на report
        os.symlink(report_dir, report)
        self._run_tests(prove_param, path_to_test, report, 3600)

        # объединяем статистику
        obj = process.run_process(
            ['y-local-env perl %s %s' % (os.path.join(self.ctx["perl_bin"], 'nytprofmerge'), 'nytprof.out.*')],
            work_dir=report, timeout=600, shell=True, check=True, log_prefix='nytprofmerge', outputs_to_one_file=False
        )
        # покрытие (json)
        obj = process.run_process(
            ['y-local-env perl scripts/dev/test/parse_nytprof.pl %s' % 'nytprof-merged.out'],
            work_dir=report, timeout=600, shell=True, check=True, log_prefix='cover_json', outputs_to_one_file=False
        )

        if not os.path.exists(obj.stdout_path) or not os.path.getsize(obj.stdout_path):
            raise SandboxTaskFailureError('Coverage output %s is empty.' % obj.stdout_path)

        f = open(obj.stdout_path, "r")
        json_data = json.loads(f.read())
        f.close()

        return json_data

    def make_resource(self):
        tar_name = "%s.tar.gz" % self.unit_tap_folder
        paths.remove_path(tar_name)
        # сжимаем директорию, потому что на данный момент есть проблемы со skynet.copier-ом.
        process.run_process([
            'tar -czf %s %s' % (tar_name, self.unit_tap_folder)
        ], shell=True, log_prefix='run_process_log')
        if not os.path.exists(tar_name) or not os.path.getsize(tar_name):
            raise SandboxTaskFailureError('Archive %s is empty.' % tar_name)

        if not self.ctx.get('test_report_unit_resource_id'):
            # для testenv-а нужна конвертация xml -> json
            if self.unit_tap_convert:
                xml_to_json.on_enqueue(self)

            # создаем ресурс
            unit_resource = self.create_resource(
                description=self.descr,
                resource_path=tar_name,
                resource_type=self.resource_type,
                arch=None,
                attributes={'arch': self.client_info['arch']}
            )
            logging.info('Create resource %s id: %s' % (self.resource_type, unit_resource.id))
            self.ctx['test_report_unit_resource_id'] = unit_resource.id

        if self.unit_tap_convert:
            xml_to_json.find_and_convert(self, self.unit_tap_folder)

    def on_success(self):
        super(TestReportUnit, self).on_success()
        self.add_startrack_comment(0)

    def on_failure(self):
        super(TestReportUnit, self).on_failure()
        self.add_startrack_comment(1)

    def add_startrack_comment(self, is_bad):
        if self.ctx.get('searel'):
            comment = self.make_message_for_st(is_bad)
            st = sandbox.common.rest.Client(
                base_url='https://st-api.yandex-team.ru/v2',
                auth=self.get_vault_data("REPORT_CORE", "zomb-prj-10-st-oauth")
            )
            st.issues[self.ctx['searel']].comments.create(text=comment)

    def make_message_for_st(self, is_bad):
        if is_bad < 0 or is_bad > 1:
            is_bad = 1

        message = [
            "((%s Unit tests)) are !!(green)OK!!%s",
            u"((%s Unit tests)) are !!(red)**FAILED**!! ((%s отчёт))"
        ]
        link = self.get_common_log_view()["url"]
        if is_bad:
            return message[is_bad] % (self.http_url(), link)

        is_bad = 1
        test_path = 'unit_test.out.txt'
        with open(self.log_path(test_path), 'r') as f:
            data = f.read()
            if data:
                root = ET.fromstring(data)
                attr = root.attrib
                if root.tag == 'testsuites' and int(attr['failures']) == 0 and int(attr['errors']) == 0:
                    link = ''
                    is_bad = 0
                else:
                    link = os.path.join(os.path.dirname(self.get_common_log_view()["url"]), test_path)

        return message[is_bad] % (self.http_url(), link)


__Task__ = TestReportUnit
