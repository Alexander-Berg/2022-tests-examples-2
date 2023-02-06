import pytest

from projects.signalq.markup.v2.trange_markup import set_aggregation
from projects.signalq.markup.v2.trange_markup import set_intersection
from projects.signalq.markup.v2.trange_markup import set_power
from projects.signalq.markup.v2.trange_markup import intersection_opt
from projects.signalq.markup.v2.trange_markup import union_opt
from projects.signalq.markup.v2.trange_markup import iou


def test_cut_set_intersection():
    section = set_intersection(
        lhs=[(0.0, 1.0), (2.0, 3.0)], rhs=[(0.1, 0.9), (2.1, 3.2)],
    )
    assert set_power(section) == 1.7


def test_set_aggregation_one_of_two_empty():

    cut_sets = [[], [(0.0, 1.0), (2.0, 3.0)]]
    aggregate = set_aggregation(cut_sets)

    assert aggregate.check_candidate


def test_set_aggregation_one_of_three_empty():
    cut_sets = [[], [(0.0, 1.0), (2.0, 3.0)], [(0.0, 1.0), (2.0, 3.5)]]
    aggregate = set_aggregation(cut_sets)

    assert aggregate.iou > 0.5 and not aggregate.check_candidate


def test_set_aggregation_two_of_three_empty():
    cut_sets = [[], [], [(0.0, 1.0), (2.0, 3.5)]]
    aggregate = set_aggregation(cut_sets)

    assert aggregate.check_candidate


def test_set_aggregation_one_of_three_incomplete():
    cut_sets = [
        [(0.0, 0.1)],
        [(0.0, 1.0), (2.0, 3.0)],
        [(0.0, 1.0), (2.0, 3.5)],
    ]
    aggregate = set_aggregation(cut_sets)

    assert aggregate.iou > 0.5 and not aggregate.check_candidate


@pytest.mark.filterwarnings('ignore:tostring()')
def test_opt_iou():
    lhs, rhs = (0.1, 0.5), (0.4, 0.7)

    union = union_opt(lhs, rhs, border_error=0.1)
    section = intersection_opt(lhs, rhs, border_error=0.1)

    assert iou(lhs, rhs) < set_power([section]) / set_power(union)
