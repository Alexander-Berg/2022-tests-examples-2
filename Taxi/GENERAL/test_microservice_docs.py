import difflib
import os
import pathlib
import tempfile
import typing

import pytest

from taxi_schemas.docs_tools import microservice_docs

STATIC_DIR = (
    pathlib.Path(__file__).parent / 'static' / 'test_microservice_docs'
)
OUTPUT_DIRNAME = 'output_dir'


@pytest.fixture(name='chdir')
def _chdir():
    curdir = os.path.curdir
    yield os.chdir
    os.chdir(curdir)


def compare_files(
        first_filename: pathlib.Path, second_filename: pathlib.Path,
) -> str:
    with open_file(first_filename) as first_file:
        with open_file(second_filename) as second_file:
            diff_generator = difflib.unified_diff(
                first_file.readlines(),
                second_file.readlines(),
                fromfile=str(first_filename),
                tofile=str(second_filename),
            )
    return ''.join(line for line in diff_generator)


def open_file(path: pathlib.Path) -> typing.IO:
    if path.exists():
        return path.open()
    return tempfile.TemporaryFile('r+t')


def get_all_relpaths(path: pathlib.Path) -> typing.Set[pathlib.Path]:
    all_files = path.rglob('*')
    return set(
        filepath.relative_to(path)
        for filepath in all_files
        if filepath.is_file()
    )


def compare_directories(
        first_dir: pathlib.Path, second_dir: pathlib.Path,
) -> None:
    first_relpaths = get_all_relpaths(first_dir)
    second_relpaths = get_all_relpaths(second_dir)
    relpaths = first_relpaths | second_relpaths
    diff_array = []

    for relpath in relpaths:
        first_path = first_dir.joinpath(relpath)
        second_path = second_dir.joinpath(relpath)
        diff_array.append(compare_files(first_path, second_path))

    assert ''.join(diff_array) == ''


@pytest.mark.parametrize('name', ['swagger', 'openapi', 'non_gen_cases'])
@pytest.mark.nofilldb()
def test_docs_render(tmpdir, chdir, name):
    chdir(tmpdir)
    test_name = STATIC_DIR / name

    repo_dir = test_name / 'repo'
    render_dir = test_name / OUTPUT_DIRNAME
    output_dir = pathlib.Path(tmpdir.join(OUTPUT_DIRNAME))
    args = ['--output-dir', str(output_dir), '--repo-dir', str(repo_dir)]

    microservice_docs.main([*args])

    compare_directories(output_dir / 'Repo', render_dir)
