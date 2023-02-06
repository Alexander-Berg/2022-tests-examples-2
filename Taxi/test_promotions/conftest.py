# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import pytest

import promotions.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['promotions.generated.service.pytest_plugins']


SETTINGS_OVERRIDE = {
    'S3MDS_TAXI_PROMOTIONS': {
        'url': 's3.mdst.yandex.net',
        'bucket': 'taxi-promotions-testing',
        'access_key_id': 'key_to_access',
        'secret_key': 'very_secret',
    },
    'API_TOKEN_TAXI_PROMOTIONS_OCR': 'api_key',
}


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update(SETTINGS_OVERRIDE)
    return simple_secdist


@pytest.fixture
def tags_service_mock(mockserver):
    @mockserver.json_handler('/passenger-tags/v1/match')
    def _match(request):
        return {
            'entities': [
                {'tags': ['good_passenger', 'lucky']},
                {'tags': ['another_entity']},
                {'tags': []},
            ],
        }

    return _match


@pytest.fixture(autouse=True)
def exp3_service_mock(mockserver):
    @mockserver.json_handler('/experiments3/v1/experiments')
    def _match(request):
        return {'items': []}

    return _match
