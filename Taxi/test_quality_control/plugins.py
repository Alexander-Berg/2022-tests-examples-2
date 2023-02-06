# pylint: disable=redefined-outer-name
import datetime
import functools
import re
import typing
import uuid

from aiohttp import web
import pytest

from taxi.maintenance import run
from taxi.util import dates

from quality_control import utils
from quality_control.crontasks import current_state
from quality_control.crontasks import lag_metric
from quality_control.crontasks import stale_pass
from quality_control.service import settings


BINARY_IMAGE = b'S\x00t\x00a'


@pytest.fixture
def qc_pools(mockserver):
    class QcPoolsContext:
        def __init__(self):
            self._storage = dict(license=dict(by_number={}, by_id={}))
            self.items = None
            self.resolution = None
            self.empty_push = False
            self.data = None

        def set_items(self, items):
            self.items = items

        def set_misc_data(self, data):
            self.data = data

        def set_resolution(self, resolution):
            self.resolution = resolution

        def set_empty_push(self, empty_push):
            self.empty_push = empty_push

    context = QcPoolsContext()

    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/retrieve')
    async def retrieve(request):
        assert request.method == 'POST'
        if request.json.get('cursor') == 'next':
            return {'cursor': 'empty', 'items': []}
        return {'cursor': 'next', 'items': context.items}

    @mockserver.json_handler('/qc-pools/internal/qc-pools/v1/pool/push')
    async def push(request):
        assert request.method == 'POST'
        if context.empty_push:
            assert not request.json['items']
        else:
            assert request.json['items']
            processed = request.json['items'][0]
            item_data = {
                data['field']: data['value'] for data in processed['data']
            }
            assert item_data['resolution'] == context.resolution
            if context.data:
                for k in context.data:
                    assert item_data.get(k) == context.data[k]
        return {}

    context.retrieve = retrieve  # pylint: disable=W0201
    context.push = push  # pylint: disable=W0201

    return context


@pytest.fixture
def qc_cache():
    cache = settings.QcSettingsCache()
    cache.update(
        {
            'type': 'entity',
            'entity_type': 'driver',
            'groups': [
                {'code': 'park', 'property': 'park_id'},
                {'code': 'city', 'property': 'city'},
            ],
            'exams': [
                {
                    'code': 'dkvu',
                    'media': {
                        'items': [
                            {
                                'code': 'front',
                                'type': 'photo',
                                'settings': 'settings',
                                'storage_settings': {
                                    'type': 'media_storage',
                                    'bucket': 'driver-license',
                                },
                            },
                            {
                                'code': 'back',
                                'type': 'photo',
                                'settings': 'settings',
                            },
                            {
                                'code': 'selfie',
                                'type': 'photo',
                                'settings': 'settings',
                            },
                        ],
                        'stale': '1d',
                        'url_expire': '5m',
                        'default': ['front', 'back'],
                    },
                    'block': {
                        'sanctions': ['orders_off'],
                        'release': 'after_resolve',
                    },
                    'pass': {
                        'stale': '2h',
                        'filter': [{'field': 'test_2'}],
                        'data': [
                            dict(field='license_pd_id', editable=True),
                            dict(field='name', editable=False),
                        ],
                    },
                },
                {
                    'code': 'vaccination',
                    'media': {
                        'items': [
                            {
                                'code': 'front',
                                'type': 'photo',
                                'settings': 'settings',
                            },
                            {
                                'code': 'back',
                                'type': 'photo',
                                'settings': 'settings',
                            },
                        ],
                        'stale': '1d',
                        'url_expire': '5m',
                        'default': ['front', 'back'],
                    },
                    'block': {
                        'sanctions': ['orders_off'],
                        'release': 'after_resolve',
                    },
                    'pass': {'stale': '2h'},
                },
                {
                    'code': 'dkk',
                    'media': {
                        'items': [
                            {
                                'code': 'front',
                                'type': 'photo',
                                'settings': 'settings',
                            },
                        ],
                        'stale': '1d',
                        'url_expire': '5m',
                        'default': ['front'],
                    },
                    'block': {
                        'sanctions': ['orders_off'],
                        'release': 'after_pass',
                    },
                    'pass': {'stale': '4h'},
                    'future': [
                        {'begin': '1d', 'can_pass': True},
                        {
                            'begin': '1h',
                            'can_pass': True,
                            'sanctions': ['orders_off'],
                        },
                    ],
                },
                {
                    'code': 'identity',
                    'media': {
                        'items': [
                            {
                                'code': 'selfie',
                                'type': 'photo',
                                'settings': 'settings',
                                'storage_settings': {
                                    'type': 'media_storage',
                                    'bucket': 'driver-photo',
                                },
                            },
                            {
                                'code': 'title',
                                'type': 'photo',
                                'settings': 'settings',
                                'storage_settings': {
                                    'type': 'media_storage',
                                    'bucket': 'identity-card',
                                },
                            },
                            {
                                'code': 'visa',
                                'type': 'photo',
                                'settings': 'settings',
                            },
                        ],
                        'stale': '1d',
                        'url_expire': '5m',
                        'default': ['selfie', 'title', 'visa'],
                    },
                    'block': {
                        'sanctions': ['orders_off'],
                        'release': 'after_pass',
                    },
                    'pass': {'stale': '4h'},
                    'future': [
                        {'begin': '1d', 'can_pass': True},
                        {
                            'begin': '1h',
                            'can_pass': True,
                            'sanctions': ['orders_off'],
                        },
                    ],
                },
            ],
        },
    )
    cache.update(
        {
            'type': 'entity',
            'entity_type': 'car',
            'groups': [],
            'exams': [
                {
                    'code': 'car_exam',
                    'media': {
                        'items': [{'code': 'front', 'type': 'photo'}],
                        'stale': '1d',
                        'url_expire': '5m',
                        'default': ['front'],
                    },
                    'block': {
                        'sanctions': ['orders_off'],
                        'release': 'after_pass',
                    },
                    'pass': {'stale': '4h'},
                    'future': [
                        {'begin': '1d', 'can_pass': True},
                        {
                            'begin': '1h',
                            'can_pass': True,
                            'sanctions': ['orders_off'],
                        },
                    ],
                },
            ],
        },
    )
    cache.build(None)
    return cache


@pytest.fixture
def qc_app(web_app, qc_cache, mds_s3_client):
    web_app.mds_client = mds_s3_client
    web_app[settings.QC_CACHE_KEY] = qc_cache
    return web_app


@pytest.fixture
def qc_context(qc_app):
    class FakeRequest(dict):
        raw_path = None
        path = None

    request = FakeRequest()
    context = utils.Context(request, qc_app)
    return context


@pytest.fixture
def qc_client(aiohttp_client, qc_app, loop):
    return loop.run_until_complete(aiohttp_client(qc_app))


def do_stuff(qc_app, func, **kwargs):
    context = run.StuffContext(
        lock=None,
        task_id='',
        start_time=datetime.datetime.utcnow(),
        data=qc_app,
        args=kwargs,
    )
    return func(context, loop=None, log_extra=None)


@pytest.fixture
def task_current_state(qc_app):
    return functools.partial(do_stuff, qc_app, current_state.do_stuff)


@pytest.fixture
def task_stale_pass(qc_app):
    return functools.partial(do_stuff, qc_app, stale_pass.do_stuff)


@pytest.fixture
def task_lag_metrics(qc_app):
    return functools.partial(do_stuff, qc_app, lag_metric.do_stuff)


class FakeMediaStorageContext:
    def __init__(self):
        self._storage = {}
        self._etags = {}

    def get_size(self, bucket):
        return len(self._storage.get(bucket, {}))

    def get_objects(self, bucket):
        return list(self._storage.get(bucket, {}).keys())

    def put_object(self, bucket, etag, body):
        self._storage.setdefault(bucket, {})
        self._storage[bucket][etag] = bytearray(body)

    def get_object(self, bucket, etag) -> bytearray:
        return self._storage.get(bucket, {}).get(etag)

    def delete_object(self, bucket, etag) -> typing.Optional[bytearray]:
        return self._storage.get(bucket, {}).pop(etag, None)

    def get_etag(self, media_id):
        return self._etags.get(media_id)

    def set_etag(self, media_id, etag):
        self._etags[media_id] = etag


@pytest.fixture
def media_storage(mockserver):
    context = FakeMediaStorageContext()

    @mockserver.handler('/media-storage', prefix=True)
    def _handler(request):
        result = re.search(
            r'service/(?P<bucket>\S*)/v1/(?P<method>\S*)', request.path,
        )
        bucket = result.group('bucket')
        method = result.group('method')

        media_id = request.query.get('id', uuid.uuid4().hex)
        version = request.query.get('version')
        current_version = context.get_etag(media_id)
        if method == 'store':
            if version != current_version:
                return mockserver.make_response(
                    status=409, json=dict(code='Conflict', message='message'),
                )
            version = version or uuid.uuid4().hex
            context.set_etag(media_id, version)
            context.put_object(bucket, version, request.get_data())
            return mockserver.make_response(
                json=dict(id=media_id, version=version),
            )
        if method == 'retrieve':
            version = version or current_version
            if not context.get_object(bucket, version):
                return mockserver.make_response(
                    status=404, json=dict(code='NotFound', message='message'),
                )
            now = datetime.datetime.utcnow()
            return mockserver.make_response(
                json=dict(
                    url='http://s3.mdst.yandex.net/media-storage/'
                    f'{bucket}/{version}',
                    version=version,
                    expired_at=dates.timestring(
                        now + datetime.timedelta(minutes=15),
                    ),
                ),
            )
        if method == 'delete':
            version = version or current_version
            if not context.delete_object(bucket, version):
                return mockserver.make_response(
                    status=404, json=dict(code='NotFound', message='message'),
                )
            return mockserver.make_response(json=dict(deleted=1))

        if method == 'avatars':
            version = version or current_version
            if not context.get_object(bucket, version):
                return mockserver.make_response(
                    status=404, json=dict(code='NotFound', message='message'),
                )
            now = datetime.datetime.utcnow()
            return mockserver.make_response(
                json=dict(
                    imagename='imagename',
                    avatar_id=123,
                    version=version,
                    expired_at=dates.timestring(
                        now + datetime.timedelta(minutes=15),
                    ),
                ),
            )

        return mockserver.make_response(
            status=404, json=dict(code='NotFound', message='message'),
        )

    return context


@pytest.fixture
def mongodb_settings(mongodb_settings):
    mongodb_settings['mqc_confirmations']['settings']['database'] = 'mqc'
    mongodb_settings['mqc_entities']['settings']['database'] = 'mqc'
    mongodb_settings['mqc_jobs_data']['settings']['database'] = 'mqc'
    mongodb_settings['mqc_notifications']['settings']['database'] = 'mqc'
    mongodb_settings['mqc_passes']['settings']['database'] = 'mqc'
    mongodb_settings['mqc_settings']['settings']['database'] = 'mqc'
    return mongodb_settings


@pytest.fixture
def avatars_mds(mockserver):
    namespace = 'media-storage'

    @mockserver.json_handler(
        fr'/avatars-mds/genurlsign-{namespace}/(?P<group_id>\w+)/'
        r'(?P<image_name>\w+)/(?P<sizename>\w+)',
        regex=True,
    )
    def _mock_genurlsign(request, group_id, image_name, sizename):
        sign = 'randomsign'
        expire_at_ts = '123'
        return mockserver.make_response(
            json=dict(
                path=f'/get-{namespace}/{group_id}/{image_name}/{sizename}/'
                f'?dynamic-watermark={request.query["dynamic-watermark"]}'
                f'&ts={expire_at_ts}&sign={sign}',
                sign=sign,
                ts=expire_at_ts,
            ),
        )

    @mockserver.json_handler(
        fr'/get-{namespace}/(?P<group_id>\w+)/(?P<image_name>\w+)/'
        r'(?P<sizename>\w+)/?dynamic-watermark=(?P<dynamic_watermark>\w+)'
        r'&sign=(?P<sign>\w+)',
        regex=True,
    )
    def _mock_get(request):
        return web.json_response(
            text=BINARY_IMAGE, headers={'Content-Type': 'image/*'}, status=200,
        )
