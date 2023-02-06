import math
# flake8: noqa F401, IS001
# pylint: disable=C5521
import pytest

from tests_atlas_drivers import driver_info
from tests_atlas_drivers import fbs_parse
from tests_atlas_drivers.candidates_fixture import _candidates
from tests_atlas_drivers.reposition_fixture import _reposition
from tests_atlas_drivers import drivers

_DRIVERS_COUNT = 16
_SAMPLE_DRIVERS = drivers.generate_drivers(
    _DRIVERS_COUNT, reposition=drivers.generate_reposition,
)
_SAMPLE_REPOSITIONS = drivers.generate_repositions(
    _DRIVERS_COUNT, reposition=drivers.generate_reposition,
)


@pytest.mark.parametrize(
    'reposition_fail, chunk_size', [(True, 20), (False, 20), (False, 5)],
)
async def test_reposition(
        taxi_atlas_drivers,
        candidates,
        reposition,
        reposition_fail,
        chunk_size,
        taxi_config,
):
    candidates.set_drivers(_SAMPLE_DRIVERS)
    candidates.set_data_keys_wanted([])

    reposition.set_error(reposition_fail)
    reposition.set_reposition(_SAMPLE_REPOSITIONS)

    taxi_config.set_values(
        dict(
            ATLAS_DRIVERS_CHUNK_SIZES={
                '__default__': 1000,
                'reposition': chunk_size,
            },
        ),
    )

    categories = ['reposition']
    request = {
        'search_area': drivers.DEFAULT_SEARCH_AREA,
        'required_fields': categories,
    }
    response = await taxi_atlas_drivers.post('v1/find-in-area', json=request)
    assert response.status_code == 200

    excepted_calls = math.ceil(_DRIVERS_COUNT / chunk_size)
    if reposition_fail:
        # one retries
        assert reposition.times_called == excepted_calls
    else:
        # actual requests
        assert reposition.times_called == excepted_calls

    infos = fbs_parse.parse_drivers_info(response.content)
    assert len(infos) == len(_SAMPLE_DRIVERS)

    infos = list(sorted(infos, key=lambda x: x.ids.park_id))
    for lhs, rhs in zip(infos, _SAMPLE_DRIVERS):
        driver_info.compare_drivers(
            lhs, rhs, [] if reposition_fail else categories,
        )
