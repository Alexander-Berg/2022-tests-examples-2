import pytest


@pytest.mark.config(
    CLOWNDUCTOR_AVAILABLE_DATACENTERS={
        'projects': [{'datacenters': ['vla', 'sas'], 'name': '__default__'}],
    },
)
@pytest.mark.usefixtures('mocks_for_project_creation')
@pytest.mark.features_on('service_creation_available_regions')
@pytest.mark.parametrize(
    ['case', 'available_regions', 'declared_amount', 'env'],
    [
        pytest.param(
            'with_allowed_regions',
            ['vla'],
            3,
            'production',
            id='with_allowed_regions',
        ),
        pytest.param(
            'without_allowed_regions',
            ['vla', 'sas'],
            3,
            'production',
            id='without_allowed_regions',
        ),
        pytest.param('in_testing', ['vla'], 2, 'testing', id='in_testing'),
    ],
)
async def test_not_enough_available_regions(
        request_service_from_yaml,
        arcadia_url,
        add_project,
        case,
        available_regions,
        declared_amount,
        env,
):
    await add_project('taxi-devops')
    response = await request_service_from_yaml(
        arcadia_url(), f'not_enough_available_regions/{case}',
    )
    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'YAML_VALIDATION_ERROR',
        'message': (
            f'service.yaml has next problems:: For environment {env} '
            f'amount of available regions ({len(available_regions)}) is less'
            f' than service.yaml\'s declared amount ({declared_amount}).\n'
            f'List of available regions: {", ".join(available_regions)}'
        ),
    }
