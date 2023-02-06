import json


async def test_upd_preparation_time(
        mockserver,
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_restapp_authorizer,
):
    place_id = 1

    @mockserver.json_handler(
        '/eats-core/v1/places/' + str(place_id) + '/update-preparation-time',
    )
    def increase_preparation_time(request):
        return mockserver.make_response(status=200, json={'isSuccess': True})

    @mockserver.json_handler(
        '/eats-core/v1/places/' + str(place_id) + '/update',
    )
    def update_place(request):
        return mockserver.make_response(
            status=201, json={'result': ['добавлено в очередь']},
        )

    req = {
        'name': 'Name',
        'address': {'city': 'ity', 'address': 'addr'},
        'phones': [{'type': 'official', 'number': '+79061112233'}],
        'emails': [{'type': 'main', 'address': 'a@amail'}],
        'payment_methods': ['card'],
        'comments': [{'type': 'courier', 'text': 'txt'}],
        'increase_preparation_time': {
            'minutes': 120,
            'valid_until': None,
            'is_infinite': True,
        },
        'preparation_time': 2000,
    }

    partner_id = 9999
    url = '/4.0/restapp-front/places/v1/update?place_id={}'.format(place_id)
    headers = {
        'X-YaEda-PartnerId': str(partner_id),
        'Content-type': 'application/json',
    }
    extra = {'headers': headers}
    await taxi_eats_restapp_places.patch(url, data=json.dumps(req), **extra)

    res = increase_preparation_time.next_call()['request'].json
    assert res == {'minutes': 120, 'valid_until': None, 'is_infinite': True}

    assert update_place.times_called == 1


async def test_upd_preparation_time_valid_until(
        mockserver,
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_restapp_authorizer,
):
    place_id = 1

    @mockserver.json_handler(
        '/eats-core/v1/places/' + str(place_id) + '/update-preparation-time',
    )
    def preparation_time_update(request):
        return mockserver.make_response(status=200, json={'isSuccess': True})

    @mockserver.json_handler(
        '/eats-core/v1/places/' + str(place_id) + '/update',
    )
    def update_place(request):
        return mockserver.make_response(
            status=201, json={'result': ['добавлено в очередь']},
        )

    req = {
        'name': 'Name',
        'address': {'city': 'ity', 'address': 'addr'},
        'phones': [{'type': 'official', 'number': '+79061112233'}],
        'emails': [{'type': 'main', 'address': 'a@amail'}],
        'payment_methods': ['card'],
        'comments': [{'type': 'courier', 'text': 'txt'}],
        'increase_preparation_time': {
            'minutes': 120,
            'valid_until': '2019-04-01T02:00:00+03:00',
            'is_infinite': False,
        },
        'preparation_time': 2000,
    }

    partner_id = 9999
    url = '/4.0/restapp-front/places/v1/update?place_id={}'.format(place_id)
    headers = {
        'X-YaEda-PartnerId': str(partner_id),
        'Content-type': 'application/json',
    }
    extra = {'headers': headers}
    await taxi_eats_restapp_places.patch(url, data=json.dumps(req), **extra)

    res = preparation_time_update.next_call()['request'].json
    assert res == {
        'minutes': 120,
        'valid_until': '2019-03-31T23:00:00+00:00',
        'is_infinite': False,
    }

    assert update_place.times_called == 1
    res = update_place.next_call()['request'].json
    assert res == {
        'address': {'address': 'addr', 'city': 'ity'},
        'comments': [{'text': 'txt', 'type': 'courier'}],
        'emails': [{'address': 'a@amail', 'type': 'main'}],
        'name': 'Name',
        'paymentMethods': ['card'],
        'phones': [{'number': '+79061112233', 'type': 'official'}],
        'preparationTime': 2000,
    }


async def test_upd_preparation_time_v2(
        mockserver,
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_restapp_authorizer,
):
    place_id = 1

    @mockserver.json_handler(
        '/eats-core/v1/places/' + str(place_id) + '/update-preparation-time',
    )
    def increase_preparation_time(request):
        return mockserver.make_response(status=200, json={'isSuccess': True})

    @mockserver.json_handler(
        '/eats-core/v1/places/' + str(place_id) + '/update',
    )
    def update_place(request):
        return mockserver.make_response(
            status=201, json={'result': ['добавлено в очередь']},
        )

    req = {
        'name': 'Name',
        'address': {'city': 'ity', 'address': 'addr'},
        'phones': [{'type': 'official', 'number': '+79061112233'}],
        'emails': [{'type': 'main', 'address': 'a@amail'}],
        'payment_methods': ['card'],
        'comments': [{'type': 'courier', 'text': 'txt'}],
        'increase_preparation_time': {
            'minutes': 120,
            'valid_until': None,
            'is_infinite': True,
        },
        'preparation_time': 2000,
    }

    partner_id = 9999
    url = '/4.0/restapp-front/places/v2/update?place_id={}'.format(place_id)
    headers = {
        'X-YaEda-PartnerId': str(partner_id),
        'Content-type': 'application/json',
    }
    extra = {'headers': headers}
    await taxi_eats_restapp_places.patch(url, data=json.dumps(req), **extra)

    res = increase_preparation_time.next_call()['request'].json
    assert res == {'minutes': 120, 'valid_until': None, 'is_infinite': True}

    assert update_place.times_called == 1


async def test_upd_preparation_time_v2_valid_until(
        mockserver,
        taxi_eats_restapp_places,
        mock_authorizer_allowed,
        mock_restapp_authorizer,
):
    place_id = 1

    @mockserver.json_handler(
        '/eats-core/v1/places/' + str(place_id) + '/update-preparation-time',
    )
    def preparation_time_update(request):
        return mockserver.make_response(status=200, json={'isSuccess': True})

    @mockserver.json_handler(
        '/eats-core/v1/places/' + str(place_id) + '/update',
    )
    def update_place(request):
        return mockserver.make_response(
            status=201, json={'result': ['добавлено в очередь']},
        )

    req = {
        'name': 'Name',
        'address': {'city': 'ity', 'address': 'addr'},
        'phones': [{'type': 'official', 'number': '+79061112233'}],
        'emails': [{'type': 'main', 'address': 'a@amail'}],
        'payment_methods': ['card'],
        'comments': [{'type': 'courier', 'text': 'txt'}],
        'increase_preparation_time': {
            'minutes': 120,
            'valid_until': '2019-04-01T02:00:00+03:00',
            'is_infinite': False,
        },
        'preparation_time': 2000,
    }

    partner_id = 9999
    url = '/4.0/restapp-front/places/v2/update?place_id={}'.format(place_id)
    headers = {
        'X-YaEda-PartnerId': str(partner_id),
        'Content-type': 'application/json',
    }
    extra = {'headers': headers}
    await taxi_eats_restapp_places.patch(url, data=json.dumps(req), **extra)

    res = preparation_time_update.next_call()['request'].json
    assert res == {
        'minutes': 120,
        'valid_until': '2019-03-31T23:00:00+00:00',
        'is_infinite': False,
    }

    assert update_place.times_called == 1
    res = update_place.next_call()['request'].json
    assert res == {
        'address': {'address': 'addr', 'city': 'ity'},
        'comments': [{'text': 'txt', 'type': 'courier'}],
        'emails': [{'address': 'a@amail', 'type': 'main'}],
        'name': 'Name',
        'paymentMethods': ['card'],
        'phones': [{'number': '+79061112233', 'type': 'official'}],
        'preparationTime': 2000,
    }
