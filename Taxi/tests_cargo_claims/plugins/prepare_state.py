# pylint: disable=too-many-lines
import collections
import logging
from typing import Callable
from typing import DefaultDict
from typing import List
from typing import Optional

import pytest

from .. import conftest
from .. import utils_v2

logger = logging.getLogger(__name__)

LOG_LEVEL = logging.INFO


TAXIMETER_STATUS_BY_STATUS = {
    'performer_found': 'new',
    'pickup_arrived': 'new',
    'pickuped': 'delivering',
    'delivery_arrived': 'delivering',
    'ready_for_pickup_confirmation': 'pickup_confirmation',
    'ready_for_delivery_confirmation': 'droppof_confirmation',
    'pay_waiting': 'droppof_confirmation',
    'ready_for_return_confirmation': 'return_confirmation',
    'return_arrived': 'returning',
    'returning': 'returning',
    'cancelled': 'complete',
    'cancelled_with_payment': 'complete',
    'cancelled_by_taxi': 'complete',
    'delivered': 'complete',
    'returned': 'complete',
    'cancelled_with_items_on_hands': 'complete',
}


VALID_TRANSITIONS = [
    {'old': {'status': 'new'}, 'new': {'status': 'estimating'}},
    {'old': {'status': 'estimating'}, 'new': {'status': 'ready_for_approval'}},
    {'old': {'status': 'estimating'}, 'new': {'status': 'estimating_failed'}},
    {'old': {'status': 'ready_for_approval'}, 'new': {'status': 'accepted'}},
    {'old': {'status': 'ready_for_approval'}, 'new': {'status': 'cancelled'}},
    {'old': {'status': 'accepted'}, 'new': {'status': 'performer_lookup'}},
    {
        'old': {'status': 'performer_lookup'},
        'new': {'status': 'performer_draft'},
    },
    {
        'id': 'set_final_price',
        'old': {'status': 'performer_found'},
        'new': {'status': 'performer_found'},
        'enabled_if': {'tags_contains': {'change_price'}, 'states': {'once'}},
        'actions': [{'id': 'change_price'}],
        'priority': 5,
    },
    {
        'old': {'status': 'performer_draft'},
        'new': {'status': 'performer_found'},
    },
    {'old': {'status': 'performer_found'}, 'new': {'status': 'failed'}},
    {
        'old': {'status': 'performer_draft'},
        'new': {'status': 'performer_not_found'},
    },
    {
        'old': {'status': 'performer_found'},
        'new': {'status': 'pickup_arrived'},
    },
    {
        'old': {'status': 'pickup_arrived'},
        'new': {'status': 'ready_for_pickup_confirmation'},
    },
    {
        'old': {'status': 'ready_for_pickup_confirmation'},
        'new': {'status': 'pickuped'},
        'enabled_if': {'tags_contains': {'admin'}},
        'actions': [{'id': 'go_to_next_point'}, {'id': 'by_admin'}],
        'priority': 4,
    },
    {
        'old': {'status': 'ready_for_pickup_confirmation'},
        'new': {'status': 'pickuped'},
        'actions': [{'id': 'go_to_next_point'}],
    },
    {'old': {'status': 'pickuped'}, 'new': {'status': 'delivery_arrived'}},
    {
        'old': {'status': 'delivery_arrived'},
        'new': {'status': 'ready_for_delivery_confirmation'},
    },
    {
        'old': {'status': 'delivery_arrived'},
        'new': {'status': 'pickuped'},
        'enabled_if': {
            'tags_contains': {'return'},
            'states': {'intermediate_destination_point'},
        },
        'actions': [{'id': 'go_to_next_point'}, {'id': 'call_return'}],
        'priority': 5,
    },
    {
        'old': {'status': 'delivery_arrived'},
        'new': {'status': 'pickuped'},
        'enabled_if': {
            'tags_contains': {'admin'},
            'states': {'intermediate_destination_point'},
        },
        'actions': [{'id': 'go_to_next_point'}, {'id': 'by_admin'}],
        'priority': 5,
    },
    {
        'old': {'status': 'delivery_arrived'},
        'new': {'status': 'returning'},
        'actions': [{'id': 'go_to_return'}],
    },
    {
        'old': {'status': 'ready_for_delivery_confirmation'},
        'new': {'status': 'cancelled_with_items_on_hands'},
    },
    {
        'old': {'status': 'ready_for_pickup_confirmation'},
        'new': {'status': 'cancelled_with_payment'},
    },
    {
        'old': {'status': 'delivery_arrived'},
        'new': {'status': 'returning'},
        'enabled_if': {'tags_contains': {'admin'}},
        'actions': [{'id': 'go_to_return'}, {'id': 'by_admin'}],
        'priority': 2,
    },
    {'old': {'status': 'returning'}, 'new': {'status': 'return_arrived'}},
    {
        'old': {'status': 'return_arrived'},
        'new': {'status': 'ready_for_return_confirmation'},
    },
    {
        'old': {'status': 'ready_for_return_confirmation'},
        'new': {'status': 'returned'},
    },
    {'old': {'status': 'returned'}, 'new': {'status': 'returned_finish'}},
    {
        'old': {'status': 'ready_for_delivery_confirmation'},
        'new': {'status': 'pickuped'},
        'enabled_if': {'states': {'intermediate_destination_point'}},
        'actions': [{'id': 'go_to_next_point'}],
        'priority': 3,
    },
    {
        'old': {'status': 'ready_for_delivery_confirmation'},
        'new': {'status': 'delivered'},
        'actions': [{'id': 'delivery_at_last_point'}],
    },
    {
        'old': {'status': 'delivery_arrived'},
        'new': {'status': 'delivered'},
        'enabled_if': {'tags_contains': {'admin'}},
        'actions': [{'id': 'delivery_at_last_point'}, {'id': 'by_admin'}],
        'priority': 3,
    },
    {'old': {'status': 'delivered'}, 'new': {'status': 'delivered_finish'}},
    {
        'old': {'status': 'performer_found'},
        'new': {'status': 'cancelled_by_taxi'},
    },
]  # type: List[dict]


CURRENT_POINT_TYPE_BY_STATUS = {
    # on the way to source
    'new': 'source',
    'estimating': 'source',
    'estimating_failed': 'source',
    'ready_for_approval': 'source',
    'accepted': 'source',
    'performer_lookup': 'source',
    'performer_draft': 'source',
    'performer_found': 'source',
    'performer_not_found': 'source',
    'pickup_arrived': 'source',
    'ready_for_pickup_confirmation': 'source',
    'failed': 'source',
    'cancelled': 'source',
    'cancelled_with_payment': 'source',
    'cancelled_by_taxi': 'source',
    # on the way to destination
    'pickuped': 'destination',
    'delivery_arrived': 'destination',
    'ready_for_delivery_confirmation': 'destination',
    'cancelled_with_items_on_hands': 'destination',
    'pay_waiting': 'destination',
    # on the way to return
    'returning': 'return',
    'return_arrived': 'return',
    'ready_for_return_confirmation': 'return',
    'returned': 'return',
    'returned_finish': 'return',
}

STATUSES_WITH_NO_CURRENT_POINT = {'delivered', 'delivered_finish'}


def get_reversed_transitions(tags: Optional[set]) -> DefaultDict[str, list]:
    map_by_new_status = collections.defaultdict(
        list,
    )  # type: DefaultDict[str, list]

    for transition in VALID_TRANSITIONS:
        if (
                not transition.get('enabled_if', {})
                .get('tags_contains', set())
                .issubset(tags)
        ):
            if LOG_LEVEL == logging.DEBUG:
                logger.debug(f'{transition} skipped due no tag set')
            continue

        for registered in map_by_new_status[transition['new']['status']]:
            assert registered.get('enabled_if', {}) != transition.get(
                'enabled_if', {},
            ), 'Valid transitions should distinct, path is ambigious'

        map_by_new_status[transition['new']['status']].append(transition)

    return map_by_new_status


@pytest.fixture
def state_controller(state_controller_fixtures):
    class StateController:
        def __init__(self):
            self.fixtures = state_controller_fixtures
            self._state_context: List[StateContext] = []

        def set_options(self, *, claim_index=0, **kwargs):
            self._add_claim_for_index(claim_index)
            self._state_context[claim_index].kwargs = kwargs

        def handlers(self, *, claim_index=0):
            """
            Returns handlers context:
              Use it to override default requests.
            See HandlerContext for possible values.

            :param claim_index: claim index (for multiple claims)
            """
            self._add_claim_for_index(claim_index)
            return self._state_context[claim_index].handlers

        # After this claim is created, and we are ready to change statuses
        async def prepare(self, *, claim_index=0):
            """
            Creates claim.
            :param claim_index: claim index (for multiple claims)
            """
            self._add_claim_for_index(claim_index)

            claim_state_context = self._state_context[claim_index]
            if claim_state_context.is_prepared():
                return

            create_context: HandlerContext = (
                claim_state_context.handlers.create
            )

            claim_create_functor = self.fixtures.claims_creator[
                create_context.version
            ]

            assert create_context.update_request is None, 'use request instead'
            claim_state_context.flow_context = await claim_create_functor(
                params=create_context.params,
                request=create_context.request,
                headers=create_context.headers,
                **claim_state_context.kwargs,
            )

            claim_info = await self.get_claim_info(claim_index=claim_index)

            # Required for c2c orders
            await self.fixtures.create_segment_for_claim(
                claim_info.claim_id, expect_ok=False,
            )

            return claim_info

        async def apply(
                self,
                *,
                target_status: str,
                next_point_order: int = None,
                transition_tags: Optional[set] = None,
                claim_index=0,
                fresh_claim=True,
        ):
            """
            Sets claim in the desired state.
              Route to desired states calculates based on target_state,
            next_point_order and transition_tags.
              Possible transitions are listed in VALID_TRANSITIONS.
              By settings transition_tags it is possible to use specific
              handlers/reach corner cases etc.
              For example:
               - use admin handlers
               - change final price
               - cancel by user
               - return

            :param target_status: claim status
            :param next_point_order: current_point on desired status (for v2)
            :param transition_tags: states route tags (for corner cases)
            :param claim_index: claim index (for multiple claims)
            :param fresh_claim: set it for continue transitions in same test
            """
            if transition_tags is None:
                transition_tags = set()

            self._add_claim_for_index(claim_index)
            if not self._state_context[claim_index].is_prepared():
                await self.prepare(claim_index=claim_index)
            else:
                assert (
                    not fresh_claim
                ), 'Set fresh_claim = False, if it is on purpose'

            assert self._state_context[claim_index] is not None
            claim_info = await self._state_context[claim_index].get_claim_info(
                self.fixtures.taxi_cargo_claims,
            )

            if next_point_order is not None:
                point = claim_info.get_point_by_order(next_point_order)
            else:
                point = claim_info.get_single_point_by_status(target_status)

            target_state = State(
                status=target_status, point_id=point.api_id if point else None,
            )

            self._state_context[claim_index].find_target_path(
                target_state, claim_info, transition_tags,
            )

            for transition in self._state_context[
                    claim_index
            ].claim_transitions:
                await self._state_context[claim_index].apply_transition(
                    transition, self.fixtures,
                )

            return await self.get_claim_info(claim_index=claim_index)

        async def get_claim_info(self, *, request=None, claim_index=0):
            """
            Returns current claim info.
            See ClaimInfo for description.

            :param claim_index: claim index (for multiple claims)
            :param request: create request (for request point_id)
            """
            return await self._state_context[claim_index].get_claim_info(
                self.fixtures.taxi_cargo_claims, request=request,
            )

        def get_flow_context(self, *, claim_index=0):
            """
            Returns generated parameters.
            See FlowContext.

            :param claim_index: claim index (for multiple claims)
            """
            return self._state_context[claim_index].flow_context

        def use_create_version(self, version, *, claim_index=0):
            """
            Convenient way to set /create parameters.

            :param version: v1, v2, v2_c2c
            :param claim_index: claim index (for multiple claims)
            """
            self._add_claim_for_index(claim_index)
            handlers_context = self._state_context[claim_index].handlers
            handlers_context.create.version = version
            if version == 'v2_cargo_c2c':
                c2c_headers = conftest.get_default_headers_c2c()

                handlers_context.accept.headers = c2c_headers
                handlers_context.cancel_by_client.headers = c2c_headers

        def _add_claim_for_index(self, claim_index=0):
            while claim_index >= len(self._state_context):
                self._state_context.append(StateContext())

    return StateController()


class PointInfo:
    def __init__(
            self,
            point_id,
            visit_order,
            visit_status,
            point_type,
            return_reasons=None,
            return_comment=None,
    ):
        self.api_id = point_id
        self.type = point_type
        self.visit_order = visit_order
        self.visit_status = visit_status
        self.is_intermediate = False
        self.return_reasons = return_reasons
        self.return_comment = return_comment

    def __repr__(self):
        return (
            f'(id: {self.api_id}, type: {self.type}, '
            f'visit_order: {self.visit_order}, '
            f'is_intermediate: {self.is_intermediate})'
        )


class ClaimInfo:
    def __init__(self, claim, create_request: dict):
        self.claim_id = claim['id']
        self.current_state = self._get_current_state(claim)
        self.points = self._get_points(claim)
        self.claim_full_response = claim

    def __repr__(self):
        return (
            f'(claim_id: {self.claim_id},'
            f'state: {self.current_state}, points: {self.points}'
        )

    def get_current_point(self):
        return self.get_point_by_id(self.current_state.point_id)

    def get_point_by_id(self, point_id):
        result = None
        for point in self.points:
            if point.api_id == point_id:
                result = point
                break

        assert (
            result is not None
        ), f'Point not found by id {point_id}, points: {self.points}'

        return result

    def get_point_by_order(self, visit_order):
        point = self._get_point_by_order(visit_order)

        assert point is not None, (
            f'Point not found by visit_order {visit_order}, '
            f'points: {self.points}'
        )
        return point

    def get_single_point_by_type(self, point_type):
        chosen_point = None
        for point in self.points:
            if point.type == point_type:
                assert chosen_point is None, (
                    f'Found multiple points of type {point_type}, '
                    f'specify point with order'
                )
                chosen_point = point
        assert (
            chosen_point
        ), f'Point not found by type {point_type}, points: {self.points}'
        return chosen_point

    def get_single_point_by_status(self, status):
        if status in STATUSES_WITH_NO_CURRENT_POINT:
            return None

        point_type = CURRENT_POINT_TYPE_BY_STATUS.get(status, None)
        assert point_type is not None, (
            f'Failed to resolve single point type by status {status}, '
            f'forgot to register transition?'
        )

        return self.get_single_point_by_type(point_type)

    def get_last_destination_point(self):
        result = None
        for point in self.points[::-1]:
            if point.type == 'destination':
                result = point
                break

        assert (
            result is not None
        ), f'No destination point for claim {self.points}'
        return result

    def is_point_after_destination(self, point):
        prev_point = self._get_point_by_order(point.visit_order - 1)
        if prev_point is None:
            return False
        return prev_point.type == 'destination'

    def _get_point_by_order(self, visit_order):
        for point in self.points:
            if point.visit_order == visit_order:
                return point
        return None

    @staticmethod
    def _get_current_state(claim):
        return State(claim['status'], claim.get('current_point_id', None))

    @staticmethod
    def _get_points(claim):
        claim['route_points'].sort(key=lambda x: x['visit_order'])

        points = []
        for point in claim['route_points']:
            points.append(
                PointInfo(
                    point_id=point['id'],
                    visit_order=point['visit_order'],
                    point_type=point['type'],
                    visit_status=point['visit_status'],
                    return_reasons=point.get('return_reasons'),
                    return_comment=point.get('return_comment'),
                ),
            )

        return points


class State:
    def __init__(self, status, point_id=None):
        self.status = status
        self.point_id = point_id

    def __repr__(self):
        return f'(status: {self.status}, claim_point_id: {self.point_id})'

    def __eq__(self, other):
        if isinstance(other, State):
            return (
                self.status == other.status and self.point_id == other.point_id
            )
        return False


class Transition:
    def __init__(self, state_from: State, state_to: State, valid_transition):
        self.old = state_from
        self.new = state_to
        self.valid_transition = valid_transition if valid_transition else {}

    def has_action(self, action_id: str):
        for action in self.valid_transition.get('actions', []):
            if action['id'] == action_id:
                return True
        return False

    def __repr__(self):
        actions = [
            action['id'] for action in self.valid_transition.get('actions', [])
        ]
        return f'(old: {self.old}, new: {self.new}, actions: {actions})'


class HandlerContext:
    def __init__(
            self,
            request: Optional[dict] = None,
            update_request: Optional[Callable[[dict], None]] = None,
            version: Optional[str] = 'v1',
            params: Optional[dict] = None,
            headers: Optional[dict] = None,
    ):
        self.request = request  # for cargo_claims.create
        self.update_request = update_request  # for other handlers

        self.version = version
        self.params = params
        self.headers = headers


class HandlersContext:
    def __init__(self):
        self.accept = HandlerContext()
        self.cancel = HandlerContext()
        self.cancel_by_client = HandlerContext()
        self.create = HandlerContext()
        self.finish_estimate = HandlerContext()
        self.performer_found = HandlerContext()
        self.performer_lookup_drafted = HandlerContext()
        self.performer_not_found = HandlerContext()


class FlowContext:
    def __init__(self):
        self.claim_id = None
        self.driver_id = None
        self.park_id = None
        self.taxi_order_id = None
        self.req_point_id_to_api_id = None


class StateContext:
    def __init__(self):
        self.claim_transitions: list = None  # filled on target path chosen

        self.handlers = HandlersContext()
        self.flow_context = FlowContext()
        self.kwargs = {}

    async def get_claim_info(self, taxi_cargo_claims, request=None):
        claim = await utils_v2.get_claim(
            self.flow_context.claim_id, taxi_cargo_claims,
        )
        assert claim

        return ClaimInfo(claim, request)

    def find_target_path(self, target_state, claim_info, transition_tags):
        self.claim_transitions = []

        map_by_new_status = get_reversed_transitions(transition_tags)

        state_it = target_state
        while state_it != claim_info.current_state:
            valid_transitions = map_by_new_status.get(state_it.status, None)
            if LOG_LEVEL == logging.DEBUG:
                logger.debug(
                    f'state_it: {state_it}, '
                    f'current: {claim_info.current_state}, '
                    f'valid: {valid_transitions}',
                )

            assert valid_transitions, (
                f'Failed to reverse search for transitions: '
                f'state: {state_it}, trs: {self.claim_transitions}'
            )

            transition = _select_transition(
                valid_transitions,
                state_it,
                self.claim_transitions,
                claim_info,
            )

            logger.info(f'state_controller: {transition}')

            self.claim_transitions.append(transition)
            state_it = transition.old

        self.claim_transitions.reverse()

    def get_current_state(self, claim):
        result = None
        for point in claim['route_points']:
            if point['id'] == claim['current_point_id']:
                result = State(claim['status'], point['id'])
                break

        assert result is not None
        return result

    def set_single_taxi_order_id(self, taxi_order_id):
        self.flow_context.taxi_order_id = taxi_order_id

    def set_single_performer_info(self, *, park_id, driver_id):
        self.flow_context.park_id = park_id
        self.flow_context.driver_id = driver_id

    async def apply_transition(self, transition, dependencies):
        method = None

        new_status = transition.new.status
        if new_status == 'estimating':
            method = state_claim_estimating
        elif new_status == 'ready_for_approval':
            method = state_claim_estimated
        elif new_status == 'cancelled':
            method = state_cancelled_by_client_free
        elif new_status == 'cancelled_with_items_on_hands':
            method = state_cancelled_by_client_paid
        elif new_status == 'cancelled_with_payment':
            method = state_cancelled_by_client_paid
        elif new_status == 'cancelled_by_taxi':
            method = state_cancelled_by_taxi
        elif new_status == 'accepted':
            method = state_claim_accepted
        elif new_status == 'performer_lookup':
            method = state_lookup_started
        elif new_status == 'performer_draft':
            method = state_lookup_drafted
        elif new_status == 'performer_not_found':
            method = state_performer_not_found
        elif new_status == 'failed':
            method = state_performer_failed
        elif new_status == 'performer_found':
            if transition.has_action('change_price'):
                method = stq_final_price
            else:
                method = state_performer_found
        elif new_status in {
            'pickup_arrived',
            'delivery_arrived',
            'return_arrived',
        }:
            method = state_driver_arrived
        elif new_status in {
            'ready_for_pickup_confirmation',
            'ready_for_delivery_confirmation',
            'ready_for_return_confirmation',
        }:
            if transition.has_action('by_admin'):
                raise NotImplementedError
            else:
                method = state_driver_init
        elif new_status == 'returning':
            method = state_driver_return
        elif new_status in {'pickuped', 'delivered', 'returned'}:
            if transition.has_action('by_admin'):
                method = state_admin_confirm
            else:
                method = state_driver_confirm
        elif new_status in {'delivered_finish', 'returned_finish'}:
            method = state_order_complete
        elif new_status == 'estimating_failed':
            method = state_estimating_failed

        assert method, f'Unregistered for transition {transition}'
        await method(self, transition, dependencies)

    def is_prepared(self):
        return self.flow_context.claim_id is not None


def get_assigned_statuses():
    return [
        'new',
        'estimating',
        'ready_for_approval',
        'accepted',
        'performer_lookup',
        'performer_draft',
        'performer_found',
    ]


def _select_transition(
        valid_transitions, new_state, current_transitions, claim_info,
):
    chosen_transition = None
    if len(valid_transitions) == 1:
        chosen_transition = valid_transitions[0]
    else:
        valid_transitions.sort(
            key=lambda x: x.get('priority', 1), reverse=True,
        )

        for transition in valid_transitions:
            enabled_if_states = transition.get('enabled_if', {}).get(
                'states', set(),
            )

            already_contains = False
            if 'once' in enabled_if_states:
                for chosen_transition in current_transitions:
                    if (
                            chosen_transition.valid_transition.get('id', None)
                            == transition['id']
                    ):
                        already_contains = True
                        break
            if already_contains:
                continue

            if 'intermediate_destination_point' in enabled_if_states:
                assert new_state.point_id
                point = claim_info.get_point_by_id(new_state.point_id)

                if (
                        point.type != 'destination'
                        or not claim_info.is_point_after_destination(point)
                ):
                    continue

            chosen_transition = transition
            break

    return _make_transition(
        chosen_transition, new_state, claim_info=claim_info,
    )


def _make_transition(
        valid_transition: dict, new_state: State, claim_info: ClaimInfo,
):
    old_point_id = new_state.point_id
    for action in valid_transition.get('actions', []):
        action_id = action['id']
        if action_id == 'go_to_next_point':
            point = claim_info.get_point_by_id(new_state.point_id)
            old_point_id = claim_info.get_point_by_order(
                point.visit_order - 1,
            ).api_id
        elif action_id == 'go_to_return':
            old_point_id = claim_info.get_last_destination_point().api_id
        elif action_id == 'delivery_at_last_point':
            old_point_id = claim_info.get_last_destination_point().api_id

    return Transition(
        state_from=State(
            status=valid_transition['old']['status'], point_id=old_point_id,
        ),
        state_to=new_state,
        valid_transition=valid_transition,
    )


async def state_claim_estimating(state_context: StateContext, _, dependencies):
    response = await dependencies.taxi_cargo_claims.post(
        'v1/claims/mark/estimate-start',
        params={'claim_id': state_context.flow_context.claim_id},
        json={'version': 1},
    )
    assert response.status_code == 200, response.json()


async def state_claim_estimated(state_context: StateContext, _, dependencies):
    handler_context = state_context.handlers.finish_estimate

    body = dependencies.get_finish_estimate_request(**state_context.kwargs)
    if handler_context.update_request:
        handler_context.update_request(body)

    response = await dependencies.taxi_cargo_claims.post(
        'v1/claims/finish-estimate',
        params={'claim_id': state_context.flow_context.claim_id},
        json=body,
    )
    assert response.status_code == 200, response.json()


async def cancel_by_client(
        state_context: StateContext, dependencies, *, cancel_state,
):
    handler_context = state_context.handlers.cancel
    if not handler_context.headers:
        handler_context.headers = dependencies.get_default_headers(
            **state_context.kwargs,
        )

    response = await dependencies.taxi_cargo_claims.post(
        '/api/integration/v2/claims/cancel',
        params={'claim_id': state_context.flow_context.claim_id},
        json={'version': 1, 'cancel_state': cancel_state},
        headers=handler_context.headers,
    )
    assert response.status_code == 200, response.json()


async def state_cancelled_by_client_free(
        state_context: StateContext, _, dependencies,
):
    await cancel_by_client(state_context, dependencies, cancel_state='free')


async def state_cancelled_by_client_paid(
        state_context: StateContext, _, dependencies,
):
    await cancel_by_client(state_context, dependencies, cancel_state='paid')


async def state_claim_accepted(state_context: StateContext, _, dependencies):
    handler_context = state_context.handlers.accept
    if not handler_context.headers:
        handler_context.headers = dependencies.get_default_headers(
            **state_context.kwargs,
        )

    response = await dependencies.taxi_cargo_claims.post(
        '/v2/processing/update-status/accepted',
        params={'claim_id': state_context.flow_context.claim_id},
        headers=handler_context.headers,
        json={'version': 1, 'accept_time': '2020-01-01T00:00:00Z'},
    )
    assert response.status_code == 200, response.json()

    # Create segment
    await dependencies.create_segment_for_claim(
        state_context.flow_context.claim_id,
    )


async def state_lookup_started(state_context: StateContext, _, dependencies):
    # Do nothing, segment already create at the end of state_claim_accepted
    # So claim already in status 'performer_lookup'
    pass


async def state_lookup_drafted(state_context: StateContext, _, dependencies):
    taxi_order_id = 'taxi_order_id_1'
    state_context.set_single_taxi_order_id(taxi_order_id)

    segment_id = await dependencies.get_segment_id()
    response = await dependencies.taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                dependencies.build_segment_update_request(
                    segment_id, taxi_order_id, with_performer=False,
                ),
            ],
        },
    )
    assert response.status_code == 200


async def state_performer_not_found(
        state_context: StateContext, _, dependencies,
):
    segment_id = await dependencies.get_segment_id()
    response = await dependencies.taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                dependencies.build_segment_update_request(
                    segment_id,
                    taxi_order_id=None,
                    with_order=False,
                    with_performer=False,
                    resolution='performer_not_found',
                    revision=2,
                ),
            ],
        },
    )
    assert response.status_code == 200


async def state_performer_failed(state_context: StateContext, _, dependencies):
    segment_id = await dependencies.get_segment_id()
    response = await dependencies.taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                dependencies.build_segment_update_request(
                    segment_id,
                    state_context.flow_context.taxi_order_id,
                    revision=3,
                    resolution='technical_fail',
                ),
            ],
        },
    )
    assert response.status_code == 200


async def state_performer_found(state_context: StateContext, _, dependencies):
    segment_id = await dependencies.get_segment_id()
    response = await dependencies.taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                dependencies.build_segment_update_request(
                    segment_id,
                    state_context.flow_context.taxi_order_id,
                    revision=2,
                    car_color=state_context.kwargs.get('car_color'),
                    car_color_hex=state_context.kwargs.get('car_color_hex'),
                ),
            ],
        },
    )
    assert response.status_code == 200, response.json()

    state_context.set_single_performer_info(
        park_id='park_id1', driver_id='driver_id1',
    )


async def state_order_complete(state_context: StateContext, _, dependencies):
    response = await dependencies.taxi_cargo_claims.post(
        'v1/claims/mark/taxi-order-complete',
        params={'claim_id': state_context.flow_context.claim_id},
        json=conftest.get_order_complete_request(),
    )
    assert response.status_code == 200, response.json()


async def state_driver_arrived(
        state_context: StateContext, transition: Transition, dependencies,
):
    segment_id = await dependencies.get_segment_id()
    await dependencies.segment_arrive_at_point(
        segment_id, transition.old.point_id,
    )


async def state_driver_init(
        state_context: StateContext, transition: Transition, dependencies,
):
    if state_context.kwargs.get('set_last_change_ts_to_now', False):
        dependencies.set_last_status_change_ts()

    segment_id = await dependencies.get_segment_id()
    await dependencies.segment_exchange_init(
        segment_id, transition.old.point_id,
    )


async def state_driver_return(
        state_context: StateContext, transition: Transition, dependencies,
):
    if state_context.kwargs.get('set_last_change_ts_to_now', False):
        dependencies.set_last_status_change_ts()

    segment_id = await dependencies.get_segment_id()
    await dependencies.segment_exchange_return(
        segment_id, transition.old.point_id,
    )


async def state_driver_confirm(
        state_context: StateContext, transition: Transition, dependencies,
):
    if state_context.kwargs.get('set_last_change_ts_to_now', False):
        dependencies.set_last_status_change_ts()

    segment_id = await dependencies.get_segment_id()
    await dependencies.segment_exchange_confirm(
        segment_id, transition.old.point_id,
    )


async def state_admin_confirm(
        state_context: StateContext, transition: Transition, dependencies,
):
    response = await dependencies.taxi_cargo_claims.post(
        'v1/admin/claims/exchange/confirm',
        params={'claim_id': state_context.flow_context.claim_id},
        json={
            'last_known_status': transition.old.status,
            'new_status': transition.new.status,
            'point_id': transition.old.point_id,
            'comment': 'support_comment',
            'ticket': 'TICKET-100',
        },
    )
    assert response.status_code == 200, response.json()


async def stq_final_price(
        state_context: StateContext, transition: Transition, dependencies,
):
    claim_id = state_context.flow_context.claim_id

    await dependencies.stq_runner.cargo_claims_change_claim_order_price.call(
        task_id=claim_id,
        args=[claim_id, '239.566', 'initial_price'],
        expect_fail=False,
    )


async def state_estimating_failed(
        state_context: StateContext, transition: Transition, dependencies,
):
    response = await dependencies.taxi_cargo_claims.post(
        f'v1/claims/finish-estimate',
        params={'claim_id': state_context.flow_context.claim_id},
        json={'cars': [], 'failure_reason': 'estimating.too_large_item'},
    )
    assert response.status_code == 200, response.json()


async def state_cancelled_by_taxi(
        state_context: StateContext, transition: Transition, dependencies,
):
    segment_id = await dependencies.get_segment_id()
    response = await dependencies.taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                dependencies.build_segment_update_request(
                    segment_id,
                    state_context.flow_context.taxi_order_id,
                    with_performer=False,
                    revision=3,
                    resolution='failed',
                ),
            ],
        },
    )
    assert response.status_code == 200
