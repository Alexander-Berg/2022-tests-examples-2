from taxi.crm.masshire.tools.match_dicts.locations.headhunter import (
    OTHER_REGIONS_ID,
    load_areas,
)
from taxi.crm.masshire.tools.match_dicts.locations.job_site_data import DataItem

from collections.abc import Generator
from typing import Any
from unittest import mock

import pytest


class Fixture:
    def __init__(self, file_open_mock: mock.Mock, json_loads_mock: mock.Mock):
        self.file_open_mock = file_open_mock
        self.json_loads_mock = json_loads_mock


@pytest.fixture
def f() -> Generator:
    with (
        mock.patch("builtins.open") as f1,
        mock.patch("json.load") as f2,
    ):
        yield Fixture(f1, f2)


def hh_item(**kwargs: Any) -> dict[str, Any]:
    return dict(**kwargs)


def test_load_areas__given_valid_areas__loads_them(f: Fixture) -> None:
    f.json_loads_mock.return_value = [
        hh_item(
            name="Россия",
            id="113",
            areas=[hh_item(name="Ростовская область", id="1530", areas=[])],
        )
    ]

    result = load_areas("file")

    assert result == {
        "россия": [DataItem(id_="113", level=0)],
        "россия, ростовская область": [DataItem(id_="1530", level=1)],
    }


def test_load_areas__given_areas_with_same_names__loads_them(
    f: Fixture,
) -> None:
    f.json_loads_mock.return_value = [
        hh_item(name="Красные Баррикады", id="5353", areas=[]),
        hh_item(name="Красные Баррикады", id="5173", areas=[]),
    ]

    result = load_areas("file")

    assert result == {
        "красные баррикады": [
            DataItem(id_="5353", level=0),
            DataItem(id_="5173", level=0),
        ],
    }


def test_load_areas__given_other_region_id__skips_it(f: Fixture) -> None:
    f.json_loads_mock.return_value = [
        hh_item(
            name="Другие регионы",
            id=OTHER_REGIONS_ID,
            areas=[hh_item(name="Япония", id="111", areas=[])],
        ),
    ]

    result = load_areas("file")

    assert result == {"япония": [DataItem(id_="111", level=1)]}


def test_load_areas__for_wrong_area_name__patches_it(f: Fixture) -> None:
    f.json_loads_mock.return_value = [
        hh_item(name="Ненецкий АО", id="1985", areas=[]),
    ]

    result = load_areas("file")

    assert result == {
        "ненецкий автономный округ": [DataItem(id_="1985", level=0)],
    }
