import pytest
import json

from noc.matilda_clickhouse_proxy.lib import parser

DATA_FILE = "tests/data/top_mutate.json"


@pytest.mark.benchmark()
def test_benchmark_top_by_mutate(benchmark):
    with open(DATA_FILE) as fd:
        keys_and_data = json.load(fd)
    benchmark(
        parser._top_by_mutate,
        keys_and_data["keys"],
        keys_and_data["data"],
    )
