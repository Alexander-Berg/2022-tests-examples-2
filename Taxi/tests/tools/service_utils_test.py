import mock
import pytest

import tools.service_utils


@pytest.mark.parametrize(
    "root, deps, expected",
    [
        ("root", {"root": []}, set()),
        ("root", {"root": [], "etl": ["root"]}, {"etl"}),
        (
            "root",
            {"root": [], "transitive": ["root"], "etl": ["transitive"]},
            {"etl", "transitive"},
        ),
        (
            "root",
            {
                "root": [],
                "diamond_left": ["root"],
                "diamond_right": ["root"],
                "etl": ["diamond_left", "diamond_right"],
            },
            {"etl", "diamond_left", "diamond_right"},
        ),
        (
            "diamond_left",
            {
                "root": [],
                "diamond_left": ["root"],
                "diamond_right": ["root"],
                "etl": ["diamond_left", "diamond_right"],
            },
            {"etl"},
        ),
        (
            "etl",
            {
                "root": [],
                "diamond_left": ["root"],
                "diamond_right": ["root"],
                "etl": ["diamond_left", "diamond_right"],
            },
            set(),
        ),
        (
            "root",
            {
                "root": [],
                "cycle1": ["root", "cycle2"],
                "cycle2": ["cycle1"],
                "etl": ["cycle2"],
            },
            {"etl", "cycle1", "cycle2"},
        ),
        (
            "cycle1",
            {
                "root": [],
                "cycle1": ["root", "cycle2"],
                "cycle2": ["cycle1"],
                "etl": ["cycle2"],
            },
            {"etl", "cycle2"},
        ),
        (
            "cycle2",
            {
                "root": [],
                "cycle1": ["root", "cycle2"],
                "cycle2": ["cycle1"],
                "etl": ["cycle2"],
            },
            {"etl", "cycle1"},
        ),
    ],
)
def test_get_dependant_services(root, deps, expected):
    with mock.patch(
        "tools.service_utils.get_service_dependencies",
        lambda service: deps[service],
    ), mock.patch(
        "tools.service_utils.collect_all_services",
        mock.Mock(return_value=[{"name": service} for service in deps.keys()]),
    ):
        actual = set(tools.service_utils.get_dependent_services(root))
    assert actual == expected
