# w -*- coding: utf-8 -*-

import logging

from sandbox import common

from sandbox.projects.common import apihelpers
from sandbox.sandboxsdk.svn import Arcadia
from sandbox.sandboxsdk.parameters import LastReleasedResource, SandboxArcadiaUrlParameter
from sandbox.sandboxsdk.channel import channel
from sandbox.projects import resource_types
from sandbox.projects.common.search.components import DefaultUpperSearchParams
from sandbox.projects import TestReportUnit as TRU
from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.errors import SandboxTaskFailureError


class ArcadiaUrl(TRU.ArcadiaUrl):
    pass


class ArcadiaUrlPrev(TRU.ArcadiaUrl):
    name = 'svn_url_prev'
    description = 'Arcadia url for previous report:'
    default_value = SandboxArcadiaUrlParameter.default_value + '/web/report@1577060'


class ShootLog(LastReleasedResource):
    name = 'prepared_log'  # store access_log_parsed in root dir
    description = 'ShootLogPrepare:'
    resource_type = resource_types.SHOOT_LOG_PREPARE

    @common.utils.classproperty
    def default_value(cls):
        return next(
            iter(channel.sandbox.server.last_resources(resource_types.SHOOT_LOG_PREPARE.name)),
            {'id': None}
        )['id']


class TestReportContext(SandboxTask):
    """
       Сравнивает контексты двух репортов
    """

    type = 'TEST_REPORT_CONTEXT'
    execution_space = 900

    DefaultUpperSearchParams.ReportTemplatesParameter.name = 'report_templates'

    input_parameters = [ArcadiaUrl, ArcadiaUrlPrev, ShootLog]

    def on_execute(self):

        if 'prev_task_id' not in self.ctx:
            prev_task = self.create_mysubtask(self.ctx['svn_url_prev'], self.ctx['prepared_log'])
            logging.info("Created prev task with id %d for url=%s" % (prev_task.id, self.ctx['svn_url_prev']))
            self.ctx['prev_task_id'] = prev_task.id
            self.wait_task_completed(prev_task.id)
        else:
            subtask = channel.sandbox.get_task(self.ctx['prev_task_id'])
            if not subtask.is_finished():
                raise SandboxTaskFailureError("First subtask #{0.id} '{0.description}' failed with status {0.status}".format(subtask))

            prev_task_resource = apihelpers.get_last_resource(resource_types.TEST_REPORT_PERFORMANCE, {'task_id': self.ctx['prev_task_id']})

        if 'task_id' not in self.ctx:
            task = self.create_mysubtask(self.ctx['svn_url'], self.ctx['prepared_log'], prev_task_resource.id)
            logging.info("Created task with id %d for url=%s" % (task.id, self.ctx['svn_url']))
            self.ctx['task_id'] = task.id
            self.wait_task_completed(task.id)
        else:
            task = channel.sandbox.get_task(self.ctx['task_id'])
            if not task.is_finished():
                raise SandboxTaskFailureError("Second subtask #{0.id} '{0.description}' failed with status {0.status}".format(task))

        self.ctx['yabs_diff'] = task.ctx['yabs_diff']

        if self.ctx['yabs_diff']:
            self.ctx['yabs_diff_resource_id'] = task.ctx['yabs_diff_resource_id']
            logging.info("GOT NON_EMPTY yabs_diff")
            arc_info = Arcadia.info(self.ctx['svn_url'])

            mail_to = '%s@yandex-team.ru' % arc_info['author']
            mail_cc = ''
            mail_subject = "%s, your commit %s probably brokens yabs context" % (arc_info['author'], arc_info['commit_revision'])
            mail_body = ''

            mail_body += "commit author: %s\n" % arc_info['author']
            mail_body += "commit revision: %s\n" % arc_info['commit_revision']
            mail_body += "https://arc.yandex-team.ru/wsvn/arc/?op=revision&rev=%s\n" % arc_info['commit_revision']
            mail_body += "diff size: %d lines\n" % self.ctx['yabs_diff']
            mail_body += "\ndiff: " + channel.sandbox.get_resource_http_links(self.ctx['yabs_diff_resource_id'])[0]
            mail_body += "\ntask: " + self.http_url()

            logging.info("\nmail_to: %s\nmail_cc: %s\nmail_subject: %s\n\nmail_body: %s\n" % (mail_to, mail_cc, mail_subject, mail_body))
            channel.sandbox.send_email(mail_to, mail_cc, mail_subject, mail_body, content_type='text/plain', charset='utf-8')

    def create_mysubtask(self, url, log, prev_res_id=None):
        task_ctx = {}
        task_ctx['svn_url'] = url
        task_ctx['threshold'] = 1
        task_ctx['prepared_log'] = log
        task_ctx['arch_param'] = ''
        if (prev_res_id is not None):
            task_ctx['cmp_ctx_prev_shoot_result'] = prev_res_id
            logging.info("Created DIFF task with prev_res_id %d for url=%s" % (prev_res_id, url))

        task = self.create_subtask(task_type='TEST_REPORT_PERFORMANCE',
                                   input_parameters=task_ctx,
                                   description='Ctx dump for %s' % url)
        return task


__Task__ = TestReportContext
