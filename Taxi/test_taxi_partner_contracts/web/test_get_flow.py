import pytest


HEADERS = {
    'X-YaTaxi-Api-Key': 'a8f5513cc4c84d18b56acd86bdd691ed',
    'Content-Type': 'application/json',
}

EXPECTED_DATA_RUS = {
    'flow_data': {
        'code': 'close_contract_refresh_oferta_corporate',
        'id': 'cb24b98fe1244ec298cbe8aa5e04d7bd',
        'is_automate_registration': True,
        'name': 'flows.close_contract_refresh_oferta_corporate',
        'version': 2,
        'stages': [
            {
                'code': '__default__',
                'fallback_sample': None,
                'name': (
                    'flows.close_contract_refresh_'
                    'oferta_corporate.stages.__default__'
                ),
                'sample_names': ['sample_1'],
            },
        ],
    },
    'linked_samples': [
        {
            'code': 'sample_1',
            'fields': [
                {'field': 'clid', 'field_type': 'from_form', 'name': 'clid'},
                {
                    'field_type': 'default',
                    'name': 'change_name',
                    'value': 'contracts',
                },
            ],
            'id': '83058d57ec2c4e52a558dc8a4f5a63e9',
            'sample_type': 'SOME_TYPE',
            'stage': '__default__',
        },
    ],
}

EXPECTED_DATA_KAZ = {
    'flow_data': {
        'code': 'close_contract_refresh_oferta_corporate',
        'id': 'cb24b98fe1244ec298cbe8aa5e04d7bc',
        'is_automate_registration': True,
        'name': 'flows.close_contract_refresh_oferta_corporate',
        'stages': [
            {
                'code': '__default__',
                'fallback_sample': None,
                'name': (
                    'flows.close_contract_refresh_'
                    'oferta_corporate.stages.__default__'
                ),
                'sample_names': ['sample_2'],
            },
        ],
    },
    'linked_samples': [
        {
            'code': 'sample_2',
            'fields': [
                {'field': 'clid', 'field_type': 'from_form', 'name': 'clid'},
                {
                    'field_type': 'default',
                    'name': 'change_name',
                    'value': 'contracts',
                },
            ],
            'id': '83058d57ec2c4e52a558dc8a4f5a63ea',
            'sample_type': 'SOME_TYPE',
            'stage': '__default__',
        },
    ],
}


@pytest.mark.parametrize(
    'country_code,flow_code,expected_status,expected_content',
    [
        (
            'rus',
            'close_contract_refresh_oferta_corporate',
            200,
            EXPECTED_DATA_RUS,
        ),
        (
            'kaz',
            'close_contract_refresh_oferta_corporate',
            200,
            EXPECTED_DATA_KAZ,
        ),
        ('rus', 'not_existed', 404, None),
    ],
)
async def test_get_flow(
        web_app_client,
        country_code,
        flow_code,
        expected_status,
        expected_content,
):
    params = {'country_code': country_code, 'flow_code': flow_code}
    response = await web_app_client.get(
        '/admin/v1/flow/', params=params, headers=HEADERS,
    )

    if response.status == 200:
        content = await response.json()
        assert (response.status, content) == (
            expected_status,
            expected_content,
        ), (
            'response status {}, expected {}, '
            'response content {!r}, expected {!r}'.format(
                response.status, expected_status, content, expected_content,
            )
        )
    else:
        content = await response.text()
        assert response.status == expected_status, f'Content: {content}'
