import pathlib
import shutil

import pytest

from taxi_linters import taxi_jsonfmt

TEST_DATA_DIR = pathlib.Path(__file__).parent / 'static' / 'json'
PARAMS_TEST_DIR = list(
    zip(
        sorted((TEST_DATA_DIR / 'before').rglob('*')),
        sorted((TEST_DATA_DIR / 'after').rglob('*')),
    ),
)


@pytest.mark.parametrize('file,formatted_file', PARAMS_TEST_DIR)
def test_dump(file, formatted_file, tmp_path):
    tmp_file = tmp_path / file.name
    with open(file) as inp, open(tmp_file, 'w') as out:
        data = taxi_jsonfmt.load(inp)
        taxi_jsonfmt.dump(data, out)
    assert len(list(tmp_path.iterdir())) == 1
    assert tmp_file.read_text() == formatted_file.read_text()


@pytest.mark.parametrize('file,formatted_file', PARAMS_TEST_DIR)
def test_dumps(file, formatted_file):
    with open(file) as inp:
        data = taxi_jsonfmt.load(inp)
    formatted_data = taxi_jsonfmt.dumps(data)
    assert formatted_data == formatted_file.read_text()


@pytest.mark.parametrize('file,formatted_file', PARAMS_TEST_DIR)
def test_load(file, formatted_file):
    with open(file) as inp_file, open(formatted_file) as inp_form_file:
        data = taxi_jsonfmt.load(inp_file)
        formatted_data = taxi_jsonfmt.load(inp_form_file)
    assert data == formatted_data


@pytest.mark.parametrize('file,formatted_file', PARAMS_TEST_DIR)
def test_loads(file, formatted_file):
    data = taxi_jsonfmt.loads(file.read_text())
    formatted_data = taxi_jsonfmt.loads(formatted_file.read_text())
    assert data == formatted_data


@pytest.mark.parametrize('file,formatted_file', PARAMS_TEST_DIR)
def test_format(file, formatted_file, tmp_path):
    temp_copy = tmp_path / file.name
    shutil.copy(file, temp_copy)
    taxi_jsonfmt.format_file(temp_copy)

    # no extra files
    assert len(list(tmp_path.iterdir())) == 1

    assert formatted_file.read_text() == temp_copy.read_text()


@pytest.mark.parametrize('file,formatted_file', PARAMS_TEST_DIR)
def test_format_str(file, formatted_file):
    data = file.read_text()
    assert formatted_file.read_text() == taxi_jsonfmt.format_str(data)
