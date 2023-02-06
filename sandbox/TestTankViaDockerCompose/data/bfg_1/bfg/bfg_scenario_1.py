import os

import logging

log = logging.getLogger(__name__)


class LoadTest(object):
    def __init__(self, gun):
        # you'll be able to call gun's methods using this field:
        self.gun = gun

        # for example, you can get something from the 'ultimate' section of a config file:
        self.my_var = self.gun.get_option("init_param", "hello")
        log.info("Taken %s as a parameter init_param from tank config", self.my_var)

    def case1(self, missile):
        # we use gun's measuring context to measure time.
        # The results will be aggregated automatically:
        with self.gun.measure("case1"):
            log.info("Shoot case 1: %s", missile)

        # there could be multiple steps in one scenario:
        with self.gun.measure("case1_step2") as sample:
            log.info("Shoot case 1, step 2: %s", missile)
            # and we can set the fields of measured object manually:
            sample["proto_code"] = 500
            sample["net_code"] = 71
            sample["interval_real"] = 1000000  # 1 s
            sample["connect_time"] = 1000  # 1 ms
            sample["send_time"] = 9000  # 9ms
            sample["latency"] = 980000  # 980 ms
            sample["receive_time"] = 10000  # 10 ms


            # the list of available fields is below

    def case2(self, missile):
        with self.gun.measure("case2"):
            log.info("Shoot case 2: %s", missile)

    def default(self, missile):
        with self.gun.measure("default_case"):
            log.info("Shoot missile without case: %s", missile)

    def setup(self, gun):
        ''' this will be executed in each worker before the test starts '''
        log.info("Setting up LoadTest with init_param: %s", self.my_var)

    def teardown(self):
        ''' this will be executed in each worker after the end of the test '''
        log.info("Tearing down LoadTest")
        # It's mandatory to explicitly stop worker process in teardown
        os._exit(0)
        return 0
