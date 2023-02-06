import pytest

from requests.exceptions import HTTPError
from requests_mock import Mocker, ANY

from taxi.crm.masshire.tools.import_amocrm_users.lib.amo_api import AMO_URL_TEST, fetch_users


def test_fetch_users__given_not_ok__raises(requests_mock: Mocker) -> None:
    requests_mock.get(ANY, status_code=401)
    with pytest.raises(HTTPError):
        fetch_users(api_url=AMO_URL_TEST, access_token="")


def test_fetch_users__given_multiple_pages__fetches_all(requests_mock: Mocker) -> None:
    requests_mock.get(ANY, text="""{ "_page_count": 5, "_embedded": {"users": [1]} }""")

    result = fetch_users(api_url=AMO_URL_TEST, access_token="", pause=0)

    assert len(result) == 5
