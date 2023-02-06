import pytest

import sandbox.common.types.task as ctt
from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShoot2.utils import generate_semaphores, update_shoot_statuses


@pytest.mark.parametrize(('final_statuses', 'statuses', 'expected'), [
    (
        {},
        {},
        {}
    ),
    (
        {},
        {'OK': 0, 'BadYabsHTTPCode': 0},
        {'OK': 0, 'BadYabsHTTPCode': 0}
    ),
    (
        {},
        {'BadYabsHTTPCode': 0},
        {'BadYabsHTTPCode': 0}
    ),
    (
        {'OK': 1, 'BadYabsHTTPCode': 3},
        {'OK': 3, 'BadYabsHTTPCode': 4},
        {'OK': 4, 'BadYabsHTTPCode': 7}
    ),
    (
        {'OK': 1, 'BadYabsHTTPCode': 3, 'BadExts': 100},
        {'OK': 3, 'BadYabsHTTPCode': 4, 'BadExts': 1},
        {'OK': 4, 'BadYabsHTTPCode': 7, 'BadExts': 1}
    ),
    (
        {'OK': 1, 'BadYabsHTTPCode': 3, 'UnknownStatus': 100},
        {'OK': 3, 'BadYabsHTTPCode': 4, 'UnknownStatus': 1},
        {'OK': 4, 'BadYabsHTTPCode': 7, 'UnknownStatus': 1}
    ),
])
def test_update_shoot_statuses(final_statuses, statuses, expected):
    assert update_shoot_statuses(final_statuses, statuses) == expected


def test_generate_semaphores():
    """Test generating semaphores for the shoot task.
    """
    hamsters = {"service_a": 1, "service_b": 2, "service_c": 3}
    capacity = {"service_a": 10, "service_b": 20}

    expected = [
        ctt.Semaphores.Acquire(name="yabs_server_hamster_service_a_1", weight=1, capacity=10),
        ctt.Semaphores.Acquire(name="yabs_server_hamster_service_b_2", weight=1, capacity=20),
    ]
    assert set(expected) == set(generate_semaphores(hamsters, capacity))
