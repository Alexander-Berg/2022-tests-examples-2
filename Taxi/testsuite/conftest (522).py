# root conftest for service passenger-feedback
import copy
import dataclasses
import json
import typing

import pytest

pytest_plugins = ['passenger_feedback_plugins.pytest_plugins']


@dataclasses.dataclass
class CallResult:
    feedback: dict
    order: dict
    zendesk_ticket: typing.Optional[dict]
    excluded_drivers_called: bool


@pytest.fixture(params=['v1', 'v2'])
def feedback_save(request, taxi_passenger_feedback, mockserver, mongodb, stq):
    api_version = request.param

    class Context:
        version = api_version

        def _prepare_request(self, request, has_survey_result=True):
            if api_version == 'v1':
                return request
            new_request = copy.deepcopy(request)
            choices = {}
            for choice in new_request.pop('choices', []):
                choices.setdefault(choice['type'], []).append(choice['value'])
            for badge in new_request.pop('badges', []):
                choices.setdefault(badge['type'], []).append(badge['value'])
            new_request['choices'] = choices

            or_ca = new_request.pop('order_cancelled')
            or_co = new_request.pop('order_completed')
            or_fi = new_request.pop('order_finished_for_client')
            # https://wiki.yandex-team.ru/taxi/backend/statuses/
            order_status_mapping = {
                # or_ca or_co or_fi
                (False, False, False): 'assigned',
                (False, False, True): 'driving',
                (False, True, False): 'finished',
                (True, False, False): 'cancelled',
                # (False, True, True): "", impossible
                # (True, False, True): "", impossible
                # (True, True, False): "", impossible
                # (True, True, True): "", impossible
            }
            order_taxi_status_mapping = {
                # or_ca or_co or_fi
                (False, False, False): 'other',
                (False, False, True): 'other',
                (False, True, False): 'complete',
                (True, False, False): 'other',
            }
            order_status = order_status_mapping[(or_ca, or_co, or_fi)]
            order_taxi_status = order_taxi_status_mapping[
                (or_ca, or_co, or_fi)
            ]
            new_request['order_status'] = order_status
            new_request['order_taxi_status'] = order_taxi_status

            if has_survey_result:
                new_request['survey'] = [
                    {'question_id': 'q_1', 'answer_id': 'a_1'},
                ]

            return new_request

        async def call(
                self,
                request,
                expected_code: int = 200,
                has_survey_result: bool = True,
        ) -> CallResult:
            request = self._prepare_request(request, has_survey_result)

            # pylint: disable=unused-variable
            @mockserver.json_handler(
                '/excluded-drivers/excluded-drivers/v1/drivers',
            )
            def mock_excluded_drivers(inner_request):
                request_json = json.loads(inner_request.get_data())
                expected_json = {
                    'driver_license_pd_id': request['driver_license_pd_id'],
                    'order_id': request['order_id'],
                    'phone_id': request['phone_id'],
                    'personal_phone_id': request['personal_phone_id'],
                    'reason': 'bad_feedback',
                }
                assert request_json == expected_json
                return {}

            response = await taxi_passenger_feedback.post(
                f'/passenger-feedback/{api_version}/feedback', request,
            )
            assert response.status_code == expected_code

            excluded_drivers_called = mock_excluded_drivers.times_called == 1
            if not excluded_drivers_called:
                assert mock_excluded_drivers.times_called == 0

            feedback = mongodb.feedbacks_mdb.find_one(request['order_id'])
            if feedback:
                feedback.pop('updated', None)
                feedback.pop('data_updated', None)
            order = mongodb.orders.find_one(request['order_id'])
            if order:
                order.pop('_id', None)
                order.pop('_shard_id', None)
                order.pop('updated', None)
                order.pop('version', None)

            if stq.zendesk_ticket.times_called == 1:
                call_params = stq.zendesk_ticket.next_call()
                assert call_params['args'][0] == request['order_id']
                zendesk_ticket = call_params['args'][1]
            else:
                assert stq.zendesk_ticket.times_called == 0
                zendesk_ticket = None

            return CallResult(
                feedback, order, zendesk_ticket, excluded_drivers_called,
            )

    return Context()
