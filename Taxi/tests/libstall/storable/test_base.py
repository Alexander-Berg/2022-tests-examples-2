# pylint: disable=blacklisted-name

from mouse import Has
from libstall import json_pp as json
from libstall.model.storable import Base


def test_eq(tap):
    with tap.plan(7, 'Стандортное сравнение объектов'):

        class Test(Base):
            foo = Has(types=str, default='xyz')
            bar = Has(types=int, default=987)

        class Test2(Test):
            pass

        tap.eq(
            Test({'foo': 'abc', 'bar': 123}),
            Test({'bar': 123, 'foo': 'abc'}),
            'Одинаковые объекты'
        )
        tap.eq(
            Test({'foo': 'abc', 'bar': 123}),
            {'foo': 'abc', 'bar': 123},
            'Простые типы тоже сравнимы'
        )

        tap.ne(
            Test({'foo': 'abc', 'bar': 123}),
            Test({'foo': 'abcd', 'bar': 123}),
            'Разные значения'
        )
        tap.ne(
            Test({'foo': 'abc', 'bar': 123}),
            Test({'foo': 'abc', 'bar': 1234}),
            'Разные значения'
        )
        tap.ne(
            Test({'foo': 'abc', 'bar': 123}),
            Test({'foo': 'abc'}),
            'Разные значения по дефолту'
        )

        tap.ne(
            Test({'foo': 'abc', 'bar': 123}),
            Test2({'foo': 'abc', 'bar': 123}),
            'Объекты разных типов'
        )

        tap.ne(
            Test({'foo': 'abc', 'bar': 123}),
            '{"bar": 123, "foo": "abc"}',
            'Несравнимые объекты без corce'
        )


def test_eq_coerce(tap):
    with tap.plan(1, 'Стандортное сравнение объектов при определении coerce'):

        class Test(Base):
            foo = Has(types=str, default='xyz')
            bar = Has(types=int, default=987)

            @classmethod
            def coerce(cls, value):
                if isinstance(value, str):
                    return cls(json.loads(value))
                return cls(value)

        tap.eq(
            Test({'foo': 'abc', 'bar': 123}),
            '{"bar": 123, "foo": "abc"}',
            'Одинаковые объекты'
        )
