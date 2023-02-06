import os
import pytest
import modules.files as files


@pytest.yield_fixture(autouse=True, scope="session")
def init_vars():
    fname = "files_test"
    test_var = {"1": 2, "3": [4, "asd"], "5": {1, 12, 35}}
    yield (fname, test_var)
    os.unlink(fname)


@pytest.mark.order0
def test_save_json(init_vars):
    (fname, test_var) = init_vars
    (is_successful, message) = files.save_json(test_var, fname)
    assert is_successful
    assert message == "ok"


@pytest.mark.order1
def test_load_json(init_vars):
    (fname, test_var) = init_vars
    (is_successful, received_var) = files.load_json(fname)
    assert is_successful
    for k, v in test_var.items():
        if isinstance(v, set):
            test_var[k] = list(v)
    assert received_var == test_var


@pytest.mark.order2
def test_sync_files(init_vars):
    (fname, test_var) = init_vars
    (is_successful, received_var) = files.sync_files([fname])
    assert is_successful
    for k, v in received_var.items():
        received_var[k] = eval(v)
    assert received_var == {fname: test_var}
