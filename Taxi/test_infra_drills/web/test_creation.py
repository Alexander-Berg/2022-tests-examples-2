import pytest

from test_infra_drills import conftest as cfg


@pytest.mark.parametrize(
    'test_request,test_result,test_status',
    [
        (
            {
                'business_unit': 'taxi',
                'drill_type': 'internal',
                'datacenter': 'MAN',
                'drill_date': '2030-02-10',
                'time_interval': '16-19',
                'coordinator': 'temox_coord',
                'anchorman': 'temox',
                'comment': 'comment',
            },
            {
                'drill_date': '2030-02-10',
                'calendar_event': 'no calendar event for draft',
                'startrack_ticket': 'no startrek ticket for draft',
            },
            200,
        ),
        (
            {
                'business_unit': 'eda',
                'drill_type': 'internal',
                'datacenter': 'MAN',
                'drill_date': '2030-02-10',
                'time_interval': '15-18',
                'coordinator': 'temox_coord',
                'anchorman': 'temox',
                'comment': 'comment',
            },
            {
                'drill_date': '2030-02-10',
                'calendar_event': 'no calendar event for draft',
                'startrack_ticket': 'no startrek ticket for draft',
            },
            200,
        ),
        (
            {
                'business_unit': 'lavka',
                'drill_type': 'internal',
                'datacenter': 'MAN',
                'drill_date': '2030-02-10',
                'time_interval': '17-20',
                'coordinator': 'temox_coord',
                'anchorman': 'temox',
                'comment': 'comment',
            },
            {
                'drill_date': '2030-02-10',
                'calendar_event': 'no calendar event for draft',
                'startrack_ticket': 'no startrek ticket for draft',
            },
            200,
        ),
    ],
)
@pytest.mark.usefixtures('taxi_infra_drills_mocks')
@pytest.mark.pgsql('infra_drills', files=['basic.sql'])
@pytest.mark.translations(infra_drills=cfg.TANKER)
async def test_drill_card_create(
        web_app_client,
        staff_mockserver,
        test_request,
        test_result,
        test_status,
):
    staff_mockserver()

    path = '/infra-drills/v1/drill_card'

    response = await web_app_client.put(
        path=path, json=test_request, headers=cfg.HEADERS,
    )
    assert response.status == test_status
    response_json = await response.json()
    assert response_json == test_result


@pytest.mark.parametrize(
    'test_request,test_result,test_status',
    [
        (
            {
                'business_unit': 'taix',
                'drill_type': 'internal',
                'datacenter': 'MAN',
                'drill_date': '2030-02-10',
                'time_interval': '16-19',
                'coordinator': 'temox_coord',
                'anchorman': 'temox',
                'comment': 'comment',
            },
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'message': 'Some parameters are invalid',
                'details': {
                    'reason': (
                        'Invalid value for business_unit: \'taix\' '
                        'must be one of [\'taxi\', \'eda\', \'lavka\']'
                    ),
                },
            },
            400,
        ),
        (
            {
                'business_unit': 'eda',
                'drill_type': 'inernal',
                'datacenter': 'MAN',
                'drill_date': '2030-02-10',
                'time_interval': '15-18',
                'coordinator': 'temox_coord',
                'anchorman': 'temox',
                'comment': 'comment',
            },
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'message': 'Some parameters are invalid',
                'details': {
                    'reason': (
                        'Invalid value for drill_type: \'inernal\' '
                        'must be one of [\'internal\', \'external\', '
                        '\'maintenance\']'
                    ),
                },
            },
            400,
        ),
        (
            {
                'business_unit': 'lavka',
                'drill_type': 'internal',
                'datacenter': 'AMN',
                'drill_date': '2030-02-10',
                'time_interval': '17-20',
                'coordinator': 'temox_coord',
                'anchorman': 'temox',
                'comment': 'comment',
            },
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'message': 'Some parameters are invalid',
                'details': {
                    'reason': (
                        'Invalid value for datacenter: \'AMN\' '
                        'must be one of [\'IVA\', \'MAN\', \'MYT\', '
                        '\'SAS\', \'VLA\']'
                    ),
                },
            },
            400,
        ),
        (
            {
                'business_unit': 'lavka',
                'drill_type': 'internal',
                'datacenter': 'MAN',
                'drill_date': '2022-01-01',
                'time_interval': '17-20',
                'coordinator': 'temox_coord',
                'anchorman': 'temox',
                'comment': 'comment',
            },
            {
                'errors': [
                    'Wrong date 2022-01-01. The date should be in the future',
                ],
            },
            400,
        ),
        (
            {
                'business_unit': 'taxi',
                'drill_type': 'internal',
                'datacenter': 'MAN',
                'drill_date': '2030-02-10',
                'time_interval': '19-16',
                'coordinator': 'temox_coord',
                'anchorman': 'temox',
                'comment': 'comment',
            },
            {
                'errors': [
                    (
                        'Wrong time_interval 19:00 - 16:00. '
                        'End time must be later than start time'
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
async def test_drill_card_creating_issues(
        web_app_client,
        staff_mockserver,
        test_request,
        test_result,
        test_status,
):
    staff_mockserver()

    path = '/infra-drills/v1/drill_card'

    response = await web_app_client.put(
        path=path, json=test_request, headers=cfg.HEADERS,
    )

    assert response.status == test_status
    response_json = await response.json()
    assert response_json == test_result
