import logging as log
from datetime import datetime, timedelta

from sandbox.projects.market.contentApi.lib import capacity_task as ct, capacity_utils as cap

TOKEN = 'secret'
CHECKOUTER_ORDERS_FORECAST_SENSOR = 'ordersForecast'
CARTER_DAU_FORECAST_SENSOR = 'dauForecast'


def ignore_test_check_solomon():
    solomon = cap.solomon_checkouter(TOKEN)
    forecast_date_to = datetime.now()
    forecast_date_from = forecast_date_to - timedelta(days=60)
    o_forecast_ts, order_forecast_values = solomon.get_values(
        date_from=forecast_date_from,
        service_name='market-checkouter',
        sensor_name=CHECKOUTER_ORDERS_FORECAST_SENSOR)
    log.info('forecast orders')
    log.info(o_forecast_ts)
    log.info(order_forecast_values)
    if len(o_forecast_ts) == 0:
        raise Exception('Cannot calculate reservation: no data in "{}"'.format(CHECKOUTER_ORDERS_FORECAST_SENSOR))
    dau_forecast_ts, dau_forecast_values = solomon.get_values(
        date_from=forecast_date_from,
        service_name='market-checkouter',
        sensor_name=CARTER_DAU_FORECAST_SENSOR)
    log.info('forecast dau')
    log.info(dau_forecast_ts)
    log.info(dau_forecast_values)
    if len(dau_forecast_ts) == 0:
        raise Exception('Cannot calculate reservation: no data in "{}"'.format(CARTER_DAU_FORECAST_SENSOR))


def ignore_test_check_rps_98():
    solomon = cap.solomon_af(TOKEN)
    date_to = datetime.now() - timedelta(days=1)
    date_from = date_to - timedelta(days=1)
    log.info('quantile')
    log.info(cap.get_rps_quantile(
        solomon=solomon,
        date_from=date_from,
        date_to=date_to,
        quantile=0.98
    ))


def ignore_test_task():
    task = ct.CapacityTask(TOKEN)
    task.run()
