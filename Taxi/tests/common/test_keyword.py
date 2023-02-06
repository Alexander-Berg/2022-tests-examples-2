from stall.keyword import keyword, noun

def test_keyword(tap):
    with tap.plan(10):
        for _ in range(10):
            k = keyword()
            tap.ok(k, f'фраза сгенерирована: {k}')

def test_noun(tap):
    with tap.plan(10):
        for _ in range(10):
            k = noun()
            tap.ok(k, f'фраза сгенерирована: {k}')
