ERROR_MSG = (
    'Usage of "std::regex" is forbidden due to '
    'a possible stack overflow, use "boost::regex" instead\n'
    'Details:\n{output}\n'
)


def test_forbidden_include(code_search) -> None:
    # clang-format formats those cases
    # "# include <regex>"
    # "#include<regex>"
    # "#include  <regex>"
    # "#include \\\n<regex>"
    # into
    # "#include <regex>"
    files = code_search('#include <regex>', ['libraries', 'services'])
    assert not files, ERROR_MSG.format(output='\n'.join(files))


def test_forbidden_regex(code_search) -> None:
    files = code_search('std::regex', ['libraries', 'services'])
    assert not files, ERROR_MSG.format(output='\n'.join(files))
