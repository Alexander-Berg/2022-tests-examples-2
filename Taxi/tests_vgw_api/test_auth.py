import pytest


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    ('handle_name', 'params'),
    [
        ('v1/consumers/id', {'id': 1}),
        ('v1/consumers', {}),
        ('v1/forwardings', {'external_ref_id': 'ext_ref_id_1'}),
        ('v1/talk', {'talk_id': 'talk_id_1'}),
        ('v1/voice_gateways_regions/id', {'region_id': 1}),
        ('v1/voice_gateways_regions', {}),
        ('v1/talk', {'talk_id': 'talk_id_1'}),
        ('v1/voice_gateways/enabled', {'id': 'id_1'}),
        ('v1/voice_gateways/id', {'id': 'id_1'}),
        ('v1/voice_gateways/token', {'id': 'id_1'}),
        ('v1/voice_gateways', {}),
    ],
)
async def test_vgw_api_bad_tvm_ticket_get(taxi_vgw_api, handle_name, params):

    response = await taxi_vgw_api.get(
        handle_name,
        params=params,
        headers={'X-Ya-Service-Ticket': 'wrong_ticket'},
    )

    assert response.status_code == 401
