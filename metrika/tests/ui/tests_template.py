import metrika.admin.python.bishop.frontend.tests.helper as tests_helper


class TestHtml(tests_helper.BishopHtmlTestCase):
    def test_list(self):
        self._assert('/template')

    def test_id(self):
        self._assert('/template/57')

    def test_name(self):
        self._assert('/template/apid.xml')

    def test_part_common(self):
        self._assert('/template/57?part=common')

    def test_part_variables(self):
        self._assert('/template/57?part=variables')

    def test_part_audit(self):
        self._assert('/template/57?part=audit')


class TestAjax(tests_helper.BishopAjaxTestCase):
    def test_parts_list_table(self):
        self._assert('/parts/list/template_table')

    def test_get(self):
        self._assert('/ajax/template/57')

    def test_forms_common(self):
        self._assert('/ajax/template/57/forms/common')

    def test_part_audit(self):
        self._assert('/ajax/template/57/part/audit')

    def test_part_common(self):
        self._assert('/ajax/template/57/part/common')

    def test_part_variables(self):
        self._assert('/ajax/template/57/part/variables')

    def test_add(self):
        self._assert('/ajax/template/add')
