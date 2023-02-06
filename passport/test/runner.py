# -*- coding: utf-8 -*-
from django.test.runner import DiscoverRunner


class OAuthTestSuiteRunner(DiscoverRunner):
    def setup_databases(self):
        # Перегружаем метод родителя
        pass

    def teardown_databases(self, *args):
        # Перегружаем метод родителя
        pass
