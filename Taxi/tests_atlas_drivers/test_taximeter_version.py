# flake8: noqa F401, IS001
# pylint: disable=C5521
import json

import pytest

from tests_atlas_drivers import driver_info
from tests_atlas_drivers import fbs_parse
from tests_atlas_drivers.candidates_fixture import _candidates
from tests_atlas_drivers import drivers


_SAMPLE_DRIVERS = drivers.generate_drivers(
    3, taximeter_versions=drivers.generate_taximeter_versions,
)


async def test_airports(taxi_atlas_drivers, candidates, mockserver):
    candidates.set_drivers(_SAMPLE_DRIVERS)
    candidates.set_data_keys_wanted([])

    categories = ['taximeter_version']
    request = {
        'search_area': drivers.DEFAULT_SEARCH_AREA,
        'required_fields': categories,
    }
    response = await taxi_atlas_drivers.post('v1/find-in-area', json=request)
    assert response.status_code == 200

    infos = fbs_parse.parse_drivers_info(response.content)
    assert len(infos) == len(_SAMPLE_DRIVERS)

    infos = list(sorted(infos, key=lambda x: x.ids.park_id))
    for lhs, rhs in zip(infos, _SAMPLE_DRIVERS):
        driver_info.compare_drivers(lhs, rhs, categories)
