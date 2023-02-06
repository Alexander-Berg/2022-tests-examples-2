# coding: utf-8

import logging
from sandbox.projects.adfox.adfox_ui.autotest import AdfoxUiTest
from sandbox.projects.partner.tasks.docker_hermione import DockerHermione, SourceType
from sandbox.projects.partner.tasks.e2e_tests.e2e_all_tests.stands_manager import StandsManager
from sandbox.projects.partner.tasks.misc import parse_docker_image_name


class TestManager(StandsManager):
    class Context(StandsManager.Context):
        pass

    class Parameters(StandsManager.Parameters):
        pass

    def run_adfox_tests(self):
        logging.debug('TestManager.run_adfox_tests')
        task = AdfoxUiTest(
            self,
            gitBranch=self.Parameters.adfox_branch,
            piFrontendTag=self.Context.frontend_image_tag,
            piBackendTag=self.Parameters.backend_deb_version,
            javaTag=self.Parameters.java_docker_images.split(';')[0].split(':')[1],
        )
        return self.run_subtask_env_aware(task)

    def run_pi_tests(self):
        logging.debug('TestManager.run_pi_tests')

        frontend_source_type = SourceType.TAG if self.Parameters.use_custom_frontend_image else SourceType.BRANCH
        frontend_tag = self.parse_tag(self.Parameters.frontend_image)
        java_source_type = SourceType.TAG if self.Parameters.use_custom_java else SourceType.BRANCH
        java_tag = self.parse_tag(self.Parameters.java_docker_images, True)
        perl_source_type = SourceType.TAG if self.Parameters.use_custom_deb_version else SourceType.BRANCH

        # PI autotests task should notify its own progress and status
        task = DockerHermione(
            self,
            callback_url=self.Parameters.callback_url,
            callback_params=self.Parameters.callback_params,
            frontend_branch=self.Parameters.yharnam_source,
            frontend_source_type=frontend_source_type,
            frontend_tag=frontend_tag,
            java_branch=self.Parameters.java_branch,
            java_source_type=java_source_type,
            java_tag=java_tag,
            perl_branch=self.Parameters.partner_branch,
            perl_source_type=perl_source_type,
            perl_tag=self.Parameters.backend_deb_version,
            priority=self.Parameters.priority,
            adfox_git_branch=self.Parameters.adfox_branch,
            is_release=self.Parameters.is_release,
            st_issue=self.Parameters.st_issue
        )

        return self.run_subtask_env_aware(task)

    def parse_tag(self, image_name, is_multiple_images=False):
        if image_name:
            if is_multiple_images:
                image_name = image_name.split(';')[0]

            _, tag, _ = parse_docker_image_name(image_name, '')

            return tag

        return ''
