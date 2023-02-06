import pytest


# Generated via `tvmknife unittest service -s 444 -d 111`
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUIvAMQbw:WPKzP90'
    '8f_Y5-7PxLhkZEx1cC5i4kdTYbv4eO1h_0tDX1d1u'
    'P8Og7N_Nl1RWyGsl_Dwk3ceh581YfoyCy0iJfW-Iv'
    'zRFi8cm4R8B8bQRq-Cuu15W1z0IGwp0Gg58UNeJ8f'
    'Go-kdaqCB2RpPcthDoqA-a9Sk-Qy_Cih0jW02ueII'
)

# Generated via `tvmknife unittest service -s 111 -d 111`
DRIVER_FREEZE_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgQIbxBv:HnWBiEb0q'
    'TecqNtfSO2O8gdh0MrHRl-bPGm47DFcjRqnK6l7Dp'
    '85VtHrO0lair9AUnsbAqQ6OLdaM7sp4qVG43A_1Kz'
    'c6GeO7X6LWWeQGKIMQVOPQyVBMcfvf1SQcx-YmGnp'
    'U6CsLiWR3YOSc6cPn1Sq7XXCiMVH1sCuMNov_zQ'
)


# pylint: disable=redefined-outer-name
@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'driver-freeze'}],
    TVM_SERVICES={'driver-freeze': 111, 'mock': 444},
)
@pytest.mark.tvm2_ticket(
    {444: MOCK_SERVICE_TICKET, 111: DRIVER_FREEZE_SERVICE_TICKET},
)
async def test_tvm(taxi_driver_freeze):
    response = await taxi_driver_freeze.get(
        'frozen', headers={'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET},
    )
    assert response.status_code == 200
    response = await taxi_driver_freeze.get('frozen')
    assert response.status_code == 401
