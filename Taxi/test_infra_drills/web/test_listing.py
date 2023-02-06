import pytest


@pytest.mark.parametrize(
    'test_result,test_status',
    [
        (
            [
                {
                    'business_unit': 'taxi',
                    'state': 'PLANNED',
                    'drill_type': 'external',
                    'datacenter': 'IVA',
                    'drill_date': '2032-01-20',
                    'time_interval': '16:00 - 19:00',
                    'coordinator': 'temox',
                    'anchorman': 'temox',
                    'members': ['test1', 'test2'],
                    'st_ticket': 'TAXIADMIN-102',
                    'calendar_event': 123456,
                    'comment': 'comment',
                },
                {
                    'business_unit': 'taxi',
                    'state': 'PLANNED',
                    'drill_type': 'maintenance',
                    'datacenter': 'VLA',
                    'drill_date': '2032-01-29',
                    'time_interval': '16:00 - 19:00',
                    'coordinator': 'temox',
                    'anchorman': 'temox',
                    'members': ['test1'],
                    'st_ticket': 'TAXIADMIN-81',
                    'comment': 'comment',
                },
                {
                    'business_unit': 'eda',
                    'state': 'NEW',
                    'drill_type': 'internal',
                    'datacenter': 'MAN',
                    'drill_date': '2032-05-17',
                    'time_interval': '16:00 - 19:00',
                    'coordinator': 'coord_eda',
                    'anchorman': 'anchorman_eda',
                    'members': [],
                    'comment': 'comment',
                },
                {
                    'business_unit': 'lavka',
                    'state': 'NEW',
                    'drill_type': 'internal',
                    'datacenter': 'MAN',
                    'drill_date': '2032-05-17',
                    'time_interval': '10:00 - 21:00',
                    'coordinator': 'coord_lavka',
                    'anchorman': 'anchorman_lavka',
                    'members': [],
                    'comment': 'comment',
                },
                {
                    'business_unit': 'taxi',
                    'state': 'NEW',
                    'drill_type': 'internal',
                    'datacenter': 'MAN',
                    'drill_date': '2032-07-17',
                    'time_interval': '16:00 - 19:00',
                    'coordinator': 'temox',
                    'anchorman': 'temox',
                    'members': ['test1'],
                    'comment': 'comment',
                },
            ],
            200,
        ),
    ],
)
@pytest.mark.usefixtures('taxi_infra_drills_mocks')
@pytest.mark.pgsql('infra_drills', files=['basic.sql'])
async def test_drill_cards_get(
        web_app_client, staff_mockserver, test_result, test_status,
):
    staff_mockserver()

    path = '/infra-drills/v1/drill_cards'

    response = await web_app_client.get(path=path)

    assert response.status == test_status
    response_json = await response.json()
    assert response_json == test_result
