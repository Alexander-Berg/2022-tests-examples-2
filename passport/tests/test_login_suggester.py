# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.suggest.faker import (
    FakeFirstNames,
    FakeTransliterations,
)
from passport.backend.core.suggest.login_suggester import (
    LoginSuggester,
    TransliterationSource,
)
from passport.backend.core.suggest.tests.test_data import (
    LANG_TO_MIXES,
    LETTER_TO_NUMBER_REPLACEMENTS,
    LETTER_TO_NUMBER_REPLACEMENTS_KEYS,
    LOADED_NAMES,
    LOADED_RULES,
    PREFIX_WEIGHT,
    TEST_LOGIN_PREFIXES,
)
from passport.backend.core.test.test_utils import (
    settings_context,
    with_settings,
)
from six import iteritems


@with_settings(
    LANG_TO_MIXES=LANG_TO_MIXES,
    LETTER_TO_NUMBER_REPLACEMENTS={},
    LETTER_TO_NUMBER_REPLACEMENTS_KEYS=set(),
    LOGIN_PREFIXES=TEST_LOGIN_PREFIXES,
    PREFIX_WEIGHT=PREFIX_WEIGHT,
)
class TestLoginSuggester(unittest.TestCase):

    def setUp(self):
        self.names = FakeFirstNames()
        self.rules = FakeTransliterations()

        self.names.start()
        self.rules.start()

        self.names.setup_names(LOADED_NAMES)
        self.rules.setup_rules(LOADED_RULES)

        self.suggester = LoginSuggester()
        self.maxDiff = None

    def tearDown(self):
        self.rules.stop()
        self.names.stop()
        del self.rules
        del self.names

    def test_set_language(self):
        for lang in ['tr', 'en', 'ru']:
            eq_(self.suggester.set_language(lang), lang)

        for lang in ['wqe', 'uk', '']:
            eq_(self.suggester.set_language(lang), 'ru')

    def test_clean__name(self):
        names = [
            u'Маша',
            u'Е к а т е р и н а',
            u'  An--na\n',
            u'ALwin',
            u'---chris!@#',
            u'AMBE   R   ',
            u'Egorova123',
            u'Петрова123',
            u'.ada-',
            u'a' * 21,
            u'123456',
            u'Gökhan',
            u'....-----....',
            u'5-. 678ftdy..z97789.-',
        ]
        expected = [
            u'маша',
            u'екатерина',
            u'an-na',
            u'alwin',
            u'chris',
            u'amber',
            u'egorova123',
            u'петрова123',
            u'ada',
            u'a' * 20,
            u'123456',
            u'gökhan',
            u'',
            u'5-678ftdy-z97789',
        ]
        for i, name in enumerate(names):
            res = self.suggester.clean(name)
            eq_(res, expected[i], msg='%d: %s != %s' % (i + 1, res, expected[i]))

    def test_clean__login(self):
        logins = [
            u'Маша',
            u'Е-к-а-т-е-р-и-н-а',
            u'  An--na\n',
            u'ALwin',
            u'---chris!@#',
            u'AMBE   R   ',
            u'fun.adaö',
            u'a' * 100,
            u'5-. 678ftdy..z97789.-',
        ]
        expected = [
            u'',
            u'',
            u'an-na',
            u'alwin',
            u'chris',
            u'amber',
            u'fun.ada',
            u'a' * 30,
            u'ftdy-z97789',
        ]
        for i, login in enumerate(logins):
            res = self.suggester.clean_login(login)
            eq_(res, expected[i], msg='%d: %s != %s' % (i + 1, res, expected[i]))

    def test_identify_gender__by_surname(self):
        self.suggester.last_name = u'варфаламеев'
        self.suggester.first_name = u'василиса'
        self.suggester.lang = 'ru'
        eq_(self.suggester.identify_gender(), 'm', msg=self.suggester.last_name)

        self.suggester.last_name = u'уткина'
        self.suggester.first_name = u'валера'
        self.suggester.lang = 'ru'
        eq_(self.suggester.identify_gender(), 'f', msg=self.suggester.last_name)

        self.suggester.last_name = u'уткин'
        self.suggester.lang = 'ru'
        eq_(self.suggester.identify_gender(), 'm', msg=self.suggester.last_name)

        self.suggester.last_name = u'красивый'
        self.suggester.first_name = u'рассвет'
        self.suggester.lang = 'ru'
        eq_(self.suggester.identify_gender(), 'm', msg=self.suggester.last_name)

    def test_identify_gender__by_name(self):
        # Нейтральная фамилия
        self.suggester.last_name = u'сокол'
        self.suggester.first_name = u'вася'
        self.suggester.lang = 'ru'
        eq_(self.suggester.identify_gender(), 'm', msg=self.suggester.first_name)

        self.suggester.last_name = u'gluck'
        self.suggester.first_name = u'василиса'
        self.suggester.lang = 'ru'
        eq_(self.suggester.identify_gender(), 'f', msg=self.suggester.first_name)

        self.suggester.first_name = u'allen'
        self.suggester.lang = 'en'
        eq_(self.suggester.identify_gender(), 'm', msg=self.suggester.first_name)

        # Нет фамилии, но имя есть в обоих наборах имен
        self.suggester.last_name = u''
        self.suggester.first_name = u'саша'
        self.suggester.lang = 'ru'
        eq_(self.suggester.identify_gender(), 'm', msg=self.suggester.first_name)

        # Имя с е и ё - находим
        self.suggester.first_name = self.suggester.clean_name(u'артём')
        self.suggester.lang = 'ru'
        eq_(self.suggester.identify_gender(), 'm', msg=self.suggester.first_name)

        self.suggester.first_name = u'артем'
        self.suggester.lang = 'ru'
        eq_(self.suggester.identify_gender(), 'm', msg=self.suggester.first_name)

        self.suggester.first_name = self.suggester.clean_name(u'фёкла')
        eq_(self.suggester.identify_gender(), 'f', msg=self.suggester.first_name)

    def test_identify_gender__undefined(self):
        self.suggester.last_name = u'доктор'
        self.suggester.first_name = u'манхэттен'
        self.suggester.lang = 'ru'
        eq_(self.suggester.identify_gender(), 'u', msg=self.suggester.first_name)

        self.suggester.first_name = u'мария'
        self.suggester.lang = 'kz'
        eq_(self.suggester.identify_gender(), 'u', msg=self.suggester.first_name)

        self.suggester.last_name = u'уткин'
        self.suggester.lang = 'tr'
        eq_(self.suggester.identify_gender(), 'u', msg=self.suggester.last_name)

        self.suggester.first_name = u'arnold'
        self.suggester.lang = 'ru'
        eq_(self.suggester.identify_gender(), 'm', msg=self.suggester.first_name)

        self.suggester.last_name = u'ass-asd-sad-sad.asd'
        self.suggester.lang = 'omg'
        eq_(self.suggester.identify_gender(), 'u', msg=self.suggester.last_name)

    def test_generate_name_synonyms__exist(self):
        self.suggester.lang = 'ru'
        self.suggester.gender = 'm'

        names = [u'василий', u'вася']

        for name in names:
            self.suggester.first_name = name
            # проверим без правил транслитерации
            name_synonyms = self.suggester.generate_name_synonyms()
            actual = [TransliterationSource(string=val.string, weight=val.weight, rules=[]) for val in name_synonyms]
            expected = [TransliterationSource(string=synonym, weight=98, rules=[]) for synonym in names if synonym != name]
            eq_(actual, expected)

        self.suggester.lang = 'ru'
        self.suggester.gender = 'f'

        names = [u'вероника', u'ника']

        for name in names:
            self.suggester.first_name = name
            # проверим без правил транслитерации
            name_synonyms = self.suggester.generate_name_synonyms()
            actual = [TransliterationSource(string=val.string, weight=val.weight, rules=[]) for val in name_synonyms]
            expected = [TransliterationSource(string=synonym, weight=98, rules=[]) for synonym in names if synonym != name]
            eq_(actual, expected)

    def test_generate_name_synonyms__not_exist(self):
        self.suggester.lang = 'ru'
        self.suggester.gender = 'u'

        self.suggester.first_name = u'пушин'
        ok_(not self.suggester.generate_name_synonyms())

        # так уже не выйдет
        self.suggester.lang = 'ru'
        self.suggester.gender = 'm'

        names = [u'вероника', u'ника']

        for name in names:
            self.suggester.first_name = name

            ok_(not self.suggester.generate_name_synonyms())

    def test_generate_name_auto_chunks__female(self):
        self.suggester.lang = 'ru'
        self.suggester.gender = 'f'

        self.suggester.first_name = u'пушин'
        expected = [
            TransliterationSource(
                string=u'п',
                weight=98,
                rules=[
                    {'replacements': [{'factor': 1.0, 'replacement': u'p'}]},
                ],
            ),
            TransliterationSource(
                string=u'пуш',
                weight=96,
                rules=[
                    {'replacements': [{'factor': 1.0, 'replacement': u'p'}]},
                    {'replacements': [{'factor': 1.0, 'replacement': u'u'}]},
                    {'replacements': [
                        {'factor': 1.0, 'replacement': u'sh'},
                        {'factor': 0.98, 'replacement': u'sch'},
                    ]},
                ],
            ),
            TransliterationSource(
                string=u'пуши',
                weight=94,
                rules=[
                    {'replacements': [{'factor': 1.0, 'replacement': u'p'}]},
                    {'replacements': [{'factor': 1.0, 'replacement': u'u'}]},
                    {'replacements': [
                        {'factor': 1.0, 'replacement': u'sh'},
                        {'factor': 0.98, 'replacement': u'sch'},
                    ]},
                    {'replacements': [
                        {'factor': 1.0, 'replacement': u'i'},
                    ]},
                ],
            ),
        ]
        eq_(self.suggester.generate_name_auto_chunks(), expected)

        self.suggester.lang = 'en'
        self.suggester.gender = 'f'

        self.suggester.first_name = u'aurora'
        expected = [
            TransliterationSource(string=u'a', weight=98, rules=[]),
            TransliterationSource(string=u'aur', weight=96, rules=[]),
            TransliterationSource(string=u'auro', weight=94, rules=[]),
        ]
        eq_(self.suggester.generate_name_auto_chunks(), expected)

    def test_generate_name_auto_chunks__male(self):
        self.suggester.lang = 'ru'
        self.suggester.gender = 'm'

        self.suggester.first_name = u'пушин'
        expected = [
            TransliterationSource(
                string=u'п',
                weight=98,
                rules=[
                    {'replacements': [{'factor': 1.0, 'replacement': u'p'}]},
                ],
            ),
            TransliterationSource(
                string=u'пуш',
                weight=96,
                rules=[
                    {'replacements': [{'factor': 1.0, 'replacement': u'p'}]},
                    {'replacements': [{'factor': 1.0, 'replacement': u'u'}]},
                    {'replacements': [
                        {'factor': 1.0, 'replacement': u'sh'},
                        {'factor': 0.98, 'replacement': u'sch'},
                    ]},
                ],
            ),
        ]
        eq_(self.suggester.generate_name_auto_chunks(), expected)

        self.suggester.lang = 'en'
        self.suggester.gender = 'm'

        self.suggester.first_name = u'brian'
        expected = [
            TransliterationSource(string=u'b', weight=98, rules=[]),
        ]
        eq_(self.suggester.generate_name_auto_chunks(), expected)

    def test_generate_name_auto_chunks__undefined(self):
        self.suggester.lang = 'ru'
        self.suggester.gender = 'u'

        self.suggester.first_name = u'пушин'
        expected = [
            TransliterationSource(
                string=u'п',
                weight=98,
                rules=[
                    {'replacements': [{'factor': 1.0, 'replacement': u'p'}]},
                ],
            ),
            TransliterationSource(
                string=u'пуш',
                weight=96,
                rules=[
                    {'replacements': [{'factor': 1.0, 'replacement': u'p'}]},
                    {'replacements': [{'factor': 1.0, 'replacement': u'u'}]},
                    {'replacements': [
                        {'factor': 1.0, 'replacement': u'sh'},
                        {'factor': 0.98, 'replacement': u'sch'},
                    ]},
                ],
            ),
        ]
        eq_(self.suggester.generate_name_auto_chunks(), expected)

        self.suggester.lang = 'tr'
        self.suggester.gender = 'u'

        self.suggester.first_name = u'çöş'
        expected = [
            TransliterationSource(
                string=u'ç',
                weight=98,
                rules=[
                    {'replacements': [{'factor': 1.0, 'replacement': u'ch'}]},
                ],
            ),
        ]
        eq_(self.suggester.generate_name_auto_chunks(), expected)

    def test_generate_name_manual_chunks__exist(self):
        self.suggester.lang = 'ru'
        self.suggester.gender = 'f'
        self.suggester.first_name = u'кристина'

        expected = [
            (100, u'k'),
            (98, u'c'),
            (96, u'kris'),
            (94, u'cris'),
            (92, u'krist'),
            (90, u'crist'),
        ]

        self.suggester.elements = self.suggester.generate_elements()
        eq_(self.suggester.elements['name_chunk'].nlargest(), expected)

    def test_generate_name_manual_chunks__not_exist(self):
        self.suggester.lang = 'ru'
        self.suggester.gender = 'm'
        self.suggester.first_name = u'азарий'

        self.suggester.elements = self.suggester.generate_elements()
        ok_('name_chunk' not in self.suggester.elements)

    def test_login_and_number(self):
        self.suggester.login = u'login123'
        eq_(self.suggester.get_login_and_number(), (u'login', u'123'), msg=self.suggester.login)

        self.suggester.login = u'login'
        eq_(self.suggester.get_login_and_number(), (u'login', None), msg=self.suggester.login)

        self.suggester.login = u'123login'
        eq_(self.suggester.get_login_and_number(), (u'123login', None), msg=self.suggester.login)

        self.suggester.login = u'logicomix1771'
        eq_(self.suggester.get_login_and_number(), (u'logicomix', u'1771'), msg=self.suggester.login)

    def test_generate_transliteration_sources_and_rules__last_name(self):
        self.suggester.lang = 'en'
        self.suggester.gender = 'u'

        self.suggester.last_name = u'peterson'
        expected = {
            'surname_synonym': [
                TransliterationSource(
                    string=u'peterson',
                    weight=100,
                    rules=[],
                ),
            ],
        }

        eq_(self.suggester.generate_transliteration_sources_and_rules(), expected)

        self.suggester.lang = 'ru'
        self.suggester.last_name = u'цы'

        expected = {
            'surname_synonym': [
                TransliterationSource(
                    string=u'цы',
                    weight=100,
                    rules=[
                        {'replacements': [
                            {'replacement': u'ts', 'factor': 1.0},
                            {'factor': 0.98, 'replacement': u'tz'},
                            {'factor': 0.96, 'replacement': u'cz'}
                        ]},
                        {'replacements': [
                            {'factor': 1.0, 'replacement': u'y'},
                            {'factor': 0.98, 'replacement': u'i'},
                        ]},
                    ],
                ),
            ],
        }
        eq_(self.suggester.generate_transliteration_sources_and_rules(), expected)

    def test_generate_transliteration_sources_and_rules__first_name(self):
        self.suggester.lang = 'en'
        self.suggester.gender = 'f'

        self.suggester.first_name = u'ada'
        expected = {
            'name_synonym': [
                TransliterationSource(
                    string=u'ada',
                    weight=100,
                    rules=[],
                ),
            ],
            'name_chunk': [
                TransliterationSource(
                    string=u'a',
                    weight=98,
                    rules=[],
                ),
                TransliterationSource(
                    string=u'ad',
                    weight=96,
                    rules=[],
                ),
            ],
        }

        eq_(self.suggester.generate_transliteration_sources_and_rules(), expected)

        self.suggester.lang = 'ru'
        self.suggester.gender = 'm'
        self.suggester.first_name = u'виктор'

        expected = {
            'name_synonym': [
                TransliterationSource(
                    string=u'виктор',
                    weight=100,
                    rules=[
                        {'replacements': [{'factor': 1.0, 'replacement': u'v'}]},
                        {'replacements': [{'factor': 1.0, 'replacement': u'i'}]},
                        {'replacements': [{'factor': 1.0, 'replacement': u'k'}, {'factor': 0.98, 'replacement': u'c'}]},
                        {'replacements': [{'factor': 1.0, 'replacement': u't'}]},
                        {'replacements': [{'factor': 1.0, 'replacement': u'o'}]},
                        {'replacements': [{'factor': 1.0, 'replacement': u'r'}]},
                    ],
                ),
                TransliterationSource(
                    string=u'витя',
                    weight=98,
                    rules=[
                        {'replacements': [{'factor': 1.0, 'replacement': u'v'}]},
                        {'replacements': [{'factor': 1.0, 'replacement': u'i'}]},
                        {'replacements': [{'factor': 1.0, 'replacement': u't'}]},
                        {'replacements': [
                            {'factor': 1.0, 'replacement': u'ya'},
                            {'factor': 0.98, 'replacement': u'ia'},
                        ]},
                    ],
                ),
            ],
        }
        eq_(self.suggester.generate_transliteration_sources_and_rules(), expected)

    def test_generate_elements(self):
        self.suggester.first_name = u'каштан'
        self.suggester.last_name = u'фыр-фыр'
        self.suggester.login = u'achtung1987'
        self.suggester.lang = 'ru'
        self.suggester.gender = 'm'

        self.suggester.sources = self.suggester.generate_transliteration_sources_and_rules()

        self.suggester.elements = self.suggester.generate_elements()

        expected = {
            'name_chunk': [
                (98.0, u'k'),
                (96.04, u'c'),
                (96.0, u'kash'),
                (94.08, u'kasch'),
                (94.08, u'cash'),
                (94.0, u'kasht'),
                (92.16, u'casch'),
                (92.12, u'kascht'),
                (92.12, u'casht'),
                (90.24, u'cascht'),
            ],
            'name_synonym': [
                (100.0, u'kashtan'),
                (98.0, u'kaschtan'),
                (98.0, u'cashtan'),
                (96.0, u'caschtan'),
            ],
            'surname_synonym': [
                (100.0, u'fyr-fyr'),
                (98.0, u'fir-fyr'),
                (98.0, u'fyr-fir'),
                (96.0, u'fir-fir'),
            ],
            'login_synonym': [
                (100.0, u'achtung1987'),
            ],
            'login_wo_number': [
                (100.0, u'achtung'),
            ],
            'login_number': [
                (100.0, u'achtung87'),
            ],
            'prefix': [
                (96.0, u'ya'),
            ],
        }
        eq_(self.suggester.elements.keys(), expected.keys())
        for k, v in iteritems(self.suggester.elements):
            eq_(sorted(v.nlargest()), sorted(expected[k]))

        self.suggester.first_name = u'джулия'
        self.suggester.last_name = u''
        self.suggester.login = u''
        self.suggester.gender = 'f'

        self.suggester.sources = self.suggester.generate_transliteration_sources_and_rules()
        self.suggester.elements = self.suggester.generate_elements()

        expected = {
            'name_chunk': [
                (100.0, u'd'),
                (98.0, u'j'),
                (96.0, u'jul'),
                (94.0, u'djul'),
            ],
            'name_synonym': [
                (100.0, u'julia'),
                (98.0, u'julya'),
                (96.0, u'juliya'),
                (94.0, u'julija'),
                (98.0, u'djulia'),
                (96.0, u'djulya'),
                (94.0, u'djuliya'),
                (92.0, u'djulija'),
                (96.0, u'dzhulia'),
                (94.0, u'dzhulya'),
                (92.0, u'dzhuliya'),
                (90.0, u'dzhulija'),
            ],
            'prefix': [
                (96.0, u'ya'),
            ],
        }
        eq_(self.suggester.elements.keys(), expected.keys())
        for k, v in iteritems(self.suggester.elements):
            eq_(sorted(v.nlargest()), sorted(expected[k]))

    def test_generate_elements_with_numbers(self):
        self.suggester.login = u'elite'
        with settings_context(
                LETTER_TO_NUMBER_REPLACEMENTS=LETTER_TO_NUMBER_REPLACEMENTS,
                LETTER_TO_NUMBER_REPLACEMENTS_KEYS=LETTER_TO_NUMBER_REPLACEMENTS_KEYS,
                LOGIN_PREFIXES=TEST_LOGIN_PREFIXES,
                PREFIX_WEIGHT=PREFIX_WEIGHT,
        ):
            self.suggester.sources = self.suggester.generate_transliteration_sources_and_rules()
            self.suggester.elements = self.suggester.generate_elements()

        expected = {
            'login_synonym': [
                (100.0, u'elite'),
                (90.0, u'elit3'),
                (90.0, u'el1te'),
                (81.0, u'el1t3'),
                (90.0, u'3lite'),
                (81.0, u'3lit3'),
                (81.0, u'3l1te'),
                (73.0, u'3l1t3'),
            ],
            'prefix': [
                (96.0, u'ya'),
            ],
        }
        eq_(self.suggester.elements.keys(), expected.keys())
        for k, v in iteritems(self.suggester.elements):
            eq_(sorted(v.nlargest()), sorted(expected[k]))

        self.suggester.login = u'e' * 31
        self.suggester.elements = self.suggester.generate_elements()
        expected = {
            'login_synonym': [
                (100.0, u'e' * 31),
            ],
            'prefix': [
                (96.0, u'ya'),
            ],
        }
        eq_(self.suggester.elements.keys(), expected.keys())
        for k, v in iteritems(self.suggester.elements):
            eq_(v.nlargest(), expected[k])

    def test_generate_mixes(self):
        self.suggester.first_name = u'lira'
        self.suggester.last_name = u'erso'
        self.suggester.lang = 'ru'
        self.suggester.gender = 'f'

        self.suggester.sources = self.suggester.generate_transliteration_sources_and_rules()
        self.suggester.elements = self.suggester.generate_elements()
        self.suggester.mixes = self.suggester.generate_mixes()

        expected = [
            {'values': [(100.0, u'erso')], 'limit': 2},
            {'values': [(100.0, u'ersolira')], 'limit': 4},
            {'values': [(100.0, u'liraerso')], 'limit': 4},
            {'values': [(96.0, u'lira')], 'limit': 3},
            {'values': [(92.12, u'lerso'), (90.24, u'lirerso')], 'limit': 4},
            {'values': [(94.0, u'lira.erso')], 'limit': 1},
            {'values': [(94.0, u'erso.lira')], 'limit': 1},
            {'values': [(91.14, u'ersol'), (89.28, u'ersolir')], 'limit': 4},
        ]

        eq_(len(self.suggester.mixes), len(expected))

        for i, items in enumerate(self.suggester.mixes):
            eq_(items['limit'], expected[i]['limit'])
            eq_(sorted(items['values'].nlargest()), sorted(expected[i]['values']))

    def test_generate_mixes_with_validators(self):
        mixes_conf = {
            'ru': [
                {
                    'factor': 1.0,
                    'limit': 4,
                    'params': ['name_synonym', 'surname_synonym'],
                    'separator': False,
                    'validator': False,
                },
                {
                    'factor': 0.98,
                    'limit': 1,
                    'params': ['login_synonym', 'surname_synonym'],
                    'separator': False,
                    'validator': True,
                },
            ],
        }

        self.suggester.first_name = u'ivanov'
        self.suggester.last_name = u'иванов'
        self.suggester.login = u'iwanov'
        self.suggester.lang = 'ru'
        self.suggester.gender = 'm'

        with settings_context(
                LANG_TO_MIXES=mixes_conf,
                LETTER_TO_NUMBER_REPLACEMENTS={},
                LETTER_TO_NUMBER_REPLACEMENTS_KEYS=set(),
                LOGIN_PREFIXES=TEST_LOGIN_PREFIXES,
                PREFIX_WEIGHT=PREFIX_WEIGHT,
        ):
            self.suggester.sources = self.suggester.generate_transliteration_sources_and_rules()
            self.suggester.elements = self.suggester.generate_elements()
            self.suggester.mixes = self.suggester.generate_mixes()

        expected = [
            {'limit': 4, 'values': [
                (100.0, u'ivanovivanov'),
                (98.0, u'ivanovivanoff'),
                (96.0, u'ivanovivanow'),
                (98.0, u'ivanoviwanov'),
                (96.0, u'ivanoviwanoff'),
                (94.0, u'ivanoviwanow'),
            ]},
            {'limit': 1, 'values': [
                (98.0, u'iwanovivanov'),
                (96.04, u'iwanovivanoff'),
                (94.08, u'iwanovivanow'),
                (94.08, u'iwanoviwanoff'),
                (92.12, u'iwanoviwanow'),
            ]},
        ]

        eq_(len(self.suggester.mixes), len(expected))

        for i, items in enumerate(self.suggester.mixes):
            eq_(items['limit'], expected[i]['limit'])
            eq_(sorted(items['values'].nlargest()), sorted(expected[i]['values']))

    def test_generate_mixes_with_prefixes(self):
        mixes_conf = {
            'en': [
                {
                    'factor': 1.0,
                    'limit': 2,
                    'params': ['prefix', 'login_synonym'],
                    'separator': True,
                    'validator': False,
                },
                {
                    'factor': 0.98,
                    'limit': 1,
                    'params': ['prefix', 'surname_synonym'],
                    'separator': True,
                    'validator': False,
                },
            ],
        }

        self.suggester.last_name = u'bright'
        self.suggester.login = u'mr'
        self.suggester.lang = 'en'
        self.suggester.gender = 'u'

        with settings_context(
                LANG_TO_MIXES=mixes_conf,
                LETTER_TO_NUMBER_REPLACEMENTS=LETTER_TO_NUMBER_REPLACEMENTS,
                LETTER_TO_NUMBER_REPLACEMENTS_KEYS=LETTER_TO_NUMBER_REPLACEMENTS_KEYS,
                LOGIN_PREFIXES=TEST_LOGIN_PREFIXES,
                PREFIX_WEIGHT=PREFIX_WEIGHT,
        ):
            self.suggester.sources = self.suggester.generate_transliteration_sources_and_rules()
            self.suggester.elements = self.suggester.generate_elements()
            self.suggester.mixes = self.suggester.generate_mixes()

        expected = [
            {'limit': 2, 'values': [
                (96.0, u'ya.mr')
            ]},
            {'limit': 1, 'values': [
                (94.08, u'ya.bright'),
                (84.67, u'ya.br1ght'),
            ]},
        ]

        eq_(len(self.suggester.mixes), len(expected))

        for i, items in enumerate(self.suggester.mixes):
            eq_(items['limit'], expected[i]['limit'])
            eq_(sorted(items['values'].nlargest()), sorted(expected[i]['values']))

    def test_next_pack(self):
        self.suggester.first_name = u'lira'
        self.suggester.last_name = u'erso'
        self.suggester.lang = 'ru'
        self.suggester.gender = 'f'

        self.suggester.sources = self.suggester.generate_transliteration_sources_and_rules()
        self.suggester.elements = self.suggester.generate_elements()
        self.suggester.mixes = self.suggester.generate_mixes()

        expected = [
            u'erso',
            u'ersolira',
            u'liraerso',
            u'lira',
            u'lerso',
            u'lirerso',
            u'lira.erso',
            u'erso.lira',
            u'ersol',
            u'ersolir',
        ]

        eq_(self.suggester.next_pack(), expected)
        for mix in self.suggester.mixes:
            ok_(not mix['values'])

        ok_(not self.suggester.next_pack())

        self.suggester.mixes = self.suggester.generate_mixes()
        with settings_context(PACK_SIZE=5):
            eq_(self.suggester.next_pack(), expected[:5])
            eq_(self.suggester.next_pack(), expected[5:])
            ok_(not self.suggester.next_pack())

    def test_with_max_combinations(self):
        self.suggester.login = u'liea'
        self.suggester.lang = 'ru'
        self.suggester.gender = 'f'

        with settings_context(
            MAX_COMBINATIONS=2,
            LANG_TO_MIXES=LANG_TO_MIXES,
            LETTER_TO_NUMBER_REPLACEMENTS=LETTER_TO_NUMBER_REPLACEMENTS,
            LETTER_TO_NUMBER_REPLACEMENTS_KEYS=LETTER_TO_NUMBER_REPLACEMENTS_KEYS,
            LOGIN_PREFIXES=TEST_LOGIN_PREFIXES,
            PREFIX_WEIGHT=PREFIX_WEIGHT,
        ):
            self.suggester.sources = self.suggester.generate_transliteration_sources_and_rules()
            self.suggester.elements = self.suggester.generate_elements()
            self.suggester.mixes = self.suggester.generate_mixes()

        expected = [
            {'limit': 1, 'values': [
                (100.0, u'liea'),
                (90.0, u'li3a'),
                (90.0, u'l1ea'),
                (81.0, u'l13a'),
            ]},
            {'limit': 2, 'values': [
                (88.32, u'ya.liea'),
                (79.49, u'ya.l1ea'),
            ]},
        ]

        eq_(len(self.suggester.mixes), len(expected))

        for i, items in enumerate(self.suggester.mixes):
            eq_(items['limit'], expected[i]['limit'])
            eq_(sorted(items['values'].nlargest()), sorted(expected[i]['values']))

    def test_transliteration_empty(self):
        self.suggester.last_name = u'ъь'
        self.suggester.lang = 'ru'
        self.suggester.gender = 'u'

        self.suggester.sources = self.suggester.generate_transliteration_sources_and_rules()
        self.suggester.elements = self.suggester.generate_elements()
        self.suggester.mixes = self.suggester.generate_mixes()

        eq_(self.suggester.mixes, [])
