# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.mda2.forms import (
    BuildContainerForm,
    UseContainerForm,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts


@with_settings_hosts()
class TestForms(unittest.TestCase):
    def test_build_container_form(self):
        invalid_params = [
            (
                {},
                ['process_uuid.empty', 'target_host.empty'],
            ),
            (
                {'process_uuid': '', 'target_host': ''},
                ['process_uuid.empty', 'target_host.empty'],
            ),
            (
                {'is_background': 'foo', 'process_uuid': 'bar', 'target_host': '-'},
                ['is_background.invalid', 'target_host.invalid'],
            ),
        ]

        valid_params = [
            (
                {'process_uuid': 'foo', 'target_host': 'my.yandex.ru'},
                {'is_background': False, 'process_uuid': 'foo', 'target_host': 'my.yandex.ru'},
            ),
            (
                {'is_background': 'true', 'process_uuid': 'foo', 'target_host': 'his.kinopoisk.ru'},
                {'is_background': True, 'process_uuid': 'foo', 'target_host': 'his.kinopoisk.ru'},
            ),
        ]

        check_form(BuildContainerForm(), invalid_params, valid_params, None)

    def test_use_container_form(self):
        invalid_params = [
            (
                {},
                ['process_uuid.empty', 'container.empty'],
            ),
            (
                {'process_uuid': '', 'container': ''},
                ['process_uuid.empty', 'container.empty'],
            ),
            (
                {'is_background': 'foo', 'process_uuid': 'bar', 'container': 'zar', 'retpath': 'abc'},
                ['is_background.invalid', 'retpath.invalid'],
            ),
            (
                {'process_uuid': 'foo', 'container': 'bar'},
                ['retpath.empty'],
            ),
        ]

        valid_params = [
            (
                {'process_uuid': 'foo', 'container': 'bar', 'retpath': 'https://kinopoisk.ru/ping'},
                {'is_background': False, 'process_uuid': 'foo', 'container': 'bar', 'retpath': 'https://kinopoisk.ru/ping'},
            ),
            (
                {'is_background': 'true', 'process_uuid': 'foo', 'container': 'bar'},
                {'is_background': True, 'process_uuid': 'foo', 'container': 'bar', 'retpath': None},
            ),
        ]

        check_form(UseContainerForm(), invalid_params, valid_params, None)
