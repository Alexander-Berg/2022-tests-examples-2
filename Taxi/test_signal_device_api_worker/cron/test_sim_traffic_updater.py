# pylint: disable=unused-variable
import datetime

import pytest

from signal_device_api_worker.generated.cron import run_cron  # noqa F401

CRON_PARAMS = [
    'signal_device_api_worker.crontasks.sim_traffic_updater',
    '-t',
    '0',
]


@pytest.mark.pgsql('signal_device_api_meta_db', files=['setup_data.sql'])
@pytest.mark.config(
    SIGNAL_DEVICE_API_WORKER_SPRINT_SETTINGS={
        'traffic_updater_enabled': True,
        'meta_batch_size': 1,
        'provider_id': 42,
        'traffic_batch_size': 100,
        'traffic_parallel_updates': 10,
        'attempts': 2,
    },
)
@pytest.mark.dontfreeze
async def test_ok(pgsql, mockserver):
    first_request = True

    @mockserver.json_handler('/sprint/www/O:ya-taxi/dcGetAbonentCDR.json')
    def _get_members(request):
        nonlocal first_request
        if first_request:
            first_request = False
            return 'invalid response'

        assert request.headers['Authorization'] == 'test_pass'

        if request.query['MSISDN'] == 'test':
            return {
                'status': 'OK',
                'CDRs': [
                    {
                        # лишнее данные не должны учитываться
                        'MSISDN': 'test',
                        'CDRTYPE': 'PDP',
                        'QTY': '23,94',
                        'DATETIME': '01-02-2021 13:39:42',
                    },
                    {
                        'MSISDN': 'test',
                        'CDRTYPE': 'PDP',
                        'QTY': '228',
                        'DATETIME': '02-02-2021 1:39:12',
                    },
                    {
                        'MSISDN': 'test',
                        'CDRTYPE': 'PDP',
                        'QTY': '228',
                        'DATETIME': '02-02-2021 23:00:00',
                    },
                    {
                        # лишнее данные не должны учитываться
                        'MSISDN': 'test',
                        'CDRTYPE': 'PDP',
                        'QTY': '228',
                        'DATETIME': '03-02-2021 1:39:12',
                    },
                ],
            }

        if request.query['MSISDN'] == 'test_empty':
            return {'status': 'OK', 'CDRs': []}

        if request.query['MSISDN'] == 'test_new':
            return {
                'status': 'OK',
                'CDRs': [
                    {
                        'MSISDN': 'test_new',
                        'CDRTYPE': 'PDP',
                        'QTY': '123',
                        'DATETIME': '01-02-2021 15:00:00',
                    },
                ],
            }

        return {
            'status': 'OK',
            'CDRs': [
                {
                    'MSISDN': 'kek',
                    'CDRTYPE': 'PDP',
                    'QTY': '2',
                    'DATETIME': '01-02-2021 20:00:00',
                },
                {
                    'MSISDN': 'kek',
                    'CDRTYPE': 'PDP',
                    'QTY': '23,94',
                    'DATETIME': '01-02-2021 23:39:12',
                },
            ],
        }

    await run_cron.main(CRON_PARAMS)

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT msisdn, mb_spent_daily, day, max_session_at '
        'FROM signal_device_api.sim_stats '
        'ORDER BY msisdn ASC, day ASC',
    )
    db_result = list(db)
    assert db_result == [
        (
            'kek',
            25.94,
            datetime.date(2021, 2, 1),
            datetime.datetime(2021, 2, 1, 23, 39, 12),
        ),
        (
            'test',
            1.0,
            datetime.date(2021, 1, 1),
            datetime.datetime(2021, 1, 1, 13, 39, 40),
        ),
        (
            'test',
            1.0,
            datetime.date(2021, 2, 1),
            datetime.datetime(2021, 2, 1, 13, 39, 40),
        ),
        (
            'test',
            456.0,
            datetime.date(2021, 2, 2),
            datetime.datetime(2021, 2, 2, 23, 00, 00),
        ),
        (
            'test_empty',
            3210.0,
            datetime.date(2021, 2, 1),
            datetime.datetime(2021, 2, 1, 13, 39, 42),
        ),
        (
            'test_empty',
            0.0,
            datetime.date(2021, 2, 2),
            datetime.datetime(2021, 2, 2, 00, 00, 00),
        ),
        (
            'test_new',
            123.0,
            datetime.date(2021, 2, 1),
            datetime.datetime(2021, 2, 1, 15, 00, 00),
        ),
    ]


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['empty_traffic_data.sql'],
)
@pytest.mark.config(
    SIGNAL_DEVICE_API_WORKER_SPRINT_SETTINGS={
        'traffic_updater_enabled': True,
        'meta_batch_size': 1,
        'provider_id': 42,
        'traffic_batch_size': 100,
        'traffic_parallel_updates': 10,
        'attempts': 0,
    },
)
@pytest.mark.dontfreeze
async def test_empty_traffic(pgsql, mockserver):
    @mockserver.json_handler('/sprint/www/O:ya-taxi/dcGetAbonentCDR.json')
    def _get_members(request):
        assert request.headers['Authorization'] == 'test_pass'

        if request.query['START_DATE'] == '2021.01.04 00:00:00':
            return {
                'status': 'OK',
                'CDRs': [
                    {
                        'MSISDN': 'test',
                        'CDRTYPE': 'PDP',
                        'QTY': '1',
                        'DATETIME': '04-01-2021 13:39:40',
                    },
                    {
                        'MSISDN': 'test',
                        'CDRTYPE': 'PDP',
                        'QTY': '228',
                        'DATETIME': '04-01-2021 18:39:42',
                    },
                    {
                        'MSISDN': 'test',
                        'CDRTYPE': 'PDP',
                        'QTY': '1',
                        'DATETIME': '04-01-2021 23:00:00',
                    },
                ],
            }
        if request.query['START_DATE'] == '2021.01.06 00:00:00':
            return {
                'status': 'OK',
                'CDRs': [
                    {
                        'MSISDN': 'test',
                        'CDRTYPE': 'PDP',
                        'QTY': '322',
                        'DATETIME': '06-01-2021 5:49:45',
                    },
                    {
                        'MSISDN': 'test',
                        'CDRTYPE': 'PDP',
                        'QTY': '1',
                        'DATETIME': '06-01-2021 23:49:45',
                    },
                ],
            }
        return {'status': 'OK', 'CDRs': []}

    await run_cron.main(CRON_PARAMS)
    await run_cron.main(CRON_PARAMS)
    await run_cron.main(CRON_PARAMS)

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT msisdn, mb_spent_daily, day, max_session_at '
        'FROM signal_device_api.sim_stats '
        'ORDER BY msisdn ASC, day ASC',
    )
    db_result = list(db)
    assert db_result == [
        (
            'test',
            230.0,
            datetime.date(2021, 1, 4),
            datetime.datetime(2021, 1, 4, 23, 0, 0),
        ),
        (
            'test',
            0.0,
            datetime.date(2021, 1, 5),
            datetime.datetime(2021, 1, 5, 0, 0, 0),
        ),
        (
            'test',
            323,
            datetime.date(2021, 1, 6),
            datetime.datetime(2021, 1, 6, 23, 49, 45),
        ),
        (
            'test2',
            1.0,
            datetime.date(2021, 1, 10),
            datetime.datetime(2021, 1, 10, 13, 39, 40),
        ),
    ]

    db.execute(
        'SELECT last_requested_traffic_datetime::DATE, '
        '       max_session_at, '
        '       last_requested_traffic_datetime '
        'FROM signal_device_api.sim_meta '
        'ORDER BY msisdn ASC',
    )
    db_result = list(db)
    assert db_result == [
        (
            datetime.date(2021, 1, 7),
            datetime.datetime(2021, 1, 6, 23, 49, 45),
            datetime.datetime(2021, 1, 7, 0, 0, 0),
        ),
    ]
