# -*- coding: utf-8 -*-

import os

from sandbox.projects.sandbox_ci.utils.ref_formatter import strip_ref_prefix, is_arcanum_ref
from sandbox.projects.sandbox_ci.task.test_task.plugins.Plugin import Plugin
from sandbox.projects.sandbox_ci.utils.dict_utils import defaults


class HtmlReporter(Plugin):
    def __init__(self, task):
        super(HtmlReporter, self).__init__(task)
        self._report_path = self._report_type = '{}-report'.format(self._task.tool if hasattr(self._task, 'tool') else 'html')

    def set_report_type(self, report_type):
        self._report_type = report_type

    def set_report_path(self, report_path):
        self._report_path = report_path

    def set_env(self):
        os.environ['html_reporter_base_host'] = self._task.Parameters.beta_domain
        os.environ['html_reporter_path'] = self._report_path

        commit = self._task.Parameters.project_github_commit

        ref = self._task.Parameters.arc_ref or commit or self._task.Parameters.project_hash or self._task.Parameters.ref
        arcadia_path = self._task.Parameters.path_in_arcadia
        
        if self._task.Parameters.project_build_context == 'pull-request' and is_arcanum_ref(self._task.Parameters.ref):
            review_request_id = strip_ref_prefix(self._task.Parameters.ref)
            file_base_url = 'https://a.yandex-team.ru/arc/trunk/arcadia/{}/?from_pr={}'.format(arcadia_path, review_request_id)
        elif ref:
            file_base_url = 'https://a.yandex-team.ru/arc/trunk/arcadia/{}/?ref={}'.format(arcadia_path, ref)
        else:
            file_base_url = ''
        
        session_log_base_url = 'https://sw.yandex-team.ru/log/'

        os.environ['html_reporter_meta_info_base_urls'] = '{{"file": "{}", "sessionId": "{}"}}'.format(
            file_base_url, session_log_base_url)

    def get_reports_attrs(self, status, common_attributes):
        sync_upload_to_mds = self._task.config.get_deep_value(['tests', self._task.tool, 'sync_html_report_to_mds'], False)
        build_context = getattr(self._task.Parameters, 'project_build_context', '')

        send_results_to_testcop = getattr(self._task.Parameters, 'send_results_to_testcop', False)

        if (build_context == 'dev' and self._task.is_automated) or send_results_to_testcop:
            collect_stats = 'true'
        else:
            collect_stats = 'false'

        return [
            defaults(common_attributes, dict(
                resource_path=self._report_path,
                type=self._report_type + '-archive',
                make_tar=True,
                sync_upload_to_mds=sync_upload_to_mds,
            )),
            defaults(common_attributes, dict(
                resource_path=self._report_path,
                type=self._report_type,
                status=status,
                add_to_context=True,
                public=True,
                root_path='index.html',
                build_context=build_context,
                build_id=getattr(self._task.Parameters, 'build_id'),
                commit_sha=getattr(self._task.Parameters, 'project_github_commit'),
                report_data_urls=getattr(self._task.Parameters, 'report_data_urls', ''),
                ttl=60,
                sync_upload_to_mds=sync_upload_to_mds,
                collect_stats=collect_stats,
            ))
        ]
