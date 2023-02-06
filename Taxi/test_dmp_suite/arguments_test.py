#!/usr/bin/env python
# coding: utf-8
import os
import argparse
from datetime import datetime
from unittest import TestCase

from mock import patch, MagicMock

from dmp_suite import datetime_utils as dtu
from dmp_suite.arguments import(
    BaseParser,
    IdParser,
    ScaleParser,
    YTParser,
    validate_pool,
    SSASParser,
    ObjectLocationParser,
)


class TestArgument(TestCase):
    def test_base_parser(self):
        parser = BaseParser()
        args = parser.parse_args([
            '--start_date', '2018-05-02',
            '--end_date', '2018-07-23',
        ])
        self.assertEqual(datetime(2018, 5, 2, 0, 0), args.start_date)
        self.assertEqual(datetime(2018, 7, 23, 23, 59, 59, 999999), args.end_date)

        parser = BaseParser(datetime_type='datetime')
        args = parser.parse_args([
            '--start_date', '2018-05-02 04:08:15',
            '--end_date', '2018-07-23 16:23:42'
        ])
        self.assertEqual(datetime(2018, 5, 2, 4, 8, 15), args.start_date)
        self.assertEqual(datetime(2018, 7, 23, 16, 23, 42), args.end_date)

    def test_id_parser(self):
        parser = IdParser()

        args = parser.parse_args([])
        assert args.start_id is None

        args = parser.parse_args(["--start_id", "42"])
        assert args.start_id == 42

    def test_scale_parser(self):
        parser = ScaleParser()
        args = parser.parse_args([
            '--start_date', '2018-05-02',
            '--end_date', '2018-07-23',
            '--scale', 'm',
        ])
        self.assertEqual(args.start_date, datetime(2018, 5, 1, 0, 0))
        self.assertEqual(args.end_date, datetime(2018, 7, 31, 23, 59, 59, 999999))
        self.assertEqual(
            args.period,
            dtu.period(
                datetime(2018, 5, 1, 0, 0),
                datetime(2018, 7, 31, 23, 59, 59, 999999)
            )
        )
        self.assertEqual('m', args.scale)
        self.assertEqual(3, len(list(args.periods)))

    def test_YT_Parser(self):
        parser = YTParser()
        args = parser.parse_args([
            '--start_date', '2018-05-02',
            '--end_date', '2018-07-23',
            '--pool', 'TAXI_DWH_PRIORITY',
        ])
        self.assertEqual('TAXI_DWH_PRIORITY', args.pool.value)

    def test_YT_Parser_wrong_argument(self):
        """
        Тут тестируется только функция validate_pool, так как если парсер сваливается с исключением - то вызывается
        внутрях sys.exit(2)
        :return:
        """
        self.assertRaises(argparse.ArgumentTypeError, validate_pool, 'Chuck_Norris')

    def test_SSAS_Parser_cube_argument(self):
        parser = SSASParser()
        args = parser.parse_args([
            '--start_date', '2018-05-02',
            '--end_date', '2018-07-23',
            '--cube_name', 'chuck_norris'
        ])
        self.assertEqual('chuck_norris', args.cube_name)
        self.assertEqual(False, args.sync_model)

    def test_ObjectLocation_Parser_wo_attribute_name(self):
        parser = ObjectLocationParser()
        args = parser.parse_args([
            __file__
        ])
        assert args.module.__name__ == __name__
        assert args.obj is None
        assert args.module_path == __file__
        assert args.attribute_name is None

    def test_ObjectLocation_Parser_w_attribute_name(self):
        parser = ObjectLocationParser()
        args = parser.parse_args([
            __file__ + "::" + self.__class__.__name__
        ])
        assert args.module.__name__ == __name__
        assert args.obj is self.__class__
        assert args.module_path == __file__
        assert args.attribute_name == self.__class__.__name__

    def test_ObjectLocation_Parser_non_existing_module(self):
        parser = ObjectLocationParser()
        with self.assertRaises(ValueError):
            args = parser.parse_args([
                os.path.join(__file__, "non_existing_module")
            ])

    def test_ObjectLocation_Parser_non_existing_object(self):
        parser = ObjectLocationParser()
        with self.assertRaises(AttributeError):
            args = parser.parse_args([
                __file__ + "::" + "non_existing_object"
            ])
