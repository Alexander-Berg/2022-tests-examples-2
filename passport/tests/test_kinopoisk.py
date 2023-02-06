# -*- coding: utf-8 -*-

from passport.backend.social.common.providers.Kinopoisk import Kinopoisk
from passport.backend.social.common.test.test_case import TestCase


class TestKinopoisk(TestCase):
    def build_settings(self):
        settings = super(TestKinopoisk, self).build_settings()
        social_config = dict(kinopoisk_host='www.kinopoisk.ru')
        settings['social_config'].update(social_config)
        return settings

    def test_profile_links(self):
        self.assertEqual(Kinopoisk.profile_link(), [])
        self.assertEqual(
            Kinopoisk.profile_link('1110000012675389'),
            ['https://www.kinopoisk.ru/user/12675389/'],
        )
        self.assertEqual(Kinopoisk.profile_link('12675389'), [])
