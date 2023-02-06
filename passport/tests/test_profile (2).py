# -*- coding: utf-8 -*-

from contextlib import contextmanager
from datetime import datetime
import os
import unittest

import mock
from nose.tools import eq_
from passport.backend.core.test.test_utils import iterdiff
from passport.backend.library.configurator import Configurator
from passport.backend.profile import initialize_app
from passport.backend.profile.scripts.build_profile_daily import build_profile_daily
from passport.backend.profile.scripts.upload_profile_to_ydb import upload_profile_to_ydb
from passport.backend.profile.test.yt import YtTestWrapper
from passport.backend.profile.utils.helpers import to_date_str
from passport.backend.profile.utils.yt import get_yt
import yenv
from yt.wrapper import JsonFormat

from .profile_test_data import (
    BUILD_PROFILE_INPUT_TABLES,
    PROFILE_ROWS,
)


iter_eq = iterdiff(eq_)


class BaseProfileTestCase(unittest.TestCase):
    INPUT_TABLES = None

    def setUp(self):
        self.config = Configurator(
            'passport-profile',
            configs=[
                {'environment': yenv.type},
                'base.yaml',
                'secrets.yaml',
                'development.yaml',
                'logging.yaml',
            ]
        )
        initialize_app(config=self.config)
        self.yt_test = YtTestWrapper(get_yt(self.config), self.INPUT_TABLES)
        self.yt_test.start()

        self.patches = []
        for option in (
            'passport_log_dir',
            'passport_dataset_dir',
            'blackbox_log_dir',
            'blackbox_dataset_dir',
            'oauth_log_dir',
            'oauth_dataset_dir',
            'profile_dir',
        ):
            value = self.yt_test.wrap_path(self.config['yt'][option])
            patch = mock.patch.dict(self.config['yt'], {option: value}, clear=False)
            self.patches.append(patch)

        @contextmanager
        def exclusive_lock_mock(**kwargs):
            yield

        exclusively_patch = mock.patch(
            'passport.backend.profile.utils.yt.ExclusiveLock',
            exclusive_lock_mock,
        )
        self.patches.append(exclusively_patch)

        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()

        self.yt_test.stop()


class BuildProfileTestCase(BaseProfileTestCase):
    INPUT_TABLES = BUILD_PROFILE_INPUT_TABLES

    def test_build_profile_daily_ok(self):
        date = datetime(2016, 7, 10)
        build_profile_daily(
            config=self.config,
            target_date=date,
            force_rerun=False,
        )

        expected_path = os.path.join(self.config['yt']['profile_dir'], to_date_str(date))
        yt = get_yt(self.config)
        assert yt.exists(expected_path)
        result_rows = [row for row in yt.read_table(expected_path, format=JsonFormat(attributes={"json": False}))]
        iter_eq(result_rows, PROFILE_ROWS)

        upload_profile_to_ydb(
            config=self.config,
            target_date=date,
            force_rerun=False,
        )
