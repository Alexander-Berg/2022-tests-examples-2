# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# pylint: disable=anomalous-backslash-in-string,misplaced-comparison-constant
import json
import logging
import os
from unittest.mock import patch

from odoo.tests.common import SavepointCase
from odoo.tests.common import tagged
from common.config import cfg
from odoo.addons.lavka.tests.utils import read_json_data
from .test_common import _logger, TestVeluationCommon
from odoo.addons.lavka.tests.utils import get_products_from_csv

# _logger = logging.getLogger('PRODUCT_TEST')

FIXTURE_PATH = 'product_test'
FIXTURES_PATH = 'common'

@tagged('lavka', 'purchase_assortment_matrix')
class TestBulkAssortmentTagsOperations(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.common_products_dict = get_products_from_csv(
            folder=FIXTURES_PATH,
            filename='products_import',
        )
        cls.products = cls.env['product.product'].create(cls.common_products_dict)

        tags_data = read_json_data(
            folder=FIXTURE_PATH,
            filename='tags_data'
        )

        cls.tag_ids = cls.env['product.tag'].create(tags_data)
        tags = {tag.name: tag for tag in cls.tag_ids}
        cls.dry_tag = tags['test_dry']
        cls.food_tag = tags['food']
        cls.assortment_tag = tags['test_assortment']
        cls.assortment_tag.update({
            'manual': True,
        })
        cls.not_assortment_tags = cls.tag_ids - cls.assortment_tag

        for i in cls.products:
            i.product_tag_ids = cls.tag_ids

    def test_bulk_change_assortment_tags(self):

        self.env['purchase.assortment'].action_open_assortment(True)
        assortments = self.env['purchase.assortment'].search([])

        # bulk delete test_assortment
        assortments.action_change_assortment_tags_continue(
            {'deactivate': self.assortment_tag}
        )
        for i in self.products:
            self.assertEqual(i.product_tag_ids, self.not_assortment_tags)

        # bulk add test_assortment
        assortments.action_change_assortment_tags_continue(
            {'activate': self.assortment_tag}
        )
        for i in self.products:
            self.assertEqual(i.product_tag_ids, self.tag_ids)
