import pytest


@pytest.mark.pgsql('clowny_perforator', files=['service_data.sql'])
@pytest.mark.parametrize(
    'service_id,clown_id,project_id,status,error_code',
    [
        (1, 100, 150, 200, None),
        (1, None, None, 200, None),
        (100, 100, 150, 404, 'NOT_FOUND'),
    ],
)
async def test_service_edit(
        web_app_client, service_id, clown_id, project_id, status, error_code,
):
    body = {'service_id': service_id}
    if clown_id is not None:
        body['clown_service'] = {
            'clown_id': clown_id,
            'project_id': project_id,
        }
    response = await web_app_client.post('/v1.0/services/edit', json=body)
    content = await response.json()
    assert response.status == status, content
    if status == 200:
        if not clown_id:
            assert 'clown_service' not in content
        else:
            assert content['clown_service'] == {
                'clown_id': clown_id,
                'project_id': project_id,
            }
