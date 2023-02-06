# note: тестирование в рамках проекта take-out https://st.yandex-team.ru/TAXIDWH-16265
# цель: показать, что анонимизация спектра полей не повлечет деградацию стабильности расчета
import json
import pytest

from dmp_suite.data_transform import Project, FlatMap
from dmp_suite.file_utils import from_same_directory

from taxi_etl.layer.yt.ods.mdb.order.extractors import ORDERS_EXTRACTORS, ORDER_PROC_EXTRACTORS
from ...takeout.impl import get_json_file
from ...takeout import data as data_package


RAW_ORDER_JSON = "raw_order.json"
RAW_ORDER_PROC_JSON = "raw_order_proc.json"
ODS_ORDER_JSON = "data/ods_order.json"
ODS_ORDER_PROC_JSON = "data/ods_order_proc.json"


@pytest.mark.parametrize(
    "raw_json, ods_json, extractors",
    [
        (RAW_ORDER_JSON, ODS_ORDER_JSON, ORDERS_EXTRACTORS),
        (RAW_ORDER_PROC_JSON, ODS_ORDER_PROC_JSON, ORDER_PROC_EXTRACTORS),
    ]
)
def test_transformation(raw_json, ods_json, extractors):
    transformation = Project(extractors=extractors)

    with open(get_json_file(data_package, raw_json)) as raw,\
            open(from_same_directory(__file__, ods_json)) as ods:
        raw_list = [entry["doc"] for entry in json.load(raw)]
        ods_list = json.load(ods)
        assert [transformation.apply(record)
                for record in raw_list] == ods_list
