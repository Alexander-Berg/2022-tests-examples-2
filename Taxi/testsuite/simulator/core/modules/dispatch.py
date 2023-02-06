"""
    Describes dispatch models.

    Currently provides interface over united-dispatch, describe API
    over it if needed to try out custom dispatch models.
"""

from typing import Callable
from typing import List
import uuid

from tests_plugins import userver_client

from simulator.core import stats
from simulator.core import structures
from tests_united_dispatch.plugins import candidates_manager
from tests_united_dispatch.plugins import cargo_dispatch_manager

SegmentBuilderType = Callable[[cargo_dispatch_manager.Segment], dict]
InternalWaybillBuilderType = Callable[[cargo_dispatch_manager.Waybill], dict]
CandidateBuilderType = Callable[[candidates_manager.Candidate], dict]


def _segments_as_input(
        segments: List[cargo_dispatch_manager.Segment],
        segment_builder: SegmentBuilderType,
) -> List[dict]:
    input_segments = []
    for segment in segments:
        input_segments.append({'info': segment_builder(segment)})
    return input_segments


def _waybills_as_input(
        waybills: List[structures.DispatchWaybill],
        internal_waybill_builder: InternalWaybillBuilderType,
        candidate_builder: CandidateBuilderType,
) -> List[dict]:
    input_waybills = []
    for waybill in waybills:
        input_waybill = {
            'id': waybill.id,
            'info': internal_waybill_builder(waybill.info),
        }
        if waybill.candidate:
            input_waybill['candidate'] = {
                'info': candidate_builder(waybill.candidate),
                'assigned_at': waybill.candidate.assigned_at,
            }
        input_waybills.append(input_waybill)
    return input_waybills


def _parse_output_waybill(output_waybill: dict) -> structures.DispatchWaybill:
    waybill_id = output_waybill['id']

    waybill = cargo_dispatch_manager.parse_waybill(
        waybill_id=waybill_id, waybill_json=output_waybill['info'],
    )

    candidate = None

    if 'candidate' in output_waybill:
        candidate = candidates_manager.parse_candidate(
            candidate_info=output_waybill['candidate']['info'],
            assigned_at=output_waybill['candidate']['assigned_at'],
        )

    return structures.DispatchWaybill(info=waybill, candidate=candidate)


def _parse_output(output_json: dict) -> structures.DispatchOutput:
    propositions = []
    for proposition in output_json['propositions']:
        result = _parse_output_waybill(proposition)
        propositions.append(result)

    assigned_candidates = []
    for assigned_candidate in output_json['assigned_candidates']:
        result = _parse_output_waybill(assigned_candidate)
        assert result.candidate
        assigned_candidates.append(result)

    return structures.DispatchOutput(
        propositions=propositions,
        assigned_candidates=assigned_candidates,
        passed_segment_ids=output_json['passed_segment_ids'],
        skipped_segment_ids=output_json['skipped_segment_ids'],
    )


class DispatchModel:
    _UNITED_DISPATCH: userver_client.Client
    _SEGMENT_BUILDER: SegmentBuilderType
    _INTERNAL_WAYBILL_BUILDER: InternalWaybillBuilderType
    _CANDIDATE_BUILDER: CandidateBuilderType
    stats: structures.DispatchStats = structures.DispatchStats()

    @classmethod
    def set_fixtures(
            cls,
            united_dispatch: userver_client.Client,
            segment_builder: SegmentBuilderType,
            internal_waybill_builder: InternalWaybillBuilderType,
            candidate_builder: CandidateBuilderType,
    ):
        cls._UNITED_DISPATCH = united_dispatch
        cls._SEGMENT_BUILDER = segment_builder
        cls._INTERNAL_WAYBILL_BUILDER = internal_waybill_builder
        cls._CANDIDATE_BUILDER = candidate_builder
        cls.stats = structures.DispatchStats()

    @classmethod
    async def run(
            cls,
            segments: List[cargo_dispatch_manager.Segment],
            active_waybills: List[structures.DispatchWaybill],
            planner_type='delivery',
    ) -> structures.DispatchOutput:
        response = await cls._UNITED_DISPATCH.post(
            '/simulation/step',
            json={
                'segments': _segments_as_input(segments, cls._SEGMENT_BUILDER),
                'waybills': _waybills_as_input(
                    active_waybills,
                    cls._INTERNAL_WAYBILL_BUILDER,
                    cls._CANDIDATE_BUILDER,
                ),
                'planner_type': planner_type,
                'gamble_id': uuid.uuid4().hex,
            },
        )
        assert response.status_code == 200

        output = _parse_output(response.json())

        return output

    @classmethod
    def gather_statistics(cls):
        dispatch_agg = stats.DispatchStatsAggregation()
        dispatch_agg.aggregate(cls.stats)

        return dispatch_agg.gather()
