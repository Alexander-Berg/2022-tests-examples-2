import pytest

from launch_use_input_user_parametrize import LAUNCH_USE_INPUT_FIELDS


@LAUNCH_USE_INPUT_FIELDS
@pytest.mark.experiments3(filename='exp3_launch_zuser.json')
def test_preserve(taxi_protocol, db, use_input_fields):
    response = taxi_protocol.post(
        '3.0/launch', {'id': 'z0000000000000000000000000000000'},
    )
    assert response.status_code == 200
    data = response.json()
    assert not data['authorized']
    user_id = data['id']
    assert user_id == 'z0000000000000000000000000000000'
    assert db.users.find_one({'_id': user_id}) is None
