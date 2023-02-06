import dateutil.parser

PARAMETRIZE_YT_DATA = [
    [
        [
            'some_file_id1a',
            'd1',
            1607779800,
            'event_id1',
            'distraction',
        ],  # 2020-12-12T16:30:00+03:00
        [
            'some_file_id2a',
            'd2',
            1607779900,
            'event_id2',
            'driver_lost',
        ],  # 2020-12-12T16:31:40+03:00
        [
            'some_file_id3a',
            'd3',
            1607771000,
            'event_id3',
            'distraction',
        ],  # 2020-12-12T14:03:20+03:00
        [
            'some_file_id4a',
            'd4',
            1607771100,
            'event_id4',
            'tired',
        ],  # 2020-12-12T14:05:00+03:00
        [
            'some_file_id5a',
            'd4',
            1607791100,
            'event_id5',
            'tired',
        ],  # 2020-12-12T19:38:20+03:00
        [
            'some_file_id6a',
            'd4',
            1607791100,
            'event_id6',
            'smoking',
        ],  # 2020-12-12T19:38:20+03:00
        [
            'some_file_id7a',
            'd4',
            1607791100,
            'event_id7',
            'smoking',
        ],  # 2020-12-12T19:38:20+03:00
        [
            'some_file_id8a',
            'd4',
            1607792400,
            'event_id8',
            'seatbelt',
        ],  # 2020-12-12T20:00:00+03:00
        [
            'some_file_id9a',
            'd4',
            1607796000,
            'event_id9',
            'sleep',
        ],  # 2020-12-12T21:00:00+03:00
    ],
]


def get_db_result_at_start():
    return [
        (
            '__default__',
            dateutil.parser.parse('2020-10-01T00:00:00+03:00'),
            dateutil.parser.parse('2020-10-01T00:00:00+03:00'),
            '',
        ),
        (
            'distraction',
            dateutil.parser.parse('2020-11-01T00:00:00+03:00'),
            dateutil.parser.parse('2020-11-01T00:00:00+03:00'),
            '',
        ),
        (
            'fart',
            dateutil.parser.parse('2020-09-01T00:00:00+03:00'),
            dateutil.parser.parse('2020-09-01T00:00:00+03:00'),
            '',
        ),
        (
            'seatbelt',
            dateutil.parser.parse('2016-01-01T00:00:00+03:00'),
            dateutil.parser.parse('2020-05-01T00:00:00+03:00'),
            '',
        ),
        (
            'sleep',
            dateutil.parser.parse('2020-12-01T00:00:00+03:00'),
            dateutil.parser.parse('2016-01-01T00:00:00+03:00'),
            '',
        ),
    ]


def get_db_external_photo_result_at_start():  # pylint: disable=invalid-name
    return [
        (
            '__default__',
            dateutil.parser.parse('2020-10-01T00:00:00+03:00'),
            dateutil.parser.parse('2220-10-01T00:00:00+03:00'),
            dateutil.parser.parse('2120-10-01T00:00:00+03:00'),
            dateutil.parser.parse('2000-10-01T00:00:00+03:00'),
            '',
        ),
        (
            'distraction',
            dateutil.parser.parse('2020-11-01T00:00:00+03:00'),
            dateutil.parser.parse('2222-11-01T00:00:00+03:00'),
            dateutil.parser.parse('2120-10-01T00:00:00+03:00'),
            dateutil.parser.parse('2004-10-01T00:00:00+03:00'),
            '',
        ),
        (
            'fart',
            dateutil.parser.parse('2020-09-01T00:00:00+03:00'),
            dateutil.parser.parse('2221-09-01T00:00:00+03:00'),
            dateutil.parser.parse('2120-10-01T00:00:00+03:00'),
            dateutil.parser.parse('2003-10-01T00:00:00+03:00'),
            '',
        ),
        (
            'seatbelt',
            dateutil.parser.parse('2016-01-01T00:00:00+03:00'),
            dateutil.parser.parse('2220-05-01T00:00:00+03:00'),
            dateutil.parser.parse('2120-10-01T00:00:00+03:00'),
            dateutil.parser.parse('2001-10-01T00:00:00+03:00'),
            '',
        ),
        (
            'sleep',
            dateutil.parser.parse('2020-12-01T00:00:00+03:00'),
            dateutil.parser.parse('2010-01-01T00:00:00+03:00'),
            dateutil.parser.parse('2120-10-01T00:00:00+03:00'),
            dateutil.parser.parse('2002-10-01T00:00:00+03:00'),
            '',
        ),
    ]


def get_db_external_video_result_at_start():  # pylint: disable=invalid-name
    return [
        (
            '__default__',
            dateutil.parser.parse('2030-10-01T00:00:00+03:00'),
            dateutil.parser.parse('2020-10-01T00:00:00+03:00'),
            dateutil.parser.parse('2021-10-01T00:00:00+03:00'),
            dateutil.parser.parse('2023-10-01T00:00:00+03:00'),
            '',
            '',
        ),
        (
            'distraction',
            dateutil.parser.parse('2020-11-01T00:00:00+03:00'),
            dateutil.parser.parse('2020-11-01T00:00:00+03:00'),
            dateutil.parser.parse('2019-10-01T00:00:00+03:00'),
            dateutil.parser.parse('2017-10-01T00:00:00+03:00'),
            '',
            '',
        ),
        (
            'fart',
            dateutil.parser.parse('2020-09-01T00:00:00+03:00'),
            dateutil.parser.parse('2020-09-01T00:00:00+03:00'),
            dateutil.parser.parse('2221-10-01T00:00:00+03:00'),
            dateutil.parser.parse('2223-10-01T00:00:00+03:00'),
            '',
            '',
        ),
        (
            'seatbelt',
            dateutil.parser.parse('2016-01-01T00:00:00+03:00'),
            dateutil.parser.parse('2020-05-01T00:00:00+03:00'),
            dateutil.parser.parse('2121-10-01T00:00:00+03:00'),
            dateutil.parser.parse('2123-10-01T00:00:00+03:00'),
            '',
            '',
        ),
        (
            'sleep',
            dateutil.parser.parse('2020-12-01T00:00:00+03:00'),
            dateutil.parser.parse('2016-01-01T00:00:00+03:00'),
            dateutil.parser.parse('2024-10-01T00:00:00+03:00'),
            dateutil.parser.parse('2043-10-01T00:00:00+03:00'),
            '',
            '',
        ),
    ]
