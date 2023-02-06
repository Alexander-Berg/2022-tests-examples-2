import typing

import pytest

SANDBOX_FIRE_TASK_ID = 1129082489
SANDBOX_UPLOAD_TASK_ID = 1181322916
LUNAPARK_ID = 123321
LUNAPARK_MESSAGE = """Load start successfully.
To check the result visit: https://lunapark.yandex-team.ru/123321"""
AMMO_LINK = 'https://proxy.sandbox.yandex-team.ru/2693572988'
FULL_TANK_CONFIG = """metaconf:
    package: yandextank.plugins.MetaConf
    firestarter:
        tank: 'nanny:production_yandex_tank'
    enabled: true
phantom:
    address: 'qqbyrftajycoh7q2.vla.yp-c.yandex.net'
    ammofile: '{ammofile}'
    load_profile:
        load_type: rps
        schedule: 'line(1,2,3)'
    uris: []
uploader:
    enabled: true
    job_dsc: 'custom-description'
    job_name: 'custom-title'
    operator: dyusudakov
    package: yandextank.plugins.DataUploader
    task: TAXICOMMON-123
"""

TANK_CONFIG = """metaconf:
    package: yandextank.plugins.MetaConf
    firestarter:
        tank: 'nanny:production_yandex_tank'
    enabled: true
phantom:
    address: 'qqbyrftajycoh7q2.vla.yp-c.yandex.net'
    ammofile: '{ammofile}'
    load_profile:
        load_type: rps
        schedule: 'line(1,2,3)'
    uris: []
uploader:
    enabled: true
    job_dsc: 'auto-fire empty description'
    job_name: 'auto-fire'
    operator: dyusudakov
    package: yandextank.plugins.DataUploader
    task: TAXICOMMON-123
"""

AMMO_FILE = """147GET /ping HTTP/1.1
Host: qqbyrftajycoh7q2.vla.yp-c.yandex.net
User-Agent: tank
Accept: */*
Content-length: 7
Connection: keep-alive

{"a":1}"""


@pytest.fixture(name='sandbox_mockserver')
def _snadbox_mocks(mockserver, mock_sandbox_py3):
    def _wrapper(task_status: str = 'SUCCESS'):
        # Dict from 'mock-name' to list of requests
        requests: typing.Dict[str, typing.List[typing.Dict]] = {}

        def _add_request_data(name: str, request):
            if name not in requests:
                requests[name] = []

            requests[name].append(request)

        @mock_sandbox_py3('/api/v1.0/task')
        def _create_task(request):
            _add_request_data('create_task_mock', request)

            req_data = request.json
            assert req_data['owner'] == 'ROBOT_TAXI_SANDLOAD'
            assert request.headers['Authorization'] == 'OAuth sandbox_api_key'
            task_id = 0

            if req_data['type'] == 'FIRESTARTER':
                assert req_data['custom_fields'] == [
                    {'name': 'dry_run', 'value': False},
                    {
                        'name': 'tank_config',
                        'value': TANK_CONFIG.format(ammofile=AMMO_LINK),
                    },
                    {'name': 'monitoring_config', 'value': ''},
                    {'name': 'use_last_binary', 'value': True},
                ]
                task_id = SANDBOX_FIRE_TASK_ID
            elif req_data['type'] == 'CREATE_TEXT_RESOURCE':
                assert req_data['custom_fields'] == [
                    {'name': 'resource_type', 'value': 'AMMO_FILE'},
                    {'name': 'resource_arch', 'value': 'any'},
                    {
                        'name': 'created_resource_name',
                        'value': 'auto-uploaded-ammo',
                    },
                    {'name': 'resource_file_content', 'value': AMMO_FILE},
                    {'name': 'store_forever', 'value': False},
                    {'name': 'resource_attrs', 'value': ''},
                ]
                task_id = SANDBOX_UPLOAD_TASK_ID

            return mockserver.make_response(
                status=201, json={'id': task_id}, headers={'Location': 'ru'},
            )

        @mock_sandbox_py3('/api/v1.0/batch/tasks/start')
        def _start_task(request):
            _add_request_data('start_task_mock', request)

            assert request.headers['Authorization'] == 'OAuth sandbox_api_key'

            return mockserver.make_response(
                status=200,
                json=[
                    {
                        'id': request.json['id'][0],
                        'status': task_status,
                        'message': 'just text',
                    },
                ],
            )

        @mock_sandbox_py3('/api/v1.0/task/{}'.format(SANDBOX_FIRE_TASK_ID))
        def _check_fire_task(request):
            _add_request_data('check_fire_task_mock', request)

            assert request.headers['Authorization'] == 'OAuth sandbox_api_key'

            return mockserver.make_response(
                status=200,
                json={
                    'id': SANDBOX_FIRE_TASK_ID,
                    'status': task_status,
                    'output_parameters': {
                        'lunapark_id': (
                            0 if task_status != 'SUCCESS' else LUNAPARK_ID
                        ),
                    },
                },
            )

        @mock_sandbox_py3('/api/v1.0/task/{}'.format(SANDBOX_UPLOAD_TASK_ID))
        def _check_upload_task(request):
            _add_request_data('check_upload_task_mock', request)

            assert request.headers['Authorization'] == 'OAuth sandbox_api_key'

            return mockserver.make_response(
                status=200,
                json={
                    'id': SANDBOX_UPLOAD_TASK_ID,
                    'status': task_status,
                    'output_parameters': {},
                },
            )

        @mock_sandbox_py3('/api/v1.0/resource')
        def _get_resource(request):
            _add_request_data('get_resource_mock', request)

            assert request.headers['Authorization'] == 'OAuth sandbox_api_key'

            return mockserver.make_response(
                status=200,
                json={
                    'items': [
                        {
                            'arch': 'any',
                            'attributes': {},
                            'description': 'custom-description',
                            'executable': False,
                            'file_name': 'test-uploaded_resource',
                            'http': {'links': [], 'proxy': AMMO_LINK},
                            'id': 2693572988,
                            'md5': 'c1d463e053ba580b1289bfc227562920',
                            'mds': None,
                            'multifile': False,
                            'owner': 'ROBOT_TAXI_SANDLOAD',
                            'resource_meta': None,
                            'rights': 'read',
                            'size': 0,
                            'skynet_id': 'rbtorrent:b14c6a917fec5a4ff153d563c',
                            'state': 'READY',
                            'system_attributes': None,
                            'task': {
                                'id': 1181322916,
                                'status': 'SUCCESS',
                                'url': AMMO_LINK,
                            },
                            'time': {
                                'accessed': '2022-01-12T10:24:55.147000Z',
                                'created': '2022-01-12T10:23:54Z',
                                'expires': '2022-01-26T10:24:55.147000Z',
                                'updated': '2022-01-12T10:24:55.161000Z',
                            },
                            'type': 'AMMO_FILE',
                            'url': (
                                'https://sandbox.yandex-team.ru/'
                                'api/v1.0/resource/2693572988'
                            ),
                        },
                    ],
                    'limit': 1,
                    'offset': 0,
                    'total': 1,
                },
            )

        return {
            'create_task_mock': _create_task,
            'start_task_mock': _start_task,
            'check_fire_task_mock': _check_fire_task,
            'check_upload_task_mock': _check_upload_task,
            'get_resource_mock': _get_resource,
            'test_data': {
                'sandbox_fire_task_id': SANDBOX_FIRE_TASK_ID,
                'sandbox_upload_task_id': SANDBOX_UPLOAD_TASK_ID,
                'lunapark_id': LUNAPARK_ID,
                'lunapark_message': LUNAPARK_MESSAGE,
                'ammo_link': AMMO_LINK,
                'full_tank_config': FULL_TANK_CONFIG.format(
                    ammofile=AMMO_LINK,
                ),
                'tank_config': TANK_CONFIG.format(ammofile=AMMO_LINK),
                'ammo_file': AMMO_FILE,
            },
            'requests': requests,
        }

    return _wrapper
