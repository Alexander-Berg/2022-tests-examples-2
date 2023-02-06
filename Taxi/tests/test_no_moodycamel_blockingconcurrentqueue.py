ERROR_MSG = (
    'Usage of "moodycamel::BlockingConcurrentQueue" is forbidden, because '
    'it uses sync primitives from STL. Use "userver::concurrent::MpmcQueue" '
    'instead.\nDetails:\n{output}\n'
)


def test_forbidden_include(code_search) -> None:
    # clang-format formats those cases
    # "# include <moodycamel/blockingconcurrentqueue.h>"
    # "#include<moodycamel/blockingconcurrentqueue.h>"
    # "#include  <moodycamel/blockingconcurrentqueue.h>"
    # "#include \\\n<moodycamel/blockingconcurrentqueue.h>"
    # into
    # "#include <moodycamel/blockingconcurrentqueue.h>"
    files = code_search(
        '#include <moodycamel/blockingconcurrentqueue.h>',
        ['libraries', 'services'],
    )
    assert not files, ERROR_MSG.format(output='\n'.join(files))


def test_forbidden_queue(code_search) -> None:
    files = code_search(
        'moodycamel::BlockingConcurrentQueue', ['libraries', 'services'],
    )
    assert not files, ERROR_MSG.format(output='\n'.join(files))
