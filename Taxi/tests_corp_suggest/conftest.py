# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import dataclasses
import typing

import pytest

from corp_suggest_plugins import *  # noqa: F403 F401


@pytest.fixture
def mock_dadata_suggestions(mockserver):
    class MockDadata:
        @dataclasses.dataclass
        class DadataSuggestionsData:
            suggest_response: dict
            dadata_error_code: typing.Optional[int]

        data = DadataSuggestionsData(
            suggest_response={'suggestions': []}, dadata_error_code=None,
        )

        @staticmethod
        @mockserver.json_handler(
            '/dadata-suggestions/suggestions/api/4_1/rs/suggest/party',
        )
        async def suggest(request):
            if MockDadata.data.dadata_error_code:
                return mockserver.make_response(
                    json={'code': 'some error'},
                    status=MockDadata.data.dadata_error_code,
                )

            return mockserver.make_response(
                json=MockDadata.data.suggest_response, status=200,
            )

    return MockDadata()
