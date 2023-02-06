import metrika.admin.python.bishop.frontend.tests.helper as tests_helper


class TestHtml(tests_helper.BishopHtmlTestCase):
    def test_system(self):
        self._assert('/system')

    def test_external_data_hosts(self):
        self._assert('/system/external_data/hosts/4')

    def test_external_data_networks(self):
        self._assert('/system/external_data/networks/4')

    def test_part_control_center(self):
        self._assert('/system?part=control_center')

    def test_part_broken_configs(self):
        self._assert('/system?part=broken_configs')


class TestAjax(tests_helper.BishopAjaxTestCase):
    def test_parts_list_table(self):
        self._assert('/parts/list/program_table')

    def test_get(self):
        self._assert('/ajax/program/12')

    def test_forms_common(self):
        self._assert('/ajax/program/12/forms/common')

    def test_part_comtrol_center(self):
        self._assert('/parts/system/control_center')

    def test_part_broken_configs(self):
        self._assert('/parts/system/broken_configs')
