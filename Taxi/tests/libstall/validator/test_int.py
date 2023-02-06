from libstall.model import validator


def test_int(tap):
    tap.plan(3)
    tap.ok(not validator.integer('hello'), 'не число')
    tap.ok(validator.integer(11), 'целое число')
    tap.ok(validator.integer(11.0), 'float, но целое число')
    tap()
