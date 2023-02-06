from libstall.util import skip_none

def test_skip_none(tap):
    tap.plan(6)

    tap.eq(skip_none(), [], 'Ничего не передано')
    tap.eq(skip_none([1, 2, 3]), [1, 2, 3], 'Нет none')
    tap.eq(skip_none([]), [], 'пустой массив')
    tap.eq(skip_none([1, 2, 3, None]), [1, 2, 3], 'None в конце')
    tap.eq(skip_none([None, 1, 2, 3]), [1, 2, 3], 'None в начале')
    tap.eq(skip_none([None]), [], 'Только None')

    tap()

