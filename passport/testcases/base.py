# -*- coding: utf-8 -*-
import inspect
import os

from django.test import TestCase
from passport.backend.utils.warnings import enable_strict_bytes_mode


class BaseTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super(BaseTestCase, cls).setUpClass()
        enable_strict_bytes_mode()

    def _fixture_setup(self):
        pass

    def _fixture_teardown(self):
        pass

    def shortDescription(self):
        module_path = os.path.relpath(inspect.getsourcefile(type(self)))  # pragma: no cover
        _, class_name, method_name = self.id().rsplit('.', 2)             # pragma: no cover
        return '%s:%s.%s' % (module_path, class_name, method_name)        # pragma: no cover
