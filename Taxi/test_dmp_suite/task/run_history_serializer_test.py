import json
import datetime

from dmp_suite import datetime_utils as dtu
from dmp_suite.task.run_history.serializer import TaskArgsJSONEncoder, TaskArgsJSONDecoder


def test_custom_serializer():
    data_original = {
        'dt': datetime.date(2000, 12, 1),
        'dttm': datetime.datetime(2000, 12, 1, 23, 59, 59),
        'dttm_micro': datetime.datetime(2000, 12, 1, 23, 59, 59, 999999),
        'period': dtu.Period('2021-01-01 20:55:55', '2021-01-02'),
        'period_micro': dtu.Period('2021-01-01 20:55:55.999998', '2021-01-01 20:55:55.999999'),
        'period_mix': dtu.Period('2021-01-01', '2021-01-01 20:55:55.999999')
    }
    data_str = json.dumps(data_original, cls=TaskArgsJSONEncoder)
    data_deserialized = json.loads(data_str, cls=TaskArgsJSONDecoder)
    assert data_deserialized == data_original
