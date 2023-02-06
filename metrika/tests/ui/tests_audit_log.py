import metrika.admin.python.bishop.frontend.tests.helper as tests_helper


class TestHtml(tests_helper.BishopHtmlTestCase):
    def test_list(self):
        self._assert('/audit_log')

    def test_name(self):
        self._assert('/audit_log/507')


class TestAjax(tests_helper.BishopAjaxTestCase):
    def test_parts_list_table(self):
        self._assert('/parts/list/audit_log_table')

    def test_get(self):
        self._assert('/ajax/audit_log/507')

    def test_part_common(self):
        self._assert('/ajax/audit_log/507/part/common')
