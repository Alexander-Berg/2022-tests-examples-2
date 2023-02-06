# -*- coding: utf-8 -*-
import mock
from passport.backend.core.test.test_utils import single_entrant_patch


@single_entrant_patch
class CodeGeneratorFaker(object):
    DEFAULT_CONFIRMATION_CODE = u'1234'

    def __init__(self, code=None):
        self._mock = mock.Mock(name=u'generate_random_code')
        self._patch = mock.patch(u'passport.backend.utils.common._generate_random_code', self._mock)
        self.set_response_value(code if code is not None else self.DEFAULT_CONFIRMATION_CODE)

    def start(self):
        self._patch.start()

    def stop(self):
        self._patch.stop()

    def set_response_value(self, response_value):
        self._mock.side_effect = None
        self._mock.return_value = response_value

    def set_response_side_effect(self, side_effect):
        self._mock.return_value = None
        self._mock.side_effect = side_effect

    set_return_value = set_response_value

    @property
    def call_count(self):
        return self._mock.call_count
