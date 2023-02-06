# note: тестирование в рамках проекта take-out https://st.yandex-team.ru/TAXIDWH-16265
# цель: показать, что анонимизация спектра полей не повлечет деградацию стабильности расчета
import json

from dmp_suite.data_transform import Project, FlatMap
from dmp_suite.file_utils import from_same_directory

from taxi_etl.layer.yt.ods.dbprocessing.order_destination_point.impl import EXTRACTORS, extract_destinations
from ...takeout.impl import get_json_file, evaluate_map_objs
from ...takeout import data as data_package


RAW_ORDER_PROC_JSON = "raw_order_proc.json"
ODS_JSON = "data/ods.json"
# note: странная история, эти экстракторы напрямую не перечислены в имплементации
# загрузчика, и тест их не видит, однако, на практике загрузка работает.
# как будто, средство тестирования отличается от продакшн процесса, непонятно
ADDITIONAL_EXTRACTORS = dict(
    destination_seq="destination_seq",
    destination_full_address="destination_full_address",
    destination_locality_name="destination_locality_name",
    destination_porch_code="destination_porch_code",
    destination_premise_code="destination_premise_code",
    destination_thoroughfare_name="destination_thoroughfare_name",
    destination_apartment_code="destination_apartment_code",
    destination_comment="destination_comment",
    destination_doorphone_code="destination_doorphone_code",
    destination_floor_code="destination_floor_code",
    extra_recipient_contact_phone_id="extra_recipient_contact_phone_id",
    destination_lat="destination_lat",
    destination_lon="destination_lon",
    destination_geohash="destination_geohash",
)
FULL_EXTRACTORS = {**EXTRACTORS, **ADDITIONAL_EXTRACTORS}


def test_transformation():
    flat_map = FlatMap(extract_destinations)
    transformation = Project(extractors=FULL_EXTRACTORS)
    with open(get_json_file(data_package, RAW_ORDER_PROC_JSON)) as raw,\
            open(from_same_directory(__file__, ODS_JSON)) as ods:
        raw_list = [entry["doc"] for entry in json.load(raw)]
        ods_list = json.load(ods)
        raw_ods_list = flat_map(raw_list)
        assert [evaluate_map_objs(transformation.apply(record))
                for record in raw_ods_list] == ods_list
