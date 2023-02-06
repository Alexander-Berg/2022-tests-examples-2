from tests_ride_discounts import common


def test_hierarchy_names(condition_descriptions):
    hierarchy_names = sorted(
        description['name'] for description in condition_descriptions
    )
    assert hierarchy_names == sorted(
        common.HIERARCHY_NAMES + common.DEPRECATED_HIERARCHY_NAMES,
    )
