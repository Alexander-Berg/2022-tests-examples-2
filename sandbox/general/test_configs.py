class UITestConfig(object):
    """
    Class with service parameters in order to run ReleaseMachineSiteMonitoring test.
    """
    # service_name - service to run tests
    service_name = ""

    # emergency_chat - chat name for emergency notifications, should be one of keys from https://ya.cc/t/bwFIuPJgd85rX
    emergency_chat = ""

    @staticmethod
    def import_selenium_tests():
        """
        Here should be UI tests import in order to overcome Sandbox import restriction

        :return: selenium_test file for chosen service, should contain `test_all` method
        """
        raise NotImplementedError


class ReleaseMachineUITestConfig(UITestConfig):
    service_name = "release_machine"
    emergency_chat = "rm_emergency"

    @staticmethod
    def import_selenium_tests():
        import release_machine.release_machine.ui_tests.test_all as selenium_test
        return selenium_test


class CoresUITestConfig(UITestConfig):
    service_name = "cores"
    emergency_chat = "cores_emergency"

    @staticmethod
    def import_selenium_tests():
        import infra.cores.ui_tests as selenium_test
        return selenium_test


SERVICES_TO_TEST = {
    service_test_config.service_name: service_test_config
    for service_test_config in [ReleaseMachineUITestConfig, CoresUITestConfig]
}
