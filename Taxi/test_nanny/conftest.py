import pytest

import nanny.components
import nanny.generated.pytest_init  # noqa: E501 pylint: disable=no-name-in-module, import-error

pytest_plugins = ['nanny.generated.pytest_plugins']


@pytest.fixture
def nanny_client(library_context):
    return nanny.components.NannyClient(
        library_context, {'base_url': 'base_url'}, None,
    )
