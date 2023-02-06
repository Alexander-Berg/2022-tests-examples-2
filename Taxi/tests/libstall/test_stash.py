from libstall.util.stash import Stash

def test_stash(tap):

    tap.plan(4)
    stash = Stash()

    tap.ok(stash, 'инстанцирован')
    tap.eq(stash('a', 'b'), 'b', 'присвоение')
    tap.eq(stash('a'), 'b', 'получить значение')

    tap.eq(stash['a'], 'b', 'квадратными скобками')

    tap()
