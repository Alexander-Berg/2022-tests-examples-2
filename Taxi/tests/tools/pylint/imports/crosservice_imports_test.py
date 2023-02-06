import pytest
import tools.pylint.imports.linter

# Here I do not check whole linter bc it would require pretty
# cumbersome mocking of imports, so I test only internal function
# that actually checks if path could be imported in crosservice context


@pytest.mark.parametrize(
    'path, paths',
    [
        ('/usr/lib/python3.7/site-packages/flask', set()),
        ('/usr/lib/python3.7/re', set()),
        (None, set()),
        ('setup.py', {'setup.py'}),
        ('taxi_etl/taxi_etl/__init__.py', {'taxi_etl/taxi_etl'}),
    ],
)
def test_valid_import(path, paths):
    tools.pylint.imports.linter.check_import_by_module(path, paths)

    # assert no exception were raised
    assert True


@pytest.mark.parametrize(
    'path, paths',
    [
        ('setup.py', set()),
        ('taxi_etl/taxi_etl/__init__.py', set()),
    ],
)
def test_invalid_import(path, paths):
    with pytest.raises(
        tools.pylint.imports.linter.CrosserviceImportError,
    ):
        tools.pylint.imports.linter.check_import_by_module(path, paths)
