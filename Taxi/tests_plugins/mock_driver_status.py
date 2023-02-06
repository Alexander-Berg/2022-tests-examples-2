import gzip

import flatbuffers
import lz4
import pytest

from fbs.driver_status.fbs.v2.statuses import Item as FbsDriverStatusesItem
from fbs.driver_status.fbs.v2.statuses import List as FbsDriverStatusesList
from fbs.driver_status.fbs.v2.statuses import Status as FbsStatus


COMPRESSION_METHOD = {
    'none': lambda x: x,
    'gzip': gzip.compress,
    'lz4': lambda x: lz4.dumps(bytes(x)),
}


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
    return COMPRESSION_METHOD.get(compression, 'gzip')(builder.Output())


@pytest.fixture(autouse=True)
def driver_status_services(request, mockserver):
    marker = request.node.get_marker('driver_status')

    @mockserver.handler('/driver-status/v2/statuses/updates')
    def _handle_statuses_updates(request):

        query = dict(
            map(
                lambda x: x.split('='),
                request.query_string.decode().split('&'),
            ),
        )

        statuses_mock = {'revision': 0, 'statuses': []}
        if marker:
            statuses_mock = marker.kwargs.get('statuses_mock')
        result = build_statuses_fbs(
            statuses_mock['revision'],
            statuses_mock['statuses'],
            query.get('compression', 'gzip'),
        )
        return mockserver.make_response(
            response=result,
            headers={'Content-Type': 'application/x-flatbuffers'},
            status=200,
        )
