import pytest

import annlib.filter_acl

from . import conftest


@pytest.mark.parametrize(
    "test_file", conftest.dataglob("data/test_filter_config_*.yaml")
)
def test_filter_config(test_file: str):
    test_data = conftest.dataparse(test_file)
    vendor: str = test_data["vendor"]
    input: str = test_data["input"]
    output: str = test_data["output"]
    acl_text: str = test_data["acl"]
    output = conftest.strip(output)

    acl = annlib.filter_acl.make_acl(acl_text, vendor)
    fmtr = annlib.filter_acl.tabparser.make_formatter(vendor)
    result = annlib.filter_acl.filter_config(acl, fmtr, input)
    result = conftest.strip(result)
    assert result == output


@pytest.mark.parametrize(
    "test_file", conftest.dataglob("data/test_filter_diff_*.yaml")
)
def test_filter_diffs(test_file: str):
    test_data = conftest.dataparse(test_file)
    vendor: str = test_data["vendor"]
    input: str = test_data["input"]
    output: str = test_data["output"]
    acl_text: str = test_data["acl"]
    output = conftest.strip(output)

    acl = annlib.filter_acl.make_acl(acl_text, vendor)
    fmtr = annlib.filter_acl.tabparser.make_formatter(vendor)
    result = annlib.filter_acl.filter_diff(acl, fmtr, input)
    result = conftest.strip(result)
    assert result == output


@pytest.mark.parametrize(
    "test_file", conftest.dataglob("data/test_filter_patch_*.yaml")
)
def test_filter_patch(test_file: str):
    test_data = conftest.dataparse(test_file)
    vendor: str = test_data["vendor"]
    input: str = test_data["input"]
    output: str = test_data["output"]
    acl_text: str = test_data["acl"]
    output = conftest.strip(output)

    acl = annlib.filter_acl.make_acl(acl_text, vendor)
    fmtr = annlib.filter_acl.tabparser.make_formatter(vendor)
    result = annlib.filter_acl.filter_patch(acl, fmtr, input)
    result = conftest.strip(result)
    assert result == output


@pytest.mark.parametrize(
    "test_file", conftest.dataglob("data/test_filter_jun_nokia_patch_*.yaml")
)
def test_filter_jun_nokia_patch(test_file: str):
    test_data = conftest.dataparse(test_file)
    vendor: str = test_data["vendor"]
    input: str = test_data["input"]
    output: str = test_data["output"]
    diff_filtered: str = test_data["diff_filtered"]

    output = conftest.strip(output)

    fmtr = annlib.filter_acl.tabparser.make_formatter(vendor)
    result = annlib.filter_acl.filter_patch_jun_nokia(diff_filtered, fmtr, input)
    result = conftest.strip(result)
    assert result == output
