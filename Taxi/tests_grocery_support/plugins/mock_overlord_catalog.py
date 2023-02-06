import pytest

DEFAULT_DEPOT_TIN = '123'


OVERLORD_DEPOT_KEY = 'depots'
DEFAULT_OVERLORD_DEPOTS: dict = {'depots': [], 'errors': []}


@pytest.fixture(name='overlord_catalog', autouse=True)
def mock_overlord_catalog(mockserver):
    payload = {}

    @mockserver.json_handler('/overlord-catalog/internal/v1/catalog/v1/depots')
    def mock_internal_catalog_depots(request):
        return payload.get(OVERLORD_DEPOT_KEY, DEFAULT_OVERLORD_DEPOTS)

    class Context:
        def add_depot(
                self,
                *,
                legacy_depot_id,
                depot_id='original_depot_id',
                country_iso3='RUS',
                country_iso2='RU',
                region_id=213,
                timezone='Europe/Moscow',
                location=None,
                address=None,
                tin=DEFAULT_DEPOT_TIN,
                phone_number='+78007700460',
                currency='RUB',
                directions=None,
                company_type='yandex',
                name=None,
                short_address=None,
        ):
            if location is None:
                location = [10, 20]
            if OVERLORD_DEPOT_KEY not in payload:
                payload[OVERLORD_DEPOT_KEY] = {'depots': [], 'errors': []}

            payload[OVERLORD_DEPOT_KEY]['depots'].append(
                {
                    'depot_id': depot_id,
                    'legacy_depot_id': legacy_depot_id,
                    'country_iso3': country_iso3,
                    'country_iso2': country_iso2,
                    'region_id': region_id,
                    'timezone': timezone,
                    'position': {'location': location},
                    'address': address,
                    'tin': tin,
                    'phone_number': phone_number,
                    'currency': currency,
                    'directions': directions,
                    'company_type': company_type,
                    'name': name,
                    'short_address': short_address,
                },
            )

        def times_called(self):
            return mock_internal_catalog_depots.times_called

        def flush(self):
            mock_internal_catalog_depots.flush()

    context = Context()
    return context
