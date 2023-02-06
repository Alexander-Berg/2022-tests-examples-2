from typing import List
from typing import NamedTuple

import pytest

from build_scripts import get_strong_depends


class Params(NamedTuple):
    packages_files: List[str]
    expected_depends: str


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                packages_files=['package_info_graph.txt'],
                expected_depends='libyandex-taxi-graph=4083882\n',
            ),
            id='simple case',
        ),
        pytest.param(
            Params(
                packages_files=[
                    'package_info_graph.txt',
                    'package_info_new_graph.txt',
                ],
                expected_depends=(
                    'libpng12-0=1.2.13-4 libyandex-taxi-graph=4083882 '
                    'yandex-taxi-backend-utils=1.0-2\n'
                ),
            ),
            id='two package case',
        ),
        pytest.param(
            Params(
                packages_files=['package_info_graph_no_strong.txt'],
                expected_depends='\n',
            ),
            id='no strong deps case',
        ),
    ],
)
def test_base(commands_mock, load, capsys, params):
    files_iter = iter(params.packages_files)

    @commands_mock('dpkg')
    def mock_dpkg(args, **kwargs):
        return load(next(files_iter))

    get_strong_depends.main(params.packages_files)

    dpkg_calls = mock_dpkg.calls
    assert dpkg_calls == [
        {
            'args': ['dpkg', '--info', package_file],
            'kwargs': {'encoding': 'utf-8', 'stdout': -1},
        }
        for package_file in params.packages_files
    ]
    captured = capsys.readouterr()
    assert captured.out == params.expected_depends
    assert captured.err == ''
