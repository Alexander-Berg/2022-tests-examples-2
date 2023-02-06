import pytest

from test_infra_drills import conftest as cfg

INFRA_DRILLS_COMMON = {
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
}

INFRA_DRILLS_COMMON_DUTY_EXCLUDED_GROUPS = {
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
    'duty_groups': {
        'action': 'exclude',
        'groups': ['taxidutyinfrastructureforthesearchforacontractor'],
    },
}

INFRA_DRILLS_COMMON_DUTY_USE_ONLY_GROUP = {
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
    'duty_groups': {
        'action': 'use_only',
        'groups': ['taxidutyinfrastructureforthesearchforacontractor'],
    },
}


@pytest.mark.parametrize(
    'test_request,test_result,test_status',
    [
        (
            {
                'business_unit': 'taxi',
                'duty_date': '2222-04-19',
                'time_interval': '10-17',
            },
            {'duty': ['bmiklaz', 'kraalex']},
            200,
        ),
        (
            {
                'business_unit': 'taxi',
                'duty_date': '2222-04-20',
                'time_interval': '10-17',
            },
            {'duty': ['bmiklaz', 'maximuriev']},
            200,
        ),
        (
            {
                'business_unit': 'lavka',
                'duty_date': '2222-04-20',
                'time_interval': '10-17',
            },
            {'duty': ['andreyvavilov', 'i-klimko']},
            200,
        ),
        (
            {
                'business_unit': 'taxi',
                'duty_date': '2022-01-01',
                'time_interval': '09-20',
            },
            {
                'errors': [
                    'Wrong date 2022-01-01. The date should be in the future',
                ],
            },
            400,
        ),
    ],
)
@pytest.mark.usefixtures('taxi_infra_drills_mocks')
@pytest.mark.config(INFRA_DRILLS_COMMON=INFRA_DRILLS_COMMON)
async def test_drill_get_members(
        web_app_client,
        staff_mockserver,
        test_request,
        test_result,
        test_status,
):
    staff_mockserver()

    path = '/infra-drills/v1/duty'
    params = {
        'business_unit': test_request['business_unit'],
        'duty_date': test_request['duty_date'],
        'time_interval': test_request['time_interval'],
    }

    response = await web_app_client.get(
        path=path, params=params, headers=cfg.HEADERS,
    )

    assert response.status == test_status
    response_json = await response.json()
    assert response_json == test_result


@pytest.mark.parametrize(
    'test_request,test_result,test_status',
    [
        (
            {
                'business_unit': 'taxi',
                'duty_date': '2222-04-19',
                'time_interval': '10-17',
            },
            {'duty': ['bmiklaz']},
            200,
        ),
    ],
)
@pytest.mark.usefixtures('taxi_infra_drills_mocks')
@pytest.mark.config(
    INFRA_DRILLS_COMMON=INFRA_DRILLS_COMMON_DUTY_EXCLUDED_GROUPS,
)
async def test_drill_get_members_exlude_filter(
        web_app_client,
        staff_mockserver,
        test_request,
        test_result,
        test_status,
):
    staff_mockserver()

    path = '/infra-drills/v1/duty'
    params = {
        'business_unit': test_request['business_unit'],
        'duty_date': test_request['duty_date'],
        'time_interval': test_request['time_interval'],
    }

    response = await web_app_client.get(
        path=path, params=params, headers=cfg.HEADERS,
    )

    assert response.status == test_status
    response_json = await response.json()
    assert response_json == test_result


@pytest.mark.parametrize(
    'test_request,test_result,test_status',
    [
        (
            {
                'business_unit': 'taxi',
                'duty_date': '2222-04-19',
                'time_interval': '10-17',
            },
            {'duty': ['kraalex']},
            200,
        ),
    ],
)
@pytest.mark.usefixtures('taxi_infra_drills_mocks')
@pytest.mark.config(
    INFRA_DRILLS_COMMON=INFRA_DRILLS_COMMON_DUTY_USE_ONLY_GROUP,
)
async def test_drill_get_members_use_only_group(
        web_app_client,
        staff_mockserver,
        test_request,
        test_result,
        test_status,
):
    staff_mockserver()

    path = '/infra-drills/v1/duty'
    params = {
        'business_unit': test_request['business_unit'],
        'duty_date': test_request['duty_date'],
        'time_interval': test_request['time_interval'],
    }

    response = await web_app_client.get(
        path=path, params=params, headers=cfg.HEADERS,
    )

    assert response.status == test_status
    response_json = await response.json()
    assert response_json == test_result
