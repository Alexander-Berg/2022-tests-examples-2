# pylint: disable=unused-variable
import pytest

from signal_device_api_worker.generated.cron import run_cron  # noqa F401

CRON_PARAMS = [
    'signal_device_api_worker.crontasks.sim_meta_updater',
    '-t',
    '0',
]


def _check_sim_meta(pgsql, expected_meta):
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT imsi, msisdn '
        'FROM signal_device_api.sim_meta '
        'ORDER BY imsi ASC',
    )
    db_result = list(db)
    assert len(db_result) == len(expected_meta)

    for pg_data, expected in zip(db_result, expected_meta):
        assert pg_data[0] == expected[0]
        assert pg_data[1] == expected[1]


@pytest.mark.config(
    SIGNAL_DEVICE_API_WORKER_SPRINT_SETTINGS={
        'meta_updater_enabled': True,
        'meta_batch_size': 1,
        'provider_id': 42,
        'traffic_batch_size': 100,
        'traffic_parallel_updates': 10,
        'attempts': 2,
    },
)
async def test_ok(pgsql, mockserver):
    first_request = True

    @mockserver.json_handler('/sprint/www/O:ya-taxi/GetMembers.json')
    def _get_members(request):
        nonlocal first_request
        if first_request:
            first_request = False
            return 'invalid response'

        assert request.headers['Authorization'] == 'test_pass'

        query = request.query
        assert query['PROVIDER_ID'] == '42'
        assert query['Lim'] == '1'
        assert query['Ofs'] in ['1', '2', '3']
        assert query['IS_MI'] in ['0', '1', '2']

        if query['IS_MI'] != '0' or query['Ofs'] > '2':
            return {'STATUS': 'OK', 'Numbers': []}

        if request.query['Ofs'] == '1':
            return {
                'STATUS': 'OK',
                'Numbers': [{'IMSI': 'hey', 'MSISDN': 'x'}],
            }

        return {'STATUS': 'OK', 'Numbers': [{'IMSI': 'test', 'MSISDN': 'y'}]}

    await run_cron.main(CRON_PARAMS)

    _check_sim_meta(pgsql, [('hey', 'x'), ('test', 'y')])

    # Тест на полный цикл обновления – несколько выгрузок,
    # начинаем с пустой базы, потом происходит пересечение по данным в ответах
    @mockserver.json_handler('/sprint/www/O:ya-taxi/GetMembers.json')
    def _get_members_intersection(request):
        if request.query['Ofs'] > '1':
            return {'STATUS': 'OK', 'Numbers': []}

        return {
            'STATUS': 'OK',
            'Numbers': [
                {'IMSI': 'test', 'MSISDN': 'y'},
                {'IMSI': 'kek', 'MSISDN': 'z'},
            ],
        }

    await run_cron.main(CRON_PARAMS)

    _check_sim_meta(pgsql, [('hey', 'x'), ('kek', 'z'), ('test', 'y')])
