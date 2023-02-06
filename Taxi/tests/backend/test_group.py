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

_logger = logging.getLogger('GROUP_TEST')

FIXTURE_PATH = 'group_test'


@tagged('lavka', 'product_groups')
class TestCreateGroup(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestCreateGroup, cls).setUpClass()
        cls.locale = 'ru_RU'

        cls.groups_template = read_json_data(
            folder=FIXTURE_PATH,
            filename='new_group_data_from_wms'
        )
        cls.update_fields = {
            # залетает товар, у которого родитель еще не создан
            0: {
                'parent_group_id': 'wms_id_8',
            },
            1: {
                # нормальный родитель
                'parent_group_id': 'wms_id_2',
            },
            3: {
                # нормальный родитель второго порядка
                'parent_group_id': 'wms_id_0',
            },
            4: {
                'products_scope': json.dumps(['england']),
            }

        }
        cls.mapping_groups_fields = cls.env['product.group'].mapping_groups_fields

    def test_create_brand_new_groups(self):

        wms_data = []
        for i in range(5):
            tmpl = self.groups_template.copy()
            tmpl.update({
                'group_id': f'wms_id_{i}',
                'external_id': f'default_code_{i}',
                'name': f'group_name_{i}',
                'description': f'group_description_{i}',
                'products_scope': ['russia'],
            })
            additional_fields = self.update_fields.get(i)
            if additional_fields:
                tmpl.update(additional_fields)
            wms_data.append(tmpl)

        with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
            cfg.set('localization.region', 'russia')
            get_wms_data_mock.return_value = wms_data, None
            result, to_process, existing_groups = self.env['product.group'].import_from_wms_sync(test=True)
        self.assertEqual(len(existing_groups), 0)
        # 4 из 5 (не дожно быть анлийского товара)
        self.assertEqual(len(to_process), 4)
        # в result должен создасться один дополнительный пустой родитель с wms_id_8
        self.assertEqual(len(result), len(to_process) + 1)
        mapped_groups = {i.wms_id: i for i in result}

        for i, fields in self.update_fields.items():
            wms_id = f'wms_id_{i}'
            if wms_id not in to_process.keys():
                continue
            _group = mapped_groups[wms_id]
            for f_name, data in fields.items():
                odoo_f_name = self.mapping_groups_fields[f_name]
                val = _group[odoo_f_name]
                self.assertEqual(val, data)
        #  проверим, что пустой родитель обновится при следующих импортах
        new_parent_group = self.groups_template.copy()
        update_fields = {
            'group_id': f'wms_id_8',
            'external_id': f'default_code_8',
            'name': f'group_name_8',
            'description': f'group_description_8',
            'products_scope': ['russia'],
        }
        new_parent_group.update(update_fields)
        with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
            get_wms_data_mock.return_value = [new_parent_group], None
            result, to_process, existing_groups = self.env['product.group'].import_from_wms_sync(test=True)
        # проверим, что родитель второй раз не создается, а только обновляет поля
        self.assertEqual(self.env['product.group'].search([], count=True), 5)
        self.assertEqual(mapped_groups['wms_id_8'], result)
        self.assertEqual(mapped_groups['wms_id_0'].parent_id, result)
        update_fields.pop('products_scope')
        for f_name, data in update_fields.items():
            odoo_f_name = self.mapping_groups_fields[f_name]
            val = result[odoo_f_name]
            self.assertEqual(val, data)

@tagged('lavka', 'product_groups')
class TestUpdateGroup(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.locale = 'ru_RU'

        cls.groups_template = read_json_data(
            folder=FIXTURE_PATH,
            filename='new_group_data_from_wms'
        )
        odoo_group_template = read_json_data(
            folder=FIXTURE_PATH,
            filename='old_group_data_from_wms'
        )

        cls.odoo_update_fields = {
            # залетает товар, у которого родитель еще не создан
            0: {
                'wms_parent_id': 'wms_id_8',
            },
            1: {
                # нормальный родитель
                'wms_parent_id': 'wms_id_2',
            },
            3: {
                # нормальный родитель второго порядка
                'wms_parent_id': 'wms_id_0',
            },
        }
        vals = []
        for i in range(5):
            tmpl = odoo_group_template.copy()
            tmpl.update({
                'wms_id': f'wms_id_{i}',
                'default_code': f'default_code_{i}',
                'name': f'group_name_{i}',
                'description': f'group_description_{i}',
            })

            additional_fields = cls.odoo_update_fields.get(i)
            if additional_fields:
                tmpl.update(additional_fields)
            vals.append(tmpl)
        cls.existing_groups = cls.env['product.group'].create(vals)

        cls.update_fields = {
            0: {
                'description': 'new_description_0',
                'parent_group_id': 'wms_id_10',
            },
            1: {
                'name': 'new_name_1',
            },
            2: {
                'parent_group_id': 'wms_id_0',
            },
            3: {
                'external_id': "new_default_code_3",
            },
            4: {
                'external_id': "new_default_code_4",
                'products_scope': json.dumps(['england']),
            }
        }
        cls.mapping_groups_fields = cls.env['product.group'].mapping_groups_fields

    def test_update_products(self):

        wms_data = []
        for i in range(5):
            tmpl = self.groups_template.copy()
            tmpl.update({
                'group_id': f'wms_id_{i}',
                'external_id': f'default_code_{i}',
                'name': f'group_name_{i}',
                'description': f'group_description_{i}',
                'products_scope': ['russia'],
            })
            additional_fields = self.update_fields.get(i)
            if additional_fields:
                tmpl.update(additional_fields)
            wms_data.append(tmpl)

        with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
            cfg.set('localization.region', 'russia')
            get_wms_data_mock.return_value = wms_data, None
            result, to_process, existing_groups = self.env['product.group'].import_from_wms_sync(test=True)
        # 4 из 5 (не дожно быть анлийского товара)
        self.assertEqual(len(existing_groups), 4)
        self.assertEqual(len(to_process), 4)
        # в result должен создасться один дополнительный пустой родитель с wms_id_10
        self.assertEqual(len(result), len(to_process) + 1)

        for i, data in self.update_fields.items():
            _group = self.env['product.group'].search([('wms_id', '=', f'wms_id_{i}')])
            for field, val in data.items():
                if not field == 'products_scope':
                    odoo_field = self.mapping_groups_fields[field]
                    _field = getattr(_group, odoo_field)
                    # 4ая группа не должна обновиться из-за региона в новых данных
                    if i == 4:
                        self.assertNotEqual(_field, val)
                    else:
                        self.assertEqual(_field, val)
            # проверим новых родителей
            if 'parent_group_id' in data.keys():
                _parent = self.env['product.group'].search([('wms_id', '=', data['parent_group_id'])])
                self.assertEqual(_group.parent_id, _parent)
