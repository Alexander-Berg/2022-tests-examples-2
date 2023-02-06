import allure
import logging
import pprint

logger = logging.getLogger(__name__)


class MockAgentApi:
    def __init__(self):
        self._ping_result = True
        self._host_status_response = None
        self._unloading_status_response = None
        self._loading_initiate_status_response = None
        self._loading_status_response = None
        self._loading_finalize_status_response = None
        self._after_loading_status_response = None
        self.start_loading_initiate_calls = 0
        self.stop_loading_initiate_calls = 0
        self.start_loading_finalize_calls = 0
        self.stop_loading_finalize_calls = 0
        self.start_unloading_calls = 0

    @property
    def ping_result(self):
        allure.attach("MockAgentApi get ping_result", pprint.pformat(self._ping_result))
        return self._ping_result

    @ping_result.setter
    def ping_result(self, value):
        self._ping_result = value
        allure.attach("MockAgentApi set ping_result", pprint.pformat(value))

    @property
    def host_status_response(self):
        allure.attach("MockAgentApi get host_status_response", pprint.pformat(self._host_status_response))
        return self._host_status_response

    @host_status_response.setter
    def host_status_response(self, value):
        self._host_status_response = value
        allure.attach("MockAgentApi set host_status_response", pprint.pformat(value))

    @property
    def unloading_status_response(self):
        allure.attach("MockAgentApi get unloading_status_response", pprint.pformat(self._unloading_status_response))
        return self._unloading_status_response

    @unloading_status_response.setter
    def unloading_status_response(self, value):
        self._unloading_status_response = value
        allure.attach("MockAgentApi set unloading_status_response", pprint.pformat(value))

    @property
    def loading_status_response(self):
        allure.attach("MockAgentApi get loading_status_response", pprint.pformat(self._loading_status_response))
        return self._loading_status_response

    @loading_status_response.setter
    def loading_status_response(self, value):
        self._loading_status_response = value
        allure.attach("MockAgentApi set loading_status_response", pprint.pformat(value))

    @property
    def loading_initiate_status_response(self):
        allure.attach("MockAgentApi get loading_initiate_status_response", pprint.pformat(self._loading_initiate_status_response))
        return self._loading_initiate_status_response

    @loading_initiate_status_response.setter
    def loading_initiate_status_response(self, value):
        self._loading_initiate_status_response = value
        allure.attach("MockAgentApi set loading_initiate_status_response", pprint.pformat(value))

    @property
    def loading_finalize_status_response(self):
        allure.attach("MockAgentApi get loading_finalize_status_response:", pprint.pformat(self._loading_finalize_status_response))
        return self._loading_finalize_status_response

    @loading_finalize_status_response.setter
    def loading_finalize_status_response(self, value):
        self._loading_finalize_status_response = value
        allure.attach("MockAgentApi set loading_finalize_status_response:", pprint.pformat(value))

    @property
    def after_loading_status_response(self):
        allure.attach("MockAgentApi get after_loading_status_response", pprint.pformat(self._after_loading_status_response))
        return self._after_loading_status_response

    @after_loading_status_response.setter
    def after_loading_status_response(self, value):
        self._after_loading_status_response = value
        allure.attach("MockAgentApi set after_loading_status_response", pprint.pformat(value))

    @allure.step("MockAgentApi Constructor call")
    def __call__(self, *args, **kwargs):
        return self

    @allure.step("MockAgentApi.ping")
    def ping(self):
        return self.ping_result

    @allure.step("MockAgentApi.get_status")
    def get_status(self):
        if self.start_loading_initiate_calls > 0 and self.after_loading_status_response is not None:
            return self.after_loading_status_response
        return self.host_status_response

    @allure.step("MockAgentApi.get_unloading_status")
    def get_unloading_status(self):
        return self.unloading_status_response

    @allure.step("MockAgentApi.start_unloading")
    def start_unloading(self):
        self.start_unloading_calls += 1

    @allure.step("MockAgentApi.get_loading_status")
    def get_loading_status(self):
        return self.loading_status_response

    @allure.step("MockAgentApi.get_loading_initiate_status")
    def get_loading_initiate_status(self):
        return self.loading_initiate_status_response

    @allure.step("MockAgentApi.start_loading_initiate")
    def start_loading_initiate(self):
        self.start_loading_initiate_calls += 1

    @allure.step("MockAgentApi.stop_loading_initiate")
    def stop_loading_initiate(self):
        self.stop_loading_initiate_calls += 1

    @allure.step("MockAgentApi.get_loading_finalize_status")
    def get_loading_finalize_status(self):
        return self.loading_finalize_status_response

    @allure.step("MockAgentApi.start_loading_finalize")
    def start_loading_finalize(self):
        self.start_loading_finalize_calls += 1

    @allure.step("MockAgentApi.stop_loading_finalize")
    def stop_loading_finalize(self):
        self.stop_loading_finalize_calls += 1
