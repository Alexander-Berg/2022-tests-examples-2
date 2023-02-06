
from libstall.pg.dbh import sqlt

def test_sqlt(tap):
    tap.plan(5)
    tap.ok(sqlt, 'импортирован')

    sql, bindvars = sqlt('tests/select_variable.sqlt', {'variable': 'test'})

    tap.like(sql, r'SELECT\s+\$1::TEXT', 'результат sql')
    tap.eq(bindvars, ['test'], 'переменные')

    tap.ok(sql, 'sql отрендерен')
    tap.ok(bindvars, 'bindvars заполнены')
    tap()
