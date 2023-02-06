# -*- coding: utf-8 -*-

from sandbox.projects.sandbox_ci.utils.testpalm import sanitize_project_name


class TestsSanitizeProjectName(object):
    def test_allows_pr_numbers(self):
        assert sanitize_project_name('0123456789') == '0123456789'

    def test_allows_names(self):
        assert sanitize_project_name('serp-15') == 'serp-15'

    def test_release(self):
        assert sanitize_project_name('v254.0.1') == 'v254_0_1'

    def test_special_symbols(self):
        assert sanitize_project_name(u' !@#$%^&*()+¡™£¢∞§¶•ªº') == u'______________________'

    def test_whiskers(self):
        assert sanitize_project_name('.!@#0.o)(*{') == '____0_o____'
