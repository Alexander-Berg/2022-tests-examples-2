# pylint:disable=too-many-arguments, redefined-outer-name,unused-variable
import http

import pytest

REQUEST_DATA = {
    'request_id': 'dummy_request_id',
    'db': '1d1c48855a1d4b00b37f8096ea8f4b5d',
    'message': {'text': 'test message'},
}


@pytest.fixture
def mock_support_chat(monkeypatch, taxi_driver_support_app):
    async def _dummy_create_chat(*args, **kwargs):
        return {'id': 'dummy_chat_id'}

    async def __dummy_attach_file(*args, **kwargs):
        return {'attachement_id': 'test_attachment'}

    monkeypatch.setattr(
        taxi_driver_support_app.support_chat_client,
        'create_chat',
        _dummy_create_chat,
    )
    monkeypatch.setattr(
        taxi_driver_support_app.support_chat_client,
        'attach_file',
        __dummy_attach_file,
    )


@pytest.fixture
def mock_cookie_generate(monkeypatch):
    pass


async def test_authorize(
        mock_driver_session,
        mock_support_chat,
        mock_driver_profiles,
        mock_personal,
        taxi_driver_support_client,
        patch_additional_meta,
):
    additional_meta_calls = patch_additional_meta()
    session = 'some_driver_session'
    request_data = REQUEST_DATA

    response = await taxi_driver_support_client.post(
        '/v1/support_chat/add_message', json=request_data,
    )
    assert response.status == http.HTTPStatus.UNAUTHORIZED

    headers = {'Authorization': 'test_session'}
    response = await taxi_driver_support_client.post(
        '/v1/support_chat/add_message', json=request_data, headers=headers,
    )
    assert response.status == http.HTTPStatus.UNAUTHORIZED

    headers = {'Authorization': session}
    response = await taxi_driver_support_client.post(
        '/v1/support_chat/add_message', json=request_data, headers=headers,
    )
    assert response.status == http.HTTPStatus.OK
    assert additional_meta_calls


@pytest.mark.config(DRIVER_SUPPORT_ALLOWED_FILE_TYPES=['text/plain'])
async def test_authorize_db_query(
        mock_driver_session,
        mock_support_chat,
        taxi_driver_support_client,
        mock_driver_profiles,
        mock_personal,
):
    session = 'some_driver_session'
    request_data = REQUEST_DATA
    db_id = request_data['db']

    headers = {'Authorization': session}
    response = await taxi_driver_support_client.post(
        '/v1/support_chat/attach_file',
        data=b'test_data',
        headers=headers,
        params={'idempotency_token': 'test_token', 'filename': 'filename'},
    )
    assert response.status == http.HTTPStatus.BAD_REQUEST

    headers = {'Authorization': session}
    response = await taxi_driver_support_client.post(
        '/v1/support_chat/attach_file',
        data=b'test_data',
        headers=headers,
        params={
            'db': db_id,
            'idempotency_token': 'test_token',
            'filename': 'filename',
        },
    )
    assert response.status == http.HTTPStatus.OK


@pytest.mark.parametrize(
    'user_agent,client_id',
    [
        ('Taximeter 8.89 (550)', 'taximeter'),
        ('Taximeter-Uber 8.89 (550)', 'uberdriver'),
        ('Taximeter-Vezet 8.89 (550)', 'vezet'),
        ('Mozilla 4.0 Android (SAMSUNG-PWH)', 'taximeter'),
        ('', 'taximeter'),
        (None, 'taximeter'),
    ],
)
async def test_authorize_client_id(
        mock_driver_session,
        mock_support_chat,
        mock_driver_profiles,
        mock_personal,
        taxi_driver_support_client,
        patch_additional_meta,
        user_agent,
        client_id,
):
    patch_additional_meta()
    headers = {'Authorization': 'some_driver_session'}
    if user_agent:
        headers['User-Agent'] = user_agent
    response = await taxi_driver_support_client.post(
        '/v1/support_chat/add_message', json=REQUEST_DATA, headers=headers,
    )

    calls = mock_driver_session.calls
    assert calls[0]['client_id'] == client_id
    assert response.status == http.HTTPStatus.OK
