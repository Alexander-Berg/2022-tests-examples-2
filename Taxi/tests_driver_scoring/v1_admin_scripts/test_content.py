import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


@pytest.mark.config(
    TVM_ENABLED=True, TVM_RULES=[{'src': 'mock', 'dst': 'driver-scoring'}],
)
@pytest.mark.pgsql('driver_scoring', files=['sample_js_scripts.sql'])
async def test_v1_admin_scripts_content_missing(taxi_driver_scoring):
    response = await taxi_driver_scoring.get(
        'v1/admin/scripts/content?id={}'.format(0xDEAD),
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
    )

    assert response.status_code == 404


@pytest.mark.config(
    TVM_ENABLED=True, TVM_RULES=[{'src': 'mock', 'dst': 'driver-scoring'}],
)
@pytest.mark.pgsql('driver_scoring', files=['sample_js_scripts.sql'])
@pytest.mark.parametrize(
    'param_id, param_body', [(1, b'return 1'), (2, b'return 2')],
)
async def test_v1_admin_scripts_content(
        taxi_driver_scoring, param_id, param_body,
):
    response = await taxi_driver_scoring.get(
        'v1/admin/scripts/content?id={}'.format(param_id),
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
    )

    assert response.status_code == 200
    assert response.content == param_body
