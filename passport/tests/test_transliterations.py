# -*- coding: utf-8 -*-
import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.conf import settings
from passport.backend.core.suggest.tests.test_base import BaseLoader
from passport.backend.core.suggest.tests.test_data import (
    LOADED_RULES,
    TRANSLITERATIONS_MOCK_FILE,
)
from passport.backend.core.suggest.transliterations import Transliterations
from passport.backend.core.test.test_utils import (
    iterdiff,
    settings_context,
)


eq_ = iterdiff(eq_)


class TestTransliterationsLoader(BaseLoader):

    def setUp(self):
        super(TestTransliterationsLoader, self).setUp()
        for lang in settings.SUGGEST_SUPPORTED_LANGUAGES:
            t_data = TRANSLITERATIONS_MOCK_FILE[lang]
            self.mocks.append(self.add_mock_file(t_data))

        self.setup_open_file_side_effect()
        self.path_exists_mock = mock.Mock()
        self.path_exists_patch = mock.patch(
            'passport.backend.core.suggest.transliterations.file.path_exists',
            self.path_exists_mock,
        )
        self.path_exists_patch.start()

    def setup_path_exists(self, path_exists=True):
        self.path_exists_mock.return_value = path_exists

    def tearDown(self):
        super(TestTransliterationsLoader, self).tearDown()
        self.path_exists_patch.stop()
        del self.path_exists_patch
        del self.path_exists_mock

    def test_rules_loaded_correctly(self):
        self.setup_path_exists()
        tr_loader = Transliterations()

        ok_(not tr_loader.rules['en'])
        eq_(tr_loader.rules['tr'], LOADED_RULES['tr'])
        eq_(tr_loader.rules['ru'], LOADED_RULES['ru'])

    def test_no_file(self):
        self.setup_path_exists(False)
        tr_loader = Transliterations()
        eq_(tr_loader.rules, {'ru': {}, 'en': {}, 'tr': {}})

    def test_collect_rules__ru(self):
        self.setup_path_exists()
        tr_loader = Transliterations()
        lang = 'ru'

        first_name = u'пушин'
        expected = [
            {'replacements': [{'factor': 1.0, 'replacement': u'p'}]},
            {'replacements': [{'factor': 1.0, 'replacement': u'u'}]},
            {'replacements': [
                {'factor': 1.0, 'replacement': u'sh'},
                {'factor': 0.98, 'replacement': u'sch'},
            ]},
            {'replacements': [
                {'factor': 1.0, 'replacement': u'i'},
            ]},
            {'replacements': [{'factor': 1.0, 'replacement': u'n'}]},
        ]
        eq_(tr_loader.collect_rules(first_name, lang), expected)

        first_name = u'вгдждр'
        expected = [
            {'replacements': [{'factor': 1.0, 'replacement': u'v'}]},
            {'replacements': [{'factor': 1.0, 'replacement': u'g'}]},
            {'replacements': [
                {'factor': 1.0, 'replacement': u'j'},
                {'factor': 0.98, 'replacement': u'dj'},
                {'factor': 0.96, 'replacement': u'dzh'},
            ]},
            {'replacements': [
                {'factor': 1.0, 'replacement': u'der'},
                {'factor': 0.98, 'replacement': u'dr'},
            ]},
        ]
        eq_(tr_loader.collect_rules(first_name, lang), expected)

        first_name = u'евёвекя'
        expected = [
            {'replacements': [
                {'factor': 1.0, 'replacement': u'ev'},
                {'factor': 0.98, 'replacement': u'eu'},
                {'factor': 0.96, 'replacement': u'ew'},
            ]},
            {'replacements': [
                {'factor': 1.0, 'replacement': u'yo'},
                {'factor': 0.98, 'replacement': u'io'},
                {'factor': 0.96, 'replacement': u'eo'},
            ]},
            {'replacements': [
                {'factor': 1.0, 'replacement': u'v'},
                {'factor': 0.98, 'replacement': u'w'},
            ]},
            {'replacements': [
                {'factor': 1.0, 'replacement': u'e'},
            ]},
            {'replacements': [
                {'factor': 1.0, 'replacement': u'k'},
                {'factor': 0.98, 'replacement': u'ck'},
            ]},
            {'replacements': [
                {'factor': 1.0, 'replacement': u'ya'},
                {'factor': 0.98, 'replacement': u'ia'},
            ]},
        ]
        eq_(tr_loader.collect_rules(first_name, lang), expected)

        first_name = u'юкг'
        expected = [
            {'replacements': [{'factor': 1.0, 'replacement': u'yu'}, {'factor': 0.98, 'replacement': u'iu'}]},
            {'replacements': [{'factor': 1.0, 'replacement': u'k'}, {'factor': 0.98, 'replacement': u'c'}]},
            {'replacements': [{'factor': 1.0, 'replacement': u'g'}]},
        ]
        eq_(tr_loader.collect_rules(first_name, lang), expected)

        first_name = u'лилия'

        expected = [
            {'replacements': [{'factor': 1.0, 'replacement': u'l'}]},
            {'replacements': [
                {'factor': 1.0, 'replacement': u'i'},
            ]},
            {'replacements': [{'factor': 1.0, 'replacement': u'l'}]},
            {'replacements': [
                {'factor': 1.0, 'replacement': u'ia'},
                {'factor': 0.98, 'replacement': u'ya'},
                {'factor': 0.96, 'replacement': u'iya'},
                {'factor': 0.94, 'replacement': u'ija'},
            ]},
        ]
        eq_(tr_loader.collect_rules(first_name, lang), expected)

        first_name = u'л0лита'
        expected = [
            {'replacements': [{'factor': 1.0, 'replacement': u'l'}]},
            {'replacements': [{'factor': 1.0, 'replacement': u'0'}]},
            {'replacements': [{'factor': 1.0, 'replacement': u'l'}]},
            {'replacements': [{'factor': 1.0, 'replacement': u'i'}]},
            {'replacements': [{'factor': 1.0, 'replacement': u't'}]},
            {'replacements': [{'factor': 1.0, 'replacement': u'a'}]},
        ]
        eq_(tr_loader.collect_rules(first_name, lang), expected)

    def test_collect_rules__tr(self):
        self.setup_path_exists()
        tr_loader = Transliterations()
        lang = 'tr'

        first_name = u'abcsöşığüç'
        expected = [
            {'replacements': [{'factor': 1.0, 'replacement': u'a'}]},
            {'replacements': [{'factor': 1.0, 'replacement': u'b'}]},
            {'replacements': [{'factor': 1.0, 'replacement': u'c'}]},
            {'replacements': [
                {'factor': 1.0, 'replacement': u's'},
                {'factor': 0.98, 'replacement': u'sh'},
            ]},
            {'replacements': [{'factor': 1.0, 'replacement': u'o'}]},
            {'replacements': [
                {'factor': 1.0, 'replacement': u'sh'},
                {'factor': 0.98, 'replacement': u's'},
            ]},
            {'replacements': [{'factor': 1.0, 'replacement': u'i'}]},
            {'replacements': [{'factor': 1.0, 'replacement': u'g'}]},
            {'replacements': [{'factor': 1.0, 'replacement': u'u'}]},
            {'replacements': [{'factor': 1.0, 'replacement': u'ch'}]},
        ]
        eq_(tr_loader.collect_rules(first_name, lang), expected)

        first_name = u'abcd'
        expected = [
            {'replacements': [{'factor': 1.0, 'replacement': u'a'}]},
            {'replacements': [{'factor': 1.0, 'replacement': u'b'}]},
            {'replacements': [{'factor': 1.0, 'replacement': u'c'}]},
            {'replacements': [{'factor': 1.0, 'replacement': u'd'}]},
        ]
        eq_(tr_loader.collect_rules(first_name, lang), expected)

    def test_collect_rules__en(self):
        self.setup_path_exists()
        tr_loader = Transliterations()
        lang = 'en'

        first_name = u'abcd'
        eq_(tr_loader.collect_rules(first_name, lang), [])

    def test_apply_rules(self):
        self.setup_path_exists()
        tr_loader = Transliterations()
        # пушин
        sources_rules = [
            {'replacements': [
                {'factor': 1.0, 'replacement': u'p'},
                {'factor': 0.98, 'replacement': u'q'},
                {'factor': 0.96, 'replacement': u'd'},
            ]},
            {'replacements': [{'factor': 1.0, 'replacement': u'u'}]},
            {'replacements': [{'factor': 1.0, 'replacement': u'sh'}, {'factor': 0.98, 'replacement': u'sch'}]},
            {'replacements': [{'factor': 1.0, 'replacement': u'i'}]},
            {'replacements': [{'factor': 1.0, 'replacement': u'n'}]},
        ]
        expected = [
            {'transliteration': u'pushin', 'factor': 1.0},
            {'transliteration': u'puschin', 'factor': 0.98},
            {'transliteration': u'qushin', 'factor': 0.98},
            {'transliteration': u'quschin', 'factor': 0.96},
            {'transliteration': u'dushin', 'factor': 0.96},
            {'transliteration': u'duschin', 'factor': 0.94},
        ]
        eq_(tr_loader.apply_rules(sources_rules), expected)

        # евё
        sources_rules = [
            {'replacements': [{'factor': 1.0, 'replacement': u'ev'}, {'factor': 0.98, 'replacement': u'eu'},
                              {'factor': 0.96, 'replacement': u'ew'}]},
            {'replacements': [{'factor': 1.0, 'replacement': u'yo'}, {'factor': 0.98, 'replacement': u'io'},
                              {'factor': 0.96, 'replacement': u'eo'}]},
        ]

        expected = [
            {'transliteration': u'evyo', 'factor': 1.0},
            {'transliteration': u'evio', 'factor': 0.98},
            {'transliteration': u'eveo', 'factor': 0.96},
            {'transliteration': u'euyo', 'factor': 0.98},
            {'transliteration': u'euio', 'factor': 0.96},
            {'transliteration': u'eueo', 'factor': 0.94},
            {'transliteration': u'ewyo', 'factor': 0.96},
            {'transliteration': u'ewio', 'factor': 0.94},
            {'transliteration': u'eweo', 'factor': 0.92}
        ]
        eq_(tr_loader.apply_rules(sources_rules), expected)

        # джидж
        sources_rules = [
            {'replacements': [{'factor': 1.0, 'replacement': u'j'}, {'factor': 0.98, 'replacement': u'dj'},
                              {'factor': 0.96, 'replacement': u'dzh'}]},
            {'replacements': [{'factor': 1.0, 'replacement': u'i'}]},
            {'replacements': [{'factor': 1.0, 'replacement': u'j'}, {'factor': 0.98, 'replacement': u'dj'},
                              {'factor': 0.96, 'replacement': u'dzh'}]},
        ]
        expected = [
            {'transliteration': u'jij', 'factor': 1.0},
            {'transliteration': u'jidj', 'factor': 0.98},
            {'transliteration': u'jidzh', 'factor': 0.96},
            {'transliteration': u'djij', 'factor': 0.98},
            {'transliteration': u'djidj', 'factor': 0.96},
            {'transliteration': u'djidzh', 'factor': 0.94},
            {'transliteration': u'dzhij', 'factor': 0.96},
            {'transliteration': u'dzhidj', 'factor': 0.94},
            {'transliteration': u'dzhidzh', 'factor': 0.92}
        ]

        eq_(tr_loader.apply_rules(sources_rules), expected)

        # джулия - достигаем лимита на транслитерации в 10 комбинаций
        sources_rules = [
            {'replacements': [
                {'factor': 1.0, 'replacement': u'j'},
                {'factor': 0.98, 'replacement': u'dj'},
                {'factor': 0.96, 'replacement': u'dzh'},
            ]},
            {'replacements': [{'factor': 1.0, 'replacement': u'u'}]},
            {'replacements': [{'factor': 1.0, 'replacement': u'l'}]},
            {'replacements': [
                {'factor': 1.0, 'replacement': u'ia'},
                {'factor': 0.98, 'replacement': u'ya'},
                {'factor': 0.96, 'replacement': u'iya'},
                {'factor': 0.96, 'replacement': u'ija'},
            ]},
        ]
        expected = [
            {'transliteration': u'julia', 'factor': 1.0},
            {'transliteration': u'julya', 'factor': 0.98},
            {'transliteration': u'juliya', 'factor': 0.96},
            {'transliteration': u'julija', 'factor': 0.96},
            {'transliteration': u'djulia', 'factor': 0.98},
            {'transliteration': u'djulya', 'factor': 0.96},
            {'transliteration': u'djuliya', 'factor': 0.94},
            {'transliteration': u'djulija', 'factor': 0.94},
            {'transliteration': u'dzhulia', 'factor': 0.96},
            {'transliteration': u'dzhulya', 'factor': 0.94},
        ]

        with settings_context(MAX_TRANSLITERATIONS=10):
            eq_(tr_loader.apply_rules(sources_rules), expected)

        eq_(tr_loader.apply_rules([], ignore_as_is=True), [])

        # замена на цифры - достигаем лимита на транслитерации elite
        sources_rules = [
            {'replacements': [
                {'factor': 1.0, 'replacement': u'e'},
                {'factor': 0.94, 'replacement': u'3'},
            ]},
            {'replacements': [
                {'factor': 1.0, 'replacement': u'l'},
                {'factor': 0.94, 'replacement': u'1'},
            ]},
            {'replacements': [
                {'factor': 1.0, 'replacement': u'i'},
                {'factor': 0.92, 'replacement': u'1'},
            ]},
            {'replacements': [
                {'factor': 1.0, 'replacement': u't'},
                {'factor': 0.92, 'replacement': u'7'},
            ]},
            {'replacements': [
                {'factor': 1.0, 'replacement': u'e'},
                {'factor': 0.94, 'replacement': u'3'},
            ]},
        ]
        expected = [
            {'transliteration': u'elit3', 'factor': 0.94},
            {'transliteration': u'eli7e', 'factor': 0.92},
            {'transliteration': u'eli73', 'factor': 0.86},
            {'transliteration': u'el1te', 'factor': 0.92},
            {'transliteration': u'el1t3', 'factor': 0.86},
        ]

        eq_(tr_loader.apply_rules(sources_rules, ignore_as_is=True, threshold=4), expected)

        # Слово со всякими знаками - ханъань
        sources_rules = [
            {'replacements': [{'factor': 1.0, 'replacement': u'h'}]},
            {'replacements': [{'factor': 1.0, 'replacement': u'a'}]},
            {'replacements': [{'factor': 1.0, 'replacement': u'n'}]},
            {'replacements': []},
            {'replacements': [{'factor': 1.0, 'replacement': u'a'}]},
            {'replacements': [{'factor': 1.0, 'replacement': u'n'}]},
            {'replacements': []},
        ]
        expected = [
            {'transliteration': u'hanan', 'factor': 1.0},
        ]
        eq_(tr_loader.apply_rules(sources_rules), expected)

        # Пустая транслитерация - ъь
        sources_rules = [
            {'replacements': []},
            {'replacements': []},
        ]
        eq_(tr_loader.apply_rules(sources_rules), [{'transliteration': u'', 'factor': 1.0}])
