import ymlcfg


def test_include(tap, test_cfg_dir):
    tap.plan(5)

    cfg = ymlcfg.loader(test_cfg_dir('include'))

    tap.ok(cfg, 'Config loaded')

    tap.eq(cfg('tests_cfg_include_parts_one_json'),
           {'hello': 'I am json'}, 'automap json')
    tap.eq(cfg('one'), {'hello': 'I am json'}, 'hand map json')

    tap.eq(cfg('tests_cfg_include_parts_two_yml'),
           {'hello': 'I am yaml'}, 'automap yaml')
    tap.eq(cfg('two'), {'hello': 'I am yaml'}, 'hand map yaml')

    tap.done_testing()
