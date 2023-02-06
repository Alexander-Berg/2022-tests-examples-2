async def test_set_pickup_status_empty(
        mockserver,
        taxi_eats_restapp_places,
        get_pickup_statuses,
        mock_authorizer_allowed,
):
    @mockserver.json_handler('/client-notify/v1/push')
    def client_notify_handler(data):
        return {'notification_id': '123123'}

    response = await taxi_eats_restapp_places.post(
        '/internal/places/v1/pickup/status', json={'places': []},
    )
    assert response.status_code == 204

    statuses = get_pickup_statuses()
    assert not statuses

    response_status = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/pickup/status?place_ids=111,222',
        headers={'X-YaEda-PartnerId': '9999'},
    )
    assert response_status.status_code == 200

    assert response_status.json() == {'places': []}

    assert client_notify_handler.times_called == 0


async def test_set_pickup_status_happy_path(
        mock_authorizer_allowed,
        stq,
        mock_restapp_authorizer,
        mockserver,
        taxi_eats_restapp_places,
        get_pickup_status_by_place_id,
        get_pickup_statuses,
        pgsql,
):
    @mockserver.json_handler('/client-notify/v1/push')
    def client_notify_handler(data):
        return {'notification_id': '123123'}

    await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/pickup/enable',
        json={'place_ids': [111, 222]},
        headers={'X-YaEda-PartnerId': '9999'},
    )
    assert stq.eats_restapp_places_pickup.times_called == 1
    response = await taxi_eats_restapp_places.post(
        '/internal/places/v1/pickup/status',
        json={
            'places': [
                {
                    'place_id': 111,
                    'pickup_enabled': False,
                    'place_commission': {'percent': 15.7},
                    'pickup_mode': 'self_allowed',
                },
                {
                    'place_id': 222,
                    'pickup_enabled': False,
                    'place_commission': {'percent': 15.8},
                    'pickup_mode': 'self_allowed',
                },
            ],
        },
    )
    assert response.status_code == 204
    statuses = get_pickup_statuses()
    assert len(statuses) == 2

    assert statuses[0]['place_id'] == 111
    assert statuses[0]['place_delivery_zone_id'] is None
    assert statuses[0]['place_delivery_zone_enabled'] is False
    assert statuses[0]['place_commission_value'] == 15.7
    assert statuses[0]['pickup_started'] is None
    assert statuses[0]['pickup_enabled'] is False
    assert statuses[0]['pickup_mode'] == 'self_allowed'
    assert statuses[0]['created_at']
    assert statuses[0]['updated_at']
    assert statuses[0]['in_process'] is False

    assert statuses[1]['place_id'] == 222
    assert statuses[1]['place_delivery_zone_id'] is None
    assert statuses[1]['place_delivery_zone_enabled'] is False
    assert statuses[1]['place_commission_value'] == 15.8
    assert statuses[1]['pickup_started'] is None
    assert statuses[1]['pickup_enabled'] is False
    assert statuses[1]['pickup_mode'] == 'self_allowed'
    assert statuses[1]['created_at']
    assert statuses[1]['updated_at']
    assert statuses[1]['in_process'] is False

    response_status = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/pickup/status?place_ids=111,222',
        headers={'X-YaEda-PartnerId': '9999'},
    )
    assert response_status.status_code == 200

    assert response_status.json() == {
        'places': [
            {
                'status': 'available',
                'commission': {'percent': 15.7},
                'place_id': 111,
            },
            {
                'status': 'available',
                'commission': {'percent': 15.8},
                'place_id': 222,
            },
        ],
    }

    cursor = pgsql['eats_restapp_places'].cursor()
    cursor.execute(
        'INSERT INTO eats_restapp_places.pickup_status (place_id,'
        'place_delivery_zone_id,'
        'place_delivery_zone_enabled,'
        'place_commission_value,'
        'pickup_started,'
        'pickup_enabled,'
        'pickup_mode,'
        'in_process) '
        'VALUES '
        '(333,NULL,false,15.2,NULL,true,'
        '\'self_allowed\'::eats_restapp_places.pickup_mode, true);',
    )

    response_status = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/pickup/status?place_ids=333',
        headers={'X-YaEda-PartnerId': '9999'},
    )

    assert response_status.status_code == 200

    assert response_status.json() == {
        'places': [
            {
                'status': 'disabled',
                'commission': {'percent': 15.2},
                'place_id': 333,
            },
        ],
    }

    assert client_notify_handler.times_called == 2


async def test_set_pickup_status_update(
        stq,
        mock_restapp_authorizer,
        mockserver,
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        get_pickup_status_by_place_id,
        get_pickup_statuses,
):
    @mockserver.json_handler('/client-notify/v1/push')
    def client_notify_handler(data):
        return {'notification_id': '123123'}

    await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/pickup/enable',
        json={'place_ids': [111, 222]},
        headers={'X-YaEda-PartnerId': '9999'},
    )
    assert stq.eats_restapp_places_pickup.times_called == 1

    response = await taxi_eats_restapp_places.post(
        '/internal/places/v1/pickup/status',
        json={
            'places': [
                {
                    'place_id': 111,
                    'pickup_enabled': False,
                    'place_commission': {'percent': 15.7},
                    'pickup_mode': 'self_allowed',
                    'place_delivery_zone': {
                        'zone_id': 'fake_zone_id',
                        'zone_enabled': True,
                    },
                },
                {
                    'place_id': 222,
                    'pickup_enabled': False,
                    'place_commission': {'percent': 15.8},
                    'pickup_mode': 'self_allowed',
                    'place_delivery_zone': {
                        'zone_id': 'fake_zone_id2',
                        'zone_enabled': True,
                    },
                },
            ],
        },
    )
    assert response.status_code == 204

    statuses = get_pickup_statuses()
    assert len(statuses) == 2

    assert statuses[0]['place_id'] == 111
    assert statuses[0]['place_delivery_zone_id'] == 'fake_zone_id'
    assert statuses[0]['place_delivery_zone_enabled'] is True
    assert statuses[0]['place_commission_value'] == 15.7
    assert statuses[0]['pickup_started'] is None
    assert statuses[0]['pickup_enabled'] is False
    assert statuses[0]['pickup_mode'] == 'self_allowed'
    assert statuses[0]['created_at']
    assert statuses[0]['updated_at']
    assert statuses[0]['in_process'] is False

    assert statuses[1]['place_id'] == 222
    assert statuses[1]['place_delivery_zone_id'] == 'fake_zone_id2'
    assert statuses[1]['place_delivery_zone_enabled'] is True
    assert statuses[1]['place_commission_value'] == 15.8
    assert statuses[1]['pickup_started'] is None
    assert statuses[1]['pickup_enabled'] is False
    assert statuses[1]['pickup_mode'] == 'self_allowed'
    assert statuses[1]['created_at']
    assert statuses[1]['updated_at']
    assert statuses[1]['in_process'] is False

    response = await taxi_eats_restapp_places.post(
        '/internal/places/v1/pickup/status',
        json={
            'places': [
                {
                    'place_id': 111,
                    'pickup_enabled': True,
                    'place_commission': {'percent': 15.7},
                    'pickup_mode': 'self_unallowed',
                },
                {
                    'place_id': 222,
                    'pickup_enabled': True,
                    'place_commission': {'percent': 15.8},
                    'pickup_mode': 'self_unallowed',
                    'place_delivery_zone': {
                        'zone_id': 'fake_zone_id3',
                        'zone_enabled': False,
                    },
                },
            ],
        },
    )
    assert response.status_code == 204

    statuses = get_pickup_statuses()
    assert len(statuses) == 2

    assert statuses[0]['place_id'] == 111
    assert statuses[0]['place_delivery_zone_id'] == 'fake_zone_id'
    assert statuses[0]['place_delivery_zone_enabled'] is True
    assert statuses[0]['place_commission_value'] == 15.7
    assert statuses[0]['pickup_started'] is None
    assert statuses[0]['pickup_enabled'] is True
    assert statuses[0]['pickup_mode'] == 'self_unallowed'
    assert statuses[0]['created_at']
    assert statuses[0]['updated_at']
    assert statuses[0]['in_process'] is False

    assert statuses[1]['place_id'] == 222
    assert statuses[1]['place_delivery_zone_id'] == 'fake_zone_id3'
    assert statuses[1]['place_delivery_zone_enabled'] is False
    assert statuses[1]['place_commission_value'] == 15.8
    assert statuses[1]['pickup_started'] is None
    assert statuses[1]['pickup_enabled'] is True
    assert statuses[1]['pickup_mode'] == 'self_unallowed'
    assert statuses[1]['created_at']
    assert statuses[1]['updated_at']
    assert statuses[1]['in_process'] is False

    response_status = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/pickup/status?place_ids=111,222',
        headers={'X-YaEda-PartnerId': '9999'},
    )
    assert response_status.status_code == 200

    assert response_status.json() == {
        'places': [
            {
                'status': 'enabled',
                'commission': {'percent': 15.7},
                'place_id': 111,
            },
            {
                'status': 'unavailable',
                'commission': {'percent': 15.8},
                'place_id': 222,
            },
        ],
    }

    assert client_notify_handler.times_called == 4


async def test_set_pickup_status_one_upd(
        stq,
        mock_restapp_authorizer,
        mockserver,
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        get_pickup_status_by_place_id,
        get_pickup_statuses,
):
    @mockserver.json_handler('/client-notify/v1/push')
    def client_notify_handler(data):
        return {'notification_id': '123123'}

    await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/pickup/enable',
        json={'place_ids': [111, 222]},
        headers={'X-YaEda-PartnerId': '9999'},
    )
    assert stq.eats_restapp_places_pickup.times_called == 1
    response = await taxi_eats_restapp_places.post(
        '/internal/places/v1/pickup/status',
        json={
            'places': [
                {
                    'place_id': 111,
                    'pickup_enabled': False,
                    'place_commission': {'percent': 15.7},
                    'pickup_mode': 'self_allowed',
                },
                {
                    'place_id': 222,
                    'pickup_enabled': False,
                    'place_commission': {'percent': 15.8},
                    'pickup_mode': 'self_allowed',
                },
            ],
        },
    )
    assert response.status_code == 204

    response = await taxi_eats_restapp_places.post(
        '/internal/places/v1/pickup/status',
        json={
            'places': [
                {
                    'place_id': 222,
                    'pickup_enabled': True,
                    'place_commission': {'percent': 15.8},
                    'pickup_mode': 'self_unallowed',
                },
            ],
        },
    )
    assert response.status_code == 204

    statuses = get_pickup_statuses()
    assert len(statuses) == 2

    assert statuses[0]['place_id'] == 111
    assert statuses[0]['place_delivery_zone_id'] is None
    assert statuses[0]['place_delivery_zone_enabled'] is False
    assert statuses[0]['place_commission_value'] == 15.7
    assert statuses[0]['pickup_started'] is None
    assert statuses[0]['pickup_enabled'] is False
    assert statuses[0]['pickup_mode'] == 'self_allowed'
    assert statuses[0]['created_at']
    assert statuses[0]['updated_at']
    assert statuses[0]['in_process'] is False

    assert statuses[1]['place_id'] == 222
    assert statuses[1]['place_delivery_zone_id'] is None
    assert statuses[1]['place_delivery_zone_enabled'] is False
    assert statuses[1]['place_commission_value'] == 15.8
    assert statuses[1]['pickup_started'] is None
    assert statuses[1]['pickup_enabled'] is True
    assert statuses[1]['pickup_mode'] == 'self_unallowed'
    assert statuses[1]['created_at']
    assert statuses[1]['updated_at']
    assert statuses[1]['in_process'] is False

    response_status = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/pickup/status?place_ids=111,222',
        headers={'X-YaEda-PartnerId': '9999'},
    )
    assert response_status.status_code == 200

    assert response_status.json() == {
        'places': [
            {
                'status': 'available',
                'commission': {'percent': 15.7},
                'place_id': 111,
            },
            {
                'status': 'unavailable',
                'commission': {'percent': 15.8},
                'place_id': 222,
            },
        ],
    }

    assert client_notify_handler.times_called == 3


async def test_set_pickup_status_400(
        taxi_eats_restapp_places,
        get_pickup_status_by_place_id,
        get_pickup_statuses,
):
    response = await taxi_eats_restapp_places.post(
        '/internal/places/v1/pickup/status',
        json={
            'places': [
                {
                    'place_id': 111,
                    'pickup_enabled': False,
                    'pickup_mode': 'self_allowed',
                },
                {
                    'place_id': 222,
                    'pickup_enabled': False,
                    'pickup_mode': 'foo',
                },
            ],
        },
    )
    assert response.status_code == 400


async def test_get_pickup_status_403(
        taxi_eats_restapp_places, mock_authorizer_forbidden,
):
    response_status = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/pickup/status?place_ids=111,222',
        headers={'X-YaEda-PartnerId': '9999'},
    )
    assert response_status.status_code == 403

    assert response_status.json() == {'code': '403', 'message': 'Forbidden'}


async def test_notification(
        mock_authorizer_allowed,
        stq,
        mock_restapp_authorizer,
        pgsql,
        mockserver,
        taxi_eats_restapp_places,
        get_pickup_status_by_place_id,
        get_pickup_statuses,
):
    @mockserver.json_handler('/client-notify/v1/push')
    def client_notify_handler(data):
        return {'notification_id': '123123'}

    await taxi_eats_restapp_places.post(
        '/4.0/restapp-front/places/v1/pickup/enable',
        json={'place_ids': [111, 222]},
        headers={'X-YaEda-PartnerId': '9999'},
    )
    assert stq.eats_restapp_places_pickup.times_called == 1

    await taxi_eats_restapp_places.post(
        '/internal/places/v1/pickup/status',
        json={
            'places': [
                {
                    'place_id': 111,
                    'pickup_enabled': False,
                    'place_commission': {'percent': 15.7},
                    'pickup_mode': 'self_allowed',
                },
                {
                    'place_id': 222,
                    'pickup_enabled': False,
                    'place_commission': {'percent': 15.8},
                    'pickup_mode': 'self_allowed',
                },
            ],
        },
    )

    cursor = pgsql['eats_restapp_places'].cursor()
    cursor.execute(
        'SELECT partner_id '
        'FROM eats_restapp_places.pickup_log '
        f'WHERE place_id={111} '
        'ORDER BY created_at DESC '
        'LIMIT 1',
    )
    sync_info = cursor.fetchone()
    assert sync_info[0] == 9999

    cursor.execute(
        'SELECT partner_id '
        'FROM eats_restapp_places.pickup_log '
        f'WHERE place_id={222} '
        'ORDER BY created_at DESC '
        'LIMIT 1',
    )
    sync_info = cursor.fetchone()
    assert sync_info[0] == 9999

    assert client_notify_handler.times_called == 2
    notify_data = client_notify_handler.next_call()['data'].json
    assert notify_data['service'] == 'eats-partners'
    assert notify_data['intent'] == 'pickup_changed_status'
    assert notify_data['client_id'] == '9999'
    assert notify_data['data']['payload'] == {
        'eventData': {
            'data': {
                'commission': {'percent': 15.7},
                'place_id': 111,
                'status': 'available',
            },
            'event': 'status_is_changed',
        },
    }

    notify_data = client_notify_handler.next_call()['data'].json
    assert notify_data['service'] == 'eats-partners'
    assert notify_data['intent'] == 'pickup_changed_status'
    assert notify_data['client_id'] == '9999'
    assert notify_data['data']['payload'] == {
        'eventData': {
            'data': {
                'commission': {'percent': 15.8},
                'place_id': 222,
                'status': 'available',
            },
            'event': 'status_is_changed',
        },
    }
