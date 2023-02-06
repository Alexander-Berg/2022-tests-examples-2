from nile.api.v1 import Record
from nile.api.v1 import aggregators as na
from qb2.api.v1 import filters as qf

from taxi_etl.layer.yt.dds.handbooks_common.generator import HandbookDimension
from taxi_etl.layer.yt.dds.handbooks_common.generator_nile import NileHandbookQueryGenerator, \
    FirstNileHandbookAggregator, LastNileHandbookAggregator

ORDER_KIND_AGGREGATORS = [
    FirstNileHandbookAggregator("first", "utc_created_dttm"),
    LastNileHandbookAggregator("last", "utc_created_dttm")
]

ORDER_SOURCE_DIMENSION = [
    HandbookDimension.any(),
    HandbookDimension("yandex", qf.equals("brand", "yandex"))
]

ORDER_SUCCESS_DIMENSION = [
    HandbookDimension.any(),
    HandbookDimension("success",
                      qf.and_(qf.equals("status", "finished"), qf.equals("taxi_status", "complete")))
]

TEST_NILE_ORDER_HANDBOOK_GENERATOR = NileHandbookQueryGenerator(
    aggregators=ORDER_KIND_AGGREGATORS,
    dimensions=[
        ORDER_SOURCE_DIMENSION,
        ORDER_SUCCESS_DIMENSION,
    ],
    suffix="order",
    fields={
        "utc_created_dttm": "utc_order_created_dttm",
    }
)
########################################################################
MAKE_MERGE_EXPECTED_DICT = {
    "last_order_utc_created_dttm":
        na.last("last_order_utc_created_dttm", "last_order_utc_created_dttm"),
    "last_success_order_utc_created_dttm":
        na.last("last_success_order_utc_created_dttm", "last_success_order_utc_created_dttm"),
    "first_order_utc_created_dttm":
        na.first("first_order_utc_created_dttm", "first_order_utc_created_dttm"),
    "last_yandex_order_utc_created_dttm":
        na.last("last_yandex_order_utc_created_dttm", "last_yandex_order_utc_created_dttm"),
    "first_success_order_utc_created_dttm":
        na.first("first_success_order_utc_created_dttm", "first_success_order_utc_created_dttm"),
    "first_yandex_order_utc_created_dttm":
        na.first("first_yandex_order_utc_created_dttm", "first_yandex_order_utc_created_dttm"),
    "last_yandex_success_order_utc_created_dttm":
        na.last("last_yandex_success_order_utc_created_dttm", "last_yandex_success_order_utc_created_dttm"),
    "first_yandex_success_order_utc_created_dttm":
        na.first("first_yandex_success_order_utc_created_dttm", "first_yandex_success_order_utc_created_dttm")
}
########################################################################

MAKE_AGGREGATIONS_EXPECTED_DICT = {
    "last_order_utc_created_dttm":
        na.last("utc_order_created_dttm", "utc_order_created_dttm"),
    "last_success_order_utc_created_dttm":
        na.last("utc_order_created_dttm", "utc_order_created_dttm",
                predicate=qf.and_(qf.equals("status", "finished"),
                                  qf.equals("taxi_status", "complete"))),
    "first_order_utc_created_dttm":
        na.first("utc_order_created_dttm", "utc_order_created_dttm"),
    "last_yandex_order_utc_created_dttm":
        na.last("utc_order_created_dttm", "utc_order_created_dttm",
                predicate=qf.equals("brand", "yandex")),
    "first_success_order_utc_created_dttm":
        na.first("utc_order_created_dttm", "utc_order_created_dttm",
                 predicate=qf.and_(qf.equals("status", "finished"),
                                   qf.equals("taxi_status", "complete"))),
    "first_yandex_order_utc_created_dttm":
        na.first("utc_order_created_dttm", "utc_order_created_dttm",
                 predicate=qf.and_(qf.equals("brand", "yandex"))),
    "last_yandex_success_order_utc_created_dttm":
        na.last("utc_order_created_dttm", "utc_order_created_dttm",
                predicate=qf.and_(qf.equals("brand", "yandex"),
                                  qf.and_(qf.equals("status", "finished"),
                                          qf.equals("taxi_status", "complete")))),
    "first_yandex_success_order_utc_created_dttm":
        na.first("utc_order_created_dttm", "utc_order_created_dttm",
                 predicate=qf.and_(qf.equals("brand", "yandex"),
                                   qf.and_(qf.equals("status", "finished"),
                                           qf.equals("taxi_status", "complete"))))
}
########################################################################

SPLIT_AND_PROJECT_EXPECTED_FIRST_UTC_CREATED_DTTM = [
    Record(first_order_utc_created_dttm="1", first_success_order_utc_created_dttm="1",
           first_yandex_order_utc_created_dttm="1", first_yandex_success_order_utc_created_dttm="1",
           id="1",
           last_order_utc_created_dttm="1", last_success_order_utc_created_dttm="1",
           last_yandex_order_utc_created_dttm="1", last_yandex_success_order_utc_created_dttm="1"),
    Record(first_order_utc_created_dttm="3", first_success_order_utc_created_dttm=None,
           first_yandex_order_utc_created_dttm="3", first_yandex_success_order_utc_created_dttm=None,
           id="3",
           last_order_utc_created_dttm="3", last_success_order_utc_created_dttm=None,
           last_yandex_order_utc_created_dttm="3", last_yandex_success_order_utc_created_dttm=None)]

SPLIT_AND_PROJECT_EXPECTED_LAST_UTC_CREATED_DTTM = [
    Record(first_order_utc_created_dttm="2", first_success_order_utc_created_dttm="2",
           first_yandex_order_utc_created_dttm=None, first_yandex_success_order_utc_created_dttm=None,
           id="1",
           last_order_utc_created_dttm="2", last_success_order_utc_created_dttm="2",
           last_yandex_order_utc_created_dttm=None, last_yandex_success_order_utc_created_dttm=None),
    Record(first_order_utc_created_dttm="3", first_success_order_utc_created_dttm=None,
           first_yandex_order_utc_created_dttm="3", first_yandex_success_order_utc_created_dttm=None,
           id="3",
           last_order_utc_created_dttm="3", last_success_order_utc_created_dttm=None,
           last_yandex_order_utc_created_dttm="3", last_yandex_success_order_utc_created_dttm=None)]
########################################################################
