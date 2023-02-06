# -*- coding: utf-8 -*-
from sandbox.projects import TestPeoplesearchTool


class SetupPylibParameters(TestPeoplesearchTool.SetupParameters):
    default_value = '--skip_social_users --skip_crawler --skip_suggest --skip_viewer --testing_data pylib_dir'


class TestPeoplesearchPylib(TestPeoplesearchTool.TestPeoplesearchTool):
    """
        запускает тесты модулей библиотеки python для Social Users и Social Crawler,
    """
    type = 'TEST_PEOPLESEARCH_PYLIB'

    def on_enqueue(self):
        if not self.ctx[TestPeoplesearchTool.TestingCmdParameter.name]:
            self.ctx[TestPeoplesearchTool.TestingCmdParameter.name] = \
                '{self.pylib_dir}/tests/launch_all_tests.py -c {self.ppl_configs_dir}'
            self.ctx[TestPeoplesearchTool.TestDataSvnPathParameter.name] = \
                'arcadia_tests_data/yweb/peoplesearch/social_users/pylib'
        TestPeoplesearchTool.on_enqueue(self)
