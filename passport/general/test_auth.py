import allure
from hamcrest import (
    all_of,
    anything,
    assert_that,
    contains,
    has_entries,
    has_items,
    has_key,
    is_not,
)
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.builders.proxied.blackbox import Blackbox
from passport.backend.qa.autotests.base.builders.proxied.passport_api import PassportApi
from passport.backend.qa.autotests.base.settings.common import PASSPORT_HOST
from passport.backend.qa.autotests.base.steps.cookie_steps import (
    dump_cookies_to_header,
    get_cookies,
    parse_cookies,
)
from passport.backend.qa.autotests.base.steps.registration_steps import (
    register_portal_account,
    register_scholar_account,
)
from passport.backend.qa.autotests.base.test_env import test_env

from .base import BaseScholarTestCase


@allure_setup(
    feature='Пользование аккаунтом школьника',
    story='Вход в аккаунт школьника',
)
class AuthTestCase(BaseScholarTestCase):
    def test_ok(self):
        with register_scholar_account() as account:
            self.account = account
            self.auth()

            rv = self.sessionid()
            with allure.step('Проверка, что выписана действительная школьная сессия'):
                assert_that(
                    rv,
                    has_entries(
                        status=has_entries(value='VALID'),
                        users=has_items(
                            # Scholar user
                            has_entries(
                                auth=has_entries(is_scholar_session=True),
                                status=has_entries(value='VALID'),
                                uid=has_entries(value=str(self.account.uid)),
                            ),
                        ),
                    ),
                )

            assert 'lah' not in self.cookies

            rv = self.get_suggest()
            assert_that(
                rv,
                has_entries(cookies=anything()),
            )

            self.update_cookies(rv['cookies'])
            with allure.step('Проверка, что кука Lah пуста'):
                assert self.cookies['lah'].value == ''

    def test_auth_logout(self):
        with (
            register_portal_account() as portal_account,
            register_scholar_account() as scholar_account,
        ):
            self.update_cookies(get_cookies(portal_account, dump=False))

            self.account = scholar_account
            self.auth()

            rv = self.sessionid()
            with allure.step('Проверка, что в мультисессии есть сессии, и портальщика, и школьника'):
                assert_that(
                    rv,
                    has_entries(
                        status=has_entries(value='VALID'),
                        users=has_items(
                            # Portal user
                            has_entries(
                                auth=is_not(has_entries(is_scholar_session=True)),
                                status=has_entries(value='VALID'),
                                uid=has_entries(value=str(portal_account.uid)),
                            ),
                            # Scholar user
                            has_entries(
                                auth=has_entries(is_scholar_session=True),
                                status=has_entries(value='VALID'),
                                uid=has_entries(value=str(scholar_account.uid)),
                            ),
                        ),
                    ),
                )

            rv = self.auth_logout()
            assert_that(
                rv,
                has_entries(
                    accounts=contains(has_entries(uid=portal_account.uid)),
                    cookies=anything(),
                    logged_out_uids=[self.account.uid],
                    status='ok',
                ),
            )

            self.update_cookies(rv['cookies'])

            rv = self.sessionid()
            with allure.step('Проверка, что в мультисессии осталась только сессия портальщика'):
                assert_that(
                    rv,
                    has_entries(
                        status=has_entries(value='VALID'),
                        users=has_items(
                            # Portal user
                            has_entries(
                                status=has_entries(value='VALID'),
                                uid=has_entries(value=str(portal_account.uid)),
                            ),
                        ),
                    ),
                )

    def test_account_logout(self):
        with register_scholar_account() as account:
            self.account = account
            self.auth()

            rv = self.account_logout()
            assert_that(
                rv,
                all_of(
                    has_entries(
                        cookies=anything(),
                        logged_out_uids=[self.account.uid],
                        status='ok',
                    ),
                    is_not(has_key('accounts')),
                ),
            )

            self.update_cookies(rv['cookies'])
            with allure.step('Проверка, что сессия школьника стёрлась'):
                assert self.cookies['Session_id'].value == ''

    @allure.step('Вход в аккаунт школьника')
    def auth(self):
        rv = self.start()
        assert_that(
            rv,
            has_entries(
                auth_methods=has_items('password'),
                can_authorize=True,
                status='ok',
                track_id=anything(),
            ),
        )
        self.track_id = rv['track_id']

        rv = self.commit_password()
        assert_that(
            rv,
            all_of(
                has_entries(status='ok'),
                is_not(has_key('state')),
            ),
        )

        rv = self.session()
        assert_that(
            rv,
            has_entries(
                cookies=anything(),
                status='ok',
            ),
        )

        self.update_cookies(rv['cookies'])
        assert_that(
            self.cookies,
            has_entries(
                sessguard=anything(),
                Session_id=anything(),
            ),
        )

    def start(self):
        return PassportApi().post(
            form_params=dict(
                allow_scholar='1',
                login=self.account.login,
            ),
            headers=self.headers,
            path='/1/bundle/auth/password/multi_step/start/',
        )

    @allure.step('Ввод пароля')
    def commit_password(self):
        return PassportApi().post(
            form_params=dict(
                password=self.account.password,
                track_id=self.track_id,
            ),
            headers=self.headers,
            path='/1/bundle/auth/password/multi_step/commit_password/',
        )

    @allure.step('Обмен авторизационного трека на сессию')
    def session(self):
        return PassportApi().post(
            form_params=dict(
                track_id=self.track_id,
            ),
            headers=self.headers,
            path='/1/bundle/session/',
        )

    @allure.step('Обмен sessionid на информацию о сессии')
    def sessionid(self):
        query_params = dict(
            allow_scholar='1',
            format='json',
            host=PASSPORT_HOST,
            method='sessionid',
            multisession='1',
            sessionid=self.cookies['Session_id'].value,
            userip=test_env.user_ip,
        )
        if self.cookies.get('sessguard'):
            query_params.update(sessguard=self.cookies['sessguard'].value)
        return Blackbox().get(path='/blackbox', query_params=query_params)

    def get_suggest(self):
        return PassportApi().get(
            headers=self.headers,
            path='/1/bundle/auth/suggest/',
        )

    def update_cookies(self, cookie_list):
        if isinstance(cookie_list, str):
            cookie_list = [cookie_list]

        if self.cookies is None:
            self.cookies = parse_cookies(cookie_list)
        else:
            for cookie in cookie_list:
                self.cookies.load(cookie)

    def auth_logout(self):
        return PassportApi().post(
            form_params=dict(
                uid=str(self.account.uid),
            ),
            headers=self.headers,
            path='/1/bundle/auth/logout/',
        )

    def account_logout(self):
        rv = self.sessionid()
        assert_that(rv, has_entries(connection_id=anything()))

        return PassportApi().post(
            form_params=dict(
                ci=rv['connection_id'],
            ),
            headers=self.headers,
            path='/1/bundle/account/logout/',
        )

    @property
    def headers(self):
        return {
            'Ya-Client-Cookie': dump_cookies_to_header(self.cookies) if self.cookies else '',
            'Ya-Client-Host': PASSPORT_HOST,
            'Ya-Client-User-Agent': test_env.user_agent,
            'Ya-Consumer-Client-Ip': test_env.user_ip,
        }
