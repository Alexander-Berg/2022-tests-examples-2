import pytest

from test_hiring_selfreg_forms import conftest


ROUTE = '/v1/eda/tickets/zendesk-ticket-id'


@pytest.mark.parametrize(
    'form_completion_id, code',
    [
        ('00000000000000000000000000000001', 'form_not_found'),
        ('00000000000000000000000000000000', 'pending_for_id'),
    ],
)
@conftest.main_configuration
async def test_eda_tickets_zendesk_ticket_id(
        make_request, set_ticket_id, form_completion_id, code,
):
    async def make_ticket_request(params, status_code=200):
        _data = await make_request(
            ROUTE, method='get', params=params, status_code=status_code,
        )
        return _data

    some_ticket_id = 100

    arg = {'form_completion_id': form_completion_id}
    if code == 'pending_for_id':
        data = await make_ticket_request(params=arg, status_code=200)
        assert data['code'] == code

        res = set_ticket_id(form_completion_id, some_ticket_id)
        assert res
        data = await make_ticket_request(params=arg, status_code=200)
        assert data['code'] != code
        assert data['zendesk_ticket_id'] == some_ticket_id
    elif code == 'form_not_found':
        data = await make_ticket_request(params=arg, status_code=404)
        assert data['code'] == code
