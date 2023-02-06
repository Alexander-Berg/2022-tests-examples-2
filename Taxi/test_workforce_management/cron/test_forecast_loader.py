# pylint: disable=redefined-outer-name
import pytest

from workforce_management.crontasks import daily_plan_prediction_calculate
from workforce_management.generated.cron import run_cron
from workforce_management.storage.postgresql import forecast

CRON_ARGS = [
    'workforce_management.crontasks.daily_plan_prediction_calculate',
    '-t',
    '0',
]

TABLES = ['2020-02-20', '2020-02-21', '2020-02-22']

RECORDS = [
    {
        'hour_calls_forecast_base': 256,
        'hour_calls_forecast_lower': 224,
        'hour_calls_forecast_upper': 286,
        'skill_code': 'disp_ar',
        'utc_launch_dttm': '2021-02-22 04:42:24',
        'utc_dttm': '2021-02-22 19:00:00',
    },
    {
        'hour_calls_forecast_base': 213,
        'hour_calls_forecast_lower': 186,
        'hour_calls_forecast_upper': 238,
        'skill_code': 'disp_ar',
        'utc_launch_dttm': '2021-02-22 04:42:24',
        'utc_dttm': '2021-02-22 20:00:00',
    },
    {
        'hour_calls_forecast_base': 240,
        'hour_calls_forecast_lower': 210,
        'hour_calls_forecast_upper': 268,
        'skill_code': 'disp',
        'utc_launch_dttm': '2021-02-22 04:42:24',
        'utc_dttm': '2021-02-22 21:00:00',
    },
    {
        'hour_calls_forecast_base': 186,
        'hour_calls_forecast_lower': 163,
        'hour_calls_forecast_upper': 208,
        'skill_code': 'disp_ar',
        'utc_launch_dttm': '2021-02-22 04:42:24',
        'utc_dttm': '2021-02-22 22:00:00',
    },
]

LAST_TABLE = ['2021-02-22']
LAST_RECORDS = [
    {
        'hour_calls_forecast_base': 256,
        'hour_calls_forecast_lower': 224,
        'hour_calls_forecast_upper': 286,
        'skill_code': 'disp_ar',
        'utc_launch_dttm': '2021-02-22 04:42:24',
        'utc_dttm': '2021-03-07 23:00:00',
    },
]

NEW_TABLE = ['2021-02-21', '22-02-2021', '23-02-2021']
NEW_RECORDS = [
    {
        'hour_calls_forecast_base': 256,
        'hour_calls_forecast_lower': 224,
        'hour_calls_forecast_upper': 286,
        'skill_code': 'disp_ar',
        'utc_launch_dttm': '2021-02-22 04:42:24',
        'utc_dttm': '2021-03-21 20:00:00',
    },
    {
        'hour_calls_forecast_base': 256,
        'hour_calls_forecast_lower': 224,
        'hour_calls_forecast_upper': 286,
        'skill_code': 'disp_ar',
        'utc_launch_dttm': '2021-02-22 04:42:24',
        'utc_dttm': '2021-03-21 21:00:00',
    },
    {
        'hour_calls_forecast_base': 256,
        'hour_calls_forecast_lower': 224,
        'hour_calls_forecast_upper': 286,
        'skill_code': 'disp_ru',
        'utc_launch_dttm': '2021-02-22 04:42:24',
        'utc_dttm': '2021-03-21 21:00:00',
    },
]

DOMAIN = 'taxi'
SOURCE_PATH = '//home/taxi_ml/dev/callcenter_calls_forecast/hourly_forecasts'
PERIOD_MINUTES = 20100


@pytest.mark.now('2016-05-06T12:00:00.0')
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            id='legacy_queue_mapping',
            marks=[
                pytest.mark.config(
                    WORKFORCE_MANAGEMENT_FORECAST_QUEUE_SKILL_MAPPING={
                        'disp_ar': 'russia',
                        'disp_ru': 'russia',
                        'disp': 'nerussia',
                    },
                    WORKFORCE_MANAGEMENT_FORECAST_SETTINGS={
                        'taxi': {
                            'source_path': SOURCE_PATH,
                            'end_of_period_minutes': PERIOD_MINUTES,
                        },
                        'eats': {
                            'source_path': SOURCE_PATH,
                            'end_of_period_minutes': PERIOD_MINUTES,
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            id='new_forecast_mapping',
            marks=[
                pytest.mark.pgsql(
                    'workforce_management', files=['forecast_mappings.sql'],
                ),
                pytest.mark.config(
                    WORKFORCE_MANAGEMENT_FORECAST_SETTINGS={
                        'taxi': {
                            'source_type': 'yt_v1',
                            'source_path': SOURCE_PATH,
                            'end_of_period_minutes': PERIOD_MINUTES,
                        },
                        'eats': {
                            'source_type': 'yt_v1',
                            'source_path': SOURCE_PATH,
                            'end_of_period_minutes': PERIOD_MINUTES,
                        },
                    },
                ),
            ],
        ),
    ],
)
@pytest.mark.pgsql('workforce_management', files=['skills.sql'])
async def test_example(cron_context, patch):
    @patch('taxi.clients.yt.YtClient.get')
    async def _(*args, **kwargs):
        return TABLES

    @patch('taxi.clients.yt.YtClient.read_table')
    async def _(*args, **kwargs):
        return RECORDS

    await run_cron.main(CRON_ARGS)

    db = forecast.ForecastRepo(context=cron_context)
    async with db.master.acquire() as conn:
        records = await db.get_forecasts(
            conn,
            forecast_type=daily_plan_prediction_calculate.FORECAST_TYPE,
            value_type=daily_plan_prediction_calculate.FORECAST_VALUE_TYPE,
            domain=DOMAIN,
        )

    assert len(records) == 12

    await run_cron.main(CRON_ARGS)

    async with db.master.acquire() as conn:
        records = await db.get_forecasts(
            conn,
            forecast_type=daily_plan_prediction_calculate.FORECAST_TYPE,
            value_type=daily_plan_prediction_calculate.FORECAST_VALUE_TYPE,
            domain=DOMAIN,
        )

    # same data wasnt updated
    assert len(records) == 12

    @patch('taxi.clients.yt.YtClient.get')
    async def _(*args, **kwargs):
        return LAST_TABLE

    @patch('taxi.clients.yt.YtClient.read_table')
    async def _(*args, **kwargs):
        return LAST_RECORDS

    await run_cron.main(CRON_ARGS)

    async with db.master.acquire() as conn:
        records = await db.get_forecasts(
            conn,
            forecast_type=daily_plan_prediction_calculate.FORECAST_TYPE,
            value_type=daily_plan_prediction_calculate.FORECAST_VALUE_TYPE,
            domain=DOMAIN,
        )

    assert len(records) == 13

    @patch('taxi.clients.yt.YtClient.get')
    async def _(*args, **kwargs):
        return NEW_TABLE

    @patch('taxi.clients.yt.YtClient.read_table')
    async def _(*args, **kwargs):
        return NEW_RECORDS

    await run_cron.main(CRON_ARGS)

    async with db.master.acquire() as conn:
        records = await db.get_forecasts(
            conn,
            forecast_type=daily_plan_prediction_calculate.FORECAST_TYPE,
            value_type=daily_plan_prediction_calculate.FORECAST_VALUE_TYPE,
            domain=DOMAIN,
        )

    # updated only one table, cause previous has last period record
    assert len(records) == 15

    for record in records:
        # check correct sum values
        assert record['base_value'] == record['plan_value']

    async with db.master.acquire() as conn:
        records = await db.get_forecast_entity(conn, domain=DOMAIN)
        assert (
            records[0]['name'] == 'Прогноз 23-02-2021'
            ' на навык Россия с 21-03-2021 по 21-03-2021'
        )
