# -*- coding: utf-8 -*-
import sandbox.sandboxsdk.parameters as sdk_parameters

from sandbox.projects.TestFusionPerformance import TestFusionPerformance
from sandbox.projects.common.TestPerformanceBest import BaseTestPerformanceBestTask
from sandbox.projects.common.fusion.task import FusionParamsDescription


class ChildTasksPriorityParameter(sdk_parameters.SandboxStringParameter):
    name = 'child_tasks_prio'
    default_value = ''
    description = 'child tasks priority'


class TestFusionPerformanceBest(BaseTestPerformanceBestTask):
    """
        Multiple runs of ``TEST_FUSION_PERFORMANCE`` subtasks (number_of_runs param)
        The best result is displayed in the result table.
    """

    type = 'TEST_FUSION_PERFORMANCE_BEST'

    input_parameters = (
        BaseTestPerformanceBestTask.input_parameters +
        (ChildTasksPriorityParameter, ) +
        TestFusionPerformance.input_parameters
    )

    def _get_performance_task_type(self):
        return TestFusionPerformance.type

    def _get_subtasks_priority(self):
        prio_ctx = self.ctx.get(ChildTasksPriorityParameter.name)
        return prio_ctx.split('_') if prio_ctx else self.priority


TestFusionPerformanceBest.__doc__ += FusionParamsDescription

__Task__ = TestFusionPerformanceBest
