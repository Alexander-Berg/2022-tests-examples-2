import metrika.admin.python.bishop.frontend.tests.helper as tests_helper


class TestHtml(tests_helper.BishopHtmlTestCase):
    def test_list(self):
        self._assert('/activation_request')

    def test_id(self):
        self._assert('/activation_request/33')

    def test_name(self):
        self._assert('/activation_request/AR-33')


class TestAjax(tests_helper.BishopAjaxTestCase):
    def test_parts_list_table(self):
        self._assert('/parts/list/activation_request_table')

    def test_get(self):
        self._assert('/ajax/activation_request/33')

    def test_forms_common(self):
        self._assert('/ajax/activation_request/33/part/common')
