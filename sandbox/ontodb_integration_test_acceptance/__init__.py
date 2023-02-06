# -*- coding: utf-8 -*-
import logging
import json

from sandbox import sdk2
from sandbox.common import errors


INTEGRATION_TEST_RESULTS_WAIT_DURATION_SECONDS = 10 * 60 * 60


class RunOntodbIntegrationTest(sdk2.Task):
    """ Task to start and track ontodb integration test """

    class Parameters(sdk2.Parameters):
        kill_timeout = INTEGRATION_TEST_RESULTS_WAIT_DURATION_SECONDS

        with sdk2.parameters.Output():
            verdict_is_testing_passed = sdk2.parameters.Bool(
                'Is testing passed',
                description='parsed from result json',
                default=False,
                required=True
            )

    def _init_testing(self):
        self.Context.is_testing_inited = True
        logging.info('Testing started')

    def _report_results(self):
        if not self.Context.test_results:
            raise errors.TaskFailure('No results in context!')

        test_results = self._get_test_results_object()
        self.Parameters.verdict_is_testing_passed = bool(test_results['verdict'])

    def _get_test_results_object(self):
        return json.loads(self.Context.test_results or '""')

    def on_execute(self):
        with self.memoize_stage.init_testing(commit_on_entrance=False):
            self._init_testing()

        with self.memoize_stage.wait_test():
            raise sdk2.WaitTime(INTEGRATION_TEST_RESULTS_WAIT_DURATION_SECONDS)

        self._report_results()

    @property
    def footer(self):
        start_str = '<b>Testing started</b>: ' + str(self.Context.is_testing_inited or False)
        verdict_str = '<b>Testing passed</b>: ' + str(self.Parameters.verdict_is_testing_passed or False)

        full_report_str = '<b>Full report</b>: '
        full_report_object_strings = json.dumps(self._get_test_results_object(), indent=4).split('\n')

        return '<br/>'.join(
            [
                start_str,
                verdict_str,
                full_report_str
            ] + full_report_object_strings
        )
