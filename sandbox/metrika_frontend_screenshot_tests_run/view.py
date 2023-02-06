# coding=utf-8

from sandbox import sdk2
from sandbox.projects.metrika.admins.base_metrika_tests import view


class ViewModel(view.ViewModel):
    @property
    def allure_link(self):
        return "{}/index.html".format(
            sdk2.Resource[self.task.Parameters.report_resource.id].http_proxy)
