import collections
import dataclasses
import typing

import pytest

from tests_cargo_pricing import utils as global_utils
from tests_cargo_pricing.taxi_dragon_resolvers import models
from tests_cargo_pricing.taxi_dragon_resolvers import utils


@pytest.fixture(name='setup_all', autouse=True)
def _setup_all(
        conf_exp3_events_saving_by_calc_kind_default,
        conf_exp3_processing_events_saving_enabled,
        v1_drivers_match_profile,
):
    pass


@pytest.fixture(name='v2_resolve_segment')
async def _v2_resolve_segment(
        taxi_cargo_pricing,
        mock_pricing_prepare,
        mock_put_processing_event,
        mock_pricing_recalc,
        mock_route,
):
    class Impl:
        url = '/v2/taxi/resolve-segment'
        payload = {'v1_request': global_utils.get_default_calc_request()}
        mock_prepare = mock_pricing_prepare
        mock_recalc = mock_pricing_recalc
        mock_router = mock_route

        async def execute(self):
            return await taxi_cargo_pricing.post(self.url, json=self.payload)

    return Impl()


@pytest.fixture(name='v2_resolve_waybill')
async def _v2_resolve_waybill(
        taxi_cargo_pricing,
        mock_pricing_prepare,
        mock_put_processing_event,
        mock_pricing_recalc,
        mock_route,
):
    class Impl:
        url = '/v2/taxi/resolve-waybill'
        payload = {'v1_request': global_utils.get_default_calc_request()}
        mock_prepare = mock_pricing_prepare
        mock_recalc = mock_pricing_recalc
        mock_router = mock_route

        async def execute(self):
            return await taxi_cargo_pricing.post(self.url, json=self.payload)

    return Impl()


@pytest.fixture(name='v2_retrieve_waybill_pricing')
def _v2_retrieve_waybill_pricing(taxi_cargo_pricing):
    async def wrapper(request):
        return await taxi_cargo_pricing.post(
            '/v2/taxi/retrieve-waybill-pricing', json=request,
        )

    return wrapper


@pytest.fixture(name='v2_estimate_waybill')
async def _v2_estimate_waybill(
        taxi_cargo_pricing,
        mock_pricing_prepare,
        mock_put_processing_event,
        mock_pricing_recalc,
        mock_route,
):
    class Impl:
        url = '/v2/taxi/estimate-waybill'
        payload = {'v1_request': global_utils.get_default_calc_request()}
        mock_prepare = mock_pricing_prepare
        mock_recalc = mock_pricing_recalc
        mock_router = mock_route

        async def execute(self):
            return await taxi_cargo_pricing.post(self.url, json=self.payload)

    return Impl()


@pytest.fixture(name='processing_state')
async def _processing_state(mockserver):
    class State:
        events_by_item_id: typing.Dict[str, list] = collections.defaultdict(
            list,
        )

        def get_events(self, entity_id: str, slice_from=0):
            return self.events_by_item_id[entity_id][slice_from:]

    global_state = State()

    @mockserver.json_handler('/processing/v1/cargo/pricing/create-event')
    def _mock_create(request):
        item_id = request.query['item_id']
        events = global_state.events_by_item_id[item_id]
        new_event_id = f'some_event_id_{len(events)}'
        events.append(
            {
                'event_id': new_event_id,
                'created': global_utils.from_start(minutes=0),
                'handled': True,
                'payload': request.json,
            },
        )

        return {'event_id': new_event_id}

    @mockserver.json_handler('/processing/v1/cargo/pricing/events')
    def _mock_list(request):
        events = global_state.events_by_item_id[request.query['item_id']]

        return {'events': events}

    return global_state


@pytest.fixture(name='processing_writer')
async def _processing_writer(
        v1_add_processing_event, conf_exp3_processing_events_saving_enabled,
):
    class Impl:
        @staticmethod
        async def add_create(entity_id):
            body = {'kind': 'create'}
            resp = await v1_add_processing_event(entity_id, [body])
            assert resp.status_code == 200

        @staticmethod
        async def add_calculation(entity_id, calc_id, price_for, calc_kind):
            body = {
                'kind': 'calculation',
                'calc_id': calc_id,
                'price_for': price_for,
                'origin_uri': 'some/origin/uri',
                'calc_kind': calc_kind,
            }
            resp = await v1_add_processing_event(entity_id, [body])
            assert resp.status_code == 200

    return Impl


@pytest.fixture(name='cargo_matcher_claim_estimating')
async def _cargo_matcher_claim_estimating(
        v1_calc_creator, processing_state, processing_writer,
):
    async def impl(segment: models.Segment):
        last_event_n = len(processing_state.get_events(segment.id))

        v1_calc_creator.payload['payment_info'] = segment.payment_info
        response = await v1_calc_creator.execute()
        await processing_writer.add_create(segment.id)
        await processing_writer.add_calculation(
            entity_id=segment.id,
            calc_id=response.json()['calc_id'],
            price_for=models.PriceFor.CLIENT,
            calc_kind=models.CalcKind.OFFER,
        )

        new_events = processing_state.get_events(
            segment.id, slice_from=last_event_n,
        )
        return response, new_events

    return impl


@pytest.fixture(name='cargo_claims_change_claim_order_price')
async def _cargo_claims_change_claim_order_price(
        v2_resolve_segment, processing_state, processing_writer,
):
    async def impl(
            segment: models.Segment, performer: typing.Optional[dict] = None,
    ):
        last_event_n = len(processing_state.get_events(segment.id))

        v2_resolve_segment.payload['segment'] = dataclasses.asdict(segment)
        v2_resolve_segment.payload['v1_request']['performer'] = performer
        v2_resolve_segment.payload['v1_request']['is_usage_confirmed'] = True
        v2_resolve_segment.payload['v1_request'][
            'waypoints'
        ] = utils.make_segment_points(segment)

        response = await v2_resolve_segment.execute()

        new_events = processing_state.get_events(
            segment.id, slice_from=last_event_n,
        )
        return response, new_events

    return impl


@pytest.fixture(name='v1_calc_price__driver_offer')
async def _v1_calc_price__driver_offer(
        v2_estimate_waybill,
        processing_state,
        processing_writer,
        v1_drivers_match_profile,
):
    async def impl(waybill: models.Waybill, performer: dict):
        entity_id = f'order/{waybill.taxi_order_id}'
        last_event_n = len(processing_state.get_events(entity_id))

        v2_estimate_waybill.payload['waybill'] = dataclasses.asdict(waybill)
        v2_estimate_waybill.payload['v1_request']['waypoints'] = []
        v2_estimate_waybill.payload['v1_request']['performer'] = performer
        v2_estimate_waybill.payload['v1_request']['is_usage_confirmed'] = True
        for segment in waybill.segments:
            v2_estimate_waybill.payload['v1_request']['waypoints'].extend(
                utils.make_segment_points(segment),
            )

        response = await v2_estimate_waybill.execute()

        new_events = processing_state.get_events(
            entity_id, slice_from=last_event_n,
        )
        return response, new_events

    return impl


@pytest.fixture(name='make_yandex_go_offer')
async def _make_yandex_go_offer(
        v1_calc_creator, processing_state, processing_writer,
):
    async def impl(segment: models.Segment):
        last_event_n = len(processing_state.get_events(segment.id))

        v1_calc_creator.payload['price_for'] = 'client'
        v1_calc_creator.payload['payment_info'] = segment.payment_info

        response = await v1_calc_creator.execute()

        await processing_writer.add_create(segment.id)
        await processing_writer.add_calculation(
            entity_id=segment.id,
            calc_id=response.json()['calc_id'],
            price_for=models.PriceFor.CLIENT,
            calc_kind=models.CalcKind.OFFER,
        )

        new_events = processing_state.get_events(
            segment.id, slice_from=last_event_n,
        )
        return response, new_events

    return impl


@pytest.fixture(name='v1_calc_price__driver_final')
async def _v1_calc_price__driver_final(
        v2_resolve_waybill,
        processing_state,
        processing_writer,
        v1_drivers_match_profile,
):
    async def impl(waybill: models.Waybill, performer: dict):
        entity_id = f'order/{waybill.taxi_order_id}'
        last_event_n = len(processing_state.get_events(entity_id))

        v2_resolve_waybill.payload['waybill'] = dataclasses.asdict(waybill)
        v2_resolve_waybill.payload['v1_request']['waypoints'] = []
        v2_resolve_waybill.payload['v1_request']['performer'] = performer
        v2_resolve_waybill.payload['v1_request']['is_usage_confirmed'] = True
        for segment in waybill.segments:
            v2_resolve_waybill.payload['v1_request']['waypoints'].extend(
                utils.make_segment_points(segment),
            )

        response = await v2_resolve_waybill.execute()

        new_events = processing_state.get_events(
            entity_id, slice_from=last_event_n,
        )
        return response, new_events

    return impl
