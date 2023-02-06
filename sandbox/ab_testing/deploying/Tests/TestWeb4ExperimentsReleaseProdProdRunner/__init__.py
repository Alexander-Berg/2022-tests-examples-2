# -*- coding: utf-8 -*-

from sandbox.projects.ab_testing.deploying.Tests.TestCIExperimentsReleaseBaseRunner import AbDeployingTestCIExperimentsReleaseBaseRunner
from sandbox.projects.sandbox_ci.sandbox_ci_web4_experiments.release_runner import SandboxCiWeb4ExperimentsReleaseRunner


class AbDeployingTestWeb4ExperimentsReleaseProdProdRunner(AbDeployingTestCIExperimentsReleaseBaseRunner):
    '''
        AB deployment Web Test prod-prod
    '''

    def get_ci_task(self):
        return SandboxCiWeb4ExperimentsReleaseRunner(
            self,
            description='running automatic ab deployment prod-prod test by {} [{}]'.format(self.type, self.id),
            test_id=self.Parameters.testid,
            allow_data_flags=True,
            release='latest',
            owner='SANDBOX_CI_SEARCH_INTERFACES',
            hermionee2e_base_url='https://yandex.ru',
            tests_source='nothing',
        )
