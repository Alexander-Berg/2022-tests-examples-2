# note: тестирование в рамках проекта take-out https://st.yandex-team.ru/TAXIDWH-16265
# цель: показать, что анонимизация спектра полей не повлечет деградацию стабильности расчета
import json

from dmp_suite.data_transform import Project
from dmp_suite.file_utils import from_same_directory

from taxi_etl.layer.yt.ods.dbprocessing.order.impl import EXTRACTORS
from ...takeout.impl import get_json_file, evaluate_map_objs
from ...takeout import data as data_package


RAW_ORDER_PROC_JSON = "raw_order_proc.json"
ODS_JSON = "data/ods.json"


def test_transformation():
    transformation = Project(extractors=EXTRACTORS)
    with open(get_json_file(data_package, RAW_ORDER_PROC_JSON)) as raw,\
            open(from_same_directory(__file__, ODS_JSON)) as ods:
        raw_list = [entry["doc"] for entry in json.load(raw)]
        ods_list = json.load(ods)
        assert [evaluate_map_objs(transformation.apply(record))
                for record in raw_list] == ods_list
