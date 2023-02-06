from stall.backend_version import version

def test_version(tap):
    with tap.plan(1, 'тест версии'):
        tap.ok(version, 'Версия есть')

