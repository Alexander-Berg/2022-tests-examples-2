from sandbox import sdk2


class UnitTestTask2(sdk2.Task):
    """ Non-service task for unit tests """

    name = "UNIT_TEST_2"

    def on_execute(self):
        pass
