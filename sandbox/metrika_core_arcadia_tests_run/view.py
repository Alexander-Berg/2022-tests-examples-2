from sandbox import sdk2
import sandbox.projects.metrika.admins.base_metrika_tests.view as base_view


class ViewModel(base_view.ViewModel):
    @property
    def allure_link(self):
        return "{}/index.html".format(sdk2.Resource[self.task.Parameters.report_resource.id].http_proxy)
