import sys
sys.path.append('../')

from datetime import timedelta

import scheduling #pylint: disable=E0401

from helpers import DateTime #pylint: disable=E0401

def test_generate_slots():
    # 7 people, 1 day long, skip weekend
    for hour in xrange(24):
        # Tuesday
        start_time = DateTime(year=2018, month=10, day=30, hour=hour, minute=33, zone='msk')
        first_end_time = DateTime(year=2018, month=10, day=31, hour=12, zone='msk')

        slots = scheduling.generate_slots(start_time, 1, True, 12, 7)

        assert len(slots) == 7

        expected_slots = [
            (start_time, first_end_time), # Still Tuesday
            (first_end_time, first_end_time + timedelta(days=1)), # Wednesday
            (first_end_time + timedelta(days=1), first_end_time + timedelta(days=2)), # Thursday
            (first_end_time + timedelta(days=2), first_end_time + timedelta(days=3)), # Friday
            (first_end_time + timedelta(days=5), first_end_time + timedelta(days=6)), # Monday
            (first_end_time + timedelta(days=6), first_end_time + timedelta(days=7)), # Tuesday
            (first_end_time + timedelta(days=7), first_end_time + timedelta(days=8)), # Thursday
        ]

        for i, slot in enumerate(slots):
            assert slot['from'] == expected_slots[i][0]
            assert slot['to'] == expected_slots[i][1]

    # 7 people, 1 day long, include weekend
    for hour in xrange(24):
        # Tuesday
        start_time = DateTime(year=2018, month=10, day=30, hour=hour, minute=33, zone='msk')
        first_end_time = DateTime(year=2018, month=10, day=31, hour=12, zone='msk')

        slots = scheduling.generate_slots(start_time, 1, False, 12, 7)

        assert len(slots) == 7

        expected_slots = [
            (start_time, first_end_time), # Still Tuesday
            (first_end_time, first_end_time + timedelta(days=1)), # Wednesday
            (first_end_time + timedelta(days=1), first_end_time + timedelta(days=2)), # Thursday
            (first_end_time + timedelta(days=2), first_end_time + timedelta(days=3)), # Friday
            (first_end_time + timedelta(days=3), first_end_time + timedelta(days=4)), # Saturday
            (first_end_time + timedelta(days=4), first_end_time + timedelta(days=5)), # Sunday
            (first_end_time + timedelta(days=5), first_end_time + timedelta(days=6)), # Monday
        ]

        for i, slot in enumerate(slots):
            assert slot['from'] == expected_slots[i][0]
            assert slot['to'] == expected_slots[i][1]


    # 3 people, 5 days long, skip weekend
    for hour in xrange(24):
        # Tuesday
        start_time = DateTime(year=2018, month=10, day=30, hour=hour, minute=33, zone='msk')
        first_end_time = DateTime(year=2018, month=11, day=4, hour=12, zone='msk')
        next_monday = DateTime(year=2018, month=11, day=5, hour=12, zone='msk')

        slots = scheduling.generate_slots(start_time, 5, True, 12, 3)

        assert len(slots) == 3

        expected_slots = [
            (start_time, first_end_time), # Tuesday - Sunday (bad corner case)
            (next_monday, next_monday + timedelta(days=5)), # Monday - Friday
            (next_monday + timedelta(days=7), next_monday + timedelta(days=12)),
        ]

        for i, slot in enumerate(slots):
            assert slot['from'] == expected_slots[i][0]
            assert slot['to'] == expected_slots[i][1]

    # 3 people, 7 days long
    for hour in xrange(24):
        # Tuesday
        start_time = DateTime(year=2018, month=10, day=30, hour=hour, minute=33, zone='msk')

        slots_skipping = slots = scheduling.generate_slots(start_time, 7, True, 12, 3)
        slots_including = slots = scheduling.generate_slots(start_time, 7, False, 12, 3)

        assert len(slots_skipping) == len(slots_including)

        for i, slot in enumerate(slots_skipping):
            slot['from'] == slots_including[i]['from']
            slot['to'] == slots_including[i]['to']

def test_make_weighted_scheduling_table():
    start_time = DateTime(year=2018, month=10, day=30, hour=12, minute=33, zone='msk')
    slots3 = scheduling.generate_slots(start_time, 7, False, 12, 3)
    people3 = ['person1', 'person2', 'person3']

    # No gaps
    gaps = {}
    scheduling_table = scheduling.make_weighted_scheduling_table(people3, slots3, gaps)
    reference_table = [
        [0, 100, 200],
        [200, 0, 100],
        [400, 200, 0]
    ]

    for i in range(3):
        for j in range(3):
            assert reference_table[i][j] == scheduling_table[i][j]

    # Gap in preferred slot
    gaps = {
        'person1': [{
            'from': DateTime(year=2018, month=10, day=31, zone='msk'),
            'to': DateTime(year=2018, month=11, day=1, zone='msk'),
        }]
    }
    scheduling_table = scheduling.make_weighted_scheduling_table(people3, slots3, gaps)
    reference_table = [
        [10000, 100, 200],
        [200, 0, 100],
        [400, 200, 0]
    ]

    for i in range(3):
        for j in range(3):
            assert reference_table[i][j] == scheduling_table[i][j]


    # Gap in other slot
    gaps = {
        'person2': [{
            'from': DateTime(year=2018, month=10, day=31, zone='msk'),
            'to': DateTime(year=2018, month=11, day=1, zone='msk'),
        }]
    }
    scheduling_table = scheduling.make_weighted_scheduling_table(people3, slots3, gaps)
    reference_table = [
        [0, 100, 200],
        [10000, 0, 100],
        [400, 200, 0]
    ]

    for i in range(3):
        for j in range(3):
            assert reference_table[i][j] == scheduling_table[i][j]


def test_fake_weighted_scheduling_table():
    start_time = DateTime(year=2018, month=10, day=30, hour=12, minute=33, zone='msk')
    slots3 = scheduling.generate_slots(start_time, 7, False, 12, 3)
    people3 = ['person1', 'person2', 'person3']

    scheduling_table = scheduling.fake_weighted_scheduling_table(people3, slots3)
    reference_table = [
        [0, 10000, 10000],
        [10000, 0, 10000],
        [10000, 10000, 0]
    ]

    for i in range(3):
        for j in range(3):
            assert reference_table[i][j] == scheduling_table[i][j]


def test_find_optimal_schedule():
    start_time = DateTime(year=2018, month=10, day=30, hour=12, minute=33, zone='msk')
    slots3 = scheduling.generate_slots(start_time, 7, False, 12, 3)
    people3 = ['person1', 'person2', 'person3']

    # No gaps
    gaps = {}
    scheduling_table = scheduling.make_weighted_scheduling_table(people3, slots3, gaps)

    schedule = scheduling.find_optimal_schedule(people3, slots3, scheduling_table)
    assert len(schedule) == len(people3)

    assert schedule[0][0] == people3[0]
    assert schedule[1][0] == people3[1]
    assert schedule[2][0] == people3[2]

    for i in range(3):
        assert schedule[i][1]['from'] == slots3[i]['from']
        assert schedule[i][1]['to'] == slots3[i]['to']

    # Gap in preferred slot
    gaps = {
        'person1': [{
            'from': DateTime(year=2018, month=10, day=31, zone='msk'),
            'to': DateTime(year=2018, month=11, day=1, zone='msk'),
        }]
    }
    scheduling_table = scheduling.make_weighted_scheduling_table(people3, slots3, gaps)

    schedule = scheduling.find_optimal_schedule(people3, slots3, scheduling_table)
    assert len(schedule) == len(people3)

    assert schedule[0][0] == people3[1]
    assert schedule[1][0] == people3[0]
    assert schedule[2][0] == people3[2]

    for i in range(3):
        assert schedule[i][1]['from'] == slots3[i]['from']
        assert schedule[i][1]['to'] == slots3[i]['to']

    # Gap in other slot
    gaps = {
        'person2': [{
            'from': DateTime(year=2018, month=10, day=31, zone='msk'),
            'to': DateTime(year=2018, month=11, day=1, zone='msk'),
        }]
    }
    scheduling_table = scheduling.make_weighted_scheduling_table(people3, slots3, gaps)

    schedule = scheduling.find_optimal_schedule(people3, slots3, scheduling_table)
    assert len(schedule) == len(people3)

    assert schedule[0][0] == people3[0]
    assert schedule[1][0] == people3[1]
    assert schedule[2][0] == people3[2]

    for i in range(3):
        assert schedule[i][1]['from'] == slots3[i]['from']
        assert schedule[i][1]['to'] == slots3[i]['to']

    # Double gap
    gaps = {
        'person1': [{
            'from': DateTime(year=2018, month=10, day=31, zone='msk'),
            'to': DateTime(year=2018, month=11, day=1, zone='msk'),
        }],
        'person2': [{
            'from': DateTime(year=2018, month=10, day=31, zone='msk'),
            'to': DateTime(year=2018, month=11, day=1, zone='msk'),
        }]
    }
    scheduling_table = scheduling.make_weighted_scheduling_table(people3, slots3, gaps)

    schedule = scheduling.find_optimal_schedule(people3, slots3, scheduling_table)
    assert len(schedule) == len(people3)

    assert schedule[0][0] == people3[2]
    assert schedule[1][0] == people3[0]
    assert schedule[2][0] == people3[1]

    for i in range(3):
        assert schedule[i][1]['from'] == slots3[i]['from']
        assert schedule[i][1]['to'] == slots3[i]['to']
