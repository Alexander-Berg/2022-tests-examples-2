import base64

import pytest

from taxi_antifraud.settings import qc_settings


@pytest.fixture
def mock_secdist(simple_secdist):
    simple_secdist['settings_override']['ANTIFRAUD_OCR_API_KEY'] = 'token'
    return simple_secdist


@pytest.fixture
def mock_personal(patch):
    @patch('taxi.clients.personal.PersonalApiClient.retrieve')
    async def _retrieve(data_type, request_id, *args, **kwargs):
        assert request_id.endswith('_pd_id')
        return {'license': request_id[:-6]}

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, driver_license, *args, **kwargs):
        return {'id': driver_license + '_pd_id'}


def get_necessary_fields(docs):
    return [
        {
            'exam': doc['exam'],
            'features': doc['features'],
            'features_name': doc['features_name'],
            'face_features_cbir_response': doc['face_features_cbir_response'],
            'face_features_name': doc['face_features_name'],
            'meta_data': doc['meta_data'],
            'neighbour_meta_info': doc['neighbour_meta_info'],
            'neighbour_similarity': doc['neighbour_similarity'],
            'recognized_text': doc['recognized_text'],
            'pass_id': doc['pass_id'],
            'pass_modified': doc['pass_modified'].isoformat(),
            'picture_type': doc['picture_type'],
            'processed': doc['processed'].isoformat(),
            'entity_id': doc['entity_id'],
            'entity_type': doc['entity_type'],
            'storage_type': doc['storage_type'],
            'storage_pass_id': doc['storage_pass_id'],
            'picture_parameters': doc['picture_parameters'],
        }
        for doc in docs
    ]


@pytest.mark.now('2020-07-03T20:34:15.677Z')
@pytest.mark.config(
    AFS_CHECK_QC_PASSES_EXAM_TO_FEATURES_NAME_MAPPING=[
        {'exam': 'dkkk', 'features_name': 'my_super_features'},
    ],
    AFS_CHECK_QC_PASSES_EXAM_TO_FACE_FEATURES_NAME_MAPPING=[
        {
            'exam': 'dkkk',
            'picture_type': 'Front',
            'features_name': 'my_super_face_features',
        },
    ],
    AFS_CHECK_QC_PASSES_FEATURES_NAME_TO_LAYER_NAME_MAPPING=[
        {'features_name': 'my_super_features', 'layer_name': 'super_layer'},
        {
            'features_name': 'my_super_face_features',
            'layer_name': 'super_face_layer',
        },
    ],
    AFS_CHECK_QC_PASSES_EXAM_TO_OCR_STRATEGY_NAME_MAPPING=[
        {
            'exam': 'dkkk',
            'picture_type': 'Front',
            'strategy_names': ['FullOcrMultihead'],
        },
    ],
    AFS_CHECK_QC_PASSES_EXAM_TO_SAAS_SERVICE_NAME_MAPPING={
        'dkkk': {'service_name': 'my_super_service'},
    },
)
async def test_check_qc_pass(
        db,
        web_app_client,
        patch_aiohttp_session,
        response_mock,
        mock_secdist,  # pylint: disable=redefined-outer-name
        mock_personal,  # pylint: disable=redefined-outer-name
):
    @patch_aiohttp_session('http://example.com/file.jpg', 'GET')
    def get_jpg(method, url, **kwargs):
        b64_jpg = """
/9j/4AAQSkZJRgABAQAAAQABAAD/4QBARXhpZgAATU0AKgAAAAgAAwEoAAMAAAABAAEAAAE7AAIA
AAAGAAAAMgITAAMAAAABAAEAAAAAAABWYXN5YQD/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgG
BgUGCQgKCgkICQkKDA8MCgsOCwkJDRENDg8QEBEQCgwSExIQEw8QEBD/2wBDAQMDAwQDBAgEBAgQ
CwkLEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBD/wAAR
CAAPABQDAREAAhEBAxEB/8QAFwABAAMAAAAAAAAAAAAAAAAACAUGB//EACIQAAICAgMAAQUAAAAA
AAAAAAMEAgUBBgcIFAAREhMVFv/EABcBAQEBAQAAAAAAAAAAAAAAAAUIAwb/xAAoEQACAQIFAgYD
AAAAAAAAAAABAgMEEQAFBhITIUEHIjGB8PFRkcH/2gAMAwEAAhEDEQA/ANZ2DnLgrkDa9Dh2AWzs
r3K81HdXoLGEG6ilrbAh8UeSVhCZhlsoxTgZwYmZhYMYczhVKtHMta7zbXGqmzSt0/OYKDL3KEK3
HI7RA8rBlJYhblrF0Vk2bUaQEYbpY6aDYsouz+46+nz+Yk+Buw3Dn9BJ7r2w2lqdZslLrmx64KeJ
VnlupYDV2FUqMkl0p5dOLJhwyAmISf8AUvJqAMR6XQVfrLSmc0mntXS80dXG7RHcHdJE87o7khjZ
SQSeRb7BG20NbGqWnnjaWnFip69rg9Og+u98Of5QGCsC/lbZjdRdGr9c2jbsabqNTY+DUtrNT/ua
oqcsGynRuIhLGw/KurGcImhLESYRAYjOZmKpmWteeDFbPn0+cZbTCpgqDdo1l4pUdvM7q8m6MgsL
ncG6SMqxrtWRW6XMVEQjc2I72uCPbr9evbFm4aM72TpNO2RO2YvOPq62hsTGzMKCRFtDijBJrrIp
wn6lV1LAUJ5mz9hPpXgFn2wYMfDXhb4S1WQZydQ5rEsO1SsUIcyOhPkLyOCELFASQt0JkJCxbVQZ
11essfEhv+Ta36+du+FV8ovBGP/Z
        """
        return response_mock(read=base64.b64decode(b64_jpg))

    @patch_aiohttp_session(qc_settings.CBIR_URL, 'POST')
    def get_features(method, url, params, **kwargs):
        if params['cbird'] == qc_settings.CBIR_ID_FACE_FEATURES:
            features = {
                'cbirdaemon': {
                    'info_orig': '320x240',
                    'similarnn': {
                        'FaceFeatures': [
                            {
                                'Dimension': [1, 96],
                                'LayerName': 'super_face_layer',
                                'Version': '8',
                                'Features': [0.736, 0.928, 0.1111],
                            },
                            {
                                'Dimension': [1, 96],
                                'LayerName': 'super_face_layer',
                                'Version': '8',
                                'Features': [0.572, 0.374, 0.2222],
                            },
                        ],
                    },
                },
            }
        else:
            features = {
                'cbirdaemon': {
                    'info_orig': '320x240',
                    'similarnn': {
                        'ImageFeatures': [
                            {
                                'Dimension': [1, 96],
                                'LayerName': 'super_layer',
                                'Version': '8',
                                'Features': [0.123, 0.546],
                            },
                        ],
                    },
                },
            }
        return response_mock(json=features)

    @patch_aiohttp_session(qc_settings.SAAS_URL, 'GET')
    def get_saas_response(method, url, params, **kwargs):
        assert params['service'] == 'my_super_service'
        return response_mock(
            # TODO: remove needless fields
            json={
                'groupings': [
                    {
                        'docs': '1',
                        'categ': '',
                        'groups-on-page': '10',
                        'mode': 'flat',
                        'attr': '',
                    },
                ],
                'response': {
                    'results': [
                        {
                            'groups': [
                                {
                                    'documents': [
                                        {
                                            'properties': {
                                                'RequestIdInMultiRequest': '0',
                                                '_Body': 'AXsiY2l0eSI9Ilx4ZDBceGE3XHhkMFx4YjVceGQwXHhiYlx4ZDFceDhmXHhkMFx4YjFceGQwXHhiOFx4ZDBceGJkXHhkMVx4ODFceGQwXHhiYSI7InBhcmtfbmFtZSI9Ilx4ZDBceGE0XHhkMFx4YjVceGQxXHg4MFx4ZDBceGJiXHhkMFx4YjBceGQwXHhiOVx4ZDBceGJkIjsiZHJpdmVyX2lkIj0iYzQ3YzRmY2VjOGQ0NzE1OGZkMzAxNTIxNTZmMzdjZTIiOyJ1cmwiPSJodHRwOi8vc3RvcmFnZS5tZHMueWFuZGV4Lm5ldC9nZXQtdGF4aW1ldGVyLzIwMDA0MzgvOTEzNjNkY2NiZTZhNDQ4ZGE5OTUwY2M5OGFlMmEzNDQuanBnIjsicGhvdG9fa2V5Ij0iRnJvbnQiOyJxY19pZCI9IjU2NTkyMmU5ZDUzNTQ3MTQ4ZmQ2NzU4ZjhiNjg5YTg5IjsiZHJpdmVyX2xpY2Vuc2UiPSJVWkFDNzk4NTU4IjsiZHJpdmVyX25hbWUiPSJceGQwXHg5OFx4ZDBceGIyXHhkMFx4YjBceGQwXHhiZFx4ZDBceGJlXHhkMFx4YjIgXHhkMFx4YTBceGQwXHhiMFx4ZDBceGI4XHhkMFx4YmJceGQxXHg4YyBceGQwXHg5Zlx4ZDBceGIwXHhkMFx4YjJceGQwXHhiYlx4ZDBceGJlXHhkMFx4YjJceGQwXHhiOFx4ZDFceDg3Ijt9',  # noqa: E501 pylint: disable=line-too-long
                                                'KnnShardId': 'hnsw_dkk_0',
                                            },
                                            'relevance': '942027688',
                                            'url': 'shard-id:0-18725421',
                                            'docId': '0-18725421',
                                            'title': [
                                                {
                                                    'text': (
                                                        'shard-id:0-18725421'
                                                    ),
                                                },
                                            ],
                                        },
                                    ],
                                    'found': {
                                        'all': '1',
                                        'phrase': '0',
                                        'strict': '0',
                                    },
                                    'relevance': '942027688',
                                    'group_attr': '',
                                    'doccount': '1',
                                },
                                {
                                    'documents': [
                                        {
                                            'properties': {
                                                'RequestIdInMultiRequest': '0',
                                                '_Body': 'AXsBCGNpdHk9ARzQmNGA0LrRg9GC0YHQujsBEnBhcmtfbmFtZT0BGtCf0LXRgNCy0YvQuS47ARJkcml2ZXJfaWQ9AUAyNGEwM2NhMmEzMzViZmQ4OGZhMjhiN2U3NTVlYTc0ODsBBnVybD0B8gNodHRwOi8vczMubWRzLnlhbmRleC5uZXQvcXVhbGl0eS1jb250cm9sL3Bhc3MvZHJpdmVyL2YzYjY5OTM3YThjNjRkN2FhNGY2YzZmYjAwZDQ0ZmNlXzI0YTAzY2EyYTMzNWJmZDg4ZmEyOGI3ZTc1NWVhNzQ4LzVlMzkyNjQyY2IzNjNkZWI5ZGU5NjYxZS9mcm9udC5qcGc/QVdTQWNjZXNzS2V5SWQ9bUdCclhzbWNyRzR1dkFDN01nTmMmU2lnbmF0dXJlPUdiWk1CSTl0ZnR5ZFFZT2JSYkpkNnIwbW1NNCUzRCZFeHBpcmVzPTE1ODI5NDQ5MTY7ARJwaG90b19rZXk9AQpGcm9udDsBCnFjX2lkPQFAMDczNDAxYjY1ZTFlNDlmMGE5YWE2OGRlNjUxMzdkN2N9',  # noqa: E501 pylint: disable=line-too-long
                                                'KnnShardId': 'hnsw_dkk_0',
                                            },
                                            'relevance': '937016308',
                                            'url': 'shard-id:0-1799572',
                                            'docId': '0-1799572',
                                            'title': [
                                                {'text': 'shard-id:0-1799572'},
                                            ],
                                        },
                                    ],
                                    'found': {
                                        'all': '1',
                                        'phrase': '0',
                                        'strict': '0',
                                    },
                                    'relevance': '937016308',
                                    'group_attr': '',
                                    'doccount': '1',
                                },
                                {
                                    'documents': [
                                        {
                                            'properties': {
                                                'RequestIdInMultiRequest': '0',
                                                '_Body': 'AXsBCGNpdHk9ARjQmtCw0LfQsNC90Yw7ARJwYXJrX25hbWU9AWLQn9Cw0YDRgtC90LXRgF/QmNCfX9ChX1UxNTY3MDAyM1/QnNC40L3Qs9Cw0YLQuNC9OwESZHJpdmVyX2lkPQFAYTg1YzI3ZmJhOWI1NDA2Y2FhMDFiZTEwN2NlMDRkNGE7AQZ1cmw9AfIDaHR0cDovL3MzLm1kcy55YW5kZXgubmV0L3F1YWxpdHktY29udHJvbC9wYXNzL2RyaXZlci9hMWMwOWM0ZTE1M2Q0N2FjOTg2YTg5ZjkwMTQ5ZjUyOV9hODVjMjdmYmE5YjU0MDZjYWEwMWJlMTA3Y2UwNGQ0YS81ZTMxNTYwNDllZDMxZjVmZDZlNjI4YTYvZnJvbnQuanBnP0FXU0FjY2Vzc0tleUlkPW1HQnJYc21jckc0dXZBQzdNZ05jJlNpZ25hdHVyZT1mR2o4WTBORGJWZ3FVd0NwN2s3YmRsd2hpRmMlM0QmRXhwaXJlcz0xNTgyNDUyMTkwOwEScGhvdG9fa2V5PQEKRnJvbnQ7AQpxY19pZD0BQGRhNjM2YzUyMGZiNzQ0ZDM5ZTJhMWVkNzYyNzUzNDJlfQ==',  # noqa: E501 pylint: disable=line-too-long
                                                'KnnShardId': 'hnsw_dkk_0',
                                            },
                                            'relevance': '931299209',
                                            'url': 'shard-id:0-9701696',
                                            'docId': '0-9701696',
                                            'title': [
                                                {'text': 'shard-id:0-9701696'},
                                            ],
                                        },
                                    ],
                                    'found': {
                                        'all': '1',
                                        'phrase': '0',
                                        'strict': '0',
                                    },
                                    'relevance': '931299209',
                                    'group_attr': '',
                                    'doccount': '1',
                                },
                            ],
                            'found': {
                                'all': '3',
                                'phrase': '0',
                                'strict': '0',
                            },
                            'groups-on-page': '10',
                            'mode': 0,
                            'attr': '',
                        },
                    ],
                    'found': {'all': '3', 'phrase': '3', 'strict': '3'},
                },
                'page': '0',
                'request_query': 'x',
            },
        )

    @patch_aiohttp_session(qc_settings.OCR_URL, 'POST')
    def get_ocr_response(method, url, **kwargs):
        response = {
            'data': {
                'fulltext': [
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8776331544,
                        'Type': 'name',
                        'Text': 'вася',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8884754777,
                        'Type': 'middle_name',
                        'Text': 'андреич',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8860994577,
                        'Type': 'surname',
                        'Text': 'торопов',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8965252042,
                        'Type': 'subdivision',
                        'Text': '270-093',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8612621427,
                        'Type': 'birth_place',
                        'Text': 'гор. хабаровск',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.8734121323,
                        'Type': 'issued_by',
                        'Text': 'отделом уфмс россии по хабаровскому краю в железнодорожном районе гор. хабаровска',  # noqa: E501 pylint: disable=line-too-long
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0,
                        'Type': 'text',
                        'Text': '\n',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.3745638475,
                        'Type': 'number',
                        'Text': '123123',
                    },
                    {
                        'LineSizeCategory': 0,
                        'Confidence': 0.2375628735,
                        'Type': 'prev_number',
                        'Text': '575768',
                    },
                ],
            },
        }
        return response_mock(json=response)

    response = await web_app_client.post(
        '/v1/check_qc_pass',
        json={
            'qc_pass': {
                'id': '1231234',
                'exam': 'dkkk',
                'status': 'NEW',
                'entity_id': 'some_entity_id',
                'entity_type': 'some_entity_type',
                'modified': '2020-01-01T02:34:56',
                'media': [
                    {
                        'code': 'Front',
                        'url': 'http://example.com/file.jpg',
                        'required': False,
                        'storage': {'type': 'pass', 'pass_id': 'some_pass_id'},
                    },
                ],
                'data': [
                    {
                        'field': 'city',
                        'required': False,
                        'value': '\u041c\u043e\u0441\u043a\u0432\u0430',
                    },
                    {'field': 'city_level', 'required': False, 'value': '1'},
                    {
                        'field': 'country',
                        'required': False,
                        'value': '\u0420\u043e\u0441\u0441\u0438\u044f',
                    },
                    {
                        'field': 'car_name',
                        'required': False,
                        'value': 'Mercedes-Benz E-klasse AMG [\u0410111\u041a\u0425777] 2019 \u0411\u0435\u043b\u044b\u0439 (\u0410111\u041a\u0425777)',  # noqa: E501 pylint: disable=line-too-long
                    },
                    {
                        'field': 'car_number',
                        'required': False,
                        'value': 'A111KX777',
                    },
                    {
                        'field': 'car_service',
                        'required': False,
                        'value': '{"lightbox":true,"sticker":true}',
                    },
                    {'field': 'year', 'required': False, 'value': 2017},
                ],
            },
        },
    )
    assert response.status == 200
    assert await response.json() == {}

    response = await web_app_client.post(
        '/v1/check_qc_pass',
        json={
            'qc_pass': {
                'id': '1231234',
                'exam': 'dkkk',
                'status': 'NEW',
                'entity_id': 'some_entity_id',
                'entity_type': 'some_entity_type',
                'modified': '2020-01-01T02:34:56',
                'media': [
                    {
                        'code': 'Front',
                        'url': 'http://example.com/file.jpg',
                        'required': False,
                        'storage': {'type': 'pass', 'pass_id': 'some_pass_id'},
                    },
                ],
            },
        },
    )
    assert response.status == 200
    assert await response.json() == {}

    assert len(get_jpg.calls) == 2
    assert len(get_features.calls) == 2
    assert len(get_saas_response.calls) == 1
    assert len(get_ocr_response.calls) == 1

    assert (
        get_necessary_fields(
            await db.antifraud_check_qc_pass_verdicts.find().to_list(None),
        )
        == [
            {
                'exam': 'dkkk',
                'features': [0.123, 0.546],
                'features_name': 'my_super_features',
                'face_features_cbir_response': {
                    'cbirdaemon': {
                        'info_orig': '320x240',
                        'similarnn': {
                            'FaceFeatures': [
                                {
                                    'Dimension': [1, 96],
                                    'Features': [0.736, 0.928, 0.1111],
                                    'LayerName': 'super_face_layer',
                                    'Version': '8',
                                },
                                {
                                    'Dimension': [1, 96],
                                    'Features': [0.572, 0.374, 0.2222],
                                    'LayerName': 'super_face_layer',
                                    'Version': '8',
                                },
                            ],
                        },
                    },
                },
                'face_features_name': 'my_super_face_features',
                'meta_data': [
                    {'field': 'city', 'required': False, 'value': 'Москва'},
                    {'field': 'city_level', 'required': False, 'value': '1'},
                    {'field': 'country', 'required': False, 'value': 'Россия'},
                    {
                        'field': 'car_name',
                        'required': False,
                        'value': (
                            'Mercedes-Benz E-klasse AMG [А111КХ777] 2019 '
                            'Белый (А111КХ777)'
                        ),
                    },
                    {
                        'field': 'car_number',
                        'required': False,
                        'value': 'A111KX777',
                    },
                    {
                        'field': 'car_service',
                        'required': False,
                        'value': '{"lightbox":true,"sticker":true}',
                    },
                    {'field': 'year', 'required': False, 'value': 2017},
                ],
                'neighbour_meta_info': {
                    'city': 'Челябинск',
                    'driver_id': 'c47c4fcec8d47158fd30152156f37ce2',
                    'driver_license': '*****98558',
                    'driver_name': 'Иванов Раиль Павлович',
                    'park_name': 'Ферлайн',
                    'photo_key': 'Front',
                    'qc_id': '565922e9d53547148fd6758f8b689a89',
                    'url': 'http://storage.mds.yandex.net/get-taximeter/2000438/91363dccbe6a448da9950cc98ae2a344.jpg',  # noqa: E501 pylint: disable=line-too-long
                },
                'neighbour_similarity': 0.942027688,
                'pass_id': '1231234',
                'pass_modified': '2020-01-01T02:34:56',
                'picture_type': 'Front',
                'processed': '2020-07-03T20:34:15.677000',
                'recognized_text': {
                    'FullOcrMultihead': [
                        {
                            'confidence': 0.8776331544,
                            'text': 'вася',
                            'type': 'name',
                        },
                        {
                            'confidence': 0.8884754777,
                            'text': 'андреич',
                            'type': 'middle_name',
                        },
                        {
                            'confidence': 0.8860994577,
                            'text': 'торопов',
                            'type': 'surname',
                        },
                        {
                            'confidence': 0.8965252042,
                            'text': '270-093',
                            'type': 'subdivision',
                        },
                        {
                            'confidence': 0.8612621427,
                            'text': 'гор. хабаровск',
                            'type': 'birth_place',
                        },
                        {
                            'confidence': 0.8734121323,
                            'text': (
                                'отделом уфмс россии по хабаровскому краю в '
                                'железнодорожном районе гор. хабаровска'
                            ),
                            'type': 'issued_by',
                        },
                        {
                            'confidence': 0.3745638475,
                            'pd_id': '123123_pd_id',
                            'text': '***123',
                            'type': 'number',
                        },
                        {
                            'confidence': 0.2375628735,
                            'pd_id': '575768_pd_id',
                            'text': '***768',
                            'type': 'prev_number',
                        },
                    ],
                },
                'entity_id': 'some_entity_id',
                'entity_type': 'some_entity_type',
                'storage_pass_id': 'some_pass_id',
                'storage_type': 'pass',
                'picture_parameters': {
                    'exif': {
                        'Artist': 'Vasya',
                        'ResolutionUnit': '1',
                        'YCbCrPositioning': '1',
                    },
                    'height': 15,
                    'bytes': 819,
                    'md5': '5e694a57f80dd228ee95ef6039839156',
                    'width': 20,
                },
            },
        ]
    )
