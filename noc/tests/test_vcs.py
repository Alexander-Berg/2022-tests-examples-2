import os
import shutil
import tempfile
import unittest
from subprocess import check_call

from django import test

from l3common.utils import chdir
from l3mgr.utils.vcs import CVS
from l3mgr.utils.vcs import CVSExecutionError

_TEST_FILE_DATA = """---
# ns1.yandex.ru
ns1.yandex.net:
  ips:
    - 2a02:6b8:a::a
    - 5.255.255.5
    - 77.88.55.80
    - 77.88.55.88
  chain_name: ns1.y.ru
---
new-service.yandex.net:
  ips: ['2a02:6b8::', 87.250.250.0]
"""

EXCEPTION_MSG = """Failed 'cvs checkout': cvs checkout: cannot find module `non-existing-vcs-file' - ignored
:
stderr=cvs checkout: cannot find module `non-existing-vcs-file' - ignored

stdout="""


class CVSTest(test.SimpleTestCase):
    FILENAME = "noc/balancers/iptables/testenv-services.yaml"
    ROOT = "/opt/CVSROOT"
    _test_cvs_root_dir = None

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        try:
            check_call(["cvs", "--version"])
        except FileNotFoundError as e:
            raise unittest.SkipTest("cvs client is not installed") from e

        cls._test_cvs_root_dir: str = tempfile.mkdtemp()
        check_call(["cvs", "-d", cls._test_cvs_root_dir, "init"])

        with tempfile.TemporaryDirectory(prefix="test-cvs-source") as d:
            path_parts = os.path.split(cls.FILENAME)
            repository = path_parts[0]

            file_path: str = os.path.join(d, *path_parts[1:])
            dir_path: str = os.path.dirname(file_path)
            os.makedirs(dir_path, exist_ok=True)
            with open(file_path, "w+") as f:
                f.write(_TEST_FILE_DATA)

            check_call(
                [
                    "cvs",
                    "-d",
                    cls._test_cvs_root_dir,
                    "import",
                    "-m",
                    "some test file",
                    repository,
                    "vendortar",
                    "releasetag",
                ],
                cwd=d,
            )

        cls.ROOT: str = "%s" % cls._test_cvs_root_dir

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls._test_cvs_root_dir)
        super().tearDownClass()

    def setUp(self) -> None:
        self.cvs = CVS(self.ROOT)

    def tearDown(self) -> None:
        try:
            os.unlink(self.FILENAME)
        except FileNotFoundError:
            pass
        super().tearDown()

    def test_checkout(self):
        with tempfile.TemporaryDirectory(prefix="test-cvs-checkout") as d, chdir(d):
            self.cvs.checkout(self.FILENAME)
            self.assertTrue(os.path.isfile(self.FILENAME), "File wasn't checked out")

    def test_checkout_to_dir(self):
        with tempfile.TemporaryDirectory(prefix="test-cvs-dir") as d, chdir(d):
            directory: str = "test-cvs-dir"
            self.cvs.checkout(self.FILENAME, directory)

            filepath: str = os.path.join(directory, os.path.basename(self.FILENAME))
            self.assertTrue(os.path.isfile(filepath), "File wasn't checked out")

    def test_diff(self):
        with tempfile.TemporaryDirectory(prefix="test-cvs-diff") as d, chdir(d):
            self.cvs.checkout(self.FILENAME)
            self.assertTrue(os.path.isfile(self.FILENAME), "File wasn't checked out")
            self.assertFalse(self.cvs.is_file_changed(self.FILENAME), "Diff return True on expected False")

            with open(self.FILENAME, "w") as fh:
                fh.write("test string only")

            self.assertTrue(self.cvs.is_file_changed(self.FILENAME), "File was changed but diff return 0")

    def test_pipe_call(self):
        with tempfile.TemporaryDirectory(prefix="test-cvs-diff") as d:
            CVS(self.ROOT, cwd=d).checkout(self.FILENAME)
            self.assertTrue(os.path.isfile(os.path.join(d, self.FILENAME)), "File wasn't checked out")

    def test_exception_message_data(self):
        with tempfile.TemporaryDirectory(prefix="test-cvs-diff") as d, chdir(d):
            with self.assertRaises(CVSExecutionError) as cvs_exc:
                self.cvs.checkout("non-existing-vcs-file")
            cvs_exception = cvs_exc.exception
            self.assertEqual(str(cvs_exception), EXCEPTION_MSG)
