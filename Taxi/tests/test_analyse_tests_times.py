import shutil
from typing import List
from typing import NamedTuple
from typing import Optional

import pytest

import analyse_tests_times


class Params(NamedTuple):
    reports_files: List = []
    expected_output_file: str = 'empty_output.txt'
    limit: Optional[int] = None


@pytest.fixture(name='copy_reports')
def _copy_reports(get_file_path, tmpdir):
    def _copy_reports_impl(reports_files):
        target_dir = str(tmpdir)
        for report_file in reports_files:
            control_path = get_file_path(report_file)
            shutil.copy(control_path, target_dir)
        return target_dir

    return _copy_reports_impl


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(Params(), id='no_reports'),
        pytest.param(
            Params(reports_files=['yandex-taxi-driver-wall_unittest.xml']),
            id='only_unittest',
        ),
        pytest.param(
            Params(
                reports_files=[
                    'junit-blender.xml',
                    'junit-documents.xml',
                    'yandex-taxi-driver-wall_unittest.xml',
                ],
                expected_output_file='all_reports_output.txt',
            ),
            id='several_reports',
        ),
        pytest.param(
            Params(
                reports_files=[
                    'junit-blender.xml',
                    'junit-documents.xml',
                    'yandex-taxi-driver-wall_unittest.xml',
                ],
                limit=3,
                expected_output_file='cut_all_reports_output.txt',
            ),
            id='with_limit',
        ),
    ],
)
def test_analyse(params, copy_reports, load, capsys):
    reports_dir = copy_reports(params.reports_files)
    argv = ['--reports-dir', reports_dir]
    if params.limit is not None:
        argv.extend(['--limit', str(params.limit)])
    analyse_tests_times.main(argv)

    captured = capsys.readouterr()
    expected_output = load(params.expected_output_file)

    assert expected_output == captured.out
    assert captured.err == ''
