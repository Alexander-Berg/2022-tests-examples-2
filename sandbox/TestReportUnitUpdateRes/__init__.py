
# -*- coding: utf-8 -*-

import time

from sandbox.projects import resource_types
from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.errors import SandboxTaskFailureError
from sandbox.projects.common import apihelpers
from sandbox.sandboxsdk.channel import channel
import sandbox.projects.ReportDataRuntime as RDR
from sandbox.projects.report.common import Project


class TestReportUnitUpdateRes(SandboxTask, object):
    """
        Создает ресурс REPORT_DATA_RUNTIME для транка репорта
        и добавляет атрибут test_env_report_unit
        Это необходимо для автообновления ресурсов в testenv-е
    """

    type = 'TEST_REPORT_UNIT_UPDATE_RES'

    input_parameters = [Project]

    execution_space = 3000

    testenv_attr = 'test_env_report_unit'

    def on_execute(self):
        if 'subtask_ids' in self.ctx:
            task_id = self.ctx['subtask_ids']
            # проверить что таски корректно выполнились
            subtask = channel.sandbox.get_task(task_id)
            if not subtask.is_finished():
                raise SandboxTaskFailureError('Subtask {0} failed with status: {1}.'.format(subtask.id, subtask.status))

            # testenv обновляет ресурсы только с одинаковым значением атрибута
            # если есть несколько зависимых ресурсов, то чтобы testenv их обновил у ресурсов должно быть одинаковое
            # значение атрибута testenv_attr
            val = int(time.time())
            res = apihelpers.list_task_resources(task_id, resource_types.REPORT_DATA_RUNTIME, limit=1)[0]
            channel.sandbox.set_resource_attribute(res.id, self.testenv_attr, val)
        else:
            project = self.ctx[Project.name]
            sub_ctx = {
                RDR.Source.UseExpiredSource.name: True,
                Project.name: project,
            }
            # не делаем уведомления для дочерних задач
            sub_ctx['notify_via'] = ''
            sub_ctx["notifications"] = []

            # создаем REPORT_DATA_RUNTIME
            subtask = self.create_subtask(
                task_type=RDR.ReportDataRuntime.type,
                description="data.runtime for unit_tests(auto update)",
                input_parameters=sub_ctx,
                important=self.important
            )

            self.ctx['subtask_ids'] = subtask.id
            self.wait_all_tasks_completed(subtask.id)


__Task__ = TestReportUnitUpdateRes
