# -*- coding: utf-8 -*-

from passport.backend.social.common.chrono import now
from passport.backend.social.common.db.schemas import profile_table
from passport.backend.social.common.providers.Vkontakte import Vkontakte
from passport.backend.social.common.providers.Yandex import Yandex
from passport.backend.social.common.test.consts import (
    PROFILE_ID1,
    SIMPLE_USERID1,
    UID1,
    USERNAME1,
)
from passport.backend.social.common.test.test_case import (
    RequestTestCaseMixin,
    ResponseTestCaseMixin,
)
from passport.backend.social.proxy2.app import (
    create_app,
    prepare_interprocess_environment,
    prepare_intraprocess_environment,
)
from passport.backend.social.proxy2.test import TestCase


class TestRedirectToProfile(ResponseTestCaseMixin, RequestTestCaseMixin, TestCase):
    REQUEST_HTTP_METHOD = 'GET'
    REQUEST_URL = '/proxy2/redirect_to_profile'

    def test_request_to_provider_not_required__no_tokens(self):
        self._create_vk_profile()

        rv = self._make_request(
            query={
                'target': self._build_gpt(),
            },
        )

        self.assertEqual(rv.status_code, 307)
        self.assertEqual(rv.headers.get('Location'), self._build_vk_external_profile_link())

    def test_invalid_gpt(self):
        rv = self._make_request(
            query={
                'target': 'ololo',
            },
        )

        self._assert_unable_to_build_profile_link_response(rv)

    def test_profile_not_found(self):
        rv = self._make_request(
            query={
                'target': self._build_gpt(),
            },
        )

        self._assert_unable_to_build_profile_link_response(rv)

    def test_invalid_signature(self):
        self._create_vk_profile()

        rv = self._make_request(
            query={
                'target': self._build_gpt(signature='0'),
            },
        )

        self._assert_unable_to_build_profile_link_response(rv)

    def test_provider_not_have_profile_links(self):
        self._create_ya_profile()

        rv = self._make_request(
            query={
                'target': self._build_gpt(),
            },
        )

        self._assert_unable_to_build_profile_link_response(rv)

    def test_unknown_provider(self):
        self._create_unknown_provider_profile()

        rv = self._make_request(
            query={
                'target': self._build_gpt(),
            },
        )

        self._assert_unable_to_build_profile_link_response(rv)

    def _create_vk_profile(self):
        with self._fake_db.no_recording() as db:
            query = profile_table.insert().values(
                profile_id=PROFILE_ID1,
                uid=UID1,
                provider_id=Vkontakte.id,
                userid=SIMPLE_USERID1,
                username=USERNAME1,
                created=now(),
            )
            db.execute(query)

    def _create_ya_profile(self):
        with self._fake_db.no_recording() as db:
            query = profile_table.insert().values(
                profile_id=PROFILE_ID1,
                uid=UID1,
                provider_id=Yandex.id,
                userid=SIMPLE_USERID1,
                username=USERNAME1,
                created=now(),
            )
            db.execute(query)

    def _create_unknown_provider_profile(self):
        with self._fake_db.no_recording() as db:
            query = profile_table.insert().values(
                profile_id=PROFILE_ID1,
                uid=UID1,
                provider_id=100500,
                userid=SIMPLE_USERID1,
                username=USERNAME1,
                created=now(),
            )
            db.execute(query)

    def _build_vk_external_profile_link(self):
        return 'https://vk.com/id%s' % SIMPLE_USERID1

    def _build_app(self):
        prepare_interprocess_environment()
        prepare_intraprocess_environment()
        return create_app()

    def _build_gpt(self, signature=None):
        if signature is None:
            signature = '75da1715348c044ef31126401d4e5d8e'
        return '0.0.%s.%s' % (PROFILE_ID1, signature)

    def _assert_unable_to_build_profile_link_response(self, rv):
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.data, 'Unable to build profile link\n')

    def build_settings(self):
        settings = super(TestRedirectToProfile, self).build_settings()
        settings['social_config'].update(
            yandex_get_profile_url='https://login.yandex.ru/info',
            yandex_avatar_url_template='https://avatars.mds.yandex.net/get-yapic/%s/',
        )
        return settings
