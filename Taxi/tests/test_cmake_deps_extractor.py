import os
import pathlib
from typing import Dict
from typing import List
from typing import NamedTuple

import pytest

import cmake_deps_extractor
from taxi_buildagent import utils

DEPEND_INTERNAL = 'depend.internal'
EXPECTED_YAML = 'expected.yaml'
ROOT_DIRS_YAML = 'root-dirs.yaml'


class Params(NamedTuple):
    lines: List[str]
    expected_result: Dict[str, List[str]]


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(Params(lines=[], expected_result={}), id='empty source'),
        pytest.param(
            Params(lines=['', ' ', '\t'], expected_result={}), id='empty',
        ),
        pytest.param(
            Params(
                lines=['# first commentary', '# second', '# 3rd', ''],
                expected_result={},
            ),
            id='comments',
        ),
        pytest.param(
            Params(
                lines=['# first commentary', '# second', '# 3rd', ''],
                expected_result={},
            ),
            id='comments empty',
        ),
        pytest.param(
            Params(
                lines=[
                    'services/pilorama/CMakeFiles/yandex-taxi-pilorama.dir'
                    '/src/components.cpp.o',
                    ' ../libraries/basic-http-client/include/clients/http.hpp',
                ],
                expected_result={},
            ),
            id='unknown root-dir',
        ),
        pytest.param(
            Params(
                lines=[
                    'services/pilorama/CMakeFiles/yandex-taxi-pilorama.dir'
                    '/src/components.cpp.o',
                    ' ../libraries/basic-http-client/include/clients/http.hpp',
                    ' /taxi/uservices/services/pilorama/src/components.cpp',
                ],
                expected_result={
                    'services/pilorama/src/components.cpp': [
                        'libraries/basic-http-client/include/clients/http.hpp',
                    ],
                },
            ),
            id='known root-dir',
        ),
        pytest.param(
            Params(
                lines=[
                    'services/pilorama/CMakeFiles/yandex-taxi-pilorama.dir'
                    '/src/components.cpp.o',
                    ' /taxi/uservices/services/pilorama/src/balancers.hpp',
                    ' ../services/pilorama/src/components.cpp',
                ],
                expected_result={
                    'services/pilorama/src/components.cpp': [
                        'services/pilorama/src/balancers.hpp',
                    ],
                },
            ),
            id='unknown root-dir root files',
        ),
        pytest.param(
            Params(
                lines=[
                    'services/pilorama/CMakeFiles/yandex-taxi-pilorama.dir'
                    '/src/components.cpp.o',
                    ' /taxi/uservices/build-integration/services/pilorama/'
                    'src/balancers.hpp',
                    ' /taxi/uservices/services/pilorama/src/components.cpp',
                ],
                expected_result={
                    'services/pilorama/src/components.cpp': [
                        'build-integration/services/pilorama/src/'
                        'balancers.hpp',
                    ],
                },
            ),
            id='build integration dir',
        ),
        pytest.param(
            Params(
                lines=[' /taxi/uservices/services/pilorama/src/balancers.hpp'],
                expected_result={},
            ),
            id='no-header',
        ),
        pytest.param(
            Params(
                lines=[
                    'services/pilorama/CMakeFiles/yandex-taxi-pilorama.dir'
                    '/src/components.cpp.o',
                ],
                expected_result={},
            ),
            id='header only',
        ),
    ],
)
def test_parsing(params: Params):
    lines = params.lines

    builder = cmake_deps_extractor.DependencyGraphBuilder(
        pathlib.Path(), 'build-integration', '/taxi/uservices',
    )
    result = builder.extract_dependencies_from_lines(lines)
    assert result == params.expected_result


def test_files() -> None:
    module_path = os.path.abspath(__file__)
    module_name = os.path.splitext(os.path.basename(module_path))[0]
    test_module_dir = os.path.dirname(module_path)
    cases_dir = os.path.join(test_module_dir, 'static', module_name)
    if not os.path.isdir(cases_dir):
        return

    test_dirs: List[str] = []
    for _root, dirs, _files in os.walk(cases_dir):
        test_dirs = list(dirs)
        break

    for test_dir in test_dirs:
        test_path = os.path.join(cases_dir, test_dir)
        with open(os.path.join(test_path, DEPEND_INTERNAL)) as inp:
            file_lines = inp.read().splitlines()
        expected_result = utils.load_yaml(
            os.path.join(test_path, EXPECTED_YAML),
        )

        builder = cmake_deps_extractor.DependencyGraphBuilder(
            pathlib.Path(test_path), 'build-integration', '/taxi/uservices',
        )
        result = builder.extract_dependencies_from_lines(file_lines)
        assert result == expected_result
