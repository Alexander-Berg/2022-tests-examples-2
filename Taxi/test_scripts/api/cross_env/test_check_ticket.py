import pytest


@pytest.mark.parametrize(
    'ticket, expected_response, st_response_data, st_response_status',
    [
        (
            'TAXIPLATFORM-1',
            {'result': 'success'},
            {
                'commentWithoutExternalMessageCount': 10,
                'commentWithExternalMessageCount': 10,
            },
            200,
        ),
        (
            'TAXIPLATFOR-1',
            {
                'status': 400,
                'msg': 'Wrong ticket queue',
                'code': 'invalid_ticket',
                'result': 'fail',
            },
            {
                'commentWithoutExternalMessageCount': 10,
                'commentWithExternalMessageCount': 10,
            },
            200,
        ),
        (
            'TAXIPLATFORM-1',
            {
                'status': 400,
                'msg': 'Too many comments in ticket, please create a new one',
                'code': 'invalid_ticket',
                'result': 'fail',
            },
            {
                'commentWithoutExternalMessageCount': 1000,
                'commentWithExternalMessageCount': 1000,
            },
            200,
        ),
        (
            'TAXIPLATFORM-1',
            {
                'status': 400,
                'msg': 'Url issues/TAXIPLATFORM-1 not found',
                'code': 'invalid_ticket',
                'result': 'fail',
            },
            {},
            404,
        ),
    ],
)
@pytest.mark.config(SCRIPTS_ST_QUEUES=['TAXIPLATFORM'])
async def test_check_regular_ticket(
        patch,
        response_mock,
        scripts_client,
        ticket,
        expected_response,
        st_response_data,
        st_response_status,
):
    @patch('taxi.clients.startrack.StartrackAPIClient._single_request')
    async def _single_request(*args, **kwargs):
        return response_mock(json=st_response_data, status=st_response_status)

    response = await scripts_client.post(
        '/v1/cross-env/check-ticket/', json={'ticket': ticket},
    )
    assert response.status == 200
    assert (await response.json()) == expected_response


async def test_finance_ticket(patch, scripts_client):
    @patch('scripts.lib.st_utils.check_finance_ticket')
    async def check(*args, **kwargs):
        pass

    response = await scripts_client.post(
        '/v1/cross-env/check-ticket/',
        json={'ticket': 'TAXIPLATFORM-1', 'is_finance': True},
    )
    assert response.status == 200
    assert len(check.calls) == 1
