import tests_driver_scoring.tvm_tickets as tvm_tickets


async def test_v2_admin_scripts_interfaces(taxi_driver_scoring, load_json):
    response = await taxi_driver_scoring.get(
        'v2/admin/scripts/interfaces',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
    )
    assert response.status_code == 200
    assert response.json() == load_json('response.json')
