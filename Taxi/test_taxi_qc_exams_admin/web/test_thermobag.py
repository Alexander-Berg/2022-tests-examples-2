from aiohttp import web
import pytest

from taxi import discovery

from taxi_qc_exams_admin.helpers import consts
from test_taxi_qc_exams_admin import utils


HEADERS = {'Content-Type': 'application/json'}


@pytest.mark.config(
    QC_EXAMS_ADMIN_UPDATE_DRIVERS_FIELDS=[
        'delivery.thermobag',
        'delivery.thermopack',
    ],
    QC_EXAMS_ADMIN_UPDATE_EXAMS=['thermobag'],
    QC_EXAMS_ADMIN_UPDATE_EXAMS_FIELDS={
        'thermobag': ['delivery.thermobag', 'delivery.thermopack'],
    },
)
@pytest.mark.parametrize(
    'driver, media',
    [
        ('driver2', ['thermobag']),
        ('driver3', ['thermopack']),
        ('driver4', ['thermobag', 'thermopack']),
    ],
)
async def test_enable(
        web_app_client,
        mock_quality_control_py3,
        mock_tags,
        patch_aiohttp_session,
        response_mock,
        driver,
        media,
):
    entity_id = f'park_{driver}'

    @patch_aiohttp_session(discovery.find_service('taximeter_xservice').url)
    def _patch_update_drivers(method, url, json, **kwargs):
        return response_mock(
            json=dict(processed=[dict(park_id='park', driver_id=driver)]),
        )

    @mock_quality_control_py3('/api/v1/data/bulk_retrieve')
    def _mock_bulk_retrieve(request):
        return web.json_response(
            dict(
                items=[
                    dict(
                        id=entity_id,
                        type='driver',
                        data=dict(park_id='park'),
                        modified='2019-04-20T12:00:00Z',
                    ),
                ],
            ),
        )

    @mock_quality_control_py3('/api/v1/data/list')
    def _mock_data_list(request):
        assert request.method.lower() == 'post'
        assert request.query == dict(type='driver')
        return web.json_response({})

    @mock_quality_control_py3('/api/v1/state/bulk_retrieve')
    def _mock_state_bulk_retrieve(request):
        assert request.method.lower() == 'post'
        return web.json_response(
            dict(items=[dict(id=entity_id, type='driver', exams=[])]),
        )

    @mock_quality_control_py3('/api/v1/state/list')
    def mock_state_list(request):
        assert request.method.lower() == 'post'
        return web.json_response({})

    @mock_tags('/v1/upload')
    def v1_upload(request):
        return web.json_response({})

    items = [dict(park_id='park', driver_id=driver)]
    response = await web_app_client.post(
        'v1/update/drivers', json=dict(items=items), headers=HEADERS,
    )

    assert response.status == 200
    response_data = await response.json()

    assert response_data.pop('modified', []) == items
    assert response_data == dict()

    assert mock_state_list.times_called == 1

    states_update = mock_state_list.next_call()['request'].json
    # remove generated log identificator
    for x in states_update:
        del x['identity']['script']['id']

    assert sorted(states_update, key=lambda k: k['id']) == sorted(
        [
            {
                'enabled': True,
                'present': dict(can_pass=True, sanctions=['thermobag_off']),
                'pass': dict(media=media),
                'id': entity_id,
                'identity': dict(script=dict(name='update_handler')),
                'reason': dict(code='newbie'),
            },
        ],
        key=lambda k: k['id'],
    )

    assert v1_upload.times_called == 4

    tag_requests = []
    while v1_upload.has_calls:
        tag_requests.append(v1_upload.next_call()['request'].json)

    assert not utils.symmetric_lists_diff(
        tag_requests,
        [
            {
                'entity_type': 'dbid_uuid',
                'merge_policy': 'append',
                'tags': [dict(match=dict(id=entity_id), name='thermobag')],
            },
            {
                'entity_type': 'dbid_uuid',
                'merge_policy': 'append',
                'tags': [dict(match=dict(id=entity_id), name='thermobag_off')],
            },
            {'entity_type': 'dbid_uuid', 'merge_policy': 'remove', 'tags': []},
            {'entity_type': 'dbid_uuid', 'merge_policy': 'remove', 'tags': []},
        ],
    )


@pytest.mark.config(
    QC_EXAMS_ADMIN_UPDATE_DRIVERS_FIELDS=[
        'delivery.thermobag',
        'delivery.thermopack',
    ],
    QC_EXAMS_ADMIN_UPDATE_EXAMS=['thermobag'],
    QC_EXAMS_ADMIN_UPDATE_EXAMS_FIELDS={
        'thermobag': ['delivery.thermobag', 'delivery.thermopack'],
    },
)
@pytest.mark.parametrize(
    'delivery_data',
    [
        dict(thermobag=True, thermopack=True),
        dict(thermobag=False, thermopack=True),
        dict(thermobag=True, thermopack=False),
    ],
)
async def test_disable(
        web_app_client,
        mock_quality_control_py3,
        mock_tags,
        patch_aiohttp_session,
        response_mock,
        delivery_data,
):
    @patch_aiohttp_session(discovery.find_service('taximeter_xservice').url)
    def _patch_update_cars(method, url, json, **kwargs):
        return response_mock(
            json=dict(
                processed=[
                    dict(park_id='park', driver_id=x['new_data']['driver_id'])
                    for x in json['items']
                ],
            ),
        )

    @mock_quality_control_py3('/api/v1/data/bulk_retrieve')
    def _mock_bulk_retrieve(request):
        return web.json_response(
            dict(
                items=[
                    dict(
                        id=x,
                        type='driver',
                        data=dict(park_id='park', delivery=delivery_data),
                        modified='2019-04-20T12:00:00Z',
                    )
                    for x in request.json['items']
                ],
            ),
        )

    @mock_quality_control_py3('/api/v1/data/list')
    def _mock_data_list(request):
        assert request.method.lower() == 'post'
        assert request.query == dict(type='driver')
        return web.json_response({})

    @mock_quality_control_py3('/api/v1/state/bulk_retrieve')
    def _mock_state_bulk_retrieve(request):
        assert request.method.lower() == 'post'
        return web.json_response(
            dict(
                items=[
                    dict(
                        id=x,
                        type=request.query['type'],
                        exams=[
                            dict(
                                code=consts.qc.Exam.THERMOBAG,
                                modified='2020-01-01',
                                enabled=True,
                            ),
                        ],
                    )
                    for x in request.json['items']
                ],
            ),
        )

    @mock_quality_control_py3('/api/v1/state/list')
    def mock_state_list(request):
        assert request.method.lower() == 'post'
        return web.json_response({})

    @mock_tags('/v1/upload')
    def v1_upload(request):
        return web.json_response({})

    items = [
        dict(park_id='park', driver_id='driver0'),
        dict(park_id='park', driver_id='driver1'),
    ]
    response = await web_app_client.post(
        'v1/update/drivers', json=dict(items=items), headers=HEADERS,
    )

    assert response.status == 200
    response_data = await response.json()

    assert response_data.pop('modified', []) == items
    assert response_data == dict()

    assert mock_state_list.times_called == 1

    states_update = mock_state_list.next_call()['request'].json
    # remove generated log identificator
    for x in states_update:
        del x['identity']['script']['id']

    assert sorted(states_update, key=lambda k: k['id']) == sorted(
        [
            dict(
                enabled=False,
                id='park_' + x['driver_id'],
                identity=dict(script=dict(name='update_handler')),
                reason=dict(code='change'),
            )
            for x in items
        ],
        key=lambda k: k['id'],
    )

    assert v1_upload.times_called == 4

    tag_requests = []
    while v1_upload.has_calls:
        tag_requests.append(v1_upload.next_call()['request'].json)

    assert not utils.symmetric_lists_diff(
        tag_requests,
        [
            {'entity_type': 'dbid_uuid', 'merge_policy': 'append', 'tags': []},
            {'entity_type': 'dbid_uuid', 'merge_policy': 'append', 'tags': []},
            {
                'entity_type': 'dbid_uuid',
                'merge_policy': 'remove',
                'tags': [
                    dict(
                        match=dict(id='park_' + x['driver_id']),
                        name='thermobag',
                    )
                    for x in items
                ],
            },
            {
                'entity_type': 'dbid_uuid',
                'merge_policy': 'remove',
                'tags': [
                    dict(
                        match=dict(id='park_' + x['driver_id']),
                        name='thermobag_off',
                    )
                    for x in items
                ],
            },
        ],
    )
