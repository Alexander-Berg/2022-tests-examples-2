# -*- coding: utf-8 -*-

from sandbox.projects.TestFusionPerformance import TestFusionPerformance
from sandbox.projects.common.TestPerformanceBest import BaseTestPerformanceBestTask
from sandbox.projects.common.fusion.task import FusionParamsDescription


class TestRefreshPerformanceBest(BaseTestPerformanceBestTask):
    """
        Multiple runs of ``TEST_FUSION_PERFORMANCE`` subtasks (number_of_runs param)
        The best result is displayed in the result table.
    """

    type = 'TEST_REFRESH_PERFORMANCE_BEST'

    input_parameters = (
        BaseTestPerformanceBestTask.input_parameters +
        TestFusionPerformance.input_parameters
    )

    def _get_performance_task_type(self):
        return TestFusionPerformance.type


TestRefreshPerformanceBest.__doc__ += FusionParamsDescription

__Task__ = TestRefreshPerformanceBest
