def test_banned_nolint(code_search) -> None:
    files = code_search('NOLINT', ['libraries', 'services'])
    assert not files, (
        'Error: taxi nolint validator detected NOLINT usage:\n{}\n'
        'See https://nda.ya.ru/t/mJQ0s_ky3Vvo9h for more info\n'
        ''.format('\n'.join(files))
    )
