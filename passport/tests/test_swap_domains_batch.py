# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    assert_raises,
    raises,
)
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.db.schemas import (
    domains_events_table as det,
    pdd_domains_table as pdt,
)
from passport.backend.core.differ import diff
from passport.backend.core.models.domain import Domain
from passport.backend.core.models.swap_domains_batch import SwapDomainsBatch
from passport.backend.core.serializers.domain import EVENT_NAME_TO_TYPE
from passport.backend.core.serializers.swap_domains_batch import SwapDomainsBatchSerializer
from passport.backend.core.test.time_utils.time_utils import DatetimeNow


TEST_MASTER_ID = 1
TEST_MASTER_DOMAIN = u'мастер.пдд.ру'
TEST_MASTER_DOMAIN_NORMALIZED = TEST_MASTER_DOMAIN.encode('idna')
TEST_ALIAS_ID = 451
TEST_ALIAS_DOMAIN = u'слейв.пдд.ру'
TEST_ALIAS_DOMAIN_NORMALIZED = TEST_ALIAS_DOMAIN.encode('idna')


class TestCreateSwapDomainsBatch(unittest.TestCase):
    def setUp(self):
        self.alias_data = {
            'domid': str(TEST_ALIAS_ID),
            'domain': TEST_ALIAS_DOMAIN,
            'master_domain_id': str(TEST_MASTER_ID),
            'options': '{"can_users_change_password": 1}',
            'ts': DatetimeNow(),
        }
        self.domain_data = {
            'domid': str(TEST_MASTER_ID),
            'admin': '2',
            'mx': '1',
            'default_uid': '1',
            'domain': TEST_MASTER_DOMAIN,
            'domain_ena': '1',
            'born_date': '2015-01-21 12:16:31',
            'options': '{"can_users_change_password": 1}',
            'slaves': TEST_ALIAS_DOMAIN,
        }

    @raises(ValueError)
    def test_master_domain_missing(self):
        batch = SwapDomainsBatch()
        SwapDomainsBatchSerializer().serialize(None, batch, diff(None, batch))

    def test_alias_missing(self):
        batch = SwapDomainsBatch()
        batch.master_domain = Domain().parse(self.domain_data)
        with assert_raises(ValueError):
            SwapDomainsBatchSerializer().serialize(None, batch, diff(None, batch))

    def test_alias_not_alias(self):
        batch = SwapDomainsBatch()
        del self.domain_data['slaves']
        batch.alias = Domain().parse(self.alias_data)
        batch.master_domain = Domain().parse(self.domain_data)
        with assert_raises(ValueError):
            SwapDomainsBatchSerializer().serialize(None, batch, diff(None, batch))

    def test_ok(self):
        batch = SwapDomainsBatch()
        batch.alias = Domain().parse(self.alias_data)
        batch.master_domain = Domain().parse(self.domain_data)

        queries = SwapDomainsBatchSerializer().serialize(None, batch, diff(None, batch))
        eq_eav_queries(
            queries,
            [
                'BEGIN',
                pdt.update().values(
                    name=b'##%s##' % TEST_ALIAS_DOMAIN_NORMALIZED,
                ).where(pdt.c.domain_id == TEST_ALIAS_ID),
                pdt.update().values(
                    name=TEST_ALIAS_DOMAIN_NORMALIZED,
                ).where(pdt.c.domain_id == TEST_MASTER_ID),
                pdt.update().values(
                    name=TEST_MASTER_DOMAIN_NORMALIZED,
                ).where(pdt.c.domain_id == TEST_ALIAS_ID),
                det.insert().values({
                    'domain_id': TEST_MASTER_ID,
                    'type': EVENT_NAME_TO_TYPE['swap'],
                    'ts': DatetimeNow(),
                    'meta': str(TEST_ALIAS_ID).encode('utf8'),
                }),
                det.insert().values({
                    'domain_id': TEST_ALIAS_ID,
                    'type': EVENT_NAME_TO_TYPE['update'],
                    'ts': DatetimeNow(),
                }),
                'COMMIT',
            ],
        )

    @raises(ValueError)
    def test_update_forbidden(self):
        batch = SwapDomainsBatch()
        SwapDomainsBatchSerializer().serialize(batch, batch, diff(batch, batch))

    @raises(ValueError)
    def test_delete_forbidden(self):
        batch = SwapDomainsBatch()
        SwapDomainsBatchSerializer().serialize(batch, None, diff(batch, None))
