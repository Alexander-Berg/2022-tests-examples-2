# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.social.forms import SocialThumbnailForm
from passport.backend.core.builders.social_api.faker.social_api import EXISTING_TASK_ID
from passport.backend.core.test.test_utils.utils import with_settings

from .base import SOCIAL_DEFAULT_SUBSCRIPTION


@with_settings(SOCIAL_DEFAULT_SUBSCRIPTION=SOCIAL_DEFAULT_SUBSCRIPTION)
class TestForms(unittest.TestCase):
    def test_get_thumbnail_form(self):
        invalid_params = [
            (
                {},
                [
                    'task_id.empty',
                    'avatar_size_x.empty',
                    'avatar_size_y.empty',
                ],
            ),
            (
                {
                    'task_id': 'ffdz',
                    'avatar_size_x': '12x',
                    'avatar_size_y': '',
                },
                [
                    'task_id.invalid',
                    'avatar_size_x.invalid',
                    'avatar_size_y.empty',
                ],
            ),
            (
                {
                    'task_id': 'ffff',
                    'avatar_size_x': '-1',
                    'avatar_size_y': '-1000',
                },
                [
                    'avatar_size_x.invalid',
                    'avatar_size_y.invalid',
                ],
            ),

        ]

        valid_params = [
            (
                {
                    'task_id': EXISTING_TASK_ID,
                    'avatar_size_x': '0',
                    'avatar_size_y': '70',
                },
                {
                    'task_id': EXISTING_TASK_ID,
                    'avatar_size_x': 0,
                    'avatar_size_y': 70,
                },
            ),
        ]

        check_form(SocialThumbnailForm(), invalid_params, valid_params, None)
