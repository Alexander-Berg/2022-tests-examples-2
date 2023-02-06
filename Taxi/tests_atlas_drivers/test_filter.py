# flake8: noqa F401, IS001, I202
# pylint: disable=C1801, C5521
from typing import List

import pytest

from tests_atlas_drivers import driver_info
from tests_atlas_drivers.candidates_fixture import _candidates
from tests_atlas_drivers import drivers
from tests_atlas_drivers import fbs_parse


def _generate_car_classes(index_driver: int) -> driver_info.CarClasses:
    return driver_info.CarClasses(['econom', 'comfort'], [], [], [])


def _generate_tags(index_driver: int) -> List[str]:
    return ['abacaba']


_SAMPLE_DRIVER = drivers.generate_drivers(
    1, car_classes=_generate_car_classes, tags=_generate_tags,
)[0]


@pytest.mark.driver_tags_match(
    dbid=_SAMPLE_DRIVER.ids.park_id,
    uuid=_SAMPLE_DRIVER.ids.driver_profile_id,
    tags=_SAMPLE_DRIVER.tags,
)
async def test_fetch_non_projected(
        taxi_atlas_drivers, candidates, driver_tags_mocks,
):
    candidates.set_drivers([_SAMPLE_DRIVER])
    candidates.set_data_keys_wanted(['classes'])

    request = {
        'search_area': drivers.DEFAULT_SEARCH_AREA,
        'required_fields': ['car_classes'],
        'filter': {'tags.tag_names': {'$all': ['abacaba']}},
    }

    response = await taxi_atlas_drivers.post('v1/find-in-area', json=request)
    assert response.status_code == 200
    response = fbs_parse.parse_drivers_info(response.content)
    assert len(response) == 1
    assert response[0].tags is None

    assert driver_tags_mocks.count_calls() == 1


@pytest.mark.driver_tags_match(
    dbid=_SAMPLE_DRIVER.ids.park_id,
    uuid=_SAMPLE_DRIVER.ids.driver_profile_id,
    tags=_SAMPLE_DRIVER.tags,
)
async def test_disallowed_first_filtered(
        taxi_atlas_drivers, candidates, driver_tags_mocks,
):
    candidates.set_drivers([_SAMPLE_DRIVER])
    candidates.set_data_keys_wanted(['classes'])

    request = {
        'search_area': drivers.DEFAULT_SEARCH_AREA,
        'required_fields': ['car_classes'],
        'filter': {
            '$and': [
                {'car_classes.actual': {'$all': ['express']}},
                {'tags.tag_names': {'$all': ['abacaba']}},
            ],
        },
    }

    response = await taxi_atlas_drivers.post('v1/find-in-area', json=request)
    assert response.status_code == 200
    response = fbs_parse.parse_drivers_info(response.content)
    assert len(response) == 0

    assert driver_tags_mocks.count_calls() == 0


@pytest.mark.driver_tags_match(
    dbid=_SAMPLE_DRIVER.ids.park_id,
    uuid=_SAMPLE_DRIVER.ids.driver_profile_id,
    tags=_SAMPLE_DRIVER.tags,
)
async def test_allowed_first_filtered(
        taxi_atlas_drivers, candidates, driver_tags_mocks,
):
    candidates.set_drivers([_SAMPLE_DRIVER])
    candidates.set_data_keys_wanted(['classes'])

    request = {
        'search_area': drivers.DEFAULT_SEARCH_AREA,
        'required_fields': ['car_classes'],
        'filter': {
            '$and': [
                {'car_classes.actual': {'$any': ['econom']}},
                {'tags.tag_names': {'$all': ['abacaba']}},
            ],
        },
    }

    response = await taxi_atlas_drivers.post('v1/find-in-area', json=request)
    assert response.status_code == 200
    response = fbs_parse.parse_drivers_info(response.content)
    assert len(response) == 1

    assert driver_tags_mocks.count_calls() == 1


@pytest.mark.driver_tags_error(
    handler='/v1/drivers/match/profiles_fbs', error_code=500,
)
async def test_unknown_filtered(
        taxi_atlas_drivers, candidates, driver_tags_mocks,
):
    candidates.set_drivers([_SAMPLE_DRIVER])
    candidates.set_data_keys_wanted(['classes'])

    request = {
        'search_area': drivers.DEFAULT_SEARCH_AREA,
        'required_fields': ['car_classes'],
        'filter': {'tags.tag_names': {'$all': ['abacaba']}},
    }

    response = await taxi_atlas_drivers.post('v1/find-in-area', json=request)
    assert response.status_code == 200
    response = fbs_parse.parse_drivers_info(response.content)
    assert len(response) == 1

    # three retries
    assert driver_tags_mocks.count_calls() == 3
