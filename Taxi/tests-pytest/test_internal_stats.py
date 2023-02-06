import datetime

import pytest

from taxi.internal import stats


@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('async')
def test_usage():
    # We have to create a class on each type of raw statistics entity

    class MyStat(stats._base.Stat):
        name = 'my_stat'

        def __init__(self, first, second):
            super(MyStat, self).__init__()
            self._common.update({
                'first': first,
                'second': second,
            })

        def add(self, third, forth):
            self._add(third=third, forth=forth)

    class AnotherStat(MyStat):
        name = 'another'

        def add(self, fifth):
            self._add(fifth=fifth)

    # Usage:
    stat = stats.Collection(my=MyStat(1, 2), another=AnotherStat('one', 'two'))
    stat.my.add(3, 4)
    stat.my.add(33, 44)
    stat.another.add('five')
    stat.another.add(5)

    # This part is not implemented yet
    stat.save()

    # But! There are dicts with statistics in each of `Stat` instances.
    # Each dict contains 'created' field. We gonna save this stat when
    # we implement an storage.
    now = datetime.datetime.utcnow()
    assert stat.my._stat_dicts == [
        {'created': now, 'first': 1, 'second': 2, 'third': 3, 'forth': 4},
        {'created': now, 'first': 1, 'second': 2, 'third': 33, 'forth': 44},
    ]
    assert stat.another._stat_dicts == [
        {'created': now, 'first': 'one', 'second': 'two', 'fifth': 'five'},
        {'created': now, 'first': 'one', 'second': 'two', 'fifth': 5},
    ]
