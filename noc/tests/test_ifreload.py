import os
import textwrap
import unittest
import unittest.mock

import ifreload

from tests import mock_subprocess
from tests import utils



class TestIfreload(mock_subprocess.MockedSubprocessTestCase):
    version_id = ""
    os_release_content = ""

    def setUp(self):
        self._backup_version_id = os.environ.get("VERSION_ID")
        if self.version_id:
            os.environ["VERSION_ID"] = self.version_id
        super().setUp()

    def tearDown(self):
        del os.environ["VERSION_ID"]
        if self._backup_version_id is not None:
            os.environ["VERSION_ID"] = self._backup_version_id
        super().tearDown()


class TestIfreloadCumulus3(TestIfreload):
    version_id = "3.7.2"

    def test_cumulus_version_3(self):
        """Проверяет что ifreload выполнится при вызове ifreload.py"""
        utils.run_ifreload()

class TestIfreloadCumulus4(TestIfreload):
    version_id = "4.1.1"

    def test_cumulus_version_4(self):
        """Проверяет что ifreload НЕ выполнится при вызове ifreload.py"""
        utils.run_ifreload()


class TestIfreloadVersionId(unittest.TestCase):
    def test_version_id_parse(self):
        self.assertEqual(str(ifreload.VersionId.parse("1")), "VersionId(1)")
        self.assertEqual(str(ifreload.VersionId.parse("2.1")), "VersionId(2,1)")
        self.assertEqual(str(ifreload.VersionId.parse("0.0.0")), "VersionId(0,0,0)")
        self.assertEqual(str(ifreload.VersionId.parse("1.2.3")), "VersionId(1,2,3)")

    def test_version_cmp(self):
        self.assertTrue(ifreload.VersionId.parse("1") == ifreload.VersionId.parse("1"))
        self.assertTrue(ifreload.VersionId.parse("1") < ifreload.VersionId.parse("2"))
        self.assertTrue(ifreload.VersionId.parse("1.1.1") > ifreload.VersionId.parse("1.1"))
        self.assertTrue(ifreload.VersionId.parse("3.7.2") <= ifreload.VersionId.parse("4.1.1"))
        self.assertTrue(ifreload.VersionId.parse("3.7.2") <= ifreload.VersionId.parse("3.7.2"))
        self.assertTrue(ifreload.VersionId.parse("2.5") >= ifreload.VersionId.parse("2"))
        self.assertTrue(ifreload.VersionId.parse("2.5") >= ifreload.VersionId.parse("2.5"))


class TestIfreloadCumulusVersionFileBase(unittest.TestCase):
    os_version_content = ""

    def setUp(self):
        self._open_mock = unittest.mock.mock_open(read_data=self.os_version_content)
        self._open_patcher = unittest.mock.patch("builtins.open", self._open_mock)
        self._open_patcher.start()
        self._isfile_patcher = unittest.mock.patch("os.path.isfile", return_value=True)
        self._isfile_patcher.start()

    def tearDown(self):
        self._isfile_patcher.stop()
        self._open_patcher.stop()


class TestIfreloadCumulusVersionFile1(TestIfreloadCumulusVersionFileBase):
    os_version_content = textwrap.dedent("""
        NAME="Cumulus Linux"
        VERSION_ID=3.7.2
        VERSION="Cumulus Linux 3.7.2"
        PRETTY_NAME="Cumulus Linux"
        ID=cumulus-linux
        ID_LIKE=debian
        CPE_NAME=cpe:/o:cumulusnetworks:cumulus_linux:3.7.2
        HOME_URL="http://www.cumulusnetworks.com/"
        SUPPORT_URL="http://support.cumulusnetworks.com/"
        """)

    def test_cumulus_version(self):
        self.assertEqual(ifreload.cumulus_version(), ifreload.VersionId(3,7,2))


class TestIfreloadCumulusVersionFile2(TestIfreloadCumulusVersionFileBase):
    os_version_content = textwrap.dedent("""
        NAME="Cumulus Linux"
        VERSION_ID=4.1.1
        VERSION="Cumulus Linux 4.1.1"
        PRETTY_NAME="Cumulus Linux"
        ID=cumulus-linux
        ID_LIKE=debian
        CPE_NAME=cpe:/o:cumulusnetworks:cumulus_linux:4.1.1
        HOME_URL="http://www.cumulusnetworks.com/"
        SUPPORT_URL="http://support.cumulusnetworks.com/"
        """)

    def test_cumulus_version(self):
        self.assertEqual(ifreload.cumulus_version(), ifreload.VersionId(4,1,1))


class TestIfreloadSwitchdev(TestIfreloadCumulusVersionFileBase):
    os_version_content = textwrap.dedent("""
        NAME="Ubuntu"
        VERSION="18.04.6 LTS (Bionic Beaver)"
        ID=ubuntu
        ID_LIKE=debian
        PRETTY_NAME="Ubuntu 18.04.6 LTS"
        VERSION_ID="18.04"
        HOME_URL="https://www.ubuntu.com/"
        SUPPORT_URL="https://help.ubuntu.com/"
        BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
        PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
        VERSION_CODENAME=bionic
        UBUNTU_CODENAME=bionic
        VARIANT=nosu
        VARIANT_ID=1.0.3.18-5.14.0
        YNDX_IMG=0.1-5.14.0-8
        """)

    def test_cumulus_version(self):
        self.assertEqual(ifreload.cumulus_version(), None)
