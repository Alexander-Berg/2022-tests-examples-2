# -*- coding: utf-8 -*-

import sandbox.common.types.misc as ctm
from sandbox.sdk2 import Task, parameters, ResourceData
from .task import AdfoxTestRunCreateTask, PROJ_PI, PROJ_ADFOX
from sandbox.projects.partner.tasks.e2e_tests.misc.resources import PartnerJSONReportResource
from sandbox.projects.adfox.adfox_ui.util.duty_tools import DutyTools
from sandbox.projects.adfox.adfox_ui.metrics import AnalyzableTask
import json


class TestpalmTestRunCreate(AnalyzableTask):
    class Requirements(Task.Requirements):
        dns = ctm.DnsType.DNS64

    class Parameters(AnalyzableTask.Parameters):

        testpalm_secret = parameters.YavSecret(
            'TestPalm секрет',
            default='sec-01entvc29ry93ja7jdb20nwhfx',
            required=True,
            description="Секрет к TestPalm (должен содержать ключ testpalm_token)"
        )
        project = parameters.String(
            'Project',
            default='pi-palmsync',
            required=False,
            description="Имя проекта в TestPalm"
        )
        pi_report = parameters.Resource(
            'PI JSON report',
            required=False,
            resource_type=PartnerJSONReportResource
        )
        adfox_report = parameters.Resource(
            'ADFOX JSON report',
            required=False,
            resource_type=PartnerJSONReportResource
        )

    def on_execute(self):
        super(TestpalmTestRunCreate, self).on_execute()
        report = {}
        if self.Parameters.pi_report:
            pi_report = json.loads(ResourceData(self.Parameters.pi_report).path.read_text('utf-8'))
            for key, value in pi_report.iteritems():
                value.update({'source_project': PROJ_PI})

            report.update(pi_report)

        if self.Parameters.adfox_report:
            adfox_report = json.loads(ResourceData(self.Parameters.adfox_report).path.read_text('utf-8'))
            for key, value in adfox_report.iteritems():
                value.update({'source_project': PROJ_ADFOX})

            report.update(adfox_report)

        secrets = self.Parameters.testpalm_secret.data()
        run_task = AdfoxTestRunCreateTask(
            testpalm_token=secrets['testpalm_token'],
            report=report,
            project=self.Parameters.project
        )
        run_task.execute()

        self.Context.version_id = run_task.version_id
        # version_id_failed содержит не только лишь кейсы по упавшии автотестам:
        # возможно не указать один или оба из отчетов, тогда в ран
        # попадут кейсы по всем (предположительно пропущенным) автоматизированным
        # кейсамы соотеветствующих проектов
        self.Context.version_id_failed = run_task.version_id_failed

        duty_tools = DutyTools()
        duty_tools.send_assessors_metrics(self._prepare_stats(run_task.stats))
        duty_tools.send_assessors_cases(self._prepare_stats(run_task.assessors_cases, False))
        duty_tools.send_coverage_maps(self._prepare_stats(run_task.get_coverage_maps_metric(), False))

    def _prepare_stats(self, metrics, send_release_id=True):
        values = metrics
        if isinstance(metrics, dict):
            values = metrics.values()

        for value in values:
            value.update({
                'external_id': self.metrics_id,
            })
            if send_release_id:
                value.update({
                    'release_id': self.metrics_release_id,
                })

        return values
