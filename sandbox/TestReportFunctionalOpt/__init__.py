# -*- coding: utf-8 -*-

import six
import json
import logging
import os
import re
import tempfile
import socket
import requests
import time

from contextlib import closing

import sandbox.common.fs

from sandbox import sdk2

from sandbox.common.types.client import Tag
from sandbox.common import errors

from sandbox.sandboxsdk import environments
from sandbox.sandboxsdk.svn import Arcadia
from sandbox.sandboxsdk import paths
from sandbox.sandboxsdk import process
from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk import parameters as sp

import sandbox.projects.release_machine.input_params as rm_params
import sandbox.projects.TestReportUnit as Unit

from sandbox.projects.common.search.components import DefaultUpperSearchParams
from sandbox.projects.common.testenv import xml_to_json
from sandbox.projects.common import error_handlers as eh
from sandbox.projects.common import utils
from sandbox.projects.common import file_utils as fu
from sandbox.projects.common import string
from sandbox.projects.common import network
from sandbox.projects.common import apihelpers
from sandbox.projects.release_machine import rm_notify
from sandbox.projects.report import common as rc
from sandbox.projects import resource_types
import sandbox.projects.sandbox.resources

from sandbox.projects.websearch.flags_provider.resources import FlagsProviderBinaryBundleResourseType


class ArcadiaUrlFunctionTest(sp.SandboxArcadiaUrlParameter):
    name = 'svn_url_function_test'
    description = 'Arcadia url for function test:'
    default_value = sp.SandboxArcadiaUrlParameter.default_value + '/search/garden/runtime_tests/@HEAD'


class RtccBundle(Unit.RtccBundle):
    pass


class ExtraParams(sp.SandboxStringParameter):
    name = 'run_test_param'
    description = 'Additional parameters for run_test.py:'
    default_value = "--enable_datatests"


class TestPathParams(sp.SandboxStringParameter):
    name = 'test_path_param'
    description = 'Parameters for tests directory'
    default_value = "report/*/{web,people} report/integration/xml"


class TestIterations(sp.SandboxIntegerParameter):
    name = 'test_iterations_max'
    description = 'Iterations for failed tests (limit, SERP-61678)'
    default_value = 4


class TestsNamesToRun(sp.SandboxStringParameter):
    name = 'test_names_to_run'
    description = 'Exact test names to run (arg for pytest -k)'
    default_value = ""


class AdditionalFlags(sp.SandboxStringParameter):
    name = 'additional_flags'
    description = 'Addition flags, json string. e.g. {"taxi_form":0}'
    default_value = ""


class CustomRequestJSONConfig(sp.SandboxUrlParameter):
    name = 'config_request_json'
    description = 'Copy request.json from uri, e.g. http://apphost.priemka.yandex.ru/viewconfig?name=request.json'
    default_value = ""


class CustomFlagsJSON(sp.SandboxUrlParameter):
    name = 'flags_json'
    description = 'Copy flags.json from uri, e.g. https://ab.yandex-team.ru/deploying/flags.json/2/content'
    default_value = ""


class CustomFlagsProviderBinary(sp.LastReleasedResource):
    name = 'flags_provider_binary'
    description = 'flags_provider binary resource. Task will get current version from Release Machine if not specified'
    required = False
    type = FlagsProviderBinaryBundleResourseType


class FlagsProviderPort(sp.SandboxIntegerParameter):
    name = 'flags_provider_port'
    description = 'flags_provider port number'
    default_value = 16300


class ContainerLxc(Unit.ContainerLxc):
    @property
    def default_value(self):
        res = apihelpers.get_last_resource_with_attribute(
            sandbox.projects.sandbox.resources.LXC_CONTAINER,
            attribute_name='report',
            attribute_value='2',
        )
        return res.id if res else None


class LaunchMarkerID(sp.SandboxUrlParameter):
    name = 'launch_marker'
    description = 'test'
    default_value = "0"


class ComponentName(rm_params.ComponentName):
    # REPORTINFRA-331
    default_value = "report"
    required = False


# Test results in json format
_RESULTS_JSON = 'results.json'
_MAX_TESTS_TO_SHOW = 50


@rm_notify.notify2()
class TestReportFunctionalOpt(Unit.TestReportUnit):
    """
        Прогон функциональных тестов report'a.
    """

    type = 'TEST_REPORT_FUNCTIONAL_OPT'

    input_parameters = [
        rc.Project,
        Unit.Selector,
        Unit.ArcadiaUrl,
        DefaultUpperSearchParams.ReportCoreParameter,
        Unit.DataRuntime,
        rc.ApacheBundleParameter,
        DefaultUpperSearchParams.ReportTemplatesParameter,
        RtccBundle,
        rc.SDCHDict,
        Unit.EnvAddition,
        ArcadiaUrlFunctionTest,
        ExtraParams,
        TestIterations,
        TestsNamesToRun,
        TestPathParams,
        AdditionalFlags,
        ContainerLxc,
        CustomRequestJSONConfig,
        CustomFlagsJSON,
        CustomFlagsProviderBinary,
        FlagsProviderPort,
        rm_params.ReleaseNum,
        ComponentName,
        Unit.CheckoutReport,
    ]
    execution_space = 16 * 1024

    required_ram = 20
    cores = 8

    # т.к. перезапуски не делаются

    # нужно ли упаковать ресурс
    tar = 0

    path = {
        'template': 'report-templates',
        'config': 'conf',
        'report': 'report',
        'apache': 'apache_bundle',
        'runtime': 'data.runtime',
        'log': 'logs_report',
        'upper_conf': 'upper_conf',
        'sdch': 'sdch-dictionaries',
    }

    client_tags = Tag.GENERIC | Tag.MULTISLOT

    def initCtx(self):
        self.ctx['kill_timeout'] = 4 * 3600  # 4 hours

    @staticmethod
    def get_sdch(res_id, dest='sdch-dictionaries', conf_dir='conf'):
        Unit.TestReportUnit.expand_resource(res_id, dest)
        # создать симлинки
        # sdch-config.json -> ../sdch-dictionaries/sdch-config.json
        # apache_include -> ../sdch-dictionaries/apache_include
        for p in ('sdch-config.json', 'apache_include'):
            src = os.path.join("../", dest, p)
            link_name = os.path.join(conf_dir, p)
            os.symlink(src, link_name)

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
        apache_bundle_id = self.ctx.get(rc.ApacheBundleParameter.name)
        if not apache_bundle_id:
            apache_bundle_id = self._get_last_released_resource('APACHE_BUNDLE')
        logging.info('Using APACHE_BUNDLE: %s', apache_bundle_id)

        data_runtime_id = self.ctx.get(Unit.DataRuntime.name)
        if not data_runtime_id:
            data_runtime_id = self._get_last_released_resource(
                'REPORT_DATA_RUNTIME',
                attrs={
                    'project': 'WEB',
                    'test_env_report_unit': None,
                },
            )
        logging.info('Using REPORT_DATA_RUNTIME: %s', data_runtime_id)

        project = self.ctx[rc.Project.name]

        flags = ''
        if self.ctx[AdditionalFlags.name]:
            # check json
            json.loads(self.ctx[AdditionalFlags.name])
            flags = self.ctx[AdditionalFlags.name]

        self.freeze_svn_url(self)

        # получить apache_bundle
        new_vars = {
            "YX_PID_FILE": os.path.join('.', self.path["config"], "httpd.pid"),
            "PID_FILE": os.path.join('.', self.path["config"], "httpd.pid"),
            "LOCK_FILE": os.path.join('.', self.path["config"], "accept.lock"),
            "YX_LOG_DIR": os.path.join('.', self.path["log"]),
            "LOG_DIR": os.path.join('.', self.path["log"]),
        }
        self.get_apache(apache_bundle_id, self.path['apache'], new_vars)

        # получить шаблоны
        report_templates_resource_id = self.ctx.get(DefaultUpperSearchParams.ReportTemplatesParameter.name)
        if not report_templates_resource_id:
            report_templates_resource_id = self._get_last_released_resource(resource_types.REPORT_TEMPLATES_PACKAGE)
        self.expand_resource(report_templates_resource_id, self.path['template'])

        # выставляем переменные окружения
        self.setup_env()

        # получить поисковый конфиг
        self.get_upper_config(
            self.ctx[RtccBundle.name],
            project=project,
            dest=self.path['upper_conf'],
            link_prefix=self.path['config'],
            is_beta=os.environ.get('IS_BETA'),
        )

        # подменить request.json для тестирования приёмок
        if utils.get_or_default(self.ctx, CustomRequestJSONConfig):
            self.download_file(
                "{}/{}".format(self.path['config'], "request.json"),
                self.ctx[CustomRequestJSONConfig.name]
            )

        # conf/report
        paths.make_folder(os.path.join(self.path['config'], 'report'), delete_content=True)
        # получить репорт из пакета либо вытянуть из svn
        self.get_report(self, self.path['report'])

        paths.make_folder(self.path["log"], delete_content=True)

        # получить sdch надо до генерации конфига апача
        sdch_dict_resource_id = self.ctx.get(rc.SDCHDict.name)
        if not sdch_dict_resource_id:
            sdch_dict_resource_id = self._get_last_released_resource('SDCH_WEB_DICTIONARY_PACK')
        logging.info('Using SdchWebdictionaryPack: %s', sdch_dict_resource_id)

        self.get_sdch(sdch_dict_resource_id, self.path['sdch'], self.path['config'])

        self.port = os.environ['PORT1']

        # chmod g+s
        sandbox.common.fs.chmod_for_path(self.abs_path(), "g+s")
        prog = os.path.join(self.path['report'], 'scripts/dev/upperconf.pl')
        self._generate_apache_config(prog, project)

        # получить data.runtime
        self.get_data_runtime(
            data_runtime_id,
            self.path['runtime'],
            self.runtime_version_for_report(self.path['report']),
        )

        # подменить файл flags.json
        if utils.get_or_default(self.ctx, CustomFlagsJSON):
            flags_beta_path = "{}/{}".format(self.path['report'], "data/flags/experiments/flags.json")
            self.download_file(flags_beta_path, self.ctx[CustomFlagsJSON.name])
            paths.copy_path(flags_beta_path, "{}/{}".format(self.path['runtime'], "util/experiments/flags.json"))
            if os.environ.get('FLAGS_JSON_TEST', ''):
                self._run_flags_provider(flags_beta_path)

        results_xml_path = self.log_path(os.path.join('result', 'results.xml'))
        paths.make_folder(os.path.dirname(results_xml_path), delete_content=True)

        func_path = 'runtime_tests'
        paths.make_folder(func_path, delete_content=True)
        svn_url = Arcadia.freeze_url_revision(self.ctx[ArcadiaUrlFunctionTest.name])
        logging.info('Arcadia svn_url: %s', svn_url)
        logging.info('get_revision: %s', Arcadia.get_revision(svn_url))
        Arcadia.checkout(url=svn_url, path=func_path, revision=Arcadia.get_revision(svn_url))

        logging.debug("Environment: %s", os.environ)

        # run apache
        process.run_process(
            [
                'y-local-env', prog, '-restart', self.abs_path(),
            ],
            log_prefix='apache',
        )

        self._prepare_output_resources()

        # a bit of global loop state
        prev_failed_test_names = []
        failed_test_names = None
        failed_tests = []
        # all merged test results to dump
        all_tests = None

        with environments.VirtualEnvironment(do_not_remove=True) as venv:
            venv.pip("pip==19.1 setuptools==41.0.1 coverage==5.5")
            environments.PipEnvironment('Fabric', '1.12.1', use_wheel=True, venv=venv).prepare()
            environments.PipEnvironment('yandex-yt-yson-bindings-skynet', '', use_wheel=True, venv=venv).prepare()
            environments.PipEnvironment('lz4', '2.0.2', use_wheel=True, venv=venv).prepare()
            environments.PipEnvironment('zstandard', '0.9.1', use_wheel=True, venv=venv).prepare()

            # hack for requirements. in the sandbox we use skynet python, but on betas we use standart python
            # so we must use yandex-yt-yson-bindings-skynet in the sandbox
            # and yandex-yt-yson-bindings on betas
            with open(os.path.join(self.abs_path(), func_path, 'report/requirements.txt')) as f:
                reqs = filter(lambda x: not x.startswith('yandex-yt-yson-bindings'), f.read().splitlines())
            with open(os.path.join(self.abs_path(), func_path, 'report/requirements.txt'), 'w') as f:
                f.write("\n".join(reqs + ['yandex-yt-yson-bindings-skynet']))

            # venv.pip("pip setuptools")
            # venv.pip('pip==9.0.1')
            venv.pip('-r {}'.format(os.path.join(func_path, 'report/requirements.txt')))
            logging.info("Environment setup complete")

            # initial pack
            test_names_to_run = self.ctx[TestsNamesToRun.name]

            # Main failed tests reduction loop
            max_iterations = utils.get_or_default(self.ctx, TestIterations)
            for test_iteration in six.moves.range(max_iterations):
                logging.info("Run tests iteration %s", test_iteration)
                self.set_info("Run tests iteration {}...".format(test_iteration))

                try:
                    self._run_tests(venv, func_path, results_xml_path, flags, test_names_to_run)
                except Exception as exc:
                    eh.log_exception("Tests run [iteration {}] failed".format(test_iteration), exc)

                self._convert_test_results_to_json(results_xml_path)  # output to _RESULTS_JSON

                # test result post-processing
                failed_tests, passed_tests = self._parse_test_results(_RESULTS_JSON)
                logging.debug("Failed tests: %s\n", json.dumps(failed_tests, indent=4))
                logging.debug("Passed tests: %s\n", json.dumps(passed_tests, indent=4))

                all_tests = self._merge_results(all_tests, failed_tests, passed_tests)

                # test_name is truncated. i don't have enough time to find why.
                failed_test_names = list(set([
                    re.sub(r'\[.*(?:\.\.\.|\])$', '', test['subtest_name'])
                    for test in failed_tests
                ]))
                self.set_info(
                    "Iteration {} failed tests count: {}".format(
                        test_iteration, len(failed_test_names),
                    )
                )

                if (
                    set(failed_test_names) == set(prev_failed_test_names) or (
                        # stable mass failures on re-run: not good
                        test_iteration > 0 and len(failed_test_names) > 100
                    )
                ):
                    # tests failures are stabilized
                    logging.info('Stable test failures: %s', failed_test_names)
                    break

                logging.info('failed_test_names: %s', failed_test_names)
                test_names_to_run = ' or '.join(failed_test_names)

            # `prev_failed_test_names` now contains failed tests
            logging.info("FINALLY failed tests: %s\n", json.dumps(failed_tests, indent=4))
            self.ctx['failed_tests_count'] = {
                'failed_tests_count': len(failed_tests),
            }

        # stop apache
        process.run_process(['y-local-env {} -stop {}'.format(prog, self.abs_path())], shell=True, log_prefix='apache')

        # Save complete logs
        detailed_logs_resource = self.create_resource(
            description='Detailed tests logs',
            resource_path=self.path['log'],
            resource_type='OTHER_RESOURCE',
            arch=None,
        )
        self.mark_resource_ready(detailed_logs_resource.id)

        # dump final results
        data = {
            'results': all_tests,
        }
        json_results_resource = channel.sandbox.get_resource(self.ctx[xml_to_json.JSON_V2_RESOURCE_FIELD_NAME])
        fu.json_dump(json_results_resource.path, data, indent=4)
        self.ctx['final_resource_url'] = json_results_resource.proxy_url
        self.mark_resource_ready(json_results_resource.id)
        self.mark_resource_ready(self.ctx[xml_to_json.LOGS_V2_RESOURCE_FIELD_NAME])

        # store failed tests state in context also
        failed_test_names = sorted(failed_test_names)
        self.ctx['failed_test_names'] = failed_test_names
        if len(failed_test_names) > _MAX_TESTS_TO_SHOW:
            self.set_info(
                "First {} failed tests (of {} total):\n\t{}".format(
                    _MAX_TESTS_TO_SHOW,
                    len(failed_test_names),
                    "\n\t".join(failed_test_names[:_MAX_TESTS_TO_SHOW])
                )
            )
        else:
            self.set_info(
                "Failed {} tests:\n\t{}".format(
                    len(failed_test_names),
                    "\n\t".join(failed_test_names)
                )
            )

        self.ctx['failed_tests_count_FINAL'] = {
            'failed_tests_count_FINAL': len(failed_tests)
        }

    def _run_flags_provider(self, flags_beta_path):
        logging.info('Trying to setup flags_provider...')
        fp_resource = utils.get_or_default(self.ctx, CustomFlagsProviderBinary)
        if not fp_resource:
            logging.info('Getting current prod version of flags_provider...')
            try:
                r = requests.post(
                    'http://rm.z.yandex-team.ru/api/release_engine.services.Model/getState',
                    data='{"component_name": "flags_provider", "key": "/current_version$stable"}',
                    headers={'Content-Type': 'application/json'},
                    timeout=10,
                )

                ans = r.json()
                logging.info('RM answer: %s', ans)
                build_task_id = json.loads(ans['entries'][0]['value'])['build_task_id']

                fp_resource = sdk2.Resource.find(
                    FlagsProviderBinaryBundleResourseType,
                    task_id=build_task_id
                ).limit(1).first()
            except Exception as exc:
                eh.log_exception('Could not get last released resource from Release Machine', exc)
                raise errors.TemporaryError('Could not get last released resource from Release Machine: {}'.format(exc))

        logging.info('flag_provider binary resource: %s', fp_resource)
        Unit.TestReportUnit.expand_resource(fp_resource, 'flags_provider_dir')

        with open(flags_beta_path, 'r') as f:
            data = json.load(f)
            logging.info(
                'flags.json used for flags_provider: v%s from %s',
                data['meta']['version'], data['meta']['ts_created']
            )

        config_file = tempfile.NamedTemporaryFile()

        its_path = "{}/{}".format(self.path['report'], "data/flags/its/upper_sas_Web.json")
        its_images_path = "{}/{}".format(self.path['report'], "data/flags/its/upper_sas_Images.json")
        its_video_path = "{}/{}".format(self.path['report'], "data/flags/its/upper_sas_Video.json")
        alias_json_path = "{}/{}".format(self.path['report'], "data/flags/experiments/alias.json")

        provider_port = utils.get_or_default(self.ctx, FlagsProviderPort)

        config = {
            'vertical': 'WEB',
            'port': provider_port,
            'grpc_port': provider_port + 1,
            'its_update_period': 1,
            'workers': 4,
            'grpc_workers': 4,
            'eventlog': 'current-eventlog',
            'flags': [
                {
                    'name': 'web',
                    'flags': flags_beta_path,
                    'alias': alias_json_path,
                    'its_flags': its_path,
                    'its_disable_flag_sections': 'empty'
                },
                {
                    'name': 'images',
                    'its_flags': its_images_path,
                    'its_disable_flag_sections': 'empty'
                },
                {
                    'name': 'video',
                    'its_flags': its_video_path,
                    'its_disable_flag_sections': 'empty'
                }
            ]
        }

        config_file.write(json.dumps(config))
        config_file.flush()

        process.run_process(
            ['flags_provider_dir/flags_provider',
             '--config', config_file.name],
            log_prefix='flags_provider',
            wait=False
        )

        logging.info('Waiting for flags_provider to start...')
        start_time = time.time()
        while True:
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                sock.settimeout(10)
                if sock.connect_ex(('127.0.0.1', provider_port)) == 0:
                    break
            if (time.time() - start_time) > 60:
                raise errors.TaskFailure('Waiting for flags_provider to start reached timeout')

        os.environ['FLAGS_PROVIDER_PORT'] = str(provider_port)
        logging.info('flags_provider started!')

    @staticmethod
    def _merge_results(all_tests, failed_tests, passed_tests):
        # merge current failures into
        if not all_tests:
            # 0th teration starts with empty list, so we update it
            all_tests = failed_tests + passed_tests

        # quadratish, praktish, gut, but who cares
        for i in six.moves.range(0, len(all_tests)):
            # check if we can replace with passed test
            for pt in passed_tests:
                if (
                    all_tests[i]['subtest_name'] == pt['subtest_name'] and
                    (
                        pt['status'] == 'OK' or
                        pt['status'] == 'SUCCESS'  # this value is never used, but who cares
                    )

                ):
                    # update with succeeded one
                    logging.info(
                        "Updated test result\n%s\nwith\n%s",
                        json.dumps(all_tests[i], indent=4),
                        json.dumps(pt, indent=4),
                    )
                    all_tests[i] = pt

        return all_tests

    def _prepare_output_resources(self):
        self.ctx['tests_type'] = 'functional'

        if 'functional_test' not in self.ctx:
            xml_to_json.on_enqueue(self, opt=True, output_file_name=_RESULTS_JSON)
            self.ctx['functional_test'] = 1

    def _convert_test_results_to_json(self, results_xml_path):
        # check output exists
        eh.ensure(
            os.path.exists(results_xml_path) and os.path.getsize(results_xml_path),
            'Functional test output {} is empty. '
            'Typically this is a configuration error or test suite failed to start. '
            'Please check logs. '.format(results_xml_path)
        )

        xml_to_json.find_and_convert(self, os.path.dirname(results_xml_path))

    def _run_tests(self, venv, func_path, result_path, flags, test_names_to_run):
        pytest_args = [
            venv.executable,
            './run_test.py',
            '--host=localhost:{}'.format(self.port),
            '-s',
            '-v',
            '-rs',
            '--sandbox',
            '--log_dir={}'.format(
                os.path.join(self.abs_path(), self.path["log"], 'test_log')
            ),
            '--reportpath={}'.format(self.abs_path()),
            '--junitxml={}'.format(result_path),
        ]
        if flags:
            # FIXME(mvel): weak place
            pytest_args.append('--flags="{}"'.format(flags))

        pytest_extra_opts = self.ctx[ExtraParams.name]
        if pytest_extra_opts:
            pytest_args += _prepare_args(pytest_extra_opts)

        if test_names_to_run:
            pytest_args += [
                '-k',
                string.all_to_str(test_names_to_run),
            ]

        # add main argument: these should be valid test paths, space-separated
        pytest_args += _prepare_args(self.ctx[TestPathParams.name])
        logging.info("pytest args:\n%s\n\n", "\n".join(pytest_args))

        process.run_process(
            pytest_args,
            work_dir=func_path,
            log_prefix='test',
        )

    def _generate_apache_config(self, prog, project):
        project_key = rc.Project.upperconf_key[project]
        args = [
            'y-local-env', prog, '-verbose', '-config_httpd',
        ]
        if project_key:
            args.append(project_key)
        args.append(self.abs_path())
        process.run_process(args, log_prefix='httpd.conf')

    def _create_results_resource(self, result_path):
        final_resource = self.create_resource(
            description='Test results',
            resource_path=result_path,
            resource_type='TEST_ENVIRONMENT_JSON_V2',
            arch=None,
        )
        self.mark_resource_ready(final_resource.id)
        self.ctx['final_resource_id'] = final_resource.id
        return final_resource

    def download_test_results(self, download_task, res_name):
        resource_path = self.sync_resource(download_task.ctx[res_name])
        return self._parse_test_results(resource_path)

    def _parse_test_results(self, results_path):
        with open(results_path) as json_file:
            json_data = json.load(json_file)
            test_results = json_data[u'results']
            failed_tests = []
            tests_ok = []
            for test in test_results:
                if test[u'status'] == u'FAILED':
                    failed_tests.append(test)
                else:
                    tests_ok.append(test)
        return failed_tests, tests_ok

    def setup_env(self):
        # NOSUDO = 1 для использования upperconf.pl
        env = {
            "NOSUDO": "1"
        }

        if self.ctx[Unit.EnvAddition.name]:
            for part in self.ctx[Unit.EnvAddition.name].split():
                (k, v) = part.split("=", 1)
                env[k] = v

        # для генерации конфига апача
        if "PORT1" not in env:
            env["PORT1"] = "8081"

        for key, value in env.items():
            if key == 'PATH' and os.environ.get(key):
                new_value = "{}:{}".format(value, os.environ[key])
                logging.info("Set PATH: `%s`", new_value)
                os.environ[key] = new_value
            else:
                logging.info("Set ENV: `%s` = `%s`", key, value)
                os.environ[key] = value

        os.environ['CLIENT_IPV6_ADDRESS'] = network.get_my_ipv6()
        logging.info("Set CLIENT_IPV6_ADDRESS: `%s`", os.environ['CLIENT_IPV6_ADDRESS'])

    def make_message_for_st(self, is_bad):
        if is_bad < 0 or is_bad > 1:
            is_bad = 1

        message = [
            "((%s Functional tests)) are !!(green)**OK**!!",
            u"((%s Functional tests)) are !!(red)**FAILED**!!"
        ]
        if is_bad:
            return message[is_bad]

        is_bad = 1
        data = json.load(open('result_final/results.json'))
        logging.info('tests')

        for i in data['results']:
            if i[u'status'] == u'OK' or i[u'status'] == u'SKIPPED':
                is_bad = 0
            else:
                is_bad = 1
                break
        return message[is_bad]


def _prepare_args(str_args):
    str_args = string.all_to_str(str_args).strip()
    return [p for p in str_args.split(' ') if p]


__Task__ = TestReportFunctionalOpt
