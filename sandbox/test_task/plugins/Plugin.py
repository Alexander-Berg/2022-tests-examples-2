# -*- coding: utf-8 -*-


class Plugin(object):
    def __init__(self, task):
        self._task = task

    def set_env(self):
        pass

    def make_reports(self, status, common_attributes):
        register_reports_in_parallel = self._task.config.get_deep_value(['tests', self._task.tool, 'register_reports_in_parallel'], False)

        self._task.artifacts.create_reports(self.get_reports_attrs(status, common_attributes), parallel=register_reports_in_parallel)

    def get_reports_attrs(self, status, common_attributes):
        pass

    def validate_result(self):
        pass
