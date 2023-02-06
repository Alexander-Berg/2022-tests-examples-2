# pylint: disable=redefined-outer-name
import pytest

from client_sup import components as sup
import client_sup.generated.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['client_sup.generated.pytest_plugins']


@pytest.fixture
def set_custom_token(simple_secdist):
    def wrapper(token):
        simple_secdist['settings_override'].update(
            {sup.SUPClient.SOUP_OAUTH_SECDIST_KEY: token},
        )

    return wrapper
