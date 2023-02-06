import ymlcfg


def test_set(tap, test_cfg_dir):
    with tap.plan(12):

        cfg = ymlcfg.loader(test_cfg_dir('update'))

        tap.ok(cfg, 'Config loaded')

        tap.eq(cfg('hello'), 'world', 'start value')


        tap.eq(cfg(op=[['set', 'hello', 'World']]), 1, 'set')
        tap.eq(cfg('hello'), 'World', 'new value')

        tap.eq(cfg(op=[['prepend', 'hello', ', ']]), 1, 'prepend')
        tap.eq(cfg('hello'), ', World', 'new value')

        tap.eq(cfg(op=[['append', 'hell*', '!']]), 1, 'append starred')
        tap.eq(cfg('hello'), ', World!', 'new value')

        tap.eq(cfg(op=[['lreplace', 'hello', ', ', '']]), 1, 'lreplace')
        tap.eq(cfg('hello'), 'World!', 'new value')

        tap.ok(cfg.reload(), 'reloaded')
        tap.eq(cfg('hello'), 'world', 'old value')
