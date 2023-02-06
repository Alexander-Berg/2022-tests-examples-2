import metrika.admin.python.bishop.frontend.tests.helper as tests_helper


class TestHtml(tests_helper.BishopHtmlTestCase):
    def test_list(self):
        self._assert('/environment')

    def test_id(self):
        self._assert('/environment/120')

    def test_name(self):
        self._assert('/environment/root.programs.apid.production')

    def test_part_common(self):
        self._assert('/environment/120?part=common')

    def test_part_audit(self):
        self._assert('/environment/120?part=audit')

    def test_forms_add_linked_variable(self):
        self._assert('/environment/120/forms/add_linked_variable')

    def test_forms_add_variable(self):
        self._assert('/environment/120/forms/add_variable')


class TestAjax(tests_helper.BishopAjaxTestCase):
    def test_parts_list_table(self):
        self._assert('/parts/list/environment_table')

    def test_get(self):
        self._assert('/ajax/environment/120')

    def test_part_audit(self):
        self._assert('/ajax/environment/120/part/audit')

    def test_part_common(self):
        self._assert('/ajax/environment/120/part/common')

    def test_add(self):
        self._assert('/ajax/environment/add')
