from libstall.util import token


def test_token(tap):
    with tap.plan(10):
        secret = 'Hello'

        gt = token.pack(secret)
        tap.ok(gt, 'пустой токен сгенерирован')
        tap.eq(token.unpack(secret, gt), {}, 'распакован')

        gt = token.pack(None)
        tap.ok(gt, 'None secret токен сгенерирован')
        tap.eq(token.unpack(None, gt), {}, 'распакован')

        gt = token.pack(secret, a='b', c='привет')
        tap.ok(gt, 'Упакован с данными')
        tap.eq(token.unpack(secret, gt),
               {'a': 'b', 'c': 'привет'}, 'распакован')

        tap.eq(token.unpack(secret, None), None, 'не падает None')
        tap.eq(token.unpack(secret, ''), None, 'не падает пустая строка')
        tap.eq(token.unpack(secret, 123), None, 'не падает число')
        tap.eq(token.unpack(secret, 'string'), None, 'не падает строка')
