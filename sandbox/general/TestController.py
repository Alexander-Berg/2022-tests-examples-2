class TestController:
    def __init__(self, component, controller):
        self.controller_name = controller
        self.component = component
        self._test_cases = []
        self.tc_idx = 1

    def add_test_case(self, test_case):
        if test_case:
            test_case.id = self.tc_idx
            self._test_cases.append(test_case)
            self.tc_idx += 1

    def get_test_cases(self):
        return self._test_cases

    def __str__(self):
        return_string = '\nComponent: {}\nTest for {} controller\n'.format(self.component, self.controller_name)
        for test_case in self._test_cases:
            return_string += str(test_case)
        return return_string
