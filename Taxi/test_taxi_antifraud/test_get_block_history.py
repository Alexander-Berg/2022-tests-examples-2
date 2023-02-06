import pytest


async def test_block_history_bad_request(web_app_client):
    response = await web_app_client.post('/v1/block_history', json={})
    assert response.status == 400


@pytest.mark.parametrize(
    'user_id,phone_id,device_id',
    [
        ('user_id_not_found', None, None),
        ('user_id_not_found', 'phone_id_not_found', 'device_id_not_found'),
    ],
)
async def test_block_history_raws_not_found(
        web_app_client, user_id, phone_id, device_id,
):
    response = await web_app_client.post(
        '/v1/block_history',
        json={
            'user_id': user_id,
            'phone_id': phone_id,
            'device_id': device_id,
        },
    )
    assert response.status == 200
    json = await response.json()

    def _get_response():
        _response = dict()
        _dict = {
            'current_state': {
                'common': {'blocked': False},
                'multiorder': {'blocked': False},
            },
            'history': [],
        }
        if user_id is not None:
            _response['user_id'] = _dict
        if phone_id is not None:
            _response['phone_id'] = _dict
        if device_id is not None:
            _response['device_id'] = _dict
        return _response

    assert json == _get_response()


@pytest.mark.parametrize(
    'user_id,phone_id,device_id,expected',
    [
        (
            'user',
            'phone',
            'device',
            {
                'user_id': {
                    'current_state': {
                        'common': {'blocked': False},
                        'multiorder': {'blocked': False},
                    },
                    'history': [
                        {
                            'multiorder': True,
                            'event_type': 'block',
                            'time': '2019-11-20T12:05:39+03:00',
                            'blocked_till': '2019-12-20T12:05:39+03:00',
                            'reason': 'some_reason',
                            'initiator': 'Kirill',
                            'ticket': 'Some ticket',
                            'support_template_reason': 'support_blocking',
                        },
                    ],
                },
                'phone_id': {
                    'current_state': {
                        'common': {'blocked': True},
                        'multiorder': {'blocked': False},
                    },
                    'history': [
                        {
                            'multiorder': False,
                            'event_type': 'block',
                            'time': '2019-11-26T12:05:39+03:00',
                            'blocked_till': '2019-12-29T12:05:39+03:00',
                            'reason': 'some_reason',
                            'initiator': 'Kirill',
                            'ticket': 'Some ticket',
                        },
                        {
                            'multiorder': True,
                            'event_type': 'unblock',
                            'time': '2019-11-20T12:05:39+03:00',
                            'reason': 'some_reason',
                            'initiator': 'Kirill',
                            'ticket': 'Some ticket',
                        },
                    ],
                },
                'device_id': {
                    'current_state': {
                        'common': {'blocked': False},
                        'multiorder': {'blocked': True},
                    },
                    'history': [],
                },
            },
        ),
    ],
)
@pytest.mark.now('2019-12-19T14:00:00Z')
async def test_block_history(
        web_app_client, user_id, phone_id, device_id, expected,
):
    response = await web_app_client.post(
        '/v1/block_history',
        json={
            'user_id': user_id,
            'phone_id': phone_id,
            'device_id': device_id,
        },
    )
    assert response.status == 200
    json = await response.json()

    assert json == expected


@pytest.mark.parametrize(
    'body,expected',
    [
        (
            {'phone_personal': {'id': '1232456', 'type': 'yandex'}},
            {
                'phone_personal': {
                    'current_state': {
                        'common': {'blocked': False},
                        'multiorder': {'blocked': False},
                    },
                    'history': [],
                },
            },
        ),
    ],
)
@pytest.mark.now('2019-12-19T14:00:00Z')
async def test_block_history_personal_phone_id(
        web_app_client, patch, body, expected,
):
    @patch('taxi_antifraud.api.get_block_history._get_properties_list')
    async def _get_properties_patch(_body, context, log_extra):
        assert _body.phone_personal.id == body['phone_personal']['id']
        assert _body.phone_personal.type == body['phone_personal']['type']
        return [('phone_personal', '1236')]

    response = await web_app_client.post('/v1/block_history', json=body)
    assert response.status == 200
    json = await response.json()

    assert json == expected


@pytest.mark.parametrize(
    'body,expected',
    [
        (
            {'phone_personal': {'id': '1232456', 'type': 'yandex'}},
            {
                'phone_personal': {
                    'current_state': {
                        'common': {'blocked': True},
                        'multiorder': {'blocked': False},
                    },
                    'history': [
                        {
                            'multiorder': False,
                            'event_type': 'block',
                            'time': '2019-11-26T12:05:39+03:00',
                            'blocked_till': '2019-12-29T12:05:39+03:00',
                            'reason': 'some_reason',
                            'initiator': 'Kirill',
                            'ticket': 'Some ticket',
                        },
                        {
                            'multiorder': True,
                            'event_type': 'unblock',
                            'time': '2019-11-20T12:05:39+03:00',
                            'reason': 'some_reason',
                            'initiator': 'Kirill',
                            'ticket': 'Some ticket',
                        },
                    ],
                },
            },
        ),
    ],
)
@pytest.mark.now('2019-12-19T14:00:00Z')
async def test_block_history_personal_phone_id_blocked(
        web_app_client, patch, body, expected,
):
    @patch('taxi_antifraud.api.get_block_history._get_properties_list')
    async def _get_properties_patch(_body, context, log_extra):
        return [('phone_personal', 'phone')]

    response = await web_app_client.post('/v1/block_history', json=body)
    assert response.status == 200
    json = await response.json()

    assert json == expected
