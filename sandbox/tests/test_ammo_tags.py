# coding: utf-8
from __future__ import unicode_literals, absolute_import, division, print_function

import unittest

from sandbox.projects.rasp.utils.ammo_tags import TagBuilder


class TestAmmoTags(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestAmmoTags, self).__init__(*args, **kwargs)
        self.builder = TagBuilder()

    def test_cut_web_method(self):
        assert self.builder.build_by_yt_log('/v3/web/method/?par1=qwe') == '/v3/web/method'

    def test_del_directions(self):
        assert self.builder.build_by_yt_log('/v3/web/from--to-direction/method/') == '/v3/web/_/method'

    def test_del_numbers(self):
        assert self.builder.build_by_yt_log('/v3/web/12345/method/') == '/v3/web/_/method'
        assert self.builder.build_by_yt_log('/v3/city/123/info') == '/v3/city/_/info'

    def test_del_thread_uids(self):
        assert self.builder.build_by_yt_log('/v3/thread/025V_1_2') == '/v3/thread/_'
        assert self.builder.build_by_yt_log('/v3/thread/T_61_12_1234567_8') == '/v3/thread/_'

    def test_del_not_url_symbols(self):
        assert self.builder.build_by_yt_log('/v3/cyrillic/cyr%3A%3B') == '/v3/cyrillic/_'

    def test_del_city_identity(self):
        assert self.builder.build_by_yt_log('/v3/from/c5/to/c213') == '/v3/from/_/to/_'

    def test_keep_first_after_version(self):
        assert self.builder.build_by_yt_log('/v3/method123/345') == '/v3/method123/_'

    def test_replace_language(self):
        assert self.builder.build_by_yt_log('/ru/method/345') == '/_/method/_'

    def test_del_settlement_slugs(self):
        assert self.builder.build_by_yt_log('/v3/settlement/moscow/stations') == '/v3/settlement/_/stations'
        assert self.builder.build_by_yt_log('/v3/settlement/omsk/transport-popular-directions') == '/v3/settlement/_/transport-popular-directions'  # noqa

    def test_keep_status_pages(self):
        assert self.builder.build_by_yt_log('/500.htm') == '/500.htm'
