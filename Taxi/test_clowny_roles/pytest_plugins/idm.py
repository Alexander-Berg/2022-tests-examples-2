import copy

import pytest


@pytest.fixture
def mock_idm_batch(mock_idm, mockserver):
    def _wrapper(responses_by_id=None):
        if responses_by_id is None:
            responses_by_id = {}
        ids_for_requested_roles = iter(range(1, 100500))

        @mock_idm('/api/v1/batch/')
        def _batch_handler(request):
            new_response = []
            status = 200
            for req in request.json:
                resp = {**copy.deepcopy(req), 'status_code': 200}
                status_ = 200
                reason = ''
                if req['id'] in responses_by_id:
                    mock = responses_by_id.pop(req['id'])
                    reason = mock.pop('reason', '')
                    resp.update(mock)
                    status_ = mock['status_code']
                if status_ == 200 and req['path'] == '/rolerequests/':
                    resp.setdefault('body', {})['id'] = next(
                        ids_for_requested_roles,
                    )
                if status_ == 400 and reason == 'already_requested':
                    next(ids_for_requested_roles)
                new_response.append(resp)
                status = max(status, status_)

            return mockserver.make_response(
                json={'responses': new_response}, status=status,
            )

        return _batch_handler

    return _wrapper
