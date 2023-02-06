import pytest

from tests_bank_applications import common

SUPPORT_HANDLE_URL = '/applications-support/v1/get_applications'
INTERNAL_HANDLE_URL = '/applications-internal/v1/get_applications'


@pytest.mark.parametrize('url', [SUPPORT_HANDLE_URL, INTERNAL_HANDLE_URL])
async def test_get_applications(
        taxi_bank_applications, mockserver, access_control_mock, url,
):
    response = await taxi_bank_applications.post(
        url,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'uid': common.DEFAULT_YANDEX_UID,
                'buid': common.DEFAULT_YANDEX_BUID,
            },
            'limit': 100,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['applications']) == 15


@pytest.mark.parametrize('url', [SUPPORT_HANDLE_URL, INTERNAL_HANDLE_URL])
async def test_get_applications_with_page_size(
        taxi_bank_applications, mockserver, access_control_mock, url,
):
    response = await taxi_bank_applications.post(
        url,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'uid': common.DEFAULT_YANDEX_UID,
                'buid': common.DEFAULT_YANDEX_BUID,
            },
            'limit': 3,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['applications']) == 3
    assert resp['cursor'] == 'eyJjdXJzb3Jfa2V5IjoxM30='


@pytest.mark.parametrize('url', [SUPPORT_HANDLE_URL, INTERNAL_HANDLE_URL])
async def test_get_applications_without_user_id(
        taxi_bank_applications, mockserver, access_control_mock, url,
):
    response = await taxi_bank_applications.post(
        url, headers=common.get_support_headers(),
    )
    assert response.status_code == 400


@pytest.mark.parametrize('url', [SUPPORT_HANDLE_URL, INTERNAL_HANDLE_URL])
async def test_get_applications_with_cursor(
        taxi_bank_applications, mockserver, access_control_mock, url,
):
    response = await taxi_bank_applications.post(
        url,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'uid': common.DEFAULT_YANDEX_UID,
                'buid': common.DEFAULT_YANDEX_BUID,
            },
            'limit': 3,
            'cursor': 'eyJjdXJzb3Jfa2V5Ijo1fQ==',
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['applications']) == 3
    assert resp['cursor'] == 'eyJjdXJzb3Jfa2V5IjoyfQ=='


@pytest.mark.parametrize(
    'app_type, count',
    [
        ('REGISTRATION', 2),
        ('SIMPLIFIED_IDENTIFICATION', 3),
        ('SIMPLIFIED_IDENTIFICATION_ESIA', 1),
        ('DIGITAL_CARD_ISSUE', 5),
        ('PLUS', 1),
    ],
)
@pytest.mark.parametrize('url', [SUPPORT_HANDLE_URL, INTERNAL_HANDLE_URL])
async def test_get_applications_with_type(
        taxi_bank_applications,
        mockserver,
        app_type,
        count,
        access_control_mock,
        url,
):
    response = await taxi_bank_applications.post(
        url,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'uid': common.DEFAULT_YANDEX_UID,
                'buid': common.DEFAULT_YANDEX_BUID,
                'type': app_type,
            },
            'limit': 100,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['applications']) == count
    assert 'cursor' not in resp


@pytest.mark.parametrize('url', [SUPPORT_HANDLE_URL, INTERNAL_HANDLE_URL])
async def test_get_applications_with_type_and_page_size(
        taxi_bank_applications, mockserver, access_control_mock, url,
):
    response = await taxi_bank_applications.post(
        url,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'uid': common.DEFAULT_YANDEX_UID,
                'buid': common.DEFAULT_YANDEX_BUID,
                'type': 'DIGITAL_CARD_ISSUE',
            },
            'limit': 2,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp['cursor'] == 'eyJjdXJzb3Jfa2V5Ijo4fQ=='
    assert resp['applications'] == [
        {
            'application_id': '7948e3a9-623c-4524-a390-9e4264d27a09',
            'status': 'SUCCESS',
            'type': 'DIGITAL_CARD_ISSUE',
            'operation_type': 'INSERT',
            'operation_at': '2022-02-09T20:28:58.838783+00:00',
        },
        {
            'application_id': '7948e3a9-623c-4524-a390-9e4264d27a08',
            'status': 'CREATED',
            'type': 'DIGITAL_CARD_ISSUE',
            'operation_type': 'INSERT',
            'operation_at': '2022-02-08T20:28:58.838783+00:00',
        },
    ]


@pytest.mark.parametrize('url', [SUPPORT_HANDLE_URL, INTERNAL_HANDLE_URL])
async def test_get_applications_with_type_and_cursor(
        taxi_bank_applications, mockserver, access_control_mock, url,
):
    response = await taxi_bank_applications.post(
        url,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'uid': common.DEFAULT_YANDEX_UID,
                'buid': common.DEFAULT_YANDEX_BUID,
                'type': 'DIGITAL_CARD_ISSUE',
            },
            'limit': 2,
            'cursor': 'eyJjdXJzb3Jfa2V5Ijo2fQ==',
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert 'cursor' not in resp
    assert resp['applications'] == [
        {
            'application_id': '7948e3a9-623c-4524-a390-9e4264d27a05',
            'type': 'DIGITAL_CARD_ISSUE',
            'status': 'FAILED',
            'reason': 'error',
            'operation_type': 'INSERT',
            'operation_at': '2022-02-05T20:28:58.838783+00:00',
        },
    ]


@pytest.mark.parametrize(
    'app_status, count',
    [('CREATED', 1), ('PROCESSING', 2), ('FAILED', 6), ('SUCCESS', 6)],
)
@pytest.mark.parametrize('url', [SUPPORT_HANDLE_URL, INTERNAL_HANDLE_URL])
async def test_get_applications_with_status(
        taxi_bank_applications,
        mockserver,
        access_control_mock,
        app_status,
        count,
        url,
):
    response = await taxi_bank_applications.post(
        url,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'uid': common.DEFAULT_YANDEX_UID,
                'buid': common.DEFAULT_YANDEX_BUID,
                'status': app_status,
            },
            'limit': 200,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['applications']) == count
    assert 'cursor' not in resp


@pytest.mark.parametrize('url', [SUPPORT_HANDLE_URL, INTERNAL_HANDLE_URL])
async def test_get_applications_with_status_and_type(
        taxi_bank_applications, mockserver, access_control_mock, url,
):
    response = await taxi_bank_applications.post(
        url,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'uid': common.DEFAULT_YANDEX_UID,
                'buid': common.DEFAULT_YANDEX_BUID,
                'status': 'PROCESSING',
                'type': 'DIGITAL_CARD_ISSUE',
            },
            'limit': 200,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert 'cursor' not in resp
    assert resp['applications'] == [
        {
            'application_id': '7948e3a9-623c-4524-a390-9e4264d27a07',
            'type': 'DIGITAL_CARD_ISSUE',
            'status': 'PROCESSING',
            'operation_type': 'INSERT',
            'operation_at': '2022-02-07T20:28:58.838783+00:00',
        },
    ]


@pytest.mark.parametrize('url', [SUPPORT_HANDLE_URL, INTERNAL_HANDLE_URL])
async def test_get_applications_with_status_and_type_and_page_size(
        taxi_bank_applications, mockserver, access_control_mock, url,
):
    response = await taxi_bank_applications.post(
        url,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'uid': common.DEFAULT_YANDEX_UID,
                'buid': common.DEFAULT_YANDEX_BUID,
                'status': 'SUCCESS',
                'type': 'DIGITAL_CARD_ISSUE',
            },
            'limit': 1,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp['cursor'] == 'eyJjdXJzb3Jfa2V5Ijo5fQ=='
    assert resp['applications'] == [
        {
            'application_id': '7948e3a9-623c-4524-a390-9e4264d27a09',
            'type': 'DIGITAL_CARD_ISSUE',
            'status': 'SUCCESS',
            'operation_type': 'INSERT',
            'operation_at': '2022-02-09T20:28:58.838783+00:00',
        },
    ]


@pytest.mark.parametrize('url', [SUPPORT_HANDLE_URL, INTERNAL_HANDLE_URL])
async def test_get_applications_with_status_and_type_and_cursor(
        taxi_bank_applications, mockserver, access_control_mock, url,
):
    response = await taxi_bank_applications.post(
        url,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'uid': common.DEFAULT_YANDEX_UID,
                'buid': common.DEFAULT_YANDEX_BUID,
                'status': 'SUCCESS',
                'type': 'DIGITAL_CARD_ISSUE',
            },
            'limit': 1,
            'cursor': 'eyJjdXJzb3Jfa2V5Ijo5fQ==',
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert 'cursor' not in resp
    assert resp['applications'] == [
        {
            'application_id': '7948e3a9-623c-4524-a390-9e4264d27a06',
            'type': 'DIGITAL_CARD_ISSUE',
            'status': 'SUCCESS',
            'operation_type': 'INSERT',
            'operation_at': '2022-02-06T20:28:58.838783+00:00',
        },
    ]


@pytest.mark.parametrize('url', [SUPPORT_HANDLE_URL, INTERNAL_HANDLE_URL])
async def test_get_applications_with_date_from(
        taxi_bank_applications, mockserver, access_control_mock, url,
):
    response = await taxi_bank_applications.post(
        url,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'uid': common.DEFAULT_YANDEX_UID,
                'buid': common.DEFAULT_YANDEX_BUID,
                'date_from': '2022-02-07T00:00:00.0+00:00',
            },
            'limit': 200,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert 'cursor' not in resp
    assert len(resp['applications']) == 6
    first_app = {
        'application_id': '7948e3a9-623c-4524-a390-9e4264d27a11',
        'type': 'SIMPLIFIED_IDENTIFICATION',
        'status': (
            common.STATUS_CREATED
            if url == SUPPORT_HANDLE_URL
            else common.STATUS_FAILED
        ),
        'operation_type': 'INSERT',
        'operation_at': '2022-02-10T20:28:58.838783+00:00',
    }
    if url == INTERNAL_HANDLE_URL:
        first_app.update({'reason': 'error'})
    assert resp['applications'] == [
        first_app,
        {
            'application_id': '7948e3a9-623c-4524-a390-9e4264d22222',
            'type': 'KYC',
            'status': 'SUCCESS',
            'operation_type': 'INSERT',
            'operation_at': '2022-02-09T20:28:58.838783+00:00',
        },
        {
            'application_id': '7948e3a9-623c-4524-a390-9e4264d11111',
            'type': 'SPLIT_CARD_ISSUE',
            'status': 'SUCCESS',
            'operation_type': 'INSERT',
            'operation_at': '2022-02-09T20:28:58.838783+00:00',
        },
        {
            'application_id': '7948e3a9-623c-4524-a390-9e4264d27a09',
            'type': 'DIGITAL_CARD_ISSUE',
            'status': 'SUCCESS',
            'operation_type': 'INSERT',
            'operation_at': '2022-02-09T20:28:58.838783+00:00',
        },
        {
            'application_id': '7948e3a9-623c-4524-a390-9e4264d27a08',
            'operation_at': '2022-02-08T20:28:58.838783+00:00',
            'operation_type': 'INSERT',
            'status': 'CREATED',
            'type': 'DIGITAL_CARD_ISSUE',
        },
        {
            'application_id': '7948e3a9-623c-4524-a390-9e4264d27a07',
            'operation_at': '2022-02-07T20:28:58.838783+00:00',
            'operation_type': 'INSERT',
            'status': 'PROCESSING',
            'type': 'DIGITAL_CARD_ISSUE',
        },
    ]


@pytest.mark.parametrize('url', [SUPPORT_HANDLE_URL, INTERNAL_HANDLE_URL])
async def test_get_applications_with_date_to(
        taxi_bank_applications, mockserver, access_control_mock, url,
):
    response = await taxi_bank_applications.post(
        url,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'uid': common.DEFAULT_YANDEX_UID,
                'buid': common.DEFAULT_YANDEX_BUID,
                'date_to': '2022-02-02T00:00:00.0+00:00',
            },
            'limit': 200,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert 'cursor' not in resp
    assert resp['applications'] == [
        {
            'application_id': '7948e3a9-623c-4524-1111-9e4264d27a01',
            'operation_at': '2022-01-01T20:28:58.838783+00:00',
            'operation_type': 'INSERT',
            'reason': 'PROCESSING_FAILED',
            'status': 'FAILED',
            'type': 'CHANGE_NUMBER',
        },
        {
            'application_id': '7948e3a9-623c-4524-a390-9e4264d27000',
            'type': 'SIMPLIFIED_IDENTIFICATION_ESIA',
            'status': 'FAILED',
            'reason': 'error1' if url == SUPPORT_HANDLE_URL else 'error',
            'operation_type': 'INSERT',
            'operation_at': '2022-01-01T20:28:58.838783+00:00',
        },
        {
            'application_id': '7948e3a9-623c-4524-a390-9e4264d27a01',
            'type': 'REGISTRATION',
            'status': 'FAILED',
            'reason': 'error2' if url == SUPPORT_HANDLE_URL else 'error',
            'operation_type': 'INSERT',
            'operation_at': '2022-02-01T20:28:58.838783+00:00',
        },
    ]


@pytest.mark.parametrize('url', [SUPPORT_HANDLE_URL, INTERNAL_HANDLE_URL])
async def test_get_applications_with_date_from_and_to(
        taxi_bank_applications, mockserver, access_control_mock, url,
):
    response = await taxi_bank_applications.post(
        url,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'uid': common.DEFAULT_YANDEX_UID,
                'buid': common.DEFAULT_YANDEX_BUID,
                'date_from': '2022-02-07T00:00:00.0+00:00',
                'date_to': '2022-02-08T00:00:00.0+00:00',
            },
            'limit': 200,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert 'cursor' not in resp
    assert resp['applications'] == [
        {
            'application_id': '7948e3a9-623c-4524-a390-9e4264d27a07',
            'type': 'DIGITAL_CARD_ISSUE',
            'status': 'PROCESSING',
            'operation_type': 'INSERT',
            'operation_at': '2022-02-07T20:28:58.838783+00:00',
        },
    ]


@pytest.mark.parametrize('url', [SUPPORT_HANDLE_URL, INTERNAL_HANDLE_URL])
async def test_get_applications_with_type_and_date_from_and_to(
        taxi_bank_applications, mockserver, access_control_mock, url,
):
    response = await taxi_bank_applications.post(
        url,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'uid': common.DEFAULT_YANDEX_UID,
                'buid': common.DEFAULT_YANDEX_BUID,
                'type': 'DIGITAL_CARD_ISSUE',
                'date_from': '2022-02-01T00:00:00.0+00:00',
                'date_to': '2022-02-06T00:00:00.0+00:00',
            },
            'limit': 200,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert 'cursor' not in resp
    assert resp['applications'] == [
        {
            'application_id': '7948e3a9-623c-4524-a390-9e4264d27a05',
            'type': 'DIGITAL_CARD_ISSUE',
            'status': 'FAILED',
            'reason': 'error',
            'operation_type': 'INSERT',
            'operation_at': '2022-02-05T20:28:58.838783+00:00',
        },
    ]


@pytest.mark.parametrize('url', [SUPPORT_HANDLE_URL, INTERNAL_HANDLE_URL])
async def test_get_applications_with_status_and_date_from_and_to(
        taxi_bank_applications, mockserver, access_control_mock, url,
):
    response = await taxi_bank_applications.post(
        url,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'uid': common.DEFAULT_YANDEX_UID,
                'buid': common.DEFAULT_YANDEX_BUID,
                'status': 'FAILED',
                'date_from': '2022-02-03T00:00:00.0+00:00',
                'date_to': '2022-02-09T00:00:00.0+00:00',
            },
            'limit': 200,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert 'cursor' not in resp
    assert resp['applications'] == [
        {
            'application_id': '7948e3a9-623c-4524-a390-9e4264d27a05',
            'type': 'DIGITAL_CARD_ISSUE',
            'status': 'FAILED',
            'reason': 'error',
            'operation_type': 'INSERT',
            'operation_at': '2022-02-05T20:28:58.838783+00:00',
        },
        {
            'application_id': '7948e3a9-623c-4524-a390-9e4264d27a03',
            'type': 'SIMPLIFIED_IDENTIFICATION',
            'status': 'FAILED',
            'reason': 'error1' if url == SUPPORT_HANDLE_URL else 'error',
            'operation_type': 'INSERT',
            'operation_at': '2022-02-03T20:28:58.838783+00:00',
        },
    ]


async def test_get_applications_with_status_and_type_and_date_from_and_to(
        taxi_bank_applications, mockserver, access_control_mock,
):
    response = await taxi_bank_applications.post(
        SUPPORT_HANDLE_URL,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'uid': common.DEFAULT_YANDEX_UID,
                'buid': common.DEFAULT_YANDEX_BUID,
                'status': 'FAILED',
                'type': 'DIGITAL_CARD_ISSUE',
                'date_from': '2022-02-01T00:00:00.0+00:00',
                'date_to': '2022-02-09T00:00:00.0+00:00',
            },
            'limit': 200,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert 'cursor' not in resp
    assert resp['applications'] == [
        {
            'application_id': '7948e3a9-623c-4524-a390-9e4264d27a05',
            'type': 'DIGITAL_CARD_ISSUE',
            'status': 'FAILED',
            'reason': 'error',
            'operation_type': 'INSERT',
            'operation_at': '2022-02-05T20:28:58.838783+00:00',
        },
    ]
    assert access_control_mock.handler_path == SUPPORT_HANDLE_URL


async def test_get_applications_access_deny(
        taxi_bank_applications, mockserver, access_control_mock,
):
    response = await taxi_bank_applications.post(
        SUPPORT_HANDLE_URL,
        headers=common.get_support_headers(''),
        json={
            'filters': {
                'uid': common.DEFAULT_YANDEX_UID,
                'buid': common.DEFAULT_YANDEX_BUID,
            },
            'limit': 200,
        },
    )
    assert response.status_code == 401
    assert access_control_mock.apply_policies_handler.times_called == 1


@pytest.mark.parametrize('uid', [common.DEFAULT_YANDEX_UID, None])
@pytest.mark.parametrize('url', [SUPPORT_HANDLE_URL, INTERNAL_HANDLE_URL])
async def test_get_applications_application_id_filters(
        taxi_bank_applications, mockserver, access_control_mock, url, uid,
):
    application_id = '7948e3a9-623c-4524-a390-9e4264d27a01'
    filters = {'application_id': application_id}
    if uid is not None:
        filters.update({'uid': uid})
    response = await taxi_bank_applications.post(
        url,
        headers=common.get_support_headers(),
        json={'filters': filters, 'limit': 100},
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['applications']) == 1
    assert resp['applications'][0]['application_id'] == application_id


@pytest.mark.parametrize('url', [SUPPORT_HANDLE_URL, INTERNAL_HANDLE_URL])
async def test_get_applications_application_id_filters_different_statues(
        taxi_bank_applications, mockserver, access_control_mock, url,
):
    application_id = '7948e3a9-623c-4524-a390-9e4264d27a11'
    response = await taxi_bank_applications.post(
        url,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'buid': common.DEFAULT_YANDEX_BUID,
                'application_id': application_id,
            },
            'limit': 100,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['applications']) == 1
    assert resp['applications'][0]['application_id'] == application_id
    if url == SUPPORT_HANDLE_URL:
        assert resp['applications'][0]['status'] == common.STATUS_CREATED
    else:
        assert resp['applications'][0]['status'] == common.STATUS_FAILED


@pytest.mark.parametrize('url', [SUPPORT_HANDLE_URL, INTERNAL_HANDLE_URL])
@pytest.mark.parametrize(
    'user_id_type, user_id, expected_size',
    [
        ('buid', common.DEFAULT_YANDEX_BUID, 13),
        ('uid', common.DEFAULT_YANDEX_UID, 2),
    ],
)
async def test_get_applications_by_single_user_type(
        taxi_bank_applications,
        access_control_mock,
        url,
        user_id_type,
        user_id,
        expected_size,
):
    filters = {user_id_type: user_id}
    response = await taxi_bank_applications.post(
        url,
        headers=common.get_support_headers(),
        json={'filters': filters, 'limit': 100},
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['applications']) == expected_size


async def test_support_get_applications_multiple_cursor_check(
        taxi_bank_applications, mockserver, access_control_mock,
):
    response = await taxi_bank_applications.post(
        SUPPORT_HANDLE_URL,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'uid': common.DEFAULT_YANDEX_UID,
                'buid': common.DEFAULT_YANDEX_BUID,
            },
            'limit': 100,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert 'cursor' not in resp
    assert (
        [application['application_id'] for application in resp['applications']]
        == [
            '3ac0a2cc-637e-4c50-b7c3-87d1e641cb9c',
            '7948e3a9-623c-4524-1111-9e4264d27a01',
            '7948e3a9-623c-4524-a390-9e4264d27000',
            '7948e3a9-623c-4524-a390-9e4264d27a11',
            '7948e3a9-623c-4524-a390-9e4264d22222',
            '7948e3a9-623c-4524-a390-9e4264d11111',
            '7948e3a9-623c-4524-a390-9e4264d27a09',
            '7948e3a9-623c-4524-a390-9e4264d27a08',
            '7948e3a9-623c-4524-a390-9e4264d27a07',
            '7948e3a9-623c-4524-a390-9e4264d27a06',
            '7948e3a9-623c-4524-a390-9e4264d27a05',
            '7948e3a9-623c-4524-a390-9e4264d27a04',
            '7948e3a9-623c-4524-a390-9e4264d27a03',
            '7948e3a9-623c-4524-a390-9e4264d27a02',
            '7948e3a9-623c-4524-a390-9e4264d27a01',
        ]
    )

    response = await taxi_bank_applications.post(
        SUPPORT_HANDLE_URL,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'uid': common.DEFAULT_YANDEX_UID,
                'buid': common.DEFAULT_YANDEX_BUID,
            },
            'limit': 2,
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp['cursor'] == 'eyJjdXJzb3Jfa2V5IjoxNH0='
    assert len(resp['applications']) == 2
    assert (
        [application['application_id'] for application in resp['applications']]
        == [
            '3ac0a2cc-637e-4c50-b7c3-87d1e641cb9c',
            '7948e3a9-623c-4524-1111-9e4264d27a01',
        ]
    )

    response = await taxi_bank_applications.post(
        SUPPORT_HANDLE_URL,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'uid': common.DEFAULT_YANDEX_UID,
                'buid': common.DEFAULT_YANDEX_BUID,
            },
            'limit': 2,
            'cursor': 'eyJjdXJzb3Jfa2V5IjoxM30=',
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp['cursor'] == 'eyJjdXJzb3Jfa2V5IjoxMX0='
    assert len(resp['applications']) == 2
    assert (
        [application['application_id'] for application in resp['applications']]
        == [
            '7948e3a9-623c-4524-a390-9e4264d27a11',
            '7948e3a9-623c-4524-a390-9e4264d22222',
        ]
    )

    response = await taxi_bank_applications.post(
        SUPPORT_HANDLE_URL,
        headers=common.get_support_headers(),
        json={
            'filters': {
                'uid': common.DEFAULT_YANDEX_UID,
                'buid': common.DEFAULT_YANDEX_BUID,
            },
            'limit': 9,
            'cursor': resp['cursor'],
        },
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp['cursor'] == 'eyJjdXJzb3Jfa2V5IjoyfQ=='
    assert len(resp['applications']) == 9
    assert (
        [application['application_id'] for application in resp['applications']]
        == [
            '7948e3a9-623c-4524-a390-9e4264d11111',
            '7948e3a9-623c-4524-a390-9e4264d27a09',
            '7948e3a9-623c-4524-a390-9e4264d27a08',
            '7948e3a9-623c-4524-a390-9e4264d27a07',
            '7948e3a9-623c-4524-a390-9e4264d27a06',
            '7948e3a9-623c-4524-a390-9e4264d27a05',
            '7948e3a9-623c-4524-a390-9e4264d27a04',
            '7948e3a9-623c-4524-a390-9e4264d27a03',
            '7948e3a9-623c-4524-a390-9e4264d27a02',
        ]
    )
