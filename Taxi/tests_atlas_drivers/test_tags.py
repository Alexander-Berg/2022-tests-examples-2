# flake8: noqa F401, IS001
# pylint: disable=C5521
import pytest

from tests_atlas_drivers import fbs_parse
from tests_atlas_drivers.candidates_fixture import _candidates
from tests_atlas_drivers import drivers
from tests_atlas_drivers import driver_info


_DRIVERS_COUNT = 7
_SAMPLE_DRIVERS = drivers.generate_drivers(
    _DRIVERS_COUNT, tags=drivers.generate_tags,
)


@pytest.mark.parametrize(
    'tags_fail, chunk_size, override_retries',
    [(True, 7, None), (False, 2, None), (False, 2, 10)],
)
async def test_tags(
        taxi_atlas_drivers,
        candidates,
        tags_fail,
        chunk_size,
        override_retries,
        driver_tags_mocks,
        taxi_config,
):
    taxi_config.set_values(
        dict(ATLAS_DRIVERS_CHUNK_SIZES={'__default__': chunk_size}),
    )

    if override_retries is not None:
        taxi_config.set_values(
            dict(
                ATLAS_DRIVERS_FETCHERS_CLIENT_QOS={
                    'tags': {'attempts': 10, 'timeout-ms': 1000},
                },
            ),
        )

    candidates.set_drivers(_SAMPLE_DRIVERS)
    candidates.set_data_keys_wanted([])

    for driver in _SAMPLE_DRIVERS:
        driver_tags_mocks.set_tags_info(
            driver.ids.park_id,
            driver.ids.driver_profile_id,
            driver.tags.tag_names,
        )

    if tags_fail:
        driver_tags_mocks.set_error(
            handler='/v1/drivers/match/profiles_fbs', error_code=500,
        )
    categories = ['tags']
    request = {
        'search_area': drivers.DEFAULT_SEARCH_AREA,
        'required_fields': categories,
    }

    response = await taxi_atlas_drivers.post('v1/find-in-area', json=request)
    assert response.status_code == 200

    if tags_fail:
        if override_retries is None:
            # three retries
            assert driver_tags_mocks.count_calls() == 3
        else:
            assert driver_tags_mocks.count_calls() == override_retries
    else:
        # four actual requests
        assert driver_tags_mocks.count_calls() == 4

    infos = fbs_parse.parse_drivers_info(response.content)
    assert len(infos) == len(_SAMPLE_DRIVERS)

    infos = list(sorted(infos, key=lambda x: x.ids.park_id))
    for lhs, rhs in zip(infos, _SAMPLE_DRIVERS):
        driver_info.compare_drivers(lhs, rhs, [] if tags_fail else categories)
