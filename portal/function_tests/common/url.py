# -*- coding: utf-8 -*-
import allure
import logging
import re
import urllib
from urlparse import parse_qs, urlsplit
from abc import ABCMeta, abstractmethod

logger = logging.getLogger(__name__)


class ApiSearchUrl(object):
    __metaclass__ = ABCMeta

    def __init__(self, app_platform):
        self.app_platform = app_platform

    @abstractmethod
    def url_to_ping(self):
        pass

    @staticmethod
    def parse(app_platform, value):
        if not value:
            return value
        schema = re.compile('^(?P<schema>(?:[^:]+:)?//).*$').match(value).group('schema')
        parser = _SCHEMA_URL_MAP.get(schema, None)
        if not parser:
            raise RuntimeError('Failed to get parser for url {}'.format(value))
        return parser.parse(app_platform, value)


class HttpUrl(ApiSearchUrl):
    def __init__(self, app_platform, url):
        super(HttpUrl, self).__init__(app_platform)
        self.url = url

    def url_to_ping(self):
        return self.to_url()

    def to_url(self):
        if self.url.startswith('//'):
            return 'https:' + self.url
        return self.url

    @staticmethod
    def parse(app_platform, value):
        return HttpUrl(app_platform, value)


class YellowSkinUrl(ApiSearchUrl):
    def __init__(self, app_platform, url, **kwargs):
        super(YellowSkinUrl, self).__init__(app_platform)
        self.url = url

    def to_url(self):
        return 'yellowskin://?primary_color={}&secondary_color={}&url={}'.format(
            urllib.quote(self.url, safe=''),
        )

    @staticmethod
    def parse(app_platform, value):
        if not value.startswith('yellowskin://'):
            raise RuntimeError('Failed to parse yellowskin url "{}"'.format(value))

        query = re.compile(r'^yellowskin://\?(?P<query>.*)$').match(value).group('query')

        if not query:
            raise RuntimeError('Invalid yellowskin url "{}"'.format(value))

        parsed = {}

        for param in query.split('&'):
            k, v = param.split('=')
            parsed[k] = urllib.unquote(v)

        return YellowSkinUrl(app_platform=app_platform, **parsed)

    def url_to_ping(self):
        return self.url


class ViewportUrl(ApiSearchUrl):
    def __init__(self, app_platform, tab_id, text, top_tab_url):
        super(ViewportUrl, self).__init__(app_platform)
        self.tab_id = tab_id
        self.text = text
        self.top_tab_url = top_tab_url

    def to_url(self):
        return 'viewport://?tab_id={}&text={}&top_tab_url={}'.format(
            self.tab_id,
            urllib.quote(self.text, safe=''),
            urllib.quote(self.top_tab_url, safe='') if self.top_tab_url is not None else ''
        )

    @staticmethod
    def parse(app_platform, value):
        if not value.startswith('viewport://'):
            raise RuntimeError('Failed to parse viewport url "{}"'.format(value))

        intent_parse = re.compile('([^;=?&]+)=([^&]+)')

        args = {i: j for i, j in intent_parse.findall(value)}

        return ViewportUrl(
            app_platform=app_platform,
            tab_id=args.get('tab_id', None),
            text=urllib.unquote(args.get('text', None)),
            top_tab_url=urllib.unquote(args['top_tab_url']) if 'top_tab_url' in args else None
        )

    def url_to_ping(self):
        return self.top_tab_url


class IntentUrl(ApiSearchUrl):
    __metaclass__ = ABCMeta

    def __init__(self, app_platform):
        super(IntentUrl, self).__init__(app_platform)

    @staticmethod
    def parse(app_platform, value):
        if app_platform == 'android':
            return AndroidIntentUrl.parse(value)
        if app_platform == 'iphone':
            return IphoneIntentUrl.parse(value)


class AndroidIntentUrl(IntentUrl):
    def __init__(self, url, fallback_url, package, scheme):
        super(AndroidIntentUrl, self).__init__('android')
        self.url = url
        self.fallback_url = fallback_url
        self.package = package
        self.scheme = scheme

    def to_url(self):
        return 'intent://{}#Intent;S.browser_fallback_url={};package={};scheme={};end;'.format(
            self.url,
            urllib.quote(self.fallback_url, safe=''),
            urllib.quote(self.package),
            urllib.quote(self.scheme),
        )

    @staticmethod
    def parse(value, app_platform='android'):
        if not re.compile('^intent://.*#Intent;.*end;$').match(value):
            raise RuntimeError('Failed to parse android intent url "{}"'.format(value))

        intent_url = re.compile('^intent://(?P<url>[^#]*)#Intent;(?P<intent>.*)end;$')
        intent_parse = re.compile('([^;=]+)=([^;]+)')
        matched = intent_url.match(value)
        args = {i: j for i, j in intent_parse.findall(matched.group('intent'))}

        return AndroidIntentUrl(
            url=matched.group('url'),
            fallback_url=urllib.unquote(args.get('S.browser_fallback_url', None)),
            scheme=args.get('scheme', None),
            package=args.get('package', None)
        )

    def url_to_ping(self):
        return self.fallback_url


class IphoneIntentUrl(IntentUrl):
    def __init__(self, url, fallback_url):
        super(IphoneIntentUrl, self).__init__('iphone')
        self.url = url
        self.fallback_url = fallback_url

    def to_url(self):
        return 'intent://?fallback_url={}&url={}'.format(
            urllib.quote(self.fallback_url, safe=''),
            urllib.quote(self.url, safe=''),
        )

    @staticmethod
    def parse(value, app_platform='iphone'):
        if not re.compile('^intent://.*$').match(value):
            raise RuntimeError('Failed to parse iphone intent url "{}"'.format(value))

        intent_parse = re.compile('([^;=?&]+)=([^&]+)')

        args = {i: j for i, j in intent_parse.findall(value)}

        return IphoneIntentUrl(
            url=urllib.unquote(args.get('url', None)),
            fallback_url=urllib.unquote(args.get('fallback_url', None))
        )

    def url_to_ping(self):
        return self.fallback_url


class MordaNavigateUrl(ApiSearchUrl):
    def __init__(self, app_platform, card, fallback):
        super(MordaNavigateUrl, self).__init__(app_platform)
        self.card = card
        self.fallback = fallback

    def to_url(self):
        return 'mordanavigate://?card={}&fallback={}'.format(
            urllib.quote(self.card, safe=''),
            urllib.quote(self.fallback, safe='')
        )

    @staticmethod
    def parse(app_platform, value):
        if not value.startswith('mordanavigate://'):
            raise RuntimeError('Failed to parse mordanavigate url "{}"'.format(value))

        query = re.compile(r'^mordanavigate://\?(?P<query>.*)$').match(value).group('query')

        if not query:
            raise RuntimeError('Invalid mordanavigate url "{}"'.format(value))

        intent_parse = re.compile('([^;=?&]+)=([^&]+)')

        args = {i: j for i, j in intent_parse.findall(value)}

        return MordaNavigateUrl(
            app_platform=app_platform,
            card=urllib.unquote(args.get('card', None)),
            fallback=urllib.unquote(args.get('fallback', None))
        )

    def url_to_ping(self):
        return self.fallback if self.fallback.startswith('http') else None


class KeyboardUrl(ApiSearchUrl):
    def __init__(self, app_platform, utm_source):
        super(KeyboardUrl, self).__init__(app_platform)
        self.utm_source = utm_source

    def to_url(self):
        return 'keyboard://?utm_source={}'.format(
            urllib.quote(self.utm_source, safe=''),
        )

    def url_to_ping(self):
        pass

    @staticmethod
    def parse(app_platform, value):
        if not value.startswith('keyboard://'):
            raise RuntimeError('Invalid keyboard url "{}"'.format(value))

        intent_parse = re.compile('([^;=?&]+)=([^&]+)')

        args = {i: j for i, j in intent_parse.findall(value)}

        return KeyboardUrl(
            app_platform=app_platform,
            utm_source=urllib.unquote(args.get('utm_source', None)),
        )


def is_url(string):
    regex = re.compile(
        r'^(?:\w+)://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})?'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(regex, string)


def check_urls(obj, template, skip_fields=None):
    if skip_fields is None:
        skip_fields = []

    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in skip_fields:
                continue
            check_urls(v, template, skip_fields)

    elif isinstance(obj, list):
        for v in obj:
            check_urls(v, template, skip_fields)

    elif isinstance(obj, basestring):
        if is_url(obj):
            regex = re.compile(template, re.IGNORECASE)
            with allure.step('Test if url match with' + template):
                assert re.match(regex, obj), 'url=' + obj + ' dont match ' + template


def check_urls_params(obj, param, template, required=False, skip_fields=None):
    if skip_fields is None:
        skip_fields = []

    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in skip_fields:
                continue
            obj = v
            check_urls_params(obj, param, template, required, skip_fields)

    elif isinstance(obj, list):
        for v in obj:
            obj = v
            check_urls_params(obj, param, template, required, skip_fields)

    elif isinstance(obj, basestring):
        if is_url(obj):
            cgi_parameters = parse_qs(urlsplit(obj).query)
            p = cgi_parameters.get(param)
            if required:
                assert p, 'url=' + obj + '; doesn\'t have rquired param ' + param
            if p:
                p = p.pop()
                regex = re.compile(template)
                with allure.step('Test if url ' + param + 'match' + template):
                    assert re.match(regex, p), 'url=' + obj + '; ' + param + ' doesn\'t match ' + template + '; ' + p


_SCHEMA_URL_MAP = {
    'http://': HttpUrl,
    'https://': HttpUrl,
    '//': HttpUrl,
    'intent://': IntentUrl,
    'yellowskin://': YellowSkinUrl,
    'mordanavigate://': MordaNavigateUrl,
    'viewport://': ViewportUrl,
    'keyboard://': KeyboardUrl
}
