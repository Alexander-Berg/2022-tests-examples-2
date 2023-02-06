import pytest


@pytest.mark.config(GLOBUS_SOFTCHECK_SETTINGS={'host': 'some.host.name'})
async def test_should_create_softcheck(
        web_app_client,
        load_json,
        mock_eats_catalog_storage,
        mock_globus_soft_check,
):
    @mock_eats_catalog_storage(
        '/internal/eats-catalog-storage/v1/places/retrieve-by-ids',
    )
    async def _mock_places(request):
        return {
            'places': [
                {
                    'id': 1,
                    'origin_id': '1',
                    'revision_id': 1,
                    'updated_at': '2020-04-28T12:00:00+03:00',
                },
            ],
            'not_found_place_ids': [],
        }

    @mock_globus_soft_check('/set-kit/softcheques/VQ8200000A/shop/1')
    async def _mock_soft_check(request):
        globus_softcheck = load_json('globus_softcheck.json')

        assert globus_softcheck == request.json

        return globus_softcheck

    request_data = load_json('soft_check.json')
    response = await web_app_client.put('/v1/create-order', json=request_data)
    assert response.status == 200
