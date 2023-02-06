# pylint:disable=too-many-arguments, redefined-outer-name
# pylint: disable=too-many-lines, unused-variable

import pytest


UNIQUE_DRIVER_ID = '5bc702f995572fa0df26e0e2'


DAP_APP_HEADERS = {
    'X-Request-Platform': 'android',
    'X-Request-Application-Version': '9.61 (1234)',
}


@pytest.fixture
def mock_get_order_by_id(taxi_driver_support_app, monkeypatch, mock):
    @mock
    async def _dummy_get_order_by_id(*args, **kwargs):
        return {'_id': 'some_order_id'}

    monkeypatch.setattr(
        taxi_driver_support_app.archive_api_client,
        'get_order_by_id',
        _dummy_get_order_by_id,
    )
    return _dummy_get_order_by_id


@pytest.fixture
def mock_qc_xservice_blocked(mockserver, load_json):
    @mockserver.json_handler('/qc_xservice/utils/qc/driver/exams/retrieve')
    def mock_qc_exams(request, *args, **kwargs):
        park_id = request.json['query']['park']['id']
        is_blocked = park_id == '8b61fac2f9d143afae2dca5592d7d14c'
        return {'dkvu_exam': {'summary': {'is_blocked': is_blocked}}}


@pytest.fixture
def mock_parks_owner(mockserver, load_json):
    def _get_park(park_id, parks):
        for park in parks:
            if park['id'] == park_id:
                return park
        return {}

    parks = load_json('parks.json')

    @mockserver.json_handler('/parks/driver-profiles/list')
    def _dummy_profiles_url(request):
        park_id = request.json['query']['park']['id']
        return {'parks': [_get_park(park_id, parks)], 'total': 1}


@pytest.mark.parametrize(
    'park_id,session,headers,message,metadata,expected_create_data',
    [
        (
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_session',
            {},
            {'text': 'test message'},
            None,
            {
                'owner_id': UNIQUE_DRIVER_ID,
                'owner_role': 'driver',
                'message_text': 'test message',
                'metadata': {
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'en',
                    'owner_type': 'unique_driver',
                },
                'message_metadata': None,
                'request_id': 'dummy_request_id',
                'message_sender_id': UNIQUE_DRIVER_ID,
                'message_sender_role': 'driver',
                'platform': 'taximeter',
            },
        ),
        (
            '1d1c48855a1d4b00b37f8096ea8f4b5d',
            'some_driver_session',
            {},
            {'text': 'test message'},
            None,
            {
                'owner_id': 'some_driver_uuid',
                'owner_role': 'driver',
                'message_text': 'test message',
                'metadata': {
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'db': '1d1c48855a1d4b00b37f8096ea8f4b5d',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'en',
                    'owner_type': 'driver_uuid',
                },
                'message_metadata': None,
                'request_id': 'dummy_request_id',
                'message_sender_id': 'some_driver_uuid',
                'message_sender_role': 'driver',
                'platform': 'taximeter',
            },
        ),
        (
            'ac3aabfa247d485d8ad612fd2dc2c09d',
            'some_driver_session',
            {},
            {'text': 'test message'},
            None,
            {
                'owner_id': 'some_driver_uuid',
                'owner_role': 'driver',
                'message_text': 'test message',
                'metadata': {
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'db': 'ac3aabfa247d485d8ad612fd2dc2c09d',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'en',
                    'owner_type': 'driver_uuid',
                },
                'message_metadata': None,
                'request_id': 'dummy_request_id',
                'message_sender_id': 'some_driver_uuid',
                'message_sender_role': 'driver',
                'platform': 'taximeter',
            },
        ),
        (
            '8b61fac2f9d143afae2dca5592d7d14c',
            'some_driver_session',
            {},
            {'text': 'test message'},
            None,
            {
                'owner_id': 'some_driver_uuid',
                'owner_role': 'driver',
                'message_text': 'test message',
                'metadata': {
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'db': '8b61fac2f9d143afae2dca5592d7d14c',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'en',
                    'owner_type': 'driver_uuid',
                },
                'message_metadata': None,
                'request_id': 'dummy_request_id',
                'message_sender_id': 'some_driver_uuid',
                'message_sender_role': 'driver',
                'platform': 'taximeter',
            },
        ),
    ],
)
async def test_add_message(
        monkeypatch,
        mock,
        mock_stq_put,
        mock_driver_session,
        mock_get_order_by_id,
        mock_driver_profiles,
        mock_qc_xservice_blocked,
        mock_personal,
        mock_parks_owner,
        taxi_driver_support_client,
        taxi_driver_support_app,
        park_id,
        session,
        headers,
        message,
        metadata,
        expected_create_data,
        patch_additional_meta,
):
    # pylint: disable=too-many-locals
    additional_meta_calls = patch_additional_meta(
        metadata={'park_country': 'rus'},
    )

    @mock
    async def _dummy_create_chat(*args, **kwargs):
        data = {'id': 'dummy_chat_id', 'newest_message_id': 'new_message_id'}
        return data

    monkeypatch.setattr(
        taxi_driver_support_app.support_chat_client,
        'create_chat',
        _dummy_create_chat,
    )

    request_data = {'request_id': 'dummy_request_id', 'db': park_id}
    if message:
        request_data['message'] = message
    headers.update({'Authorization': session, 'Accept-Language': 'en'})
    if metadata is not None:
        request_data['metadata'] = metadata

    response = await taxi_driver_support_client.post(
        '/v1/support_chat/add_message', json=request_data, headers=headers,
    )
    assert response.status == 200
    assert additional_meta_calls

    create_chat_calls = _dummy_create_chat.calls
    support_chat_call = create_chat_calls[0]
    for key, value in expected_create_data.items():
        assert support_chat_call['kwargs'][key] == value


# This test for new endpoints behind dap
@pytest.mark.parametrize(
    'park_id,driver_profile_id,headers,message,expected_create_data',
    [
        (
            '59de5222293145d09d31cd1604f8f656',
            'some_driver_uuid',
            {},
            {'text': 'test message'},
            {
                'owner_id': UNIQUE_DRIVER_ID,
                'owner_role': 'driver',
                'message_text': 'test message',
                'metadata': {
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'db': '59de5222293145d09d31cd1604f8f656',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'en',
                    'owner_type': 'unique_driver',
                },
                'message_metadata': None,
                'request_id': 'dummy_request_id',
                'message_sender_id': UNIQUE_DRIVER_ID,
                'message_sender_role': 'driver',
                'platform': 'taximeter',
            },
        ),
        (
            '1d1c48855a1d4b00b37f8096ea8f4b5d',
            'some_driver_uuid',
            {},
            {'text': 'test message'},
            {
                'owner_id': 'some_driver_uuid',
                'owner_role': 'driver',
                'message_text': 'test message',
                'metadata': {
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'db': '1d1c48855a1d4b00b37f8096ea8f4b5d',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'en',
                    'owner_type': 'driver_uuid',
                },
                'message_metadata': None,
                'request_id': 'dummy_request_id',
                'message_sender_id': 'some_driver_uuid',
                'message_sender_role': 'driver',
                'platform': 'taximeter',
            },
        ),
        (
            'ac3aabfa247d485d8ad612fd2dc2c09d',
            'some_driver_uuid',
            {},
            {'text': 'test message'},
            {
                'owner_id': 'some_driver_uuid',
                'owner_role': 'driver',
                'message_text': 'test message',
                'metadata': {
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'db': 'ac3aabfa247d485d8ad612fd2dc2c09d',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'en',
                    'owner_type': 'driver_uuid',
                },
                'message_metadata': None,
                'request_id': 'dummy_request_id',
                'message_sender_id': 'some_driver_uuid',
                'message_sender_role': 'driver',
                'platform': 'taximeter',
            },
        ),
        (
            '8b61fac2f9d143afae2dca5592d7d14c',
            'some_driver_uuid',
            {},
            {'text': 'test message'},
            {
                'owner_id': 'some_driver_uuid',
                'owner_role': 'driver',
                'message_text': 'test message',
                'metadata': {
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'db': '8b61fac2f9d143afae2dca5592d7d14c',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'en',
                    'owner_type': 'driver_uuid',
                },
                'message_metadata': None,
                'request_id': 'dummy_request_id',
                'message_sender_id': 'some_driver_uuid',
                'message_sender_role': 'driver',
                'platform': 'taximeter',
            },
        ),
    ],
)
async def test_add_message_new(
        monkeypatch,
        mock,
        mock_stq_put,
        mock_get_order_by_id,
        mock_driver_profiles,
        mock_personal,
        mock_qc_xservice_blocked,
        mock_parks_owner,
        taxi_driver_support_client,
        taxi_driver_support_app,
        park_id,
        driver_profile_id,
        headers,
        message,
        expected_create_data,
        patch_additional_meta,
):
    # pylint: disable=too-many-locals
    additional_meta_calls = patch_additional_meta(
        metadata={'park_country': 'rus'},
    )

    @mock
    async def _dummy_create_chat(*args, **kwargs):
        data = {'id': 'dummy_chat_id', 'newest_message_id': 'new_message_id'}
        return data

    monkeypatch.setattr(
        taxi_driver_support_app.support_chat_client,
        'create_chat',
        _dummy_create_chat,
    )

    request_data = {'request_id': 'dummy_request_id'}
    headers['Accept-Language'] = 'en'
    headers.update(DAP_APP_HEADERS)
    cookies = {}
    if park_id:
        headers['X-YaTaxi-Park-Id'] = park_id
    if driver_profile_id:
        headers['X-YaTaxi-Driver-Profile-Id'] = driver_profile_id
    if message:
        request_data['message'] = message

    await taxi_driver_support_client.post(
        '/driver/v1/driver-support/v1/support_chat/add_message',
        headers=headers,
        cookies=cookies,
        json=request_data,
    )

    assert additional_meta_calls

    create_chat_calls = _dummy_create_chat.calls
    support_chat_call = create_chat_calls[0]
    for key, value in expected_create_data.items():
        assert support_chat_call['kwargs'][key] == value


@pytest.mark.config(DRIVER_SUPPORT_USE_UUID_AS_OWNER=False)
@pytest.mark.parametrize(
    'park_id,session,headers,message,metadata,expected_create_data',
    [
        (
            '1d1c48855a1d4b00b37f8096ea8f4b5d',
            'some_driver_session',
            {},
            {'text': 'test message'},
            None,
            {
                'owner_id': UNIQUE_DRIVER_ID,
                'owner_role': 'driver',
                'message_text': 'test message',
                'metadata': {
                    'user_application': 'taximeter',
                    'user_country': 'rus',
                    'db': '1d1c48855a1d4b00b37f8096ea8f4b5d',
                    'driver_uuid': 'some_driver_uuid',
                    'user_locale': 'en',
                    'owner_type': 'unique_driver',
                },
                'message_metadata': None,
                'request_id': 'dummy_request_id',
                'message_sender_id': UNIQUE_DRIVER_ID,
                'message_sender_role': 'driver',
                'platform': 'taximeter',
            },
        ),
    ],
)
async def test_add_message_old_way(
        monkeypatch,
        mock,
        mock_stq_put,
        mock_driver_session,
        mock_get_order_by_id,
        mock_driver_profiles,
        mock_qc_xservice_blocked,
        mock_personal,
        mock_parks_owner,
        taxi_driver_support_client,
        taxi_driver_support_app,
        park_id,
        session,
        headers,
        message,
        metadata,
        expected_create_data,
):
    @mock
    async def _dummy_create_chat(*args, **kwargs):
        data = {'id': 'dummy_chat_id', 'newest_message_id': 'new_message_id'}
        return data

    monkeypatch.setattr(
        taxi_driver_support_app.support_chat_client,
        'create_chat',
        _dummy_create_chat,
    )

    request_data = {'request_id': 'dummy_request_id', 'db': park_id}
    if message:
        request_data['message'] = message
    headers.update({'Authorization': session, 'Accept-Language': 'en'})
    if metadata is not None:
        request_data['metadata'] = metadata

    response = await taxi_driver_support_client.post(
        '/v1/support_chat/add_message', json=request_data, headers=headers,
    )
    assert response.status == 200

    create_chat_calls = _dummy_create_chat.calls
    support_chat_call = create_chat_calls[0]
    for key, value in expected_create_data.items():
        assert support_chat_call['kwargs'][key] == value
