#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import watchdog_helpers as wh

import json


class SuggestParserFactory:
    def __init__(self):
        self.parsers = [
            SuggestFFParser(),
            SuggestSDParser(),
            SuggestYAParser(),
            SuggestEndingsParser(),
            SuggestBrowserParser(),
            SuggestOperaParser(),
            SuggestSLParser()
        ]

    def get_word_suggest(self, url, handler):
        for parser in self.parsers:
            if parser.get_handler() == handler:
                return parser.get_word_suggest(url)

    def get_fulltext_suggest(self, url, handler):
        for parser in self.parsers:
            if parser.get_handler() == handler:
                return parser.get_fulltext_suggest(url)

    def get_nav_suggest(self, url, handler):
        for parser in self.parsers:
            if parser.get_handler() == handler:
                return parser.get_nav_suggest(url)

    def get_fact_suggest(self, url, handler):
        for parser in self.parsers:
            if parser.get_handler() == handler:
                return parser.get_fact_suggest(url)


class SuggestParser:
    def __init__(self):
        pass

    def get_response(self, url):
        return json.loads(wh.get_url(url))

    def get_handler(self):
        pass

    def get_word_suggest(self, url):
        pass

    def get_fulltext_suggest(self, url):
        pass

    def get_nav_suggest(self, url):
        pass

    def get_fact_suggest(self, url):
        pass


class SuggestFFParser(SuggestParser):
    def get_handler(self):
        return '/suggest/suggest-ff.cgi?'

    def get_fulltext_suggest(self, url):
        return self.get_response(url)[1]

    def get_nav_suggest(self, url):
        pass

    def get_fact_suggest(self, url):
        pass


class SuggestEndingsParser(SuggestParser):
    def get_handler(self):
        return '/suggest/suggest-endings?'

    def get_word_suggest(self, url):
        return [item[0] for item in self.get_response(url)[2]]

    def get_fulltext_suggest(self, url):
        url = url + 'full_text_count=5&'
        return [item[0] for item in self.get_response(url)[4]['suggestions']]

    def get_nav_suggest(self, url):
        return [item[1] for item in self.get_response(url) if type(item) == list and item[0] == 'nav']

    def get_fact_suggest(self, url):
        return [item[1] for item in self.get_response(url) if type(item) == list and item[0] == 'fact']


class SuggestSDParser(SuggestParser):
    def get_handler(self):
        return '/suggest/suggest-sd.cgi?'

    def get_fulltext_suggest(self, url):
        response = self.get_response(url)
        return [item for item in response[1] if len(response[2][response[1].index(item)]) == 0]

    def get_nav_suggest(self, url):
        response = self.get_response(url)
        return [item for item in response[2]]

    def get_fact_suggest(self, url):
        pass


class SuggestYAParser(SuggestParser):
    def get_handler(self):
        return '/suggest/suggest-ya.cgi?'

    def get_fulltext_suggest(self, url):
        url = url + 'v=4'

        return [item for item in self.get_response(url)[1] if type(item) == unicode]

    def get_nav_suggest(self, url):
        url = url + 'v=4'
        return [item for item in self.get_response(url)[1] if type(item) == list and item[0] == 'nav'][0]

    def get_fact_suggest(self, url):
        url = url + 'v=4&fact=1'
        return [item[1] for item in self.get_response(url)[1] if type(item) == list and item[0] == 'fact']


class SuggestBrowserParser(SuggestParser):
    def get_handler(self):
        return '/suggest/suggest-browser?'

    def get_fulltext_suggest(self, url):
        response = self.get_response(url)
        return [item for item in response[1] if len(response[2][response[1].index(item)]) == 0]

    def get_nav_suggest(self, url):
        return [item for item in self.get_response(url)[2] if len(item) != 0]

    def get_fact_suggest(self, url):
        pass


class SuggestOperaParser(SuggestParser):
    def get_handler(self):
        return '/suggest-opera?'

    def get_fulltext_suggest(self, url):
        return self.get_response(url)[1]

    def get_nav_suggest(self, url):
        url = url + 'nav=yes'
        return self.get_response(url)[2]

    def get_fact_suggest(self, url):
        pass


class SuggestSLParser(SuggestParser):
    def get_handler(self):
        return '/suggest-sl?'

    def get_fulltext_suggest(self, url):
        return self.get_response(url)[1]

    def get_nav_suggest(self, url):
        pass

    def get_fact_suggest(self, url):
        pass
