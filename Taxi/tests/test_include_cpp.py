CPP_ERROR_MSG = 'You should not include *.cpp files\nDetails:\n{output}\n'
DEFS_IPP_ERROR_MSG = 'You should not include *.ipp of definitions\n{output}\n'


def test_include_cpp(code_search) -> None:
    files = code_search('#include [<"].*\\.cpp[>"]', ['libraries', 'services'])
    assert not files, CPP_ERROR_MSG.format(output='\n'.join(files))


def test_include_definitions_ipp(code_search) -> None:
    files = code_search('#include .*defs/.*\\.ipp', ['libraries', 'services'])
    assert not files, DEFS_IPP_ERROR_MSG.format(output='\n'.join(files))
