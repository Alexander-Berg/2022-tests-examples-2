from libstall.model import coerces


def test_jsonhash(tap):
    tap.plan(2)
    d = coerces.json_hash('{"a": "b"}')
    tap.isa_ok(d, dict, 'Конверсия простого хеша')
    tap.eq(d, {'a': 'b'}, 'Значение')
    tap()
