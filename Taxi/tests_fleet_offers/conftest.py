# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from fleet_offers_plugins import *  # noqa: F403 F401


@pytest.fixture
def mock_fleet_parks(mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _parks_list(request):
        return {
            'parks': [
                {
                    'id': 'park1',
                    'login': 'login',
                    'name': 'some park name',
                    'is_active': True,
                    'city_id': 'city',
                    'locale': 'locale',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'country_id': 'country_id',
                    'demo_mode': False,
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                    'provider_config': {'type': 'production', 'clid': '123'},
                },
            ],
        }


@pytest.fixture
def mock_parks_replica(mockserver):
    @mockserver.json_handler(
        '/parks-replica/v1/parks/billing_client_id/retrieve',
    )
    def _billing_client_id(request):
        return {'billing_client_id': '1234'}


@pytest.fixture
def mock_billing_replication(mockserver):
    @mockserver.json_handler('/billing-replication/contract/')
    def _contract(request):
        return [
            {'ID': 100, 'IS_ACTIVE': 1, 'SERVICES': [111], 'PERSON_ID': 100},
            {'ID': 101, 'IS_ACTIVE': 0, 'SERVICES': [111], 'PERSON_ID': 101},
            {'ID': 102, 'IS_ACTIVE': 1, 'SERVICES': [651], 'PERSON_ID': 102},
        ]

    @mockserver.json_handler('/billing-replication/person/')
    def _person(request):
        return [
            {
                'ID': '100',
                'NAME': 'ООО ААА',
                'LEGALADDRESS': 'Moscow',
                'INN': '12345678',
                'OGRN': '1234567',
                'ACCOUNT': '777',
                'BIK': '123456789',
            },
        ]


@pytest.fixture
def mock_balance_replica(mockserver):
    @mockserver.json_handler('/balance-replica/v1/banks/by_bik')
    def _bank(request):
        return {
            'id': 1,
            'hidden': 0,
            'bik': '123456789',
            'name': 'sber',
            'cor_acc': '888',
        }


@pytest.fixture
def mock_document_templator(mockserver):
    @mockserver.json_handler(
        '/document-templator/v1/dynamic_documents/document_id/',
    )
    def _document_id(request):
        return {'id': 'doc_id'}
