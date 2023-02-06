import logging
import unittest
from os.path import join as pj
import time

from robot.library.yuppie.modules.environment import Environment
from robot.library.yuppie.modules.tm import LocalTm
from robot.library.yuppie.modules.yt_mod import LocalYt
from yt.transfer_manager.client import TransferManager as TMClient
import yatest.common


class TestTm(unittest.TestCase):
    TEST_YT_USER = "test_tm_user"
    TEST_TABLE_PATH = "//{0}/test_table".format(TEST_YT_USER)
    TEST_DATA = [
        {"col0": "val00", "col1": "val10", "col2": "val20"},
        {"col0": "val01", "col1": "val11", "col2": "val21"},
        {"col0": "val02", "col1": "val12", "col2": "val22"}
    ]
    TASK_RETRY_MAX_COUNT = 3

    def setUp(self):
        env = Environment()

        logging.info("Starting YT A")

        self.yt_a = LocalYt(
            wait_tablet_cell_initialization=True,
            cell_tag=1,
            ram_drive_path=env.ram_drive_path,
            yt_work_dir=pj(env.ram_drive_path, "yt_a") if env.ram_drive_path else yatest.common.work_path("yt_a"),
            yt_work_dir_in_ram_drive=True
        )
        logging.info("YT A id: " + str(self.yt_a.yt_stuff.yt_id))

        client_a = self.yt_a.create_yt_client()
        client_a.create("table", TestTm.TEST_TABLE_PATH, recursive=True)
        client_a.write_table(TestTm.TEST_TABLE_PATH, TestTm.TEST_DATA)

        logging.info("Starting YT B")
        self.yt_b = LocalYt(
            wait_tablet_cell_initialization=True,
            cell_tag=2,
            ram_drive_path=env.ram_drive_path,
            yt_work_dir=pj(env.ram_drive_path, "yt_b") if env.ram_drive_path else yatest.common.work_path("yt_b"),
            yt_work_dir_in_ram_drive=True
        )
        logging.info("YT B id: " + str(self.yt_b.yt_stuff.yt_id))

        client_b = self.yt_b.create_yt_client()
        client_b.create("map_node", "//" + TestTm.TEST_YT_USER)

        logging.info("Initializing TM")
        self.tm = LocalTm(
            self.yt_a,
            self.yt_b,
            yt_a_name="yt_a",
            yt_b_name="yt_b"
        )

        logging.info("Starting TM")
        self.tm.start_local_tm()

        logging.info("Everything was started")

    def test_check_tm(self):
        self.tm_client = TMClient(
            "{0}:{1}".format(self.tm.get_host(), self.tm.get_port()),
            http_request_timeout=1000,
            enable_retries=True,
            token="test_token"
        )

        for try_num in range(TestTm.TASK_RETRY_MAX_COUNT):
            logging.info("Task try {} was started".format(try_num))
            try:
                self.tm_client.add_task(
                    "yt_a",
                    TestTm.TEST_TABLE_PATH,
                    "yt_b",
                    TestTm.TEST_TABLE_PATH,
                    sync=True
                )
            except Exception as ex:
                logging.info("Task try {0} is failed: {1}".format(try_num, ex))
                if try_num == TestTm.TASK_RETRY_MAX_COUNT - 1:
                    raise
                time.sleep(5)  # time to rest
            else:
                logging.info("Task try {} is succeeded".format(try_num))
                break

        client_b = self.yt_b.create_yt_client()
        transfered_data = list(client_b.read_table(TestTm.TEST_TABLE_PATH))
        self.assertTrue(transfered_data == TestTm.TEST_DATA)

    def tearDown(self):
        self.tm.down()


if __name__ == "__main__":
    unittest.main()
