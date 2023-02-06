import pytest


async def test_bad_request(taxi_driver_wall):
    response = await taxi_driver_wall.get('/internal/driver-wall/v1/add')
    assert response.status_code == 405

    response = await taxi_driver_wall.post('/internal/driver-wall/v1/add')
    assert response.status_code == 400

    response = await taxi_driver_wall.post(
        '/internal/driver-wall/v1/add',
        json={
            'id': 'test',
            'template': {'title': ['title'], 'text': 'text'},
            'filters': {'drivers': ['dbid_uuid']},
        },
    )
    assert response.status_code == 400

    response = await taxi_driver_wall.post(
        '/internal/driver-wall/v1/add',
        json={
            'id': 'test',
            'template': {'title': 'title', 'text': ['text']},
            'filters': {'drivers': ['dbid_uuid']},
        },
    )
    assert response.status_code == 400

    response = await taxi_driver_wall.post(
        '/internal/driver-wall/v1/add',
        json={
            'id': 'test',
            'template': {'title': {'title': 'title'}, 'text': 'text'},
            'filters': {'drivers': ['dbid_uuid']},
        },
    )
    assert response.status_code == 400

    response = await taxi_driver_wall.post(
        '/internal/driver-wall/v1/add',
        json={
            'id': 'test',
            'template': {'title': 'title', 'text': {'text': 'text'}},
            'filters': {'drivers': ['dbid_uuid']},
        },
    )
    assert response.status_code == 400


@pytest.mark.now('2018-08-05T00:00:00Z')
async def test_bad_feeds_response(taxi_driver_wall, mockserver):
    @mockserver.json_handler('/feeds/v1/create')
    def _mock_feeds(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'Error message'},
        )

    response = await taxi_driver_wall.post(
        '/internal/driver-wall/v1/add',
        json={
            'id': 'my_request_id',
            'template': {
                'title': 'Hello, driver!',
                'text': 'How are you doing?',
            },
            'filters': {'drivers': ['dbid_uuid']},
            'expire': '2018-08-12T00:00:00+00:00',
        },
    )
    assert response.status_code == 400


@pytest.mark.now('2018-08-05T00:00:00Z')
async def test_empty_template(taxi_driver_wall, load_json, mockserver):
    @mockserver.json_handler('/feeds/v1/create')
    def _mock_feeds(request):
        assert request.json['service'] == 'driver-wall'
        assert request.json['expire'] == '2018-09-04T00:00:00+00:00'
        if request.json['request_id'] == 'test1':
            assert {
                'channel': 'taximeter:Driver:dbid:uuid1',
                'payload_overrides': {'title': 'test', 'text': 'test'},
            } in request.json['channels']
            assert {
                'channel': 'taximeter:Driver:dbid:uuid2',
                'payload_overrides': {'title': 'test 2', 'text': 'test 2'},
            } in request.json['channels']
            assert request.json['payload'] == {
                'text': '',
                'title': '',
                'series_id': 'test1',
            }
        elif request.json['request_id'] == 'test2':
            assert {
                'channel': 'taximeter:Driver:dbid:uuid1',
                'payload_overrides': {'text': 'test'},
            } in request.json['channels']
            assert {
                'channel': 'taximeter:Driver:dbid:uuid2',
                'payload_overrides': {'title': 'test'},
            } in request.json['channels']
            assert request.json['payload'] == {
                'title': 'async default title',
                'text': 'async default text',
                'series_id': 'test2',
            }
        else:
            assert False

        return {
            'service': 'driver-wall',
            'filtered': [],
            'feed_ids': {
                'taximeter:Driver:dbid:uuid1': (
                    '0134567812345678123456781234567'
                ),
                'taximeter:Driver:dbid:uuid2': (
                    '0234567812345678123456781234567'
                ),
            },
        }

    # Error: template's required fields are empty
    response = await taxi_driver_wall.post(
        '/internal/driver-wall/v1/add',
        json={
            'id': 'test',
            'template': {'title': '', 'text': ''},
            'filters': {'drivers': ['dbid_uuid']},
        },
    )
    assert response.status_code == 400

    # Error: template's required fields are empty, and one driver don't have
    # personal text and title
    response = await taxi_driver_wall.post(
        '/internal/driver-wall/v1/add',
        json={
            'id': 'test',
            'template': {'title': '', 'text': ''},
            'drivers': [
                {'driver': 'dbid_uuid1', 'title': 'test', 'text': 'test'},
                {'driver': 'dbid_uuid2'},
            ],
        },
    )
    assert response.status_code == 400

    # Ok: template's required fields are empty, but each driver has
    # non-empty personal text and title
    response = await taxi_driver_wall.post(
        '/internal/driver-wall/v1/add',
        json={
            'id': 'test1',
            'template': {'title': '', 'text': ''},
            'drivers': [
                {'driver': 'dbid_uuid1', 'title': 'test', 'text': 'test'},
                {'driver': 'dbid_uuid2', 'title': 'test 2', 'text': 'test 2'},
            ],
        },
    )
    assert response.status_code == 200

    # Ok: template's required fields are not empty, and drivers don't have
    # personal text and title
    response = await taxi_driver_wall.post(
        '/internal/driver-wall/v1/add',
        json={
            'id': 'test2',
            'template': {
                'title': 'async default title',
                'text': 'async default text',
            },
            'drivers': [
                {'driver': 'dbid_uuid1', 'text': 'test'},
                {'driver': 'dbid_uuid2', 'title': 'test'},
            ],
        },
    )
    assert response.status_code == 200


async def _add_with_idempotency_token(taxi_driver_wall, idempotency_token):
    response = await taxi_driver_wall.post(
        '/internal/driver-wall/v1/add',
        headers={'X-Idempotency-Token': idempotency_token},
        json={
            'id': 'idempotency_request_id',
            # Message template
            'template': {
                'title': 'Hello, driver!',
                'text': 'How are you doing?',
                'type': 'newsletter',
                'format': 'Raw',
                'image_id': 'hexhexhex',
                'url': 'https://driver.yandex',
                'teaser': 'teaser',
                'important': True,
                'alert': True,
                'dom_storage': True,
            },
            # Non-personal
            'filters': {
                'drivers': ['PristinaPark_driver', 'UnknownPark_driver'],
                'domains': ['park1', 'park2'],
                'cities': ['Москва', 'Приштина'],
                'countries': ['Россия', 'Украина'],
                'tags': ['tag1', 'tag2', 'tag with-special_chars'],
            },
            # Personal
            'drivers': [
                {
                    'driver': 'MskPark_driver1',
                    'title': 'MskPark driver1',
                    'text': 'Special message #1',
                    'url': 'http://driver.yandex/driver1',
                    'image_id': 'another_id',
                    'alert': False,
                    'expires': '2100-10-22T16:00:00.000000Z',
                },
            ],
            'expire': '2018-08-22T16:00:00.000000Z',
        },
    )
    return response


@pytest.mark.now('2018-08-05T00:00:00Z')
@pytest.mark.parametrize(
    'feeds_code,feeds_response',
    [
        (200, {'service': 'driver-wall', 'filtered': [], 'feed_ids': {}}),
        (409, {'code': '409', 'message': 'Request already in progress'}),
    ],
)
async def test_idempotency(
        taxi_driver_wall, mockserver, load_binary, feeds_code, feeds_response,
):
    @mockserver.handler('/s3mds', prefix=True)
    def _mock_mds(request):
        if request.method == 'PUT':
            return mockserver.make_response('', 200)
        if request.method == 'GET':
            img = load_binary('ya_taxi.png')
            return mockserver.make_response(img, 200)
        return mockserver.make_response('Wrong method', 500)

    idempotency_token = '12345'

    @mockserver.json_handler('/feeds/v1/create')
    def _mock_feeds(request):
        assert request.headers['X-Idempotency-Token'] == idempotency_token
        return mockserver.make_response(status=feeds_code, json=feeds_response)

    response = await _add_with_idempotency_token(
        taxi_driver_wall, idempotency_token,
    )
    assert response.status_code == feeds_code


@pytest.mark.now('2018-08-05T00:00:00Z')
async def test_basic(taxi_driver_wall, mockserver, load_binary):
    @mockserver.handler('/s3mds', prefix=True)
    def _mock_mds(request):
        if request.method == 'PUT':
            return mockserver.make_response('', 200)
        if request.method == 'GET':
            img = load_binary('ya_taxi.png')
            return mockserver.make_response(img, 200)
        return mockserver.make_response('Wrong method', 500)

    template = {
        'title': 'Hello, driver!',
        'text': 'How are you doing?',
        'type': 'newsletter',
        'format': 'Raw',
        'image_id': 'hexhexhex',
        'url': 'https://driver.yandex',
        'teaser': 'teaser',
        'important': True,
        'dom_storage': True,
    }

    @mockserver.json_handler('/feeds/v1/create')
    def _mock_feeds(request):
        assert request.json['service'] == 'driver-wall'
        assert request.json['expire'] == '2018-08-22T16:00:00+00:00'
        assert request.json['request_id'] == 'my_request_id'
        assert sorted(
            [
                {'channel': 'taximeter:Driver:PristinaPark:driver'},
                {'channel': 'taximeter:Driver:UnknownPark:driver'},
                {'channel': 'taximeter:Park:park1'},
                {'channel': 'taximeter:Park:park2'},
                {'channel': 'taximeter:City:МОСКВА'},
                {'channel': 'taximeter:City:ПРИШТИНА'},
                {'channel': 'taximeter:Country:РОССИЯ'},
                {'channel': 'taximeter:Country:УКРАИНА'},
                {'channel': 'taximeter:Tag:tag1'},
                {'channel': 'taximeter:Tag:tag2'},
                {'channel': 'taximeter:Tag:tag with-special_chars'},
                {'channel': 'taximeter:Experiment:experiment1'},
                {'channel': 'taximeter:Experiment:experiment2'},
                {
                    'channel': 'taximeter:Driver:MskPark:driver1',
                    'payload_overrides': {
                        'title': 'MskPark driver1',
                        'text': 'Special message #1',
                        'url': 'http://driver.yandex/driver1',
                        'image_id': 'another_id',
                        'expires': '2100-10-22T16:00:00+00:00',
                        'thumbnail': (
                            'iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAA'
                            'dElEQVQImQFpAJb/AYyMjAACAgIA+vr6AAcHBwD7+/sABNra'
                            '2gD29vYBDgn0FgcF+wv09wXxBB37/DTcAwMGHx0U9uvyEPAy'
                            'JfQiBCRGRcwb9/cAFhH8GA8NBAzt8P3eBOXl5QAAAAAA8vIE'
                            '6AAAAAAMDAwA+dopO4N83CcAAAAASUVORK5CYII='
                        ),
                    },
                },
            ],
            key=lambda x: x['channel'],
        ) == sorted(request.json['channels'], key=lambda x: x['channel'])
        assert request.json['payload'] == {
            **template,
            'series_id': 'my_request_id',
            'thumbnail': (
                'iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAdElEQVQImQF'
                'pAJb/AYyMjAACAgIA+vr6AAcHBwD7+/sABNra2gD29vYBDgn0FgcF+wv09w'
                'XxBB37/DTcAwMGHx0U9uvyEPAyJfQiBCRGRcwb9/cAFhH8GA8NBAzt8P3eB'
                'OXl5QAAAAAA8vIE6AAAAAAMDAwA+dopO4N83CcAAAAASUVORK5CYII='
            ),
        }
        assert request.json['meta'] == {
            'crm_campaign': {'campaign_id': 'hex-hex'},
            'source_service': 'driver-wall',
        }

        return {
            'service': 'driver-wall',
            'filtered': [],
            'feed_ids': {
                'taximeter:Driver:PristinaPark:driver': (
                    '0134567812345678123456781234567'
                ),
                'taximeter:Driver:UnknownPark:driver': (
                    '0134567812345678123456781234567'
                ),
                'taximeter:Park:park1': '0134567812345678123456781234567',
                'taximeter:Park:park2': '0134567812345678123456781234567',
                'taximeter:City:МОСКВА': '0134567812345678123456781234567',
                'taximeter:City:ПРИШТИНА': '0134567812345678123456781234567',
                'taximeter:Country:РОССИЯ': '0134567812345678123456781234567',
                'taximeter:Country:УКРАИНА': '0134567812345678123456781234567',
                'taximeter:Tag:tag1': '0134567812345678123456781234567',
                'taximeter:Tag:tag2': '0134567812345678123456781234567',
                'taximeter:Tag:tag with-special_chars': (
                    '0134567812345678123456781234567'
                ),
                'taximeter:Driver:MskPark:driver1': (
                    '0234567812345678123456781234567'
                ),
            },
        }

    response = await taxi_driver_wall.post(
        '/internal/driver-wall/v1/add',
        json={
            'id': 'my_request_id',
            # Message template
            'template': template,
            # Non-personal
            'filters': {
                'drivers': ['PristinaPark_driver', 'UnknownPark_driver'],
                'domains': ['park1', 'park2'],
                'cities': ['Москва', 'Приштина'],
                'countries': ['Россия', 'Украина'],
                'tags': ['tag1', 'tag2', 'tag with-special_chars'],
                'experiments': ['experiment1', 'experiment2'],
            },
            # Personal
            'drivers': [
                {
                    'driver': 'MskPark_driver1',
                    'title': 'MskPark driver1',
                    'text': 'Special message #1',
                    'url': 'http://driver.yandex/driver1',
                    'image_id': 'another_id',
                    'expires': '2100-10-22T16:00:00.000000Z',
                },
            ],
            'crm_campaign': {'campaign_id': 'hex-hex'},
            'expire': '2018-08-22T16:00:00.000000Z',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'id': 'my_request_id'}


@pytest.mark.now('2018-08-05T00:00:00Z')
@pytest.mark.parametrize('application', ['taximeter', 'uberdriver'])
async def test_application(taxi_driver_wall, application, mockserver):
    @mockserver.json_handler('/feeds/v1/create')
    def _mock_feeds(request):
        assert (
            request.json['channels'][0]['channel'].split(':')[0] == application
        )

        return {
            'service': 'driver-wall',
            'filtered': [],
            'feed_ids': {'channel': '1234567812345678123456781234567'},
        }

    response = await taxi_driver_wall.post(
        '/internal/driver-wall/v1/add',
        json={
            'id': 'my_request_id',
            'application': application,
            'template': {
                'title': 'Hello, driver!',
                'text': 'How are you doing?',
            },
            'filters': {
                'drivers': ['PristinaPark_driver'],
                'domains': ['park1'],
                'cities': ['Москва'],
                'countries': ['Россия'],
                'tags': ['tag1'],
            },
            'drivers': [{'driver': 'MskPark_driver1'}],
        },
    )
    assert response.status_code == 200


@pytest.mark.now('2018-08-05T00:00:00Z')
async def test_localized(taxi_driver_wall, mockserver, load_binary):
    template = {
        'title': {'key': 'key2', 'keyset': 'client_messages'},
        'text': {'key': 'key2', 'keyset': 'client_messages'},
        'type': 'newsletter',
        'format': 'Raw',
        'image_id': 'hexhexhex',
        'url': 'https://driver.yandex',
        'teaser': 'teaser',
        'important': True,
        'alert': True,
        'dom_storage': True,
    }

    @mockserver.handler('/s3mds', prefix=True)
    def _mock_mds(request):
        if request.method == 'PUT':
            return mockserver.make_response('', 200)
        if request.method == 'GET':
            img = load_binary('ya_taxi.png')
            return mockserver.make_response(img, 200)
        return mockserver.make_response('Wrong method', 500)

    @mockserver.json_handler('/feeds/v1/create')
    def _mock_feeds(request):
        assert request.json['payload'] == {
            **template,
            'series_id': 'my_request_id',
            'thumbnail': (
                'iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAdElEQVQImQF'
                'pAJb/AYyMjAACAgIA+vr6AAcHBwD7+/sABNra2gD29vYBDgn0FgcF+wv09w'
                'XxBB37/DTcAwMGHx0U9uvyEPAyJfQiBCRGRcwb9/cAFhH8GA8NBAzt8P3eB'
                'OXl5QAAAAAA8vIE6AAAAAAMDAwA+dopO4N83CcAAAAASUVORK5CYII='
            ),
        }
        return {
            'service': 'driver-wall',
            'filtered': [],
            'feed_ids': {'channel': '1234567812345678123456781234567'},
        }

    response = await taxi_driver_wall.post(
        '/internal/driver-wall/v1/add',
        json={
            'id': 'my_request_id',
            # Message template
            'template': template,
            # Non-personal
            'filters': {
                'drivers': ['PristinaPark_driver', 'UnknownPark_driver'],
                'domains': ['park1', 'park2'],
                'cities': ['Москва', 'Приштина'],
                'countries': ['Россия', 'Украина'],
                'tags': ['tag1', 'tag2', 'tag with-special_chars'],
            },
            # Personal
            'drivers': [
                {
                    'driver': 'MskPark_driver1',
                    'title': {'key': 'key1', 'keyset': 'client_messages'},
                    'text': {'key': 'key1', 'keyset': 'client_messages'},
                    'url': 'http://driver.yandex/driver1',
                    'image_id': 'another_id',
                    'alert': False,
                    'expires': '2100-10-22T16:00:00.000000Z',
                },
            ],
            'expire': '2018-08-22T16:00:00.000000Z',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'id': 'my_request_id'}


@pytest.mark.now('2018-08-05T00:00:00Z')
async def test_driver_fullscreen(taxi_driver_wall, mockserver, load_binary):
    template = {
        'title': 'Hello, driver!',
        'text': 'How are you doing?',
        'type': 'newsletter',
        'format': 'Raw',
        'alert': True,
        'url': 'https://driver.yandex',
        'teaser': 'teaser',
        'important': True,
        'dom_storage': True,
    }

    @mockserver.json_handler('/feeds/v1/create')
    def _mock_feeds(request):
        return {
            'service': request.json['service'],
            'filtered': [],
            'feed_ids': {
                'taximeter:Driver:PristinaPark:driver': (
                    '0134567812345678123456781234567'
                ),
                'taximeter:Driver:MskPark:driver1': (
                    '0234567812345678123456781234567'
                ),
            },
        }

    response = await taxi_driver_wall.post(
        '/internal/driver-wall/v1/add',
        json={
            'id': 'my_request_id',
            # Message template
            'template': template,
            # Non-personal
            'filters': {'drivers': ['PristinaPark_driver']},
            # Personal
            'drivers': [{'driver': 'MskPark_driver1', 'alert': False}],
            'crm_campaign': {'campaign_id': 'hex-hex'},
            'expire': '2018-08-22T16:00:00.000000Z',
        },
    )
    assert response.status_code == 200
    assert _mock_feeds.times_called == 2

    template['alert'] = False
    response = await taxi_driver_wall.post(
        '/internal/driver-wall/v1/add',
        json={
            'id': 'my_request_id',
            # Message template
            'template': template,
            # Non-personal
            'filters': {'drivers': ['PristinaPark_driver']},
            # Personal
            'drivers': [{'driver': 'MskPark_driver1', 'alert': True}],
            'crm_campaign': {'campaign_id': 'hex-hex'},
            'expire': '2018-08-22T16:00:00.000000Z',
        },
    )
    assert response.status_code == 200
    assert _mock_feeds.times_called == 4


@pytest.mark.now('2018-08-05T00:00:00Z')
async def test_dsat(taxi_driver_wall, mockserver, load_binary):
    template = {
        'title': 'Hello, driver!',
        'text': 'How are you doing?',
        'type': 'dsat',
        'format': 'Raw',
        'alert': False,
        'url': 'https://driver.yandex',
        'teaser': 'teaser',
        'important': True,
        'dom_storage': True,
    }
    feeds_services = set()

    @mockserver.json_handler('/feeds/v1/create')
    def _mock_feeds(request):
        feeds_services.add(request.json['service'])
        return {
            'service': request.json['service'],
            'filtered': [],
            'feed_ids': {
                'taximeter:Driver:PristinaPark:driver': (
                    '0134567812345678123456781234567'
                ),
                'taximeter:Driver:MskPark:driver1': (
                    '0234567812345678123456781234567'
                ),
            },
        }

    response = await taxi_driver_wall.post(
        '/internal/driver-wall/v1/add',
        json={
            'id': 'my_request_id',
            # Message template
            'template': template,
            # Non-personal
            'filters': {'drivers': ['PristinaPark_driver']},
            # Personal
            'drivers': [{'driver': 'MskPark_driver1', 'type': 'newsletter'}],
            'crm_campaign': {'campaign_id': 'hex-hex'},
            'expire': '2018-08-22T16:00:00.000000Z',
        },
    )
    assert response.status_code == 200
    assert _mock_feeds.times_called == 2

    assert feeds_services == {'contractor-sat', 'driver-wall'}


@pytest.mark.now('2018-08-05T00:00:00Z')
@pytest.mark.config(
    DRIVER_WALL_FEEDS_SERVICES=[
        'driver-wall',
        'driver-fullscreen',
        'driver-service',
    ],
)
async def test_feeds_service_config(taxi_driver_wall, mockserver, load_binary):
    template = {
        'title': 'Hello, driver!',
        'text': 'How are you doing?',
        'type': 'newsletter',
        'format': 'Raw',
        'alert': True,
        'url': 'https://driver.yandex',
        'teaser': 'teaser',
        'important': True,
        'dom_storage': True,
    }

    @mockserver.json_handler('/feeds/v1/create')
    def _mock_feeds(request):
        assert request.json['service'] in (
            'driver-service',
            'contractor-fullscreen',
        )
        return {
            'service': request.json['service'],
            'filtered': [],
            'feed_ids': {
                'taximeter:Driver:PristinaPark:driver': (
                    '0134567812345678123456781234567'
                ),
                'taximeter:Driver:MskPark:driver1': (
                    '0234567812345678123456781234567'
                ),
            },
        }

    response = await taxi_driver_wall.post(
        '/internal/driver-wall/v1/add',
        json={
            'id': 'my_request_id',
            'template': template,
            'filters': {'drivers': ['PristinaPark_driver']},
            'crm_campaign': {'campaign_id': 'hex-hex'},
            'expire': '2018-08-22T16:00:00.000000Z',
            'service': 'driver-service',
        },
    )
    assert response.status_code == 200
    assert _mock_feeds.times_called == 2
