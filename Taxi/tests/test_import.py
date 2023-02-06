def test_load(tap):
    tap.plan(1)
    tap.import_ok('ymlcfg')
    tap.done_testing()
