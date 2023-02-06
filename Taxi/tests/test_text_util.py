from util.swaggen import text_util


def dist(str_a: str, str_b: str) -> int:
    return text_util.levenshtein_dist(str_a, str_b)


def test_levenshtein_insert():
    assert dist('qwerty', 'aqwerty') == 1
    assert dist('qwerty', 'qwearty') == 1
    assert dist('qwerty', 'qwertya') == 1

    assert dist('qwerty', 'asqwerty') == 2
    assert dist('qwerty', 'qweasrty') == 2
    assert dist('qwerty', 'qwertyas') == 2


def test_levenshtein_replace():
    assert dist('qwerty', 'awerty') == 1
    assert dist('qwerty', 'qwarty') == 1
    assert dist('qwerty', 'qwerta') == 1

    assert dist('qwerty', 'aserty') == 2
    assert dist('qwerty', 'qwasty') == 2
    assert dist('qwerty', 'qweras') == 2


def test_levenshtein_remove():
    assert dist('qwerty', 'werty') == 1
    assert dist('qwerty', 'qwrty') == 1
    assert dist('qwerty', 'qwert') == 1

    assert dist('qwerty', 'erty') == 2
    assert dist('qwerty', 'qwty') == 2
    assert dist('qwerty', 'qwer') == 2
