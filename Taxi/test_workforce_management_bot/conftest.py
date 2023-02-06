# pylint: disable=redefined-outer-name
import pytest

from test_workforce_management_bot import data
import workforce_management_bot.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['workforce_management_bot.generated.service.pytest_plugins']

WFM = '/workforce-management-py3'
OPERATORS_CHECK = f'{WFM}/v1/operators/check'
SHIFT_VALUES = f'{WFM}/v2/shifts/values'
SHIFT_EVENTS_VALUES = f'{WFM}/v1/shift/event/values'
ADDITIONAL_SHIFTS_JOBS_VALUES = f'{WFM}/v1/additional-shifts/job/values'
ADDITIONAL_SHIFT_ACCEPT = f'{WFM}/v1/additional-shift/accept'
ADDITIONAL_SHIFT_REJECT = f'{WFM}/v1/additional-shift/reject'


@pytest.fixture()
def mock_wfm(mockserver):
    def patch_request(statuses=None, bodies=None):
        if bodies is None:
            bodies = {}

        if statuses is None:
            statuses = {}

        @mockserver.json_handler(OPERATORS_CHECK, raw_request=True)
        def _(request, *args, **kwargs):
            status = statuses.get(OPERATORS_CHECK, 200)
            body = bodies.get(OPERATORS_CHECK)
            if status == 200:
                return mockserver.make_response(
                    json=body
                    or {
                        'yandex_uid': '123',
                        'state': 'ready',
                        'domain': 'taxi',
                    },
                    status=status,
                )
            return mockserver.make_response(
                json=body or {'code': 'error', 'message': 'error'},
                status=status,
            )

        @mockserver.json_handler(SHIFT_EVENTS_VALUES, raw_request=True)
        def _(request, *args, **kwargs):
            status = statuses.get(SHIFT_EVENTS_VALUES, 200)
            return mockserver.make_response(
                json={
                    'shift_events': [
                        {'id': 1, 'alias': 'Отдых'},
                        {'id': 2, 'alias': 'Химиотерапия'},
                        {'id': 3, 'alias': 'Тест на ковид'},
                    ],
                },
                status=status,
            )

        @mockserver.json_handler(SHIFT_VALUES, raw_request=True)
        def _(request, *args, **kwargs):
            status = statuses.get(SHIFT_VALUES, 200)
            return mockserver.make_response(json=data.SHIFTS, status=status)

        @mockserver.json_handler(
            ADDITIONAL_SHIFTS_JOBS_VALUES, raw_request=True,
        )
        def _(request, *args, **kwargs):
            status = statuses.get(ADDITIONAL_SHIFTS_JOBS_VALUES, 200)
            body = bodies.get(ADDITIONAL_SHIFTS_JOBS_VALUES)
            return mockserver.make_response(
                json=body or data.ADDITIONAL_SHIFTS_JOBS, status=status,
            )

        @mockserver.json_handler(ADDITIONAL_SHIFT_ACCEPT, raw_request=True)
        def _(request, *args, **kwargs):
            status = statuses.get(ADDITIONAL_SHIFT_ACCEPT, 200)
            body = bodies.get(ADDITIONAL_SHIFT_ACCEPT)
            return mockserver.make_response(json=body or {}, status=status)

        @mockserver.json_handler(ADDITIONAL_SHIFT_REJECT, raw_request=True)
        def _(request, *args, **kwargs):
            status = statuses.get(ADDITIONAL_SHIFT_REJECT, 200)
            body = bodies.get(ADDITIONAL_SHIFT_REJECT)
            return mockserver.make_response(json=body or {}, status=status)

    return patch_request


@pytest.fixture()
async def registered_operator(web_context):
    collection = web_context.mongo.workforce_management_bot_operators_bounds
    await collection.insert_one(
        {'yandex_uid': '123', 'telegram': 'roma', 'chat_id': 1},
    )
