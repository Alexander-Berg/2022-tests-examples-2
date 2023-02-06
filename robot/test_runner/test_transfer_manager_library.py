from transfer_manager.python.recipe.interface import TransferManagerTest
from yatest.common import binary_path, execute
import pytest


test_app_cmd = binary_path("robot/jupiter/library/transfer_manager/test/test_app/test_app")


class TestTransferManagerCppApi(TransferManagerTest):
    def run_test_suite(self, suite):
        (tm_host, tm_port) = self.tm_proxy.rsplit(":", 1)
        cmd = [test_app_cmd, "--test-suite", suite, "--cluster", self.first_cluster,
               "--cluster", self.second_cluster, "--tm-host", tm_host, "--tm-port", tm_port]
        execute(cmd)

    @pytest.mark.flaky(max_runs=10)
    def test_transfer_tables(self):
        self.run_test_suite("transfer_tables")

    @pytest.mark.flaky(max_runs=10)
    def test_transfer_directory(self):
        self.run_test_suite("transfer_directory")

    def test_same_cluster_copy(self):
        self.run_test_suite("same_cluster_copy")
