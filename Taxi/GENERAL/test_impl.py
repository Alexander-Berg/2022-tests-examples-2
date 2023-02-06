from string import ascii_lowercase

import pytest
from nile.api.v1 import Record

from market_platform_eff_etl.layer.greenplum.ods.mbo.category.impl import (
    build_category_tree, is_leaf,
)

missed_name = 'Не указано'
missed_id = -1
root_category = Record(
    id=7,
    hyper_id=7,
    name='h',
    parents=[],
    parent_hyper_ids=[],
    parents_names=[],
)
mid_category = root_category.transform(
    parents=list(range(3)),
    parent_hyper_ids=list(range(3)),
    parents_names=list(ascii_lowercase[:3])
)
leaf_category = root_category.transform(
    parents=list(range(8)),
    parent_hyper_ids=list(range(8)),
    parents_names=list(ascii_lowercase[:8])
)


@pytest.mark.parametrize('input, expected', [
    (
        root_category,
        root_category.transform(
            lvl0_name_ru='h',
            lvl1_name_ru=missed_name,
            lvl2_name_ru=missed_name,
            lvl3_name_ru=missed_name,
            lvl4_name_ru=missed_name,
            lvl5_name_ru=missed_name,
            lvl6_name_ru=missed_name,
            lvl7_name_ru=missed_name,
            lvl0_hyper_id=7,
            lvl1_hyper_id=missed_id,
            lvl2_hyper_id=missed_id,
            lvl3_hyper_id=missed_id,
            lvl4_hyper_id=missed_id,
            lvl5_hyper_id=missed_id,
            lvl6_hyper_id=missed_id,
            lvl7_hyper_id=missed_id,
        ),
    ),
    (
        leaf_category,
        leaf_category.transform(
            lvl0_name_ru='a',
            lvl1_name_ru='b',
            lvl2_name_ru='c',
            lvl3_name_ru='d',
            lvl4_name_ru='e',
            lvl5_name_ru='f',
            lvl6_name_ru='g',
            lvl7_name_ru='h',
            lvl0_hyper_id=0,
            lvl1_hyper_id=1,
            lvl2_hyper_id=2,
            lvl3_hyper_id=3,
            lvl4_hyper_id=4,
            lvl5_hyper_id=5,
            lvl6_hyper_id=6,
            lvl7_hyper_id=7,
        ),
    ),
    (
        mid_category,
        mid_category.transform(
            lvl0_name_ru='a',
            lvl1_name_ru='b',
            lvl2_name_ru='c',
            lvl3_name_ru='h',
            lvl4_name_ru=missed_name,
            lvl5_name_ru=missed_name,
            lvl6_name_ru=missed_name,
            lvl7_name_ru=missed_name,
            lvl0_hyper_id=0,
            lvl1_hyper_id=1,
            lvl2_hyper_id=2,
            lvl3_hyper_id=7,
            lvl4_hyper_id=missed_id,
            lvl5_hyper_id=missed_id,
            lvl6_hyper_id=missed_id,
            lvl7_hyper_id=missed_id,
        ),
    ),
])
def test_build_category_tree(expected, input):
    assert [expected.to_dict()] == [r.to_dict() for r in build_category_tree([input])]


def test_is_leaf():
    assert is_leaf({'children': [1]})
    assert not is_leaf({'children': []})
