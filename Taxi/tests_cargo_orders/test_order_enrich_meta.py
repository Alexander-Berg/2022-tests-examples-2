import datetime

import bson
import pytest


PARK_ID = 'park_id1'
DRIVER_ID = 'driver_id1'
UNIQUE_DRIVER_ID = 'unique_driver_id1'
PREFIX = 'taxi/shift_ended/unique_driver_id'


@pytest.mark.parametrize(
    [
        'is_long_distance',
        'waiting_time',
        'waiting_cost',
        'unloading_time',
        'unloading_cost',
        'pickup_confirmation_code',
        'tags',
    ],
    [
        pytest.param(
            True,
            12.34,
            23.45,
            34.56,
            45.67,
            '123456',
            ['test_tag_1'],
            id='Happy path',
        ),
        pytest.param(None, None, None, None, None, None, [], id='No info'),
    ],
)
async def test_order_enrich_meta(
        taxi_cargo_orders,
        my_waybill_info,
        mockserver,
        is_long_distance,
        waiting_time,
        waiting_cost,
        unloading_time,
        unloading_cost,
        pickup_confirmation_code,
        tags,
        happy_path_park_list,
        mock_cargo_pricing_v2_calc_retrieve,
        fines_queue,
        load_json,
        taxi_order_id='taxi-order',
):
    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _driver_tags(request):
        assert request.json == {'dbid': 'park_id1', 'uuid': 'driver_id1'}
        return {'tags': tags}

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def _mock_order_core(request):
        assert request.content_type == 'application/bson'
        assert request.query['order_id'] == taxi_order_id
        response = {
            'document': {
                'processing': {'version': 19},
                '_id': taxi_order_id,
                'order': {'version': 10},
            },
            'revision': {'order.version': 10, 'processing.version': 19},
        }
        if is_long_distance is not None:
            response['document']['order']['performer'] = {
                'paid_supply': is_long_distance,
            }
        if waiting_time is not None and waiting_cost is not None:
            response['document']['order']['calc_info'] = {
                'waiting_time': waiting_time,
                'waiting_cost': waiting_cost,
            }
        if unloading_time is not None and unloading_cost is not None:
            response['document']['order']['taximeter_receipt'] = {
                'details': [
                    {
                        'service_type': 'unloading',
                        'meter_value': unloading_time,
                        'sum': unloading_cost,
                    },
                ],
            }

        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(response),
        )

    @mockserver.json_handler(
        '/esignature-issuer/v1/signatures/confirmation-code',
    )
    def _mock_esignature_issuer(request):
        assert request.json == {
            'signature_id': 'sender_to_driver',
            'doc_type': 'cargo_claims',
            'doc_id': 'claim_uuid_1',
        }
        return {'code': pickup_confirmation_code, 'attempts': 10}

    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def _vgw_api(request):
        assert request.query['external_ref_id'] == 'taxi-order'
        return []

    @mockserver.json_handler('/processing/v1/taxi/order_fines/events')
    def _processing_events_handler(request):
        return {'events': fines_queue.events}

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    async def _unique_drivers(request):
        assert request.json['profile_id_in_set'][0] == f'{PARK_ID}_{DRIVER_ID}'
        return {
            'uniques': [
                {
                    'park_driver_profile_id': f'{PARK_ID}_{DRIVER_ID}',
                    'data': {'unique_driver_id': UNIQUE_DRIVER_ID},
                },
            ],
        }

    @mockserver.json_handler('billing-reports/v1/docs/by_tag')
    async def _billing_reports(request):
        today = datetime.date.today()
        yesterday = (today - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        assert (
            request.json['tag']
            == f'{PREFIX}/{UNIQUE_DRIVER_ID}/{yesterday}/nmfg'
        )
        return load_json('billing_reports_doc.json')

    for segment in my_waybill_info['segments']:
        segment['corp_client_id'] = '162b9899216246f7a1ba9fc14a479e87'

    for segment in my_waybill_info['execution']['segments']:
        segment['pricing'] = {
            'final_pricing_calc_id': (
                'cargo-pricing/v1/83948031-c88d-4f02-a7a6-a9d7715112de'
            ),
        }

    response = await taxi_cargo_orders.post(
        'v1/order/enrich-meta',
        json={
            'metadata': {
                'order_id': taxi_order_id,
                'some_meta_key': 'some_meta_value',
            },
        },
    )
    assert response.status_code == 200

    expected_metadata = {
        'antifraud_decision': True,
        'order_id': taxi_order_id,
        'some_meta_key': 'some_meta_value',
        'claim_info_total_weight': 15.0,
        'count_of_destination_points': 1,
        'employer': 'eats',
        'driver_tags': list(set(tags)),
        'order_tariffs': ['express'],
        'park_name': 'Премьер',
        'is_order_eda': True,
        'order_calls_num': 0,
        'points_types': ['source', 'destination', 'return'],
        'current_point': 1,
        'is_postpayment_in_order': False,
        'fare_reasons': ['first_fine'],
        'park_is_blocked': False,
        'door_to_door_cost': '50',
        'paid_supply_cost': '159',
        'nmfg_value': '0.0000',
    }
    if is_long_distance is not None:
        expected_metadata['is_long_distance'] = is_long_distance
    if pickup_confirmation_code is not None:
        expected_metadata[
            'pickup_confirmation_code'
        ] = pickup_confirmation_code
    if waiting_time is not None and waiting_cost is not None:
        expected_metadata['waiting_time'] = waiting_time
        expected_metadata['waiting_cost'] = waiting_cost
    if unloading_time is not None and unloading_cost is not None:
        expected_metadata['unloading_time'] = unloading_time
        expected_metadata['unloading_cost'] = unloading_cost

    assert response.json()['metadata'] == expected_metadata
