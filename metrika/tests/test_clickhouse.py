import pytest
from metrika.pylib.clickhouse.lib import ClickHouseInstanceSelector


@pytest.fixture()
def round_robin_selector():
    yield ClickHouseInstanceSelector(["a", "b"], round_robin=True)


@pytest.fixture()
def stable_selector():
    yield ClickHouseInstanceSelector(["a", "b"], round_robin=False)


def test_round_robin_selector(round_robin_selector):
    assert round_robin_selector.hosts == ["a", "b"]
    for _ in range(3):
        assert [h for h in round_robin_selector.hosts_iter()] == ["a", "b"]
        assert next(round_robin_selector.hosts_iter()) == "a"
        assert next(round_robin_selector.hosts_iter()) == "b"


def test_stable_selector(stable_selector):
    assert stable_selector.hosts == ["a", "b"]

    assert [h for h in stable_selector.hosts_iter()] == ["a", "b"]
    assert next(stable_selector.hosts_iter()) == "b"
    assert next(stable_selector.hosts_iter()) == "b"

    assert [h for h in stable_selector.hosts_iter()] == ["b", "a"]
    assert next(stable_selector.hosts_iter()) == "a"
    assert next(stable_selector.hosts_iter()) == "a"

    assert [h for h in stable_selector.hosts_iter()] == ["a", "b"]
    assert next(stable_selector.hosts_iter()) == "b"
    assert next(stable_selector.hosts_iter()) == "b"
