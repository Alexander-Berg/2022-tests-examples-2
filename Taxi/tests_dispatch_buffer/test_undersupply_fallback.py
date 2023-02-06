import datetime
import json

import pytest

from tests_dispatch_buffer import utils

DELAYED = 'delayed'
DELAYED_WITH_UNDERSUPPLY = 'delayed_with_undersupply'


@pytest.mark.pgsql('driver_dispatcher', files=['dispatch_meta_insert.sql'])
@pytest.mark.config(DISPATCH_BUFFER_PERIOD_OF_ANALYSIS_OF_ORDERS_DELAYS=500)
@pytest.mark.experiments3(filename='experiments3.json')
async def test_undersupply_fallback(taxi_dispatch_buffer, load_json):
    await taxi_dispatch_buffer.invalidate_caches()

    order_meta = load_json('performer_order_meta.json')
    response = await taxi_dispatch_buffer.post(
        'performer-for-order', json=order_meta,
    )

    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['message'] == 'updated'


def _insert_order(pgsql, **kwargs):
    now = datetime.datetime.now()

    params = {
        'service': 'taxi',
        'user_id': 'user_id',
        'zone_id': 'moscow',
        'agglomeration': 'moscow',
        'created': now - datetime.timedelta(seconds=40),
        'first_dispatch_run': now - datetime.timedelta(seconds=40),
        'last_dispatch_run': now,
        'dispatch_status': 'dispatched',
        'classes': '{"econom"}',
        'order_lookup': 'ROW(0,1,3)',
        'order_meta': json.dumps({}),
    }
    params.update(kwargs)

    utils.insert_order(pgsql, **params)


@pytest.mark.config(DISPATCH_BUFFER_AGGLOMERATIONS={'moscow': ['moscow']})
@pytest.mark.experiments3(filename='experiments3.json')
async def test_fallback_with_different_tariffs(
        taxi_dispatch_buffer, pgsql, load_json, experiments3,
):
    experiments3.add_config(
        **utils.agglomeration_settings(
            'moscow',
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

    now = datetime.datetime.now()
    _insert_order(
        pgsql,
        order_id='order_id_1',
        created=(now - datetime.timedelta(seconds=40)),
        first_dispatch_run=(now - datetime.timedelta(seconds=40)),
    )
    _insert_order(
        pgsql,
        order_id='order_id_2',
        created=(now - datetime.timedelta(seconds=90)),
        first_dispatch_run=(now - datetime.timedelta(seconds=90)),
    )
    await taxi_dispatch_buffer.invalidate_caches()
    order_meta = load_json('performer_order_meta.json')
    order_meta['order_id'] = 'order_id_1'
    order_meta['order']['nearest_zone'] = 'moscow'
    response = await taxi_dispatch_buffer.post(
        'performer-for-order', json=order_meta,
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['message'] == 'delayed_with_undersupply'

    _insert_order(
        pgsql,
        order_id='order_id_3',
        created=(now - datetime.timedelta(seconds=40)),
        first_dispatch_run=(now - datetime.timedelta(seconds=40)),
        classes='{"comfort"}',
    )
    _insert_order(
        pgsql,
        order_id='order_id_4',
        created=(now - datetime.timedelta(seconds=80)),
        first_dispatch_run=(now - datetime.timedelta(seconds=80)),
        classes='{"business"}',
    )
    await taxi_dispatch_buffer.invalidate_caches()
    order_meta['order_id'] = 'order_id_3'
    response = await taxi_dispatch_buffer.post(
        'performer-for-order', json=order_meta,
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['message'] == 'delayed_with_undersupply'

    order_meta = load_json('performer_order_meta.json')
    order_meta['order_id'] = 'order_id_5'
    order_meta['order']['nearest_zone'] = 'moscow'
    response = await taxi_dispatch_buffer.post(
        'performer-for-order', json=order_meta,
    )

    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['message'] == 'created'

    _insert_order(
        pgsql,
        order_id='order_id_6',
        created=(now - datetime.timedelta(seconds=300)),
        first_dispatch_run=(now - datetime.timedelta(seconds=300)),
        classes='{"business"}',
    )
    await taxi_dispatch_buffer.invalidate_caches()
    order_meta['order_id'] = 'order_id_6'
    response = await taxi_dispatch_buffer.post(
        'performer-for-order', json=order_meta,
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['message'] == 'not found'


@pytest.mark.experiments3(filename='experiments3_statuses.json')
@pytest.mark.pgsql(
    'driver_dispatcher', files=['dispatch_meta_insert_statuses.sql'],
)
@pytest.mark.config(
    DISPATCH_BUFFER_UNDERSUPPLY_DISPATCH_STATUS_SETTINGS={
        'dispatch_statuses_set': [
            ['idle', 'on_draw', 'dispatched'],
            ['dispatched'],
        ],
    },
)
async def test_fallback_with_several_statuses(taxi_dispatch_buffer, load_json):
    await taxi_dispatch_buffer.invalidate_caches()
    order_meta = load_json('performer_order_meta.json')

    response = await taxi_dispatch_buffer.post(
        'performer-for-order', json=order_meta,
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['message'] == 'delayed_with_undersupply'
