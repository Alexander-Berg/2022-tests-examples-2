import pytest

import nanny_yp.components
import nanny_yp.generated.pytest_init  # noqa: E501 pylint: disable=no-name-in-module, import-error

pytest_plugins = ['nanny_yp.generated.pytest_plugins']


@pytest.fixture
def nanny_yp_client(library_context):
    return nanny_yp.components.NannyYpClient(
        library_context, {'base_url': 'base_url'}, None,
    )
