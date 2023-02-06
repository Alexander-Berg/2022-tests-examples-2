# -*- coding: utf-8 -*-

from sandbox.projects.common import utils
from sandbox.projects.common.TestPerformanceBest import BaseTestPerformanceBestTask
from sandbox.projects.WizardTestPerformance import WizardTestPerformance
from sandbox.projects.common.wizard import utils as wizard_utils


class TestWizardPerformanceBest(BaseTestPerformanceBestTask):
    """
        Parallel run of wizard performance tasks with result aggregation
        :param number_of_runs: how many tests to execute
    """
    type = 'TEST_WIZARD_PERFORMANCE_BEST'
    client_tags = wizard_utils.ALL_SANDBOX_HOSTS_TAGS
    execution_space = 1 * 1024

    input_parameters = (
        BaseTestPerformanceBestTask.input_parameters +
        WizardTestPerformance.input_parameters
    )

    def _get_performance_task_type(self):
        return WizardTestPerformance.type

    def _get_default_cpu_model(self):
        # Filtered directly in WizardTestPerformance
        return ''

    def on_enqueue(self):
        wizard_utils.setup_hosts_sdk1(self)
        wizard_utils.on_enqueue(self)

    def on_execute(self):
        BaseTestPerformanceBestTask.on_execute(self)
        if utils.check_all_subtasks_done():
            self.ctx['rule_stats'] = rs = {}
            for task in self.list_subtasks(load=True):
                for rule, stats in task.ctx.get('rule_stats', {}).items():
                    target = rs.setdefault(rule, {'duration': 0.0, 'count': 0, 'ok': 0})
                    target['duration'] += stats['duration']
                    target['count'] += stats['count']
                    target['ok'] += stats['ok']


__Task__ = TestWizardPerformanceBest
