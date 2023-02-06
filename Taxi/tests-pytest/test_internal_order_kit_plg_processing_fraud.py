import copy
import bson
import json
import pytest


from taxi.core import async
from taxi.internal.dbh import order_proc
from taxi.internal.dbh import user_phones
from taxi.internal.order_kit.plg.fraud_expire import (
    mark_as_user_fraud_and_expired
)


@pytest.fixture(autouse=True)
def patch_userapi_phone_id(patch):
    @patch('taxi.internal.userapi.get_user_phone')
    @async.inline_callbacks
    def impl(
            phone_id,
            primary_replica=False,
            fields=None,
            log_extra=None,
    ):
        doc = yield user_phones.Doc.find_one_by_id(
            phone_id,
            secondary=not primary_replica,
            fields=fields,
        )
        async.return_value(doc)


def _make_proc_and_phone(data):
    proc = order_proc.Doc()
    proc._id = 'order_proc1'
    proc.order.request.classes = ['econom']
    proc.status = order_proc.STATUS_PENDING
    proc.order.user_id = data['user_id']
    proc.order.nearest_zone = data['nz']
    proc.processing.version = 1
    if data.get('is_multiorder'):
        proc.order.multiorder_order_number = 3
    if 'request' in data:
        proc.order.request = data['request']
    if 'payment_tech' in data:
        proc.payment_tech = data['payment_tech']
    if 'user_agent' in data:
        proc.order.user_agent = data['user_agent']
    return proc


@pytest.inline_callbacks
def _check(data, frauder, patch):

    @patch('taxi.internal.dbh.user_phones.Doc.find_one_by_id')
    @async.inline_callbacks
    def test_find_phone_doc_by_id(phone_id, **kwargs):
        phone_doc = yield user_phones.Doc()
        phone_doc._id = bson.ObjectId('01f9c4506315954f4eea78fb')
        phone_doc.stat.complete = data['complete']
        phone_doc.stat.total = data['total']
        is_extra_phone_id = (phone_id == bson.ObjectId('5c0e2616030553e658070fe8'))
        phone_doc.phone = data['extra_phone'] if is_extra_phone_id else data['phone']
        async.return_value(phone_doc)

    new_proc = yield mark_as_user_fraud_and_expired(
        proc=_make_proc_and_phone(data),
        log_extra=None,
    )
    if frauder:
        assert new_proc.order.user_fraud is True
        assert new_proc.status == 'finished'
    else:
        assert new_proc.status == 'pending'


@pytest.mark.parametrize('data,afs_frauder,old_frauder,frauder', [
    (
        {
            'user_id': 'user_android',
            'complete': 2,
            'total': 10,
            'phone': '89162991414',
            'extra_phone': '89162991415',
            'user_phone_id': bson.ObjectId(
                '01f9c4506315954f4eea78fb',
            ),
            'yandex_uid_type': 'phonish',
            'nz': 'moscow',
            'request': {
                'extra_user_phone_id': bson.ObjectId(
                    '5c0e2616030553e658070fe8'
                ),
                'comment': 'speed - 300; wait - 2;',
                'class': ['econom'],
                'requirements': {
                    "yellowcarnumber": True,
                },
            },
            'payment_tech': {
                'type': 'card',
            },
            'is_multiorder': True,
        },
        False,
        False,
        True,
    ),
    (
        {
            'user_id': 'user_android',
            'complete': 3,
            'total': 10,
            'phone': '89162991414',
            'nz': 'moscow',
        },
        False,
        False,
        False,
    ),
    (
        {
            'user_id': 'user_android',
            'complete': 3,
            'total': 10,
            'phone': '89172991414',
            'nz': 'moscow',
        },
        False,
        False,
        False,
    ),
    (
        {
            'user_id': 'user_web',
            'complete': 2,
            'total': 10,
            'phone': '89202991414',
            'nz': 'ekb',
        },
        False,
        False,
        True,
    ),
    (
        {
            'user_id': 'user_web',
            'complete': 3,
            'total': 10,
            'phone': '89202991414',
            'nz': 'ekb',
        },
        False,
        False,
        False,
    ),
    (
        {
            'user_id': 'user_web',
            'complete': 2,
            'total': 10,
            'phone': '89202991414',
            'nz': 'reutov',
        },
        False,
        False,
        False,
    ),
    (
        {
            'user_id': 'user_web',
            'complete': 2,
            'total': 10,
            'phone': '89202991414',
            'nz': 'moscow',
        },
        False,
        False,
        False,
    ),
    # antifake [old = true, zone = moscow -> false]
    (
        {
            'user_id': 'user_web',
            'complete': 2,
            'total': 10,
            'phone': '89202991414',
            'nz': 'moscow',
        },
        False,
        True,
        False,
    ),
    # antifake [afs = true -> true]
    (
        {
            'user_id': 'user_web',
            'complete': 2,
            'total': 10,
            'phone': '89202991414',
            'nz': 'moscow',
        },
        True,
        False,
        True,
    ),
    # antifake [afs throw -> false]
    (
        {
            'user_id': 'user_web',
            'complete': 2,
            'total': 10,
            'phone': '89202991414',
            'nz': 'riga',
        },
        True,
        False,
        False,
    ),
    # antifake [afs throw, old = true -> true]
    (
        {
            'user_id': 'user_web',
            'complete': 2,
            'total': 10,
            'phone': '89202991414',
            'nz': 'riga',
        },
        True,
        True,
        True,
    ),
    # antifake [old = true, zone = spb -> true]
    (
        {
            'user_id': 'user_web',
            'complete': 2,
            'total': 10,
            'phone': '89202991414',
            'nz': 'spb',
        },
        False,
        True,
        True,
    ),
    # request.source and request.destinations parameters
    (
        {
            'user_id': 'user_android',
            'complete': 2,
            'total': 10,
            'phone': '89162991414',
            'nz': 'moscow',
            'user_agent': 'python-requests/2.25.1',
            'request': {
                'source': {
                    # all possible source parameters
                    'country': 'COUNTRY',
                    'description': 'DESCRIPTION',
                    'exact': True,
                    'fullname': 'FULLNAME',
                    'geopoint': [
                        55.75759956270413,
                        37.61646333794469,
                    ],
                    'locality': 'LOCALITY',
                    'metrica_action': 'METRICA_ACTION',
                    'metrica_method': 'METRICA_METHOD',
                    'object_type': 'OBJECT_TYPE',
                    'oid': 'OID',
                    'porchnumber': 'PORCHNUMBER',
                    'premisenumber': 'PREMISENUMBER',
                    'short_text': 'SHORT_TEXT',
                    'thoroughfare': 'THOROUGHFARE',
                    'type': 'TYPE',
                    'use_geopoint': True,
                },
                'destinations': [
                    # all possible destinations parameters
                    {
                        'country': 'COUNTRY',
                        'description': 'DESCRIPTION',
                        'exact': True,
                        'fullname': 'FULLNAME',
                        'geopoint': [
                            55.76448705465592,
                            37.62929993934462,
                        ],
                        'locality': 'LOCALITY',
                        'metrica_action': 'METRICA_ACTION',
                        'metrica_method': 'METRICA_METHOD',
                        'object_type': 'OBJECT_TYPE',
                        'oid': 'OID',
                        'porchnumber': 'PORCHNUMBER',
                        'premisenumber': 'PREMISENUMBER',
                        'short_text': 'SHORT_TEXT',
                        'thoroughfare': 'THOROUGHFARE',
                        'type': 'TYPE',
                        'use_geopoint': True,
                    },
                ],
                'class': ['econom'],
            },
        },
        False,
        False,
        True,
    ),
])
@pytest.mark.config(
    AFS_USER_ANTIFAKE_ENABLED=True,
    USER_ANTIFRAUD_ENABLED=True,
    USER_ANTIFRAUD_ENABLED_ZONES=[
        'spb',
        'riga',
    ],
    USER_ANTIFRAUD_NON_NEWBIES_MIN_COMPLETED=3,
    USER_ANTIFRAUD_NEWBIES_MASKS=[
        '^8916',
    ],
    USER_ANTIFRAUD_BLOCK_WEB={
        '__default__': False,
        'ekb': True,
        'reutov': False,
    },
)
@pytest.inline_callbacks
def test_mark_as_user_fraud_and_expired_base(areq_request, patch, data,
                                             afs_frauder, old_frauder,
                                             frauder, mock_send_event):
    @areq_request
    def requests_request(method, url, **kwargs):
        assert method == 'POST'
        assert url == 'http://antifraud.taxi.dev.yandex.net/client/user/check_fake'
        payload = kwargs['json']
        try:
            json.dumps(payload)
        except Exception as e:
            assert False, str(e)
        if payload['zone'] == 'riga':
            return areq_request.response(500)
        assert payload['user_phone'] == data['phone']
        if 'user_phone_id' in data:
            assert payload['user_phone_id'] == str(
                data['user_phone_id']
            )
        assert payload['order_complete_count'] == data['complete']
        assert payload['order_total_count'] == data['total']

        if data.get('is_multiorder'):
            assert payload['is_multiorder'] == data['is_multiorder']
            assert payload['multiorder_order_number'] == 3

        assert payload['tariff_class'] == 'econom'
        if 'request' in data:
            if 'extra_user_phone_id' in data['request']:
                assert payload['extra_user_phone'] == str(
                    data['extra_phone']
                )
            if 'comment' in data['request']:
                assert payload['comment'] == data['request']['comment']
            if 'requirements' in data['request']:
                assert payload['requirements_quantity'] == (
                    len(data['request']['requirements'])
                )
        if 'payment_tech' in data:
            if 'type' in data['payment_tech']:
                assert payload['payment_type'] == (
                    data['payment_tech']['type']
                )
        if 'yandex_uid_type' in data:
            payload_yandex_uid_type = payload.get('yandex_uid_type', '')
            data_yandex_uid_type = data.get('yandex_uid_type', '')
            assert payload_yandex_uid_type == data_yandex_uid_type
        if 'request' in data:
            data_request = data['request']
        else:
            data_request = {}
        if 'destinations' in data_request:
            destinations = copy.deepcopy(data_request['destinations'])
            for dst in destinations:
                geopoint = copy.deepcopy(dst['geopoint'])
                del dst['geopoint']
                dst['lon'] = geopoint[0]
                dst['lat'] = geopoint[1]
            assert payload['destinations'] == destinations
        if 'source' in data_request:
            source = copy.deepcopy(data_request['source'])
            geopoint = copy.deepcopy(source['geopoint'])
            del source['geopoint']
            source['lon'] = geopoint[0]
            source['lat'] = geopoint[1]
            assert payload['source'] == source
        if 'user_agent' in data:
            assert payload['user_agent'] == data['user_agent']
        return areq_request.response(200, body=json.dumps({
            'frauder': afs_frauder
        }))

    @patch('taxi.external.taxi_protocol.user_antifraud')
    @async.inline_callbacks
    def user_antifraud(
            user, nearest_zone, user_phone, order_id=None, log_extra=None):
        yield async.return_value(old_frauder)

    yield _check(data, frauder, patch)
    assert len(requests_request.calls) == 1


@pytest.mark.parametrize('data,frauder', [
    (
        {
            'user_id': 'user_web',
            'complete': 2,
            'total': 10,
            'phone': '89162991414',
            'nz': 'spb',
        },
        False,
    ),
    (
        {
            'user_id': 'user_android',
            'complete': 2,
            'total': 10,
            'phone': '89162991414',
            'nz': 'spb',
        },
        True,
    )
])
@pytest.mark.config(
    AFS_USER_ANTIFAKE_ENABLED=False,
    USER_ANTIFRAUD_ENABLED=True,
    USER_ANTIFRAUD_ENABLED_ZONES=[
        'spb',
    ],
)
@pytest.inline_callbacks
def test_mark_as_user_fraud_and_expired_afs_off(
        patch, data, frauder, mock_send_event,
):
    @patch('taxi.external.antifraud.check_user_fake')
    @async.inline_callbacks
    def check_user_fake(user, user_phone_doc, proc,
                        tvm_src_service=None, log_extra=None):
        assert False

    @patch('taxi.external.taxi_protocol.user_antifraud')
    @async.inline_callbacks
    def user_antifraud(
            user, nearest_zone, user_phone, order_id=None, log_extra=None):
        if user.antifraud.position:
            yield async.return_value(
                user.antifraud.position.point[1] == 60.4095595)
        yield async.return_value(False)

    yield _check(data, frauder, patch)

    assert len(check_user_fake.calls) == 0
    assert len(user_antifraud.calls) == 1


@pytest.mark.parametrize('data,frauder', [
    (
        {
            'user_id': 'user_web',
            'complete': 2,
            'total': 10,
            'phone': '89202991414',
            'nz': 'ekb',
        },
        True,
    ),
    (
        {
            'user_id': 'user_web',
            'complete': 3,
            'total': 10,
            'phone': '89202991414',
            'nz': 'ekb',
        },
        False,
    ),
    (
        {
            'user_id': 'user_web',
            'complete': 2,
            'total': 10,
            'phone': '89202991414',
            'nz': 'reutov',
        },
        False,
    ),
    (
        {
            'user_id': 'user_web',
            'complete': 2,
            'total': 10,
            'phone': '89202991414',
            'nz': 'moscow',
        },
        True,
    ),
    (
        {
            'user_id': 'user_web',
            'complete': 2,
            'total': 10,
            'phone': '89202991414',
            'nz': 'spb',
        },
        True,
    ),
])
@pytest.mark.config(
    AFS_USER_ANTIFAKE_ENABLED=False,
    USER_ANTIFRAUD_ENABLED=True,
    USER_ANTIFRAUD_ENABLED_ZONES=[],
    USER_ANTIFRAUD_NON_NEWBIES_MIN_COMPLETED=3,
    USER_ANTIFRAUD_NEWBIES_MASKS=[],
    USER_ANTIFRAUD_BLOCK_WEB={
        '__default__': True,
        'ekb': True,
        'reutov': False,
    },
)
@pytest.inline_callbacks
def test_mark_as_user_fraud_and_expired_global(
        data, frauder, patch, mock_send_event,
):
    yield _check(data, frauder, patch)
