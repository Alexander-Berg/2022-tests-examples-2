# coding: utf-8

"""
Tests for Beta api
"""

import unittest
import mock

from sandbox.projects.common.betas.beta_api import BetaApi
from sandbox.projects.common.betas.yappy_api import YappyApi


class TestBetaApi(unittest.TestCase):
    def setUp(self):
        self.yappy = mock.Mock(YappyApi)

        self.beta_api = BetaApi(self.yappy)

    def test_beta_exists(self):
        self.yappy.beta_exists.return_value = False
        self.assertFalse(self.beta_api.beta_exists('my-beta'))

        self.yappy.beta_exists.return_value = True
        self.assertTrue(self.beta_api.beta_exists('my-beta'))

    def test_get_beta_info_yappy(self):
        self.yappy.beta_exists.return_value = True
        self.yappy.get_beta_info.return_value = 'yappy-beta-info'
        self.assertEqual('yappy-beta-info', self.beta_api.get_beta_info('my-beta'))
