import datetime
import json
import time
import xml.etree.ElementTree as ET

import bson
import pytest


MAIN_PHONE = '+79031520355'
EXTRA_PHONE = '+79031520356'
A_PHONE = '+79030000001'
B_PHONE = '+79030000002'

MAIN_PHONE_ID = '5714f45e98956f06baaae3d4'
EXTRA_PHONE_ID = '5714f45e98956f06baaae3d5'
A_PHONE_ID = '5714f45e98956f06baaae3d6'
B_PHONE_ID = '5714f45e98956f06baaae3d7'


@pytest.mark.parametrize(
    'extra_type, callee_phone',
    [(None, EXTRA_PHONE), ('main', MAIN_PHONE), ('extra', EXTRA_PHONE)],
)
def test_voiceforwarding_extra(
        taxi_protocol, mockserver, extra_type, callee_phone, db,
):
    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {
            '$set': {
                'order.request.extra_user_phone_id': bson.ObjectId(
                    '5714f45e98956f06baaae3d5',
                ),
            },
        },
    )
    params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'for': 'driver',
        'clid': '999012',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
    }
    if extra_type:
        params['type'] = extra_type

    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        req_data = json.loads(request.get_data())
        assert req_data['caller'] == 'driver'
        assert req_data['callee'] == 'passenger'
        assert req_data['callee_phone'] == callee_phone
        return {'phone': '+75557775522', 'ext': '2323'}

    response = taxi_protocol.post('1.x/voiceforwarding', params=params)

    assert response.status_code == 200
    xml_root = ET.fromstring(response.text)
    assert len(xml_root) == 1
    correct_values = {
        'Orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'Phone': '+75557775522',
        'Ext': '2323',
    }
    checks_count = 0
    for param in xml_root[0]:
        if param.tag in correct_values:
            assert correct_values[param.tag] == param.text
            del correct_values[param.tag]
            checks_count += 1
    assert checks_count == 3


@pytest.mark.config(VGW_TIMEOUT_MS=1000)
def test_voiceforwarding_timeout(taxi_protocol, mockserver):
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        req_data = json.loads(request.get_data())
        assert req_data['callee_phone'] == MAIN_PHONE
        assert req_data['caller'] == 'driver'
        assert req_data['callee'] == 'passenger'
        time.sleep(2)  # 2 seconds
        return {'phone': '+75557775522', 'ext': '2323'}

    response = taxi_protocol.post(
        '1.x/voiceforwarding',
        params={
            'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
            'for': 'driver',
            'clid': '999012',
            'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        },
    )

    assert response.status_code == 200
    xml_root = ET.fromstring(response.text)
    assert len(xml_root) == 1
    correct_values = {
        'Orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'Phone': MAIN_PHONE,
        'Ext': None,
    }
    checks_count = 0
    for param in xml_root[0]:
        if param.tag in correct_values:
            assert correct_values[param.tag] == param.text
            del correct_values[param.tag]
            checks_count += 1
    assert checks_count == 3


@pytest.mark.config(VGW_PROTOCOL_BLACKLISTED_SETTINGS={'__default__': True})
@pytest.mark.config(VGW_TIMEOUT_MS=1000)
def test_voiceforwarding_not_check_blacklist(taxi_protocol, mockserver):
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        req_data = json.loads(request.get_data())
        assert not req_data['check_blacklisted']
        return {'phone': '+75557775522', 'ext': '2323'}

    response = taxi_protocol.post(
        '1.x/voiceforwarding',
        params={
            'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
            'for': 'driver',
            'clid': '999012',
            'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        },
    )

    assert response.status_code == 200


@pytest.mark.config(VGW_TIMEOUT_MS=5000)
def test_voiceforwarding_no_500(taxi_protocol, mockserver, testpoint):
    """
    Regression for TAXIBACKEND-5252
    """

    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        req_data = json.loads(request.get_data())
        assert '+79031520355' == req_data['callee_phone']
        assert 'driver' == req_data['caller']
        return {'phone': '+75557775522', 'ext': '2323'}

    @testpoint('voicegateways::gatewayobtained')
    def do_parallel_call(data):
        assert data is None
        parallel_response = taxi_protocol.post(
            '1.x/voiceforwarding',
            params={
                'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
                'for': 'driver',
                'clid': '999012',
                'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
            },
        )
        assert parallel_response.status_code == 409
        assert parallel_response.json() == {
            'error': {'text': 'can not create new draft'},
        }

    # Call handler
    response = taxi_protocol.post(
        '1.x/voiceforwarding',
        params={
            'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
            'for': 'driver',
            'clid': '999012',
            'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        },
    )

    # Check test point was called
    assert do_parallel_call.times_called == 1

    # Check response
    assert response.status_code == 200
    xml_root = ET.fromstring(response.text)
    assert len(xml_root) == 1
    correct_values = {
        'Orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'Phone': '+75557775522',
        'Ext': '2323',
    }
    checks_count = 0
    for param in xml_root[0]:
        if param.tag in correct_values:
            assert correct_values[param.tag] == param.text
            del correct_values[param.tag]
            checks_count += 1
    assert checks_count == 3


@pytest.mark.parametrize(
    'tariff_zone,expected_phone,expected_ext',
    [
        ('moscow', '+75557775522', '2323'),
        ('almaty', '+79031520355', None),
        ('unknown_zone', '+79031520355', None),
    ],
)
@pytest.mark.config(
    VGW_DRIVER_VOICE_FORWARDING_DISABLE_TARIFFS_BY_COUNTRY={
        '__default__': [],
        'kaz': ['econom'],
    },
)
@pytest.mark.filldb(orders='zone_change', order_proc='zone_change')
def test_voiceforwarding_disable_by_country(
        taxi_protocol,
        mockserver,
        db,
        tariff_zone,
        expected_phone,
        expected_ext,
):
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        req_data = json.loads(request.get_data())
        assert req_data['callee_phone'] == '+79031520355'
        assert req_data['caller'] == 'driver'
        return {'phone': '+75557775522', 'ext': '2323'}

    order_alias_id = 'da60d02916ae4a1a91eafa3a1a8ed04d'

    db.orders.update(
        {'performer.taxi_alias.id': order_alias_id, '_shard_id': 0},
        {'$set': {'nz': tariff_zone}},
    )
    db.order_proc.update(
        {
            '_id': '8c83b49edb274ce0992f337061047375',
            'performer.alias_id': order_alias_id,
        },
        {'$set': {'order.nz': tariff_zone}},
    )

    response = taxi_protocol.post(
        '1.x/voiceforwarding',
        params={
            'orderid': order_alias_id,
            'for': 'driver',
            'clid': '999012',
            'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        },
    )

    assert response.status_code == 200
    xml_root = ET.fromstring(response.text)
    assert len(xml_root) == 1
    correct_values = {
        'Orderid': order_alias_id,
        'Phone': expected_phone,
        'Ext': expected_ext,
    }
    checks_count = 0
    for param in xml_root[0]:
        if param.tag in correct_values:
            assert correct_values[param.tag] == param.text
            del correct_values[param.tag]
            checks_count += 1
    assert checks_count == 3


@pytest.mark.parametrize(
    'caller, caller_phone, type, forwarding_id',
    [
        (
            'driver',
            '+79100000000',
            'onuser4driver',
            'da60d02916ae4a1a91eafa3a1a8ed04d00000000',
        ),
        (
            'dispatcher',
            '+79031524203',
            'onuser4dispatch',
            'da60d02916ae4a1a91eafa3a1a8ed04d01000000',
        ),
    ],
)
@pytest.mark.now('2018-02-25T00:00:00')
@pytest.mark.filldb(order_proc='vgw_api')
def test_voiceforwarding_vgw_api(
        taxi_protocol,
        mockserver,
        db,
        caller,
        caller_phone,
        type,
        forwarding_id,
):
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_forwardings(request):
        req_data = json.loads(request.get_data())
        assert req_data['caller'] == caller
        assert req_data['callee'] == 'passenger'
        assert req_data['caller_phone'] == caller_phone
        assert req_data['callee_phone'] == '+79031520355'
        assert (
            req_data['external_ref_id'] == 'da60d02916ae4a1a91eafa3a1a8ed04d'
        )
        assert len(req_data['nonce']) == 32
        assert req_data['consumer'] == 2
        assert req_data['call_location'] == [
            37.58917997300821,
            55.73341076871702,
        ]

        return {'phone': '+75557775522', 'ext': '2323'}

    response = taxi_protocol.post(
        '1.x/voiceforwarding',
        params={
            'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
            'for': caller,
            'clid': '999012',
            'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        },
    )

    assert response.status_code == 200
    xml_root = ET.fromstring(response.text)
    assert len(xml_root) == 1
    correct_values = {
        'Orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'Phone': '+75557775522',
        'Ext': '2323',
    }
    checks_count = 0
    for param in xml_root[0]:
        if param.tag in correct_values:
            assert correct_values[param.tag] == param.text
            del correct_values[param.tag]
            checks_count += 1
    assert checks_count == 3

    # Check database
    assert db.order_talks.count() == 1
    talks = db.order_talks.find_one(
        {'_id': '8c83b49edb274ce0992f337061047375'},
    )
    #  We can't mock $currentDate now, so check it separately
    item_updated = talks['forwardings'][0].pop('updated')
    assert abs(datetime.datetime.utcnow() - item_updated) < datetime.timedelta(
        minutes=10,
    )
    doc_updated = talks.pop('updated')
    assert abs(datetime.datetime.utcnow() - doc_updated) < datetime.timedelta(
        minutes=10,
    )
    #  Check equality for other
    assert talks == {
        '_id': '8c83b49edb274ce0992f337061047375',
        'forwardings': [
            {
                'driver_id': '999012_a5709ce56c2740d9a536650f5390de0b',
                'gateway_id': 'vgw-api',
                'created': datetime.datetime(2018, 2, 25, 0, 0),
                'expires': datetime.datetime(2018, 2, 25, 0, 15),
                'callee': '+79031520355',
                'forwarding_id': forwarding_id,
                'phone': '+75557775522',
                'ext': '2323',
                'type': type,
            },
        ],
        'forwardings_active': [forwarding_id],
        'talks': [],
    }


@pytest.mark.now('2018-02-25T00:00:00')
@pytest.mark.config(VGW_USE_EXPERIMENTS3=True)
@pytest.mark.filldb(order_proc='experiments3')
@pytest.mark.experiments3(filename='experiments3_01.json')
def test_voiceforwarding_softswitch_experiments3_normal(
        taxi_protocol, mockserver,
):
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        req_data = json.loads(request.get_data())
        assert req_data['callee_phone'] == '+79031520355'
        assert req_data['caller'] == 'driver'
        return {'phone': '+75557775522', 'ext': '2323'}

    response = taxi_protocol.post(
        '1.x/voiceforwarding',
        params={
            'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
            'for': 'driver',
            'clid': '999012',
            'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        },
    )

    assert response.status_code == 200
    xml_root = ET.fromstring(response.text)
    assert len(xml_root) == 1
    correct_values = {
        'Orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'Phone': '+75557775522',
        'Ext': '2323',
    }
    checks_count = 0
    for param in xml_root[0]:
        if param.tag in correct_values:
            assert correct_values[param.tag] == param.text
            del correct_values[param.tag]
            checks_count += 1
    assert checks_count == 3


@pytest.mark.now('2018-02-25T00:00:00')
@pytest.mark.config(VGW_USE_EXPERIMENTS3=True)
@pytest.mark.filldb(order_proc='experiments3')
@pytest.mark.experiments3(filename='experiments3_01.json')
def test_voiceforwarding_softswitch_experiments3_fail(taxi_protocol):
    response = taxi_protocol.post(
        '1.x/voiceforwarding',
        params={
            'orderid': 'da60d02916ae4a1a91eafa3a1a8ed44d',
            'for': 'driver',
            'clid': '999012',
            'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        },
    )

    assert response.status_code == 200
    xml_root = ET.fromstring(response.text)
    assert len(xml_root) == 1
    correct_values = {
        'Orderid': 'da60d02916ae4a1a91eafa3a1a8ed44d',
        'Phone': '+79031520355',
        'Ext': None,
    }
    checks_count = 0
    for param in xml_root[0]:
        if param.tag in correct_values:
            assert correct_values[param.tag] == param.text
            del correct_values[param.tag]
            checks_count += 1
    assert checks_count == 3

    response = taxi_protocol.post(
        '1.x/voiceforwarding',
        params={
            'orderid': 'da60d02916ae4a1a91eafa3a1a8ed44d',
            'for': 'driver',
            'clid': '999012',
            'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        },
    )

    assert response.status_code == 200
    xml_root = ET.fromstring(response.text)
    assert len(xml_root) == 1
    correct_values = {
        'Orderid': 'da60d02916ae4a1a91eafa3a1a8ed44d',
        'Phone': '+79031520355',
        'Ext': None,
    }
    checks_count = 0
    for param in xml_root[0]:
        if param.tag in correct_values:
            assert correct_values[param.tag] == param.text
            del correct_values[param.tag]
            checks_count += 1
    assert checks_count == 3


@pytest.mark.parametrize(
    ('deaf', 'has_forwarding_rule'), ((True, False), (False, True)),
)
@pytest.mark.now('2018-02-25T00:00:00')
@pytest.mark.config(VGW_USE_EXPERIMENTS3=True)
@pytest.mark.filldb(order_proc='experiments3')
@pytest.mark.experiments3(filename='experiments3_deaf_disabled.json')
def test_voiceforwarding_experiments3_deaf_driver(
        taxi_protocol, mockserver, deaf, has_forwarding_rule,
):

    PHONE_FROM_FORWARDING = '+75557775522'
    EXT_FROM_FORWARDING = '2323'
    PHONE_TO_MASK = '+79031520355'

    if deaf:
        response_phone = PHONE_TO_MASK
        response_ext = None
    else:
        response_phone = PHONE_FROM_FORWARDING
        response_ext = EXT_FROM_FORWARDING

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def mock_driver_profiles(request):
        doc = json.loads(request.get_data())
        assert doc['id_in_set'] == [
            '73c9925b9d244b26aa2985423828cd6e'
            '_a5709ce56c2740d9a536650f5390de0b',
        ]
        assert doc['projection'] == ['data.is_deaf']
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'some_unnecessary_id',
                    'data': {'is_deaf': deaf},
                },
            ],
        }

    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        req_data = json.loads(request.get_data())
        assert req_data['callee_phone'] == PHONE_TO_MASK
        assert req_data['caller'] == 'driver'
        return {'phone': PHONE_FROM_FORWARDING, 'ext': EXT_FROM_FORWARDING}

    response = taxi_protocol.post(
        '1.x/voiceforwarding',
        params={
            'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
            'for': 'driver',
            'clid': '999012',
            'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        },
    )

    assert response.status_code == 200
    xml_root = ET.fromstring(response.text)
    assert len(xml_root) == 1
    correct_values = {
        'Orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'Phone': response_phone,
        'Ext': response_ext,
    }
    checks_count = 0
    for param in xml_root[0]:
        if param.tag in correct_values:
            assert correct_values[param.tag] == param.text
            del correct_values[param.tag]
            checks_count += 1
    assert checks_count == 3


@pytest.mark.now('2018-02-25T00:00:00')
@pytest.mark.config(VGW_USE_EXPERIMENTS3=True)
@pytest.mark.filldb(order_proc='experiments3')
@pytest.mark.experiments3(filename='experiments3_park_id_disabled.json')
def test_voiceforwarding_experiments3_park_id_disabled(taxi_protocol):

    response = taxi_protocol.post(
        '1.x/voiceforwarding',
        params={
            'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
            'for': 'driver',
            'clid': '999012',
            'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        },
    )

    assert response.status_code == 200
    xml_root = ET.fromstring(response.text)
    assert len(xml_root) == 1
    correct_values = {
        'Orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'Phone': '+79031520355',
        'Ext': None,
    }
    checks_count = 0
    for param in xml_root[0]:
        if param.tag in correct_values:
            assert correct_values[param.tag] == param.text
            del correct_values[param.tag]
            checks_count += 1
    assert checks_count == 3


@pytest.mark.now('2018-02-25T00:00:00')
@pytest.mark.config(VGW_USE_EXPERIMENTS3=True)
@pytest.mark.filldb(order_proc='experiments3')
@pytest.mark.experiments3(filename='experiments3_driver_uuid_disabled.json')
def test_voiceforwarding_experiments3_driver_uuid_disabled(taxi_protocol):

    response = taxi_protocol.post(
        '1.x/voiceforwarding',
        params={
            'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
            'for': 'driver',
            'clid': '999012',
            'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        },
    )

    assert response.status_code == 200
    xml_root = ET.fromstring(response.text)
    assert len(xml_root) == 1
    correct_values = {
        'Orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'Phone': '+79031520355',
        'Ext': None,
    }
    checks_count = 0
    for param in xml_root[0]:
        if param.tag in correct_values:
            assert correct_values[param.tag] == param.text
            del correct_values[param.tag]
            checks_count += 1
    assert checks_count == 3


@pytest.mark.parametrize(
    'caller, caller_phone, type, forwarding_id',
    [
        (
            'driver',
            '+79100000000',
            'onuser4driver',
            'da60d02916ae4a1a91eafa3a1a8ed04d00000000',
        ),
        (
            'dispatcher',
            '+79031524203',
            'onuser4dispatch',
            'da60d02916ae4a1a91eafa3a1a8ed04d01000000',
        ),
    ],
)
@pytest.mark.parametrize(
    'accept, content_type',
    [
        ('', 'application/xml; charset=utf-8'),
        ('backward_compatibility', 'application/xml; charset=utf-8'),
        ('application/xml', 'application/xml; charset=utf-8'),
        ('application/json', 'application/json; charset=utf-8'),
    ],
)
@pytest.mark.now('2018-02-25T00:00:00')
@pytest.mark.config(
    VGW_MIN_EXPIRATION_SECONDS=300,
    VGW_NEW_FWD_EXPIRATION_SECONDS=900,
    VGW_USE_VGW_API=True,
)
@pytest.mark.filldb(order_proc='vgw_api_full')
def test_voiceforwarding_vgw_api_full(
        taxi_protocol,
        mockserver,
        db,
        caller,
        caller_phone,
        type,
        forwarding_id,
        accept,
        content_type,
):
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_forwardings(request):
        req_data = json.loads(request.get_data())
        assert req_data['caller'] == caller
        assert req_data['callee'] == 'passenger'
        assert req_data['caller_phone'] == caller_phone
        assert req_data['callee_phone'] == '+79031520355'
        assert (
            req_data['external_ref_id'] == '8c83b49edb274ce0992f337061047375'
        )
        assert len(req_data['nonce']) == 32
        assert req_data['consumer'] == 2
        assert req_data['call_location'] == [
            37.58917997300821,
            55.73341076871702,
        ]
        assert req_data['min_ttl'] == 300
        assert req_data['new_ttl'] == 900

        return {'phone': '+75557775522', 'ext': '2323'}

    response = taxi_protocol.post(
        '1.x/voiceforwarding',
        headers={'Accept': accept},
        params={
            'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
            'for': caller,
            'clid': '999012',
            'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        },
    )

    assert response.status_code == 200
    assert response.headers['Content-Type'] == content_type

    correct_values = {
        'Orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'Phone': '+75557775522',
        'Ext': '2323',
        'TtlSeconds': 900,
    }

    if content_type == 'application/xml; charset=utf-8':
        xml_root = ET.fromstring(response.text)
        assert len(xml_root) == 1

        checks_count = 0
        for param in xml_root[0]:
            if param.tag in correct_values:
                assert str(correct_values[param.tag]) == param.text
                del correct_values[param.tag]
                checks_count += 1
        assert checks_count == 4
    else:
        assert response.json() == {
            'forwardings': [
                {
                    'ext': correct_values['Ext'],
                    'order_id': correct_values['Orderid'],
                    'phone': correct_values['Phone'],
                    'ttl_seconds': correct_values['TtlSeconds'],
                },
            ],
        }

    # Check database
    assert db.order_talks.count() == 0


@pytest.mark.config(VGW_USE_EXPERIMENTS3=True, VGW_USE_VGW_API=True)
@pytest.mark.experiments3(filename='experiments3_mtt_enabled.json')
def test_voiceforwarding_vgw_enabled_kwargs(taxi_protocol, mockserver, db):
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        req_data = json.loads(request.get_data())
        assert req_data['callee_phone'] == '+79031520355'
        assert req_data['caller'] == 'driver'
        return {'phone': '+75557775522', 'ext': '2323'}

    mtt_enabled = False

    @mockserver.json_handler('/vgw-api/v1/voice_gateways')
    def mock_voice_gateways(request):
        nonlocal mtt_enabled
        print('mtt_enabled = {}', mtt_enabled)
        return [{'id': 'mtt', 'enabled': mtt_enabled}]

    response = taxi_protocol.post(
        '1.x/voiceforwarding',
        params={
            'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
            'for': 'driver',
            'clid': '999012',
            'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        },
    )

    assert response.status_code == 200
    xml_root = ET.fromstring(response.text)
    assert len(xml_root) == 1
    correct_values = {
        'Orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'Phone': '+79031520355',
        'Ext': None,
    }
    checks_count = 0
    for param in xml_root[0]:
        if param.tag in correct_values:
            assert correct_values[param.tag] == param.text
            del correct_values[param.tag]
            checks_count += 1
    assert checks_count == 3

    mtt_enabled = True

    taxi_protocol.invalidate_caches()

    response = taxi_protocol.post(
        '1.x/voiceforwarding',
        params={
            'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
            'for': 'driver',
            'clid': '999012',
            'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        },
    )

    assert response.status_code == 200
    xml_root = ET.fromstring(response.text)
    assert len(xml_root) == 1
    correct_values = {
        'Orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'Phone': '+75557775522',
        'Ext': '2323',
    }
    checks_count = 0
    for param in xml_root[0]:
        if param.tag in correct_values:
            assert correct_values[param.tag] == param.text
            del correct_values[param.tag]
            checks_count += 1
    assert checks_count == 3


@pytest.mark.parametrize('tariff', ['business', 'econom'])
def test_voiceforwarding_send_tariff_performer(
        taxi_protocol, mockserver, tariff, db,
):
    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {'$set': {'order.performer.tariff.class': tariff}},
    )
    params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'for': 'driver',
        'clid': '999012',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
    }

    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        req_data = json.loads(request.get_data())

        service_level = req_data['service_level']
        assert service_level == tariff

        return {'phone': '+75557775522', 'ext': '2323'}

    response = taxi_protocol.post('1.x/voiceforwarding', params=params)

    assert response.status_code == 200


@pytest.mark.parametrize(
    'extra_type, order_with_phones_in_route, callee_phone',
    [
        ('main', True, A_PHONE),
        ('extra', True, B_PHONE),
        (None, True, MAIN_PHONE),
        ('main', False, MAIN_PHONE),
        ('extra', False, EXTRA_PHONE),
        (None, False, EXTRA_PHONE),
    ],
)
@pytest.mark.config(
    VGW_PHONES_FROM_ROUTE_RULES={'econom': {'main': 0, 'extra': 1}},
)
def test_voiceforwarding_phones_from_route(
        taxi_protocol,
        mockserver,
        db,
        extra_type,
        order_with_phones_in_route,
        callee_phone,
):

    if order_with_phones_in_route:
        phone_field = 'extra_data.contact_phone_id'
        db.order_proc.update(
            {'_id': '8c83b49edb274ce0992f337061047375'},
            {
                '$set': {
                    'order.request.source.%s'
                    % phone_field: (bson.ObjectId(A_PHONE_ID)),
                    'order.request.destinations.0.%s'
                    % phone_field: (bson.ObjectId(B_PHONE_ID)),
                },
            },
        )
    else:
        db.order_proc.update(
            {'_id': '8c83b49edb274ce0992f337061047375'},
            {
                '$set': {
                    'order.request.extra_user_phone_id': bson.ObjectId(
                        EXTRA_PHONE_ID,
                    ),
                },
            },
        )

    params = {
        'orderid': 'da60d02916ae4a1a91eafa3a1a8ed04d',
        'for': 'driver',
        'clid': '999012',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
    }
    if extra_type:
        params['type'] = extra_type

    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_redirections(request):
        req_data = json.loads(request.get_data())
        assert req_data['caller'] == 'driver'
        assert req_data['callee'] == 'passenger'
        assert req_data['callee_phone'] == callee_phone
        return {'phone': '+75557775522', 'ext': '2323'}

    response = taxi_protocol.post('1.x/voiceforwarding', params=params)

    assert response.status_code == 200
