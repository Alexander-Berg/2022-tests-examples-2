import pytest

from test_infra_drills import conftest as cfg


@pytest.mark.parametrize(
    'test_request,test_result,test_status',
    [
        (
            {
                'business_unit': 'taxi',
                'drill_date': '2032-07-17',
                'state': 'planned',
            },
            {
                'business_unit': 'taxi',
                'drill_date': '2032-07-17',
                'state': 'PLANNED',
            },
            200,
        ),
        (
            {
                'business_unit': 'taxi',
                'drill_date': '2032-07-17',
                'state': 'deleted',
            },
            {
                'business_unit': 'taxi',
                'drill_date': '2032-07-17',
                'state': 'DELETED',
            },
            200,
        ),
        (
            {
                'business_unit': 'taxi',
                'drill_date': '2032-01-29',
                'state': 'deleted',
            },
            {
                'errors': [
                    (
                        'can\'t move from PLANNED to DELETED.'
                        ' Allowed states: NEW for DELETED'
                    ),
                ],
            },
            400,
        ),
        (
            {
                'business_unit': 'eda',
                'drill_date': '2032-05-17',
                'state': 'planned',
            },
            {
                'business_unit': 'eda',
                'drill_date': '2032-05-17',
                'state': 'PLANNED',
            },
            200,
        ),
        (
            {
                'business_unit': 'lavka',
                'drill_date': '2032-05-17',
                'state': 'NEW',
            },
            {'errors': ['state is already NEW']},
            400,
        ),
        (
            {
                'business_unit': 'taxi',
                'drill_date': '2032-01-20',
                'state': 'cancelled',
            },
            {
                'business_unit': 'taxi',
                'drill_date': '2032-01-20',
                'state': 'CANCELLED',
            },
            200,
        ),
        (
            {
                'business_unit': 'taxi',
                'drill_date': '2032-01-20',
                'state': 'finished',
            },
            {
                'business_unit': 'taxi',
                'drill_date': '2032-01-20',
                'state': 'FINISHED',
            },
            200,
        ),
        (
            {
                'business_unit': 'taxi',
                'drill_date': '2032-01-20',
                'state': 'new',
            },
            {
                'errors': [
                    (
                        'can\'t move from PLANNED to NEW. '
                        'Allowed states: No allowed states for NEW'
                    ),
                ],
            },
            400,
        ),
    ],
)
@pytest.mark.usefixtures('taxi_infra_drills_mocks')
@pytest.mark.pgsql('infra_drills', files=['basic.sql'])
@pytest.mark.translations(infra_drills=cfg.TANKER)
async def test_drill_card_move_states(
        web_app_client,
        staff_mockserver,
        test_request,
        test_result,
        test_status,
):
    staff_mockserver()

    path = '/infra-drills/v1/card_state'
    params = {
        'business_unit': test_request['business_unit'],
        'drill_date': test_request['drill_date'],
        'state': test_request['state'],
    }

    response = await web_app_client.patch(
        path=path, params=params, json={}, headers=cfg.HEADERS,
    )
    response_json = await response.json()
    assert response.status == test_status
    assert response_json == test_result
