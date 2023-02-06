import allure
from passport.backend.qa.autotests.base.allure import allure_setup
from passport.backend.qa.autotests.base.builders.proxied.passport_api import PassportApi
from passport.backend.qa.autotests.base.settings.common import PASSPORT_HOST
from passport.backend.qa.autotests.base.steps.registration_steps import register_portal_account
from passport.backend.qa.autotests.base.steps.tracks import delete_track
from passport.backend.qa.autotests.base.testcase import (
    BaseTestCase,
    limit_envs,
)


@limit_envs(intranet_testing=False, intranet_production=False, description='для ятима пока нет тестовых аккаунтов')
@allure_setup(
    feature='passport-api: /1/bundle/oauth/device_authorize/qr_code/info/',
    story='/1/bundle/oauth/device_authorize/qr_code/info/',
)
class PassportAuthTestCase(BaseTestCase):
    @allure.step
    def setUp(self):
        super(PassportAuthTestCase, self).setUp()
        self.default_headers = {
            'Ya-Client-Host': PASSPORT_HOST,
            'Ya-Client-User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Ya-Client-Cookie': '',
            'Ya-Consumer-Client-Ip': '46.175.31.223',
        }

    def assert_qr_code_info_is_valid(self, track_id, device_name):
        rv = PassportApi().get(
            path='/1/bundle/oauth/device_authorize/qr_code/info/',
            query_params={
                'track_id': track_id,
            },
            headers=self.default_headers,
        )
        self.assert_has_entries(rv, {'status': 'ok'})
        self.assert_has_entries(
            rv,
            {
                'browser': 'Firefox',
                'os_family': [
                    'Mac OS X Yosemite',
                    '10.10.5',
                ],
                'region_id': 1,
                'device_name': device_name,
            },
        )

    def test_info__after_multistep_start(self):
        with register_portal_account() as user:
            device_name = 'iPhone ({})'.format(user.login)
            rv = PassportApi().post(
                path='/1/bundle/auth/password/multi_step/start/',
                form_params={
                    'login': user.login,
                    'device_name': device_name,
                },
                headers=self.default_headers,
            )
            self.assert_has_entries(rv, {'status': 'ok'})
            self.assert_has_keys(rv, ['track_id'])
            track_id = rv['track_id']

            self.assert_qr_code_info_is_valid(track_id, device_name)
            delete_track(track_id)

    def test_info__after_password_submit(self):
        with register_portal_account() as user:
            device_name = 'iPhone ({})'.format(user.login)
            rv = PassportApi().post(
                path='/2/bundle/auth/password/submit/',
                form_params={
                    'login': user.login,
                    'device_name': device_name,
                    'with_code': 'true',
                },
                headers=self.default_headers,
            )
            self.assert_has_entries(rv, {'status': 'ok'})
            self.assert_has_keys(rv, ['track_id'])
            track_id = rv['track_id']
            self.assert_has_keys(rv, ['user_code', 'verification_url', 'expires_in'])

            self.assert_qr_code_info_is_valid(track_id, device_name)
            delete_track(track_id)
