import logging
import os
import unittest

from sandbox.projects.browser.monitoring import config


class TestMonitorConfigLoader(unittest.TestCase):
    def test_all_configs(self):
        import yatest.common
        task_dir = os.path.join(yatest.common.test_source_path(), os.pardir)
        config_dir = os.path.join(task_dir, 'config')
        yql_templates_dir = os.path.join(task_dir, 'yql-templates')

        configs = config.MonitorConfigLoader.available_configs(config_dir)
        assert configs
        for choice_name, config_path in configs.iteritems():
            logging.warning('%s: %s', choice_name, config_path)
            # Check config can be loaded using standard method.
            config.MonitorConfigLoader.load_config(config_path, yql_templates_dir)
