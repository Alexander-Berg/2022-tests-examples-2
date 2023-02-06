# -*- coding: utf-8 -*-

from unittest import TestCase

from nose.tools import raises
from passport.backend.core.serializers.utils import CallbackResultContainer


class TestCallbackResultContainer(TestCase):
    def setUp(self):
        self.container = CallbackResultContainer()

    def tearDown(self):
        del self.container

    def test_val(self):
        self.container('a', 'b', 'c')
        assert self.container.val == 'a'

    def test_args(self):
        self.container('a', 'b', 'c')
        assert self.container.args == ('a', 'b', 'c')

    def test_kwargs(self):
        self.container(a='a', b='b')
        assert self.container.kwargs == {'a': 'a', 'b': 'b'}

    def test_assign(self):
        self.container.assign('a', 'b', c='c', d='d')
        assert self.container.args == ('a', 'b')
        assert self.container.kwargs == {'c': 'c', 'd': 'd'}

    def test_getitem(self):
        self.container('a', 'b', c='c', d='d')
        assert self.container[0] == 'a'
        assert self.container['c'] == 'c'

    @raises(ValueError)
    def test_reset(self):
        self.container('a', 'b', c='c', d='d')
        self.container.reset()
        self.container.__getitem__('a')
