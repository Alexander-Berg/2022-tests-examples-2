# -*- coding: utf-8 -*-

from unittest import TestCase

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.models.base import Model
from passport.backend.core.models.base.fields import Field
from passport.backend.core.undefined import Undefined


class TestModel(Model):
    id = Field('id')

    @property
    def foo(self):
        raise ValueError('foo')


class AnotherModel(TestModel):
    pass


class TestModelBase(TestCase):
    def test_model_eq(self):
        m1 = TestModel().parse({'id': 42})
        m2 = TestModel().parse({'id': 40000})
        empty = TestModel().parse({})

        # Экземпляр модель всегда неравен Undefined и None
        ok_(m1 != Undefined)
        ok_(m1 is not None)

        # Экземпляр модель всегда равен себе
        eq_(m1, m1)
        # Экземпляр модель всегда неравен экземпляру той же модели
        # с иным содержимым
        ok_(m1 != m2)
        # Экземпляр модель всегда неравен экземпляру той же модели
        # с пустым содержимым
        ok_(m1 != empty)

        # Экземпляр модели всегда неравен экземпляру другой модели,
        # даже если у них совпадает содержимое.
        am1 = AnotherModel()
        am1.__dict__ = m1.__dict__
        ok_(m1 != am1)

    def test_property__set_raises_exception(self):
        # Проверка, что исключение в свойствах не маскируются
        model = TestModel()
        with assert_raises(ValueError) as assertion:
            model.foo = 'bar'
        eq_(assertion.exception.args, ('foo',))
