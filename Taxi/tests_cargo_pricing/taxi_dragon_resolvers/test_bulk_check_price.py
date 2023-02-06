import dataclasses

import pytest

from tests_cargo_pricing import utils as global_utils
from tests_cargo_pricing.taxi_dragon_resolvers import models
from tests_cargo_pricing.taxi_dragon_resolvers import utils


def get_v2_check_price_waybill(waybill_request):
    waypoints = []
    for segment in waybill_request['segments']:
        waypoints.extend(utils.make_segment_points(segment))
    waybill = {
        'segments': [
            dataclasses.asdict(segment)
            for segment in waybill_request['segments']
        ],
        'waypoints': waypoints,
        'candidates': waybill_request['candidates'],
    }

    required_fields = [
        'homezone',
        'clients',
        'tariff_class',
        'taxi_requirements',
    ]
    default_req = global_utils.get_default_calc_request()
    for field in required_fields:
        waybill[field] = default_req[field]
    return waybill


@pytest.fixture(name='v2_check_price_handler')
async def _v2_check_price_handler(
        taxi_cargo_pricing,
        mock_pricing_prepare,
        mock_put_processing_event,
        mock_pricing_recalc,
        mock_route,
):
    class CheckPriceHandler:
        def __init__(self):
            self.url = '/v2/taxi/check-prices-for-performers'
            self.mock_prepare = mock_pricing_prepare
            self.mock_recalc = mock_pricing_recalc
            self.mock_router = mock_route

        async def execute(self, waybill_requests):
            payload = {
                'waybills': [
                    get_v2_check_price_waybill(request)
                    for request in waybill_requests
                ],
            }
            return await taxi_cargo_pricing.post(self.url, json=payload)

    return CheckPriceHandler()


@pytest.fixture(name='create_client_calcs')
def _create_client_calcs(cargo_matcher_claim_estimating, make_yandex_go_offer):
    async def wrapper(waybill_requests):
        for waybill_request in waybill_requests:
            for segment in waybill_request['segments']:
                if segment.payment_info == models.PaymentMethod.CORP:
                    await cargo_matcher_claim_estimating(segment)
                else:
                    await make_yandex_go_offer(segment)

    return wrapper


async def test_bulk_check_price(
        v2_check_price_handler,
        create_client_calcs,
        mock_put_processing_event,
        v1_drivers_match_profile,
):
    waybill_requests = [
        {
            'segments': [
                models.make_segment(payment_info=models.PaymentMethod.CORP),
                models.make_segment(payment_info=models.PaymentMethod.CARD),
            ],
            'candidates': [models.Performer.FIRST, models.Performer.SECOND],
        },
        {
            'segments': [
                models.make_segment(payment_info=models.PaymentMethod.CARD),
                models.make_segment(payment_info=models.PaymentMethod.CORP),
            ],
            'candidates': [models.Performer.THIRD],
        },
    ]

    await create_client_calcs(waybill_requests)

    resp = await v2_check_price_handler.execute(waybill_requests)
    assert resp.status_code == 200
    assert mock_put_processing_event.mock.times_called == 0

    waybill_responses = resp.json()['waybill_responses']
    assert len(waybill_responses) == len(waybill_requests)
    for i, response in enumerate(waybill_responses):
        assert len(response['candidate_responses']) == len(
            waybill_requests[i]['candidates'],
        )
        for j, candidate_response in enumerate(
                response['candidate_responses'],
        ):
            waybill_requests[i]['candidates'][j].pop('assigned_at', None)
            assert (
                candidate_response['candidate']
                == waybill_requests[i]['candidates'][j]
            )
            assert len(candidate_response['segments']) == len(
                waybill_requests[i]['segments'],
            )


async def test_bulk_check_price_driver_tags(
        v2_check_price_handler,
        create_client_calcs,
        overload_tariff_class,
        experiments3,
        v1_drivers_match_profile,
):
    predicate = {
        'type': 'contains',
        'init': {
            'arg_name': 'driver_tags',
            'set_elem_type': 'string',
            'value': 'driver_honor_good_guy',
        },
    }
    overload_tariff_class.predicate = predicate
    await overload_tariff_class.execute(new_class='courier')

    waybill_requests = [
        {
            'segments': [
                models.make_segment(payment_info=models.PaymentMethod.CORP),
            ],
            'candidates': [models.Performer.FIRST, models.Performer.SECOND],
        },
    ]
    await create_client_calcs(waybill_requests)

    exp3_recorder = experiments3.record_match_tries(
        'cargo_pricing_class_substitution',
    )

    resp = await v2_check_price_handler.execute(waybill_requests)
    assert resp.status_code == 200

    waybill_resp = resp.json()['waybill_responses'][0]
    assert (
        waybill_resp['candidate_responses'][0]['candidate']
        == waybill_requests[0]['candidates'][0]
    )
    assert waybill_resp['candidate_responses'][0]['total_price'] == '200.9999'
    assert waybill_resp['candidate_responses'][1]['code'] == 'tariff_not_found'

    matches = await exp3_recorder.get_match_tries(ensure_ntries=2)
    assert matches[0].kwargs['driver_tags'] == ['driver_fix_bad_guy']
    assert matches[1].kwargs['driver_tags'] == ['driver_honor_good_guy']
