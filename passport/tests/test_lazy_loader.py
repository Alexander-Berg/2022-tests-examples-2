# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.core.lazy_loader import (
    InstanceNotRegisteredError,
    lazy_loadable,
    LazyLoader,
)


@lazy_loadable(name='class_arg_for_test_lazy_arg', timeout=5, retries=5)
class ClassArgForTestLazy_arg(object):
    def __init__(self, retries=0, timeout=None):
        self.timeout = timeout
        self.retries = retries

    def get_timeout(self):
        return self.timeout

    def get_retries(self):
        return self.retries


@lazy_loadable(name='class_arg_for_test_lazy')
class ClassArgForTestLazy(object):
    def __init__(self, retries=0, timeout=None):
        self.timeout = timeout
        self.retries = retries

    def get_timeout(self):
        return self.timeout

    def get_retries(self):
        return self.retries


class TestLazyLoader(unittest.TestCase):
    def setUp(self):
        LazyLoader.register('list', list)
        LazyLoader.register('my_dict', dict, {1: 1})

    def test_instance(self):
        instance = LazyLoader.get_instance('list')
        instance.append(42)
        eq_(LazyLoader.get_instance('list'), instance)

    def test_instance_with_args(self):
        instance = LazyLoader.get_instance('my_dict')
        eq_(instance, {1: 1})
        instance['foo'] = 'bar'
        eq_(LazyLoader.get_instance('my_dict'), instance)

        instance = LazyLoader.get_instance('list', (1, 2, 3))
        eq_(instance, [1, 2, 3])
        eq_(LazyLoader.get_instance('list', (1, 2, 3)), instance)

    def test_creation_is_lazy(self):
        ok_(LazyLoader._instances['list']._instance is None)
        LazyLoader.get_instance('list')
        ok_(LazyLoader._instances['list']._instance is not None)

    def test_creation_dict_is_lazy(self):
        LazyLoader.flush()
        ok_(LazyLoader._instances['my_dict']._instance is None)
        LazyLoader.get_instance('my_dict')
        ok_(LazyLoader._instances['my_dict']._instance is not None)
        ok_("my_dict_['timeout']" not in LazyLoader._instances)
        LazyLoader.get_instance('my_dict', timeout=1)
        ok_(LazyLoader._instances['my_dict']._instance is not None)
        ok_(LazyLoader._instances["my_dict_[('timeout', 1)]"]._instance is not None)

    def test_creation_dict_kwargs_is_lazy(self):
        LazyLoader.flush()
        ok_(LazyLoader._instances['my_dict']._instance is None)
        LazyLoader.get_instance('my_dict', timeout=1)
        ok_(LazyLoader._instances['my_dict']._instance is None)
        ok_(LazyLoader._instances["my_dict_[('timeout', 1)]"]._instance is not None)
        LazyLoader.get_instance('my_dict')
        ok_(LazyLoader._instances['my_dict']._instance is not None)
        ok_(LazyLoader._instances["my_dict_[('timeout', 1)]"]._instance is not None)

    def test_creation_class_is_lazy(self):
        # тестируем порядок
        LazyLoader.flush()
        instance_timeout = LazyLoader.get_instance("class_arg_for_test_lazy", timeout=1)
        eq_(instance_timeout.timeout, 1)
        instance = LazyLoader.get_instance('class_arg_for_test_lazy')
        eq_(instance.timeout, None)
        eq_(instance.retries, 0)
        eq_(instance_timeout.timeout, 1)
        eq_(instance_timeout.retries, 0)

        LazyLoader.flush()
        instance = LazyLoader.get_instance('class_arg_for_test_lazy')
        eq_(instance.timeout, None)
        eq_(instance.retries, 0)
        instance_timeout = LazyLoader.get_instance('class_arg_for_test_lazy', timeout=1)
        eq_(instance_timeout.timeout, 1)
        eq_(instance_timeout.retries, 0)
        # тестируем на переменные
        instance = LazyLoader.get_instance('class_arg_for_test_lazy_arg')
        eq_(instance.timeout, 5)
        eq_(instance.retries, 5)
        instance_timeout = LazyLoader.get_instance('class_arg_for_test_lazy_arg', timeout=1)
        eq_(instance.timeout, 5)
        eq_(instance.retries, 5)
        eq_(instance_timeout.timeout, 1)
        eq_(instance_timeout.retries, 5)
        instance_all = LazyLoader.get_instance('class_arg_for_test_lazy_arg', timeout=3, retries=3)
        eq_(instance.timeout, 5)
        eq_(instance.retries, 5)
        eq_(instance_timeout.timeout, 1)
        eq_(instance_timeout.retries, 5)
        eq_(instance_all.timeout, 3)
        eq_(instance_all.retries, 3)

    def test_creation_class_is_lazy_inner(self):
        LazyLoader.flush()
        ok_(LazyLoader._instances['class_arg_for_test_lazy']._instance is None)
        ok_(
            "class_arg_for_test_lazy_[('timeout', 1)]" not in LazyLoader._instances or
            LazyLoader._instances["class_arg_for_test_lazy_[('timeout', 1)]"]._instance is None
        )
        LazyLoader.get_instance("class_arg_for_test_lazy", timeout=1)
        ok_(LazyLoader._instances['class_arg_for_test_lazy']._instance is None)
        ok_(LazyLoader._instances["class_arg_for_test_lazy_[('timeout', 1)]"]._instance is not None)
        LazyLoader.get_instance('class_arg_for_test_lazy')
        ok_(LazyLoader._instances['class_arg_for_test_lazy']._instance is not None)
        ok_(LazyLoader._instances["class_arg_for_test_lazy_[('timeout', 1)]"]._instance is not None)
        eq_(LazyLoader._instances["class_arg_for_test_lazy"]._instance.get_timeout(), None)
        eq_(LazyLoader._instances["class_arg_for_test_lazy_[('timeout', 1)]"]._instance.get_timeout(), 1)
        eq_(LazyLoader._instances["class_arg_for_test_lazy_[('timeout', 1)]"]._instance.get_retries(), 0)
        LazyLoader.flush()

        ok_(LazyLoader._instances['class_arg_for_test_lazy']._instance is None)
        ok_(LazyLoader._instances["class_arg_for_test_lazy_[('timeout', 1)]"]._instance is None)
        LazyLoader.get_instance('class_arg_for_test_lazy')
        ok_(LazyLoader._instances['class_arg_for_test_lazy']._instance is not None)
        ok_(LazyLoader._instances["class_arg_for_test_lazy_[('timeout', 1)]"]._instance is None)
        LazyLoader.get_instance('class_arg_for_test_lazy', timeout=1)
        ok_(LazyLoader._instances['class_arg_for_test_lazy']._instance is not None)
        ok_(LazyLoader._instances["class_arg_for_test_lazy_[('timeout', 1)]"]._instance is not None)
        eq_(LazyLoader._instances["class_arg_for_test_lazy"]._instance.get_timeout(), None)
        eq_(LazyLoader._instances["class_arg_for_test_lazy_[('timeout', 1)]"]._instance.get_timeout(), 1)
        eq_(LazyLoader._instances["class_arg_for_test_lazy_[('timeout', 1)]"]._instance.get_retries(), 0)

        LazyLoader.get_instance('class_arg_for_test_lazy_arg')
        eq_(LazyLoader._instances["class_arg_for_test_lazy_arg"]._instance.get_timeout(), 5)
        eq_(LazyLoader._instances["class_arg_for_test_lazy_arg"]._instance.get_retries(), 5)
        LazyLoader.get_instance('class_arg_for_test_lazy_arg', timeout=1)
        eq_(LazyLoader._instances["class_arg_for_test_lazy_arg"]._instance.get_timeout(), 5)
        eq_(LazyLoader._instances["class_arg_for_test_lazy_arg"]._instance.get_retries(), 5)
        eq_(LazyLoader._instances["class_arg_for_test_lazy_arg_[('timeout', 1)]"]._instance.get_timeout(), 1)
        eq_(LazyLoader._instances["class_arg_for_test_lazy_arg_[('timeout', 1)]"]._instance.get_retries(), 5)
        LazyLoader.get_instance('class_arg_for_test_lazy_arg', timeout=3, retries=3)
        eq_(LazyLoader._instances["class_arg_for_test_lazy_arg"]._instance.get_timeout(), 5)
        eq_(LazyLoader._instances["class_arg_for_test_lazy_arg"]._instance.get_retries(), 5)
        eq_(LazyLoader._instances["class_arg_for_test_lazy_arg_[('timeout', 1)]"]._instance.get_timeout(), 1)
        eq_(LazyLoader._instances["class_arg_for_test_lazy_arg_[('timeout', 1)]"]._instance.get_retries(), 5)
        eq_(LazyLoader._instances["class_arg_for_test_lazy_arg_[('retries', 3), ('timeout', 3)]"]
            ._instance.get_timeout(), 3)

    def test_flush(self):
        LazyLoader.get_instance('list')
        LazyLoader.get_instance('my_dict')
        ok_(LazyLoader._instances['list']._instance is not None)
        ok_(LazyLoader._instances['my_dict']._instance is not None)
        LazyLoader.flush(instance_name='my_dict')
        ok_(LazyLoader._instances['list']._instance is not None)
        ok_(LazyLoader._instances['my_dict']._instance is None)
        LazyLoader.flush()
        ok_(LazyLoader._instances['list']._instance is None)

    def test_drop(self):
        LazyLoader.get_instance('list')
        LazyLoader.get_instance('my_dict')
        ok_(LazyLoader._instances['list']._instance is not None)
        ok_(LazyLoader._instances['my_dict']._instance is not None)
        LazyLoader.drop(instance_name='my_dict')
        ok_('list' in LazyLoader._instances)
        ok_('my_dict' not in LazyLoader._instances)
        LazyLoader.drop(instance_name='list')
        ok_('list' not in LazyLoader._instances)

    @raises(InstanceNotRegisteredError)
    def test_instance_not_registered(self):
        LazyLoader.get_instance('unknown')

    @raises(InstanceNotRegisteredError)
    def test_flush_not_registered_instance(self):
        LazyLoader.flush('unknown')

    @raises(InstanceNotRegisteredError)
    def test_drop_not_registered_instance(self):
        LazyLoader.drop('unknown')

    @raises(ValueError)
    def test_error_on_create(self):
        LazyLoader.register('int', int, 'a')
        LazyLoader.get_instance('int')
