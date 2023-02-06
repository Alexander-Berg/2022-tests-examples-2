import pytest


@pytest.mark.pgsql('eats_partners', files=['insert_partner_data.sql'])
@pytest.mark.parametrize(
    'response_code,partner_id,response_json',
    [
        (200, 1, 'response_1.json'),
        (404, 2, 'response_2.json'),
        (404, 3, 'response_3.json'),
    ],
)
async def test_external_partners_info(
        taxi_eats_partners,
        response_code,
        partner_id,
        response_json,
        load_json,
        mock_personal_retrieve,
):
    response = await taxi_eats_partners.get(
        '/4.0/restapp-front/partners/v1/info',
        headers={'X-YaEda-PartnerId': str(partner_id)},
    )

    assert response.status_code == response_code
    assert response.json() == load_json(response_json)
