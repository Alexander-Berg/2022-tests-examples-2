#!/usr/bin/env python
# coding: utf-8

from unittest import TestCase

from dmp_suite import split


class TestLibSplit(TestCase):
    def test_chunks(self):
        iterable = range(10)
        chunks = list(split.chunks(iterable, chunk_size=4))
        expected_result = [list(range(4)), list(range(4, 8)), list(range(8, 10))]
        self.assertEqual(chunks, expected_result)

    def test_change_chunks_size(self):
        chunks = \
            [range(3), range(3, 7), range(7, 12), range(12, 18)]  # random sizes

        result = list(split.change_chunks_size(chunks, new_chunk_size=4))
        expected_result = list(split.chunks(range(18), 4))
        self.assertEqual(result, expected_result)

    def test_split(self):
        list_ = [1, 2, 3, 4]
        true, false = split.split(lambda x: x < 3, list_)
        self.assertTupleEqual((1, 2), tuple(true))
        self.assertTupleEqual((3, 4), tuple(false))

        str_ = 'abcd'
        true, false = split.split(lambda x: x <= 'b', str_)
        self.assertTupleEqual(('a', 'b'), tuple(true))
        self.assertTupleEqual(('c', 'd'), tuple(false))

        def generator(): yield None; yield 0; yield ''; yield False; yield True
        true, false = split.split(bool, generator())
        self.assertTupleEqual((True, ), tuple(true))
        self.assertTupleEqual((None, 0, '', False), tuple(false))
