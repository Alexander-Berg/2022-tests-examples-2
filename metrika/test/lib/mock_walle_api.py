import allure
import pprint
import walle_api.constants


class MockWalleApi:
    def __init__(self):
        self.host_response = None

    @allure.step
    def set_ready_response(self):
        self.host_response = {"status": walle_api.constants.HostStatus.READY}

    @allure.step
    def set_switching_response(self):
        self.host_response = {"status": walle_api.constants.HostStatus.SWITCHING_TO_ASSIGNED}

    @allure.step
    def set_dead_response(self):
        self.host_response = {"status": walle_api.constants.HostStatus.DEAD}

    @allure.step("MockWalleApi Constructor call")
    def __call__(self, url=None, access_token=None, name=None):
        return self

    @allure.step("MockWalleApi get_host host_id: {1}")
    def get_host(self, host_id, resolve_deploy_configuration=False, fields=None):
        allure.attach("Wall-E response", pprint.pformat(self.host_response))
        return self.host_response
