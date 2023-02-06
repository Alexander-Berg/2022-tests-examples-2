# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import collections
import datetime
import gzip

import flatbuffers
import lz4
import pytest

from driver_status.fbs.v2.statuses import Item as FbsDriverStatusesItem
from driver_status.fbs.v2.statuses import List as FbsDriverStatusesList
from driver_status.fbs.v2.statuses import Status as FbsStatus
from logistic_supply_conductor_plugins import *  # noqa: F403 F401

COMPRESSION_METHOD = {
    'none': lambda x: x,
    'gzip': gzip.compress,
    'lz4': lambda x: lz4.dumps(bytes(x)),
}


@pytest.fixture(name='tags')
def _tags(mockserver):
    class Context:
        def __init__(self):
            self.append = None
            self.remove = None

        def set_tags(self, append, remove):
            self.append = collections.Counter(append)
            self.remove = collections.Counter(remove)

    context = Context()

    @mockserver.json_handler('/tags/v2/upload')
    def _tags_upload(request):
        if 'append' in request.json:
            actual_append = [
                x['name'] for x in request.json['append'][0]['tags']
            ]
        else:
            actual_append = None
        assert context.append == collections.Counter(actual_append)

        if 'remove' in request.json:
            actual_remove = [
                x['name'] for x in request.json['remove'][0]['tags']
            ]
        else:
            actual_remove = None
        assert context.remove == collections.Counter(actual_remove)

        context.set_tags({}, {})

        return {}

    return context


@pytest.fixture(name='driver_status')
def driver_status(mockserver):
    @mockserver.json_handler('/driver-status/v2/status/store')
    def _mock_driver_status(request):
        return {'status': request.json['status'], 'updated_ts': 42}


@pytest.fixture(name='contractor_profession')
def contractor_profession(mockserver):
    @mockserver.json_handler(
        '/contractor-profession/internal/v1/professions/get/active/bulk',
    )
    def _mock_contractor_profession(request):
        contractor_profile_id = request.json['contractors'][0][
            'contractor_profile_id'
        ]
        return {
            'contractors': [
                {
                    'contractor': {
                        'contractor_profile_id': contractor_profile_id,
                        'park_id': 'sample',
                    },
                    'profession': {'id': 'fisher', 'groups': []},
                },
            ],
        }


@pytest.fixture(autouse=True)
def driver_status_request(mockserver, load_json):
    @mockserver.handler('/driver-status/v2/statuses/updates')
    def _mock_driver_statuses(request):
        def _get_current_timestamp(minus_hours=None):
            required_time = datetime.datetime.now()
            if minus_hours is not None:
                required_time = required_time - datetime.timedelta(
                    hours=minus_hours,
                )
            return int((required_time.timestamp() * 1e6))

        def _replace_ts(timestamp):
            prefix = 'now_minus_'
            if isinstance(timestamp, str) and timestamp.startswith(prefix):
                minus_hours = timestamp[len(prefix) :]
                if minus_hours.isdecimal():
                    return _get_current_timestamp(int(minus_hours))
            return timestamp

        def load_drv_statuses_mock(load_json, filename):
            data = load_json(filename)
            data['revision'] = _replace_ts(data['revision'])
            for status in data['statuses']:
                if isinstance(status['updated_ts'], str):
                    status['updated_ts'] = _replace_ts(status['updated_ts'])
            return data

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
            FbsDriverStatusesItem.ItemAddUpdatedTs(
                builder, status['updated_ts'],
            )
            return FbsDriverStatusesItem.ItemEnd(builder)

        def build_statuses_fbs(revision, statuses, compression):
            builder = flatbuffers.Builder(initialSize=1024)
            statuses_fb = []
            for item in statuses:
                statuses_fb.append(_build_statuses_fbs_item(builder, item))
            FbsDriverStatusesList.ListStartItemsVector(
                builder, len(statuses_fb),
            )
            for status_fb in statuses_fb:
                builder.PrependUOffsetTRelative(status_fb)
            items = builder.EndVector(len(statuses_fb))
            FbsDriverStatusesList.ListStart(builder)
            FbsDriverStatusesList.ListAddRevision(builder, revision)
            FbsDriverStatusesList.ListAddItems(builder, items)
            statuses_list = FbsDriverStatusesList.ListEnd(builder)
            builder.Finish(statuses_list)
            return COMPRESSION_METHOD.get(compression, gzip)(builder.Output())

        statuses = load_drv_statuses_mock(
            load_json, 'driver_status_statuses_response.json',
        )
        result = build_statuses_fbs(
            statuses['revision'],
            statuses['statuses'],
            request.query.get('compression', 'gzip'),
        )
        return mockserver.make_response(
            response=result,
            headers={'Content-Type': 'application/x-flatbuffers'},
            status=200,
        )


@pytest.fixture(name='client_events')
def client_events(mockserver):
    @mockserver.json_handler('/client-events/push')
    def push(request):
        return {'version': '1.1234'}

    return push
