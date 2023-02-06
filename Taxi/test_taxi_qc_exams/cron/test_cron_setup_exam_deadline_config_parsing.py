# pylint: disable=W0212
import datetime

import pytest

from taxi_qc_exams.crontasks import setup_exam_deadlines


@pytest.mark.parametrize(
    'dates_config',
    [
        (
            [
                dict(
                    date_begin='10-01',
                    date_end='05-01',
                    ranges=[dict(time_begin='9:00', time_end='12:00')],
                ),
                dict(
                    date_begin='05-02',
                    date_end='09-30',
                    ranges=[dict(time_begin='17:00', time_end='2:00')],
                ),
            ]
        ),
        ([dict(date_begin='05-02', date_end='09-30', ranges=[])]),
    ],
)
def test_parse_dates_config_success(dates_config):
    parsed = setup_exam_deadlines._parse_dates_config(dates_config)
    assert parsed

    assert len(parsed) == len(dates_config)


@pytest.mark.parametrize(
    'dates_config',
    [
        (
            [
                dict(
                    date_begin='10-01',
                    date_end='15-01',
                    ranges=[dict(time_begin='9:00', time_end='12:00')],
                ),
            ]
        ),
        (
            [
                dict(
                    date_begin='05-02',
                    date_end='09-30',
                    ranges=[dict(time_begin='17:00', time_end='24:00')],
                ),
            ]
        ),
        (
            [
                dict(
                    date_begin='05-02',
                    ranges=[dict(time_begin='17:00', time_end='14:00')],
                ),
            ]
        ),
        (
            [
                dict(
                    date_begin='05-02',
                    date_end='09-30',
                    ranges=[dict(time_begin='17:00')],
                ),
            ]
        ),
    ],
)
def test_parse_dates_config_error(dates_config):
    parsed = setup_exam_deadlines._parse_dates_config(dates_config)
    assert not parsed


def _date(month: int, day: int) -> datetime.date:
    return datetime.date(1900, month, day)


@pytest.mark.parametrize(
    'exam_config, parsed_result',
    [
        (
            {
                '__default__': [
                    dict(date_begin='10-01', date_end='09-01', ranges=[]),
                ],
                'spb': [
                    dict(
                        date_begin='10-01',
                        date_end='05-01',
                        ranges=[dict(time_begin='9:00', time_end='12:00')],
                    ),
                    dict(
                        date_begin='05-02',
                        date_end='09-30',
                        ranges=[dict(time_begin='17:00', time_end='2:30')],
                    ),
                ],
            },
            [
                {
                    'zones': [],
                    'date_ranges': [
                        dict(
                            date_begin=_date(10, 1),
                            date_end=_date(9, 1),
                            ranges=[],
                        ),
                    ],
                },
                {
                    'zones': ['spb'],
                    'date_ranges': [
                        dict(
                            date_begin=_date(10, 1),
                            date_end=_date(5, 1),
                            ranges=[
                                dict(
                                    time_begin=datetime.time(hour=9, minute=0),
                                    time_end=datetime.time(hour=12, minute=0),
                                ),
                            ],
                        ),
                        dict(
                            date_begin=_date(5, 2),
                            date_end=_date(9, 30),
                            ranges=[
                                dict(
                                    time_begin=datetime.time(
                                        hour=17, minute=0,
                                    ),
                                    time_end=datetime.time(hour=2, minute=30),
                                ),
                            ],
                        ),
                    ],
                },
            ],
        ),
        (
            {
                '__default__': [
                    dict(date_begin='05-02', date_end='09-30', ranges=[]),
                ],
                'spb': [
                    dict(
                        date_begin='10-01',
                        date_end='15-01',
                        ranges=[dict(time_begin='9:00', time_end='12:00')],
                    ),
                ],
            },
            [
                {
                    'zones': [],
                    'date_ranges': [
                        dict(
                            date_begin=_date(5, 2),
                            date_end=_date(9, 30),
                            ranges=[],
                        ),
                    ],
                },
            ],
        ),
    ],
)
def test_parse_old_exam_config(exam_config, parsed_result):
    parsed = setup_exam_deadlines._parse_exam_config(exam_config)
    assert parsed == parsed_result


@pytest.mark.parametrize(
    'exam_config',
    [
        {
            'spb': [
                dict(
                    date_begin='10-01',
                    date_end='05-01',
                    ranges=[dict(time_begin='9:00', time_end='12:00')],
                ),
                dict(
                    date_begin='05-02',
                    date_end='09-30',
                    ranges=[dict(time_begin='17:00', time_end='2:30')],
                ),
            ],
        },
        {
            '__default__': [
                dict(
                    date_begin='10-01',
                    date_end='09-01',
                    ranges=[dict(time_begin='9:00', time_end='24:00')],
                ),
            ],
            'spb': [
                dict(
                    date_begin='10-01',
                    date_end='05-01',
                    ranges=[dict(time_begin='9:00', time_end='12:00')],
                ),
                dict(
                    date_begin='05-02',
                    date_end='09-30',
                    ranges=[dict(time_begin='17:00', time_end='2:30')],
                ),
            ],
        },
    ],
)
def test_parse_old_exam_config_err(exam_config):
    parsed = setup_exam_deadlines._parse_exam_config(exam_config)
    assert not parsed


@pytest.mark.parametrize(
    'exam_config, parsed_result',
    [
        (
            [
                {
                    'date_ranges': [
                        dict(date_begin='10-01', date_end='09-01', ranges=[]),
                    ],
                },
                {
                    'zones': ['spb'],
                    'date_ranges': [
                        dict(
                            date_begin='10-01',
                            date_end='05-01',
                            ranges=[dict(time_begin='9:00', time_end='12:00')],
                        ),
                        dict(
                            date_begin='05-02',
                            date_end='09-30',
                            ranges=[dict(time_begin='17:00', time_end='2:30')],
                        ),
                    ],
                },
            ],
            [
                {
                    'zones': [],
                    'date_ranges': [
                        dict(
                            date_begin=_date(10, 1),
                            date_end=_date(9, 1),
                            ranges=[],
                        ),
                    ],
                },
                {
                    'zones': ['spb'],
                    'date_ranges': [
                        dict(
                            date_begin=_date(10, 1),
                            date_end=_date(5, 1),
                            ranges=[
                                dict(
                                    time_begin=datetime.time(hour=9, minute=0),
                                    time_end=datetime.time(hour=12, minute=0),
                                ),
                            ],
                        ),
                        dict(
                            date_begin=_date(5, 2),
                            date_end=_date(9, 30),
                            ranges=[
                                dict(
                                    time_begin=datetime.time(
                                        hour=17, minute=0,
                                    ),
                                    time_end=datetime.time(hour=2, minute=30),
                                ),
                            ],
                        ),
                    ],
                },
            ],
        ),
        (
            [
                {
                    'zones': [],
                    'date_ranges': [
                        dict(date_begin='05-02', date_end='09-30', ranges=[]),
                    ],
                },
                {
                    'zones': ['spb'],
                    'date_ranges': [
                        dict(
                            date_begin='10-01',
                            date_end='15-01',
                            ranges=[dict(time_begin='9:00', time_end='12:00')],
                        ),
                    ],
                },
            ],
            [
                {
                    'zones': [],
                    'date_ranges': [
                        dict(
                            date_begin=_date(5, 2),
                            date_end=_date(9, 30),
                            ranges=[],
                        ),
                    ],
                },
            ],
        ),
    ],
)
def test_parse_new_exam_config(exam_config, parsed_result):
    parsed = setup_exam_deadlines._parse_exam_config(exam_config)
    assert parsed == parsed_result


@pytest.mark.parametrize(
    'exam_config',
    [
        [
            {
                'zones': ['spb'],
                'date_ranges': [
                    dict(
                        date_begin='10-01',
                        date_end='05-01',
                        ranges=[dict(time_begin='9:00', time_end='12:00')],
                    ),
                    dict(
                        date_begin='05-02',
                        date_end='09-30',
                        ranges=[dict(time_begin='17:00', time_end='2:30')],
                    ),
                ],
            },
        ],
        [
            {
                'date_ranges': [
                    dict(
                        date_begin='10-01',
                        date_end='09-01',
                        ranges=[dict(time_begin='9:00', time_end='24:00')],
                    ),
                ],
            },
            {
                'zones': ['spb'],
                'date_ranges': [
                    dict(
                        date_begin='10-01',
                        date_end='05-01',
                        ranges=[dict(time_begin='9:00', time_end='12:00')],
                    ),
                    dict(
                        date_begin='05-02',
                        date_end='09-30',
                        ranges=[dict(time_begin='17:00', time_end='2:30')],
                    ),
                ],
            },
        ],
    ],
)
def test_parse_new_exam_config_err(exam_config):
    parsed = setup_exam_deadlines._parse_exam_config(exam_config)
    assert not parsed
