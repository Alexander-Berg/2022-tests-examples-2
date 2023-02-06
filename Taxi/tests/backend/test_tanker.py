import hashlib
import logging
import re
from odoo.tests.common import SingleTransactionCase
from odoo.tests.common import tagged
from common.config import cfg

_logger = logging.getLogger(__name__)


@tagged('lavka', 'trn', 'tanker_integration')
class TestTankerTranslations(SingleTransactionCase):

    def setUp(self):
        super().setUp()
        self.locale = 'ru_RU'
        self.wms_ids = ['wms_id_00', 'wms_id_11']
        self.trn_list = [
            "Voulez-vous coucher avec moi se soir?",
            "okay, it's Hebrew",
            "ENGLAND FOR GENTLEMEN!",
            "FRANCE IS A GREAT FOR MAROCCANS!",
            "Hava nagila ve-nismeḥa",
            "KALINKA-MALINKA"
        ]

        self.tanker_data = {
            "export_info": {
                "request": {
                    "keyset-id": "production_products",
                    "language": "en,fr,he",
                    "project-id": "lavka-ma"
                },
                "name": "lavka-ma",
                "branch": "master"
            },
            "keysets": {
                "production_products": {
                    "keys": {
                        f"{self.wms_ids[0]}_title": {
                            "info": {
                                "context": "",
                                "is_plural": False,
                                "references": ""
                            },
                            "translations": {
                                "en": {
                                    "status": "requires_translation",
                                    "translator_comment": "",
                                    "author": "robot-emelya",
                                    "change_date": "11:49:36 15.04.2021",
                                    "form": "ENGLAND FOR GENTLEMEN!"
                                },
                                "fr": {
                                    "status": "requires_translation",
                                    "translator_comment": "",
                                    "author": "robot-emelya",
                                    "change_date": "11:49:36 15.04.2021",
                                    "form": "FRANCE IS A GREAT FOR MAROCCANS!"
                                },
                                "he": {
                                    "status": "requires_translation",
                                    "translator_comment": "",
                                    "author": "robot-emelya",
                                    "change_date": "11:49:36 15.04.2021",
                                    "form": "Hava nagila ve-nismeḥa"
                                },
                                "ru": {
                                    "status": "requires_translation",
                                    "translator_comment": "",
                                    "author": "robot-emelya",
                                    "change_date": "11:49:36 15.04.2021",
                                    "form": "KALINKA-MALINKA"
                                }

                            }
                        },
                        f"{self.wms_ids[1]}_title": {
                            "info": {
                                "context": "",
                                "is_plural": False,
                                "references": ""
                            },
                            "translations": {
                                "fr": {
                                    "status": "requires_translation",
                                    "translator_comment": "",
                                    "author": "robot-emelya",
                                    "change_date": "11:49:36 15.04.2021",
                                    "form": "Voulez-vous coucher avec moi se soir?"
                                },
                                "he": {
                                    "status": "requires_translation",
                                    "translator_comment": "",
                                    "author": "robot-emelya",
                                    "change_date": "11:49:36 15.04.2021",
                                    "form": "okay, it is Hebrew"
                                },
                            }
                        },
                    }
                }
            }
        }

        self.tanker_data_updt = {
            "export_info": {
                "request": {
                    "keyset-id": "production_products",
                    "language": "en,fr,he",
                    "project-id": "lavka-ma"
                },
                "name": "lavka-ma",
                "branch": "master"
            },
            "keysets": {
                "production_products": {
                    "keys": {
                        f"{self.wms_ids[0]}_title": {
                            "info": {
                                "context": "",
                                "is_plural": False,
                                "references": ""
                            },
                            "translations": {
                                "en": {
                                    "status": "requires_translation",
                                    "translator_comment": "",
                                    "author": "robot-emelya",
                                    "change_date": "11:49:36 15.04.2021",
                                    "form": "ENGLAND FOR GENTLEMEN! AND INDIAN PEOPLE!"
                                },
                                "fr": {
                                    "status": "requires_translation",
                                    "translator_comment": "",
                                    "author": "robot-emelya",
                                    "change_date": "11:49:36 15.04.2021",
                                    "form": "FRANCE IS A GREAT FOR MAROCCANS! AND ALGERIANS!"
                                },
                                "he": {
                                    "status": "requires_translation",
                                    "translator_comment": "",
                                    "author": "robot-emelya",
                                    "change_date": "11:49:36 15.04.2021",
                                    "form": "Hava nagila ve-nismeḥa"
                                },
                                "ru": {
                                    "status": "requires_translation",
                                    "translator_comment": "",
                                    "author": "robot-emelya",
                                    "change_date": "11:49:36 15.04.2021",
                                    "form": "KALINKA-MALINKA"
                                }

                            }
                        },
                    }
                }
            }
        }

        self.data_product_0 = {
            'wms_id': self.wms_ids[0],
            'image_url': 'http:\\127.0.0.0\image.jpg',
            'name': 'title_00',
            'barcode': '123456789123',
            'default_code': 'code_00',
            'categ_id': 1,
            'type': 'product',
            'description': 'description_0',
            'description_sale': 'long_title_0'}

        self.data_product_1_old = {
            'wms_id': self.wms_ids[1],
            'image_url': 'http:\\127.0.0.0\image1.jpg',
            'barcode': '123456789124',
            'default_code': 'code_11',
            'name': 'title_1_already_in_base',
            'categ_id': 1,
            'type': 'product',
            'description': 'description_1',
            'description_sale': 'long_title_1'}

        self.product = self.env['product.product']

        self.product_0 = self.product.search([('wms_id','=', self.wms_ids[0])]) \
                         or self.product.create(self.data_product_0)
        self.product_1 = self.product.search([('wms_id','=', self.wms_ids[1])]) \
                         or self.product.create(self.data_product_1_old)

        self.products = [self.product_0.product_tmpl_id, self.product_1.product_tmpl_id]

        self.langs = [('en', 'en_US'), ('fr', 'fr_FR'), ('he', 'he_IL'), ('ru', 'ru_RU')]

        self.En = self.langs[0][1]
        self.Fr = self.langs[1][1]
        self.He = self.langs[2][1]
        self.Ru = self.langs[3][1]

        for iso_code, lang_code in self.langs:
            _logger.debug(f'Looking for {lang_code}')
            lang_obj = self.env['res.lang'].search([
                ('active', '=', True),
                ('code', '=', lang_code)
            ])
            if not lang_obj:
                self.env['res.lang']._activate_lang(lang_code)
                _logger.debug(f'Activated lang {lang_code}')
            else:
                _logger.debug(f'{lang_code} is activated already')

        self.trns = self.env['ir.translation']
        for obj in self.products:
            for iso_code, lang in self.langs:
                tr_name = 'product.template,name'
                self.trns += self.env['ir.translation'].create({
                    'src': obj.name,
                    'name': tr_name,
                    'res_id': obj.id,
                    'lang': lang,
                    'type': 'model',
                    'value': f'before {obj.name} {lang}',
                    'state': 'to_translate',
                })

    def test_translations(self):
        field_names = ['name']
        all_translations = self.tanker_data.get('keysets').get('production_products').get('keys')
        translations = self.env['lavka.translations'].dry_translation(
            [self.product_0.product_tmpl_id, self.product_1.product_tmpl_id],
            all_translations,
            field_names,
            self.langs,
        )
        products = [self.product_0.product_tmpl_id, self.product_1.product_tmpl_id]
        lang = self.env['res.lang'].search([('active', '=', True)])
        curr_translations = self.env['lavka.translations'].get_translation_to_update(products, field_names, lang)
        # загружаем переводы
        for obj in products:
            trn_names = [f'{obj._name},{fld}' for fld in field_names]

            self.env['lavka.translations'].update_create_field_translations(translations, self.langs, obj, field_names, curr_translations)
            trns = self.env['ir.translation'].search([
                ('res_id', '=', obj.id),
                ('name', 'in', trn_names)
            ])

            if obj.id == self.product_0.product_tmpl_id.id:
                self.assertEqual(len(trns), len(self.langs), f'some translation are missing!'
                                                         f'Expected {len(self.langs)} got {len(trns)}')
            if obj.id == self.product_1.product_tmpl_id.id:
                self.assertEqual(len(trns), len(self.langs), f'some translation are missing!'
                                                         f'Expected {len(self.langs)} got {len(trns)}')
            for trn in trns:
                if obj == self.product_0.product_tmpl_id:
                    vals = ['ENGLAND FOR GENTLEMEN!',
                            'FRANCE IS A GREAT FOR MAROCCANS!',
                            'Hava nagila ve-nismeḥa',
                            'KALINKA-MALINKA']
                    self.assertIn(trn.value, vals, f'{trn.value} not in {vals}')
                if obj == self.product_1.product_tmpl_id and trn.lang in ['fr_FR', 'he_IL']:
                    vals0 = [
                        'Voulez-vous coucher avec moi se soir?',
                        'okay, it is Hebrew',
                    ]
                    self.assertIn(trn.value, vals0, f'{trn.value} not in {vals0}')

        # теперь обновим переводы
        self.env['ir.config_parameter'].set_param('refresh_all_product_translations', 'true')
        updated_data = self.tanker_data_updt.get('keysets').get('production_products').get('keys')
        translations = self.env['lavka.translations'].dry_translation(
            [self.product_0.product_tmpl_id],
            updated_data,
            field_names,
            self.langs,
        )
        curr_translations = self.env['lavka.translations'].get_translation_to_update(products, field_names, lang)
        self.env['lavka.translations'].update_create_field_translations(
            translations,
            self.langs,
            self.product_0.product_tmpl_id,
            field_names,
            curr_translations
        )
        trns0 = self.env['ir.translation'].search([
            ('res_id', '=', self.product_0.product_tmpl_id.id),
            ('name', '=', 'product.template,name')
        ])
        for trn in trns0:
            vals = [
                'Hava nagila ve-nismeḥa',
                'KALINKA-MALINKA',
                # это измененные переводы
                'FRANCE IS A GREAT FOR MAROCCANS! AND ALGERIANS!',
                'ENGLAND FOR GENTLEMEN! AND INDIAN PEOPLE!',
            ]
            self.assertIn(trn.value, vals, f'{trn.value} not in {vals}')


@tagged('lavka', 'trn', 'tanker_woody')
class TestTankerWoodyTranslations(SingleTransactionCase):

    def setUp(self):
        super().setUp()
        self.dt_tr =[
            # need translation FR
            {
                'name': 'ir.model.fields,help',
                'res_id': 555777,
                'lang': 'fr_FR',
                'type': 'model',
                'src': '<span class="o_stat_text">Invoiced</span>',
                'value': '',
                'module': 'lavka',
                'state': 'to_translate',
                'comments': 'translate plz FR'
            },
            # need translation RU
            {
                'name': 'ir.model.fields,help',
                'res_id': 555777,
                'lang': 'ru_RU',
                'type': 'model',
                'src': '<span class="o_stat_text">Invoiced</span>',
                'value': '',
                'module': 'lavka',
                'state': 'to_translate',
                'comments': 'translate plz RU'
            },
            # already translated
            {
                'name': 'ir.model.fields,help',
                'res_id': 555888,
                'lang': 'fr_FR',
                'type': 'code',
                'src': 'Post',
                'value': 'Le Post',
                'module': 'lavka',
                'state': 'translated',
                'comments': ''
            },
            # EN don't need translation
            {
                'name': 'ir.model.fields,help',
                'res_id': 555888,
                'lang': 'en_US',
                'type': 'code',
                'src': 'Post',
                'value': 'Post',
                'module': 'lavka',
                'state': 'to_translate',
                'comments': ''
            },
            # need translation RU, but has exceptional name
            {
                'name': 'product.template,name',
                'res_id': 555888,
                'lang': 'ru_RU',
                'type': 'model',
                'src': 'Some product name',
                'value': '',
                'module': 'lavka',
                'state': 'to_translate',
                'comments': 'translate plz RU'
            },
            # empty src
            {
                'name': 'ir.model.fields,help',
                'res_id': 555888,
                'lang': 'fr_FR',
                'type': 'model',
                'src': '',
                'value': '',
                'module': 'lavka',
                'state': 'to_translate',
                'comments': 'translate plz FR'
            },
            # space in src
            # don't need to translate
            {
                'name': 'ir.model.fields,help',
                'res_id': 555999,
                'lang': 'fr_FR',
                'type': 'model',
                'src': ' ',
                'value': '',
                'module': 'lavka',
                'state': 'to_translate',
                'comments': 'translate plz FR'
            },
            # space at beginning and text after in src
            # need to translate
            {
                'name': 'ir.model.fields,help',
                'res_id': 555999,
                'lang': 'ru_RU',
                'type': 'model',
                'src': ' Some text',
                'value': '',
                'module': 'lavka',
                'state': 'to_translate',
                'comments': 'translate plz RU'
            },
        ]
        self.langs = [('en', 'en_US'), ('fr', 'fr_FR'), ('he', 'he_IL'), ('ru', 'ru_RU')]

        self.En = self.langs[0][1]
        self.Fr = self.langs[1][1]
        self.He = self.langs[2][1]
        self.Ru = self.langs[3][1]

        for iso_code, lang_code in self.langs:
            _logger.debug(f'Looking for {lang_code}')
            lang_obj = self.env['res.lang'].search([
                ('active', '=', True),
                ('code', '=', lang_code)
            ])
            if not lang_obj:
                self.env['res.lang']._activate_lang(lang_code)
                _logger.debug(f'Activated lang {lang_code}')
            else:
                _logger.debug(f'{lang_code} is activated already')

        ir_trn = self.env['ir.translation']
        self.translation_objects = []
        for dt_tr_item in self.dt_tr:
            self.translation_objects.append(
                (
                        ir_trn.search(
                            [
                                ('type', '=', dt_tr_item['type']),
                                ('name', '=', dt_tr_item['name']),
                                ('lang', '=', dt_tr_item['lang']),
                                ('res_id', '=', dt_tr_item['res_id']),
                                ('src', '=', dt_tr_item['src']),
                            ]
                        )
                        or
                        ir_trn.create(dt_tr_item)
                )
             )
        self.env.cr.commit()

        self.tanker_data_empty =[]

        keyName = self.env['lavka.translations'].get_key_name(
            'ir.model.fields,help',
            '<span class="o_stat_text">Invoiced</span>',
            555777
        )

        self.tanker_data_keys_added =[
            {'lang': 'ru',
             'keys': [{'commit_id': 4998844, 'name': keyName,
                       'translations': {'en': {'commit_id': 4998844,
                                               'name': keyName,
                                               'language': 'en', 'status': 'REQUIRES_TRANSLATION', 'payload': {
                               'singular_form': '<span class="o_stat_text">Invoiced</span>',
                               'translator_comment': ''}}},
                       'meta': {'context': {'text': 'translate plz RU', 'links': [], 'images': []}, 'locked': False,
                                'plural': False, 'source_reference': '', 'array': False, 'position': 0,
                                'custom_data': {}}},
                      ]},
            {'lang': 'fr',
             'keys': [{'commit_id': 4998845, 'name': keyName,
                       'translations': {'en': {'commit_id': 4998845,
                                               'name': keyName,
                                               'language': 'en', 'status': 'REQUIRES_TRANSLATION', 'payload': {
                               'singular_form': '<span class="o_stat_text">Invoiced</span>',
                               'translator_comment': ''}}},
                       'meta': {'context': {'text': 'translate plz FR', 'links': [], 'images': []}, 'locked': False,
                                'plural': False, 'source_reference': '', 'array': False, 'position': 0,
                                'custom_data': {}}},
                      ]}
        ]

        self.tanker_data_keys_translated =[
            {'lang': 'ru',
              'keys': [{'commit_id': 4998847, 'name': keyName,
                        'translations': {'en': {'commit_id': 4998847,
                                                'name': keyName,
                                                'language': 'en', 'status': 'APPROVED', 'payload': {
                                'singular_form': '<span class="o_stat_text">Invoiced</span>',
                                'translator_comment': ''}},
                                         'ru': {'commit_id': 4998847,
                                                'name': keyName,
                                                'language': 'ru', 'status': 'APPROVED',
                                                'payload': {
                                                    'singular_form': '<span class="o_stat_text">RU Invoiced</span>',
                                                    'translator_comment': ''}}},
                        'meta': {'context': {'text': 'translate plz RU', 'links': [], 'images': []}, 'locked': False,
                                 'plural': False, 'source_reference': '', 'array': False, 'position': 0,
                                 'custom_data': {}}},
                       ]},
             {'lang': 'fr',
              'keys': [{'commit_id': 4998846, 'name': keyName,
                        'translations': {'en': {'commit_id': 4998846,
                                                'name': keyName,
                                                'language': 'en', 'status': 'APPROVED', 'payload': {
                                'singular_form': '<span class="o_stat_text">Invoiced</span>',
                                'translator_comment': ''}},
                                         'fr': {'commit_id': 4998846,
                                                'name': keyName,
                                                'language': 'fr', 'status': 'APPROVED',
                                                'payload': {
                                                    'singular_form': '<span class="o_stat_text">FR Invoiced</span>',
                                                    'translator_comment': ''}}},
                        'meta': {'context': {'text': 'translate plz FR', 'links': [], 'images': []}, 'locked': False,
                                 'plural': False, 'source_reference': '', 'array': False, 'position': 0,
                                 'custom_data': {}}},
                       ]}]

        self.langs = [('en', 'en_US'), ('fr', 'fr_FR'), ('ru', 'ru_RU')]

        for iso_code, lang_code in self.langs:
            _logger.debug(f'Looking for {lang_code}')
            lang_obj = self.env['res.lang'].search([
                ('active', '=', True),
                ('code', '=', lang_code)
            ])
            if not lang_obj:
                self.env['res.lang']._activate_lang(lang_code)

    def tearDown(self):
        for translation_objects_item in self.translation_objects:
            translation_objects_item.unlink()
        self.env.cr.commit()

    def test_translations(self):
        lang = self.env['res.lang'].search([('active', '=', True)])
        lang_mapping = {la.code: la.iso_code for la in lang}

        all_tanker_keys = self.tanker_data_empty
        tanker_keys = self.env['lavka.translations'].dry_tanker_keys(all_tanker_keys)
        del all_tanker_keys

        not_translated = self.env['lavka.translations'].get_not_translated_woody_strings(lang_mapping)
        # leave only keys created for testing
        not_translated = [x for x in not_translated if x in self.translation_objects]

        # test no exceptional names in not translated keys
        not_translated_names = [x.name for x in not_translated]
        for name_exception in cfg('tanker.woody_name_exceptions'):
            with self.subTest(value=name_exception):
                self.assertTrue(name_exception not in not_translated_names,
                         f'only not exceptional names must be selected to translate')

        woody_not_translated_keys = self.env['lavka.translations'].get_not_translated_keys(not_translated, lang_mapping)
        # test selection of woody non translated keys
        self.assertEqual(len(woody_not_translated_keys), 3,
                         f'only not translated non EN not empty keys must be selected to translate')

        # test keyName creation algorithm
        remove_characters = ('.', ',', '/')
        rc = '[' + re.escape(''.join(remove_characters)) + ']'
        for not_translated_key in woody_not_translated_keys:
            keyPrefix = re.sub(rc, '_', not_translated_key['key']['name'])
            keyName = hashlib.md5(not_translated_key['key']['src'].encode('utf-8')).hexdigest()
            keyName = f"{keyPrefix}_{not_translated_key['key']['res_id']}_{keyName}"

            self.assertEqual(not_translated_key['keyName'], keyName,
                             f'key name creation algorithm error')

        # test selection of keys to add to Tanker
        # we have 2 not translated keys are not in Tanker
        tanker_keys_to_add = self.env['lavka.translations'].get_tanker_keys_to_add(woody_not_translated_keys,
                                                                                   tanker_keys)
        self.assertEqual(len(tanker_keys_to_add), 3,
                         f'get_tanker_keys_to_add() returns wrong number of keys')

        # all not translated woody keys are in Tanker
        # test no need to add keys to Tanker
        all_tanker_keys = self.tanker_data_keys_added
        tanker_keys = self.env['lavka.translations'].dry_tanker_keys(all_tanker_keys)
        del all_tanker_keys

        tanker_keys_to_add = self.env['lavka.translations'].get_tanker_keys_to_add(woody_not_translated_keys,
                                                                                   tanker_keys)
        self.assertEqual(len(tanker_keys_to_add), 1,
                         f'get_tanker_keys_to_add() returns wrong number of keys')

        # all not translated woody keys are translated in Tanker
        all_tanker_keys = self.tanker_data_keys_translated
        tanker_keys = self.env['lavka.translations'].dry_tanker_keys(all_tanker_keys)
        del all_tanker_keys

        # test updation keys in Woody
        self.env['lavka.translations'].update_woody_key_translations(woody_not_translated_keys, tanker_keys)
        self.env.cr.commit()

        # test selection of woody non translated keys
        # all keys are translated now
        not_translated = self.env['lavka.translations'].get_not_translated_woody_strings(lang_mapping)
        # leave only keys created for testing
        not_translated = [x for x in not_translated if x in self.translation_objects]

        woody_not_translated_keys = self.env['lavka.translations'].get_not_translated_keys(not_translated, lang_mapping)
        self.assertEqual(len(woody_not_translated_keys), 1,
                         f'only not translated non EN not empty keys must be selected to translate')

        # test right translated value
        translated_key_FR = self.env['ir.translation'].search([
                ('id', '=', self.translation_objects[0]['id']),
            ])
        self.assertEqual(translated_key_FR.value, '<span class="o_stat_text">FR Invoiced</span>',
                         f'right value for FR translation not found')

        translated_key_RU = self.env['ir.translation'].search([
                ('id', '=', self.translation_objects[1]['id']),
            ])
        self.assertEqual(translated_key_RU.value, '<span class="o_stat_text">RU Invoiced</span>',
                         f'right value for RU translation not found')
