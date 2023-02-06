import typing

from aiohttp import web
import pytest


@pytest.mark.config(
    QC_EXAMS_ADMIN_UPDATE_EXAMS_FIELDS={
        'thermobag': ['delivery.thermobag', 'delivery.thermopack'],
    },
)
async def test_get_media_thermopack(mock_quality_control_py3, web_app_client):
    @mock_quality_control_py3('/api/v1/data')
    def _mock_data_get(request):
        assert request.method.lower() == 'get'
        return web.json_response(
            dict(
                id='entity_id',
                type='driver',
                data=dict(
                    last_name='Петров',
                    middle_name='Петрович',
                    first_name='Петр',
                    delivery=dict(thermobag=False, thermopack=True),
                ),
                modified='2018-12-21T05:00:00+03:00',
            ),
        )

    @mock_quality_control_py3('/api/v1/schedule')
    def _mock_schedule_post(request):
        assert request.json == {
            'future': [
                {
                    'begin': '2018-12-21T05:00:00+03:00',
                    'can_pass': True,
                    'sanctions': ['orders_off'],
                },
            ],
            'media': ['thermopack'],
        }
        assert request.method.lower() == 'post'
        return web.json_response(data={})

    response = await web_app_client.post(
        'api/v1/schedule',
        params={
            'type': 'driver',
            'id': 'entity_id',
            'exam': 'thermobag',
            'modified': '2018-12-21T05:00:00+03:00',
        },
        json={
            'future': [
                {
                    'begin': '2018-12-21T05:00:00+03:00',
                    'can_pass': True,
                    'sanctions': ['orders_off'],
                },
            ],
        },
    )

    assert response.status == 200


@pytest.mark.config(
    QC_EXAMS_ADMIN_UPDATE_EXAMS_FIELDS={
        'thermobag': ['delivery.thermobag', 'delivery.thermopack'],
    },
    TAXIMETER_QC_MEDIA={
        '__default__': {'thermobag': ['front', 'left']},
        'rus': {'thermobag': ['thermobag', 'thermopack']},
    },
)
async def test_get_media_no_data(
        mockserver,
        mock_quality_control_py3,
        web_app_client,
        load_json: typing.Callable[[str], dict],
):
    @mock_quality_control_py3('/api/v1/data')
    def _mock_data_get(request):
        assert request.method.lower() == 'get'
        return web.json_response(
            dict(
                id='entity_id',
                type='driver',
                data=dict(
                    last_name='Петров',
                    middle_name='Петрович',
                    first_name='Петр',
                ),
                modified='2018-12-21T05:00:00+03:00',
            ),
        )

    @mock_quality_control_py3('/api/v1/schedule')
    def _mock_schedule_post(request):
        assert request.json == {
            'future': [
                {
                    'begin': '2018-12-21T05:00:00+03:00',
                    'can_pass': True,
                    'sanctions': ['orders_off'],
                },
            ],
            'media': ['thermobag', 'thermopack'],
        }
        assert request.method.lower() == 'post'
        return web.json_response(data={})

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _fleet_parks_handler(request):
        return load_json('fleet_parks_response.json')

    response = await web_app_client.post(
        'api/v1/schedule',
        params={
            'type': 'driver',
            'id': 'entity_id',
            'exam': 'thermobag',
            'modified': '2018-12-21T05:00:00+03:00',
        },
        json={
            'future': [
                {
                    'begin': '2018-12-21T05:00:00+03:00',
                    'can_pass': True,
                    'sanctions': ['orders_off'],
                },
            ],
        },
    )

    assert response.status == 200
