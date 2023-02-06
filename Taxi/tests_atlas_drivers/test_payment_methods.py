# flake8: noqa F401, IS001
# pylint: disable=C5521
import pytest

from tests_atlas_drivers import driver_info
from tests_atlas_drivers import fbs_parse
from tests_atlas_drivers.candidates_fixture import _candidates
from tests_atlas_drivers import drivers


_DRIVERS_COUNT = 7


def _generate_payment_methods_fail(
        index_driver: int,
) -> driver_info.PaymentMethods:
    return driver_info.PaymentMethods(actual=['card'], taximeter=['card'])


@pytest.mark.parametrize('fail', [True, False])
async def test_payment_methods(
        taxi_atlas_drivers, candidates, fail, parks_activation_mocks,
):
    sample_drivers = drivers.generate_drivers(
        _DRIVERS_COUNT,
        payment_methods=_generate_payment_methods_fail
        if fail
        else drivers.generate_payment_methods,
    )

    candidates.set_drivers(sample_drivers)
    candidates.set_data_keys_wanted(['payment_methods'])

    if fail:
        parks_activation_mocks.set_parks({})
    else:
        parks_activation_mocks.set_parks(
            drivers.generate_parks_activation(sample_drivers),
        )

    await taxi_atlas_drivers.invalidate_caches()

    request = {
        'search_area': drivers.DEFAULT_SEARCH_AREA,
        'required_fields': ['payment_methods', 'payment_methods_taximeter'],
    }
    response = await taxi_atlas_drivers.post('v1/find-in-area', json=request)
    assert response.status_code == 200

    infos = fbs_parse.parse_drivers_info(response.content)
    assert len(infos) == len(sample_drivers)

    infos = list(sorted(infos, key=lambda x: x.ids.park_id))
    for lhs, rhs in zip(infos, sample_drivers):
        driver_info.compare_drivers(lhs, rhs, ['payment_methods'])
