import pytest

from test_infra_drills import conftest as cfg


@pytest.mark.parametrize(
    'test_request,test_parameters,test_result,test_status',
    [
        (
            {'business_unit': 'taxi', 'drill_date': '2032-01-20'},
            {'drill_date': '2031-01-20'},
            {
                'drill_date': '2031-01-20',
                'calendar_event': 123456,
                'startrack_ticket': 'TAXIADMIN-102',
            },
            200,
        ),
        (
            {'business_unit': 'taxi', 'drill_date': '2032-01-20'},
            {'business_unit': 'lavka'},
            {
                'drill_date': '2032-01-20',
                'calendar_event': 123456,
                'startrack_ticket': 'EDAOPS-205',
            },
            200,
        ),
        (
            {'business_unit': 'taxi', 'drill_date': '2032-01-20'},
            {'time_interval': '12-15'},
            {
                'drill_date': '2032-01-20',
                'calendar_event': 123456,
                'startrack_ticket': 'TAXIADMIN-102',
            },
            200,
        ),
        (
            {'business_unit': 'taxi', 'drill_date': '2032-01-20'},
            {'time_interval': '15-12'},
            {
                'errors': [
                    (
                        'Wrong time_interval 15:00 - 12:00. '
                        'End time must be later than start time'
                    ),
                ],
            },
            400,
        ),
        (
            {'business_unit': 'taxi', 'drill_date': '2032-01-20'},
            {'drill_date': '2021-01-01'},
            {
                'errors': [
                    'Wrong date 2021-01-01. The date should be in the future',
                ],
            },
            400,
        ),
        (
            {'business_unit': 'taxi', 'drill_date': '2021-01-20'},
            {'drill_date': '2032-01-01'},
            {'errors': ['Can\'t find the drill scheduled on 2021-01-20']},
            400,
        ),
    ],
)
@pytest.mark.usefixtures('taxi_infra_drills_mocks')
@pytest.mark.pgsql('infra_drills', files=['basic.sql'])
@pytest.mark.translations(infra_drills=cfg.TANKER)
@pytest.mark.config(
    INFRA_DRILLS_COMMON={
        'business_units': [
            {
                'name': 'Такси/Доставка',
                'startrek_queue': 'TAXIADMIN',
                'unit': 'taxi',
            },
            {'name': 'Еда', 'startrek_queue': 'EDAOPS', 'unit': 'eda'},
            {'name': 'Лавка', 'startrek_queue': 'EDAOPS', 'unit': 'lavka'},
        ],
        'datacenters': ['IVA', 'MAN', 'MYT', 'SAS', 'VLA'],
        'types': [
            {'drill_description': 'Учения', 'drill_type': 'internal'},
            {'drill_description': 'Учения', 'drill_type': 'external'},
            {
                'drill_description': 'Регламентные работы',
                'drill_type': 'maintenance',
            },
        ],
        'defaults': {'default_domain': 'yandex-team-test.ru'},
    },
)
async def test_drill_card_update(
        web_app_client,
        staff_mockserver,
        test_request,
        test_parameters,
        test_result,
        test_status,
        taxi_config,
):
    staff_mockserver()

    path = '/infra-drills/v1/drill_card'
    params = {
        'business_unit': test_request['business_unit'],
        'drill_date': test_request['drill_date'],
    }

    response = await web_app_client.patch(
        path=path, params=params, json=test_parameters, headers=cfg.HEADERS,
    )

    assert response.status == test_status
    response_json = await response.json()
    assert response_json == test_result
