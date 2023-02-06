# pylint: disable=redefined-outer-name
import datetime
import json

import aiohttp.web
import pytest

from parks_certifications_worker.generated.cron import run_cron


CURR_DATE = datetime.datetime.now().replace(microsecond=0)


@pytest.mark.parametrize(
    ['parks_list_response', 'parks_contacts_response', 'file_payload'],
    [
        (
            'list_response_1.json',
            'contacts_response_1.json',
            {
                'park1': {
                    'address': 'address1',
                    'city': 'Москва',
                    'email': 'email1',
                    'name': 'Test Park 1',
                    'schedule': 'schedule1',
                },
                'park2': {
                    'address': 'address2',
                    'city': 'Брянск',
                    'email': 'mail2',
                    'name': 'Test Park 2',
                    'schedule': 'schedule2',
                },
            },
        ),
        (
            'list_response_2.json',
            'contacts_response_2.json',
            {
                'park1': {
                    'address': 'address1',
                    'city': 'Москва',
                    'email': 'email1',
                    'name': 'Test Park 1',
                    'schedule': 'schedule1',
                },
                'park2': {
                    'address': 'address2',
                    'city': 'Брянск',
                    'email': 'mail2',
                    'name': 'Test Park 2',
                    'schedule': 'schedule2',
                },
                'park3': {
                    'address': None,
                    'city': 'Чебоксары',
                    'email': 'mail3',
                    'name': 'Test Park 3',
                    'schedule': None,
                },
            },
        ),
        (
            'list_response_3.json',
            'contacts_response_3.json',
            {'park1': {'city': 'Москва', 'name': 'Test Park 1'}},
        ),
    ],
)
async def test_certified_parks_upload(
        patch,
        load_json,
        mock_fleet_parks,
        simple_secdist,
        mockserver,
        patch_aiohttp_session,
        response_mock,
        parks_list_response,
        parks_contacts_response,
        file_payload,
):
    @patch(
        (
            'parks_certifications_worker.generated.'
            'cron.yt_wrapper.plugin.AsyncYTClient.list'
        ),
    )
    async def _yt_list(path, *args, **kwargs):
        assert path.endswith(CURR_DATE.strftime('quarterly/%Y/new_widget'))
        return ['q1', 'q2', 'q3']

    @patch(
        (
            'parks_certifications_worker.generated.'
            'cron.yt_wrapper.plugin.AsyncYTClient.read_table'
        ),
    )
    async def _yt_select_rows(select_query, *args, **kwargs):
        return load_json('yt_certs.json')

    @mock_fleet_parks('/v1/parks/contacts')
    async def _v1_parks_contacts_get(request):
        parks_index = int(request.query['park_id'][-1]) - 1
        parks_contacts_json = load_json(parks_contacts_response)
        return aiohttp.web.json_response(parks_contacts_json[parks_index])

    @mock_fleet_parks('/v1/parks/list')
    async def _v1_parks_list_post(request):
        assert request.json['query']['park']['ids'] == [
            'park1',
            'park2',
            'park3',
        ]
        parks_list_json = load_json(parks_list_response)
        return aiohttp.web.json_response({'parks': parks_list_json})

    @patch_aiohttp_session(
        'https://cloud-api.yandex.net:443/v1/disk/resources', 'GET',
    )
    def _yadisk_resources(*args, **kwargs):
        response_json = {'public_url': 'https://yadi.sk/d/xXt6YeGJBU4hHg'}
        return response_mock(json=response_json, status=200)

    @patch_aiohttp_session(
        'https://cloud-api.yandex.net:443/v1/disk/resources/upload', 'GET',
    )
    def _yadisk_resources_upload_get(*args, **kwargs):
        response_json = {
            'operation_id': '746a7e7831d4',
            'href': (
                'https://uploader35o.disk.yandex.net:443/'
                'upload-target/20200416T014445'
            ),
            'method': 'PUT',
            'templated': False,
        }
        return response_mock(json=response_json, status=200)

    @patch_aiohttp_session(
        (
            'https://uploader35o.disk.yandex.net:443/'
            'upload-target/20200416T014445'
        ),
        'PUT',
    )
    def _yadisk_resources_upload_put(*args, **kwargs):
        assert json.loads(kwargs['data']) == file_payload
        return response_mock(json={}, status=200)

    @patch_aiohttp_session(
        'https://cloud-api.yandex.net:443/v1/disk/resources/publish', 'PUT',
    )
    def _yadisk_resources_publish(*args, **kwargs):
        response_json = {
            'href': (
                'https://cloud-api.yandex.net/v1/disk/resources?'
                'path=disk%3A%2Fcertified_partners_temp.json'
            ),
            'method': 'GET',
            'templated': False,
        }
        return response_mock(json=response_json, status=200)

    simple_secdist['settings_override'].update({'YADISK_OAUTH_TOKEN': '12345'})

    await run_cron.main(
        [
            'parks_certifications_worker.crontasks.certified_parks_upload',
            '-t',
            '0',
        ],
    )
