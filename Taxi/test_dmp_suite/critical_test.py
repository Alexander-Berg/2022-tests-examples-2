from dmp_suite.critical import is_critical, critical_flag


def test_critical_section():
    # Проверим, что флаг выставляется
    # только на время выполнения секции

    assert is_critical() is False

    with critical_flag():
        assert is_critical() is True

    assert is_critical() is False
