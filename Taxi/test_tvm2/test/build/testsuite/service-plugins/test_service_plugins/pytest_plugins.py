import pathlib
import sys


pytest_plugins = [
    # service.yaml#/pytest/pytest-plugins
    'tests_plugins.mock_statistics',
]


def _root_source_dir():
    return pathlib.Path(__file__).parent.joinpath('../../../..')


def _add_libraries_paths():
    sys.path.extend([
        str(_root_source_dir().joinpath('libraries/codegen-clients/testsuite')),
        str(_root_source_dir().joinpath('libraries/codegen-clients/testsuite/static/default')),
        str(_root_source_dir().joinpath('libraries/codegen/testsuite')),
        str(_root_source_dir().joinpath('libraries/codegen/testsuite/static/default')),
        str(_root_source_dir().joinpath('libraries/solomon-stats/testsuite')),
        str(_root_source_dir().joinpath('libraries/solomon-stats/testsuite/static/default')),
        str(_root_source_dir().joinpath('libraries/tvm2-http-client/testsuite')),
        str(_root_source_dir().joinpath('libraries/tvm2-http-client/testsuite/static/default')),
        str(_root_source_dir().joinpath('libraries/tvm2/testsuite')),
        str(_root_source_dir().joinpath('libraries/tvm2/testsuite/static/default')),
    ])


_add_libraries_paths()
