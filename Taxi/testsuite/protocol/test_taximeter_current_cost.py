import pytest

from individual_tariffs_switch_parametrize import (
    PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS,
)


@pytest.mark.parametrize(
    'order_id,expected_cost',
    [
        ('da60d02916ae4a1a91eafa3a1a8ed04d', 1523),
        ('9d17bacf1eae4bbaa898fe144e43cb16', 639),
        ('95565c253c4c415a8528bdd5888e7dc8', 199),
    ],
)
@PROTOCOL_SWITCH_TO_INDIVIDUAL_TARIFFS
def test_current_cost(
        taxi_protocol,
        order_id,
        expected_cost,
        db,
        individual_tariffs_switch_on,
):
    request = {
        'clid': '999012',
        'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
        'order': order_id,
    }
    response = taxi_protocol.get('1.x/current-cost', params=request)

    assert response.status_code == 200
    assert (
        response.headers['Content-Type'] == 'application/json; charset=utf-8'
    )

    data = response.json()
    assert data == {'current_cost': expected_cost}
