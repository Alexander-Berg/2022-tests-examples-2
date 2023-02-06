import datetime
import pytest

from dmp_suite.maintenance.checks import CheckResult
from test_dmp_suite.testing_utils.spark_testing_utils import do_check, local_spark_session

# from demand_etl.layer.yt.cdm.demand.demand_session.checks import (
#     DemandSessionUserPhoneCheck, DemandSessionUniqueIdCheck,
#     DemandSessionOverlapCheck
# )

session = dict
order = dict


@pytest.mark.skip(reason="test requires rewrite or deletion (TAXIDWH-9153)")
@pytest.mark.parametrize(
        'sessions, orders, expected_result_phone_check, expected_check_report',
        [
            pytest.param(
                [
                    session(
                        phone_pd_id='37493434433',
                        session_id='8068a28b7eba753983edb0221e50019b',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        order_list=['000384314e091e7a8147011f991bf040']
                    ),
                    session(
                        phone_pd_id='37493434433',
                        session_id='8068a28b7eba753983edb0221e50019b',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        order_list=['c319daa552c71c6db92c033ed8fe0950']
                    ),
                    session(
                        phone_pd_id='37493434433',
                        session_id='8069a28b7eba753983edb0221e50021c',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        order_list=['6636ee1de9513c6fa842edb4f2fe8b83']
                    ),
                ],
                [
                    order(
                        utc_order_dt='2020-03-11',
                        order_id='000384314e091e7a8147011f991bf040',
                        user_phone_pd_id='37493434433'
                    ),
                    order(
                        utc_order_dt='2020-03-11',
                        order_id='c319daa552c71c6db92c033ed8fe0950',
                        user_phone_pd_id='37493434433'
                    ),
                    order(
                        utc_order_dt='2020-03-11',
                        order_id='6636ee1de9513c6fa842edb4f2fe8b83',
                        user_phone_pd_id='37493434433'
                    )
                ],
                # expected_result_phone_check
                [],
                # expected_check_report
                CheckResult('MockedUserPhoneCheck', 0, 0, '')
            ),
            pytest.param(
                [
                    session(
                        phone_pd_id='37493434433',
                        session_id='8068a28b7eba753983edb0221e50019b',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        order_list=['000384314e091e7a8147011f991bf040']
                    ),
                    session(
                        phone_pd_id='37493434433',
                        session_id='8068a28b7eba753983edb0221e50019b',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        order_list=['c319daa552c71c6db92c033ed8fe0950']
                    ),
                    session(
                        phone_pd_id='37493434433',
                        session_id='310b7519c45670d8523a4dda465849e7',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        order_list=['aa063c86e14e242d93effd47bff93f1e']
                    ),
                ],
                [
                    order(
                        utc_order_dt='2020-03-11',
                        order_id='e05835c659d938c68a24a466e9143563',
                        user_phone_pd_id='374934344667'
                    ),
                    order(
                        utc_order_dt='2020-03-11',
                        order_id='e7956aeba1832812b8137222b6b9a11a',
                        user_phone_pd_id='79174384366'
                    ),
                    order(
                        utc_order_dt='2020-03-11',
                        order_id='e796d14092352e079488cce2707dc79b',
                        user_phone_pd_id='79174384366'
                    ),
                    order(
                        utc_order_dt='2020-03-11',
                        order_id='c319daa552c71c6db92c033ed8fe0950',
                        user_phone_pd_id='79174384366'
                    ),
                ],
                # expected_result_phone_check
                [
                    {
                        'order_id': 'e796d14092352e079488cce2707dc79b',
                        'user_phone_pd_id': '79174384366',
                        'utc_order_dt': '2020-03-11'
                    },
                    {
                        'order_id': 'e7956aeba1832812b8137222b6b9a11a',
                        'user_phone_pd_id': '79174384366',
                        'utc_order_dt': '2020-03-11'
                    },
                    {
                        'order_id': 'e05835c659d938c68a24a466e9143563',
                        'user_phone_pd_id': '374934344667',
                        'utc_order_dt': '2020-03-11'
                    }
                ],
                # expected_check_report
                CheckResult(
                    'MockedUserPhoneCheck', 3, 3,
                    'Не все заказы с заполненным user_phone_pd_id из дня N попали в сессии,'
                    ' пример order_id = e796d14092352e079488cce2707dc79b.'
                )

            )
        ]
    )
# Fixme https://st.yandex-team.ru/SPYT-55
@pytest.mark.slow
def test_demand_session_user_phone_check(
        sessions, orders,
        expected_result_phone_check,
        expected_check_report,
        local_spark_session
):
    class MockedUserPhoneCheck(DemandSessionUserPhoneCheck):
        def _read_orders_df(self):
            return local_spark_session.createDataFrame(list(orders))

        def _read_sessions_df(self):
            return local_spark_session.createDataFrame(list(sessions))

    check = MockedUserPhoneCheck({
            'start_date': datetime.datetime(2020, 3, 11),
            'end_date': datetime.datetime(2020, 3, 12)
        })

    do_check(check, local_spark_session, expected_result_phone_check, expected_check_report)


@pytest.mark.skip(reason="test requires rewrite or deletion (TAXIDWH-9153)")
@pytest.mark.parametrize(
        'sessions, expected_result_unique_id_check, expected_check_report',
        [
            pytest.param(
                [
                    session(
                        phone_pd_id='37493434433',
                        session_id='8068a28b7eba753983edb0221e50019b',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        order_list=['000384314e091e7a8147011f991bf040']
                    ),
                    session(
                        phone_pd_id='37493434433',
                        session_id='8068a28b7eba753983edb0221e50019b',
                        utc_session_start_dttm='2020-03-10 10:00:50',
                        order_list=['c319daa552c71c6db92c033ed8fe0950']
                    ),
                    session(
                        phone_pd_id='37493434433',
                        session_id='8069a28b7eba753983edb0221e50021c',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        order_list=['6636ee1de9513c6fa842edb4f2fe8b83']
                    ),
                ],
                # expected_result_unique_id_check
                [
                    {'count': 2, 'session_id': '8068a28b7eba753983edb0221e50019b'}
                ],
                # expected_check_report
                CheckResult(
                    'MockedUniqueIdCheck', 1, 1,
                    'В деманд-сессиях есть дубликаты. '
                    'Пример: session_id = 8068a28b7eba753983edb0221e50019b не уникален в рамках дня N и (N-1).'
                )

            ),
            pytest.param(
                [
                    session(
                        phone_pd_id='37493434433',
                        session_id='8068a28b7eba753983edb0221e50019b',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        order_list=['000384314e091e7a8147011f991bf040']
                    ),
                    session(
                        phone_pd_id='37493434433',
                        session_id='8068a28b7eba753983edb0221e50019b',
                        utc_session_start_dttm='2020-03-14 13:08:50',
                        order_list=['c319daa552c71c6db92c033ed8fe0950']
                    ),
                    session(
                        phone_pd_id='37493434433',
                        session_id='310b7519c45670d8523a4dda465849e7',
                        utc_session_start_dttm='2020-03-11 05:00:34',
                        order_list=['aa063c86e14e242d93effd47bff93f1e']
                    ),
                ],
                # expected_result_unique_id_check
                [],
                # expected_check_report
                CheckResult('MockedUniqueIdCheck', 0, 0, '')
            ),
            pytest.param(
                [
                    session(
                        phone_pd_id='37493434433',
                        session_id='8068a28b7eba753983edb0221e50019b',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        order_list=['000384314e091e7a8147011f991bf040']
                    ),
                    session(
                        phone_pd_id='37493434433',
                        session_id='8075c27a8fh89ba753983edb0221e500n',
                        utc_session_start_dttm='2020-03-10 10:04:50',
                        order_list=['c319daa552c71c6db92c033ed8fe0950']
                    ),
                    session(
                        phone_pd_id='37493434433',
                        session_id='560bc7y7945670d8523a4dda4658gg7',
                        utc_session_start_dttm='2020-03-11 13:07:50',
                        order_list=['aa063c86e14e242d93effd47bff93f1e']
                    ),
                ],
                # expected_result_unique_id_check
                [],
                # expected_check_report
                CheckResult('MockedUniqueIdCheck', 0, 0, '')
            )
        ]
)
@pytest.mark.slow
def test_demand_unique_user_id_check(
        sessions, expected_result_unique_id_check,
        expected_check_report, local_spark_session
):
    class MockedUniqueIdCheck(DemandSessionUniqueIdCheck):
        def _read_sessions_df(self):
            return local_spark_session.createDataFrame(list(sessions))

    check = MockedUniqueIdCheck({
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
                        phone_pd_id='37493434433',
                        session_id='8068a28b7eba753983edb0221e50019b',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        utc_session_end_dttm='2020-03-11 21:04:50',
                        order_list=['000384314e091e7a8147011f991bf040']
                    ),
                    session(
                        phone_pd_id='37493434433',
                        session_id='8069a28b7eba753983edb0221e50021c',
                        utc_session_start_dttm='2020-03-11 19:01:50',
                        utc_session_end_dttm='2020-03-11 22:04:50',
                        order_list=['6636ee1de9513c6fa842edb4f2fe8b83']
                    ),
                ],
                # expected_result_overlap_check result
                [
                    {
                        'session_id': '8068a28b7eba753983edb0221e50019b',
                        'utc_session_start_dttm': '2020-03-11 18:04:50',
                        'utc_session_end_dttm': '2020-03-11 21:04:50',
                        'next_utc_session_start_dttm': '2020-03-11 19:01:50',
                        'next_session_id': '8069a28b7eba753983edb0221e50021c'
                    }
                ],
                # expected_check_report
                CheckResult(
                    'MockedOverlapCheck', 1, 1,
                    'В деманд-сессиях есть пересечения: сессии 8068a28b7eba753983edb0221e50019b '
                    'и 8069a28b7eba753983edb0221e50021c пересекаются в рамках дней N и (N-1)'
                )


            ),
            pytest.param(
                [
                    session(
                        phone_pd_id='37493434433',
                        session_id='8068a28b7eba753983edb0221e50019b',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        utc_session_end_dttm='2020-03-11 19:04:50',
                        order_list=['000384314e091e7a8147011f991bf040']
                    ),
                    session(
                        phone_pd_id='37493434433',
                        session_id='8068a28b7eba753983edb0221ehjjj54',
                        utc_session_start_dttm='2020-03-10 10:04:50',
                        utc_session_end_dttm='2020-03-10 12:04:50',
                        order_list=['c319daa552c71c6db92c033ed8fe0950']
                    )
                ],
                # expected_result_overlap_check result
                [],
                # expected_check_report
                CheckResult('MockedOverlapCheck', 0, 0, '')
            ),
            pytest.param(
                [
                    session(
                        phone_pd_id='37493434433',
                        session_id='8068a28b7eba753983edb0221e50019b',
                        utc_session_start_dttm='2020-03-11 18:04:50',
                        utc_session_end_dttm='2020-03-11 19:04:50',
                        order_list=['000384314e091e7a8147011f991bf040']
                    ),
                    session(
                        phone_pd_id='37493434433',
                        session_id='8068aghj6753983edb0221ehjjj54',
                        utc_session_start_dttm='2020-03-13 12:04:50',
                        utc_session_end_dttm='2020-03-13 12:04:50',
                        order_list=['c319daa552c71c6db92c033ed8fe0950']
                    )
                ],
                # expected_result_overlap_check result
                [],
                # expected_check_report
                CheckResult('MockedOverlapCheck', 0, 0, '')
            )
        ]
    )
@pytest.mark.slow
def test_demand_overlap_check(
        sessions, expected_result_overlap_check,
        expected_check_report, local_spark_session
):
    class MockedOverlapCheck(DemandSessionOverlapCheck):
        def _read_sessions_df(self):
            return local_spark_session.createDataFrame(list(sessions))

    check = MockedOverlapCheck({
        'start_date': datetime.datetime(2020, 3, 10),
        'end_date': datetime.datetime(2020, 3, 11)
    })

    do_check(check, local_spark_session, expected_result_overlap_check, expected_check_report)
