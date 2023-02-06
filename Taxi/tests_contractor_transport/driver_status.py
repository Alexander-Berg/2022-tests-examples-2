# pylint: disable=wildcard-import, import-error
import datetime
import gzip

import flatbuffers

# pylint: disable=no-name-in-module
from driver_status.fbs.v2.statuses import Item as FbsDriverStatusesItem
from driver_status.fbs.v2.statuses import List as FbsDriverStatusesList
from driver_status.fbs.v2.statuses import Status as FbsStatus


def _get_current_timestamp(minus_hours=None):
    required_time = datetime.datetime.now()
    if minus_hours is not None:
        required_time = required_time - datetime.timedelta(hours=minus_hours)
    return int((required_time.timestamp() * 1e6))


def _replace_ts(timestamp):
    prefix = 'now_minus_'
    if isinstance(timestamp, str) and timestamp.startswith(prefix):
        minus_hours = timestamp[len(prefix) :]
        if minus_hours.isdecimal():
            return _get_current_timestamp(int(minus_hours))
    return timestamp


def _str_status_to_fbs_status(str_status):
    str_status = str_status.lower()
    if str_status == 'offline':
        return FbsStatus.Status.Offline
    if str_status == 'online':
        return FbsStatus.Status.Online
    if str_status == 'busy':
        return FbsStatus.Status.Busy
    raise Exception('unknown status {}'.format(str_status))


def _build_statuses_fbs_item(builder, status):
    park_id = builder.CreateString(status['park_id'])
    driver_id = builder.CreateString(status['driver_id'])
    fbs_status = _str_status_to_fbs_status(status['status'])
    FbsDriverStatusesItem.ItemStart(builder)
    FbsDriverStatusesItem.ItemAddParkId(builder, park_id)
    FbsDriverStatusesItem.ItemAddDriverId(builder, driver_id)
    FbsDriverStatusesItem.ItemAddStatus(builder, fbs_status)
    FbsDriverStatusesItem.ItemAddUpdatedTs(builder, status['updated_ts'])
    return FbsDriverStatusesItem.ItemEnd(builder)


def load_drv_statuses_mock(load_json, filename):
    data = load_json(filename)
    data['revision'] = _replace_ts(data['revision'])
    for status in data['statuses']:
        if isinstance(status['updated_ts'], str):
            status['updated_ts'] = _replace_ts(status['updated_ts'])
    return data


def build_statuses_fbs(revision, statuses):
    builder = flatbuffers.Builder(initialSize=1024)
    statuses_fb = []
    for item in statuses:
        statuses_fb.append(_build_statuses_fbs_item(builder, item))
    FbsDriverStatusesList.ListStartItemsVector(builder, len(statuses_fb))
    for status_fb in statuses_fb:
        builder.PrependUOffsetTRelative(status_fb)
    items = builder.EndVector(len(statuses_fb))
    FbsDriverStatusesList.ListStart(builder)
    FbsDriverStatusesList.ListAddRevision(builder, revision)
    FbsDriverStatusesList.ListAddItems(builder, items)
    statuses_list = FbsDriverStatusesList.ListEnd(builder)
    builder.Finish(statuses_list)
    return gzip.compress(builder.Output())
