import dataclasses
import io

import pytest

import modify_yaml


@dataclasses.dataclass
class Params:
    source: str
    patch: str
    result: str


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                source=(
                    'bar: \n'
                    '   - baz\n'
                    'version: foo\n'
                    'foobar: |\n'
                    '   baz\n'
                ),
                patch='version: bam',
                result=(
                    'bar:\n'
                    '  - baz\n'
                    'version: bam\n'
                    'foobar: |\n'
                    '    baz\n'
                ),
            ),
        ),
    ],
)
def test_modify_yaml(monkeypatch, tmpdir, params: Params):
    filename = tmpdir / 'testfile'
    with open(filename, 'w') as in_file:
        in_file.write(params.source)

    monkeypatch.setattr('sys.argv', ['modify_yaml.py', filename.strpath])

    patch_buffer = io.StringIO(params.patch)
    monkeypatch.setattr('sys.stdin', patch_buffer)

    modify_yaml.main()

    with open(filename, 'r') as in_file:
        result = in_file.read()

    assert result == params.result
