# pylint: disable=redefined-outer-name
import pytest

from client_ok import components as ok
import client_ok.generated.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['client_ok.generated.pytest_plugins']


@pytest.fixture
def set_custom_token(simple_secdist):
    def wrapper(token):
        simple_secdist['settings_override'].update(
            {ok.OKClient.OK_OAUTH_SECDIST_KEY: token},
        )

    return wrapper
