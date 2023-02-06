import pytest

from typing import Any, Final, Generator
from unittest.mock import patch, MagicMock

from taxi.crm.masshire.tools.import_amocrm_users.lib.secrets import get_secret

MODULE: Final = "taxi.crm.masshire.tools.import_amocrm_users.lib.secrets"
SECRET_ID: Final = "sec-4242"
KEY: Final = "KEY"


@pytest.fixture()
def yav_client() -> Generator[MagicMock, None, None]:
    with patch(f"{MODULE}.YavClient") as mock_method:
        yield mock_method


def test_get_secret__given_env_variable__returns_it(monkeypatch: Any, yav_client: MagicMock) -> None:
    monkeypatch.setenv(KEY, "secret_value")
    assert get_secret(SECRET_ID, KEY, is_production=False) == "secret_value"
    yav_client.assert_not_called()


def test_get_secret__for_no_env_variable__uses_yavault(yav_client: MagicMock) -> None:
    get_secret(SECRET_ID, KEY, is_production=False)
    yav_client.assert_called_once()


def test_get_secret__for_empty_env_variable__uses_yavault(monkeypatch: Any, yav_client: MagicMock) -> None:
    monkeypatch.setenv(KEY, "")
    get_secret(SECRET_ID, KEY, is_production=False)
    yav_client.assert_called_once()


def test_get_secret__for_production__uses_production_key(yav_client: MagicMock) -> None:
    get_secret(SECRET_ID, KEY, is_production=True)
    yav_client().get_version().__getitem__().__getitem__.assert_called_with("KEY_PRODUCTION")


def test_get_secret__for_testing__uses_testing_key(yav_client: MagicMock) -> None:
    get_secret(SECRET_ID, KEY, is_production=False)
    yav_client().get_version().__getitem__().__getitem__.assert_called_with("KEY_TESTING")
