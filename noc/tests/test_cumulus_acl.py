from tests import mock_subprocess
from tests import utils


class TestCumulusAcl(mock_subprocess.MockedSubprocessTestCase):
    """Проверяет релоад `acltool.service` при изменении файлов в `/etc/cumulus/acl/policy.d`."""

    def test_00control_plane_cuml3(self):
        """Проверяет изменение файла `00control_plane_catch_all.rules`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.cumulus.control_plane_zero.CumulusCopp00`
        """
        utils.run_commit_reload()

    def test_00control_plane_cuml4(self):
        """Проверяет изменение файла `00control_plane_catch_all.rules`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.cumulus.control_plane_zero.CumulusCopp00`
        """
        utils.run_commit_reload()

    def test_99control_plane_cuml3(self):
        """Проверяет изменение файла `99control_plane_catch_all.rules`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.cumulus.control_plane_nine.CumulusCopp99`
        """
        utils.run_commit_reload()

    def test_99control_plane_cuml4(self):
        """Проверяет изменение файла `99control_plane_catch_all.rules`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.cumulus.control_plane_nine.CumulusCopp99`
        """
        utils.run_commit_reload()

    def test_mgmt_cuml3(self):
        """Проверяет изменение файла `mgmt.rules`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.cumulus.copp.CumulusCopp`
        """
        utils.run_commit_reload()

    def test_mgmt_cuml4(self):
        """Проверяет изменение файла `mgmt.rules`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.cumulus.copp.CumulusCopp`
        """
        utils.run_commit_reload()

    def test_project_id_cuml3(self):
        """Проверяет изменение файла `project_id_acl.rules`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.cumulus.project_id_acl.CumulusACLs`
        """
        utils.run_commit_reload()

    def test_project_id_cuml4(self):
        """Проверяет изменение файла `project_id_acl.rules`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.cumulus.project_id_acl.CumulusACLs`
        """
        utils.run_commit_reload()

    def test_remark_cuml3(self):
        """Проверяет изменение файла `remark.rules`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.cumulus.qos.CumulusQosMarking`
        """
        utils.run_commit_reload()

    def test_remark_cuml4(self):
        """Проверяет изменение файла `remark.rules`.

        Тест для генератора из Аннушки:

        - `annushka.generators.entire.whitebox.cumulus.qos.CumulusQosMarking`
        """
        utils.run_commit_reload()
