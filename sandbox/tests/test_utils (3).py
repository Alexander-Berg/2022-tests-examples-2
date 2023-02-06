import pytest

from sandbox.projects.yabs.qa.tasks.YabsServerCreateGoalnetHamster import (
    filter_bases_by_shard,
    st_shards_to_goalnet_shards,
)


@pytest.mark.parametrize(("st_shards", "base_shards"), [
    ([], []),
    ([1], list(range(1, 360, 12))),
    ([1, 1], list(range(1, 360, 12))),
    ([1, 2], list(range(1, 360, 12)) + list(range(2, 360, 12))),
])
def test_st_shards_to_goalnet_shards(st_shards, base_shards):
    assert set(st_shards_to_goalnet_shards(st_shards)) == set(base_shards)


@pytest.mark.parametrize("st_shards", [
    [0, 1],
    [1, 100]
])
def test_st_shards_to_goalnet_shards_invalid_params(st_shards):
    with pytest.raises(ValueError):
        st_shards_to_goalnet_shards(st_shards)


@pytest.mark.parametrize(("bases", "shards", "expected"), [
    (
        ["1.dbc.yabs", "1.goalst001.yabs", "1.goalst002.yabs", "1.goalst003.yabs"],
        [1],
        ["1.dbc.yabs", "1.goalst001.yabs"],
    ),
    (
        ["1.dbc.yabs", "1.goalst001.yabs", "1.goalst002.yabs", "1.goalst003.yabs"],
        [1, 2],
        ["1.dbc.yabs", "1.goalst001.yabs", "1.goalst002.yabs"],
    ),
    (
        ["1.dbc.yabs", "1.goalst001.yabs", "1.goalst002.yabs", "1.goalst003.yabs"],
        [],
        ["1.dbc.yabs"],
    ),
])
def test_filter_bases_by_shard(bases, shards, expected):
    assert set(filter_bases_by_shard(bases, shards)) == set(expected)
