# pylint: disable=redefined-outer-name
import pytest


@pytest.fixture
def get_segment_id(get_db_segment_ids):
    async def _wrapper():
        segment_ids = await get_db_segment_ids()

        return segment_ids[0]

    return _wrapper


@pytest.fixture(name='check_audit')
async def _check_audit(taxi_cargo_claims):
    async def _wrapper(
            claim_uuid: str, ticket: str = 'TICKET-100', comment='some text',
    ):
        response = await taxi_cargo_claims.post(
            'v2/admin/claims/full', params={'claim_id': claim_uuid},
        )
        assert response.status_code == 200

        for audit in response.json()['history']:
            if (
                    audit.get('ticket') == ticket
                    and audit.get('comment') == comment
            ):
                return
        assert False, 'Support audit (comment, ticket) not found in history'

    return _wrapper


@pytest.fixture(name='set_offer_calc_id')
def _set_offer_calc_id(mockserver, pgsql):
    def mock(claim_uuid, offer_calc_id, status='new', final_price=0):
        cursor = pgsql['cargo_claims'].conn.cursor()
        cursor.execute(
            'UPDATE cargo_claims.claim_estimating_results '
            f'SET taxi_offer_id=\'{offer_calc_id}\''
            f'WHERE claim_uuid = \'{claim_uuid}\'',
        )

        cursor.execute(
            'UPDATE cargo_claims.claims '
            f'SET final_price={final_price}, '
            f'status=\'{status}\' '
            f'WHERE uuid_id = \'{claim_uuid}\'',
        )

    return mock


@pytest.fixture(name='set_final_calc_id')
def _set_final_calc_id(mockserver, pgsql):
    def mock(claim_uuid, final_calc_id, status='delivered', final_price=0):
        cursor = pgsql['cargo_claims'].conn.cursor()
        cursor.execute(
            'UPDATE cargo_claims.claims '
            f'SET final_pricing_calc_id=\'{final_calc_id}\', '
            f'status=\'{status}\', '
            f'final_price={final_price} '
            f'WHERE uuid_id = \'{claim_uuid}\'',
        )

    return mock


@pytest.fixture(name='get_default_pricing_calc_request')
def _get_default_pricing_calc_request():
    def wrapper(claim_id, waypoint_ids):
        return {
            'idempotency_token': f'resolved-{claim_id}',
            'clients': [
                {'corp_client_id': '01234567890123456789012345678912'},
            ],
            'external_ref': f'cargo_ref_id/{claim_id}',
            'homezone': 'moscow',
            'is_usage_confirmed': True,
            'payment_info': {
                'method_id': 'corp-01234567890123456789012345678912',
                'type': 'corp',
            },
            'performer': {'driver_id': 'driver_id1', 'park_db_id': 'park_id1'},
            'previous_calc_id': 'cargo-pricing/v1/taxi_offer_id_1',
            'price_for': 'client',
            'taxi_requirements': {'cargo_loaders': 2, 'cargo_type': 'lcv_m'},
            'tariff_class': 'cargo',
            'entity_id': claim_id,
            'origin_uri': 'stq_cargo_claims_change_claim_order_price',
            'calc_kind': 'final',
            'resolution_info': {'resolution': 'completed'},
            'waypoints': [
                {
                    'id': waypoint_ids[0],
                    'position': [37.5, 55.7],
                    'resolution_info': {'resolution': 'delivered'},
                    'type': 'pickup',
                    'claim_id': claim_id,
                },
                {
                    'id': waypoint_ids[1],
                    'position': [37.6, 55.6],
                    'resolution_info': {'resolution': 'delivered'},
                    'type': 'dropoff',
                    'claim_id': claim_id,
                },
                {
                    'id': waypoint_ids[2],
                    'position': [37.8, 55.4],
                    'resolution_info': {'resolution': 'skipped'},
                    'type': 'return',
                    'claim_id': claim_id,
                },
            ],
            'cargo_items': [
                {
                    'dropoff_point_id': waypoint_ids[1],
                    'pickup_point_id': waypoint_ids[0],
                    'quantity': 3,
                    'size': {'height': 0.5, 'length': 20.0, 'width': 5.8},
                    'weight': 10.2,
                },
                {
                    'dropoff_point_id': waypoint_ids[1],
                    'pickup_point_id': waypoint_ids[0],
                    'quantity': 1,
                    'size': {'height': 1.0, 'length': 2.2, 'width': 5.0},
                    'weight': 5.0,
                },
            ],
        }

    return wrapper
