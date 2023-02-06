from libstall.model import validator


def test_time(tap):
    with tap.plan(5):
        tap.ok(validator.time('10:20:30'),  'полное время')
        tap.ok(validator.time('10:20'),     'время без секунд')

        tap.ok(not validator.time(None),    'не время')
        tap.ok(not validator.time(''),      'не время')
        tap.ok(not validator.time('hello'), 'не время')
