# -*- coding: utf-8 -*-
import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.conf import settings
from passport.backend.core.suggest.first_names import FirstNames
from passport.backend.core.suggest.tests.test_base import BaseLoader
from passport.backend.core.suggest.tests.test_data import (
    FEMALE_NAMES_MOCK_FILE,
    LOADED_NAMES,
    MALE_NAMES_MOCK_FILE,
)
from passport.backend.core.test.test_utils import iterdiff


eq_ = iterdiff(eq_)


class TestFirstNamesLoader(BaseLoader):
    def setUp(self):
        super(TestFirstNamesLoader, self).setUp()
        for lang in settings.SUGGEST_SUPPORTED_LANGUAGES:
            f_data = FEMALE_NAMES_MOCK_FILE[lang]
            self.mocks.append(self.add_mock_file(f_data))

            m_data = MALE_NAMES_MOCK_FILE[lang]
            self.mocks.append(self.add_mock_file(m_data))

        self.setup_open_file_side_effect()

    def tearDown(self):
        super(TestFirstNamesLoader, self).tearDown()

    @property
    def empty_names(self):
        return {
            'm': {'ru': {}, 'en': {}, 'tr': {}},
            'f': {'ru': {}, 'en': {}, 'tr': {}},
            'u': {},
        }

    def test_names_loaded_correctly(self):
        with mock.patch('passport.backend.core.suggest.first_names.file.path_exists', return_value=True):
            names_loader = FirstNames()

            ok_(not names_loader.names['u'])
            ok_(not names_loader.names['m']['tr'])
            eq_(names_loader.names['m']['en'], LOADED_NAMES['m']['en'])
            eq_(names_loader.names['m']['ru'], LOADED_NAMES['m']['ru'])

            ok_(not names_loader.names['f']['tr'])
            eq_(names_loader.names['f']['en'], LOADED_NAMES['f']['en'])
            eq_(names_loader.names['f']['ru'], LOADED_NAMES['f']['ru'])

    def test_no_file(self):
        with mock.patch('passport.backend.core.suggest.first_names.file.path_exists', return_value=False):
            names_loader = FirstNames()
            eq_(names_loader.names, self.empty_names)
