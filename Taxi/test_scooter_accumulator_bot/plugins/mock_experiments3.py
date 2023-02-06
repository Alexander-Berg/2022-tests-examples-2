import aiohttp.web
import pytest

from scooter_accumulator_bot.telegram_bot import notification


def experiments_get(request):
    assert request.method == 'POST'
    assert (
        request.json['consumer']
        == 'scooter_accumulator_bot/users_to_notificate'
    )

    exp = {'note_types': []}
    for arg in request.json['args']:
        if arg['name'] == 'role' and arg['type'] == 'string':
            if arg['value'] == 'STOREKEEPER':
                exp['note_types'].append(
                    notification.Type.CHARGES_UPDATE_REQUEST,
                )
            elif arg['value'] == 'STOREKEEPER_MANAGER':
                exp['note_types'].append(
                    notification.Type.VALIDATE_ACCUMULATORS_RESPONSE,
                )
            elif arg['value'] == 'ADMIN':
                exp['note_types'].append(
                    notification.Type.VALIDATE_ACCUMULATORS_RESPONSE,
                )
                exp['note_types'].append(notification.Type.JOB_SKIPPED)
                exp['note_types'].append(
                    notification.Type.MISSION_COMPLETED_MANUALLY,
                )
            elif arg['value'] == 'REPAIRER':
                exp['note_types'].append(notification.Type.JOB_SKIPPED)

    res = {'items': []}
    res['items'].append(
        dict(name='scooter_accumulator_bot_notification_settings', value=exp),
    )

    return res


@pytest.fixture(name='mock_experiments3')
def do_mock_experiments3(mockserver):
    def mocker(path, prefix=False, raw_request=False, regex=False):
        def wrapper(func):
            full_path = '/experiments3' + path
            return mockserver.json_handler(
                full_path, prefix=prefix, raw_request=raw_request, regex=regex,
            )(func)

        return wrapper

    return mocker


@pytest.fixture
def scooter_accumulator_bot_experiments_mocks(
        mock_experiments3,
):  # pylint: disable=C0103
    @mock_experiments3('/v1/configs')
    async def _experiments_get(request):
        return aiohttp.web.json_response(experiments_get(request))

    return _experiments_get
