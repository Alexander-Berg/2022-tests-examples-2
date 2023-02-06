from dmp_suite import datetime_utils as dtu

from market_b2c_etl.layer.greenplum.ods.checkouter.item_event.extractors import _get_event_date_with_microseconds

def test_extractors():
    assert _get_event_date_with_microseconds(d={'from_date': "20-04-2022 23:54:31", 'event_id': 2907146272}, tz=dtu.UTC) == '2022-04-20 20:54:31.146272'
    assert _get_event_date_with_microseconds(d={'from_date': "20-04-2022 23:54:31", 'event_id': 2907146272}, tz=dtu.MSK) == '2022-04-20 23:54:31.146272'
    assert _get_event_date_with_microseconds(d={'from_date': "20-04-2022 23:54:31", 'event_id': 12907146272}, tz=dtu.UTC) == '2022-04-20 20:54:31.146272'
    assert _get_event_date_with_microseconds(d={'from_date': "20-04-2022 23:54:31", 'event_id': 12907146272}, tz=dtu.MSK) == '2022-04-20 23:54:31.146272'
