# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import dataclasses
import typing

import pytest

from fleet_legal_entities_plugins import *  # noqa: F403 F401

DADATA_ENDPOINT = '/dadata-suggestions/suggestions/api/4_1/rs/findById/party'
BELARUS_ENDPOINT_MAIN = (
    '/fleet-legal-entities-belarus/v2/egr/getShortInfoByRegNum/'
)
BELARUS_ENDPOINT_ADDRESS = (
    '/fleet-legal-entities-belarus/v2/egr/getAddressByRegNum/'
)


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
        @mockserver.json_handler(DADATA_ENDPOINT)
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


@pytest.fixture
def mock_blr_api(mockserver):
    class MockBlrApi:
        @dataclasses.dataclass
        class Data:
            main_response: typing.List
            address_response: typing.List

        data = Data(main_response=[], address_response=[])

        registration_number = 12356

        @staticmethod
        @mockserver.json_handler(
            f'{BELARUS_ENDPOINT_MAIN}{registration_number}',
        )
        async def suggest_(request):
            return mockserver.make_response(
                json=MockBlrApi.data.main_response, status=200,
            )

        @staticmethod
        @mockserver.json_handler(
            f'{BELARUS_ENDPOINT_ADDRESS}{registration_number}',
        )
        async def address_(request):
            return mockserver.make_response(
                json=MockBlrApi.data.address_response, status=200,
            )

    return MockBlrApi()
