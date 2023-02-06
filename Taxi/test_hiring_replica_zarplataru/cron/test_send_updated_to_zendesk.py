import collections

import aiohttp
import pytest


@pytest.mark.config(ZARPLATARU_DELIVERY_TO_ZENDESK_ENABLED=False)
async def test_nothing_if_disabled(_step_send_to_zendesk):
    step = await _step_send_to_zendesk()
    assert not step.resume_updates_calls


@pytest.mark.config(ZARPLATARU_DELIVERY_TO_ZENDESK_ENABLED=True)
async def test_has_calls_if_enabled(_step_send_to_zendesk):
    step = await _step_send_to_zendesk()
    assert step.resume_updates_calls and step.infrazendesk_calls


@pytest.mark.config(ZARPLATARU_DELIVERY_TO_ZENDESK_ENABLED=True)
async def test_personal_route(_step_send_to_zendesk):
    step = await _step_send_to_zendesk()
    assert step.infrazendesk_calls[0].personal_route == 'zarplataru'


@pytest.mark.config(ZARPLATARU_DELIVERY_TO_ZENDESK_ENABLED=True)
async def test_keep_cursor(_step_send_to_zendesk, send_updated_to_zendesk):
    step = await _step_send_to_zendesk()
    await send_updated_to_zendesk()
    # First two calls from first cron run, second from last.
    # In second cron run cursor were taken from database.
    assert step.resume_updates_calls == ['first', 'last', 'last']


@pytest.mark.config(ZARPLATARU_DELIVERY_TO_ZENDESK_ENABLED=True)
async def test_dont_send_already_sent_phones(_step_send_to_zendesk):
    step = await _step_send_to_zendesk()
    # with one call to infrazendesk with two updates
    assert len(step.infrazendesk_calls) == 1


@pytest.mark.config(ZARPLATARU_DELIVERY_TO_ZENDESK_ENABLED=True)
@pytest.mark.config(ZARPLATARU_ZENDESK_DELIVERY_EXPIRATION_SECONDS=-10)
async def test_process_old_phones_as_new(_step_send_to_zendesk):
    step = await _step_send_to_zendesk()
    phones = [c.payload['phone'] for c in step.infrazendesk_calls]
    num_calls = len(step.infrazendesk_calls)
    # send the same phone two times
    assert num_calls == 4 and len(phones) == 4 and len(set(phones)) == 1


@pytest.mark.config(ZARPLATARU_DELIVERY_TO_ZENDESK_ENABLED=True)
async def test_payload(_step_send_to_zendesk, load_json, load):
    expected_payload = load_json('expected_payload_without_comment.json')
    expected_payload['comment'] = load('expected_comment.txt').strip()

    step = await _step_send_to_zendesk()
    payload = step.infrazendesk_calls[0].payload

    assert payload == expected_payload


@pytest.mark.config(ZARPLATARU_DELIVERY_TO_ZENDESK_ENABLED=True)
async def test_treat_409_as_200(
        _step_send_to_zendesk, send_updated_to_zendesk,
):
    step = await _step_send_to_zendesk(infranaim_response_code=409)
    first_time_calls_num = len(step.infrazendesk_calls)
    await send_updated_to_zendesk()
    second_time_calls_num = len(step.infrazendesk_calls) - first_time_calls_num
    assert first_time_calls_num and not second_time_calls_num


@pytest.fixture
def _step_send_to_zendesk(
        build_infrazendesk_handler,
        send_updated_to_zendesk,
        _replica_zarplataru_mockserver,
        load_json,
):
    async def _wrapper(infranaim_response_code=200):
        class _Request(
                collections.namedtuple('_Request', 'personal_route payload'),
        ):
            pass

        class InfrazendeskResponseBuilder:
            calls = []

            def __call__(self, personal_route, payload):
                self.calls.append(_Request(personal_route, payload))
                return aiohttp.web.json_response(
                    status=infranaim_response_code, data={},
                )

        class ReplicaResumeUpdatesBuilder:
            calls = []

            def __call__(self, cursor=None):
                if cursor is None:
                    cursor = 'first'
                self.calls.append(cursor)
                return load_json('resume_updates_at_cursor_%s.json' % cursor)

        infrazendesk_response_builder = InfrazendeskResponseBuilder()
        resume_updates_response_builder = ReplicaResumeUpdatesBuilder()

        infrazendesk_handler_ = build_infrazendesk_handler(
            infrazendesk_response_builder,
        )
        resume_updates_handler_ = _replica_zarplataru_mockserver(
            resume_updates_response_builder,
        )

        class Step:
            infrazendesk_handler = infrazendesk_handler_
            resume_updates_handler = resume_updates_handler_
            infrazendesk_calls = infrazendesk_response_builder.calls
            resume_updates_calls = resume_updates_response_builder.calls

        await send_updated_to_zendesk()

        return Step()

    return _wrapper


@pytest.fixture
def _replica_zarplataru_mockserver(mockserver):
    def _wrapper(response_builder):
        @mockserver.json_handler(
            '/hiring-replica-zarplataru/v1/resumes/updates',
        )
        async def _handler(request):
            assert request.method == 'GET', 'only GET method supported'
            cursor = request.query.get('cursor')
            return response_builder(cursor)

        return _handler

    return _wrapper
