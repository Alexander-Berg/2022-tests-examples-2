# -*- coding: utf-8 -*-

from sandbox.projects.common import error_handlers as eh
import sandbox.projects.common.proxy_wizard.Responses as PWR


class TestProxyWizardsRequests(PWR.ProxyWizardResponses):
    type = 'TEST_PROXY_WIZARDS_REQUESTS'

    def on_after_execute(self, queries, responses1, responses2):
        self.write_diff_result(queries, responses1, responses2)

        if self.ctx['num_of_diffs']:
            eh.check_failed(
                'Output is not equal. Number of diffs: "{}"\n'
                'See PROXY_WIZARD_RESPONSES_COMPARE_RESULT resource for more info'.format(self.ctx['num_of_diffs'])
            )


__Task__ = TestProxyWizardsRequests
