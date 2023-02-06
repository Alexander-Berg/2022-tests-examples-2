import datetime

import pytest

from taxi.clients import mds_s3
from taxi.stq import async_worker_ng

from rida.stq import upload_route_image
from test_rida import helpers
from test_rida import maps_utils


_NOW = datetime.datetime(2021, 1, 1, tzinfo=datetime.timezone.utc)
_POINT_A = maps_utils.POLYLINE[0]
_POINT_B = maps_utils.POLYLINE[-1]
_OFFER_GUID = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5K'


def _verify_one_request(mock, request_params):
    assert mock.times_called >= 1
    google_maps_request = mock.next_call()['request']
    mock_args = list(google_maps_request.query.items())
    assert sorted(mock_args) == sorted(request_params)


def _setup_mocks(patch, mockserver, fail_gmaps: bool = False):
    @patch('taxi.clients.mds_s3.MdsS3Client.upload_content')
    async def _mds_s3_mock(*args, **kwargs):
        return mds_s3.S3Object(Key='key', ETag=None)

    @mockserver.json_handler('/googleapis/maps/api/staticmap')
    def _mock_static_maps(request):
        return mockserver.make_response(b'image_of_route', status=200)

    @mockserver.json_handler(
        '/api-proxy-external-geo/google/maps/api/directions/json',
    )
    def _mock_google_maps(request):
        if fail_gmaps:
            return mockserver.make_response(
                'Internal server error', status=500,
            )
        return maps_utils.make_gmaps_directions_response(
            maps_utils.POLYLINE, 1, 1, 1, 200, 'OK', False, mockserver,
        )

    @mockserver.json_handler('/static-yandex-maps/1.x/')
    def _mock_static_yandex_maps(request):
        return mockserver.make_response(
            b'yandex_image_of_route', content_type='image/png', status=200,
        )

    @mockserver.json_handler('/yamaps-over-osm-router/v2/route')
    def _mock_yamaps(request):
        return maps_utils.mock_yamaps(request, False, mockserver)

    return (
        _mds_s3_mock,
        _mock_static_maps,
        _mock_google_maps,
        _mock_static_yandex_maps,
        _mock_yamaps,
    )


async def _create_offer(web_app_client, single_point: bool):
    headers = helpers.get_auth_headers(user_id=3456)
    response = await web_app_client.post(
        '/v3/user/offer/create',
        headers=headers,
        json={
            'offer_guid': _OFFER_GUID,
            'point_a': 'point_a',
            'point_b': 'point_b',
            'point_a_lat': _POINT_A[1],
            'point_a_long': _POINT_A[0],
            'point_b_lat': 0 if single_point else _POINT_B[1],
            'point_b_long': 0 if single_point else _POINT_B[0],
            'points_data': 'points_data',
            'entrance': '1',
            'comment': 'comment',
            'initial_price': 35.5,
            'payment_method_id': 1,
            'payment_method': 'cash',
            'zone_id': 34,
            'country_id': 87,
        },
    )
    assert response.status == 200


@pytest.mark.mongodb_collections('rida_offers')
@pytest.mark.filldb()
@pytest.mark.parametrize('single_point', [False, True])
async def test_user_offer_create_check_url(
        web_app_client, mockserver, patch, single_point, stq,
):
    (
        _mds_s3_mock,
        _mock_static_maps,
        _mock_google_maps,
        _mock_static_yandex_maps,
        _mock_yamaps,
    ) = _setup_mocks(patch, mockserver)
    headers = helpers.get_auth_headers(user_id=3456)

    await _create_offer(web_app_client, single_point)

    response = await web_app_client.post(
        '/v3/user/offer/info',
        headers=headers,
        json={'offer_guid': _OFFER_GUID},
    )
    assert response.status == 200
    offer = (await response.json())['data']['offer']
    url = (
        f'https://rida-external.s3.yandex.net/routes/'
        f'%5B{_POINT_A[0]}%2C%20{_POINT_A[1]}%5D_'
    )
    if single_point:
        url += 'None.png'
    else:
        url += f'%5B{_POINT_B[0]}%2C%20{_POINT_B[1]}%5D.png'
    assert offer['direction_map_url'] == url

    request = stq.rida_upload_route_image.next_call()
    assert request['id'] == _OFFER_GUID
    assert request['kwargs'] == {
        'src': _POINT_A,
        'dst': None if single_point else _POINT_B,
    }

    assert not _mock_static_maps.has_calls


@pytest.mark.parametrize(
    'single_point, image_source',
    [
        pytest.param(False, 'google'),
        pytest.param(True, 'google'),
        pytest.param(
            False,
            'yandex',
            marks=pytest.mark.config(
                RIDA_ROUTE_IMAGE_SOURCE='yamaps_over_osm',
            ),
        ),
    ],
)
@pytest.mark.filldb()
async def test_route_image_uploading(
        patch,
        mds_s3_client,
        stq3_context,
        mockserver,
        single_point,
        image_source,
):
    (
        _mds_s3_mock,
        _mock_static_maps,
        _mock_google_maps,
        _mock_static_yandex_maps,
        _mock_yamaps,
    ) = _setup_mocks(patch, mockserver)
    task_info = async_worker_ng.TaskInfo(
        id=_OFFER_GUID,
        exec_tries=0,
        reschedule_counter=0,
        queue='upload_route_image',
    )
    await upload_route_image.task(
        stq3_context,
        src=_POINT_A,
        dst=None if single_point else _POINT_B,
        task_meta_info=task_info,
    )

    if single_point:
        _verify_one_request(
            _mock_static_maps,
            [
                ('size', f'300x600'),
                ('maptype', 'roadmap'),
                ('key', 'super-duper-secret'),
                (
                    'markers',
                    'icon:https://api.rida.app///img/'
                    'point_from_orange.png|64.54372,40.51758',
                ),
            ],
        )
    else:
        if image_source == 'google':
            _verify_one_request(
                _mock_static_maps,
                [
                    ('size', f'300x600'),
                    ('maptype', 'roadmap'),
                    ('key', 'super-duper-secret'),
                    (
                        'path',
                        'color:#000000|weight:5|enc:ge}hK'
                        '{qhvFj{X|~eBle}Fr{Z|tIzd'
                        'fCpmdAucA~|Bw}yQq`tAtmTa^neuC}d|F~hRg{XxdfC',
                    ),
                    (
                        'markers',
                        'icon:https://api.rida.app///img/'
                        'point_from_orange.png|64.54372,40.51758',
                    ),
                    (
                        'markers',
                        'icon:https://api.rida.app///img/'
                        'point_to_green.png|64.54844,40.5835',
                    ),
                ],
            )
            assert _mock_static_yandex_maps.times_called == 0
        else:
            _verify_one_request(
                _mock_static_yandex_maps,
                [
                    ('l', 'map'),
                    (
                        'pl',
                        'zD9qAujb2AMK-vv_Iv3-_wD6-_8i_f7_Dun-__gR9v8O6f7_Ah'
                        'L2_yq4-v8qlf__Krj6_yCV__9yFQAAeEn9_3wVAABuSf3_nI0X'
                        'AKDY__-cjRcAoNj__2Qp__94UgMAbin__4JSAwD4Ifr_ugkAAP'
                        'gh-v-wCQAA4D7__9bjCQDgPv__4OMJACq4-v_UAgEANLj6_9QC'
                        'AQA=',
                    ),
                    ('size', '300,600'),
                    ('data_provider', 'osm'),
                    ('api_key', 'static-api-key'),
                    (
                        'signature',
                        'WUKpKnN0yGqmERkBhsH7UvSssOOGNusTZnFhrSYcGZs=',
                    ),
                    ('cr', '0'),
                    ('lg', '0'),
                    ('lang', 'en_US'),
                ],
            )
            assert _mock_static_maps.times_called == 0

    call = _mds_s3_mock.call
    if image_source == 'google':
        assert call['kwargs']['body'] == b'image_of_route'
    else:
        assert call['kwargs']['body'] == b'yandex_image_of_route'


@pytest.mark.config(
    RIDA_ROUTE_IMAGE_SOURCE='yamaps_over_osm',
    RIDA_GEO_ROUTER_SETTINGS={
        '__default__': {},
        'yamaps_over_osm': {
            'route_preview': {
                'image_size': {'width': 600, 'height': 300},
                'route_color': '#000000',
                'route_weight': 5,
                'start_image_url': 'url',
                'end_image_url': 'url',
                'max_number_of_points': 6,
            },
        },
    },
)
async def test_route_size(patch, mds_s3_client, stq3_context, mockserver):
    (
        _mds_s3_mock,
        _mock_static_maps,
        _mock_google_maps,
        _mock_static_yandex_maps,
        _mock_yamaps,
    ) = _setup_mocks(patch, mockserver)
    task_info = async_worker_ng.TaskInfo(
        id=_OFFER_GUID,
        exec_tries=0,
        reschedule_counter=0,
        queue='upload_route_image',
    )
    await upload_route_image.task(
        stq3_context, src=_POINT_A, dst=_POINT_B, task_meta_info=task_info,
    )
    request = _mock_static_yandex_maps.next_call()['request']
    assert len(request.query['pl']) == 64


@pytest.mark.filldb()
async def test_gmaps_failing(patch, mds_s3_client, stq3_context, mockserver):
    (
        _mds_s3_mock,
        _mock_static_maps,
        _mock_google_maps,
        _mock_static_yandex_maps,
        _mock_yamaps,
    ) = _setup_mocks(patch, mockserver, fail_gmaps=True)

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def _stq_reschedule(request):
        return {}

    task_info = async_worker_ng.TaskInfo(
        id=_OFFER_GUID,
        exec_tries=0,
        reschedule_counter=0,
        queue='upload_route_image',
    )
    await upload_route_image.task(
        stq3_context, src=_POINT_A, dst=_POINT_B, task_meta_info=task_info,
    )

    assert _stq_reschedule.times_called == 1
