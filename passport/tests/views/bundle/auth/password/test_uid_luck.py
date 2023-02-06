# -*- coding: utf-8 -*-
from nose.tools import (
    assert_almost_equal,
    eq_,
    nottest,
)
from passport.backend.api.views.bundle.mixins.challenge import is_lucky_uid
from passport.backend.utils.time import get_unixtime


@nottest
def test_luck(uids, buckets, chance):
    """
    Здесь проверяется функция определения везунчиков, кому показывать челлендж.

    Вкратце сама функция работает так:
    на некий период времени (3600 секунд, например) выделяется некий диапазон уидов, которым показывается челлендж.

    Поэтому в тестах мы этот период сдвигаем и проверяем, что счастливые уиды не пересекаются при этом,
    что в каждый новый временной интервал повезёт новой партии уидов, которой не везло раньше.
    """
    period = 3600

    now = get_unixtime()
    now -= now % period  # округляю таймстемп до 0 минут 0 секунд

    timestamps_to_test = [
        now - period,
        now - period / 2,
        now,
        now + period / 2,
        now + period,
        now + period * 1.5,
    ]
    lucky_uids_list = []

    for timestamp in timestamps_to_test:
        lucky_uids = set()
        lucky_uids_list.append(lucky_uids)

        for uid in uids:
            lucky = is_lucky_uid(uid, timestamp, chance, buckets, period)
            if lucky:
                lucky_uids.add(uid)

        affected_uids_ratio = float(len(lucky_uids)) / len(uids)
        assert_almost_equal(
            affected_uids_ratio,
            chance,
            places=3,
            msg="{} != {}; Total uids: {}, lucky estimate: {}, actually lucky: {}".format(
                affected_uids_ratio,
                chance,
                len(uids),
                len(uids) * chance,
                len(lucky_uids),
            ),
        )

    # проверяем отсутствие пересечения везучих уидов при шансе != 1.0, если события произошли в разные часы
    for uids1, uids2 in zip(lucky_uids_list[::2], lucky_uids_list[2::2]):
        intersection = uids1 & uids2
        eq_(intersection, set(uids) if chance == 1.0 else set())

    # проверяем наличие полного пересечения везучих уидов, если события произошли в один час
    for uids1, uids2 in zip(lucky_uids_list[::2], lucky_uids_list[1::2]):
        eq_(uids1, uids2)


def test_luck_05_chance():
    """Везёт половине пользователей."""
    uids = range(10000, 20000)
    buckets = 10000
    chance = 0.5
    test_luck(uids, buckets, chance)


def test_luck_0_chance():
    """Никому не должно повезти с нулевым шансом."""
    uids = range(10000, 20000)
    buckets = 10000
    chance = 0.0
    test_luck(uids, buckets, chance)


def test_luck_1_chance():
    """С шансом равным единице везёт всем."""
    uids = range(10000, 20000)
    buckets = 10000
    chance = 1.0
    test_luck(uids, buckets, chance)


def test_luck_0001_chance():
    """Везёт только 0.001 части пользователей."""
    uids = range(10000, 20000)
    buckets = 10000
    chance = 0.001
    test_luck(uids, buckets, chance)


def test_luck_lots_uids_0001_chance():
    """Когда уидов много и их количество не кратно 10, везёт всё равно пропорциональной части."""
    uids = range(2 ** 16, 2 ** 17)
    buckets = 10000
    chance = 0.001
    test_luck(uids, buckets, chance)
