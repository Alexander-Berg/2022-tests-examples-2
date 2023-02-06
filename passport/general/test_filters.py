from passport.backend.tools.metrics.metrics import if_matches


def test_empty():
    assert if_matches({}, {'foo': 'bar'})


def test_not():
    filter_rule = {
        'key1': ([], '1'),
    }
    assert if_matches(
        filter_rule,
        {'key1': '2'},
    )
    assert not if_matches(
        filter_rule,
        {'key1': '1'},
    )


def test_and():
    filter_rule = {
        'key1': ('1', []),
        'key2': ('2', []),
    }
    # всё на месте и совпадает
    assert if_matches(
        filter_rule,
        {'key1': '1', 'key2': '2'},
    )
    # всё на месте и совпадает + есть лишняя пара ключ-значение
    assert if_matches(
        filter_rule,
        {'key1': '1', 'key2': '2', 'key3': '3'},
    )
    # нет одного из ключей
    assert not if_matches(
        filter_rule,
        {'key1': '1'},
    )
    # нет одного из ключей
    assert not if_matches(
        filter_rule,
        {'key2': '2'},
    )
    # искомых ключей нет => не совпадение
    assert not if_matches(
        filter_rule,
        {'key3': '3'},
    )
    # ключи на месте, значения не те => не совпадение
    assert not if_matches(
        filter_rule,
        {'key1': '10', 'key2': '20'},
    )


def test_or():
    filter_rule = {
        'foo': (['bar', 'zar'], []),
    }
    # всё на месте и совпадает
    assert if_matches(
        filter_rule,
        {'foo': 'bar'}
    )
    assert if_matches(
        filter_rule,
        {'foo': 'zar'}
    )
    assert not if_matches(
        filter_rule,
        {'foo': 'xar'}
    )


def test_complex():
    filter_rule = {
        'key_odd': (['1', '3'], ['5']),
        'key_even': (['2', '4'], ['6']),
    }
    assert if_matches(
        filter_rule,
        {
            'key_odd': '1',
            'key_even': '2',
        },
    )
    assert if_matches(
        filter_rule,
        {
            'key_odd': '3',
            'key_even': '4',
        },
    )
    assert not if_matches(
        filter_rule,
        {
            'key_odd': 'wrong',
            'key_even': 'also_wrong',
        },
    )
    assert not if_matches(
        filter_rule,
        {
            'key_odd': '1',
            'key_even': '6',
        },
    )
    assert not if_matches(
        filter_rule,
        {
            'key_odd': '5',
            'key_even': '4',
        },
    )
    assert not if_matches(
        filter_rule,
        {
            'key_odd': '5',
            'key_even': '6',
        },
    )


def test_not_empty():
    filter_rule = {
        'key_exists': ([], []),
    }
    assert if_matches(
        filter_rule,
        {
            'key_exists': 'foobar',
        },
    )
    assert not if_matches(
        filter_rule,
        {
            'another_key': 'foobar',
        },
    )
