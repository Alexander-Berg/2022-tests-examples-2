from collections import Iterable
from datetime import timedelta

import pytest

import dmp_suite.clickhouse as ch
import dmp_suite.greenplum as gp
import dmp_suite.yt as yt
from dmp_suite import scales
from dmp_suite.ctl import CTL_LAST_SYNC_DATE, CTL_LAST_LOAD_DATE
from dmp_suite.exceptions import DWHError
from dmp_suite.greenplum.table import GPTable, Int, String
from dmp_suite.meta import Meta
from dmp_suite.table import (
    DBObject, Table, Field, PartitionScale,
    LayeredLayout, ValidateError, OdsLayout,
    abstracttable, TableMeta, Sla, build_new_layout,
)
from test_dmp_suite.domain.common import test_domain


def test_partition_scale_has_equal_scale():
    ps1 = PartitionScale('a', scales.day)
    ps2 = PartitionScale('a', scales.day)
    assert ps1.has_equal_scale(ps2) and ps2.has_equal_scale(ps1)

    ps1 = PartitionScale('a', scales.day)
    ps2 = PartitionScale('b', scales.day)
    assert ps1.has_equal_scale(ps2) and ps2.has_equal_scale(ps1)

    ps1 = PartitionScale('a', scales.month)
    ps2 = PartitionScale('a', scales.day)
    assert not ps1.has_equal_scale(ps2) and not ps2.has_equal_scale(ps1)


class SimpleTable(Table):
    __layout__ = None
    field = Field()


def test_partition_scale_validate():
    meta = Meta(SimpleTable)

    ps = PartitionScale('f', scales.day)
    with pytest.raises(AttributeError):
        ps.validate(meta)

    ps = PartitionScale('field', scales.day)
    ps.validate(meta)


def test_field_init():
    with pytest.raises(AttributeError):
        Field(not_a_field=1)

    class AField(Field):
        z = None

    with pytest.raises(AttributeError):
        AField(not_a_field=1)

    af = AField(z=3, name='a', )
    assert af.name == 'a'
    assert af.z == 3


class TestTable:
    class TestLayout(LayeredLayout):
        def __init__(self, name):
            super().__init__(layer='testing', name=name, prefix_key='test')

    def test_field_name(self):
        class T(Table):
            a = Field()
            b = Field(name='bb')

        assert T.a.name == 'a'
        assert T.b.name == 'bb'

    def test_is_abstract(self):
        class T(Table):
            pass

        assert not T.is_abstract()

        @abstracttable
        class AbstractT(Table):
            pass

        assert AbstractT.is_abstract()

        class DerivedFromAbstract(AbstractT):
            pass

        assert not DerivedFromAbstract.is_abstract()

    def test_get_layout(self):
        class T(Table):
            pass

        with pytest.raises(AttributeError):
            T.get_layout()

        layout = LayeredLayout('layer', 'name')

        class T(Table):
            __layout__ = layout

        assert T.get_layout() is layout

    def test_has_and_get_field(self):
        class T(Table):
            a = Field()
            b = Field(name='bb')

        assert T.has_field('a')
        assert not T.has_field('b')
        assert T.has_field('bb')

        with pytest.raises(ValueError):
            T.get_field('b')

        assert T.get_field('a') == Field(name='a', alias='a')
        assert T.get_field('bb') == Field(name='bb', alias='b')

    def test_bad_field_names(self):
        with pytest.raises(AttributeError):
            class DuplicateFields1(Table):
                a = Field(name='b')
                b = Field()

        with pytest.raises(AttributeError):
            class DuplicateFields2(Table):
                a = Field(name='c')
                b = Field(name='c')

        with pytest.raises(AttributeError):
            class T1(Table):
                # `has_field` - метод в `Table`, нельзя его заменять на `field`
                has_field = Field()

        class AField(Field):
            a = ''

        with pytest.raises(AttributeError):
            class FieldDerivedHack(Table):
                # наследование Field не помогает обойти это
                has_field = AField()

        def f(_):
            return False

        class OverridenHasField(Table):
            a = Field()
            # переопределить метод на другой, даже таким своеобразным образом
            # можно. Запреты распространяются только на поля, т.к. это можно
            # сделать случайно
            has_field = f

        assert not OverridenHasField.has_field('a')

        with pytest.raises(AttributeError):
            class T2(Table):
                # `__layout__` - специальный атрибут `Table`,
                # нельзя его заменять на `field`
                has_field = Field()

        class T3(Table):
            # так метод `has_field` остается на месте, и нет ограничения на
            # название поля в базе данных
            hf = Field(name='has_field')

        assert T3.has_field('has_field')
        assert T3.get_field('has_field') == Field(name='has_field', alias='hf')

        class BaseTable(Table):
            my_special_arg = 10

            def f(self):
                pass

        with pytest.raises(AttributeError):
            class DerivedFromBase1(BaseTable):
                # добавляя новые атрибуты (не `Field`) в свои таблицы, можно не
                # беспокоится, что их затрут `field`-ами
                my_special_arg = Field()

        with pytest.raises(AttributeError):
            class DerivedFromBase2(BaseTable):
                # добавляя новые методы в свои таблицы, можно не
                # беспокоится, что их затрут `field`-ами
                f = Field()

        # все "магические" имена атрибутов классов нельзя использовать для
        # для задания `field`
        with pytest.raises(AttributeError):
            class T3(Table):
                __fields__ = Field()

        with pytest.raises(AttributeError):
            class T4(Table):
                __reserved_field_names__ = Field()

        with pytest.raises(AttributeError):
            class T5(Table):
                __f__ = Field()

    def test_inheritance_fails(self):
        class Base1(Table):
            a = Field()

        with pytest.raises(AttributeError):
            class Derived1(Base1):
                # тут не должно произойти неявного переопределения
                # поля `a` из таблицы `Base`
                f1 = Field(name='a')

        class Base2(Table):
            a = Field(name='b')

        with pytest.raises(AttributeError):
            class Derived2(Base2):
                # тут не должно произойти неявного переопределения
                # поля `b` из таблицы `Base2`
                b = Field()

        with pytest.raises(AttributeError):
            class Derived3(Base2):
                # тут получается дубль по имени поля с Base2.a
                c = Field(name='b')

    def test_inheritance(self):
        class OtherField(Field):
            pass

        class Base(Table):
            a = Field()
            aa = Field()
            b = Field(name='bb')
            bb = Field(name='b_b')
            c = Field(default_value=10)
            cc = Field(default_value=10)

        class Derived(Base):
            aa = OtherField()
            bb = OtherField(name='bbb')
            cc = Field(default_value=20)
            d = Field()

        assert Base.aa == Field(name='aa', alias='aa')
        assert Base.bb == Field(name='b_b', alias='bb')
        assert Base.cc == Field(name='cc', alias='cc', default_value=10)

        assert Derived.aa == OtherField(name='aa', alias='aa')
        assert Derived.bb == OtherField(name='bbb', alias='bb')
        assert Derived.cc == Field(name='cc', alias='cc', default_value=20)
        assert Derived.d == Field(name='d', alias='d')

        assert len(list(Base.fields())) == 6
        assert len(list(Base.field_names())) == 6
        assert len(set(Base.field_names())) == 6
        assert len(list(Derived.fields())) == 7
        assert len(list(Derived.field_names())) == 7
        assert len(set(Derived.field_names())) == 7

    def test_simple_multiple_inheritance(self):
        class SimpleBase1(Table):
            a = Field()

        class SimpleBase2(Table):
            b = Field()

        class SimpleDerived(SimpleBase1, SimpleBase2):
            c = Field()

        expected = [
            Field(name='a', alias='a'),
            Field(name='b', alias='b'),
            Field(name='c', alias='c'),
        ]
        assert list(SimpleDerived.fields()) == expected

    def test_simple_multiple_inheritance_overrides(self):
        class SimpleBase1(Table):
            a = Field()

        class SimpleBase2(Table):
            a = Field(name='b')

        class SimpleDerived(SimpleBase1, SimpleBase2):
            c = Field()

        expected = [
            Field(name='b', alias='a'),
            Field(name='c', alias='c'),
        ]
        assert list(SimpleDerived.fields()) == expected

    def test_multiple_inheritance_fails(self):
        class SimpleBase1(Table):
            a = Field()

        class SimpleBase2(Table):
            b = Field(name='a')

        with pytest.raises(AttributeError):
            class SimpleDerived(SimpleBase1, SimpleBase2):
                c = Field()

    def test_field_order(self):
        class T(Table):
            one = Field()
            two = Field()
            three = Field()

        assert list(T.field_names()) == ['one', 'three', 'two']

        class D(Table):
            one = Field(name='1')
            two = Field(name='12')
            three = Field(name='5')

        assert list(D.field_names()) == ['1', '12', '5']

        class C(T):
            dwa = Field(name='dwa')

        assert list(C.field_names()) == ['dwa', 'one', 'three', 'two']

    def test_get_etl_service(self):
        assert SimpleTable.get_layout_prefix() == 'test_dmp_suite'

    def test_get_etl_service_with_custom_layout(self):
        class TestTableWithLayout(Table):
            __layout__ = OdsLayout(source='mdb', name='driver', prefix_key='custom')

        assert TestTableWithLayout.get_layout_prefix() == 'custom'

    def test_get_sla(self):
        sla = Sla(CTL_LAST_SYNC_DATE, warn_lag=timedelta(seconds=42))

        class TestTableWithSLa(Table):
            __sla__ = sla

        assert isinstance(TestTableWithSLa.get_sla(), Iterable)
        assert list(TestTableWithSLa.get_sla()) == [sla]

    def test_get_sla_list(self):
        sla_list = [
            Sla(CTL_LAST_SYNC_DATE, warn_lag=timedelta(seconds=24)),
            Sla(CTL_LAST_LOAD_DATE, crit_lag=timedelta(seconds=42))
        ]

        class TestTableWithSLa(Table):
            __sla__ = sla_list

        assert isinstance(TestTableWithSLa.get_sla(), Iterable)
        assert list(TestTableWithSLa.get_sla()) == sla_list

    def test_get_empty_sla(self):
        class TestTableWOSLa(Table):
            ...

        assert TestTableWOSLa.get_sla() is None


def test_entity_name_validator_ok():
    LayeredLayout('layer', 'name', 'groups1-groups2', 'service')
    LayeredLayout('layer', 'name_1')
    OdsLayout(source='mdb', name='driver')
    OdsLayout(name='driver', domain=test_domain)


@pytest.mark.parametrize('layer, name, groups, service, domain', [
    ('layer^', 'name%', None, None, None),
    ('lay.er', 'name', None, None, None),
    ('lay.er', ' ', None, None, None),
    ('layer', 'name', 'gp/gp', None, None),
    ('layer', 'name', 'gpgp', 'a%', None),
    ('1layer', 'name', 'gpgp', 'a', None),
    ('123', 'name', 'gpgp', 'a', None),
    ('layer', 'name', 'lvl1/lvl2', 'a', None),
    ('layer', 'name', 'lvl', 'a', test_domain),
])
def test_entity_name_validator_raises(layer, name, groups, service, domain):
    with pytest.raises(DWHError):
        LayeredLayout(layer, name, groups, service, domain)


def test_common_layout():
    class CommonTestLayout(OdsLayout):
        domain = test_domain
        prefix_key = 'test_layout'

    # проверяем, что domain прорастает из класса
    test_layout = CommonTestLayout(name='test_name')
    assert test_layout.domain == test_domain

    # при указание домена в консрукторе должен завалиться
    with pytest.raises(ValidateError):
        CommonTestLayout(name='test_name', domain=test_domain)

    with pytest.raises(ValidateError):
        CommonTestLayout(name='test_name', prefix_key='tst_service')


class Usual(GPTable):
    __layout__ = OdsLayout(name="some_name", source="some_source")
    field_string1 = String()
    field_int1 = Int()


class Mixin:
    field_string2 = String()
    field_int2 = Int()


class MixinWDuplicates:
    field_string1 = String()
    field_int1 = Int()


class MixinWMeta(metaclass=TableMeta):
    field_string2 = String()
    field_int2 = Int()


class MixinInherited(Mixin, GPTable):
    __layout__ = OdsLayout(name="some_name", source="some_source")


class MixinUsualInherited(Mixin, Usual, GPTable):
    __layout__ = OdsLayout(name="some_name", source="some_source")


class MixinWDuplicatesUsualInherited(MixinWDuplicates, Usual, GPTable):
    __layout__ = OdsLayout(name="some_name", source="some_source")


class MixinWMetaInherited(MixinWMeta, GPTable):
    __layout__ = OdsLayout(name="some_name", source="some_source")


class MixinWMetaUsualInherited(MixinWMeta, Usual, GPTable):
    __layout__ = OdsLayout(name="some_name", source="some_source")


@pytest.mark.parametrize(
    'table, fields',
    [
        (MixinInherited, ("field_string2", "field_int2")),
        (MixinUsualInherited, ("field_string1", "field_int1", "field_string2", "field_int2")),
        (MixinWDuplicatesUsualInherited, ("field_string1", "field_int1")),
        (MixinWMetaInherited, ("field_string2", "field_int2")),
        (MixinWMetaUsualInherited, ("field_string1", "field_int1", "field_string2", "field_int2")),
    ],
)
def test_arbitrary_table_inheritance(table, fields):
    """убедимся, что таблица, наследуемая от:
     - произвольного класса
     - класса с указанием метакласса TableMeta
     - обычного класса и обоих перечисленных
    получает правильные наборы филдов в каждом случае"""
    assert sorted(table.field_names()) == sorted(fields)


@pytest.mark.parametrize('table_type', [yt.YTTable, gp.GPTable, ch.CHTable])
@pytest.mark.parametrize('f1,f2', [
        (yt.Date(sort_key=True), gp.BigInt()),
        (yt.Date(), ch.Date()),
        (gp.Int(), ch.Int()),
    ]
)
def test_database_validation_field(table_type, f1, f2):
    with pytest.raises(TypeError):
        class DummyTable(table_type):
            field_one = f1
            field_two = f2


@pytest.mark.parametrize(
    'table_type,partition_scale,field', [
        (yt.YTTable, gp.MonthPartitionScale(partition_key='date'), yt.Date()),
        (gp.GPTable, yt.YearPartitionScale(partition_key='date'), gp.Date()),
    ]
)
def test_database_validation_partition_scale(table_type, partition_scale, field):
    with pytest.raises(TypeError):
        class DummyTable(table_type):
            __partition_scale__ = partition_scale
            date = field


@pytest.mark.parametrize(
    'table_type,location,field', [
        (yt.YTTable, gp.ExternalGPLocation, yt.Date()),
        (ch.CHTable, yt.NotLayeredYtLocation, ch.Date()),
        (gp.GPTable, ch.CHLocation, gp.Date()),
    ]
)
def test_database_validation_location(table_type, location, field):
    with pytest.raises(TypeError):
        class DummyTable(table_type):
            __location_cls__ = location
            date = field


def test_validatin_with_inheritance():
    class OneObject(DBObject):
        pass

    class TwoObject(DBObject):
        pass

    class OneField(OneObject, Field):
        pass

    class OneTable(OneObject, Table):
        pass

    class TwoField(TwoObject, Field):
        pass

    class TwoTable(TwoObject, Table):
        pass

    with pytest.raises(TypeError):
        class _SomeTable1(OneTable):
            field = TwoField()

    class _CorrectTable(OneTable):
        field_1 = OneField()

    class _WrongBase(TwoTable):
        field_2 = TwoField()

    # должен бросать исключение при наследовании
    # от таблицы несовместимой бд.
    with pytest.raises(TypeError):
        class _SomeTable2(_WrongBase, _CorrectTable):
            pass

    class _WrongMixin:
        field_2 = TwoField()

    class _RepairMixin:
        field_2 = OneField()

    # должен бросать исключение если Mixin
    # содержит несовместимый атрибут.
    with pytest.raises(TypeError):
        class _SomeTable3(_WrongMixin, _CorrectTable):
            pass

    # НЕ должен бросать исключение если
    # несовместимый атрибут одного из
    # Mixin'ов скрыт по MRO, т.к. атрибут
    # все равно в таблице не окажется.
    class _SomeTable4(_RepairMixin, _WrongMixin, _CorrectTable):
        pass


def test_build_new_layout():
    layout = OdsLayout(source='mdb', name='driver', prefix_key='custom')
    new_layout = LayeredLayout(layer='ods', group='mdb', name='new_driver', prefix_key='custom')

    assert new_layout == build_new_layout(layout, new_name='new_driver')

    layout = OdsLayout(source='mdb', name='driver', prefix_key='custom')
    new_layout = LayeredLayout(layer='ods', group='new_mdb', name='new_driver', prefix_key='custom')

    assert new_layout == build_new_layout(layout, new_name='new_driver', new_group='new_mdb')

    layout = OdsLayout(source='mdb', name='driver', prefix_key='custom')
    new_layout = LayeredLayout(layer='ods', group='new_mdb', name='new_driver', prefix_key='new_custom')

    assert new_layout == build_new_layout(layout, new_name='new_driver', new_group='new_mdb', new_prefix_key='new_custom')

    layout = OdsLayout(source='mdb', name='driver', prefix_key='custom')
    new_layout = LayeredLayout(layer='dds', group='new_mdb', name='new_driver', prefix_key='new_custom')

    assert new_layout == build_new_layout(layout, new_layer='dds', new_name='new_driver', new_group='new_mdb', new_prefix_key='new_custom')

    layout = OdsLayout(source='mdb', name='driver', prefix_key='custom')
    new_layout = LayeredLayout(layer='dds', name='new_driver', prefix_key='new_custom', domain=test_domain)

    assert new_layout == build_new_layout(layout, new_domain=test_domain, new_layer='dds', new_name='new_driver', new_prefix_key='new_custom')

    with pytest.raises(ValidateError):
        build_new_layout(layout, new_domain=test_domain, new_group='new_mdb')
