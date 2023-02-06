import datetime
import json

import pytest

from tests_dispatch_buffer import common
from tests_dispatch_buffer import utils


ORDER_ID_1 = 'order_id_1'
OFFER_ID_1 = 'offer_id_1'
ORDER_ID_2 = 'order_id_2'


async def test_performer_for_order_found(
        taxi_dispatch_buffer, pgsql, load_json,
):
    order_meta = load_json('performer_order_meta.json')
    original_candidate = load_json('candidate.json')

    utils.insert_order(
        pgsql,
        order_id=ORDER_ID_1,
        offer_id=OFFER_ID_1,
        user_id='user_id',
        created=datetime.datetime.now(),
        zone_id='example',
        classes='{"econom"}',
        service='taxi',
        order_lookup='ROW(0,1,3)',
        dispatch_status='dispatched',
        order_meta=json.dumps(order_meta),
        dispatched_performer=json.dumps(original_candidate),
    )
    response = await taxi_dispatch_buffer.post(
        'performer-for-order', json=order_meta,
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert 'candidate' in resp_json
    assert resp_json['message'] == 'found'
    candidate = response.json()['candidate']
    assert candidate == original_candidate


async def test_performer_for_order_not_found(
        taxi_dispatch_buffer, pgsql, load_json,
):
    order_meta = load_json('performer_order_meta.json')

    utils.insert_order(
        pgsql,
        user_id='user_id',
        order_id=ORDER_ID_1,
        offer_id=OFFER_ID_1,
        created=datetime.datetime.now(),
        zone_id='example',
        classes='{"econom"}',
        service='taxi',
        order_lookup='ROW(0,1,3)',
        dispatch_status='dispatched',
        order_meta=json.dumps(order_meta),
    )
    response = await taxi_dispatch_buffer.post(
        'performer-for-order', json=order_meta,
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert 'candidate' not in response.json()
    assert resp_json['message'] == 'not found'


async def test_performer_for_order_created(
        taxi_dispatch_buffer, pgsql, load_json,
):
    order_meta = load_json('performer_order_meta.json')

    response = await taxi_dispatch_buffer.post(
        'performer-for-order', json=order_meta,
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert 'candidate' not in response.json()
    assert resp_json['message'] == 'created'

    rows = utils.select_named(pgsql, order_id=ORDER_ID_1)
    assert rows


async def test_performer_for_order_updated(
        taxi_dispatch_buffer, pgsql, load_json,
):
    order_meta = load_json('performer_order_meta.json')

    utils.insert_order(
        pgsql,
        user_id='user_id',
        order_id=ORDER_ID_1,
        offer_id=OFFER_ID_1,
        created=datetime.datetime.now(),
        zone_id='example',
        classes='{"econom"}',
        service='taxi',
        order_lookup='ROW(0,1,3)',
        dispatch_status='dispatched',
        order_meta=json.dumps(order_meta),
    )
    response = await taxi_dispatch_buffer.post(
        'performer-for-order', json=order_meta,
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert 'candidate' not in response.json()
    assert resp_json['message'] == 'not found'


async def test_performer_for_order_updated_only_one(
        taxi_dispatch_buffer, pgsql, load_json,
):
    order_meta = load_json('performer_order_meta.json')
    del order_meta['order']['request']['offer']

    utils.insert_order(
        pgsql,
        user_id='user_id',
        order_id=ORDER_ID_1,
        created=datetime.datetime.now(),
        zone_id='example',
        classes='{"econom"}',
        service='taxi',
        order_lookup='ROW(0,1,3)',
        dispatch_status='idle',
        order_meta=json.dumps(order_meta),
    )

    order_meta['order_id'] = ORDER_ID_2
    utils.insert_order(
        pgsql,
        user_id='user_id',
        order_id=ORDER_ID_2,
        created=datetime.datetime.now(),
        zone_id='example',
        classes='{"econom"}',
        service='taxi',
        order_lookup='ROW(0,1,3)',
        dispatch_status='idle',
        order_meta=json.dumps(order_meta),
    )

    order_meta['lookup'] = {'generation': 0, 'version': 1, 'wave': 2}

    response = await taxi_dispatch_buffer.post(
        'performer-for-order', json=order_meta,
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['message'] == 'updated'

    order_1 = utils.select_named(pgsql, order_id=ORDER_ID_1)[0]
    order_2 = utils.select_named(pgsql, order_id=ORDER_ID_2)[0]

    assert order_1['order_meta']['order_id'] == ORDER_ID_1
    assert order_2['order_meta']['order_id'] == ORDER_ID_2


async def test_performer_for_order_same_offers(
        taxi_dispatch_buffer, pgsql, load_json,
):
    order_meta = load_json('performer_order_meta.json')
    original_candidate = load_json('candidate.json')

    utils.insert_order(
        pgsql,
        order_id=ORDER_ID_1,
        offer_id=OFFER_ID_1,
        user_id='user_id',
        created=datetime.datetime.now(),
        zone_id='example',
        classes='{"econom"}',
        service='taxi',
        order_lookup='ROW(0,1,3)',
        dispatch_status='dispatched',
        order_meta=json.dumps(order_meta),
        dispatched_performer=json.dumps(original_candidate),
    )
    order_meta['order_id'] = ORDER_ID_2
    response = await taxi_dispatch_buffer.post(
        'performer-for-order', json=order_meta,
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert 'candidate' not in resp_json
    assert resp_json['message'] == 'created'


@pytest.mark.parametrize(
    'lookup_json,message',
    [
        ({'generation': 0, 'version': 2, 'wave': 4}, 'found'),
        ({'generation': 1, 'version': 2, 'wave': 4}, 'updated'),
        ({'generation': 0, 'version': 1, 'wave': 4}, 'updated'),
    ],
)
async def test_performer_for_order_lookup(
        taxi_dispatch_buffer, pgsql, lookup_json, message, load_json,
):
    order_meta = load_json('performer_order_meta.json')
    candidate = load_json('candidate.json')

    utils.insert_order(
        pgsql,
        user_id='user_id',
        order_id=ORDER_ID_1,
        offer_id=OFFER_ID_1,
        created=datetime.datetime.now(),
        zone_id='example',
        classes='{"econom"}',
        service='taxi',
        order_lookup='ROW(0,1,3)',
        dispatch_status='dispatched',
        order_meta=json.dumps(order_meta),
        dispatched_performer=json.dumps(candidate),
    )
    order_meta['lookup'] = lookup_json

    response = await taxi_dispatch_buffer.post(
        'performer-for-order', json=order_meta,
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['message'] == message


@pytest.mark.parametrize(
    'callback,code',
    [
        ('http://lookup.taxi.yandex.net/event', 200),
        ('http://abracadabra.taxi.yandex.net', 406),
    ],
)
async def test_performer_for_order_callback(
        taxi_dispatch_buffer, load_json, pgsql, callback, code,
):
    order_meta = load_json('performer_order_meta.json')
    order_meta['callback']['url'] = callback

    utils.insert_order(
        pgsql,
        user_id='user_id',
        order_id=ORDER_ID_1,
        offer_id=OFFER_ID_1,
        created=datetime.datetime.now(),
        zone_id='example',
        classes='{"econom"}',
        service='taxi',
        order_lookup='ROW(0,1,4)',
        dispatch_status='on_draw',
        order_meta=json.dumps(order_meta),
    )

    response = await taxi_dispatch_buffer.post(
        'performer-for-order', json=order_meta,
    )
    assert response.status_code == code


@pytest.mark.now('2040-01-01T16:47:54.721')
@pytest.mark.config(
    DRIVER_FOR_ORDER_HEALTH_CHECK_ENABLED=True,
    DRIVER_FOR_ORDER_HEALTH_CHECK_THRESHOLD=0,
)
async def test_performer_for_order_unhealthy(
        taxi_dispatch_buffer, load_json, pgsql,
):
    order_meta = load_json('performer_order_meta.json')
    candidate = load_json('candidate.json')

    updated = datetime.datetime.now() - datetime.timedelta(hours=24)

    utils.insert_order(
        pgsql,
        user_id='user_id',
        order_id=ORDER_ID_1,
        offer_id=OFFER_ID_1,
        created=updated,
        updated=updated,
        zone_id='example',
        classes='{"econom"}',
        service='taxi',
        order_lookup='ROW(0,1,4)',
        dispatch_status='on_draw',
        order_meta=json.dumps(order_meta),
        dispatched_performer=json.dumps(candidate),
    )

    response = await taxi_dispatch_buffer.post(
        'performer-for-order', json=order_meta,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'message' in response_json
    assert response_json['message'] == 'irrelevant'


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'dispatch-buffer'}],
    TVM_SERVICES={'dispatch-buffer': 2345, 'mock': 111},
    DISPATCH_BUFFER_ENABLED_REGISTERING_PIN=True,
)
@pytest.mark.tvm2_ticket(
    {
        2345: common.DISPATCH_BUFFER_SERVICE_TICKET,
        111: common.MOCK_SERVICE_TICKET,
    },
)
async def test_performer_for_order_tvm(taxi_dispatch_buffer, load_json):
    order_meta = load_json('performer_order_meta.json')

    url = '/performer-for-order'
    headers = common.DEFAULT_DISPATCH_BUFFER_HEADER

    response = await taxi_dispatch_buffer.post(url, json=order_meta)
    # unauthorized
    assert response.status_code == 401

    response = await taxi_dispatch_buffer.post(
        url, headers=headers, json=order_meta,
    )
    assert response.status_code == 200


@pytest.mark.config(
    DISPATCH_BUFFER_ENABLED=True,
    DISPATCH_BUFFER_AGGLOMERATIONS={
        'domodedovo_check_in': ['moscow', 'himki'],
    },
    DISPATCH_CHECK_IN_PICKUP_LINES={
        'pickup_line_0': {
            'enabled': True,
            'terminal_id': 'terminal_C',
            'allowed_tariffs': ['econom'],
            'pickup_points': [],
        },
    },
)
async def test_performer_for_order_check_in(
        taxi_dispatch_buffer, pgsql, load_json, experiments3,
):
    experiments3.add_config(
        **utils.agglomeration_settings(
            'domodedovo_check_in',
            {
                'ALGORITHMS': ['hungarian'],
                'APPLY_ALGORITHM': 'hungarian',
                'APPLY_RESULTS': True,
                'DISPATCH_ORDER_AFTER_FIRST_RUN_SECONDS': 0,
                'ENABLED': True,
                'OLD_LOOKUP_FALLBACK_WAIT_SECONDS': 12000,
                'ORDERS_LIMIT': 1000,
                'RUNNING_INTERVAL': 2,
                'TERMINALS': ['terminal_C'],
            },
        ),
    )

    order_meta = load_json('performer_order_meta.json')
    order_meta['dispatch_check_in'] = {
        'check_in_time': 1588064400,
        'pickup_line': 'pickup_line_0',
    }

    response = await taxi_dispatch_buffer.post(
        'performer-for-order', json=order_meta,
    )
    assert response.status_code == 200
    assert response.json()['message'] == 'created'

    rows = utils.select_named(pgsql, order_id=ORDER_ID_1)
    assert rows
    assert rows[0]['order_meta']['dispatch_check_in']
    assert rows[0]['service'] == 'check_in'


async def test_performer_for_order_retained(
        taxi_dispatch_buffer, pgsql, load_json,
):
    order_meta = load_json('performer_order_meta.json')

    utils.insert_order(
        pgsql,
        user_id='user_id',
        order_id=ORDER_ID_1,
        offer_id=OFFER_ID_1,
        created=datetime.datetime.now(),
        zone_id='example',
        classes='{"econom"}',
        service='taxi',
        order_lookup='ROW(0,1,3)',
        is_retained=True,
        dispatch_status='dispatched',
        order_meta=json.dumps(order_meta),
    )
    response = await taxi_dispatch_buffer.post(
        'performer-for-order', json=order_meta,
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert 'candidate' not in response.json()
    assert resp_json['message'] == 'retained'


@pytest.mark.config(
    DISPATCH_BUFFER_EXTERNAL_REQUESTS_FALLBACK='is_unavailable_strong',
)
@pytest.mark.parametrize(
    'fallback,code',
    [
        ('dispatch-buffer.tasks_count.example_agglomeration.fallback', 200),
        ('dispatch-buffer.is_unavailable_strong', 200),
    ],
)
async def test_performer_for_order_fallback_fired(
        taxi_dispatch_buffer, statistics, pgsql, load_json, fallback, code,
):
    order_meta = load_json('performer_order_meta.json')

    utils.insert_order(
        pgsql,
        user_id='user_id',
        order_id=ORDER_ID_1,
        offer_id=OFFER_ID_1,
        created=datetime.datetime.now(),
        agglomeration='example_agglomeration',
        zone_id='example',
        classes='{"econom"}',
        service='taxi',
        order_lookup='ROW(0,1,3)',
        dispatch_status='dispatched',
        order_meta=json.dumps(order_meta),
    )

    statistics.fallbacks = [fallback]
    response = await taxi_dispatch_buffer.post(
        'performer-for-order', json=order_meta,
    )
    assert response.status_code == code
    resp_json = response.json()
    assert 'candidate' not in resp_json
    assert resp_json['message'] == 'irrelevant'


async def test_performer_for_order_bad_request(
        taxi_dispatch_buffer, pgsql, load_json,
):
    order_meta = load_json('order_data.json')
    order_meta.pop('order_id')
    order_meta['order']['request'].pop('offer')

    response = await taxi_dispatch_buffer.post(
        'performer-for-order', json=order_meta,
    )
    assert response.status_code == 400


@pytest.mark.config(DISPATCH_BUFFER_AGGLOMERATIONS={'example': []})
async def test_performer_for_order_empty_agglomeration(
        taxi_dispatch_buffer, load_json, experiments3,
):
    experiments3.add_config(
        **utils.agglomeration_settings(
            'example',
            {
                'APPLY_ALGORITHM': 'hungarian',
                'APPLY_RESULTS': True,
                'DISPATCH_ORDER_AFTER_FIRST_RUN_SECONDS': 0,
                'ENABLED': True,
                'OLD_LOOKUP_FALLBACK_WAIT_SECONDS': 60,
                'ORDERS_LIMIT': 0,
                'RUNNING_INTERVAL': 60,
            },
        ),
    )

    order_meta = load_json('order_data.json')
    response = await taxi_dispatch_buffer.post(
        'performer-for-order', json=order_meta,
    )
    assert response.status_code == 200
