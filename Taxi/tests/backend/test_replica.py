# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# pylint: disable=anomalous-backslash-in-string,misplaced-comparison-constant
from contextlib import closing
import logging

from odoo.tests.common import SavepointCase
from odoo.tests.common import tagged
from common.db import cursor_replica


_logger = logging.getLogger('REPLICA_TEST')



@tagged('lavka', 'replica')
class TestReplica(SavepointCase):

    def test_read_replica(self):

        with closing(cursor_replica()) as cr:
            wh_slave = self.env['stock.warehouse'].with_env(self.env(cr=cr)).search([],)

