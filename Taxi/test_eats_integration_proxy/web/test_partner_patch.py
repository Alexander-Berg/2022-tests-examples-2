import pytest


@pytest.mark.parametrize(
    'partner_id, file_name, code',
    [
        (1, 'test_partner_update.json', 200),
        (-1, 'test_partner_update.json', 404),
    ],
)
@pytest.mark.pgsql('eats_integration_proxy', files=['create_partner.sql'])
async def test_patch_partner(
        web_app_client, web_context, load_json, partner_id, file_name, code,
):
    data_update = load_json(file_name)

    response = await web_app_client.patch(
        '/partner', json=data_update, params={'id': partner_id},
    )
    assert response.status == code
