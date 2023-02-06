import collections
import datetime
import difflib
import os
import pathlib
import shutil
from typing import Dict
from typing import Iterable

import freezegun
import pytest

from codegen import utils

DIFF_ERROR_MESSAGE = (
    'run `make create-codegen-tests-data` to update generated files'
)


@pytest.fixture
def stub():
    """Stub fixture.

    Provides function that takes only keyword arguments `**kw` and
    creates stub object which attributes are `kw` keys.

    Usage:

        def test_something(stub):
            obj = stub(x=1, get_x=lambda: return 2)
            assert obj.x == 1
            assert obj.get_x() == 2

    :return: Function that creates stub objects.
    """

    def _stub(**kwargs):
        return collections.namedtuple('Stub', kwargs.keys())(**kwargs)

    return _stub


@pytest.fixture
def load_swagger_schema():
    schemas_path = os.path.join(os.path.dirname(__file__), 'swagger_schemas')

    def load(filename: str):
        return utils.load_yaml(os.path.join(schemas_path, filename))

    return load


@pytest.fixture
def freeze_time():
    def _timestr(now, offset):
        return now.strftime('%Y-%m-%dT%H:%M:%S') + '%+05d' % (offset * 100)

    now = datetime.datetime(2019, 8, 7, 6, 5, 4)
    offset = 3

    with freezegun.freeze_time(
            _timestr(now, offset), tz_offset=offset, ignore=[''], tick=False,
    ) as frozen:
        yield frozen


@pytest.fixture
def dir_comparator(request):
    def read_files(path: str) -> Dict[str, str]:
        result: Dict[str, str] = {}
        for fpath in pathlib.Path(path).rglob('*'):
            if not fpath.is_file() or fpath.is_symlink():
                continue
            result[fpath.relative_to(path).as_posix()] = fpath.read_text()
        return result

    def _dir_comparator(
            generated_dir: str,
            main_test_dir: str,
            *test_dirs: str,
            ignore: Iterable = (),
    ) -> None:
        generated_files = read_files(generated_dir)
        test_files = {}
        static_dir = os.path.join(
            os.path.dirname(request.node.fspath), 'static',
        )
        assert not os.path.isabs(main_test_dir), 'test_dir must be relative'
        abs_test_dir = os.path.join(static_dir, main_test_dir)
        for test_dir in reversed(test_dirs):
            assert not os.path.isabs(test_dir), 'test_dir must be relative'
            test_files.update(read_files(os.path.join(static_dir, test_dir)))

        if os.getenv('CREATE_GENERATED_FILES'):
            shutil.rmtree(abs_test_dir, ignore_errors=True)
            for filename, content in generated_files.items():
                if filename in ignore or test_files.get(filename) == content:
                    continue
                target_filename = os.path.join(abs_test_dir, filename)
                os.makedirs(os.path.dirname(target_filename), exist_ok=True)
                with open(target_filename, 'w') as fin:
                    fin.write(content)

        main_test_files = read_files(abs_test_dir)
        for filename in test_files.keys() & main_test_files.keys():
            if filename in ignore:
                continue
            assert (
                main_test_files[filename] != test_files[filename]
            ), 'duplicate file %s, %s' % (filename, DIFF_ERROR_MESSAGE)
        test_files.update(main_test_files)

        diff = []
        for filename in sorted(generated_files.keys() | test_files.keys()):
            if filename in ignore:
                continue
            if generated_files.get(filename) == test_files.get(filename):
                continue
            fromfile = filename if filename in test_files else ''
            tofile = filename if filename in generated_files else ''
            diff_result = ''.join(
                difflib.unified_diff(
                    a=test_files.get(filename, '').splitlines(True),
                    b=generated_files.get(filename, '').splitlines(True),
                    fromfile=fromfile,
                    tofile=tofile,
                ),
            )
            if not diff_result:
                if filename not in generated_files:
                    diff_result = 'deleted file %s\n' % filename
                elif filename not in test_files:
                    diff_result = 'new file %s\n' % filename
            assert diff_result
            diff.append(diff_result)

        if diff:
            raise ValueError(
                'codegen files differ, %s\n\n%s'
                % (DIFF_ERROR_MESSAGE, '\n'.join(diff)),
            )

    return _dir_comparator
