import hashlib
import json
import pathlib

import pytest

Path = pathlib.Path


@pytest.fixture(autouse=True)
def mds_avatarnica(mockserver, request):
    if request.node.get_closest_marker('no_mds_avatarnica'):
        return

    path_prefix = '/avatars-mds/put-eda/'

    @mockserver.handler(path_prefix, prefix=True)
    def _mock_ava(request):
        if request.method != 'POST':
            return mockserver.make_response('Not found or invalid method', 404)

        md5 = hashlib.md5(request.get_data()).hexdigest()
        # remove extension from filename
        image_id = str(Path(request.path[len(path_prefix) :]).stem)
        group_id = ord(md5[0]) * 10 + ord(md5[1])

        response = {
            'imagename': image_id,
            'group-id': group_id,
            'meta': {'orig-format': 'JPEG'},
            'sizes': {
                'orig': {
                    'height': 640,
                    'path': f'/get-eda/{group_id}/{image_id}/orig',
                    'width': 1024,
                },
                'sizename': {
                    'height': 200,
                    'path': f'/get-eda/{group_id}/{image_id}/sizename',
                    'width': 200,
                },
            },
        }

        return mockserver.make_response(json.dumps(response), 200)


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'no_mds_avatarnica: disable mds_avatarnica mocking.',
    )
