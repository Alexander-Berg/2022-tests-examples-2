# -*- coding: utf-8 -*-
import hashlib
import logging
import time

from furl import furl
from requests import Session
import re
from common.env import morda_env
from common.http import Req
from common.morda import Morda, MordaWithRegion, DesktopMain
from common.utils import delete

logger = logging.getLogger(__name__)


class MordaClient(object):
    def __init__(self, morda=None, env=None):
        if env is None:
            env = morda_env()
        self.env = env
        self._session = Session()
        if morda is None:
            morda = DesktopMain()
        self._morda = morda
        self._prepare_client()

    def _prepare_client(self):
        if isinstance(self._morda, MordaWithRegion) and self._morda.region:
            self._session.cookies.set('yandex_gid', str(self._morda.region), domain=self._morda.get_cookie_domain())

        for cookie, value in self._morda.cookies.iteritems():
            self._session.cookies.set(cookie, value, domain=self._morda.get_cookie_domain())

    def _prepare_request(self, req):
        headers = req.headers or {}
        headers['User-Agent'] = self._morda.user_agent

        if self._morda.experiments:
            headers['X-Yandex-TestExpForceDisabled'] = '1'
            headers['X-Yandex-TestExp'] = ','.join(self._morda.experiments)

        if self._morda.counters is not None:
            headers['X-Yandex-TestCounters'] = str(self._morda.counters)

        req.rh()

        for k, v in self._morda.headers.iteritems():
            headers[k] = v

        req.headers = headers
        return req

    def export(self, name, **kwargs):
        url = Morda.get_origin(env=self.env)

        if not kwargs:
            kwargs = {}

        if 'params' not in kwargs:
            kwargs['params'] = {}

        kwargs['params']['export'] = name
        kwargs['params']['cleanvars'] = 1

        if 'step' not in kwargs:
            kwargs['step'] = 'Get export "{}" from "{}"'.format(name, self.env)

        return Req(url, session=self._session, cookies={'yandex_gid': '213'}, allow_retry=True, retries=10 **kwargs)

    def request(self, **kwargs):
        if 'allow_retry' not in kwargs:
            kwargs['allow_retry'] = True
        if 'retries' not in kwargs:
            kwargs['retries'] = 10
        return self._prepare_request(Req(session=self._session, **kwargs))

    def morda(self):
        req = Req(self._morda.get_url(self.env), session=self._session, allow_retry=True, retries=10)
        return self._prepare_request(req)

    def cleanvars(self, blocks=None, **kwargs):
        if 'params' not in kwargs:
            kwargs['params'] = {}
        kwargs['params']['cleanvars'] = '1' if not blocks else '|'.join(['{}'.format(block) for block in blocks])
        req = Req(self._morda.get_url(self.env), session=self._session, allow_retry=True, retries=10, **kwargs)
        return self._prepare_request(req)

    def cleanvars_data(self, blocks=None, **kwargs):
        request = self.cleanvars(blocks, **kwargs).send()
        if request.is_ok():
            return request.json()
        else:
            return None

    def tvstream_online_data(self, **kwargs):
        req = Req('{}/portal/tvstream_json/online'.format(self._morda.get_url(self.env)),
                  session=self._session, allow_retry=True, retries=10, **kwargs)
        request = self._prepare_request(req).send()
        if request.is_ok():
            return request.json()
        else:
            return None

    def tvstream_data(self,  **kwargs):
        if 'params' not in kwargs:
            kwargs['params'] = {}
        kwargs['params']['json'] = '1'
        kwargs['params']['cleanvars'] = '1'
        req = Req('{}/portal/tvstream'.format(self._morda.get_url(self.env)),
                  session=self._session, allow_retry=True, retries=10, **kwargs)
        request = self._prepare_request(req).send()
        if request.is_ok():
            return request.json()
        else:
            return None

    def themes(self):
        req = Req('{}/themes'.format(self._morda.get_url(self.env)), params=dict(cleanvars=1), session=self._session, allow_retry=True, retries=10)
        return self._prepare_request(req)

    def theme_set(self, theme):
        params = dict(sk=self.get_sk())
        req = Req('{}/themes/{}/set'.format(self._morda.get_url(self.env), theme),
                  params=params, session=self._session, allow_retry=True, retries=10)
        return self._prepare_request(req)

    def api_search_2(self, block='', app_platform='android', app_version=None,
                     afisha_version=3, dp=None, geo=None, lang=None, lat=None,
                     lon=None, size=None, os_version=None, uuid=None, ab_flags=None,
                     user_agent=None, zen_extensions=None, informersCard=None, processAssist=None,
                     bs_promo=None, app_id=None, madm_mocks=None, morda_ng=None, cleanvars=None, 
                     topnews_extra_params=None, httpmock=None, geo_by_settings=None, OAuth=None, **kwargs):
        params = kwargs
        params.update({
            'app_platform': app_platform,
            'app_version': app_version,
            'afisha_version': afisha_version,
            'dp': dp,
            'geo_by_settings': geo,
            'lang': lang,
            'lat': lat,
            'lon': lon,
            'size': size,
            'uuid': uuid,
            'ab_flags': ab_flags,
            'madm_mocks': madm_mocks,
            'morda_ng': morda_ng,
        })
        if OAuth is not None:
            params["oauth"] = OAuth

        if geo_by_settings is not None:
            params['geo_by_settings'] = geo_by_settings

        if cleanvars is not None:
            params['cleanvars'] = cleanvars

        if topnews_extra_params is not None:
            params['topnews_extra_params'] = topnews_extra_params

        if httpmock is not None:
            params['httpmock'] = httpmock
        
        if app_id is not None:
            params['app_id'] = app_id

        if bs_promo is not None:
            params['bs_promo'] = bs_promo

        if processAssist is not None:
            params['processAssist'] = processAssist

        if zen_extensions is not None:
            params['zen_extensions'] = zen_extensions

        if informersCard is not None:
            params['informersCard'] = informersCard

        if os_version is not None:
            params['os_version'] = os_version

        if madm_mocks is not None:
            params['madm_mocks'] = madm_mocks

        if morda_ng is not None:
            params['morda_ng'] = morda_ng

        base_url = Morda.get_origin(env=self.env)
        headers = {'X-Yandex-Autotests': '1'}
        if user_agent is not None:
            headers['User-Agent'] = user_agent

        return Req('{}/portal/api/search/2/{}'.format(base_url, block), params=params,
                   headers=headers, session=self._session, allow_retry=True, retries=10)

    def api_yabrowser_2(self, block='', app_platform='android', app_version=None, dp=None, geo=None,
                        lang=None, lat=None, lon=None, size=None, os_version=None, uuid=None,
                        make_morda_first_feed=None, user_agent=None, zen_extensions=None,
                        zenkit_experiments=None, informersCard=None, processAssist=None, ab_flags=None,):

        params = {
            'app_platform': app_platform,
            'app_version': app_version,
            'dp': dp,
            'geo_by_settings': geo,
            'lang': lang,
            'lat': lat,
            'lon': lon,
            'size': size,
            'uuid': uuid,
            'ab_flags': ab_flags,
        }
        if processAssist is not None:
            params['processAssist'] = processAssist

        if os_version is not None:
            params['os_version'] = os_version

        if make_morda_first_feed is not None:
            params['make_morda_first_feed'] = make_morda_first_feed

        if zen_extensions is not None:
            params['zen_extensions'] = zen_extensions

        if zenkit_experiments is not None:
            params['zenkit_experiments'] = zenkit_experiments

        if informersCard is not None:
            params['informersCard'] = informersCard

        base_url = Morda.get_origin(env=self.env)
        headers = {'X-Yandex-Autotests': '1'}
        if user_agent is not None:
            headers['User-Agent'] = user_agent

        return Req('{}/portal/api/yabrowser/2/{}'.format(base_url, block), params=params,
                   headers=headers, session=self._session, allow_retry=True, retries=10)

    def simple(self, params=None):

        request    = delete(params, 'request')
        user_agent = delete(params, 'user_agent')

        base_url = Morda.get_origin(env=self.env)
        headers  = {'X-Yandex-Autotests': '1'}
        if user_agent is not None:
            headers['User-Agent'] = user_agent

        return Req('{}{}'.format(base_url, request), params=params,
                   headers=headers, session=self._session, allow_retry=True, retries=10)

    def api_ioswidget_2(self, block='', app_platform='iphone', app_version=None, dp=None, geo=None,
                        lang=None, lat=None, lon=None, size=None, os_version=None, uuid=None):

        params = {
            'app_platform': app_platform,
            'app_version': app_version,
            'dp': dp,
            'geo_by_settings': geo,
            'lang': lang,
            'lat': lat,
            'lon': lon,
            'size': size,
            'uuid': uuid,
        }
        if os_version is not None:
            params['os_version'] = os_version

        base_url = Morda.get_origin(env=self.env)
        headers = {'X-Yandex-Autotests': '1'}

        return Req('{}/portal/api/ios_widget/2/{}'.format(base_url, block), params=params,
                   headers=headers, session=self._session, allow_retry=True, retries=10)

    def portal_ntp_notifications(self, cards='', geo=None):
        base_url = Morda.get_origin(env=self.env)
        params = {
            'cards': cards,
            'geo': geo,
        }
        headers = {'X-Yandex-Autotests': '1'}

        return Req('{}/portal/ntp/notifications/'.format(base_url), params=params,
                   headers=headers, session=self._session, allow_retry=True, retries=10)

    def portal_ntp_refresh_data(self, **kwargs):
        if 'params' not in kwargs:
            kwargs['params'] = {}
        headers = {'X-Yandex-Autotests': '1'}
        req = Req('{}/portal/ntp/refresh_data/'.format(Morda.get_origin(env=self.env)), session=self._session, allow_retry=True, retries=10, **kwargs)
        return self._prepare_request(req)

    def subs_config_0(self, block='', app_platform='android', app_version=None, afisha_version=3, dp=None, geo=None,
                      lang=None, lat=None, lon=None, size=None, os_version=None, uuid=None, user_agent=None):

        params = {
            'app_platform': app_platform,
            'app_version': app_version,
            'afisha_version': afisha_version,
            'dp': dp,
            'geo_by_settings': geo,
            'lang': lang,
            'lat': lat,
            'lon': lon,
            'size': size,
            'uuid': uuid,
        }

        base_url = Morda.get_origin(env=self.env)
        headers = {'X-Yandex-Autotests': '1'}

        return Req('{}/portal/subs/config/0{}'.format(base_url, block), params=params,
                   headers=headers, session=self._session, allow_retry=True, retries=10)

    def android_widget_api(self, block='', app_platform='android', app_version=None, afisha_version=3, dp=None,
                           geo=None, lang=None, ll=None, from_app='', os_version=None, uuid=None):

        params = {
            'block': block,
            'app_platform': app_platform,
            'app_version': app_version,
            'geo_by_settings': geo,
            'lang': lang,
            'll': ll,
            'afisha_version': afisha_version,
            'dp': dp,
            'from': from_app,
            'uuid': uuid,
        }

        base_url = Morda.get_origin(env=self.env)
        headers = {'X-Yandex-Autotests': '1'}

        return Req('{}/android_widget_api/2'.format(base_url), params=params,
                   headers=headers, session=self._session, allow_retry=True, retries=10)

    def api_data_samsung_bixby(self, geo=None):

        params = {
            'geo_by_settings': geo,
        }

        base_url = Morda.get_origin(env=self.env)
        headers = {'X-Yandex-Autotests': '1'}

        return Req('{}/samsung-bixby/'.format(base_url), params=params,
                   headers=headers, session=self._session, allow_retry=True, retries=10)

    def any(self, url):
        parsed_url = furl(url)
        headers = {}

        if self.env == 'production':
            any_host = 'http://any.yandex.ru'
            headers['HOST'] = parsed_url.netloc
        else:
            any_host = 'http://any-{}.yandex.ru'.format(self.env)
            headers['DEV-HOST'] = parsed_url.netloc

        if parsed_url.scheme == 'https':
            headers['X-YANDEX-HTTPS'] = '1'

        parsed_url.origin = any_host

        return Req(parsed_url.url, headers=headers, allow_redirects=False, allow_retry=True, retries=10)

    def make_url(self, url_fmt, *args):
        return url_fmt.format(self._morda.get_url(self.env), *args)

    def login(self, passport_host, login, password):
        data = 'login={}&passwd={}'.format(login, password)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        return self._prepare_request(
            Req(method='POST', url='https://{}/passport'.format(passport_host), data=data, headers=headers,
                session=self._session, allow_retry=True, retries=10))

    def logout(self, passport_host):
        params = {
            'mode': 'logout',
            'yu': self.get_yu()
        }
        return self._prepare_request(
            Req(url='https://{}/passport'.format(passport_host), params=params, session=self._session, allow_retry=True, retries=10))

    def __repr__(self):
        return 'Morda client on host "{}"'.format(self.env)

    def get_uid(self, morda):
        session_id = self._session.cookies.get('Session_id', domain=morda.get_cookie_domain())
        if not session_id:
            return None

        parts = session_id.split('.')

        if len(parts) < 4:
            raise RuntimeError('Cookie "Session_id" has incorrect format: ' + session_id)

        if session_id.startswith('2'):
            return parts[3].lstrip('*')
        elif session_id.startswith('3'):
            return parts[4][2:]

        raise RuntimeError('Failed to parse "Session_id": ' + session_id)

    def get_yu(self):
        return self._session.cookies.get('yandexuid', domain=self._morda.get_cookie_domain())

    def get_cookie(self, cookie_name, domain=None):
        if domain is None:
            domain = self._morda.get_cookie_domain()
        return self._session.cookies.get(cookie_name, domain=domain)

    def remove_cookie(self, cookie_name, domain=None):
        if domain is None:
            domain = self._morda.get_cookie_domain()
        return self._session.cookies.clear(name=cookie_name, domain=domain, path='/')

    def set_cookie(self, cookie_name, value, domain=None):
        if domain is None:
            domain = self._morda.get_cookie_domain()
        return self._session.cookies.set(cookie_name, str(value), domain=domain)

    def get_yandexuid(self, domain=None):
        return self.get_cookie('yandexuid', domain=domain)

    def get_cookie_my(self, domain=None):
        return self.get_cookie('my', domain)

    def get_cookie_yp(self, domain=None):
        return self.get_cookie('yp', domain)

    def set_cookie_yp(self, yp_value, domain=None):
        return self.set_cookie('yp', yp_value, domain=domain)

    def test_cookie_yp(self, test_pattern, domain=None):
        if test_pattern is None:
            assert not self.get_cookie('yp', domain), 'yp must be empty'
        else:
            assert test_pattern in self.get_cookie('yp', domain), test_pattern + ' does not exists in yp'

    def get_cookie_yandex_gid(self, domain=None):
        return self.get_cookie('yandex_gid', domain)

    def set_cookie_yandex_gid(self, region, domain=None):
        self.set_cookie('yandex_gid', region, domain=domain)

    def test_cookie_yandex_gid(self, test_id, domain=None):
        assert test_id == self.get_cookie_yandex_gid(domain)

    def test_cookie(self, cookie_name, test_pattern, domain=None):
        cookies = self.get_cookie(cookie_name, domain)
        assert cookies is not None, 'Have no cookies for domain {}'.format(domain)
        assert test_pattern in cookies

    def test_cookie_regex(self, cookie_name, test_pattern_regex, domain=None):
        cookies = self.get_cookie(cookie_name, domain)
        assert cookies is not None, 'Have no cookies for domain {}'.format(domain)
        assert re.search(test_pattern_regex, cookies)

    def get_sk(self):
        """
        Генерация csrf токена для морды (версия 1)
        :return: string
        """
        yandexuid = self.get_yu()
        if yandexuid is None:
            raise RuntimeError('not yandexuid in cookies')
        current_time = time.time()
        days = int(current_time // 86400)
        m = hashlib.md5('0:' + yandexuid + ':' + str(days))
        return 'y' + m.hexdigest()

    def is_logged(self, morda):
        pass

    def set_tune(self, secret_key, method, name, value, retpath):
        """
        Вызов ручки /portal/set/tune/ двумя способами - GET/POST
        выставляет значение в сабкуку yp и куку my
        :param secret_key: str
        :param method: str 'GET' или 'POST'
        :param name: string
        :param value: string
        :param retpath: string
        :return:
        """
        params = {
            'sk': secret_key or self.get_sk(),
            'retpath': retpath,
        }
        if value is not None:
            params[name] = value

        base_url = self._morda.get_origin(env=self.env, domain=self._morda.get_domain())

        if method == 'GET':
            return Req('{}/portal/set/tune/'.format(base_url), params=params, session=self._session,
                       allow_redirects=False, allow_retry=True, retries=10)
        elif method == 'POST':
            params['fields'] = name
            return Req('{}/portal/set/tune/'.format(base_url), method='POST', session=self._session, data=params,
                       allow_redirects=False, allow_retry=True, retries=10)
        else:
            raise RuntimeError('bad method for set_tune')

    def set_my(self, secret_key, params, retpath):
        """
        Вызов ручки /portal/set/my/
        выставляет значение в сабкуку yp и куку my
        :param secret_key: str
        :param params: tuple
        :param retpath: string
        :return:
        """
        query_params = (
            ('sk', secret_key or self.get_sk()),
            ('retpath', retpath),
        )

        query_params += params

        base_url = self._morda.get_origin(env=self.env, domain=self._morda.get_domain())

        return Req('{}/portal/set/my/'.format(base_url), params=query_params, session=self._session,
                   allow_redirects=False, allow_retry=True, retries=10)

    def set_region(self, secret_key, method, params, retpath, allow_redirects=True):
        """
        Вызов ручки /portal/set/region/
        выставляет значение в сабкуку yp и куку my
        :param secret_key: str
        :param method: str
        :param params: dict
        :param retpath: string
        :param allow_redirects: boolean
        :return:
        """
        query_params = {
            'sk': secret_key or self.get_sk(),
            'retpath': retpath,
        }

        query_params.update(params)

        base_url = self._morda.get_origin(env=self.env, domain=self._morda.get_domain())

        if method == 'GET':
            return Req('{}/portal/set/region/'.format(base_url), params=query_params, session=self._session,
                       allow_redirects=allow_redirects, allow_retry=True, retries=10)
        elif method == 'POST':
            # params['fields'] = name
            return Req('{}/portal/set/region/'.format(base_url), method='POST', session=self._session,
                       data=query_params, allow_redirects=allow_redirects, allow_retry=True, retries=10)

    def set_any(self, secret_key=None, params=None, retpath=None):
        """
        Вызов ручки /portal/set/any/
        выставляет сабкуки в куку yp
        :param secret_key: str
        :param params: dict
        :param retpath: string
        :return:
        """
        query_params = {
            'sk': secret_key or self.get_sk(),
            'retpath': retpath,
        }
        query_params.update(params)

        base_url = self._morda.get_origin(env=self.env, domain=self._morda.get_domain())

        return Req('{}/portal/set/any/'.format(base_url), params=query_params, session=self._session,
                   allow_redirects=False, allow_retry=True, retries=10)

    def set_lang(self, secret_key, params):
        """
        Вызов ручки /portal/set/my/
        выставляет значение в сабкуку yp и куку my
        :param secret_key: str
        :param params: tuple
        :return:
        """
        query_params = {
            'sk': secret_key or self.get_sk(),
            'retpath': 'https://www.yandex.ru/',
        }

        query_params.update(params)

        base_url = self._morda.get_origin(env=self.env, domain=self._morda.get_domain())

        return Req('{}/portal/set/lang/'.format(base_url), params=query_params, session=self._session,
                   allow_redirects=False, allow_retry=True, retries=10)

    def set_gpsave(self, lat, lon, precision, secret_key, retpath='https://www.yandex.ru/', params=None):
        """
        Вызов ручки /gpsave
        выставляет значение блока gpauto в сабкуку yp
        :param lat: str
        :param lon: str
        :param precision: str
        :param secret_key: str
        :param retpath: str
        :param params: dict
        :return:
        """
        query_params = {
            'sk': secret_key or self.get_sk(),
            'retpath': retpath,
            'lat': lat,
            'lon': lon,
            'precision': precision,
        }

        if params is not None:
            query_params.update(params)

        base_url = self._morda.get_origin(env=self.env, domain=self._morda.get_domain())

        return Req('{}/gpsave'.format(base_url), params=query_params, session=self._session, allow_retry=True, retries=10)


class StreamClient(object):
    def __init__(self, host=None):
        self.host = host if host else 'https://frontend.vh.yandex.ru'

    def episodes(self, channel_id, start_date_from=None, start_date_to=None, end_date_from=None, end_date_to=None,
                 locale='ru', offset=None, limit=None):
        params = {
            'parent_id': channel_id,
            'start_date__from': start_date_from,
            'start_date__to': start_date_to,
            'end_date__from': end_date_from,
            'end_date__to': end_date_to,
            'locale': locale,
            'offset': offset,
            'limit': limit
        }

        return Req('{}/episodes.json'.format(self.host), rh=1,  headers={'X-Forwarded-For': '93.158.178.98'},
                   params=params, allow_retry=True, retries=10)


class GeohelperClient(object):
    # def __init__(self, host='l7test.yandex.ru/geohelper'):
    # def __init__(self, host='l7test.yandex.ru/geohelper-dev'):
    def __init__(self, host='yandex.ru/geohelper', url=None):
        if url is None:
            self.host = host
            self.url = None
        else:
            self.url = url

    def get_check(self):
        if self.url is not None:
            raise RuntimeError('Client with url is not support Check')
        return Req(url='https://{}/check'.format(self.host), allow_retry=True, retries=10)

    def simple_get(self, params, post_data):
        """
        Получение данных для морды
        Обязательные параметры в params: lat, long, lang, geoid,
        :param params: dict
        :param post_data: str
        :return:
        """
        if self.url is not None:
            raise RuntimeError('Client with url is not support simple get')
        return Req(url='https://{}/get'.format(self.host), method='POST', params=params, data=post_data, allow_retry=True, retries=10)

    def searchapp_get(self, params=None, post_data=''):
        """
        Получение данных для поискового приложения
        :param params: dict
        :param post_data: str
        :return:
        """
        post_data = post_data.encode('utf-8')
        if self.url is not None:
            return Req(url=self.url, method='POST', data=post_data, allow_retry=True, retries=10)
        else:
            return Req(url='https://{}/api/v1/sa_heavy'.format(self.host), method='POST', params=params, data=post_data, allow_retry=True, retries=10)


class ConfigppClient(object):
    def __init__(self, env=None):
        if env is None:
            env = morda_env()
        host = Morda.get_origin(env=env)
        self.host = host

    def simple_get(self, params=None):
        return Req(url='{}/portal/mobilesearch/config/searchapp'.format(self.host), method='GET', params=params, allow_retry=True, retries=10)

    def get(self, params=None, headers=None):
        return Req(url='{}/portal/mobilesearch/config/searchapp'.format(self.host), method='GET', params=params,
                   headers=headers, allow_retry=True, retries=10)


class VpsClient(object):
    def __init__(self, env=None):
        if env is None:
            env = morda_env()
        host = Morda.get_origin(env=env)
        self.host = host

    def simple_get(self, params=None):
        return Req(url='{}/portal/mobilesearch/vps'.format(self.host), method='GET', params=params, allow_retry=True, retries=10)

    def get(self, params=None, headers=None):
        return Req(url='{}/portal/mobilesearch/vps'.format(self.host), method='GET', params=params,
                   headers=headers, allow_retry=True, retries=10)
