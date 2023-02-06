from libstall.model import validator


def test_timezone(tap):
    with tap.plan(4):
        tap.ok(not validator.timezone('1130'), 'смещение без знака')
        tap.ok(not validator.timezone('+1130'), 'смещение со знаком')
        tap.ok(validator.timezone('Europe/London'), 'IANA')
        tap.ok(not validator.timezone('Europe/SinCity'),
               'несуществующий часовой пояс')
