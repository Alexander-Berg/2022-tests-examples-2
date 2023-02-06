# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from taxi.util import helpers
from taxi.internal import requirement_manager


@pytest.mark.parametrize(
    'seconds,expected_result',
    [
        (5, '1 min'),
        (61, '2 min'),
        (25 * 60, '25 min'),
        (37 * 60, '40 min'),
        (55 * 60, '55 min'),
        (56 * 60, '1 h'),
        (3600 + 5 * 60, '1 h 10 min'),
        (3600 + 4 * 60, '1 h 10 min'),
        (23 * 3600 + 50 * 60, '23 h 50 min'),
        (23 * 3600 + 51 * 60, '1 d'),
        (86400 + 16 * 3600, '1 d 16 h'),
        (86400 * 2 + 23 * 3600, '2 d 23 h'),
        (86400 * 2 + 23 * 3600 + 1, '3 d'),
        (86400 * 7 + 3600 * 3, '8 d'),
    ],
)
@pytest.mark.translations(
    [
        ('tariff', 'round.minute', 'en', '%(value)d min'),
        ('tariff', 'round.tens_minutes', 'en', '%(value)d min'),
        ('tariff', 'round.almost_hour', 'en', '%(value)d min'),
        ('tariff', 'round.hours', 'en', '%(value)d h'),
        ('tariff', 'round.hours_mintes', 'en', '%(hours)d h %(minutes)d min'),
        ('tariff', 'round.days', 'en', '%(value)d d'),
        ('tariff', 'round.days_hours', 'en', '%(days)d d %(hours)d h'),
    ],
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb(_fill=False)
def test_round_time_original(seconds, expected_result):
    result = helpers.round_time(seconds, 'en')
    assert result == expected_result


@pytest.mark.parametrize(
    'seconds,expected_result',
    [
        (5, '1 min'),
        (61, '2 min'),
        (25 * 60, '25 min'),
        (37 * 60, '37 min'),
        (55 * 60, '55 min'),
        (56 * 60, '56 min'),
        (59 * 60 + 50, '1 h'),
        (3600 + 5 * 60, '1 h 5 min'),
        (3600 + 4 * 60, '1 h 4 min'),
        (23 * 3600 + 50 * 60, '23 h 50 min'),
        (23 * 3600 + 51 * 60, '23 h 51 min'),
        (23 * 3600 + 59 * 60, '23 h 59 min'),
        (23 * 3600 + 59 * 60 + 1, '1 d'),
        (86400 + 16 * 3600, '1 d 16 h'),
        (86400 * 2 + 23 * 3600, '2 d 23 h'),
        (86400 * 2 + 23 * 3600 + 1, '3 d'),
        (86400 * 7 + 3600 * 3, '8 d'),
    ],
)
@pytest.mark.translations(
    [
        ('tariff', 'round.minute', 'en', '%(value)d min'),
        ('tariff', 'round.tens_minutes', 'en', '%(value)d min'),
        ('tariff', 'round.almost_hour', 'en', '%(value)d min'),
        ('tariff', 'round.hours', 'en', '%(value)d h'),
        ('tariff', 'round.hours_mintes', 'en', '%(hours)d h %(minutes)d min'),
        ('tariff', 'round.days', 'en', '%(value)d d'),
        ('tariff', 'round.days_hours', 'en', '%(days)d d %(hours)d h'),
    ],
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb(_fill=False)
def test_round_time_original_no_round_minutes(seconds, expected_result):
    result = helpers.round_time(seconds, 'en', round_minutes=False)
    assert result == expected_result


@pytest.mark.parametrize(
    'req, expected',
    [
        (('hourly_rental', 2), 'Booking 2 hours'),
        (('hourly_rental', 3), 'Booking 3 hours fallback'),
    ],
)
@pytest.mark.translations(
    [
        (
            'client_messages',
            'requirement.hourly_rental.2_hours_driver_title',
            'en',
            'Booking 2 hours',
        ),
        (
            'client_messages',
            'requirement.hourly_rental.3_hours_title',
            'en',
            'Booking 3 hours fallback',
        ),
    ],
)
@pytest.inline_callbacks
def test_translate_requirement(req, expected):
    mapping = yield requirement_manager.get_c2d_requirements_mapper(
        extended=True,
    )
    result = helpers.translate_requirement(req, mapping, 'en')
    assert result == expected


@pytest.mark.parametrize(
    'seconds,expected_result',
    [
        (1, '1 s'),
        (60, '1 min'),
        (60 * 4 + 59, '4 min 59 s'),
        (60 * 5 + 1, '5 min'),
        (3600, '1 h'),
        (3600 + 2 * 60, '1 h 2 min'),
        (3600 + 1, '1 h'),
    ],
)
@pytest.mark.translations(
    [
        ('tariff', 'detailed.hours', 'en', '%(value)d h'),
        ('tariff', 'detailed.minutes', 'en', '%(value)d min'),
        ('tariff', 'detailed.seconds', 'en', '%(value)d s'),
    ],
)
@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb(_fill=False)
def test_detailed_time(seconds, expected_result):
    assert expected_result == helpers.detailed_time(seconds, 'en')
