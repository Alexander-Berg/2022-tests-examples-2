import pytest

from taxi.internal import dbh
from taxi_maintenance.stuff import exams_apply


@pytest.mark.parametrize('id,only_newbie,result_score', [
    ('newbie_no_exam', True, 5),
    ('newbie_bad_exam', True, 5),
    ('acknowledged', True, 4),
    ('ordinary', True, 4),
    ('time_traveler', True, 4),

    ('newbie_no_exam', False, 5),
    ('newbie_bad_exam', False, 5),
    ('acknowledged', False, 5),
    ('ordinary', False, 5),
    ('time_traveler', False, 4)
])
@pytest.inline_callbacks
def test_exams_apply(id, only_newbie, result_score):
    yield exams_apply.update_exam_results(only_newbies=only_newbie)
    new = yield dbh.unique_drivers.Doc.find_one_by_id(id)
    assert new.exam_score == result_score
