# pylint: disable=too-many-arguments
import pytest

from taxi_billing_limits.stq import budget_alert


@pytest.mark.config(BILLING_LIMITS_CREATE_ALERT_TICKET=True)
@pytest.mark.now('2019-08-29T12:00:00.000000+00:00')
@pytest.mark.pgsql(
    'billing_limits@0', files=('limits.limits.sql', 'limits.windows.sql'),
)
@pytest.mark.parametrize(
    'task_data,ticket',
    (
        ('budget_alert_data_tumbling.json', 'ticket_tumbling.json'),
        ('budget_alert_data_sliding.json', 'ticket_sliding.json'),
    ),
)
async def test_task(stq3_context, patch, load_json, task_data, ticket):
    actual_ticket_data = None

    @patch('taxi.clients.startrack.StartrackAPIClient._request')
    async def _request(url, *_args, **kwargs):
        nonlocal actual_ticket_data
        actual_ticket_data = kwargs['json']
        actual_ticket_data.pop('unique')
        key = 'TAXIBUDGETALERT-1234'
        return {'self': f'{url}/{key}', 'key': key, 'id': 'badc0de'}

    await budget_alert.task(stq3_context, data=load_json(task_data))
    assert actual_ticket_data == load_json(ticket)


@pytest.mark.config(BILLING_LIMITS_CREATE_ALERT_TICKET=True)
@pytest.mark.now('2019-09-18T12:00:00+00:00')
@pytest.mark.pgsql(
    'billing_limits@0', files=('limits.limits.sql', 'limits.windows.sql'),
)
async def test_add_comment(stq3_context, load_json, patch):
    request_data = None

    @patch('taxi.clients.startrack.StartrackAPIClient._request')
    async def _request(url, *_args, **kwargs):
        nonlocal request_data
        request_data = kwargs['json']
        return

    await budget_alert.task(
        stq3_context, data=load_json('budget_alert_test_comment.json'),
    )
    assert request_data == load_json('comment.json')
