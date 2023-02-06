from libstall.util import skip_empty

def test_skip_empty(tap):
    tap.plan(12)

    tap.eq(skip_empty(), [], 'Ничего не передано')
    tap.eq(skip_empty([1, 2, 3]), [1, 2, 3], 'Нет none')
    tap.eq(skip_empty([]), [], 'пустой массив')
    tap.eq(skip_empty([1, 2, 3, None]), [1, 2, 3], 'None в конце')
    tap.eq(skip_empty([None, 1, 2, 3]), [1, 2, 3], 'None в начале')
    tap.eq(skip_empty([None]), [], 'Только None')

    tap.eq(skip_empty(), [], 'Ничего не передано')
    tap.eq(skip_empty([1, 2, 3]), [1, 2, 3], 'Нет none')
    tap.eq(skip_empty([]), [], 'пустой массив')
    tap.eq(skip_empty([1, 2, 3, '']), [1, 2, 3], 'Empty в конце')
    tap.eq(skip_empty(['', 1, 2, 3]), [1, 2, 3], 'Empty в начале')
    tap.eq(skip_empty(['']), [], 'Только Empty')
    tap()



