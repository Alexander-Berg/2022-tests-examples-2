from taxi.crm.masshire.tools.match_dicts.locations.geocoder_data import (
    BatchResultRow,
    BatchRow,
    GEOID_MAPPING,
    GeocodedItem,
    merge_geocoder_results,
    upload_geocoder_batch,
)
from taxi.crm.masshire.tools.match_dicts.common.dictionary_typing import JobSite

from typing import Any
from unittest import mock

import pytest


@pytest.fixture
def yt_client_mock() -> mock.Mock:
    return mock.Mock()


def test_upload_geocoder_batch__always__uploads_it(
    yt_client_mock: mock.Mock,
) -> None:
    data: dict[JobSite, dict[str, list[Any]]] = {
        JobSite.HEAD_HUNTER: {
            "россия": [],
            "россия, москва": [],
        },
    }
    upload_geocoder_batch(yt_client_mock, "some-path", "2022-04-14", data)

    yt_client_mock.write_table_structured.assert_called_once_with(
        "some-path/head_hunter_2022-04-14",
        BatchRow,
        [
            BatchRow(request="россия", lang="ru"),
            BatchRow(request="россия, москва", lang="ru"),
        ],
    )


def test_merge_geocoder_results__given_row_without_geoid__skips_it(
    yt_client_mock: mock.Mock,
) -> None:
    yt_client_mock.read_table_structured.return_value = [
        BatchResultRow(geoid=None),
    ]

    assert merge_geocoder_results(yt_client_mock, "some-path", "2022-04-14") == {}


def test_merge_geocoder_results__given_valid_results__merges_it(
    yt_client_mock: mock.Mock,
) -> None:
    sj_result = [
        BatchResultRow(geoid=213, input_request="sj-request", kind="province", accuracy=1),
    ]
    hh_result = [
        BatchResultRow(geoid=213, input_request="hh-request", kind="province", accuracy=1),
    ]

    yt_client_mock.read_table_structured.side_effect = [hh_result, sj_result]

    result = merge_geocoder_results(yt_client_mock, "some-path", "2022-04-14")

    assert len(result) == 1
    assert result["213"] == {
        JobSite.HEAD_HUNTER: [
            GeocodedItem(original_address="hh-request", kind="province", accuracy=1),
        ],
        JobSite.SUPERJOB: [
            GeocodedItem(original_address="sj-request", kind="province", accuracy=1),
        ],
    }


@pytest.mark.parametrize("geoid", GEOID_MAPPING)
def test_merge_geocoder_results__given_complex_provinces__patches_them(
    geoid: str,
    yt_client_mock: mock.Mock,
) -> None:
    yt_result = [BatchResultRow(geoid=int(geoid))]
    yt_client_mock.read_table_structured.return_value = yt_result

    result = merge_geocoder_results(yt_client_mock, "some-path", "2022-04-14")

    assert result.keys() == {GEOID_MAPPING[geoid]}
