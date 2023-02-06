import datetime

from odoo import exceptions
from odoo.tests import tagged, SavepointCase
from odoo.addons.lavka.backend.wizzard.base_import_wizzard import (
    IntParser,
    FloatParser,
    IDListParser,
    StringParser,
    BooleanParser,
    DateParser,
    ForeignKeySerializer,
)


@tagged('lavka', 'autoorder', 'autoorder_imports', 'base_import')
class TestBaseImportTools(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.wh_tag1 = cls.env['stock.warehouse.tag'].create(
            {
                'type': 'geo',
                'name': 'Paris 1',
            }
        )

        cls.wh_tag2 = cls.env['stock.warehouse.tag'].create(
            {
                'type': 'geo',
                'name': 'Paris 2',
            }
        )

        cls.wh_tag3 = cls.env['stock.warehouse.tag'].create(
            {
                'type': 'size',
                'name': 'Big',
            }
        )

        cls.wh_tag4 = cls.env['stock.warehouse.tag'].create(
            {
                'type': 'size',
                'name': 'Little',
            }
        )

    def test_id_list_parser_001(self):
        parser = IDListParser()

        value = parser.parse('1')
        self.assertEqual(['1'], value)

        value = parser.parse('1, 2')
        self.assertEqual(['1', '2'], value)

        value = parser.parse(1)
        self.assertEqual(['1'], value)

        value = parser.parse(1.0)
        self.assertEqual(['1'], value)

        value = parser.parse(0)
        self.assertEqual(['0'], value)

    def test_id_list_parser_002(self):
        parser = IDListParser()

        value = parser.parse('abc')
        self.assertEqual(['abc'], value)

        value = parser.parse('abc, 567')
        self.assertEqual(['abc', '567'], value)

        value = parser.parse('abc,def')
        self.assertEqual(['abc', 'def'], value)

        value = parser.parse('  abc   ,    def  ')
        self.assertEqual(['abc', 'def'], value)

        value = parser.parse(None)
        self.assertEqual([], value)

    def test_id_list_parser_003(self):
        parser = IDListParser(required=True)
        self.assertRaises(ValueError, parser.parse, None)

    def test_id_list_parser_004(self):
        parser = IDListParser(default=['1', '2'])
        self.assertEqual(['1', '2'], parser.parse(None))

    def test_int_parser_001(self):
        parser = IntParser()

        value = parser.parse('0')
        self.assertEqual(0, value)

        value = parser.parse('1')
        self.assertEqual(1, value)

        value = parser.parse('1.0')
        self.assertEqual(1, value)

        value = parser.parse(1)
        self.assertEqual(1, value)

        value = parser.parse(1.0)
        self.assertEqual(1, value)

        value = parser.parse(1.2)
        self.assertEqual(1, value)

        value = parser.parse('abc')
        self.assertEqual(None, value)

    def test_int_parser_002(self):
        parser = IntParser(required=True)
        self.assertRaises(ValueError, parser.parse, 'abc')

    def test_int_parser_003(self):
        parser = IntParser(process=str, default=0)

        value = parser.parse('0')
        self.assertEqual('0', value)

        value = parser.parse('1')
        self.assertEqual('1', value)

        value = parser.parse('1.0')
        self.assertEqual('1', value)

        value = parser.parse(1)
        self.assertEqual('1', value)

        value = parser.parse('abc')
        self.assertEqual('0', value)

    def test_float_parser_001(self):
        parser = FloatParser()

        value = parser.parse(0)
        self.assertEqual(0.0, value)

        value = parser.parse(1)
        self.assertEqual(1.0, value)

        value = parser.parse('0')
        self.assertEqual(0.0, value)

        value = parser.parse('1')
        self.assertEqual(1.0, value)

        value = parser.parse('1.5')
        self.assertEqual(1.5, value)

        value = parser.parse('abc')
        self.assertEqual(None, value)

    def test_float_parser_002(self):
        parser = FloatParser(required=True)
        self.assertRaises(ValueError, parser.parse, 'abc')

    def test_boolean_parser(self):
        parser = BooleanParser()

        value = parser.parse(0)
        self.assertEqual(False, value)

        value = parser.parse(1)
        self.assertEqual(True, value)

        value = parser.parse('0')
        self.assertEqual(False, value)

        value = parser.parse('1')
        self.assertEqual(True, value)

    def test_date_parser_001(self):
        parser = DateParser()

        value = parser.parse('2021-05-05')
        self.assertEqual(datetime.date(2021, 5, 5), value)

        value = parser.parse('05.05.2021')
        self.assertEqual(None, value)

    def test_date_parser_002(self):
        parser = DateParser(required=True, fmt='%d.%m.%Y')

        value = parser.parse('05.05.2021')
        self.assertEqual(datetime.date(2021, 5, 5), value)

        self.assertRaises(ValueError, parser.parse, '2021-05-05')

    def test_string_parser(self):
        parser = StringParser()

        value = parser.parse('1')
        self.assertEqual('1', value)

        value = parser.parse('abc')
        self.assertEqual('abc', value)

        value = parser.parse(0)
        self.assertEqual('0', value)

        value = parser.parse(1)
        self.assertEqual('1', value)

        value = parser.parse('  1  ')
        self.assertEqual('1', value)

        value = parser.parse('')
        self.assertEqual(None, value)

    def test_foreign_key_serializer_001(self):
        serializer = ForeignKeySerializer(
            'stock.warehouse.tag',
            'tag',
            'name',
            domain=[('type', '=', 'geo')],
            multi=True,
        )

        rows = [
            {'tag': ['Paris 1', 'Paris 2']},
            {'tag': ['Paris 1']},
        ]

        serializer.prepare(self.env, rows)

        test_values = [
            {'tag': (self.wh_tag1.id, self.wh_tag2.id)},
            {'tag': (self.wh_tag1.id,)},
        ]

        for row, value in zip(rows, test_values):
            serializer.serialize(row)
            self.assertEqual(row, value)

    def test_foreign_key_serializer_002(self):
        serializer = ForeignKeySerializer(
            'stock.warehouse.tag',
            'tag',
            'name',
            domain=[('type', '=', 'geo')],
        )

        rows = [
            {'tag': 'Paris 1'},
            {'tag': 'Paris 2'},
        ]

        serializer.prepare(self.env, rows)

        test_values = [
            {'tag': self.wh_tag1.id},
            {'tag': self.wh_tag2.id},
        ]

        for row, value in zip(rows, test_values):
            serializer.serialize(row)
            self.assertEqual(row, value)

    def test_foreign_key_serializer_003(self):
        serializer = ForeignKeySerializer(
            'stock.warehouse.tag',
            'tag',
            'name',
            multi=True,
        )

        rows = [
            {'tag': ['Paris 1', 'Paris 2']},
            {'tag': ['Big', 'Little']},
        ]

        serializer.prepare(self.env, rows)

        test_values = [
            {'tag': (self.wh_tag1.id, self.wh_tag2.id)},
            {'tag': (self.wh_tag3.id, self.wh_tag4.id)},
        ]

        for row, value in zip(rows, test_values):
            serializer.serialize(row)
            self.assertEqual(row, value)

    def test_foreign_key_serializer_004(self):
        serializer = ForeignKeySerializer(
            'stock.warehouse.tag',
            'tag',
            'name',
            multi=True,
        )

        rows = [
            {'tag': ['Paris 1']},
            {'tag': ['Big']},
        ]

        serializer.prepare(self.env)

        test_values = [
            {'tag': (self.wh_tag1.id,)},
            {'tag': (self.wh_tag3.id,)},
        ]

        for row, value in zip(rows, test_values):
            serializer.serialize(row)
            self.assertEqual(row, value)

    def test_foreign_key_serializer_005(self):
        serializer = ForeignKeySerializer(
            'stock.warehouse.tag',
            'tag',
            'name',
            domain=[('type', '=', 'geo')],
        )

        rows = [
            {'tag': 'Big'},
        ]

        serializer.prepare(self.env, rows)

        self.assertRaises(exceptions.UserError, serializer.serialize, rows[0])
