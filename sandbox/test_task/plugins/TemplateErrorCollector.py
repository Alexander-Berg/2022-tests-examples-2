# -*- coding: utf-8 -*-

import os

from sandbox.common.types import task as ctt
from sandbox.common.errors import TaskFailure
from sandbox.projects.sandbox_ci.task.test_task.plugins.Plugin import Plugin


class TemplateErrorCollector(Plugin):
    def __init__(self, task):
        super(TemplateErrorCollector, self).__init__(task)
        self._report_file_name = 'template-errors.txt'
        self._report_type = 'template-errors'

    @property
    def report_type(self):
        return self._report_type

    @property
    def report_file_name(self):
        return self._report_file_name

    def set_env(self):
        os.environ['template_error_collector_report_path'] = self._report_file_name

        # Если упадет процесс gemini|hermione, то все репорты прокрасятся в красный
        os.environ['template_error_collector_fail_on_errors'] = 'false'

    def get_reports_attrs(self, status, common_attributes):
        return [dict(
            common_attributes,
            resource_path=self._report_file_name,
            type=self._report_type,
            status=ctt.Status.FAILURE,
            add_to_context=True,
        )]

    def validate_result(self):
        report_path = self._task.artifacts.get_artifact_path(self._task.project_path(self._report_file_name))

        if not report_path.exists():
            return

        if self._task.config.get_deep_value(['tests', self._task.tool, 'ignore_template_errors'], False):
            return

        raise TaskFailure('There were some errors during template execution. See reports for more details')
