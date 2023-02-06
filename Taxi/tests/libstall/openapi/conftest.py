import pathlib

import pytest

from libstall import oa


@pytest.fixture
def spec():
    return oa.Spec.from_file(
        pathlib.Path('tests/libstall/openapi/data/petstore.yaml').absolute(),
        validate=True,
    )
