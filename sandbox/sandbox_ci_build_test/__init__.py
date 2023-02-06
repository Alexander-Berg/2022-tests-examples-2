# -*- coding: utf-8 -*-

from sandbox.projects.sandbox_ci.task import BaseBuildTask


class SandboxCiBuildTest(BaseBuildTask):
    project_name = 'web4'

    github_context = 'build_test_task'
