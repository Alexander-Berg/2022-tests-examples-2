# -*- coding: utf-8 -*-
from unittest import TestCase

from nose.tools import assert_raises
from passport.backend.core.types.bit_vector.bit_vector import (
    BitVector,
    PhoneBindingsFlags,
    PhoneOperationFlags,
)


class TestBitVector(TestCase):
    def test_basic(self):
        """
        Проверим основные возможности класса: возьмем число, поменяем у него биты.
        """
        bv = BitVector(4)
        assert int(bv) == 4
        assert bv[2] == 1

        bv[0] = 1
        assert int(bv) == 5
        assert bv[0] == 1

        bv[1] = True
        assert int(bv) == 7
        assert bv[1] == 1

        bv[0] = 0
        assert int(bv) == 6
        assert bv[0] == 0

        bv[1] = False
        assert int(bv) == 4
        assert bv[1] == 0

        bv[2] = 0
        assert int(bv) == 0
        assert bv[2] == 0

        # Ставить можно только 0/1 и True/False
        with assert_raises(ValueError):
            bv[0] = '1'

    def test_eq(self):
        """
        Проверим, что работает == и !=
        """
        assert BitVector(4) == BitVector(4)
        assert BitVector() == BitVector(0)

        assert BitVector(4) != BitVector(5)
        assert BitVector(3) != 3

        # Инстансы разных классов не должны быть равны никогда!
        assert PhoneBindingsFlags(0) != PhoneOperationFlags(0)

    def test_invalid_input_data(self):
        with assert_raises(TypeError):
            BitVector('4')

    def test_named_fields(self):
        bv = BitVector()
        bv.field_names = {
            'a': 0,
            'b': 2,
        }
        bv.a = 1
        assert bv[0] == 1
        assert int(bv) == 1

        bv.b = 1
        assert bv[2] == 1
        assert int(bv) == 5

        # Поставим не относящееся к делу поле
        bv.c = 1
        assert int(bv) == 5


class TestNamedBitVectors(TestCase):
    def test_operation_flags(self):
        flags = PhoneOperationFlags()
        flags.aliasify = True
        flags.should_ignore_binding_limit = True
        assert int(flags) == 3

    def test_bindings_flags(self):
        flags = PhoneBindingsFlags()
        flags.should_ignore_binding_limit = True
        assert int(flags) == 1
