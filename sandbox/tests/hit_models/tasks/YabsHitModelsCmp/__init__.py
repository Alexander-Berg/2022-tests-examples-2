import os
import logging
import posixpath
from sandbox import sdk2
from sandbox.sdk2 import service_resources
from sandbox.common import config
from collections import OrderedDict
from sandbox.common.types import task as task_type
from sandbox.common.errors import SandboxException
from sandbox.sdk2.helpers import subprocess as sp
import sandbox.common.types.resource as ctr
from sandbox.common.types import task as ctt
from sandbox.projects.common import environments
from sandbox.projects.resource_types import OTHER_RESOURCE
from sandbox.projects.yabs.qa.resource_types import YABS_REPORT_RESOURCE, BaseBackupAbstractResource
from sandbox.projects.runtime_models.tests.hit_models.tasks.YabsHitModelsShootTask import YabsHitModelsResponseDump
from sandbox.projects.yabs.qa.utils.resource import sync_resource
from sandbox.projects.runtime_models.tests.hit_models.tasks.YabsHitModelsCmp.compare import compare_responses
from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShootCmp import YabsFtReport, YabsFtReportIndex
from sandbox.projects.yabs.sandbox_task_tracing.wrappers.sandbox.generic import new_resource
from sandbox.projects.yabs.sandbox_task_tracing.wrappers.sandbox.sdk2 import make_resource_ready
from sandbox.projects.yabs.qa.utils.general import html_hyperlink
from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShootCmp.report import (
    CmpReport, CmpReportLinksIndex,
    ECmpReportFiles, create_comparison_metareport,
)


class YabsHitModelsDumpParser(BaseBackupAbstractResource):
    """ Resource with dolbilo2json utility """
    releasable = True
    auto_backup = True
    sync_upload_to_mds = True
    releasers = ["YABS_SERVER_SANDBOX_TESTS"]
    ttl = 42


def get_shoot_task_dump(task_id):
    logging.debug('Get dumps from shoot task resources')
    return list(
        YabsHitModelsResponseDump.find(task_id=task_id, state=ctr.State.READY).order(sdk2.Resource.id).limit(1)
    )[0]


class YabsHitModelsCmp(sdk2.Task):
    class Requirements(sdk2.Task.Requirements):
        environments = (environments.PipEnvironment("yandex-yt"),)

    class Parameters(sdk2.Parameters):
        description = "HitModels shoots compare task"
        max_restarts = 3
        kill_timeout = 60 * 60 * 2

        dump_parser_binary = sdk2.parameters.Resource(
            "HitModels dump parser",
            resource_type=OTHER_RESOURCE,
            state=ctr.State.READY,
            required=True,
        )

        pre_task = sdk2.parameters.Task(
            "Pre task",
            task_type="YABS_HIT_MODELS_SHOOT_TASK",
            required=True,
        )

        test_task = sdk2.parameters.Task(
            "Test task",
            task_type="YABS_HIT_MODELS_SHOOT_TASK",
            required=True,
        )

        template_resource = sdk2.parameters.Resource('Template resource', resource_type=YABS_REPORT_RESOURCE)
        report_ttl = sdk2.parameters.Integer(
            'TTL for b2b report',
            description='Default ttl is 42 days. It should be 550 days for big tests',
            default=42
        )

        parser_threads = sdk2.parameters.Integer(
            "Parser threads count",
            default=4
        )

        comparison_jobs = sdk2.parameters.Integer(
            "Comparison jobs count",
            default=1
        )

    def on_create(self):
        self.Requirements.tasks_resource = service_resources.SandboxTasksBinary.find(
            owner="YABS_MODELS_SERVICES",
            attrs={
                "tasks_bundle": "YABS_HIT_MODELS_TESTS_BUNDLE",
                "released": ctt.ReleaseStatus.STABLE
            },
        ).first()

    def parse_dumps(self, pre, test):
        dump_resources = {}
        for shoot_type, shoot_task in [(pre, self.Parameters.pre_task), (test, self.Parameters.test_task)]:
            dump_resources[shoot_type] = get_shoot_task_dump(shoot_task.id)
            if not dump_resources[shoot_type]:
                raise SandboxException('Could not find a dump result from input task {}'.format(shoot_task.id))

        dump_parser_path = sdk2.ResourceData(self.Parameters.dump_parser_binary).path
        for shoot_type, dump_resource in dump_resources.items():
            dump_path = sync_resource(dump_resource)
            cmd = [str(dump_parser_path), '-r', shoot_type]
            cmd += ['-j', str(self.Parameters.parser_threads)]
            cmd += ['--multiline', '--quotes']
            cmd += [dump_path]

            os.mkdir(shoot_type)
            with sdk2.helpers.ProcessLog(self, logger='dump_parse_{}'.format(shoot_type)) as logger:
                sp.check_call(cmd, stdout=logger.stdout, stderr=logger.stderr)

    @staticmethod
    def get_resource_url(task_id, resource_path, resource_id):
        settings = config.Registry()
        fs_settings = settings.client.fileserver
        if fs_settings.proxy.host:
            return "https://{}/{}".format(fs_settings.proxy.host, resource_id)

        return "http://{}:{}/{}/{}".format(
            settings.server.web.address.host, fs_settings.port, "/".join(task_type.relpath(task_id)), resource_path
        )

    def _create_report_resource(self, resource_class, description, path, **kwargs):
        resource = new_resource(resource_class, task=self, description=description, path=path, ttl=self.Parameters.report_ttl, **kwargs)
        make_resource_ready(resource)
        return resource

    def construct_metadata(self, comparison_result):
        metadata = {
            "Tests": comparison_result.test_total_count,
            "Failures": comparison_result.test_failures_count,
        }
        return metadata

    def on_execute(self):
        pre_path = 'pre'
        test_path = 'test'
        self.parse_dumps(pre=pre_path, test=test_path)

        pre_responses = set(os.listdir(pre_path))
        test_responses = set(os.listdir(test_path))

        if pre_responses ^ test_responses:
            logging.warning(
                'Non-identical response sets\n'
                'Pre response count: %s\n'
                'Test response count: %s',
                len(pre_responses),
                len(test_responses),
            )
            logging.warning('Request-ID\'s unique to pre: %s', ', '.join(pre_responses - test_responses))
            logging.warning('Request-ID\'s unique to test: %s', ', '.join(test_responses - pre_responses))

        template_path = sync_resource(resource=self.Parameters.template_resource, resource_type=YABS_REPORT_RESOURCE)
        report = CmpReport()
        report.prepare(template_path)

        request_ids = pre_responses & test_responses
        logging.info('RequestIDs to compare: {}'.format(request_ids))
        comparison_result, web_report_index = compare_responses(
            pre_path=pre_path,
            test_path=test_path,
            request_ids=request_ids,
            report=report,
            jobs=self.Parameters.comparison_jobs,
        )

        report_results = {
            'search': OrderedDict([
                ('pre.code', list(comparison_result.pre_codes)),
                ('test.code', list(comparison_result.test_codes)),
                ('handler', list(comparison_result.handlers)),
                ('tags', list(comparison_result.diff_tags))
            ]),
            'meta': [
                {'title': title, 'value': value}
                for title, value in self.construct_metadata(comparison_result).iteritems()
            ],
            'results': web_report_index,
        }

        logging.info('Saving report.json')
        report.add_final_report_results(report_results)

        report_resource = self._create_report_resource(
            resource_class=YabsFtReport,
            description='Report resource',
            path=report.get_local_path(),
        )
        report_url = self.get_resource_url(self.id, report.get_local_path(), report_resource.id)

        def report_file_url(rel_path):
            return posixpath.join(report_url, rel_path)

        report_links = [
            ("Diff viewer", report_file_url(ECmpReportFiles.report_index_html)),
        ]

        task_execution_report_html = create_comparison_metareport(
            comparison_result.test_total_count,
            len(web_report_index),
            comparison_result.test_failures_count,
            report_links,
            line_sep='<br>',
            link_formatter=html_hyperlink,
        )

        report_links_index = CmpReportLinksIndex()
        report_links_index.add_report_links_index(task_execution_report_html)

        report_index_resource = self._create_report_resource(
            resource_class=YabsFtReportIndex,
            description='Report index resource',
            path=report_links_index.get_local_path(),
        )
        report_index_url = self.get_resource_url(self.id, ECmpReportFiles.report_index_html, report_index_resource.id)

        self.Context.short_report_text = '{failures} out of {total_tests} tests failed'.format(
            failures=comparison_result.test_failures_count, total_tests=comparison_result.test_total_count
        )
        self.Context.has_diff = bool(comparison_result.test_failures_count)
        self.Context.short_report_link = report_index_url
        self.set_info(task_execution_report_html, do_escape=False)
