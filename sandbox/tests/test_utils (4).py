import pytest
from sandbox.projects.yabs.qa.tasks.YabsServerFreezeCurrentKvrsSaasSnapshot.utils import validate_states


@pytest.mark.parametrize(("states", "namespace_count", "expected_missing_namespaces"), [
    (
        [{"Namespace": "test-0", "StateId": 0}],
        {"test": 1},
        []
    ),
    (
        [
            {"Namespace": "test-1", "StateId": 0},
            {"Namespace": "foo-2", "StateId": 0},
            {"Namespace": "xxx-3", "StateId": 0},
        ],
        {"test": 2, "foo": 2},
        [
            "test-0",
            "foo-0", "foo-1"
        ]
    ),
])
def test_valiadate_states(states, namespace_count, expected_missing_namespaces):
    assert set(validate_states(states, namespace_count)) == set(expected_missing_namespaces)
