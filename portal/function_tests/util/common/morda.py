# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

from furl import furl
from publicsuffix2 import get_public_suffix

from portal.function_tests.util.common import env
from portal.function_tests.util.common.geobase import get_kubr_domain


# FIXME: походу не испольхуется - надо убрать наверное
class Language(object):
    RU = 'ru'
    UK = 'uk'
    BE = 'be'
    KK = 'kk'
    EN = 'en'


class Morda(object):
    __metaclass__ = ABCMeta

    def __init__(self, scheme='https', prefix='', path='', name=None, params=None, user_agent=None,
                 experiments=None, headers=None, cookies=None, counters=None, morda_content=None,
                 no_prefix=True, **kwargs):
        self.scheme = scheme
        self.prefix = prefix
        self.user_agent = user_agent
        self.path = path
        self.params = params or dict()
        self.headers = headers or dict()
        self.cookies = cookies or dict()
        self.experiments = set(experiments) if experiments else {}
        self.counters = counters
        self.name = name or self.__class__.__name__
        self.morda_content = morda_content
        self.no_prefix = no_prefix

    @abstractmethod
    def get_domain(self):
        """
        Возвращается TLD 'ru', 'com.tr' etc.
        :return: str
        """
        return ''

    # FIXME: нет возможности сгенерировать origin равный yandex.ru
    @staticmethod
    def get_origin(scheme='https', env='production', prefix='www', domain='ru', no_prefix=False):
        """
        Протокол плюс полный домен - https://yandex.TLD/
        :param scheme: string
        :param env: string
        :param prefix: string
        :param domain: string
        :return: string
        """

        if no_prefix:
            return '{scheme}://{env}yandex.{domain}'.format(scheme=scheme,
                                                            env=Morda._get_env_prefix(prefix=None, env=env),
                                                            domain=domain)
        else:
            return '{scheme}://{env}yandex.{domain}'.format(scheme=scheme,
                                                            env=Morda._get_env_prefix(prefix=prefix, env=env),
                                                            domain=domain)

    def get_cookie_domain(self):
        """
        Возвращает домен, на который ставятся куки
        :return: string
        """
        return '.' + get_public_suffix(self.get_url())

    def get_url(self, env='production'):
        """
        Протокол, домен, локейшн, параметры https://yandex.TLD/location...
        :param env: string
        :return: string
        """

        url = furl(Morda.get_origin(scheme=self.scheme,
                                    env=env,
                                    prefix=self.prefix,
                                    domain=self.get_domain(),
                                    no_prefix=self.no_prefix))

        url.path.set(self.path)

        if self.params:
            url.args.update(**self.params)

        return url.url

    @staticmethod
    def _get_env_prefix(prefix, env):
        if env == 'production':
            return prefix + '.' if prefix else ''
        else:
            return prefix + '-' + env + '.' if prefix else env + '.'

    def __str__(self):
        return self.name


class MordaWithLanguage(Morda):
    __metaclass__ = ABCMeta

    def __init__(self, language=None, **kwargs):
        super(MordaWithLanguage, self).__init__(**kwargs)
        self.language = language

    def __str__(self):
        return super(MordaWithLanguage, self).__str__() + ', language=' + str(self.language)


class MordaWithRegion(Morda):
    __metaclass__ = ABCMeta

    def __init__(self, region=None, **kwargs):
        super(MordaWithRegion, self).__init__(**kwargs)
        self.region = region

    def __str__(self):
        return super(MordaWithRegion, self).__str__() + ', region=' + str(self.region)


class DesktopMorda(Morda):
    __metaclass__ = ABCMeta

    def __init__(self, user_agent=None, **kwargs):
        if not user_agent:
            user_agent = env.desktop_ua()
        super(DesktopMorda, self).__init__(user_agent=user_agent, **kwargs)


class TouchMorda(Morda):
    __metaclass__ = ABCMeta

    def __init__(self, user_agent=None, **kwargs):
        if not user_agent:
            user_agent = env.touch_ua()
        super(TouchMorda, self).__init__(user_agent=user_agent, **kwargs)


class TouchWpMorda(Morda):
    __metaclass__ = ABCMeta

    def __init__(self, user_agent=None, **kwargs):
        if not user_agent:
            user_agent = env.touch_wp_ua()
        super(TouchWpMorda, self).__init__(user_agent=user_agent, **kwargs)


class PdaMorda(Morda):
    __metaclass__ = ABCMeta

    def __init__(self, user_agent=None, **kwargs):
        if not user_agent:
            user_agent = env.pda_ua()
        super(PdaMorda, self).__init__(user_agent=user_agent, **kwargs)


class TelMorda(Morda):
    __metaclass__ = ABCMeta

    def __init__(self, user_agent=None, **kwargs):
        if not user_agent:
            user_agent = env.tel_ua()
        super(TelMorda, self).__init__(user_agent=user_agent, **kwargs)


class KubrMorda(MordaWithRegion):
    __metaclass__ = ABCMeta

    def __init__(self, region=None, **kwargs):
        super(KubrMorda, self).__init__(region=region, **kwargs)

    def get_domain(self):
        return get_kubr_domain(self.region)


class MainMorda(MordaWithLanguage, KubrMorda):
    __metaclass__ = ABCMeta

    def __init__(self, region=None, language=None, **kwargs):
        super(MainMorda, self).__init__(language=language, region=region, **kwargs)


class YaruMorda(Morda):
    __metaclass__ = ABCMeta

    def __init__(self, **kwargs):
        super(YaruMorda, self).__init__(**kwargs)

    def get_url(self, env='production'):
        return '{}://{}ya.{}'.format(self.scheme,
                                     Morda._get_env_prefix(prefix=self.prefix, env=env),
                                     self.get_domain())

    def get_domain(self):
        return 'ru'

    def get_cookie_domain(self):
        return '.yandex.ru'


class HwMorda(Morda):
    __metaclass__ = ABCMeta

    def __init__(self, region=None, language=None, scheme='http', **kwargs):
        super(HwMorda, self).__init__(scheme=scheme, language=language, region=region, prefix='hw', **kwargs)

    def get_domain(self):
        return 'ru'


class ComMorda(MordaWithLanguage):
    __metaclass__ = ABCMeta

    def __init__(self, language=None, **kwargs):
        super(ComMorda, self).__init__(language=language, **kwargs)
        self.headers['No-Redirect'] = '1'

    def get_domain(self):
        return 'com'


class ComTrMorda(MordaWithRegion):
    __metaclass__ = ABCMeta

    def __init__(self, region=None, **kwargs):
        super(ComTrMorda, self).__init__(region=region, **kwargs)

    def get_domain(self):
        return 'com.tr'


class DesktopMain(MainMorda, DesktopMorda):
    def __init__(self, region=None, language=None, **kwargs):
        super(DesktopMain, self).__init__(name='d_main', morda_content='big',
                                          language=language, region=region, **kwargs)


class DesktopMainAll(DesktopMain):
    def __init__(self, region=None, language=None, **kwargs):
        super(DesktopMainAll, self).__init__(language=language, region=region, path='/all', **kwargs)
        self.name = 'd_main_all'


class Desktop404(DesktopMain):
    def __init__(self, region=None, language=None, **kwargs):
        super(Desktop404, self).__init__(language=language, region=region, path='/sl/blah', **kwargs)
        self.name = 'd_404'


class DesktopFamily(MordaWithLanguage, DesktopMorda, KubrMorda):
    def __init__(self, region=None, language=None, **kwargs):
        super(DesktopFamily, self).__init__(name='d_family', prefix='family', language=language, region=region,
                                            **kwargs)


class DesktopFirefox(MordaWithLanguage, DesktopMorda, KubrMorda, ComTrMorda):
    def __init__(self, domain, region=None, language=None, **kwargs):
        super(DesktopFirefox, self).__init__(name='d_firefox',
                                             prefix='firefox', language=language, region=region, **kwargs)
        self.domain = domain

    def get_domain(self):
        return self.domain


class TouchMain(MainMorda, TouchMorda):
    def __init__(self, region=None, language=None, **kwargs):
        super(TouchMain, self).__init__(name='t_main', morda_content='touch', language=language,
                                        region=region, cookies=dict(mda='0'), **kwargs)


class TouchMainWp(MainMorda, TouchWpMorda):
    def __init__(self, region=None, language=None, **kwargs):
        super(TouchMainWp, self).__init__(name='t_main_wp', language=language, region=region, params={'q': ''},
                                          **kwargs)


class TouchMainAll(TouchMain):
    def __init__(self, region=None, language=None, **kwargs):
        super(TouchMainAll, self).__init__(path='/all', language=language, region=region, **kwargs)
        self.name = 't_main_all'


class PdaMain(MainMorda, PdaMorda):
    def __init__(self, region=None, language=None, **kwargs):
        super(PdaMain, self).__init__(name='p_main', morda_content='mob', language=language,
                                      cookies=dict(mda='0'), region=region, **kwargs)


class PdaAll(PdaMain):
    def __init__(self, region=None, language=None, **kwargs):
        super(PdaAll, self).__init__(name='p_main_all', path='/all', language=language, region=region, **kwargs)


class TelMain(MainMorda, TelMorda):
    def __init__(self, region=None, language=None, **kwargs):
        super(TelMain, self).__init__(name='tel_main', language=language, region=region, **kwargs)


class DesktopYaru(YaruMorda, DesktopMorda):
    def __init__(self, **kwargs):
        super(DesktopYaru, self).__init__(name='d_yaru', morda_content='yaru', **kwargs)


class TouchYaru(YaruMorda, TouchMorda):
    def __init__(self, **kwargs):
        super(TouchYaru, self).__init__(name='t_yaru', morda_content='yaru', **kwargs)


class PdaYaru(YaruMorda, PdaMorda):
    def __init__(self, **kwargs):
        super(PdaYaru, self).__init__(name='p_yaru', **kwargs)


class DesktopCom(ComMorda, DesktopMorda):
    def __init__(self, language=None, **kwargs):
        super(DesktopCom, self).__init__(name='d_com', morda_content='com', language=language, **kwargs)


class DesktopCom404(ComMorda, DesktopMorda):
    def __init__(self, language=None, **kwargs):
        super(DesktopCom404, self).__init__(name='d_com_404', path='/sl/blah', language=language, **kwargs)


class TouchCom(ComMorda, TouchMorda):
    def __init__(self, language=None, **kwargs):
        super(TouchCom, self).__init__(name='t_com', morda_content='com', language=language, **kwargs)


class PdaCom(ComMorda, PdaMorda):
    def __init__(self, language=None, **kwargs):
        super(PdaCom, self).__init__(name='p_com', anguage=language, **kwargs)


class DesktopComTr(ComTrMorda, DesktopMorda):
    def __init__(self, region=None, **kwargs):
        super(DesktopComTr, self).__init__(name='d_comtr', morda_content='spok', region=region, **kwargs)


class DesktopComTrFoot(ComTrMorda, DesktopMorda):
    def __init__(self, club, region=None, **kwargs):
        super(DesktopComTrFoot, self).__init__(name='d_comtrfoot', path='/' + club,
                                               morda_content='comtrfoot', region=region, **kwargs)


class DesktopComTrAll(ComTrMorda, DesktopMorda):
    def __init__(self, region=None, **kwargs):
        super(DesktopComTrAll, self).__init__(name='d_comtr_all', morda_content='spok',
                                              path='/all', region=region, **kwargs)


class DesktopComTr404(ComTrMorda, DesktopMorda):
    def __init__(self, region=None, **kwargs):
        super(DesktopComTr404, self).__init__(name='d_comtr_404', region=region, **kwargs)


class TouchComTr(ComTrMorda, TouchMorda):
    def __init__(self, region=None, **kwargs):
        super(TouchComTr, self).__init__(name='t_comtr', morda_content='spok', region=region, **kwargs)


class PdaComTr(ComTrMorda, PdaMorda):
    def __init__(self, region=None, **kwargs):
        super(PdaComTr, self).__init__(name='p_comtr', morda_content='spok', region=region, **kwargs)
