from libstall.model import validator


def test_enum(tap):
    with tap.plan(2, 'Скаляр'):
        tap.ok(validator.enum('hello', ('hello', 'world')), 'входит')
        tap.ok(not validator.enum('hello', ('foo', 'bar')), 'не входит')


def test_list(tap):
    with tap.plan(2, 'В списках тестируем каждый элемент'):
        tap.ok(
            validator.enum(
                ['hello', 'world'],
                ('hello', 'world')
            ),
            'входит'
        )
        tap.ok(
            not validator.enum(
                ['hello', 'world'],
                ('foo', 'bar')
            ),
            'не входит'
        )
