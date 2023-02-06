import pytest

TOKEN = '4e6f81a8-891b-4e35-b4ed-f4c10f9a4987'


@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['db_iiko_transport_meta.sql'],
)
async def test_iiko_meta_cache(web_context, place_id, mock_iiko_cloud):
    transport_meta = await web_context.iiko_meta_cache.transport_meta(
        place_id=place_id,
    )
    assert transport_meta.api_login == '77c54078bb024d39ad5cb8193fe62035'
    assert (
        transport_meta.organization_id == '00000000-0000-0000-orga-00000000001'
    )
    assert (
        transport_meta.terminal_group_id
        == '00000000-0000-0000-term-00000000001'
    )

    @mock_iiko_cloud('/api/1/access_token')
    async def iiko_cloud_access_token(request):
        api_login = request.json['apiLogin']
        assert api_login == '77c54078bb024d39ad5cb8193fe62035'
        return {
            'correlationId': 'd7ca58cd-ff9a-4748-8f7e-deb19a9b14dd',
            'token': TOKEN,
        }

    authorization = await web_context.iiko_meta_cache.authorization(
        place_id=place_id,
    )
    assert authorization == f'Bearer {TOKEN}'

    _ = await web_context.iiko_meta_cache.authorization(place_id=place_id)
    assert iiko_cloud_access_token.times_called == 1
