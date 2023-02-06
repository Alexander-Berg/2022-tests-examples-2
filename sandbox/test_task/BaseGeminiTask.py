# -*- coding: utf-8 -*-

import os

from sandbox.projects.sandbox_ci.task.test_task.BaseTestTask import BaseTestTask


class BaseGeminiTask(BaseTestTask):
    class Requirements(BaseTestTask.Requirements):
        cores = 8
        ram = 16384

        class Caches(BaseTestTask.Requirements.Caches):
            pass

    tool = 'gemini'

    @property
    def run_cmd(self):
        return 'node_modules/.bin/gemini test'

    @property
    def run_opts(self):
        return '--reporter vflat {}'.format(super(BaseGeminiTask, self).run_opts)

    def set_environments(self):
        super(BaseGeminiTask, self).set_environments()

        os.environ['gemini_faildump_enabled'] = 'true'
