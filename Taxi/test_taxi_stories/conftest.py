# pylint: disable=redefined-outer-name
import pytest

from taxi.clients import archive_api

import taxi_stories.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['taxi_stories.generated.service.pytest_plugins']


@pytest.fixture
def mock_archive_response(monkeypatch):
    def mock_archive(
            order_response, get_rows_yandexuid=None, get_rows_response=None,
    ):
        if get_rows_response is None:
            get_rows_response = order_response

        async def get_order_patch(*args, **kwargs):
            return order_response

        monkeypatch.setattr(
            archive_api.ArchiveApiClient, 'get_order_by_id', get_order_patch,
        )

        async def get_rows_patch(*args, **kwargs):
            if get_rows_yandexuid is not None:
                assert (
                    kwargs['query_string'] == ' * FROM %t WHERE user_uid = %p '
                    'ORDER BY created DESC LIMIT 1'
                )

                query_params = kwargs['query_params']
                assert len(query_params) == 2
                assert query_params[1] == get_rows_yandexuid

            return [get_rows_response] if get_rows_response is not None else []

        monkeypatch.setattr(
            archive_api.ArchiveApiClient, 'select_rows', get_rows_patch,
        )

    return mock_archive
