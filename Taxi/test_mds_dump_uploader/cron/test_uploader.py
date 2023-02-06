import datetime
import json
import logging

import aiohttp.web
import multidict
import pytest

# pylint: disable=redefined-outer-name
from mds_dump_uploader.generated.cron import run_cron

logger = logging.getLogger(__name__)

MDS_HOST = 'http://s3.mds.yandex.net'
LIST_MDS_RESPONSE = (
    '<list_object>                                           '
    ' <Contents><Key>dump/1266400000</Key><ETag></ETag></Contents>'
    ' <Contents><Key>dump/1266404000</Key><ETag></ETag></Contents>'
    ' <Contents><Key>dump/1266408377</Key><ETag></ETag></Contents>'
    ' <Contents><Key>dump/126640.377</Key><ETag></ETag></Contents>'
    '</list_object>                                         '
)

MDS_CATEGORIES_DUMP_UPLOADER = {
    '__default__': {
        'enabled': True,
        'sources': [
            {
                'compress': True,
                'enabled': True,
                'request': {
                    'body': (
                        '{"revisions":{"cars":"",'
                        '"drivers":"","parks":""}, "limits": {"cars":"1",'
                        '"drivers":"1","parks":"1"}}'
                    ),
                    'timeout': 600,
                },
                'keys_limit': 1,
                'outdated_hours_limit': 10,
                's3_target_path': 'dump',
                'max_requests': 10,
            },
        ],
    },
}


@pytest.fixture
def mock_mds_req(patch_aiohttp_session, response_mock, load_json):
    @patch_aiohttp_session(MDS_HOST, 'GET')
    def patch_request_get(method, url, headers, **kwargs):
        response = response_mock(headers={'ETag': ''}, read=LIST_MDS_RESPONSE)
        response.status_code = response.status
        response.raw_headers = [
            (k.encode(), v.encode()) for k, v in response.headers.items()
        ]
        return response

    @patch_aiohttp_session(MDS_HOST, 'DELETE')
    def patch_request_delete(method, url, headers, **kwargs):
        response = response_mock(headers={'ETag': ''})
        response.status_code = response.status
        response.raw_headers = [
            (k.encode(), v.encode()) for k, v in response.headers.items()
        ]
        return response

    @patch_aiohttp_session(MDS_HOST, 'PUT')
    def patch_request(method, url, headers, **kwargs):
        response = response_mock(headers={'ETag': ''})
        response.status_code = response.status
        response.raw_headers = [
            (k.encode(), v.encode()) for k, v in response.headers.items()
        ]
        return response

    return [patch_request, patch_request_delete, patch_request_get]


@pytest.mark.config(MDS_CATEGORIES_DUMP_UPLOADER=MDS_CATEGORIES_DUMP_UPLOADER)
async def test_uploader(
        mockserver,
        taxi_config,
        simple_secdist,
        mock_mds_req,
        mock_driver_categories_api,
):
    @mock_driver_categories_api('/v1/drivers/categories/bulk')
    async def v1_drivers_categories_bulk(request):
        def _get_current_timestamp():
            return int(
                datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
                * 1000000000,
            )

        categories_mock = {
            'blocked_by_driver': [],
            'cars': [],
            'parks': [],
            'revisions': {'parks': '', 'cars': '', 'drivers': ''},
        }
        revision = _get_current_timestamp()
        categories_mock['revisions']['parks'] = str(revision)
        categories_mock['revisions']['cars'] = str(revision)
        categories_mock['revisions']['drivers'] = str(revision)
        headers = multidict.MultiDict(
            {
                'ETag': '',
                'Content-Type': 'application/octet-stream',
                'X-YaTaxi-Drivers-Revision': str(revision),
                'X-YaTaxi-Parks-Revision': str(revision),
                'X-YaTaxi-Cars-Revision': str(revision),
            },
        )

        return aiohttp.web.Response(
            body=bytearray(json.dumps(categories_mock).encode('utf-8')),
            headers=headers,
        )

    await run_cron.main(['mds_dump_uploader.crontasks.uploader', '-t', '0'])
    source = MDS_CATEGORIES_DUMP_UPLOADER['__default__']['sources'][0]
    mds_calls = mock_mds_req[0].calls
    assert mds_calls

    mds_secdist = simple_secdist['settings_override']['DRIVER_STATUS_MDS_S3']
    mds_url = 'http://{0}/{1}/{2}'.format(
        mds_secdist['url'], mds_secdist['bucket'], source['s3_target_path'],
    )
    assert mds_calls[0]['method'] == 'put'
    assert mds_calls[0]['url'].startswith(mds_url)

    dca_call = await v1_drivers_categories_bulk.wait_call()
    assert dca_call
    assert dca_call['request'].json != source['request']['body']

    mds_calls_delete = mock_mds_req[1].calls

    assert len(mds_calls_delete) == 3
    assert mds_calls_delete[0]['method'] == 'delete'
    assert mds_calls_delete[0]['url'] == '{0}/1266404000'.format(mds_url)

    assert mds_calls_delete[1]['method'] == 'delete'
    assert mds_calls_delete[1]['url'] == '{0}/1266400000'.format(mds_url)
