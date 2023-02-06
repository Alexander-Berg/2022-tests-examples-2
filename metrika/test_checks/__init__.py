from metrika.admin.python.cms.judge.lib.decider.checks import check_setting


def test_check_setting_not_inf_le():
    assert check_setting(1, 2)


def test_check_setting_not_inf_ge():
    assert not check_setting(1, 1)


def test_check_setting_inf():
    assert check_setting(100, -1)
