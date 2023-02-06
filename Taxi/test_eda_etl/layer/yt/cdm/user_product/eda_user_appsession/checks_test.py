import datetime

import pytest
from pandas import Timestamp

from dmp_suite.maintenance.checks import CheckResult
from dmp_suite.spark.spark_tools import all_columns, cast_to_spark_datetime

# Those checks are rewritten with new check task
# from eda_etl.layer.yt.cdm.food.demand.eda_user_appsession.checks import (
#     EdaUserAppSessionRequiredAppPlatformCheck, EdaUserAppSessionUnexpectedAppPlatformCheck,
#     EdaUserAppSessionNotNullCheck, EdaUserAppSessionOverlapCheck, EdaUserAppSessionUniqueIdCheck,
#     EdaUserAppSessionDestinationChangeCheck, EdaUserAppSessionUserMoveChangeCheck,
#     EdaUserAppSessionUserMoveChangeWithNullCoordCheck, EdaUserAppSessionDestinationChangeWithNullCoordCheck,
#     EdaUserAppSessionUserCoordinateCheck, EdaUserAppSessionDestinationCoordinateCheck, EdaUserAppSessionEventLimitCheck
# )
from test_dmp_suite.testing_utils.spark_testing_utils import do_check, local_spark_session

session = dict

@pytest.mark.skip(reason="test requires rewrite or deletion (TAXIDWH-9153)")
@pytest.mark.parametrize(
        'sessions, expected_result_unique_id_check, expected_check_report',
        [
            pytest.param(
                [
                    session(
                        appsession_id='8068a28b7eba753983edb0221e50019b',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                    ),
                    session(
                        appsession_id='8068a28b7eba753983edb0221e50019b',
                        utc_session_start_dttm='2020-03-10 10:00:50',
                    ),
                    session(
                        appsession_id='8069a28b7eba753983edb0221e50021c',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                    ),
                ],
                # expected_result_unique_id_check
                [
                    {'count': 2, 'appsession_id': '8068a28b7eba753983edb0221e50019b'}
                ],
                # expected_check_report
                CheckResult(
                    'MockedEdaAppSessionUniqueIdCheck', 1, 1,
                    "В пользовательских сессиях еды есть дубликаты по session_id. "
                 "Пример: appsession_id = 8068a28b7eba753983edb0221e50019b не уникален в рамках дня N и (N-1)."
                )
            ),
            pytest.param(
                [
                    session(
                        appsession_id='8068a28b7eba753983edb0221e50019b',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                    ),
                    session(
                        appsession_id='8068a28b7eba753983edb0221e50019b',
                        utc_session_start_dttm='2020-03-14 13:08:50',
                    ),
                    session(
                        appsession_id='310b7519c45670d8523a4dda465849e7',
                        utc_session_start_dttm='2020-03-11 05:00:34',
                    ),
                ],
                # expected_result_unique_id_check
                [],
                # expected_check_report
                CheckResult('MockedEdaAppSessionUniqueIdCheck', 0, 0, '')
            ),
            pytest.param(
                [
                    session(
                        appsession_id='8068a28b7eba753983edb0221e50019b',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                    ),
                    session(
                        appsession_id='8075c27a8fh89ba753983edb0221e500n',
                        utc_session_start_dttm='2020-03-10 10:04:50',
                    ),
                    session(
                        appsession_id='560bc7y7945670d8523a4dda4658gg7',
                        utc_session_start_dttm='2020-03-11 13:07:50',
                    ),
                ],
                # expected_result_unique_id_check
                [],
                # expected_check_report
                CheckResult('MockedEdaAppSessionUniqueIdCheck', 0, 0, '')
            )
        ]
)
@pytest.mark.slow
def test_eda_appsession_unique_id_check(
        sessions, expected_result_unique_id_check,
        expected_check_report, local_spark_session
):

    class MockedEdaAppSessionUniqueIdCheck(EdaUserAppSessionUniqueIdCheck):
        def _read_sessions_df(self):
            df = local_spark_session.createDataFrame(list(sessions))
            return df.select(
                *all_columns(df, exclude=['utc_session_start_dttm']),
                cast_to_spark_datetime('utc_session_start_dttm'),
            )

    check = MockedEdaAppSessionUniqueIdCheck({
        'start_date': datetime.datetime(2020, 3, 10),
        'end_date': datetime.datetime(2020, 3, 11)
    })

    do_check(check, local_spark_session, expected_result_unique_id_check, expected_check_report)


@pytest.mark.skip(reason="test requires rewrite or deletion (TAXIDWH-9153)")
@pytest.mark.parametrize(
        'sessions, expected_result_overlap_check, expected_check_report',
        [
            pytest.param(
                [
                    session(
                        device_id='37493434433',
                        appsession_id='8068a28b7eba753983edb0221e50019b',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        utc_session_end_dttm='2020-03-11 21:04:50',
                    ),
                    session(
                        device_id='37493434433',
                        appsession_id='8069a28b7eba753983edb0221e50021c',
                        utc_session_start_dttm='2020-03-11 19:01:50',
                        utc_session_end_dttm='2020-03-11 22:04:50',
                    ),
                ],
                # expected_result_overlap_check result
                [
                    {
                        'appsession_id': '8068a28b7eba753983edb0221e50019b',
                        'utc_session_start_dttm': Timestamp('2020-03-11 18:04:50'),
                        'utc_session_end_dttm': Timestamp('2020-03-11 21:04:50'),
                        'next_utc_session_start_dttm': Timestamp('2020-03-11 19:01:50'),
                        'next_appsession_id': '8069a28b7eba753983edb0221e50021c'
                    }
                ],
                # expected_check_report
                CheckResult(
                    'MockedAppSessionOverlapCheck', 1, 1,
                    "В сессиях еды есть пересечения: сессии 8068a28b7eba753983edb0221e50019b и 8069a28b7eba753983edb0221e50021c пересекаются"
                    " в рамках дней N и (N-1)"
                )
            ),
            pytest.param(
                [
                    session(
                        device_id='37493434433',
                        appsession_id='8068a28b7eba753983edb0221e50019b',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        utc_session_end_dttm='2020-03-11 19:04:50',
                    ),
                    session(
                        device_id='37493434433',
                        appsession_id='8068a28b7eba753983edb0221ehjjj54',
                        utc_session_start_dttm='2020-03-10 10:04:50',
                        utc_session_end_dttm='2020-03-10 12:04:50',
                    )
                ],
                # expected_result_overlap_check result
                [],
                # expected_check_report
                CheckResult('MockedAppSessionOverlapCheck', 0, 0, '')
            ),
            pytest.param(
                [
                    session(
                        device_id='37493434433',
                        appsession_id='8068a28b7eba753983edb0221e50019b',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        utc_session_end_dttm='2020-03-11 19:04:50',
                    ),
                    session(
                        device_id='37493434433',
                        appsession_id='8068aghj6753983edb0221ehjjj54',
                        utc_session_start_dttm='2020-03-13 12:04:50',
                        utc_session_end_dttm='2020-03-13 12:04:50',
                    )
                ],
                # expected_result_overlap_check result
                [],
                # expected_check_report
                CheckResult('MockedAppSessionOverlapCheck', 0, 0, '')
            )
        ]
    )
@pytest.mark.slow
def test_eda_appsession_overlap_check(
        sessions, expected_result_overlap_check,
        expected_check_report, local_spark_session
):
    class MockedAppSessionOverlapCheck(EdaUserAppSessionOverlapCheck):
        def _read_sessions_df(self):
            df = local_spark_session.createDataFrame(list(sessions))
            return df.select(
                *all_columns(df, exclude=['utc_session_start_dttm', 'utc_session_end_dttm']),
                cast_to_spark_datetime('utc_session_start_dttm'),
                cast_to_spark_datetime('utc_session_end_dttm'),
            )

    check = MockedAppSessionOverlapCheck({
        'start_date': datetime.datetime(2020, 3, 10),
        'end_date': datetime.datetime(2020, 3, 11)
    })

    do_check(check, local_spark_session, expected_result_overlap_check, expected_check_report)


@pytest.mark.skip(reason="test requires rewrite or deletion (TAXIDWH-9153)")
@pytest.mark.parametrize(
        'sessions, expected_result_not_null_check, expected_check_report',
        [
            pytest.param(
                [
                    session(
                        appsession_id='8068a28b7eba753983edb0221e50019b123',
                        device_id=None,
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        utc_session_end_dttm='2020-03-11 21:04:50',
                    ),
                    session(
                        appsession_id='8069a28b7eba753983edb0221e50021c',
                        device_id='1234567',
                        utc_session_start_dttm='2020-03-11 19:01:50',
                        utc_session_end_dttm='2020-03-11 22:04:50',
                    ),
                ],
                # expected_result_not_null_check result
                [
                    {
                        'appsession_id': '8068a28b7eba753983edb0221e50019b123'
                    }
                ],
                # expected_check_report
                CheckResult(
                    'MockedAppSessionNotNullCheck', 1, 1,
                    "В пользовательских сессиях еды найдена запись, где "
                    " одно из полей device_id, utc_session_start_dttm, utc_session_end_dttm пустое. "
                    "Пример: appsession_id = 8068a28b7eba753983edb0221e50019b123."
                )
            ),
            pytest.param(
                [
                    session(
                        device_id='37493434433',
                        appsession_id='8068a28b7eba753983edb0221e50019b',
                        utc_session_start_dttm='2020-03-11 19:04:50',
                        utc_session_end_dttm='2020-03-11 19:04:50',
                    ),
                    session(
                        device_id='37493434433',
                        appsession_id='8068aghj6753983edb0221ehjjj54',
                        utc_session_start_dttm='2020-03-11 12:04:50',
                        utc_session_end_dttm='2020-03-11 12:04:50',
                    )
                ],
                # expected_result_not_null_check result
                [],
                # expected_check_report
                CheckResult('MockedAppSessionOverlapCheck', 0, 0, '')
            )
        ]
    )
@pytest.mark.slow
def test_eda_appsession_not_null_check(
        sessions, expected_result_not_null_check,
        expected_check_report, local_spark_session
):
    class MockedAppSessionNotNullCheck(EdaUserAppSessionNotNullCheck):
        def _read_sessions_df(self):
            df = local_spark_session.createDataFrame(list(sessions))
            return df.select(
                *all_columns(df, exclude=['utc_session_start_dttm', 'utc_session_end_dttm']),
                cast_to_spark_datetime('utc_session_start_dttm'),
                cast_to_spark_datetime('utc_session_end_dttm'),
            )

    check = MockedAppSessionNotNullCheck({
        'start_date': datetime.datetime(2020, 3, 10),
        'end_date': datetime.datetime(2020, 3, 11)
    })

    do_check(check, local_spark_session, expected_result_not_null_check, expected_check_report)


@pytest.mark.skip(reason="test requires rewrite or deletion (TAXIDWH-9153)")
@pytest.mark.parametrize(
        'sessions, expected_result_required_app_platform_check, expected_check_report',
        [
            pytest.param(
                [
                    session(
                        appsession_id='8068a28b7eba753983edb0221e50019b123',
                        app_platform_name='android',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        utc_session_end_dttm='2020-03-11 21:04:50',
                    ),
                    session(
                        appsession_id='8069a28b7eba753983edb0221e50021c',
                        app_platform_name='android',
                        utc_session_start_dttm='2020-03-11 19:01:50',
                        utc_session_end_dttm='2020-03-11 22:04:50',
                    ),
                ],
                # expected_result_required_app_platform_check result
                [
                    {
                        'value': 'ios'
                    }
                ],
                # expected_check_report
                CheckResult(
                    'MockedAppSessionRequiredAppPlatformCheck', 1, 1,
                    "В пользовательских сессиях еды отсутствует платформа app_platform = ios."
                )
            ),
            pytest.param(
                [
                    session(
                        device_id='37493434433',
                        appsession_id='8068a28b7eba753983edb0221e50019b',
                        utc_session_start_dttm='2020-03-11 19:04:50',
                        utc_session_end_dttm='2020-03-11 19:04:50',
                        app_platform_name='ios',
                    ),
                    session(
                        device_id='37493434433',
                        appsession_id='8068aghj6753983edb0221ehjjj54',
                        utc_session_start_dttm='2020-03-11 12:04:50',
                        utc_session_end_dttm='2020-03-11 12:04:50',
                        app_platform_name='android',
                    )
                ],
                # expected_result_required_app_platform_check result
                [],
                # expected_check_report
                CheckResult('MockedAppSessionRequiredAppPlatformCheck', 0, 0, '')
            )
        ]
    )
@pytest.mark.slow
def test_eda_appsession_required_app_platform_check(
        sessions, expected_result_required_app_platform_check,
        expected_check_report, local_spark_session
):
    class MockedAppSessionRequiredAppPlatformCheck(EdaUserAppSessionRequiredAppPlatformCheck):
        def _read_sessions_df(self):
            df = local_spark_session.createDataFrame(list(sessions))
            return df.select(
                *all_columns(df, exclude=['utc_session_start_dttm', 'utc_session_end_dttm']),
                cast_to_spark_datetime('utc_session_start_dttm'),
                cast_to_spark_datetime('utc_session_end_dttm'),
            )

    check = MockedAppSessionRequiredAppPlatformCheck({
        'start_date': datetime.datetime(2020, 3, 10),
        'end_date': datetime.datetime(2020, 3, 11)
    })

    do_check(check, local_spark_session, expected_result_required_app_platform_check, expected_check_report)


@pytest.mark.skip(reason="test requires rewrite or deletion (TAXIDWH-9153)")
@pytest.mark.parametrize(
        'sessions, expected_result_unexpected_app_platform_check, expected_check_report',
        [
            pytest.param(
                [
                    session(
                        appsession_id='8068a28b7eba753983edb0221e50019b123',
                        app_platform_name='ios1',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        utc_session_end_dttm='2020-03-11 21:04:50',
                    ),
                    session(
                        appsession_id='8069a28b7eba753983edb0221e50021c',
                        app_platform_name='android',
                        utc_session_start_dttm='2020-03-11 19:01:50',
                        utc_session_end_dttm='2020-03-11 22:04:50',
                    ),
                ],
                # expected_result_unexpected_app_platform_check result
                [
                    {
                        'app_platform_name': 'ios1'
                    }
                ],
                # expected_check_report
                CheckResult(
                    'MockedAppSessionUnexpectedAppPlatformCheck', 1, 1,
                    "В пользовательских сессиях еды присутствует платформа app_platform = ios1, которая "
                    "не входит в ожидаемый список ['ios', 'android']."
                )
            ),
            pytest.param(
                [
                    session(
                        device_id='37493434433',
                        appsession_id='8068a28b7eba753983edb0221e50019b',
                        utc_session_start_dttm='2020-03-11 19:04:50',
                        utc_session_end_dttm='2020-03-11 19:04:50',
                        app_platform_name='ios',
                    ),
                    session(
                        device_id='37493434433',
                        appsession_id='8068aghj6753983edb0221ehjjj54',
                        utc_session_start_dttm='2020-03-11 12:04:50',
                        utc_session_end_dttm='2020-03-11 12:04:50',
                        app_platform_name='android',
                    )
                ],
                # expected_result_unexpected_app_platform_check result
                [],
                # expected_check_report
                CheckResult('MockedAppSessionUnexpectedAppPlatformCheck', 0, 0, '')
            )
        ]
    )
@pytest.mark.slow
def test_eda_appsession_unexpected_app_platform_check(
        sessions, expected_result_unexpected_app_platform_check,
        expected_check_report, local_spark_session
):
    class MockedAppSessionUnexpectedAppPlatformCheck(EdaUserAppSessionUnexpectedAppPlatformCheck):
        def _read_sessions_df(self):
            df = local_spark_session.createDataFrame(list(sessions))
            return df.select(
                *all_columns(df, exclude=['utc_session_start_dttm', 'utc_session_end_dttm']),
                cast_to_spark_datetime('utc_session_start_dttm'),
                cast_to_spark_datetime('utc_session_end_dttm'),
            )

    check = MockedAppSessionUnexpectedAppPlatformCheck({
        'start_date': datetime.datetime(2020, 3, 10),
        'end_date': datetime.datetime(2020, 3, 11)
    })

    do_check(check, local_spark_session, expected_result_unexpected_app_platform_check, expected_check_report)


@pytest.mark.skip(reason="test requires rewrite or deletion (TAXIDWH-9153)")
@pytest.mark.parametrize(
        'sessions, expected_result_user_move_change_check, expected_check_report',
        [
            pytest.param(
                [
                    session(
                        appsession_id='8068a28b7eba753983edb0221e50019b123',
                        device_id='1234566',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        utc_session_end_dttm='2020-03-11 21:04:50',
                        user_lat=11.22,
                        user_lon=33.44,
                        user_move_diff_m=1234
                    ),
                    session(
                        appsession_id='8069a28b7eba753983edb0221e50021c',
                        device_id='1234567',
                        utc_session_start_dttm='2020-03-11 19:01:50',
                        utc_session_end_dttm='2020-03-11 22:04:50',
                        user_lat=11.22,
                        user_lon=33.44,
                        user_move_diff_m=None
                    ),
                ],
                # expected_result_user_move_change_check result
                [
                    {
                        'appsession_id': '8069a28b7eba753983edb0221e50021c'
                    }
                ],
                # expected_check_report
                CheckResult(
                    'MockedAppSessionUserMoveChangeCheck', 1, 1,
                    "В пользовательских сессиях еды найдена запись, где "
                    " поле user_move_diff_m не рассчитано, хотя координаты(user_lat/user_lon) заполнены. "
                    "Пример: appsession_id = 8069a28b7eba753983edb0221e50021c."
                )
            ),
            pytest.param(
                [
                    session(
                        appsession_id='8068a28b7eba753983edb0221e50019b123',
                        device_id='1234566',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        utc_session_end_dttm='2020-03-11 21:04:50',
                        user_lat=11.22,
                        user_lon=33.44,
                        user_move_diff_m=1234
                    ),
                    session(
                        appsession_id='8069a28b7eba753983edb0221e50021c',
                        device_id='1234567',
                        utc_session_start_dttm='2020-03-11 19:01:50',
                        utc_session_end_dttm='2020-03-11 22:04:50',
                        user_lat=None,
                        user_lon=None,
                        user_move_diff_m=None
                    ),
                ],
                # expected_result_user_move_change_check result
                [],
                # expected_check_report
                CheckResult('MockedAppSessionUserMoveChangeCheck', 0, 0, '')
            )
        ]
    )
@pytest.mark.slow
def test_eda_appsession_user_move_change_check(
        sessions, expected_result_user_move_change_check,
        expected_check_report, local_spark_session
):
    class MockedAppSessionUserMoveChangeCheck(EdaUserAppSessionUserMoveChangeCheck):
        def _read_sessions_df(self):
            df = local_spark_session.createDataFrame(list(sessions))
            return df.select(
                *all_columns(df, exclude=['utc_session_start_dttm', 'utc_session_end_dttm']),
                cast_to_spark_datetime('utc_session_start_dttm'),
                cast_to_spark_datetime('utc_session_end_dttm'),
            )

    check = MockedAppSessionUserMoveChangeCheck({
        'start_date': datetime.datetime(2020, 3, 10),
        'end_date': datetime.datetime(2020, 3, 11)
    })

    do_check(check, local_spark_session, expected_result_user_move_change_check, expected_check_report)


@pytest.mark.skip(reason="test requires rewrite or deletion (TAXIDWH-9153)")
@pytest.mark.parametrize(
        'sessions, expected_result_destination_change_with_null_coord_check, expected_check_report',
        [
            pytest.param(
                [
                    session(
                        appsession_id='8068a28b7eba753983edb0221e50019b123',
                        device_id='1234566',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        utc_session_end_dttm='2020-03-11 21:04:50',
                        destination_lat=11.22,
                        destination_lon=33.44,
                        destination_diff_m=1234
                    ),
                    session(
                        appsession_id='8069a28b7eba753983edb0221e50021c',
                        device_id='1234567',
                        utc_session_start_dttm='2020-03-11 19:01:50',
                        utc_session_end_dttm='2020-03-11 22:04:50',
                        destination_lat=None,
                        destination_lon=33.44,
                        destination_diff_m=1234
                    ),
                ],
                # expected_result_destination_change_with_null_coord_check result
                [
                    {
                        'appsession_id': '8069a28b7eba753983edb0221e50021c'
                    }
                ],
                # expected_check_report
                CheckResult(
                    'MockedAppSessionDestinationChangeCheck', 1, 1,
                    "В пользовательских сессиях еды найдена запись, где "
                    " поле destination_diff_m рассчитано, хотя одна из координат(destination_lat/lon) не заполнена. "
                    "Пример: appsession_id = 8069a28b7eba753983edb0221e50021c."
                )
            ),
            pytest.param(
                [
                    session(
                        appsession_id='8068a28b7eba753983edb0221e50019b123',
                        device_id='1234566',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        utc_session_end_dttm='2020-03-11 21:04:50',
                        destination_lat=11.22,
                        destination_lon=33.44,
                        destination_diff_m=1234
                    ),
                    session(
                        appsession_id='8069a28b7eba753983edb0221e50021c',
                        device_id='1234567',
                        utc_session_start_dttm='2020-03-11 19:01:50',
                        utc_session_end_dttm='2020-03-11 22:04:50',
                        destination_lat=None,
                        destination_lon=None,
                        destination_diff_m=None
                    ),
                ],
                # expected_result_destination_change_with_null_coord_check result
                [],
                # expected_check_report
                CheckResult('MockedAppSessionDestinationChangeCheck', 0, 0, '')
            )
        ]
    )
@pytest.mark.slow
def test_eda_appsession_destination_change_check(
        sessions, expected_result_destination_change_with_null_coord_check,
        expected_check_report, local_spark_session
):
    class MockedAppSessionDestinationChangeWithNullCoordCheck(EdaUserAppSessionDestinationChangeWithNullCoordCheck):
        def _read_sessions_df(self):
            df = local_spark_session.createDataFrame(list(sessions))
            return df.select(
                *all_columns(df, exclude=['utc_session_start_dttm', 'utc_session_end_dttm']),
                cast_to_spark_datetime('utc_session_start_dttm'),
                cast_to_spark_datetime('utc_session_end_dttm'),
            )

    check = MockedAppSessionDestinationChangeWithNullCoordCheck({
        'start_date': datetime.datetime(2020, 3, 10),
        'end_date': datetime.datetime(2020, 3, 11)
    })

    do_check(check, local_spark_session, expected_result_destination_change_with_null_coord_check, expected_check_report)


@pytest.mark.skip(reason="test requires rewrite or deletion (TAXIDWH-9153)")
@pytest.mark.parametrize(
        'sessions, expected_result_user_move_change_with_null_coord_check, expected_check_report',
        [
            pytest.param(
                [
                    session(
                        appsession_id='8068a28b7eba753983edb0221e50019b123',
                        device_id='1234566',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        utc_session_end_dttm='2020-03-11 21:04:50',
                        user_lat=11.22,
                        user_lon=33.44,
                        user_move_diff_m=1234
                    ),
                    session(
                        appsession_id='8069a28b7eba753983edb0221e50021c',
                        device_id='1234567',
                        utc_session_start_dttm='2020-03-11 19:01:50',
                        utc_session_end_dttm='2020-03-11 22:04:50',
                        user_lat=None,
                        user_lon=33.44,
                        user_move_diff_m=1234
                    ),
                ],
                # expected_result_user_move_change_with_null_coord_check result
                [
                    {
                        'appsession_id': '8069a28b7eba753983edb0221e50021c'
                    }
                ],
                # expected_check_report
                CheckResult(
                    'MockedAppSessionUserMoveChangeWithNullCoordCheck', 1, 1,
                    "В пользовательских сессиях еды найдена запись, где "
                    " поле user_move_diff_m рассчитано, хотя одна из координат(user_lat/user_lon) не заполнена. "
                    "Пример: appsession_id = 8069a28b7eba753983edb0221e50021c."
                )
            ),
            pytest.param(
                [
                    session(
                        appsession_id='8068a28b7eba753983edb0221e50019b123',
                        device_id='1234566',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        utc_session_end_dttm='2020-03-11 21:04:50',
                        user_lat=11.22,
                        user_lon=33.44,
                        user_move_diff_m=1234
                    ),
                    session(
                        appsession_id='8069a28b7eba753983edb0221e50021c',
                        device_id='1234567',
                        utc_session_start_dttm='2020-03-11 19:01:50',
                        utc_session_end_dttm='2020-03-11 22:04:50',
                        user_lat=None,
                        user_lon=None,
                        user_move_diff_m=None
                    ),
                ],
                # expected_result_user_move_change_with_null_coord_check result
                [],
                # expected_check_report
                CheckResult('MockedAppSessionUserMoveChangeWithNullCoordCheck', 0, 0, '')
            )
        ]
    )
@pytest.mark.slow
def test_eda_appsession_user_move_change_with_null_coord_check(
        sessions, expected_result_user_move_change_with_null_coord_check,
        expected_check_report, local_spark_session
):
    class MockedAppSessionUserMoveChangeWithNullCoordCheck(EdaUserAppSessionUserMoveChangeWithNullCoordCheck):
        def _read_sessions_df(self):
            df = local_spark_session.createDataFrame(list(sessions))
            return df.select(
                *all_columns(df, exclude=['utc_session_start_dttm', 'utc_session_end_dttm']),
                cast_to_spark_datetime('utc_session_start_dttm'),
                cast_to_spark_datetime('utc_session_end_dttm'),
            )

    check = MockedAppSessionUserMoveChangeWithNullCoordCheck({
        'start_date': datetime.datetime(2020, 3, 10),
        'end_date': datetime.datetime(2020, 3, 11)
    })

    do_check(check, local_spark_session, expected_result_user_move_change_with_null_coord_check, expected_check_report)


@pytest.mark.skip(reason="test requires rewrite or deletion (TAXIDWH-9153)")
@pytest.mark.parametrize(
        'sessions, expected_result_user_coordinate_check, expected_check_report',
        [
            pytest.param(
                [
                    session(
                        appsession_id='8068a28b7eba753983edb0221e50019b123',
                        device_id='1234566',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        utc_session_end_dttm='2020-03-11 21:04:50',
                        user_lat=11.22,
                        user_lon=33.44
                    ),
                    session(
                        appsession_id='8069a28b7eba753983edb0221e50021c',
                        device_id='1234567',
                        utc_session_start_dttm='2020-03-11 19:01:50',
                        utc_session_end_dttm='2020-03-11 22:04:50',
                        user_lat=11.22,
                        user_lon=33.44
                    ),
                    session(
                        appsession_id='8069a28b7eba753983edb0221e50021c',
                        device_id='1234567',
                        utc_session_start_dttm='2020-03-11 19:01:50',
                        utc_session_end_dttm='2020-03-11 22:04:50',
                        user_lat=None,
                        user_lon=33.44
                    ),
                    session(
                        appsession_id='8069a28b7eba753983edb0221e50021c',
                        device_id='1234567',
                        utc_session_start_dttm='2020-03-11 19:01:50',
                        utc_session_end_dttm='2020-03-11 22:04:50',
                        user_lat=11.22,
                        user_lon=None
                    ),
                    session(
                        appsession_id='8069a28b7eba753983edb0221e50021c',
                        device_id='1234567',
                        utc_session_start_dttm='2020-03-11 19:01:50',
                        utc_session_end_dttm='2020-03-11 22:04:50',
                        user_lat=None,
                        user_lon=None
                    ),
                ],
                # expected_result_user_coordinate_check result
                [
                    {
                        'result': 40.0
                    }
                ],
                # expected_check_report
                CheckResult(
                    'MockedAppSessionUserCoordinateCheck', 1, 1,
                    "Процент заполненных фактических координат физического нахождения пользователя ниже границы в 85 % "
                    "и составляет 40.00 %"
                )
            ),
            pytest.param(
                [
                    session(
                        appsession_id='8068a28b7eba753983edb0221e50019b123',
                        device_id='1234566',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        utc_session_end_dttm='2020-03-11 21:04:50',
                        user_lat=11.22,
                        user_lon=33.44,
                        user_move_diff_m=1234
                    ),
                    session(
                        appsession_id='8069a28b7eba753983edb0221e50021c',
                        device_id='1234567',
                        utc_session_start_dttm='2020-03-11 19:01:50',
                        utc_session_end_dttm='2020-03-11 22:04:50',
                        user_lat=11.22,
                        user_lon=11.33,
                        user_move_diff_m=None
                    ),
                ],
                # expected_result_user_coordinate_check result
                [],
                # expected_check_report
                CheckResult('MockedAppSessionUserCoordinateCheck', 0, 0, '')
            )
        ]
    )
@pytest.mark.slow
def test_eda_appsession_user_coordinate_check(
        sessions, expected_result_user_coordinate_check,
        expected_check_report, local_spark_session
):
    class MockedAppSessionUserCoordinateCheck(EdaUserAppSessionUserCoordinateCheck):
        def _read_sessions_df(self):
            df = local_spark_session.createDataFrame(list(sessions))
            return df.select(
                *all_columns(df, exclude=['utc_session_start_dttm', 'utc_session_end_dttm']),
                cast_to_spark_datetime('utc_session_start_dttm'),
                cast_to_spark_datetime('utc_session_end_dttm'),
            )

    check = MockedAppSessionUserCoordinateCheck({
        'start_date': datetime.datetime(2020, 3, 10),
        'end_date': datetime.datetime(2020, 3, 11)
    })

    do_check(check, local_spark_session, expected_result_user_coordinate_check, expected_check_report)


@pytest.mark.skip(reason="test requires rewrite or deletion (TAXIDWH-9153)")
@pytest.mark.parametrize(
        'sessions, expected_result_destination_coordinate_check, expected_check_report',
        [
            pytest.param(
                [
                    session(
                        appsession_id='8068a28b7eba753983edb0221e50019b123',
                        device_id='1234566',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        utc_session_end_dttm='2020-03-11 21:04:50',
                        destination_lat=11.22,
                        destination_lon=33.44
                    ),
                    session(
                        appsession_id='8069a28b7eba753983edb0221e50021c',
                        device_id='1234567',
                        utc_session_start_dttm='2020-03-11 19:01:50',
                        utc_session_end_dttm='2020-03-11 22:04:50',
                        destination_lat=11.22,
                        destination_lon=33.44
                    ),
                    session(
                        appsession_id='8069a28b7eba753983edb0221e50021c',
                        device_id='1234567',
                        utc_session_start_dttm='2020-03-11 19:01:50',
                        utc_session_end_dttm='2020-03-11 22:04:50',
                        destination_lat=None,
                        destination_lon=33.44
                    ),
                    session(
                        appsession_id='8069a28b7eba753983edb0221e50021c',
                        device_id='1234567',
                        utc_session_start_dttm='2020-03-11 19:01:50',
                        utc_session_end_dttm='2020-03-11 22:04:50',
                        destination_lat=11.22,
                        destination_lon=None
                    ),
                    session(
                        appsession_id='8069a28b7eba753983edb0221e50021c',
                        device_id='1234567',
                        utc_session_start_dttm='2020-03-11 19:01:50',
                        utc_session_end_dttm='2020-03-11 22:04:50',
                        destination_lat=None,
                        destination_lon=None
                    ),
                ],
                # expected_result_destination_coordinate_check result
                [
                    {
                        'result': 40.0
                    }
                ],
                # expected_check_report
                CheckResult(
                    'MockedAppSessionDestinationCoordinateCheck', 1, 1,
                    "Процент заполненных координат адреса доставки ниже границы в 85 % "
                    "и составляет 40.00 %"
                )
            ),
            pytest.param(
                [
                    session(
                        appsession_id='8068a28b7eba753983edb0221e50019b123',
                        device_id='1234566',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        utc_session_end_dttm='2020-03-11 21:04:50',
                        destination_lat=11.22,
                        destination_lon=33.44,
                        user_move_diff_m=1234
                    ),
                    session(
                        appsession_id='8069a28b7eba753983edb0221e50021c',
                        device_id='1234567',
                        utc_session_start_dttm='2020-03-11 19:01:50',
                        utc_session_end_dttm='2020-03-11 22:04:50',
                        destination_lat=11.22,
                        destination_lon=11.33,
                        user_move_diff_m=None
                    ),
                ],
                # expected_result_destination_coordinate_check result
                [],
                # expected_check_report
                CheckResult('MockedAppSessionDestinationCoordinateCheck', 0, 0, '')
            )
        ]
    )
@pytest.mark.slow
def test_eda_appsession_destination_coordinate_check(
        sessions, expected_result_destination_coordinate_check,
        expected_check_report, local_spark_session
):
    class MockedAppSessionDestinationCoordinateCheck(EdaUserAppSessionDestinationCoordinateCheck):
        def _read_sessions_df(self):
            df = local_spark_session.createDataFrame(list(sessions))
            return df.select(
                *all_columns(df, exclude=['utc_session_start_dttm', 'utc_session_end_dttm']),
                cast_to_spark_datetime('utc_session_start_dttm'),
                cast_to_spark_datetime('utc_session_end_dttm'),
            )

    check = MockedAppSessionDestinationCoordinateCheck({
        'start_date': datetime.datetime(2020, 3, 10),
        'end_date': datetime.datetime(2020, 3, 11)
    })

    do_check(check, local_spark_session, expected_result_destination_coordinate_check, expected_check_report)


@pytest.mark.skip(reason="test requires rewrite or deletion (TAXIDWH-9153)")
@pytest.mark.parametrize(
        'sessions, expected_result_event_cnt_limit_check, expected_check_report',
        [
            pytest.param(
                [
                    session(
                        appsession_id='8068a28b7eba753983edb0221e50019b',
                        break_reason='event_cnt_limit',
                        order_id_paid_list=['1'],
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        utc_session_end_dttm='2020-03-11 22:04:50',
                    ),
                    session(
                        appsession_id='8069a28b7eba753983edb0221e50021c',
                        order_id_paid_list=['1'],
                        break_reason='not_event_cnt_limit',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        utc_session_end_dttm='2020-03-11 22:04:50',
                    ),
                ],
                # expected_result_event_cnt_limit_check
                [
                    {'appsession_id': '8068a28b7eba753983edb0221e50019b'}
                ],
                # expected_check_report
                CheckResult(
                    'MockedEdaAppSessionUniqueIdCheck', 1, 1,
                    "В пользовательских сессиях еды найдена сессия с причиной разрыва = event_cnt_limit. " \
                 "Пример: appsession_id = 8068a28b7eba753983edb0221e50019b."
                )
            ),
            pytest.param(
                [
                    session(
                        appsession_id='8068a28b7eba753983edb0221e50019b',
                        break_reason='not_event_cnt_limit1',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        utc_session_end_dttm='2020-03-11 22:04:50',
                        order_id_paid_list=['1']
                    ),
                    session(
                        appsession_id='8075c27a8fh89ba753983edb0221e500n',
                        break_reason='not_event_cnt_limit2',
                        utc_session_start_dttm='2020-03-10 10:04:50',
                        utc_session_end_dttm='2020-03-11 22:04:50',
                        order_id_paid_list=None
                    ),
                ],
                # expected_result_event_cnt_limit_check
                [],
                # expected_check_report
                CheckResult('MockedEdaAppSessionUniqueIdCheck', 0, 0, '')
            )
        ]
)
@pytest.mark.slow
def test_eda_appsession_event_cnt_limit_check(
        sessions, expected_result_event_cnt_limit_check,
        expected_check_report, local_spark_session
):
    class MockedAppSessionEventLimitCheck(EdaUserAppSessionEventLimitCheck):
        def _read_sessions_df(self):
            df = local_spark_session.createDataFrame(list(sessions))
            return df.select(
                *all_columns(df, exclude=['utc_session_start_dttm', 'utc_session_end_dttm']),
                cast_to_spark_datetime('utc_session_start_dttm'),
                cast_to_spark_datetime('utc_session_end_dttm'),
            )

    check = MockedAppSessionEventLimitCheck({
        'start_date': datetime.datetime(2020, 3, 10),
        'end_date': datetime.datetime(2020, 3, 11)
    })

    do_check(check, local_spark_session, expected_result_event_cnt_limit_check, expected_check_report)
