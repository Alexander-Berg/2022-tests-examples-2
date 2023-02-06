# -*- coding: utf-8 -*-
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings_hosts,
)
from passport.backend.core.turboapp_partners import (
    get_partner_id_by_host,
    get_partner_id_by_url,
    is_psuid_allowed,
)
from passport.backend.core.turboapp_partners.schemas import (
    allowed_hosts_table as aht,
    allowed_urls_table as aut,
)
from passport.backend.core.ydb.declarative import select
from passport.backend.core.ydb.declarative.elements import and_
from passport.backend.core.ydb.exceptions import YdbTemporaryError
from passport.backend.core.ydb.faker.stubs import FakeResultSet
from passport.backend.core.ydb.faker.ydb import FakeYdb
import passport.backend.core.ydb_client as ydb


TEST_PARTNER_ID = 'p1'
TEST_HOST = 'gmail.ru'
TEST_URL = 'https://gmail.ru/mail'


@with_settings_hosts(
    YDB_TURBOAPP_PARTNERS_DATABASE='/turboapp_partners',
    YDB_TURBOAPP_PARTNERS_ENABLED=True,
    YDB_RETRIES=2,
)
class TurboappPartnersTestCase(PassportTestCase):
    def setUp(self):
        super(TurboappPartnersTestCase, self).setUp()

        self.fake_ydb = FakeYdb()

        self.__patches = [
            self.fake_ydb,
        ]

        for patch in self.__patches:
            patch.start()

    def tearDown(self):
        for patch in reversed(self.__patches):
            patch.stop()
        super(TurboappPartnersTestCase, self).tearDown()

    def build_host_row(self, host, partner_id, allow_psuid=False):
        return dict(
            host=host,
            partner_id=partner_id,
            allow_psuid=allow_psuid,
        )

    def build_url_row(self, url, partner_id):
        return dict(
            url=url,
            partner_id=partner_id,
        )

    def build_host_query(self, host):
        return select(aht, aht.c.host == host).compile()

    def build_url_query(self, url):
        return select(aut, aut.c.url == url).compile()

    def build_psuid_query(self, host):
        return select(aht, and_(aht.c.host == host, aht.c.allow_psuid)).compile()

    def test_get_partner_id_by_host__ok(self):
        self.fake_ydb.set_execute_return_value(
            [FakeResultSet([
                self.build_host_row(TEST_HOST, TEST_PARTNER_ID),
            ])],
        )

        assert get_partner_id_by_host(TEST_HOST) == TEST_PARTNER_ID

        self.fake_ydb.assert_queries_executed(
            [
                self.build_host_query(TEST_HOST),
            ],
        )

    def test_get_partner_id_by_host__not_found(self):
        self.fake_ydb.set_execute_return_value(
            [FakeResultSet([])],
        )

        assert get_partner_id_by_host(TEST_HOST) is None

        self.fake_ydb.assert_queries_executed(
            [
                self.build_host_query(TEST_HOST),
            ],
        )

    def test_get_partner_id_by_url__ok(self):
        self.fake_ydb.set_execute_return_value(
            [FakeResultSet([
                self.build_url_row(TEST_URL, TEST_PARTNER_ID),
            ])],
        )

        assert get_partner_id_by_url(TEST_URL) == TEST_PARTNER_ID

        self.fake_ydb.assert_queries_executed(
            [
                self.build_url_query(TEST_URL),
            ],
        )

    def test_get_partner_id_by_url__not_found(self):
        self.fake_ydb.set_execute_return_value(
            [FakeResultSet([])],
        )

        assert get_partner_id_by_url(TEST_URL) is None

        self.fake_ydb.assert_queries_executed(
            [
                self.build_url_query(TEST_URL),
            ],
        )

    def test_allow_psuid__ok(self):
        self.fake_ydb.set_execute_return_value(
            [FakeResultSet([
                self.build_host_row(TEST_HOST, TEST_PARTNER_ID, True),
            ])],
        )

        assert is_psuid_allowed(TEST_HOST)

        self.fake_ydb.assert_queries_executed(
            [
                self.build_psuid_query(TEST_HOST),
            ],
        )

    def test_allow_psuid__not_found(self):
        self.fake_ydb.set_execute_return_value(
            [FakeResultSet([])],
        )

        assert not is_psuid_allowed(TEST_HOST)

        self.fake_ydb.assert_queries_executed(
            [
                self.build_psuid_query(TEST_HOST),
            ],
        )

    def test_ydb_timeout(self):
        self.fake_ydb.set_execute_side_effect(ydb.Timeout('timeout'))

        with self.assertRaises(YdbTemporaryError):
            get_partner_id_by_host(TEST_HOST)

        self.fake_ydb.assert_queries_executed(
            [
                self.build_host_query(TEST_HOST),
            ],
        )
