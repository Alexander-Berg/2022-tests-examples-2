# -*- coding: utf-8 -*-

from sandbox.projects.ab_testing.deploying.Tests.TestCIExperimentsReleaseBaseRunner import AbDeployingTestCIExperimentsReleaseBaseRunner
from sandbox.projects.sandbox_ci.sandbox_ci_fiji_experiments.release_runner import SandboxCiFijiExperimentsReleaseRunner


class AbDeployingTestFijiExperimentsReleaseImagesRunner(AbDeployingTestCIExperimentsReleaseBaseRunner):
    '''
        AB deployment Fiji images test
    '''

    def get_ci_task(self):
        return SandboxCiFijiExperimentsReleaseRunner(
            self,
            description='running automatic ab deployment fiji images test by {} [{}]'.format(self.type, self.id),
            test_id=self.Parameters.testid,
            release='latest',
            tests_source='dev',
            platforms=['desktop', 'touch-pad', 'touch-phone'],
            service='images',
            owner='SANDBOX_CI_SEARCH_INTERFACES',
            hermionee2e_base_url='https://yandex.ru',
        )
