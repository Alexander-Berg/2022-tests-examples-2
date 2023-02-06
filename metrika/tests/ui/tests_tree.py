import metrika.admin.python.bishop.frontend.tests.helper as tests_helper


class TestHtml(tests_helper.BishopHtmlTestCase):
    def test_get(self):
        self._assert('/tree')


class TestAjax(tests_helper.BishopAjaxTestCase):
    def test_environment_tree_info(self):
        self._assert('/ajax/environment/120/tree_info')
