import bson
import pytest

INIT_CLAIMS = """
INSERT INTO cargo_claims.claims(status, uuid_id,
            idempotency_token,
            due, taxi_order_id)
VALUES ('performer_lookup', '987cfe7d6ab142ee811ab8e5f647a5fe',
        '3703070dfbd54eef937523721db9fda2',
        CURRENT_TIMESTAMP, 'd2651f7dfa4bcf16a5be8906cae7a4e8'),
        ('performer_lookup', '987cfe7d6ab142ee811ab8e5f647a5ff',
        '3703070dfbd54eef937523721db9fda3',
        CURRENT_TIMESTAMP, NULL)
"""

DOCUMENT_DATA = {
    'document': {
        'processing': {'version': 20},
        '_id': 'd2651f7dfa4bcf16a5be8906cae7a4e8',
        'order': {
            'version': 10,
            'request': {'dispatch_type': 'forced_performer'},
        },
    },
    'revision': {'order.version': 10, 'processing.version': 20},
}

DBID_UUID = 'a3608f8f7ee84e0b9c21862beef7e48d_d2936e38e2234a55b413c3d7a55b288c'
DBID_UUID2 = (
    'a3608f8f7ee84e0b9c21862beef7e48d_d2936e38e2234a55b413c3d7a55b288d'
)


@pytest.mark.config(
    CARGO_CLAIMS_MANUAL_DISPATCHER_SETTINGS={
        'enabled': True,
        'dispatch_period': 30,
    },
    CARGO_CLAIMS_DENORM_READ_SETTINGS_V2={
        '__default__': {
            'enabled': True,
            'yt-use-runtime': False,
            'yt-timeout-ms': 1000,
            'ttl-days': 1,
        },
    },
)
async def test_simple_admin_courier_change(
        taxi_cargo_claims, pgsql, mockserver,
):
    @mockserver.json_handler(
        '/cargo-dispatch/v1/internal/segment/force-router',
    )
    def force_fallback_router(request):
        assert request.json == {
            'segment_id': '987cfe7d6ab142ee811ab8e5f647a5ff',
            'router_id': 'fallback_router',
        }
        return mockserver.make_response('', status=200)

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def get_fields(request):
        assert bson.BSON.decode(request.get_data()) == {
            'fields': ['order.request'],
        }
        return mockserver.make_response(
            bson.BSON.encode(DOCUMENT_DATA), status=200,
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    def set_fields(request):
        assert bson.BSON.decode(request.get_data()) == {
            'revision': {'order.version': 10, 'processing.version': 20},
            'update': {
                '$set': {
                    'order.request.dispatch_type': 'forced_performer',
                    'order.request.lookup_extra.intent': 'cargo',
                    'order.request.lookup_extra.performer_id': DBID_UUID,
                },
            },
        }
        return mockserver.make_response(
            bson.BSON.encode(DOCUMENT_DATA), status=200,
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/start-lookup',
    )
    def start_lookup(request):
        assert bson.BSON.decode(request.get_data()) == {
            'filters': {'status': 'pending'},
        }
        return mockserver.make_response('', status=200)

    @mockserver.json_handler('/driver-status/v2/status/store')
    def change_status(request):
        assert request.json == {
            'comment': 'before manual dispatcher lookup',
            'park_id': 'a3608f8f7ee84e0b9c21862beef7e48d',
            'driver_id': 'd2936e38e2234a55b413c3d7a55b288c',
            'status': 'online',
        }
        return {'status': request.json.get('status'), 'updated_ts': 1}

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(INIT_CLAIMS)

    response = await taxi_cargo_claims.get(
        '/v2/admin/claim/courier',
        params={'claim_id': '987cfe7d6ab142ee811ab8e5f647a5fe'},
    )

    assert response.status_code == 200

    assert response.json() == {'revision': 0}

    response = await taxi_cargo_claims.post(
        '/v2/admin/claim/courier',
        json={
            'claim_id': '987cfe7d6ab142ee811ab8e5f647a5fe',
            'corp_client_id': '7ff7900803534212a3a66f4d0e114fc2',
            'revision': 0,
            'courier_id': '',
        },
    )

    assert response.status_code == 400

    response = await taxi_cargo_claims.post(
        '/v2/admin/claim/courier',
        json={
            'claim_id': '987cfe7d6ab142ee811ab8e5f647a5fe',
            'corp_client_id': '7ff7900803534212a3a66f4d0e114fc2',
            'revision': 0,
            'courier_id': DBID_UUID,
        },
    )

    assert response.status_code == 200

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        """
        SELECT *
        FROM cargo_claims.courier_manual_dispatch
        """,
    )
    assert list(cursor) == [
        (
            1,
            '987cfe7d6ab142ee811ab8e5f647a5fe',
            DBID_UUID,
            1,
            False,
            '7ff7900803534212a3a66f4d0e114fc2',
            '987cfe7d6ab142ee811ab8e5f647a5fe',
        ),
    ]

    response = await taxi_cargo_claims.get(
        'v2/claims/full',
        params={'claim_id': '987cfe7d6ab142ee811ab8e5f647a5fe'},
    )

    assert response.status_code == 200
    assert response.json()['forced_performer'] == DBID_UUID

    response = await taxi_cargo_claims.post(
        '/v2/admin/claim/courier',
        json={
            'claim_id': '987cfe7d6ab142ee811ab8e5f647a5ff',
            'corp_client_id': '7ff7900803534212a3a66f4d0e114fc2',
            'revision': 0,
            'courier_id': DBID_UUID2,
        },
    )

    assert response.status_code == 200

    await taxi_cargo_claims.run_task('cargo-claims-manual-dispatcher')

    cursor = pgsql['cargo_claims'].cursor()
    cursor.execute(
        """
        SELECT *
        FROM cargo_claims.courier_manual_dispatch
        ORDER BY id
        """,
    )
    assert list(cursor) == [
        (
            1,
            '987cfe7d6ab142ee811ab8e5f647a5fe',
            DBID_UUID,
            1,
            True,
            '7ff7900803534212a3a66f4d0e114fc2',
            '987cfe7d6ab142ee811ab8e5f647a5fe',
        ),
        (
            2,
            '987cfe7d6ab142ee811ab8e5f647a5ff',
            DBID_UUID2,
            1,
            False,
            '7ff7900803534212a3a66f4d0e114fc2',
            '987cfe7d6ab142ee811ab8e5f647a5ff',
        ),
    ]

    response = await taxi_cargo_claims.get(
        '/v2/admin/claim/courier',
        params={'claim_id': '987cfe7d6ab142ee811ab8e5f647a5fe'},
    )

    assert response.status_code == 200

    assert response.json() == {'courier_id': DBID_UUID, 'revision': 1}

    assert force_fallback_router.times_called
    assert get_fields.times_called
    assert set_fields.times_called
    assert start_lookup.times_called
    assert change_status.times_called
