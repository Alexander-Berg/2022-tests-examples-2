import dataclasses
import uuid

import pytest

from . import candidates_manager


@pytest.fixture(autouse=True, name='candidates')
def _candidates(load_json, mockserver):
    response = None

    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        if response is not None:
            return response
        try:
            return load_json('candidates.json')
        except FileNotFoundError:
            return {'candidates': []}

    @mockserver.json_handler('/candidates/order-satisfy')
    def _order_satisfy(request):
        if response is not None:
            return response
        try:
            return load_json('candidates.json')
        except FileNotFoundError:
            return {'candidates': []}

    def _set_response(data):
        nonlocal response
        response = data

    _set_response.order_search = _order_search
    _set_response.order_satisfy = _order_satisfy

    return _set_response


@pytest.fixture(autouse=True, name='scoring')
def _scoring(load_json, mockserver):
    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def mock(request):
        context.requests.append(request)
        if context.response is not None:
            return context.response
        response = {'responses': []}
        for req in request.json['requests']:
            candidates = []
            for candidate in req['candidates']:
                candidates.append(
                    {'id': candidate['id'], 'score': len(candidates)},
                )
            response['responses'].append({'candidates': candidates})
        return response

    class Context:
        def __init__(self):
            self.requests = []
            self.handler = mock
            self.response = None

        def __call__(self, data):
            context.response = data

    context = Context()

    return context


@pytest.fixture(autouse=True, name='driver-trackstory')
def _driver_trackstory(mockserver):
    @mockserver.json_handler('/driver-trackstory/positions')
    def _positions(request):
        return {'results': []}


@pytest.fixture(name='performer_for_order')
async def _performer_for_order(united_dispatch_unit, get_single_waybill):
    def _make_performer_request(
            *,
            taxi_order_id=None,
            generation=1,
            version=1,
            wave=1,
            callback=None,
    ):
        if taxi_order_id is None:
            taxi_order_id = get_single_waybill()['waybill']['taxi_order_id']

        return {
            'order_id': taxi_order_id,
            'allowed_classes': ['cargo'],
            'lookup': {
                'generation': generation,
                'version': version,
                'wave': wave,
            },
            'callback': callback,
            'order': {'created': 1584378627.69, 'nearest_zone': 'moscow'},
        }

    async def wrapper(**kwargs):
        response = await united_dispatch_unit.post(
            '/performer-for-order', json=_make_performer_request(**kwargs),
        )

        assert response.status_code == 200
        return response.json()

    return wrapper


@pytest.fixture(name='create_candidates_segment')
def _create_candidates_segment(create_segment):
    def wrapper(assignment_type):
        return create_segment(
            corp_client_id='candidates-testsuite',
            taxi_classes=['eda'],
            taxi_requirements={'some_requirement': True},
            pickup_coordinates=[33.5, 55.5],
            dropoff_coordinates=[33.5, 55.5],
            special_requirements={'cargo': {'cargo_pickup_points'}},
            custom_context={'candidates-testsuite': {'type': assignment_type}},
        )

    return wrapper


@pytest.fixture(name='candidate_builder')
async def _candidate_builder(load_json_var):
    def wrapper(candidate: candidates_manager.Candidate) -> dict:
        return load_json_var(
            'performer-for-order/candidate.json',
            id=candidate.id,
            **dataclasses.asdict(candidate),
        )

    return wrapper


@pytest.fixture(name='build_waybill_candidate')
async def _build_waybill_candidate(candidate_builder):
    def wrapper(*, performer_id=None, allowed_classes=None):
        if performer_id is None:
            park_id = uuid.uuid4().hex
            driver_profile_id = uuid.uuid4().hex
        else:
            park_id, driver_profile_id = performer_id.split('_')

        if allowed_classes is None:
            allowed_classes = ['courier', 'express']

        candidate = candidates_manager.make_candidate(
            park_id=park_id,
            driver_profile_id=driver_profile_id,
            classes=allowed_classes,
        )

        return candidate_builder(candidate)

    return wrapper
