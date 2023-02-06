# -*- coding: utf-8 -*-
# pylint: disable=import-error, unused-argument, too-many-locals, protected-access
import json
import os
from collections import defaultdict
from datetime import datetime
from unittest.mock import patch
import xml.etree.ElementTree as ET
from common.client.wms import WMSConnector
from freezegun import freeze_time
from odoo import exceptions
from odoo.tests import tagged
from odoo.tests.common import Form
from .test_common import TestVeluationCommon
from .test_orders import Fixtures
from odoo.addons.lavka.tests.utils import save_xlsx_report, get_stock_loc, read_json_data
import random


# pylint: disable=invalid-name,too-many-statements
@tagged('lavka', 'sale_price_list')
class TestSalePriceList(TestVeluationCommon):
    # pylint: disable=unused-variable, attribute-defined-outside-init
    def _create_sale_price(self, params):
        self.sale_price_list = self.env['sale_price_list.lavka'].create(params)
        return self.sale_price_list.id

    def _create_draft_sale_price(self, params):
        self.draft_sale_price_list = self.env['draft.sale_price_list.lavka'].create(params)
        return self.draft_sale_price_list.id

    def _create_lines(self, sale_price_list_id=None):
        if sale_price_list_id is None:
            sale_price_list_id = self.sale_price_list.id

        vals = []
        for i in range(10):
            vals.append(
                {
                    'sale_price_list_id': sale_price_list_id,
                    'product_id': self.products[i].id,
                    'store_price': random.randint(9, 100),
                    'markdown_price': random.randint(9, 100),
                },
            )

        self.env['sale_price_list.lavka.products'].create(vals)

    def test_create(self):
        self._create_sale_price({
            'title': 'Sale Price List',
            }
        )
        self._create_lines()
        self.assertEqual(len(self.sale_price_list.products_line), 10, 'Длина совпала')

    def test_change_status(self):
        self._create_sale_price({
            'title': 'Sale Price List',
        }
        )
        vals = []
        for i in range(2):
            vals.append(
                {
                    'sale_price_list_id': self.sale_price_list.id,
                    'product_id': self.products[i].id,
                    'store_price': 10,
                    'markdown_price': 10,
                },
            )
        self.env['sale_price_list.lavka.products'].create(vals)
        self._create_draft_sale_price({
            'title': 'Draft Sale Price List',
            'target_price_list_id': self.sale_price_list.id,
            'status': 'active',
        }
        )
        vals = []
        for i in range(3):
            vals.append(
                {
                    'draft_sale_price_list_id': self.draft_sale_price_list.id,
                    'product_id': self.products[i].id,
                    'store_price': 20,
                    'markdown_price': 15,
                },
            )

        self.draft_sale_price_list.button_ready()
        self.assertEqual(self.draft_sale_price_list.status, 'ready',
                         'статус ready')

    def test_update_mode(self):
        self._create_sale_price({
                'title': 'Sale Price List',
            }
        )
        vals = []
        for i in range(2):
            vals.append(
                {
                    'sale_price_list_id': self.sale_price_list.id,
                    'product_id': self.products[i].id,
                    'store_price': 10,
                    'markdown_price': 10,
                },
            )
        self.env['sale_price_list.lavka.products'].create(vals)
        self._create_draft_sale_price({
                'title': 'Draft Sale Price List',
                'target_price_list_id': self.sale_price_list.id,
                'status': 'processing',
        }
        )
        vals = []
        for i in range(3):
            vals.append(
                {
                    'draft_sale_price_list_id': self.draft_sale_price_list.id,
                    'product_id': self.products[i].id,
                    'store_price': 20,
                    'markdown_price': 15,
                },
            )

        self.env['draft.sale_price_list.lavka.products'].create(vals)

        self.draft_sale_price_list.make_from_drafts()
        self.assertEqual(
            len(self.sale_price_list.products_line),
            3,
            'Product add'
        )

        for line in self.sale_price_list.products_line:
            self.assertEqual(line.store_price, 20, 'Store price change')
            self.assertEqual(line.markdown_price, 15, 'Markdown price change')
