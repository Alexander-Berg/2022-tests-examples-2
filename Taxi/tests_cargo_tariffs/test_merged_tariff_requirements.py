import pytest


@pytest.fixture(name='request_admin_v1_merged_tariff_requirements')
def _request_admin_v1_merged_tariff_requirements(taxi_cargo_tariffs):
    async def wrapper(corp_client=True):
        json = {'homezone': 'moscow', 'tariff_class': 'express'}
        if corp_client:
            json['corp_client_ids'] = [
                'corp_client_id_12312312312312312',
                'corp_client_id_12312312312312323',
            ]
        response = await taxi_cargo_tariffs.post(
            '/cargo-tariffs/admin/v1/express/merged-tariff-requirements',
            json=json,
        )
        return response

    return wrapper


async def test_corp_client_id_requirements(
        request_admin_v1_merged_tariff_requirements,
        cargo_matcher_tariff_requirements,
):
    response = await request_admin_v1_merged_tariff_requirements()

    assert response.status_code == 200
    assert response.json() == {
        'requirements': [
            {
                'default': False,
                'name': 'add_req1',
                'required': True,
                'text': 'requirement.add_req1.text',
                'title': 'requirement.add_req1.title',
                'type': 'bool',
            },
            {
                'default': True,
                'name': 'add_req2',
                'required': False,
                'text': 'requirement.add_req2.text',
                'title': 'requirement.add_req2.title',
                'type': 'bool',
            },
        ],
    }


@pytest.mark.config(
    CARGO_TARIFFS_C2C_REQUIREMENTS={
        'door_to_door': {
            'title_key': 'requirement.door_to_door.title',
            'text_key': 'requirement.door_to_door.text',
            'type': 'bool',
            'default': False,
        },
        'cargo_loaders': {
            'title_key': 'requirement.cargo_loaders.title',
            'text_key': 'requirement.cargo_loaders.text',
            'type': 'select',
            'required': False,
            'variants': [
                {
                    'name': 'cargo_loaders',
                    'title_key': 'cargo_loaders.two_loaders.title',
                    'text_key': 'cargo_type.two_loaders.text',
                    'value': 2,
                },
            ],
        },
    },
)
@pytest.mark.translations(
    cargo={
        'requirement.door_to_door.text': {'ru': '???? ?????????? ???? ??????????'},
        'requirement.door_to_door.title': {'ru': '???? ?????????? ???? ??????????'},
        'requirement.cargo_loaders.text': {
            'ru': '???????????????????? ???????????????????? ??????????????????',
        },
        'requirement.cargo_loaders.title': {'ru': '???????????????????? ??????????????????'},
        'cargo_type.two_loaders.text': {'ru': '?????? ????????????????'},
        'cargo_loaders.two_loaders.title': {'ru': '?????? ????????????????'},
    },
)
async def test_c2c_requirements(
        request_admin_v1_merged_tariff_requirements,
        cargo_matcher_tariff_requirements,
        mock_tariff_settings,
):
    response = await request_admin_v1_merged_tariff_requirements(
        corp_client=False,
    )

    assert response.status_code == 200
    assert response.json() == {
        'requirements': [
            {
                'default': False,
                'name': 'door_to_door',
                'required': False,
                'text': '???? ?????????? ???? ??????????',
                'title': '???? ?????????? ???? ??????????',
                'type': 'bool',
            },
            {
                'name': 'cargo_loaders',
                'options': [
                    {
                        'text': '?????? ????????????????',
                        'title': '?????? ????????????????',
                        'value': 2,
                    },
                ],
                'required': False,
                'text': '???????????????????? ???????????????????? ??????????????????',
                'title': '???????????????????? ??????????????????',
                'type': 'select',
            },
        ],
    }
