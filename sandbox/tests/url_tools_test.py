# -*- coding: utf-8 -*-

import url_tools


class TestGetQueriesFromUrls(object):
    def test_should_return_text_query(self):
        input = [
            'https://yandex.ru/search/?text=1',
            'https://yandex.ru/search/?text=2'
        ]
        expected = ['1', '2']
        actual = url_tools.get_queries_from_urls(input)

        assert actual == expected

    def test_should_return_filtered_text_queries(self):
        input = [
            'https://yandex.ru/search/?text=1',
            'https://yandex.ru/search/?netext=2'
        ]
        expected = ['1']
        actual = url_tools.get_queries_from_urls(input)

        assert actual == expected


class TestGetQueryFromUrl(object):
    def test_should_return_text_query(self):
        input = 'https://yandex.ru/search/?text=1'
        expected = '1'
        actual = url_tools.get_query_from_url(input)

        assert actual == expected

    def test_should_return_none_if_text_is_not_exist(self):
        input = 'https://yandex.ru/search/?netext=1'
        expected = None
        actual = url_tools.get_query_from_url(input)

        assert actual == expected

    def test_should_return_none_if_non_utf8_symbol(self):
        input = 'https://yandex.ru/search/?text=%F1LOL'
        expected = None
        actual = url_tools.get_query_from_url(input)

        assert actual == expected

    def test_should_return_unicode_string(self):
        input = 'https://yandex.ru/search/?text=%D0%BF%D1%80%D0%B8%D0%B2%D0%B5%D1%82'
        expected = u'привет'
        actual = url_tools.get_query_from_url(input)

        assert actual == expected

    def test_should_return_none_if_url_is_unicode_type(self):
        input = u'https://yandex.ru/search/?text=test'
        expected = u'test'
        actual = url_tools.get_query_from_url(input)

        assert actual == expected
