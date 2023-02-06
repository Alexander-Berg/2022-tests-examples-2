import datetime

from nile.api.v1 import clusters

from projects.geosuggest.data_context import v1 as data_context


def test_driver_stops_context():
    job = clusters.MockCluster().job()
    context = data_context.DriverStopsContext(
        job=job,
        begin_dttm=datetime.datetime(2019, 1, 1),
        end_dttm=datetime.datetime(2019, 6, 1),
    )
    context.get_driver_stops()


def test_orders_context():
    job = clusters.MockCluster().job()
    context = data_context.OrdersContext(
        job=job,
        begin_dttm=datetime.datetime(2019, 1, 1),
        end_dttm=datetime.datetime(2019, 6, 1),
    )
    context.get_dm_order()


def test_orders_with_stops_context():
    job = clusters.MockCluster().job()
    context = data_context.OrdersWithStopsContext(
        job=job,
        begin_dttm=datetime.datetime(2019, 1, 1),
        end_dttm=datetime.datetime(2019, 6, 1),
    )
    context.get_orders_w_stops()


def test_maps_context():
    job = clusters.MockCluster().job()
    context = data_context.MapsContext(job=job)
    context.get_objects()


def test_mlaas_logs_context():
    job = clusters.MockCluster().job()
    context = data_context.MLaaSLogsContext(
        job,
        begin_dttm=datetime.datetime(2019, 1, 1),
        end_dttm=datetime.datetime(2019, 6, 1),
    )
    context(uri=None, _type=None)


def test_umlaas_logs_context():
    job = clusters.MockCluster().job()
    context = data_context.UmlaasGeoLogsContext(
        job,
        begin_dttm=datetime.datetime(2019, 1, 1),
        end_dttm=datetime.datetime(2019, 6, 1),
    )
    context(uri=None, code_place=None)
    context(uri='/umlaas-geo/v1/finalsuggest', code_place='log_data')
