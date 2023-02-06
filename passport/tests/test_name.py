# -*- coding: utf-8 -*-

import json
import unittest

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.suggest.faker import FakeFioSuggest
from passport.backend.core.builders.suggest.name import (
    FioSuggest,
    get_gender,
    get_language_by_name,
    split_name,
)
from passport.backend.core.names.en import (
    EN_FEMALE_NAMES,
    EN_MALE_NAMES,
)
from passport.backend.core.names.ru import (
    RU_FEMALE_NAMES,
    RU_MALE_NAMES,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.useragent.sync import RequestError


@with_settings(FIO_SUGGEST_API_URL='http://localhost')
class TestExternalSuggest(unittest.TestCase):
    def setUp(self):
        self.fio = FioSuggest()
        self.faker = FakeFioSuggest()
        self.faker.start()

    def set_response(self, value):
        self.faker.set_response_value(
            'get',
            json.dumps({'passport': value}).encode('utf8'),
        )

    def tearDown(self):
        self.faker.stop()
        del self.faker

    def test_full_suggest(self):
        self.set_response([{"BasicFio": {"FirstName": u"Ольга", "Gender": "f", "LastName": u"Иванова-петрова"}}])

        suggest = self.fio.get(u"Иванова-петрова Ольга", fallback=False)
        eq_(suggest.firstname, u"Ольга")
        eq_(suggest.lastname, u"Иванова-петрова")
        eq_(suggest.gender, "female")
        ok_(self.fio.useragent is not None)
        suggest_request = self.faker.get_requests_by_url_prefix('http://localhost/passport')
        eq_(len(suggest_request), 1)

    def test_parial_suggest(self):
        self.set_response([{"BasicFio": {"FirstName": u"Ольга", "LastName": u"Иванова-петрова"}}])

        suggest = self.fio.get(u"Иванова-петрова Ольга", fallback=False)
        eq_(suggest.firstname, u"Ольга")
        eq_(suggest.lastname, u"Иванова-петрова")
        eq_(suggest.gender, None)

        self.set_response([{"BasicFio": {"Gender": "f", "LastName": u"Иванова-петрова"}}])

        suggest = self.fio.get(u"Иванова-петрова Ольга", fallback=False)
        eq_(suggest.firstname, None)
        eq_(suggest.lastname, u'Иванова-петрова')
        eq_(suggest.gender, 'female')

        self.set_response([{'BasicFio': {'FirstName': u'Ольга', 'Gender': 'f'}}])

        suggest = self.fio.get(u'Иванова-петрова Ольга', fallback=False)
        eq_(suggest.firstname, u'Ольга')
        eq_(suggest.lastname, None)
        eq_(suggest.gender, 'female')

    def test_fallback(self):
        self.set_response([])

        suggest = self.fio.get(u'Иван Иванов')
        eq_(suggest.firstname, u'Иван')
        eq_(suggest.lastname, u'Иванов')
        eq_(suggest.gender, 'male')

    def test_no_response(self):
        self.set_response([{}])

        suggest = self.fio.get('test data', fallback=False)
        eq_(suggest, (None, None, None))

    def test_empty_response(self):
        self.set_response([])

        suggest = self.fio.get('test data', fallback=False)
        eq_(suggest, (None, None, None))

    def test_invalid_json_response(self):
        self.faker.set_response_value('get', '<html/>')

        suggest = self.fio.get('test data', fallback=False)
        eq_(suggest, (None, None, None))

    def test_invalid_empty_json_response(self):
        self.faker.set_response_value('get', '')

        suggest = self.fio.get('test data', fallback=False)
        eq_(suggest, (None, None, None))

    def test_request_error(self):
        self.faker.set_response_side_effect('get', RequestError)

        suggest = self.fio.get(u'Иван Иванов')
        eq_(suggest.firstname, u'Иван')
        eq_(suggest.lastname, u'Иванов')
        eq_(suggest.gender, 'male')


def test_get_gender():
    params = [
        (('vasya', '', 'en'), 'unknown'),
        (('Adam', 'smith', 'en'), 'male'),
        (('Regina', 'Spektor', 'en'), 'female'),
        ((u'Александр', u'Друзь', 'ru'), 'male'),
        ((u'Кирилл', u'Мифодий', 'ru'), 'male'),
        ((u'федор', u'робинович', 'ru'), 'male'),
        ((u'Светлана', u'Моисеева', 'ru'), 'female'),
        ((u'Test', u'Моисеев', 'ru'), 'male'),
    ]

    for args, result in params:
        eq_(get_gender(*args), result)


def test_split_name():
    params = [
        ((u'Вася', RU_MALE_NAMES, 'ru'), (u'Вася', '')),
        ((u'Кирилл', RU_MALE_NAMES, 'ru'), (u'Кирилл', '')),
        ((u'Моисеева Светлана', RU_FEMALE_NAMES, 'ru'), (u'Светлана', u'Моисеева')),
        ((u'Светлана Моисеева', RU_FEMALE_NAMES, 'ru'), (u'Светлана', u'Моисеева')),
        ((u'Саша Моисеев', None, 'ru'), (u'Саша', u'Моисеев')),
        ((u'Моисеев Саша', None, 'ru'), (u'Саша', u'Моисеев')),
        (('Ray Charles', EN_MALE_NAMES, 'en'), ('Ray', 'Charles')),
        ((u'Janis Joplin', EN_FEMALE_NAMES, 'en'), (u'Janis', u'Joplin')),
        ((u'Joplin Janis', EN_FEMALE_NAMES, 'en'), (u'Janis', u'Joplin')),
    ]

    for args, result in params:
        eq_(split_name(*args), result)


def test_get_language_by_name():
    params = [
        (u'Василий', 'ru'),
        (u'Василий', 'ru'),
        (u'Ёёё', 'ru'),
        ('Ella', 'en'),
        (u'Jimmy', 'en'),
    ]
    for name, result in params:
        eq_(get_language_by_name(name), result)


@with_settings(FIO_SUGGEST_API_URL='localhost')
class TestExternalSuggestWithRequestMock(unittest.TestCase):
    def setUp(self):
        self.useragent = mock.Mock()
        self.fio_suggest = FioSuggest(useragent=self.useragent)

    def tearDown(self):
        del self.useragent
        del self.fio_suggest

    def set_response(self, value):
        response = mock.Mock()
        response.status_code = 200
        response.content = value
        self.useragent.request.return_value = response

    def test_ok(self):
        self.set_response(
            u'{"passport":[{"BasicFio":{"Gender":"m","FirstName":"ВАСИЛИЙ ВАСИЛЬЕВИЧ","LastName":"ВАСИЛЬЕВ"}}]}'.encode('utf8'),
        )

        suggest = self.fio_suggest.get(u'ВАСИЛИЙ ВАСИЛЬЕВИЧ ВАСИЛЬЕВ', fallback=False)
        eq_(suggest.firstname, u'ВАСИЛИЙ ВАСИЛЬЕВИЧ')
        eq_(suggest.lastname, u'ВАСИЛЬЕВ')
        eq_(suggest.gender, 'male')
