import metrika.admin.python.bishop.frontend.tests.helper as tests_helper


class TestHtml(tests_helper.BishopHtmlTestCase):
    def test_list(self):
        self._assert('/config')

    def test_name(self):
        self._assert('/program/apid/config/root.programs.apid.production/20')

    def test_raw(self):
        self._assert('/program/apid/config/root.programs.apid.production/20?raw=True')

    def test_part_audit(self):
        self._assert('/program/apid/config/root.programs.apid.production/20?part=audit')

    def test_part_common(self):
        self._assert('/program/apid/config/root.programs.apid.production/20?part=common')

    def test_part_versions(self):
        self._assert('/program/apid/config/root.programs.apid.production/20?part=versions')


class TestAjax(tests_helper.BishopAjaxTestCase):
    def test_parts_list_table(self):
        self._assert('/parts/list/config_table')

    def test_get(self):
        self._assert('/ajax/config/20')

    def test_text(self):
        self._assert('/ajax/config/20/text')

    def test_part_audit(self):
        self._assert('/ajax/config/20/part/audit')

    def test_part_common(self):
        self._assert('/ajax/config/20/part/common')

    def test_part_versions(self):
        self._assert('/ajax/config/20/part/versions')
