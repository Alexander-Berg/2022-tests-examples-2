# coding: utf-8
import unittest
import dmp_suite.tsv as tsv
from dmp_suite.exceptions import DWHError


class TestTSV(unittest.TestCase):
    def test_escape(self):
        self.assertEqual(tsv.escape('stroka'), 'stroka')
        self.assertEqual(tsv.escape('строка'), 'строка')
        self.assertEqual(tsv.escape(r'a\b\c'), r'a\\b\\c')
        self.assertEqual(tsv.escape('aa\tbb'), 'aa\\\tbb')
        self.assertEqual(tsv.escape('aa\\\tbb'), 'aa\\\\\\\tbb')
        self.assertEqual(tsv.escape('aa\nbb'), 'aa\\\nbb')
        self.assertEqual(tsv.escape('aa\tb\nb\n'), 'aa\\\tb\\\nb\\\n')
        self.assertEqual(tsv.escape('2018-12-12 12:12:12'),
                         '2018-12-12 12:12:12'),
        self.assertEqual(tsv.escape(b'\N'), br'\N'),
        self.assertEqual(tsv.escape(b'aa\Nbb'), br'aa\\Nbb')

    def test_serialize_if_need(self):
        self.assertEqual(tsv._try_to_serialize_if_need(7), b'7')
        from_float = tsv._try_to_serialize_if_need(2.0 / 3)
        self.assertTrue(from_float.startswith(b'0.66666'))
        self.assertEqual(tsv._try_to_serialize_if_need(u'строка'), u'строка'.encode('utf-8'))
        self.assertEqual(tsv._try_to_serialize_if_need(None), b'')
        self.assertRaises(DWHError, tsv._try_to_serialize_if_need, [1, 2])
        self.assertRaises(DWHError, tsv._try_to_serialize_if_need, dict(a=1))

    def test_serialize_records(self):
        records = [
            dict(a=u'stroka1', b=u'aa\tbb', c=u'a\nb'),
            dict(a=u'stroka2', b=u'aa\tbb', c=u'a\nb')
        ]
        true_tsv_records = \
            b"stroka1\taa\\\tbb\ta\\\nb\n"\
            b"stroka2\taa\\\tbb\ta\\\nb\n"
        self.assertEqual(
            tsv.serialize_records(records, ['a', 'b', 'c']),
            true_tsv_records
        )
