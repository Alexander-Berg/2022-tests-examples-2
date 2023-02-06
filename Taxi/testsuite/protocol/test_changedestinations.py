import copy
import json

import dateutil.parser
import pytest

from notify_on_change_version_switch import NOTIFY_ON_CHANGE_VERSION_SWITCH
from validate_stq_task import validate_notify_on_change_stq_task
from validate_stq_task import validate_process_update_stq_task

DEFAULT_DESTINATIONS = [
    {
        'country': 'Russia',
        'description': 'Moscow, Russia',
        'fullname': 'Russia, Moscow, Kropotkinsky Lane',
        'geopoint': [37.642474, 55.735520],
        'locality': 'Moscow',
        'object_type': 'другое',
        'short_text': 'Kropotkinsky Lane',
        'thoroughfare': 'Kropotkinsky Lane',
        'extra_data': {'floor': '4', 'apartment': '100', 'porch': '200'},
        'type': 'address',
    },
]


@pytest.mark.now('2017-07-22T17:15:15+0000')
@pytest.mark.config(BLOCKED_ZONES_ENABLED=False)
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_changedestinations_empty_changes(
        taxi_protocol,
        db,
        now,
        mockserver,
        load_json,
        notify_on_change_version_switch,
):
    """Change destinations with empty changes"""

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return load_json('yamaps_kropotkinsky.json')

    created_time = dateutil.parser.parse('2017-07-22T17:15:20+0000')
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': '8c83b49edb274ce0992f337061041111',
        'created_time': created_time.isoformat(),
        'destinations': copy.deepcopy(DEFAULT_DESTINATIONS),
    }
    query = {'_id': request['orderid']}
    order_proc = db.order_proc.find_one(query)
    assert order_proc is not None
    version = order_proc['order']['version']
    # there is no changes in order_proc
    assert 'changes' not in order_proc
    assert now > order_proc['updated']

    response = taxi_protocol.post('3.0/changedestinations', request)
    assert response.status_code == 200
    data = response.json()

    # validate response according to protocol
    request['destinations'][0]['uris'] = [
        'ymapsbm1://geo?ll=37.591%2C55.739&spn=0.008%2C0.004&text='
        '%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D1%8F%2C%20%D0%9C%D0%BE%D1%81%D0%BA%D0'
        '%B2%D0%B0%2C%20%D0%9A%D1%80%D0%BE%D0%BF%D0%BE%D1%82%D0%BA%D0%B8%D0%BD'
        '%D1%81%D0%BA%D0%B8%D0%B9%20%D0%BF%D0%B5%D1%80%D0%B5%D1%83%D0%BB%D0%BE'
        '%D0%BA',
    ]

    request['destinations'][0]['extra_data'].pop('porch')
    request['destinations'][0]['porchnumber'] = '200'
    assert data == {
        'change_id': data['change_id'],
        'status': 'success',
        'name': 'destinations',
        'value': request['destinations'],
    }
    # validate order_proc table
    order_proc = db.order_proc.find_one(query)
    assert order_proc['processing']['need_start'] is True
    assert order_proc['order_info']['need_sync'] is True
    assert (
        order_proc['order']['request']['destinations']
        == request['destinations']
    )
    assert order_proc['order']['version'] == version + 1

    # there should be 2 items in the 'objects', according to protocol
    # we need to create one fake item
    assert order_proc['changes']['objects'] == [
        {
            'id': order_proc['changes']['objects'][0]['id'],
            'vl': [
                {
                    'country': 'Belarus',
                    'description': 'Moscow, Belarus',
                    'exact': False,
                    'fullname': 'Belarus, Moscow, Kropotkinsky Lane',
                    'geopoint': [37.59090617361221, 55.73921060048498],
                    'locality': 'Moscow',
                    'object_type': 'другое',
                    'short_text': 'Kropotkinsky Lane',
                    'thoroughfare': 'Kropotkinsky Lane',
                    'type': 'address',
                    'use_geopoint': True,
                },
            ],
            's': 'applied',
            'ci': request['id'],
            'n': 'destinations',
            'vr': version + 1,
            'c': now.replace(tzinfo=None, microsecond=0),
            't': created_time.replace(tzinfo=None, microsecond=0),
            'si': {'s': 'delivered', 'c': 0},
        },
        {
            'id': order_proc['changes']['objects'][1]['id'],
            'vl': request['destinations'],
            's': 'applying',
            'ci': request['id'],
            'n': 'destinations',
            'vr': version + 1,
            'c': now.replace(tzinfo=None, microsecond=0),
            't': created_time.replace(tzinfo=None, microsecond=0),
            'si': {'s': 'init', 'c': 0},
        },
    ]


@pytest.mark.config(CROSSDEVICE_ENABLED=True, BLOCKED_ZONES_ENABLED=False)
@pytest.mark.now('2017-07-22T17:15:15+0000')
@pytest.mark.filldb(users='crossdevice')
@pytest.mark.parametrize('crossdevice_user_first', [True, False])
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_crossdevice(
        taxi_protocol,
        db,
        now,
        mockserver,
        load_json,
        crossdevice_user_first,
        notify_on_change_version_switch,
):
    user_id = 'b300bda7d41b4bae8d58dfa93221ef16'
    orderid = '8c83b49edb274ce0992f337061041111'
    crossdevice_user_id = 'crossdeviceuser00000000000000000'

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return load_json('yamaps_kropotkinsky.json')

    created_time = dateutil.parser.parse('2017-07-22T17:15:20+0000')
    request = {
        'orderid': orderid,
        'created_time': created_time.isoformat(),
        'destinations': copy.deepcopy(DEFAULT_DESTINATIONS),
    }
    sequence = [user_id, crossdevice_user_id]
    responses = []
    if crossdevice_user_first:
        sequence = reversed(sequence)
    for user_id in sequence:
        request['id'] = user_id
        resp = taxi_protocol.post('3.0/changedestinations', request)
        assert resp.status_code == 200
        resp_json = resp.json()
        resp_json.pop('change_id')
        responses.append(resp_json)
    assert responses[0] == responses[1]


@pytest.mark.now('2017-07-22T17:15:15+0000')
@pytest.mark.config(BLOCKED_ZONES_ENABLED=False)
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_changedestinations_empty_order_version(
        taxi_protocol,
        db,
        now,
        mockserver,
        load_json,
        notify_on_change_version_switch,
):
    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return load_json('yamaps_kropotkinsky.json')

    created_time = dateutil.parser.parse('2017-07-22T17:15:20+0000')
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': '8c83b49edb274ce0992f337061040001',
        'created_time': created_time.isoformat(),
        'destinations': copy.deepcopy(DEFAULT_DESTINATIONS),
    }
    query = {'_id': request['orderid']}
    order_proc = db.order_proc.find_one(query)
    assert order_proc is not None
    # there is no changes in order_proc
    assert 'changes' not in order_proc
    assert now > order_proc['updated']

    response = taxi_protocol.post('3.0/changedestinations', request)
    assert response.status_code == 200
    data = response.json()

    # validate response according to protocol
    request['destinations'][0]['uris'] = [
        'ymapsbm1://geo?ll=37.591%2C55.739&spn=0.008%2C0.004&text='
        '%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D1%8F%2C%20%D0%9C%D0%BE%D1%81%D0%BA%D0'
        '%B2%D0%B0%2C%20%D0%9A%D1%80%D0%BE%D0%BF%D0%BE%D1%82%D0%BA%D0%B8%D0%BD'
        '%D1%81%D0%BA%D0%B8%D0%B9%20%D0%BF%D0%B5%D1%80%D0%B5%D1%83%D0%BB%D0%BE'
        '%D0%BA',
    ]

    request['destinations'][0]['porchnumber'] = request['destinations'][0][
        'extra_data'
    ]['porch']
    request['destinations'][0]['extra_data'].pop('porch')

    assert data == {
        'change_id': data['change_id'],
        'status': 'success',
        'name': 'destinations',
        'value': request['destinations'],
    }
    # validate order_proc table
    order_proc = db.order_proc.find_one(query)
    assert order_proc['processing']['need_start'] is True
    assert order_proc['order_info']['need_sync'] is True
    assert (
        order_proc['order']['request']['destinations']
        == request['destinations']
    )
    assert order_proc['order']['version'] == 1

    # there should be 2 items in the 'objects', according to protocol
    # we need to create one fake item
    assert order_proc['changes']['objects'] == [
        {
            'id': order_proc['changes']['objects'][0]['id'],
            'vl': [
                {
                    'country': 'Belarus',
                    'description': 'Moscow, Belarus',
                    'exact': False,
                    'fullname': 'Belarus, Moscow, Kropotkinsky Lane',
                    'geopoint': [37.59090617361221, 55.73921060048498],
                    'locality': 'Moscow',
                    'object_type': 'другое',
                    'short_text': 'Kropotkinsky Lane',
                    'thoroughfare': 'Kropotkinsky Lane',
                    'type': 'address',
                    'use_geopoint': True,
                },
            ],
            's': 'applied',
            'ci': request['id'],
            'n': 'destinations',
            'vr': 1,
            'c': now.replace(tzinfo=None, microsecond=0),
            't': created_time.replace(tzinfo=None, microsecond=0),
            'si': {'s': 'delivered', 'c': 0},
        },
        {
            'id': order_proc['changes']['objects'][1]['id'],
            'vl': request['destinations'],
            's': 'applying',
            'ci': request['id'],
            'n': 'destinations',
            'vr': 1,
            'c': now.replace(tzinfo=None, microsecond=0),
            't': created_time.replace(tzinfo=None, microsecond=0),
            'si': {'s': 'init', 'c': 0},
        },
    ]


@pytest.mark.parametrize(
    'order_id, lang',
    [
        ('8c83b49edb274ce0992f337061042222', 'en'),
        ('8c83b49edb274ce0992f337061046666', 'ru'),
    ],
)
@pytest.mark.now('2017-07-22T17:20:15+0000')
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_changedestinations(
        taxi_protocol,
        db,
        mockserver,
        load_json,
        now,
        order_id,
        lang,
        mock_stq_agent,
        notify_on_change_version_switch,
):
    """Basic change destinations"""

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        assert lang == request.args.get('lang')
        return load_json('yamaps_kropotkinsky.json')

    @mockserver.json_handler(
        '/pricing_data_preparer/internal/v1/backend_variables',
    )
    def pricing_backend_variables_mock(req):
        req_data = json.loads(req.get_data())
        assert req_data['new_value'] == {
            'variable_id': 'waypoints_count',
            'waypoints_count': 2,
        }
        assert req_data['order_id'] == order_id
        assert req_data['reason'] == 'change_destinations'
        return {
            'set': {
                'pricing_data_updates': {
                    'order.pricing_data.user.data.waypoints_count': 1,
                },
            },
            'unset': {'pricing_data_updates': {}},
        }

    created_time = dateutil.parser.parse('2017-07-22T17:20:20+0000')
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': order_id,
        'created_time': created_time.isoformat(),
        'destinations': [
            {
                'country': 'Russian Federation',
                'description': 'Moscow, Russian Federation',
                'fullname': 'Russian Federation, Moscow, Kropotkinsky Lane',
                'geopoint': [37.59090617361221, 55.73921060048498],
                'locality': 'Moscow',
                'object_type': 'другое',
                'short_text': 'Kropotkinsky Lane',
                'thoroughfare': 'Kropotkinsky Lane',
                'extra_data': {'floor': '4', 'apartment': '10', 'porch': '20'},
                'type': 'address',
                'uri': 'ymapsbm1://geo?ll=37.642%2C55.738',
            },
        ],
    }
    query = {'_id': request['orderid']}
    order_proc = db.order_proc.find_one(query)
    assert order_proc is not None
    version = order_proc['order']['version']
    assert now > order_proc['updated']

    response = taxi_protocol.post(
        '3.0/changedestinations', request, headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    data = response.json()

    # validate response according to protocol
    request['destinations'][0]['uris'] = [request['destinations'][0]['uri']]
    request['destinations'][0].pop('uri')

    request['destinations'][0]['extra_data'].pop('porch')
    assert data == {
        'change_id': data['change_id'],
        'status': 'success',
        'name': 'destinations',
        'value': request['destinations'],
    }
    # validate order_proc table
    order_proc = db.order_proc.find_one(query)
    assert order_proc['processing']['need_start'] is True
    assert order_proc['order_info']['need_sync'] is True
    assert order_proc['order']['request']['destinations'] == (
        request['destinations']
    )
    assert (
        order_proc['order']['pricing_data']['user']['data']['waypoints_count']
        == 1
    )
    assert order_proc['order']['version'] == version + 1

    # 'objects' already has 2 items, we add a new item
    assert len(order_proc['changes']['objects']) == 3
    last_change = order_proc['changes']['objects'][2]
    assert last_change == {
        'id': order_proc['changes']['objects'][2]['id'],
        'vl': request['destinations'],
        's': 'applying',
        'ci': request['id'],
        'n': 'destinations',
        'vr': version + 1,
        'c': now.replace(tzinfo=None, microsecond=0),
        't': created_time.replace(tzinfo=None, microsecond=0),
        'si': {'s': 'init', 'c': 0},
    }

    args = [mock_stq_agent, request['orderid'], 'destinations']
    validate_process_update_stq_task(*args, exists=False)
    validate_notify_on_change_stq_task(*args, exists=False)


@pytest.mark.parametrize('events_enabled', [True, False])
@pytest.mark.parametrize('use_order_core', [True, False])
@pytest.mark.now('2017-07-22T17:20:15+0000')
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_processing_events(
        taxi_protocol,
        db,
        mockserver,
        mock_order_core,
        load_json,
        now,
        config,
        events_enabled,
        use_order_core,
        notify_on_change_version_switch,
):
    """Test processing events creation"""

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        assert 'en' == request.args.get('lang')
        return load_json('yamaps_kropotkinsky.json')

    config.set_values(dict(CHANGEDESTINATIONS_EVENTS_ENABLED=events_enabled))
    if use_order_core:
        config.set_values(
            dict(PROCESSING_BACKEND_CPP_SWITCH=['changedestinations']),
        )

    order_id = '8c83b49edb274ce0992f337061042222'
    created_time = dateutil.parser.parse('2017-07-22T17:20:20+0000')
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': order_id,
        'created_time': created_time.isoformat(),
        'destinations': [
            {
                'country': 'Russian Federation',
                'description': 'Moscow, Russian Federation',
                'fullname': 'Russian Federation, Moscow, Kropotkinsky Lane',
                'geopoint': [37.59090617361221, 55.73921060048498],
                'locality': 'Moscow',
                'object_type': 'другое',
                'short_text': 'Kropotkinsky Lane',
                'thoroughfare': 'Kropotkinsky Lane',
                'type': 'address',
                'uri': 'ymapsbm1://geo?ll=37.642%2C55.738',
            },
        ],
    }
    query = {'_id': request['orderid']}
    order_proc = db.order_proc.find_one(query)
    assert order_proc is not None
    assert now > order_proc['updated']
    prev_updated = order_proc['updated']
    proc_version = order_proc['processing']['version']

    response = taxi_protocol.post(
        '3.0/changedestinations', request, headers={'Accept-Language': 'ru'},
    )

    if use_order_core:
        # mock_order_core does not return doc and handler returns 500
        assert mock_order_core.post_event_times_called == events_enabled
        return

    assert mock_order_core.post_event_times_called == 0

    assert response.status_code == 200

    order_proc = db.order_proc.find_one(query)
    if events_enabled:
        statuses = order_proc['order_info']['statistics']['status_updates']
        assert len(statuses) == 1
        assert statuses[0]['q'] == 'destinations_changed'
        assert statuses[0]['h'] is True
        assert statuses[0]['c'] > prev_updated
        assert order_proc['processing']['version'] == proc_version + 1
    else:
        assert order_proc['processing']['version'] == proc_version


@pytest.mark.now('2017-07-22T17:20:15+0000')
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_idempotency_token(
        taxi_protocol,
        db,
        mockserver,
        mock_order_core,
        load_json,
        now,
        config,
        notify_on_change_version_switch,
):
    """Use order-core. Send user-defined idempotency token"""

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        assert 'en' == request.args.get('lang')
        return load_json('yamaps_kropotkinsky.json')

    config.set_values(dict(CHANGEDESTINATIONS_EVENTS_ENABLED=True))
    config.set_values(
        dict(PROCESSING_BACKEND_CPP_SWITCH=['changedestinations']),
    )

    order_id = '8c83b49edb274ce0992f337061042222'
    created_time = dateutil.parser.parse('2017-07-22T17:20:20+0000')
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': order_id,
        'created_time': created_time.isoformat(),
        'destinations': DEFAULT_DESTINATIONS,
        'idempotency_token': 'test_token_123',
    }
    query = {'_id': request['orderid']}
    order_proc = db.order_proc.find_one(query)
    assert order_proc is not None
    assert now > order_proc['updated']

    response = taxi_protocol.post(
        '3.0/changedestinations', request, headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200

    assert mock_order_core.post_event_times_called == 1
    assert mock_order_core.last_call_idempotency_token == 'test_token_123'


@pytest.mark.parametrize(
    'order_points, changes, expect_fixed_price_unset, altpin',
    [
        ([], [], False, False),
        ([], [[[37.588630, 55.734367]]], True, False),
        ([[37.588630, 55.734367]], [[[37.588630, 55.734367]]], False, False),
        (
            [[37.588630, 55.734367]],
            [[[37.588630, 55.734367]], [[37.588630, 55.734367]]],
            False,
            False,
        ),
        ([[37.588630, 55.734367]], [[[37.588663, 55.735140]]], False, False),
        ([[37.588663, 55.735140]], [[[37.588658, 55.735809]]], False, False),
        ([[37.588630, 55.734367]], [[[37.588658, 55.735809]]], True, False),
        (
            [[37.588630, 55.734367]],
            [[[37.588663, 55.735140]], [[37.588658, 55.735809]]],
            True,
            False,
        ),
        (
            [[37.588630, 55.734367]],
            [
                [[37.588635, 55.734369]],
                [[37.588652, 55.735000]],
                [[37.589924, 55.734696]],
            ],
            False,
            False,
        ),
        (
            [[37.588630, 55.734367]],
            [[[37.588652, 55.735000]]],  # distance between = 50 < 70 < 100
            True,
            True,
        ),
        (
            [[37.588630, 55.734367]],
            [[[38.588630, 56.734367]], [[37.588631, 55.734368]]],
            True,
            False,
        ),
        ([[1, 1]], [[[1, 1]]], False, False),
        ([[37, 55], [37, 55]], [[[37, 55], [37, 55]]], False, False),
        ([[37, 55]], [[[37, 55], [37, 55]]], True, False),
        ([[37, 55], [37, 55]], [[[37, 55]]], True, False),
    ],
)
@pytest.mark.parametrize('performer_not_in_candidates', [False, True])
@pytest.mark.config(
    FIXED_PRICE_MAX_CHANGE_DESTINATION_DISTANCE=100,
    REQUEST_NEW_PRICE_AT_CHANGE_DESTINATIONS=True,
)
@pytest.mark.experiments3(
    is_config=True,
    name='fixed_price_max_change_destination_distance_altpin',
    consumers=['protocol/changedestinations'],
    clauses=[],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={'distance': 50},
)
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_changedestinations_fixed_price(
        order_points,
        changes,
        expect_fixed_price_unset,
        altpin,
        taxi_protocol,
        mockserver,
        load_json,
        db,
        notify_on_change_version_switch,
        performer_not_in_candidates,
):
    @mockserver.json_handler('/tracker/position')
    def get_position(_request):
        if performer_not_in_candidates:
            assert 'current_driver_position' not in request.json
        else:
            assert 'current_driver_position' in request.json

    if performer_not_in_candidates:
        order_id = '1234567890124456b890123456789021'
    else:
        order_id = '1234567890124456b890123456789012'
    geo_template = {
        'country': 'Russian Federation',
        'description': 'Moscow, Russian Federation',
        'exact': False,
        'fullname': 'Russian Federation, Moscow, Kropotkinsky Lane',
        'locality': 'Moscow',
        'object_type': 'другое',
        'short_text': 'Kropotkinsky Lane',
        'thoroughfare': 'Kropotkinsky Lane',
        'type': 'address',
        'use_geopoint': True,
    }
    if altpin:
        db.order_proc.update(
            {'_id': order_id},
            {'$set': {'order.request.alternative_type': 'altpin_b'}},
        )
    db.order_proc.update(
        {'_id': order_id},
        {
            '$set': {
                'order.request.destinations': [
                    dict(geopoint=point, **geo_template)
                    for point in order_points
                ],
            },
        },
    )

    @mockserver.json_handler(
        '/pricing_data_preparer/v1/recalc_fixed_price/destination_changed',
    )
    def pricing_mock(req):
        return {}

    @mockserver.json_handler(
        '/pricing_data_preparer/internal/v1/backend_variables',
    )
    def pricing_backend_variables_mock(req):
        req_data = json.loads(req.get_data())
        assert req_data['new_value'] == {
            'variable_id': 'waypoints_count',
            'waypoints_count': len(change) + 1,
        }
        return {}

    for change in changes:
        request = {
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': order_id,
            'created_time': '2017-08-01T10:00:00+0000',
            'destinations': [
                dict(geopoint=point, **geo_template) for point in change
            ],
        }
        response = taxi_protocol.post('3.0/changedestinations', request)
        assert response.status_code == 200, response.content

    order = db.order_proc.find_one(order_id)['order']
    fixed_price = order['fixed_price']
    if expect_fixed_price_unset:
        assert 'price' not in fixed_price
        assert 'driver_price' not in fixed_price
        assert order['fixed_price_discard_reason'] == 'destinations_changed'
        assert pricing_mock.times_called == len(changes)
    else:
        assert fixed_price['price'] == 100
        assert fixed_price['driver_price'] == 100


@pytest.mark.parametrize(
    'created_time,route_type',
    [
        (123, 'address'),
        ('2013-03-13T08:57:22.123', 'address'),
        ('2017-07-22T17:20:15+0000', 'organ1zat1on'),
    ],
    ids=[
        'created_time is not a string',
        'wrong time format',
        'wrong routepoint type',
    ],
)
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_parse_created_time(
        taxi_protocol,
        created_time,
        route_type,
        mockserver,
        load_json,
        notify_on_change_version_switch,
):
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': '8c83b49edb274ce0992f337061041111',
        'created_time': created_time,
        'destinations': [
            {
                'country': 'Russian Federation',
                'description': 'Moscow, Russian Federation',
                'fullname': 'Russian Federation, Moscow, Kropotkinsky Lane',
                'geopoint': [37.59090617361221, 55.73921060048498],
                'locality': 'Moscow',
                'object_type': 'другое',
                'short_text': 'Kropotkinsky Lane',
                'thoroughfare': 'Kropotkinsky Lane',
                'type': route_type,
            },
        ],
    }
    response = taxi_protocol.post('3.0/changedestinations', request)
    assert response.status_code == 400
    data = response.json()
    assert data['error']['text'] == 'Bad Request'


@pytest.mark.parametrize(
    'orderid,expected_status,error_text',
    [
        ('8c83b49edb274ce0992f337061043333', 404, 'order is finished'),
        ('8c83b49edb274ce0992f337061040000', 404, 'order_proc not found'),
        (
            '8c83b49edb274ce0992f337061044444',
            404,
            'zone not found in tariff settings',
        ),
        (
            '8c83b49edb274ce0992f337061045555',
            406,
            'forbidden_by_city_with_pre_cost',
        ),
        (
            '8c83b49edb274ce0992f337061042222',
            409,
            'last change time stamp > current change time stamp',
        ),
        (
            '8c83b49edb274ce0992f337061042222',
            409,
            'last change time stamp > current change time stamp',
        ),
    ],
    ids=[
        'order is finished',
        'order does not exist',
        'nearest zone was removed',
        'is cant change destinations',
        'destinations is already applied',
        'new time stamp less than old time stamp',
    ],
)
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_errors(
        taxi_protocol,
        orderid,
        expected_status,
        error_text,
        mockserver,
        load_json,
        notify_on_change_version_switch,
):
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': orderid,
        'created_time': '2017-07-22T17:00:00+0000',
        'destinations': [
            {
                'country': 'Russian Federation',
                'description': 'Moscow, Russian Federation',
                'fullname': 'Russian Federation, Moscow, Kropotkinsky Lane',
                'geopoint': [37.59090617361221, 55.73921060048498],
                'locality': 'Moscow',
                'object_type': 'другое',
                'short_text': 'Kropotkinsky Lane',
                'thoroughfare': 'Kropotkinsky Lane',
                'type': 'address',
            },
        ],
    }
    response = taxi_protocol.post('3.0/changedestinations', request)
    assert response.status_code == expected_status
    data = response.json()
    assert data['error']['text'] == error_text


@pytest.mark.parametrize(
    'order_id,zone_available,expect_corp_payment_methods',
    [
        ('8c83b49edb274ce0992f337061042222', True, True),
        ('8c83b49edb274ce0992f337061042222', False, True),
        ('8888b49edb274ce0992f337061043333', True, False),
    ],
)
@pytest.mark.config(
    APPLICATION_TO_CORP_SOURCE_MAP={'android': 'android'},
    CORP_INTEGRATION_CLIENT_PAYMENTMETHODS_ENABLED=True,
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'protocol', 'dst': 'corp-integration-api'}],
)
@pytest.mark.now('2017-07-22T17:20:15+0000')
@NOTIFY_ON_CHANGE_VERSION_SWITCH
def test_changedestinations_corp_paymentmethods(
        taxi_protocol,
        db,
        mockserver,
        load_json,
        tvm2_client,
        zone_available,
        expect_corp_payment_methods,
        order_id,
        notify_on_change_version_switch,
):
    ticket = 'ticket'
    tvm2_client.set_ticket(json.dumps({'24': {'ticket': ticket}}))

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return load_json('yamaps_kropotkinsky.json')

    @mockserver.json_handler('/corp_integration_api/corp_paymentmethods')
    def mock_corp_paymentmethods(request):
        data = json.loads(request.get_data())
        assert request.headers['X-Ya-Service-Ticket'] == ticket
        assert data['source']['app'] == 'android'
        assert data['client_id'] == '327eba75e92c4603933981bbf3216889'
        assert data['identity']['phone_id'] == '5714f45e98956f06baaae3d4'
        assert (
            data['identity']['personal_phone_id'] == 'test_personal_phone_id'
        )
        assert data['route'][0]['geopoint'] == [37.59, 55.73]
        assert data['route'][1]['geopoint'] == [
            37.59090617361221,
            55.73921060048498,
        ]
        assert data['combo_order'] == {'delivery_id': 'delivery1'}
        return mockserver.make_response(
            json.dumps(
                {
                    'methods': [
                        {
                            'client_id': '327eba75e92c4603933981bbf3216889',
                            'zone_available': zone_available,
                            'zone_disable_reason': 'reason',
                        },
                    ],
                },
            ),
        )

    created_time = dateutil.parser.parse('2017-07-22T17:20:20+0000')
    request = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'orderid': order_id,
        'created_time': created_time.isoformat(),
        'destinations': [
            {
                'country': 'Russian Federation',
                'description': 'Moscow, Russian Federation',
                'fullname': 'Russian Federation, Moscow, Kropotkinsky Lane',
                'geopoint': [37.59090617361221, 55.73921060048498],
                'locality': 'Moscow',
                'object_type': 'другое',
                'short_text': 'Kropotkinsky Lane',
                'thoroughfare': 'Kropotkinsky Lane',
                'extra_data': {'floor': '4', 'apartment': '10', 'porch': '20'},
                'type': 'address',
                'uri': 'ymapsbm1://geo?ll=37.642%2C55.738',
            },
        ],
    }

    response = taxi_protocol.post(
        '3.0/changedestinations', request, headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200 if zone_available else 406
    if expect_corp_payment_methods:
        assert mock_corp_paymentmethods.times_called == 1
    else:
        assert mock_corp_paymentmethods.times_called == 0
