import pytest


@pytest.mark.parametrize(
    'group_id, result, file', [(1, 200, 'ok.json'), (2, 404, None)],
)
@pytest.mark.pgsql('crm_admin', files=['init.sql'])
async def test_internal_import_export_bundle(
        web_context, web_app_client, group_id, result, file, load_json,
):
    response = await web_app_client.get(
        '/v2/campaigns/groups/sending', params={'group_id': group_id},
    )

    assert result == response.status

    if result == 200:
        expected = load_json(file)
        real = await response.json()
        assert real == expected
