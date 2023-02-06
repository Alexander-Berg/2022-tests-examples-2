# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from qc_executors_plugins import *  # noqa: F403 F401


class BiometryEtalonsContext:
    def __init__(self):
        self.expected_etalons = dict()

    def set_expected_etalons(self, park_id, driver_profile_id, etalons):
        self.expected_etalons[(park_id, driver_profile_id)] = []
        for storage_id, storage_bucket in etalons:
            self.expected_etalons[(park_id, driver_profile_id)].append(
                {'storage_id': storage_id, 'storage_bucket': storage_bucket},
            )

    def get_etalons(self, park_id, driver_profile_id):
        return self.expected_etalons.get((park_id, driver_profile_id), [])


@pytest.fixture(name='biometry_etalons')
def _biometry_etalons(mockserver):
    context = BiometryEtalonsContext()

    @mockserver.json_handler('/biometry-etalons/service/v1/store')
    def _service_v1_store_mock(request):
        park_id = request.json['park_id']
        driver_profile_id = request.json['driver_profile_id']

        assert park_id is not None and driver_profile_id is not None
        assert request.json['version'] == 123

        assert request.json['etalon_media'] == {
            'selfie': context.get_etalons(park_id, driver_profile_id),
        }

        return mockserver.make_response(json={}, status=200)

    return context
