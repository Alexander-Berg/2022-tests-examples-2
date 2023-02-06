# pylint: disable=import-only-modules, unsubscriptable-object, invalid-name
# flake8: noqa IS001
from dataclasses import dataclass, field, fields
from datetime import datetime
from enum import Enum
from typing import Tuple, List, Optional, Dict


import pytest
from tests_grocery_performer_watcher.plugins.service_mock import (
    EndpointContext,
    ServiceContext,
    make_response,
)


class VisitStatus(str, Enum):
    PENDING = 'pending'
    ARRIVED = 'arrived'
    SKIPPED = 'skipped'
    VISITED = 'visited'


@dataclass
class WaybillPoint:
    claim_point_id: int
    coords: Tuple[float, float]
    visit_status: VisitStatus
    last_status_change_ts: datetime = datetime.fromisoformat(
        '2021-12-17T05:45:14+00:00',
    )
    was_ready_at: Optional[datetime] = None


@dataclass
class V1WaybillInfoContext(EndpointContext):
    file_name: str = 'cargo-dispatch/waybill_info.json'
    waybill_points: List[WaybillPoint] = field(default_factory=list)
    is_pull_dispatch: Optional[bool] = None


@pytest.fixture(name='v1_waybill_info')
def _v1_waybill_info(mockserver, load_json):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def handler(request):
        # check request
        assert request.query['waybill_external_ref'] == context.waybill_ref

        if context.error:
            return context.make_error_response()
        if context.response:
            return context.response

        response = load_json(context.file_name)

        if context.is_pull_dispatch is not None:
            response['dispatch']['is_pull_dispatch'] = context.is_pull_dispatch

        for idx, point in enumerate(context.waybill_points):
            response['execution']['points'][idx][
                'visit_status'
            ] = point.visit_status
            response['execution']['points'][idx]['location'][
                'coordinates'
            ] = point.coords
            response['execution']['points'][idx][
                'claim_point_id'
            ] = point.claim_point_id
            response['execution']['points'][idx][
                'last_status_change_ts'
            ] = point.last_status_change_ts.isoformat()
            if point.was_ready_at:
                response['execution']['points'][idx][
                    'was_ready_at'
                ] = point.was_ready_at.isoformat()

        return make_response(json=response)

    context = V1WaybillInfoContext(mock=handler)
    return context


@dataclass
class V1WaybillArriveAtPointContext(EndpointContext):
    point_id: int = 112233
    driver_id: str = 'driver_id_1'
    park_id: str = 'park_id_1'
    file_name: str = 'cargo-dispatch/dummy_confirm_response.json'


@pytest.fixture(name='v1_waybill_arrive_at_point')
def _v1_waybill_arrive_at_point(mockserver, load_json):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/arrive-at-point')
    def handler(request):
        assert request.json['point_id'] == context.point_id
        assert request.json['performer_info']['park_id'] == context.park_id
        assert request.json['performer_info']['driver_id'] == context.driver_id
        assert 'comment' in request.json['support']
        assert 'ticket' in request.json['support']

        if context.error:
            return context.make_error_response()
        if context.response:
            return context.response

        return make_response(json=load_json(context.file_name), status=200)

    context = V1WaybillArriveAtPointContext(mock=handler)
    return context


@dataclass
class V1SegmentInfoContext(EndpointContext):
    file_name: str = 'cargo-dispatch/base_segment.json'


@pytest.fixture(name='v1_segment_info')
def _v1_segment_info(mockserver, load_json):
    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    async def handler(request):
        assert request.query['segment_id']

        if context.error:
            return context.make_error_response()
        if context.response:
            return context.response

        segment = load_json('cargo-dispatch/base_segment.json')
        segment['dispatch']['chosen_waybill'][
            'external_ref'
        ] = context.waybill_ref
        return make_response(json=segment, status=200)

    context = V1SegmentInfoContext(mock=handler)
    return context


@dataclass
class V1WaybillExchangeConfirmContext(EndpointContext):
    file_name: str = 'cargo-dispatch/dummy_confirm_response.json'


@pytest.fixture(name='v1_waybill_exchange_confirm')
def _v1_waybill_exchange_confirm(mockserver, load_json):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/exchange/confirm')
    def handler(request):

        if context.error:
            return context.make_error_response()
        if context.response:
            return context.response

        return make_response(json=load_json(context.file_name), status=200)

    context = V1WaybillExchangeConfirmContext(mock=handler)
    return context


@dataclass
class CargoDispatchContext(ServiceContext):
    v1_waybill_info: V1WaybillInfoContext
    v1_segment_info: V1SegmentInfoContext
    v1_waybill_exchange_confirm: V1WaybillExchangeConfirmContext
    v1_waybill_arrive_at_point: V1WaybillArriveAtPointContext

    # Views shared settings
    waybill_ref: str = 'WAYBILL_REF'


@pytest.fixture(name='cargo_dispatch')
def cargo_dispatch(
        v1_waybill_info,
        v1_segment_info,
        v1_waybill_exchange_confirm,
        v1_waybill_arrive_at_point,
):
    return CargoDispatchContext(
        v1_waybill_info=v1_waybill_info,
        v1_segment_info=v1_segment_info,
        v1_waybill_arrive_at_point=v1_waybill_arrive_at_point,
        v1_waybill_exchange_confirm=v1_waybill_exchange_confirm,
    )
