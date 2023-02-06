from demand_etl.layer.yt.cdm.user_rating.user_rating_history.impl import calculate_rating_stat


def test_rating_calculation():
    for rating_list, expected in (
        ([], (40, 5.0, None)),
        (10 * [4], (30, 4.57, 4.0)),
        (30 * [5] + 10 * [4], (0, 4.57, 4.57)),
        (10 * [4] + 30 * [5], (0, 4.93, 4.93)),
        (20 * [3] + 20 * [4], (0, 3.74, 3.74)),
        (20 * [4] + 20 * [3], (0, 3.26, 3.26)),
        (30 * [5] + 30 * [4], (0, 4.25, 4.25)),
        (30 * [4] + 30 * [5], (0, 4.75, 4.75)),
        (40 * [4] + 60 * [5], (0, 4.84, 4.84)),
        (40 * [5] + 60 * [4], (0, 4.16, 4.16)),
        (75 * [5] + 75 * [4], (0, 4.06, 4.06)),
        (75 * [4] + 75 * [5], (0, 4.94, 4.94)),
        (10 * [2] + 10 * [None] + 10 * [3], (10, 3.57, 3.55)),
        (30 * [2] + 10 * [None] + 10 * [3], (0, 3.19, 3.19)),
        (80 * [2] + 10 * [None] + 10 * [3], (0, 2.7, 2.7)),
        (100 * [2] + 10 * [None] + 10 * [3], (0, 2.7, 2.7)),
        (40 * [None], (0, 5.0, 5.0)),
        (60 * [None], (0, 5.0, 5.0)),
        (100 * [None], (0, 5.0, 5.0)),
        (120 * [None], (0, 5.0, 5.0)),
        (10 * [None], (30, 5.0, 5.0))
    ):
        actual = calculate_rating_stat(rating_list)

        assert (expected == actual), \
            'Expected rating is different from actual:\nexpected: {},\nactual: {}\ntest sample: {}'.format(
                expected, actual, rating_list
            )
