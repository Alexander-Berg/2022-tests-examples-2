# pylint: disable=import-error

import typing as tp

from lxml import etree
import pytest

S3MOCKHANDLE = '/heatmap-mds-s3'
VERSION_PREFIX = 'AFDB'  # some hex-like value


@pytest.fixture(name='s3_heatmap_storage', autouse=True)
def _s3_heatmap_storage(mockserver):
    S3MapData = tp.NamedTuple(
        'S3MapData',
        [
            ('content_key', str),
            ('s3version', str),
            ('created', tp.Optional[str]),
            ('expires', tp.Optional[str]),
            ('map_type', tp.Optional[str]),
            ('map_data', bytes),
        ],
    )

    class StorageContext:
        def __init__(self):
            self.actual_versions = {}
            self.maps = {}
            self.next_version = 0

            # mock handler need for example for times_called
            self.handler = None

        def add_map(
                self,
                content_key: str,
                s3version: str,
                created: tp.Optional[str],
                expires: tp.Optional[str],
                map_type: tp.Optional[str],
                map_data: tp.Union[bytes, bytearray],
        ):
            # old code bugs search
            assert isinstance(map_data, (bytes, bytearray))

            if content_key not in self.maps:
                self.maps[content_key] = {}

            self.maps[content_key][s3version] = S3MapData(
                content_key, s3version, created, expires, map_type, map_data,
            )

            self.actual_versions[content_key] = s3version

        def put_map_by_id(
                self,
                map_id: str,
                created: tp.Optional[str],
                expires: tp.Optional[str],
                map_type: tp.Optional[str],
                map_data: bytes,
        ):
            content_key, s3version = map_id.split(':', 2)
            self.add_map(
                content_key, s3version, created, expires, map_type, map_data,
            )

        def put_map(
                self, content_key, created, expires, map_type, map_data=None,
        ):
            version = f'{VERSION_PREFIX}{self.next_version}'
            self.next_version += 1
            self.add_map(
                content_key, version, created, expires, map_type, map_data,
            )

        def get_map(self, map_id):
            content_key, s3version = map_id.split(':', 2)
            if (
                    content_key in self.maps
                    and s3version in self.maps[content_key]
            ):
                return self.maps[content_key][s3version]

            return None

        def get_actual_map(self, content_key):
            s3version = self.actual_versions.get(content_key)
            return (
                self.maps[content_key][s3version]
                if s3version is not None
                else None
            )

        def get_content_keys(self):
            return self.maps.keys()

    context = StorageContext()

    def list_objects(request):
        assert request.method == 'GET'

        # list objects
        assert request.path[len(f'{S3MOCKHANDLE}/') :] == ''

        max_keys = int(request.query.get('max_keys', '1000'))
        assert max_keys <= 1000

        prefix = request.query.get('prefix', '')
        marker = request.query.get('marker', '')

        keys = [
            key
            for key in context.get_content_keys()
            if key.startswith(prefix) and key > marker
        ]

        result = etree.Element('ListBucketResult')

        is_truncated = etree.Element('IsTruncated')
        is_truncated.text = 'false'
        result.append(is_truncated)

        marker_elem = etree.Element('Marker')
        marker_elem.text = marker
        result.append(marker_elem)

        max_keys_elem = etree.Element('MaxKeys')
        max_keys_elem.text = str(max_keys)
        result.append(max_keys_elem)

        name = etree.Element('Name')
        name.text = 'heatmap'
        result.append(name)

        for key in keys:
            contents = etree.Element('Contents')

            key_elem = etree.Element('Key')
            key_elem.text = key
            contents.append(key_elem)

            # s3api library reads Size
            size_elem = etree.Element('Size')
            size_elem.text = '1'
            contents.append(size_elem)

            result.append(contents)

        return mockserver.make_response(
            response=etree.tostring(
                result, xml_declaration=True, encoding='UTF-8',
            ),
            status=200,
        )

    def get(request):
        assert request.method == 'GET' or request.method == 'HEAD'
        content_key = request.path[len(f'{S3MOCKHANDLE}/') :]

        if 'versionId' in request.query:
            current_map = context.get_map(
                f'{content_key}:{request.query["versionId"]}',
            )
        else:
            current_map = context.get_actual_map(content_key)

        if current_map is None:
            return mockserver.make_response('Not found', 404)

        body = ''
        if request.method == 'GET':
            body = current_map.map_data

        return mockserver.make_response(
            response=body,
            status=200,
            headers={
                'X-Amz-Meta-Heatmapcompression': 'none',
                'X-Amz-Meta-Heatmaptype': current_map.map_type,
                'X-Amz-Meta-Created': current_map.created,
                'X-Amz-Meta-Expires': current_map.expires,
                'X-Amz-Version-Id': current_map.s3version,
            },
        )

    def put(request):
        assert request.method == 'PUT'
        map_data = request.get_data()
        content_key = request.path[len(f'{S3MOCKHANDLE}/') :]

        map_type = request.headers['X-Amz-Meta-Heatmaptype']
        created = request.headers['X-Amz-Meta-Created']
        expires = request.headers['X-Amz-Meta-Expires']

        context.put_map(content_key, created, expires, map_type, map_data)
        return mockserver.make_response('OK', 200)

    @mockserver.handler(S3MOCKHANDLE, prefix=True)
    def _mock_request_s3(request):
        if request.method == 'GET' or request.method == 'HEAD':
            if request.path == f'{S3MOCKHANDLE}/':
                return list_objects(request)

            return get(request)

        if request.method == 'PUT':
            return put(request)

        return mockserver.make_response('No suitable handler', 500)

    context.handler = _mock_request_s3

    return context
