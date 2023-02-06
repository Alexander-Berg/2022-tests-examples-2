import json
from dmp_suite.data_transform import Project
from dmp_suite.file_utils import from_same_directory
from taxi_etl.layer.yt.ods.dbtaxi.park_client.impl import EXTRACTORS


RAW_JSON = "data/raw_parks.json"
ODS_JSON = "data/ods_park_client.json"


def test_new_transformation():
    EXTRACT = Project(extractors=EXTRACTORS)
    with open(from_same_directory(__file__, RAW_JSON)) as raw,\
            open(from_same_directory(__file__, ODS_JSON)) as ods:
        record = json.load(raw)[0]['doc']
        ods = json.load(ods)[0]
        assert EXTRACT.apply(record) == ods

