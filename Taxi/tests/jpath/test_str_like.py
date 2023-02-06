from ymlcfg.jpath import str_like

def test_like(tap):
    with tap.plan(14):
        tap.ok(str_like('abc', 'abc'), 'точное соответствие')
        tap.ok(not str_like('abc', 'ab'), 'несоответствие')
        tap.ok(str_like('abc', '*'), 'звездочка')
        tap.ok(str_like('abc', 'a*'), 'звездочка в конце')
        tap.ok(str_like('abc', '*c'), 'звездочка в начале')

        tap.ok(str_like('abc', 'a?c'), 'вопросик')
        tap.ok(str_like('abc', '[Aa]bc'), 'набор символов')
        tap.ok(str_like('abc', '[^c]bc'), 'антинабор символов')
        tap.ok(str_like('abc', '[A^a]bc'), 'набор символов с ^')


        tap.ok(str_like('a..bc', 'a..bc'), 'символ . в паттерне')
        tap.ok(not str_like('aaabc', 'a..bc'), 'символ . в паттерне: неуспех')


        tap.ok(str_like('a^bc', 'a^*'), 'символ ^ в паттерне')
        tap.ok(str_like('^bc', '^b*'), 'символ ^ в начале паттерна')


        tap.ok(not str_like('abc', '[A^abc'), 'невалидный набор')
