# pylint: disable=wildcard-import, import-error
import datetime
import gzip

import flatbuffers
import lz4

# pylint: disable=no-name-in-module
from driver_status.fbs.v2.blocks import Item as FbsDriverBlocksItem
from driver_status.fbs.v2.blocks import List as FbsDriverBlocksList
from driver_status.fbs.v2.orders import Item as FbsDriverOrdersItem
from driver_status.fbs.v2.orders import List as FbsDriverOrdersList
from driver_status.fbs.v2.orders import Status as FbsOrderStatus
from driver_status.fbs.v2.statuses import Item as FbsDriverStatusesItem
from driver_status.fbs.v2.statuses import List as FbsDriverStatusesList
from driver_status.fbs.v2.statuses import Status as FbsStatus

COMPRESSION_METHOD = {
    'none': lambda x: x,
    'gzip': gzip.compress,
    'lz4': lambda x: lz4.dumps(bytes(x)),
}


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


def _build_blocks_fbs_item(builder, block):
    park_id = builder.CreateString(block['park_id'])
    driver_id = builder.CreateString(block['driver_id'])
    block_reason = builder.CreateString(block['reason'])
    FbsDriverBlocksItem.ItemStart(builder)
    FbsDriverBlocksItem.ItemAddParkId(builder, park_id)
    FbsDriverBlocksItem.ItemAddDriverId(builder, driver_id)
    FbsDriverBlocksItem.ItemAddReason(builder, block_reason)
    FbsDriverBlocksItem.ItemAddUpdatedTs(builder, block['updated_ts'])
    return FbsDriverBlocksItem.ItemEnd(builder)


def _str_order_status_to_fbs_status(str_status):
    str_status = str_status.lower()
    if str_status == 'none':
        return FbsOrderStatus.Status.None_
    if str_status == 'driving':
        return FbsOrderStatus.Status.Driving
    if str_status == 'waiting':
        return FbsOrderStatus.Status.Waiting
    if str_status == 'calling':
        return FbsOrderStatus.Status.Calling
    if str_status == 'trasporting':
        return FbsOrderStatus.Status.Transporting
    if str_status == 'complete':
        return FbsOrderStatus.Status.Complete
    if str_status == 'failed':
        return FbsOrderStatus.Status.Failed
    if str_status == 'cancelled':
        return FbsOrderStatus.Status.Cancelled
    if str_status == 'expired':
        return FbsOrderStatus.Status.Expired
    raise Exception('unknown status {}'.format(str_status))


def _build_orders_fbs_item(builder, order):
    park_id = builder.CreateString(order['park_id'])
    driver_id = builder.CreateString(order['driver_id'])
    order_id = builder.CreateString(order['order_id'])
    order_provider = builder.CreateString(order['provider'])
    order_status = _str_order_status_to_fbs_status(order['status'])
    FbsDriverOrdersItem.ItemStart(builder)
    FbsDriverOrdersItem.ItemAddDriverId(builder, driver_id)
    FbsDriverOrdersItem.ItemAddParkId(builder, park_id)
    FbsDriverOrdersItem.ItemAddOrderId(builder, order_id)
    FbsDriverOrdersItem.ItemAddStatus(builder, order_status)
    FbsDriverOrdersItem.ItemAddProvider(builder, order_provider)
    FbsDriverOrdersItem.ItemAddUpdatedTs(builder, order['updated_ts'])
    return FbsDriverBlocksItem.ItemEnd(builder)


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


def load_statuses_mock(load_json, filename):
    statuses = load_json(filename)
    statuses['revision'] = _replace_ts(statuses['revision'])
    for status in statuses['response']:
        status['status_updated_ts'] = _replace_ts(status['status_updated_ts'])
        status['updated_ts'] = _replace_ts(status['updated_ts'])
    return statuses


def load_blocks_mock(load_json, filename):
    blocks = load_json(filename)
    blocks['revision'] = _replace_ts(blocks['revision'])
    for block in blocks['blocks']:
        if isinstance(block['updated_ts'], str):
            block['updated_ts'] = _replace_ts(block['updated_ts'])
    return blocks


def load_drv_orders_mock(load_json, filename):
    data = load_json(filename)
    data['revision'] = _replace_ts(data['revision'])
    for order in data['orders']:
        if isinstance(order['updated_ts'], str):
            order['updated_ts'] = _replace_ts(order['updated_ts'])
    return data


def load_drv_statuses_mock(load_json, filename):
    data = load_json(filename)
    data['revision'] = _replace_ts(data['revision'])
    for status in data['statuses']:
        if isinstance(status['updated_ts'], str):
            status['updated_ts'] = _replace_ts(status['updated_ts'])
    return data


def load_drv_onlycard_mock(load_json, filename):
    data = load_json(filename)
    data['revision'] = _replace_ts(data['revision'])
    return data


def build_blocks_fbs(revision, blocks, compression):
    builder = flatbuffers.Builder(initialSize=1024)
    blocks_fb = []
    for item in blocks:
        blocks_fb.append(_build_blocks_fbs_item(builder, item))
    FbsDriverBlocksList.ListStartItemVector(builder, len(blocks_fb))
    for block_fb in blocks_fb:
        builder.PrependUOffsetTRelative(block_fb)
    items = builder.EndVector(len(blocks_fb))
    FbsDriverBlocksList.ListStart(builder)
    FbsDriverBlocksList.ListAddRevision(builder, revision)
    FbsDriverBlocksList.ListAddItem(builder, items)
    blocks_list = FbsDriverBlocksList.ListEnd(builder)
    builder.Finish(blocks_list)
    return COMPRESSION_METHOD.get(compression, gzip)(builder.Output())


def build_orders_fbs(revision, orders, compression):
    builder = flatbuffers.Builder(initialSize=1024)
    orders_fb = []
    for item in orders:
        orders_fb.append(_build_orders_fbs_item(builder, item))
    FbsDriverOrdersList.ListStartItemsVector(builder, len(orders_fb))
    for order_fb in orders_fb:
        builder.PrependUOffsetTRelative(order_fb)
    items = builder.EndVector(len(orders_fb))
    FbsDriverOrdersList.ListStart(builder)
    FbsDriverOrdersList.ListAddRevision(builder, revision)
    FbsDriverOrdersList.ListAddItems(builder, items)
    orders_list = FbsDriverOrdersList.ListEnd(builder)
    builder.Finish(orders_list)
    return COMPRESSION_METHOD.get(compression, gzip)(builder.Output())


def build_statuses_fbs(revision, statuses, compression):
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
    return COMPRESSION_METHOD.get(compression, gzip)(builder.Output())
