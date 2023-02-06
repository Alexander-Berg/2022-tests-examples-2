import metrika.admin.python.bishop.frontend.tests.helper as tests_helper


class TestHtml(tests_helper.BishopHtmlTestCase):
    def test_list(self):
        self._assert('/program')

    def test_id(self):
        self._assert('/program/12')

    def test_name(self):
        self._assert('/program/apid')

    def test_forms_attach_environment(self):
        self._assert('/program/12/forms/attach_environment')

    def test_form_change_environment(self):
        self._assert('/program/12/forms/change_attachment?environment_id=120')

    def test_part_common(self):
        self._assert('/program/12?part=common')

    def test_part_configs(self):
        self._assert('/program/12?part=configs')

    def test_part_audit(self):
        self._assert('/program/12?part=audit')


class TestAjax(tests_helper.BishopAjaxTestCase):
    def test_parts_list_table(self):
        self._assert('/parts/list/program_table')

    def test_get(self):
        self._assert('/ajax/program/12')

    def test_forms_common(self):
        self._assert('/ajax/program/12/forms/common')

    def test_part_audit(self):
        self._assert('/ajax/program/12/part/audit')

    def test_part_common(self):
        self._assert('/ajax/program/12/part/common')

    def test_part_configs(self):
        self._assert('/ajax/program/12/part/configs')

    def test_rebuild_configs(self):
        self._assert('/ajax/program/12/rebuild_configs', http_type='post')

    def test_add(self):
        self._assert('/ajax/program/add')
