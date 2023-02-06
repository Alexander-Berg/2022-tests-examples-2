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

_logger = logging.getLogger('PRODUCT_TEST')

FIXTURE_PATH = 'product_test'


@tagged('lavka', 'products')
class TestCreateProduct(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestCreateProduct, cls).setUpClass()
        cls.locale = 'ru_RU'

        cls.products_template = read_json_data(
            folder=FIXTURE_PATH,
            filename='new_product_data_from_wms'
        )
        tags_data = read_json_data(
            folder=FIXTURE_PATH,
            filename='tags_data'
        )
        groups_data = read_json_data(
            folder=FIXTURE_PATH,
            filename='groups_data'
        )
        tags = {tag.name: tag for tag in cls.env['product.tag'].create(tags_data)}
        cls.mapped_groups = {group.wms_id: group for group in cls.env['product.group'].create(groups_data)}
        cls.freeze_tag = tags['test_freeze']
        cls.dry_tag = tags['test_dry']
        cls.food_tag = tags['food']
        cls.assortment_tag = tags['test_assortment']
        cls.mapped_tags = tags
        cls.real_parents = ['wms_id_4', 'wms_id_5']
        cls.virtual_parents = ['wms_id_2', 'wms_id_3']

        cls.update_fields = {
            # залетает товар, у которого родитель еще не создан
            0: {
                'product_kind': 'test_food',
                'parent_id': 'wms_id_5',
                'tags': [
                    # такого тега нет в базе, должен создасться
                    'test_freeze_2',
                    'test_freeze',
                ],
                'groups': [
                    'wms_id_0',
                    'wms_id_1',
                ],
                'nomenclature_type': 'product',
            },
            1: {
                'product_kind': 'test_food',
                'tags': [
                    # такого тега нет в базе, должен создасться
                    'test_freeze_2',
                    'test_freeze',
                ],
                'groups': ['wms_id_2'],
                'nomenclature_type': 'sample',
            },
            2: {
                'tags': [
                    'test_dry',
                    'test_assortment',
                ],
                # этот товар указан как виртуальный родитель у ДРУГИХ товаров
                # не должен прорастать как родитель в ВУДИ
                'virtual_product': True,
                'nomenclature_type': 'consumable',
            },
            3: {
                'tags': [
                    'test_assortment_2',
                ],
                'product_kind': 'nonfood',
                # этот товар указан как виртуальный родитель у ДРУГИХ товаров
                # не должен прорастать как родитель в ВУДИ
                'virtual_product': True
            },
            4: {
                'tags': [
                    'test_assortment_2',
                ],
                # У этого товара виртуальный родитель!
                'parent_id': 'wms_id_2',
            },
            5: {
                'tags': [
                    'test_assortment_2',
                ],
                # У этого товара виртуальный родитель!
                'parent_id': 'wms_id_3',
            },
            6: {
                'tags': [
                    'test_assortment_2',
                ],
                # нормальный родитель
                'parent_id': 'wms_id_4',
            },
            7: {
                'tags': [
                    # такого тега нет в вуди
                    'test_assortment_2',
                    'test_assortment',
                    'test_dry',
                    'test_freeze'
                ],
                # нормальный родитель
                'parent_id': 'wms_id_4',
                # такого тега нет в вуди
                'product_kind': 'rm'
            },
            8: {
                'tags': [
                    'test_assortment_2',
                    'test_assortment',
                    'test_dry',
                    'test_freeze'
                ],
                # нормальный родитель
                'parent_id': 'wms_id_4',
                'product_kind': 'NFchemicals',
            },
            9: {
                'tags': [
                    'test_assortment_2',
                    'test_assortment',
                    'test_dry',
                    'test_freeze'
                ],
                'parent_id': 'wms_id_4',
                'product_kind': 'nonfood',
                # не из нашей песочницы, не должен загрузиться
                'products_scope': json.dumps(['england']),
            }

        }
        cls.mapping_products_fields = cls.env['product.product'].mapping_products_fields

    def test_create_brand_new_products(self):

        wms_data = []
        for i in range(10):
            tmpl = self.products_template.copy()
            tmpl.update({
                'product_id': f'wms_id_{i}',
                'barcode': [f'barcode_{i}'],
                'external_id': f'default_code_{i}',
                'title': f'product_title_{i}',
                'long_title': f'product_long_title_{i}',
                'description': f'product_description_{i}',
                'products_scope': ['russia'],
                'images': [
                    f'http:\\127.0.0.0\\image_{i}.jpg'
                ],
            })
            additional_fields = self.update_fields.get(i)
            if additional_fields:
                tmpl.update(additional_fields)
            virt_parent = tmpl.get('virtual_product')
            if virt_parent:
                self.assertTrue(tmpl['product_id'] in self.virtual_parents)
            parent = tmpl.get('parent_id')
            if parent:
                self.assertTrue(parent in self.virtual_parents + self.real_parents, parent)
            wms_data.append(tmpl)

        with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
            cfg.set('localization.region', 'russia')
            get_wms_data_mock.return_value = wms_data, None
            result, to_process, existing_products = self.env['product.product'].import_from_wms_sync(test=True)
        self.assertEqual(len(existing_products), 0)
        # 9 из 10 (не дожно быть анлийского товара)
        self.assertEqual(len(to_process), 9)
        self.assertEqual(len(result), len(to_process))
        mapped_products = {i.wms_id: i for i in result}

        for i, fields in self.update_fields.items():
            wms_id = f'wms_id_{i}'
            if wms_id not in to_process.keys():
                continue
            _product = mapped_products[wms_id]
            _product_tags = {t.name: t for t in _product.product_tag_ids}
            _product_groups = {g.wms_id: g for g in _product.group_ids}
            for f_name, data in fields.items():
                if f_name == 'tags':
                    for tag_name in data:
                        _tag = _product_tags.get(tag_name)
                        self.assertEqual(_tag.name, tag_name)
                elif f_name == 'product_kind':
                    if data in ('rm', 'nonfood', 'cigarettes', 'NFchemicals'):
                        _tag = _product_tags.get('true')
                        self.assertEqual(_tag.name, 'true')
                    else:
                        # food
                        _tag = _product_tags.get(data)
                        self.assertIsNone(_tag)
                elif f_name == 'groups':
                    for group_id in data:
                        _group = _product_groups.get(group_id)
                        self.assertEqual(_group.wms_id, group_id)
                elif f_name == 'nomenclature_type':
                    self.assertEqual(_product['type'], self.env['product.product'].TYPE_WMS_WOODY[data])
                else:
                    odoo_f_name = self.mapping_products_fields[f_name]
                    val = _product[odoo_f_name]
                    if odoo_f_name == 'wms_parent':
                        # должны прорастать только реальные родители
                        odoo_parent = mapped_products[val]
                        self.assertFalse(odoo_parent.virtual_parent)
                    else:
                        self.assertEqual(val, data)

        for p in mapped_products.values():
            self.assertTrue(len(p.wms_parent) > 0)
            if p.product_parent and p.product_parent.wms_id != p.wms_id:
                self.assertTrue(p.product_parent.wms_id not in self.virtual_parents)


@tagged('lavka', 'products')
class TestUpdateProduct(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.locale = 'ru_RU'

        cls.products_template = read_json_data(
            folder=FIXTURE_PATH,
            filename='new_product_data_from_wms'
        )
        odoo_product_template = read_json_data(
            folder=FIXTURE_PATH,
            filename='old_product_data_from_wms'
        )

        tags_data = read_json_data(
            folder=FIXTURE_PATH,
            filename='tags_data'
        )
        tags = {tag.name: tag for tag in cls.env['product.tag'].create(tags_data)}
        cls.freeze_tag = tags['test_freeze']
        cls.dry_tag = tags['test_dry']
        cls.nonfood_tag = tags['nonfood']
        cls.food_tag = tags['food']
        cls.assortment_tag = tags['test_assortment']
        cls.mapped_tags = tags
        # меняем местами виртуальность
        # то что было не виртуальными, стало имим
        cls.real_parents = ['wms_id_2', 'wms_id_3']
        cls.virtual_parents = ['wms_id_4', 'wms_id_5']

        cls.odoo_update_fields = {
            # залетает товар, у которого родитель еще не создан
            0: {
                'wms_parent': False,
                'product_tag_ids': [(6, 0, [cls.freeze_tag.id])],
            },
            1: {
                'product_tag_ids': [(6, 0, [cls.freeze_tag.id])],
            },
            2: {
                'product_tag_ids': [(6, 0, [
                    cls.freeze_tag.id,
                    cls.food_tag.id,
                    cls.assortment_tag.id,
                    cls.dry_tag.id,
                ])],
                # этот товар указан как виртуальный родитель у ДРУГИХ товаров
                # не должен прорастать как родитель в ВУДИ
                'virtual_parent': True
            },
            3: {
                'product_tag_ids': [(6, 0, [
                    cls.freeze_tag.id,
                    cls.dry_tag.id,
                    cls.nonfood_tag.id,
                ])],
                # этот товар указан как виртуальный родитель у ДРУГИХ товаров
                # не должен прорастать как родитель в ВУДИ
                'virtual_parent': True
            },
            4: {
                'product_tag_ids': [(6, 0, [
                    cls.freeze_tag.id,
                    cls.assortment_tag.id,
                    cls.food_tag.id,
                ])],
                # У этого товара виртуальный родитель!
                'wms_parent': 'wms_id_2',
            },
            5: {
                'product_tag_ids': [(6, 0, [
                    cls.food_tag.id,
                    cls.assortment_tag.id,
                ])],
                # У этого товара виртуальный родитель!
                'wms_parent': 'wms_id_3',
            },
            6: {
                # нормальный родитель
                'wms_parent': 'wms_id_4',
            },
            7: {
                'product_tag_ids': [(6, 0, [
                    cls.assortment_tag.id,
                ])],
                # нормальный родитель
                'wms_parent': 'wms_id_4',
            },
            8: {
                'product_tag_ids': [(6, 0, [
                    cls.dry_tag.id,
                    cls.assortment_tag.id,
                    cls.food_tag.id,
                ])],
                # нормальный родитель
                'wms_parent': 'wms_id_5',
            },
            9: {
                'product_tag_ids': [(6, 0, [
                    cls.assortment_tag.id,
                ])],
                # нормальный родитель
                'wms_parent': 'wms_id_4',
            }

        }
        vals = []
        for i in range(10):
            tmpl = odoo_product_template.copy()
            tmpl.update({
                'wms_id': f'wms_id_{i}',
                'image_url': f'http:\\127.0.0.0\\image_{i}.jpg',
                'name': f'already_in_base_{i}',
                'barcode': '000000000_{i}',
                'default_code': f'default_code_{i}',
                'description_sale': f'product_long_title_{i}',
                'description': f'product_description_{i}',
            })

            additional_fields = cls.odoo_update_fields.get(i)
            if additional_fields:
                tmpl.update(additional_fields)
            vals.append(tmpl)
        cls.existing_products = cls.env['product.product'].create(vals)
        # запоминаем ассортиментные теги
        cls.assortment_tags_products = {}
        for p in cls.existing_products:
            for t in p.product_tag_ids:
                if t.type == 'assortment':
                    cls.assortment_tags_products[p.wms_id] = t

        cls.update_fields = {
            0: {
                'product_kind': 'nonfood',
                'parent_id': 'wms_id_5',
                'tags': [
                    # такого тега нет в базе, должен создасться
                    'test_freeze_2',
                    'test_freeze',
                ],
            },
            1: {
                'product_kind': 'nonfood',
                'parent_id': 'wms_id_2',
                'tags': [
                    # такого тега нет в базе, должен создасться
                    'test_freeze_2',
                    'test_freeze',
                ],
            },
            2: {
                'tags': [
                    'test_dry',
                    'test_assortment',
                ],
                'virtual_product': False,

            },
            3: {
                'tags': [
                    'test_assortment_2',
                ],
                'product_kind': 'nonfood',
                'virtual_product': False,
            },
            4: {
                'tags': [
                    'test_assortment_2',
                ],
                'virtual_product': True
            },
            5: {
                'tags': [
                    'test_assortment_2',
                ],
                'parent_id': 'wms_id_3',
                'virtual_product': True
            },
            6: {
                'tags': [
                    'test_assortment_2',
                ],
                'parent_id': 'wms_id_4',
            },
            7: {
                'tags': [
                    # такого тега нет в вуди
                    'test_assortment_2',
                    'test_assortment',
                    'test_dry',
                    'test_freeze'
                ],
                # нормальный родитель
                'parent_id': 'wms_id_4',
                # такого тега нет в вуди
                'product_kind': 'test_food_2'
            },
            8: {
                'tags': [
                    'test_assortment_2',
                    'test_assortment',
                    'test_dry',
                    'test_freeze'
                ],
                # нормальный родитель
                'parent_id': 'wms_id_4',
                'product_kind': 'test_food',
            },
            9: {
                'tags': [
                    'test_assortment_2',
                    'test_assortment',
                    'test_dry',
                    'test_freeze'
                ],
                'parent_id': 'wms_id_3',
                'product_kind': 'test_food',
            }

        }
        cls.mapping_products_fields = cls.env['product.product'].mapping_products_fields

    def test_update_products(self):

        wms_data = []
        for i in range(10):
            tmpl = self.products_template.copy()
            tmpl.update({
                'product_id': f'wms_id_{i}',
                'barcode': [f'barcode_{i}'],
                'external_id': f'default_code_{i}',
                'title': f'product_title_{i}',
                'long_title': f'product_long_title_{i}',
                'description': f'product_description_{i}',
                'products_scope': ['russia'],
                'images': [
                    f'http:\\127.0.0.0\\image_{i}.jpg'
                ],
            })
            additional_fields = self.update_fields.get(i)
            if additional_fields:
                tmpl.update(additional_fields)
            wms_data.append(tmpl)

        with patch('common.client.wms.WMSConnector.get_wms_data') as get_wms_data_mock:
            cfg.set('localization.region', 'russia')
            get_wms_data_mock.return_value = wms_data, None
            result, to_process, existing_products = self.env['product.product'].import_from_wms_sync(test=True)
        self.assertEqual(len(existing_products), 10)
        self.assertEqual(len(to_process), 10)
        self.assertEqual(len(result), len(to_process))

        for i, product in enumerate(result):
            # проверяем, что не затерли ассортиментные теги
            t = self.assortment_tags_products.get(product.wms_id)
            if t:
                self.assertTrue(t in product.product_tag_ids)

            additional_fields = self.update_fields.get(i)
            _product_tags = {t.name: t for t in product.product_tag_ids}
            # проверяем, что проапдейтили товары новыми значениями
            for f_name, data in additional_fields.items():
                if f_name == 'tags':
                    for tag_name in data:
                        _tag = _product_tags.get(tag_name)
                        self.assertEqual(_tag.name, tag_name)
                elif f_name == 'product_kind':
                    if data in ('rm', 'nonfood', 'cigarettes', 'NFchemicals'):
                        _tag = _product_tags.get('true')
                        self.assertEqual(_tag.name, 'true')
                    else:
                        # food
                        _tag = _product_tags.get(data)
                        self.assertIsNone(_tag)
                else:
                    odoo_f_name = self.mapping_products_fields[f_name]
                    val = product[odoo_f_name]
                    if odoo_f_name == 'wms_parent':
                        # должны прорастать только реальные родители
                        odoo_parent = product.product_parent
                        self.assertFalse(odoo_parent.virtual_parent)
                        self.assertEqual(odoo_parent.wms_id, val)

                    else:
                        self.assertEqual(val, data)
            # проверяем родителей
            self.assertTrue(len(product.wms_parent) > 0)
            # все родители, отличные от самомго себя должны быть не виртуальными
            # и быть новыми
            if product.wms_id != product.wms_parent:
                self.assertFalse(product.product_parent.virtual_parent)
                self.assertTrue(product.product_parent.wms_id in self.real_parents)
