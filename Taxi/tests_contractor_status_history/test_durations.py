import pytest

import tests_contractor_status_history.utils as utils


# legend:
#   [ - request interval start, 2020-11-26 12:00:00.0+00
#   ] - request interval end, 2020-11-26 14:00:00.0+00
#   | - some event within day
#   || - days boundary
#   no events, online, online + order, etc - event description
#
# Test contents
#
# 100. no events [ no events ]
# 101. no events [ no events | online ]
# 102. no events [ no events | online | busy ]
# 103. no events [ no events | online | online + order | busy ]
# 104. no events [ no events | online | online + order | busy + order | busy ]
# 105. no events [ no events | online | offline ]
# 106. no events [ no events | offline ]
# 107. no events [ online ]
# 108. online [ no events ]
# 109. online [ no events | offline ]
# 110. online [ no events ] offline
# 111. offline [ no events | online ]
#
# 200. online || no events [ no events ]
# 201. online || no events [ no events | offline ]
# 202. online || no events [ offline ]
# 203. online || no events | offline [ no events ]
# 204. offline || no events [ no events ]


NOW = utils.parse_date_str('2020-11-26 23:59:59.0+00')

# corresponds to 2020-11-26 ('today')
FILL_EVENTS_000 = (
    'BEGIN; SET SEARCH_PATH TO history;'
    'INSERT INTO events_000 VALUES '
    # 100. no events [ no events ]
    # 101. no events [ no events | online ]
    '(\'park\', \'onedayprofile1\', ARRAY['
    '(\'2020-11-26 13:00:00.0+00\', \'online\', \'{}\')::event_tuple'
    # 102. no events [ no events | online | busy ]
    ']), (\'park\', \'onedayprofile2\',  ARRAY['
    '(\'2020-11-26 12:30:00.0+00\', \'online\', \'{}\')::event_tuple,'
    '(\'2020-11-26 13:30:00.0+00\', \'busy\', \'{}\')::event_tuple'
    # 103. no events [ no events | online | online + order | busy ]
    ']), (\'park\', \'onedayprofile3\',  ARRAY['
    '(\'2020-11-26 12:30:00.0+00\', \'online\', \'{}\')::event_tuple,'
    '(\'2020-11-26 13:00:00.0+00\', \'online\', \'{transporting}\')'
    '::event_tuple,'
    '(\'2020-11-26 13:30:00.0+00\', \'busy\', \'{}\')::event_tuple'
    # 104. no events
    #      [ no events | online | online + order | busy + order | busy ]
    ']), (\'park\', \'onedayprofile4\',  ARRAY['
    '(\'2020-11-26 12:20:00.0+00\', \'online\', \'{}\')::event_tuple,'
    '(\'2020-11-26 12:40:00.0+00\', \'online\', \'{transporting}\')'
    '::event_tuple,'
    '(\'2020-11-26 13:00:00.0+00\', \'busy\', \'{transporting}\')'
    '::event_tuple,'
    '(\'2020-11-26 13:30:00.0+00\', \'busy\', \'{}\')::event_tuple'
    # 105. no events [ no events | online | offline ]
    ']), (\'park\', \'onedayprofile5\',  ARRAY['
    '(\'2020-11-26 12:30:00.0+00\', \'online\', \'{}\')::event_tuple,'
    '(\'2020-11-26 13:30:00.0+00\', \'offline\', \'{}\')::event_tuple'
    # 106. no events [ no events | offline ]
    ']), (\'park\', \'onedayprofile6\',  ARRAY['
    '(\'2020-11-26 13:00:00.0+00\', \'offline\', \'{}\')::event_tuple'
    # 107. no events [ online ]
    ']), (\'park\', \'onedayprofile7\',  ARRAY['
    '(\'2020-11-26 12:00:00.0+00\', \'online\', \'{}\')::event_tuple'
    # 108. online [ no events ]
    ']), (\'park\', \'onedayprofile8\',  ARRAY['
    '(\'2020-11-26 11:00:00.0+00\', \'online\', \'{}\')::event_tuple'
    # 109. online [ no events | offline ]
    ']), (\'park\', \'onedayprofile9\',  ARRAY['
    '(\'2020-11-26 11:59:00.0+00\', \'online\', \'{}\')::event_tuple,'
    '(\'2020-11-26 13:00:00.0+00\', \'offline\', \'{}\')::event_tuple'
    # 110. online [ no events ] offline
    ']), (\'park\', \'onedayprofile10\',  ARRAY['
    '(\'2020-11-26 11:00:00.0+00\', \'online\', \'{}\')::event_tuple,'
    '(\'2020-11-26 14:00:00.0+00\', \'offline\', \'{}\')::event_tuple'
    # 111. offline [ no events | online ]
    ']), (\'park\', \'onedayprofile11\',  ARRAY['
    '(\'2020-11-26 11:00:00.0+00\', \'offline\', \'{}\')::event_tuple,'
    '(\'2020-11-26 13:00:00.0+00\', \'online\', \'{}\')::event_tuple'
    #
    # 200. online || no events [ no events ]
    # 201. online || no events [ no events | offline ]
    ']), (\'park\', \'twodaysprofile1\',  ARRAY['
    '(\'2020-11-26 13:00:00.0+00\', \'offline\', \'{}\')::event_tuple'
    # 202. online || no events [ offline ]
    ']), (\'park\', \'twodaysprofile2\',  ARRAY['
    '(\'2020-11-26 12:00:00.0+00\', \'offline\', \'{}\')::event_tuple'
    # 203. online || no events | offline [ no events ]
    ']), (\'park\', \'twodaysprofile3\',  ARRAY['
    '(\'2020-11-26 11:00:00.0+00\', \'offline\', \'{}\')::event_tuple'
    ']); '
    # 204. offline || no events [ no events ]
    'COMMIT;'
)


# corresponds to 2020-11-25 ('yesterday')
FILL_EVENTS_015 = (
    'BEGIN; SET SEARCH_PATH TO history;'
    'INSERT INTO events_015 VALUES '
    # 200. online || no events [ no events ]
    '(\'park\', \'twodaysprofile0\',  ARRAY['
    '(\'2020-11-25 12:00:00.0+00\', \'online\', \'{}\')::event_tuple'
    # 201. online || no events [ no events | offline ]
    ']), (\'park\', \'twodaysprofile1\',  ARRAY['
    '(\'2020-11-25 12:00:00.0+00\', \'online\', \'{}\')::event_tuple'
    # 202. online || no events [ offline ]
    ']), (\'park\', \'twodaysprofile2\',  ARRAY['
    '(\'2020-11-25 12:00:00.0+00\', \'online\', \'{}\')::event_tuple'
    # 203. online || no events | offline [ no events ]
    ']), (\'park\', \'twodaysprofile3\',  ARRAY['
    '(\'2020-11-25 12:00:00.0+00\', \'online\', \'{}\')::event_tuple'
    # 204. offline || no events [ no events ]
    ']), (\'park\', \'twodaysprofile4\',  ARRAY['
    '(\'2020-11-25 12:00:00.0+00\', \'offline\', \'{}\')::event_tuple'
    ']); '
    'COMMIT;'
)


@pytest.mark.pgsql(
    'contractor_status_history', queries=[FILL_EVENTS_000, FILL_EVENTS_015],
)
@pytest.mark.parametrize(
    'profile, expected',
    [
        pytest.param(
            'onedayprofile0',
            {
                'online': {'total': 0, 'on_order': 0},
                'busy': {'total': 0, 'on_order': 0},
            },
            id='100. no events [ no events ]',
        ),
        pytest.param(
            'onedayprofile1',
            {
                'online': {'total': 3600, 'on_order': 0},
                'busy': {'total': 0, 'on_order': 0},
            },
            id='101. no events [ no events | online ]',
        ),
        pytest.param(
            'onedayprofile2',
            {
                'online': {'total': 3600, 'on_order': 0},
                'busy': {'total': 1800, 'on_order': 0},
            },
            id='102. no events [ no events | online | busy ]',
        ),
        pytest.param(
            'onedayprofile3',
            {
                'online': {'total': 3600, 'on_order': 1800},
                'busy': {'total': 1800, 'on_order': 0},
            },
            id='103. no events [ no events | online | online + order | busy ]',
        ),
        pytest.param(
            'onedayprofile4',
            {
                'online': {'total': 2400, 'on_order': 1200},
                'busy': {'total': 3600, 'on_order': 1800},
            },
            id='104. no events '
            '[ no events | online | online + order | busy + order | busy ]',
        ),
        pytest.param(
            'onedayprofile5',
            {
                'online': {'total': 3600, 'on_order': 0},
                'busy': {'total': 0, 'on_order': 0},
            },
            id='105. no events [ no events | online | offline ]',
        ),
        pytest.param(
            'onedayprofile6',
            {
                'online': {'total': 0, 'on_order': 0},
                'busy': {'total': 0, 'on_order': 0},
            },
            id='106. no events [ no events | offline ]',
        ),
        pytest.param(
            'onedayprofile7',
            {
                'online': {'total': 7200, 'on_order': 0},
                'busy': {'total': 0, 'on_order': 0},
            },
            id='107. no events [ online ]',
        ),
        pytest.param(
            'onedayprofile8',
            {
                'online': {'total': 7200, 'on_order': 0},
                'busy': {'total': 0, 'on_order': 0},
            },
            id='108. online [ no events ]',
        ),
        pytest.param(
            'onedayprofile9',
            {
                'online': {'total': 3600, 'on_order': 0},
                'busy': {'total': 0, 'on_order': 0},
            },
            id='109. online [ no events | offline ]',
        ),
        pytest.param(
            'onedayprofile10',
            {
                'online': {'total': 7200, 'on_order': 0},
                'busy': {'total': 0, 'on_order': 0},
            },
            id='110. online [ no events ] offline',
        ),
        pytest.param(
            'onedayprofile11',
            {
                'online': {'total': 3600, 'on_order': 0},
                'busy': {'total': 0, 'on_order': 0},
            },
            id='111. offline [ no events | online ]',
        ),
        #
        pytest.param(
            'twodaysprofile0',
            {
                'online': {'total': 7200, 'on_order': 0},
                'busy': {'total': 0, 'on_order': 0},
            },
            id='200. online || no events [ no events ]',
        ),
        pytest.param(
            'twodaysprofile1',
            {
                'online': {'total': 3600, 'on_order': 0},
                'busy': {'total': 0, 'on_order': 0},
            },
            id='201. online || no events [ no events | offline ]',
        ),
        pytest.param(
            'twodaysprofile2',
            {
                'online': {'total': 0, 'on_order': 0},
                'busy': {'total': 0, 'on_order': 0},
            },
            id='202. online || no events [ offline ]',
        ),
        pytest.param(
            'twodaysprofile3',
            {
                'online': {'total': 0, 'on_order': 0},
                'busy': {'total': 0, 'on_order': 0},
            },
            id='203. online || no events | offline [ no events ]',
        ),
        pytest.param(
            'twodaysprofile4',
            {
                'online': {'total': 0, 'on_order': 0},
                'busy': {'total': 0, 'on_order': 0},
            },
            id='204. offline || no events [ no events ]',
        ),
    ],
)
@pytest.mark.config(
    CONTRACTOR_STATUS_HISTORY_EVENTS_STORE_DAYS=2,
    CONTRACTOR_STATUS_HISTORY_CONSIDER_OFFLINE_AFTER_HOURS=36,
)
@pytest.mark.suspend_periodic_tasks('tables-arch-checker')
async def disable_test_durations(
        taxi_contractor_status_history,
        mocked_time,
        testpoint,
        profile,
        expected,
):
    await utils.reset_arch_status(
        taxi_contractor_status_history, mocked_time, testpoint, NOW,
    )

    mocked_time.set(NOW)
    req = {
        'interval': {
            'from': utils.date_str_to_sec('2020-11-26 12:00:00.0+00'),
            'to': utils.date_str_to_sec('2020-11-26 14:00:00.0+00'),
        },
        'contractors': [{'park_id': 'park', 'profile_id': profile}],
    }
    response = await taxi_contractor_status_history.post('durations', json=req)
    assert response.status_code == 200

    expected_contractor = expected
    expected_contractor['park_id'] = 'park'
    expected_contractor['profile_id'] = profile
    expected_resp = {'contractors': [expected_contractor]}
    assert expected_resp == response.json()
