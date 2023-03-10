import datetime
import json

import pytest

from taxi_approvals import stq_tasks
from taxi_approvals import utils


TARIFF_EDITOR_HOST = 'https://tariff-editor.taxi.yandex-team.ru'
MARKET_HOST = 'https://market.tplatform.yandex-team.ru'


@pytest.mark.pgsql('approvals', files=['edit.sql'])
@pytest.mark.parametrize(
    ['old_url'],
    [
        pytest.param(
            True,
            id='old_url',
            marks=[pytest.mark.features_off('use_entity_urls')],
        ),
        pytest.param(
            False,
            id='new_url',
            marks=[pytest.mark.features_on('use_entity_urls')],
        ),
    ],
)
@pytest.mark.parametrize(
    ['tplatform_namespace'],
    [
        pytest.param(None, id='no_namespace'),
        pytest.param('taxi', id='taxi_namespace'),
        pytest.param('market', id='market_namespace'),
    ],
)
async def test_send_email(
        patch, taxi_approvals_app_stq, old_url, tplatform_namespace,
):
    is_executed = False

    @patch('taxi.clients.sender.SenderClient._request')
    async def _request(_, params, data, *args, **kwargs):
        nonlocal is_executed
        url = json.loads(data['args'])['url']
        custom_url = '/test_service/test_api/2'
        if old_url:
            assert url == '/drafts/draft/2'
        elif tplatform_namespace == 'market':
            assert url == MARKET_HOST + custom_url
        else:
            assert url == TARIFF_EDITOR_HOST + custom_url
        is_executed = True
        assert params['to_email'] == 'test_login@yandex-team.ru'

    api_path = 'test_api'
    service_name = 'test_service'
    await stq_tasks.approvals_send_email(
        taxi_approvals_app_stq,
        api_path,
        service_name,
        2,
        ['test_login'],
        ['TICKET-1'],
        tplatform_namespace,
        log_extra=None,
    )
    assert is_executed


@pytest.mark.parametrize(
    'action', [utils.APPROVAL, utils.DELETE_APPROVAL, utils.REJECT],
)
@pytest.mark.pgsql('approvals', files=['edit.sql'])
async def test_send_confirmation_comment(
        patch, taxi_approvals_app_stq, action,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def _request(*args, **kwargs):
        ticket = args[0]
        assert ticket == 'TAXIRATE-35'
        text = '??????:test_login {action_text} ?? 02.02.2019 05:02:02(??????)\n{url}'
        if action == utils.APPROVAL:
            action_text = '????????????????????(??) ????????????????'
        elif action == utils.DELETE_APPROVAL:
            action_text = '????????(??) ?????????????????????????? ?? ??????????????????'
        else:
            action_text = '????????????????(??) ????????????????'
        assert kwargs == {
            'text': text.format(
                action_text=action_text,
                url=f'????????????: {TARIFF_EDITOR_HOST}/drafts/draft/1',
            ),
        }

    await stq_tasks.send_confirmation_comment(
        taxi_approvals_app_stq,
        1,
        'test_api',
        'TAXIRATE-35',
        'test_login',
        action,
        datetime.datetime(2019, 2, 2, 2, 2, 2),
    )
