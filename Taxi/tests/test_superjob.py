from taxi.crm.masshire.tools.match_dicts.locations.superjob import (
    RegionType,
    load_areas,
)
from taxi.crm.masshire.tools.match_dicts.locations.job_site_data import (
    JobSiteData,
    DataItem,
)

from collections.abc import Generator
from typing import Any
from unittest import mock

import pytest


class Fixture:
    def __init__(self, file_open_mock: mock.Mock, json_loads_mock: mock.Mock):
        self.file_open_mock = file_open_mock
        self.json_loads_mock = json_loads_mock

        self.towns: list[Any] = []
        self.regions: list[Any] = []
        self.countries: list[Any] = []

    def load(self) -> JobSiteData:
        self.json_loads_mock.side_effect = [
            {"objects": self.towns},
            {"objects": self.regions},
            {"objects": self.countries},
        ]
        return load_areas("f1", "f2", "f3")


@pytest.fixture
def f() -> Generator:
    with (
        mock.patch("builtins.open") as f1,
        mock.patch("json.load") as f2,
    ):
        yield Fixture(f1, f2)


def sj_item(**kwargs: Any) -> dict[str, Any]:
    return dict(**kwargs)


def test_load_areas__given_valid_areas__loads_them(f: Fixture) -> None:
    f.towns = [sj_item(title="Ростов", id=73, id_country=1, id_region=60)]
    f.regions = [sj_item(title="Ростовская область", id=60, id_country=1)]
    f.countries = [sj_item(title="Россия", id=1)]

    result = f.load()

    assert result == {
        "россия": [DataItem(id_="1", level=RegionType.COUNTRY.value)],
        "россия, ростовская область": [
            DataItem(id_="60", level=RegionType.PROVINCE.value),
        ],
        "россия, ростовская область, ростов": [
            DataItem(id_="73", level=RegionType.TOWN.value),
        ],
    }


def test_load_areas__given_tuymen__patches_it(f: Fixture) -> None:
    f.countries = [sj_item(title="Россия", id=1)]
    f.regions = [
        sj_item(
            title="Тюменская область, включая Ханты-Мансийский АО и Ямало-Ненецкий АО",
            id=71,
            id_country=1,
        ),
    ]

    result = f.load()

    assert result == {
        "россия": [DataItem(id_="1", level=RegionType.COUNTRY.value)],
        "россия, тюменская область": [
            DataItem(id_="71", level=RegionType.PROVINCE.value),
        ],
    }


def test_load_areas__given_moscow__skips_region_name(f: Fixture) -> None:
    f.countries = [sj_item(title="Россия", id=1)]
    f.regions = [sj_item(title="Московская область", id=46, id_country=1)]
    f.towns = [sj_item(title="Москва", id=4, id_country=1, id_region=46)]

    result = f.load()

    assert result == {
        "россия": [DataItem(id_="1", level=RegionType.COUNTRY.value)],
        "россия, московская область": [
            DataItem(id_="46", level=RegionType.PROVINCE.value),
        ],
        "россия, москва": [DataItem(id_="4", level=RegionType.TOWN.value)],
    }


def test_load_areas__given_town_without_region__loads_it(f: Fixture) -> None:
    f.countries = [sj_item(title="Беларусь", id=10)]
    f.regions = []
    f.towns = [sj_item(title="Минск", id=430, id_country=10, id_region=0)]

    result = f.load()

    assert result == {
        "беларусь": [DataItem(id_="10", level=RegionType.COUNTRY.value)],
        "беларусь, минск": [DataItem(id_="430", level=RegionType.TOWN.value)],
    }
