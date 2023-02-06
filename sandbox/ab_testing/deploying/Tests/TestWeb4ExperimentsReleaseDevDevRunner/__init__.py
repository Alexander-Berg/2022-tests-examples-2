# -*- coding: utf-8 -*-

from sandbox.projects.ab_testing.deploying.Tests.TestCIExperimentsReleaseBaseRunner import AbDeployingTestCIExperimentsReleaseBaseRunner
from sandbox.projects.sandbox_ci.sandbox_ci_web4_experiments.release_runner import SandboxCiWeb4ExperimentsReleaseRunner


class AbDeployingTestWeb4ExperimentsReleaseDevDevRunner(AbDeployingTestCIExperimentsReleaseBaseRunner):
    '''
        AB deployment Web Test dev-dev
    '''

    class Parameters(AbDeployingTestCIExperimentsReleaseBaseRunner.Parameters):
        max_restarts = 0  # was 1 by USEREXP-6436, but removed by USEREXP-6801

    def get_ci_task(self):
        return SandboxCiWeb4ExperimentsReleaseRunner(
            self,
            description='running automatic ab deployment dev-dev test by {} [{}]'.format(self.type, self.id),
            test_id=self.Parameters.testid,
            allow_data_flags=True,
            release='specify',
            project_git_base_ref='dev',
            owner='SANDBOX_CI_SEARCH_INTERFACES',
            hermionee2e_base_url='https://renderer-web4-dev.hamster.yandex.ru',
            tests_source='dev',
        )
