# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import pytest

import grocery_tasks.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['grocery_tasks.generated.service.pytest_plugins']

SETTINGS_OVERRIDE = {
    'S3MDS_TAXI_CRITEO': {
        'url': 'taxi-criteo.s3.yandex.net',
        'bucket': 'taxi-criteo',
        'access_key_id': 'key_to_access',
        'secret_key': 'very_secret',
    },
}


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update(SETTINGS_OVERRIDE)
    return simple_secdist


DEFAULT_DEPOT_LOCATION = [10, 20]
DEPOT_KEY = 'depots'
DEFAULT_DEPOTS: dict = {'depots': [], 'errors': []}


@pytest.fixture(name='grocery_depots', autouse=True)
def mock_grocery_depots(mockserver):
    payload = {}

    class Context:
        def add_depot(
                self,
                *,
                legacy_depot_id,
                location=None,
                depot_id=None,
                country_iso3=None,
                country_iso2=None,
                region_id=None,
                company_type=None,
                currency=None,
                phone_number=None,
                timezone=None,
        ):
            if location is None:
                location = DEFAULT_DEPOT_LOCATION
            if DEPOT_KEY not in payload:
                payload[DEPOT_KEY] = {'depots': [], 'errors': []}

            location = {'lat': location[0], 'lon': location[0]}

            depot = {
                'depot_id': depot_id,
                'legacy_depot_id': legacy_depot_id,
                'country_iso3': country_iso3,
                'country_iso2': country_iso2,
                'region_id': region_id,
                'timezone': timezone,
                'location': location,
                'phone_number': phone_number,
                'currency': currency,
                'company_type': company_type,
                'status': 'active',
                'hidden': False,
            }

            payload[DEPOT_KEY]['depots'].append(depot)
            return depot

    @mockserver.json_handler('/grocery-depots/internal/v1/depots/v1/depots')
    def _mock_internal_catalog_depots(request):
        return payload.get(DEPOT_KEY, DEFAULT_DEPOTS)

    context = Context()

    return context
