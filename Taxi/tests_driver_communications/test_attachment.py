import pytest


from tests_driver_communications import utils


@pytest.mark.parametrize(
    'chat_id,expected_code', [('support_chat', 200), ('news', 500)],
)
@pytest.mark.parametrize('attach_id', ['1234', 'abcd'])
@pytest.mark.now('2020-06-01T06:35:00+0000')
async def test_driver_attachment(
        taxi_driver_communications,
        unique_drivers,
        mock_support_chat,
        experiments3,
        mock_fleet_parks_list,
        load_json,
        chat_id,
        expected_code,
        attach_id,
        mock_driver_trackstory,
):
    experiments3.add_experiments_json(
        load_json('chat_settings_support_chat.json'),
    )
    mock_support_chat.set_response(
        {'attachment_id': attach_id}, code=200, handler='attach',
    )
    unique_drivers.add_driver('db1', 'uuid1', 'unique_driver_id1')
    response = await utils.set_attachment(
        taxi_driver_communications, body='somebinarydata', chat_id=chat_id,
    )

    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json() == {'id': attach_id}


@pytest.mark.parametrize('chat_id,expected_code', [('support_chat', 200)])
@pytest.mark.parametrize('attach_id', ['1234'])
@pytest.mark.now('2020-06-01T06:35:00+0000')
async def test_driver_attachment_fleet_parks_list_error(
        taxi_driver_communications,
        unique_drivers,
        mock_support_chat,
        experiments3,
        mock_fleet_parks_list,
        load_json,
        chat_id,
        expected_code,
        attach_id,
        mock_driver_trackstory,
):
    mock_fleet_parks_list.set_return_error()

    experiments3.add_experiments_json(
        load_json('chat_settings_support_chat.json'),
    )
    mock_support_chat.set_response(
        {'attachment_id': attach_id}, code=200, handler='attach',
    )
    unique_drivers.add_driver(
        utils.PARK_ID, utils.PROFILE_ID, utils.UNIQUE_DRIVER_ID,
    )
    response = await utils.set_attachment(
        taxi_driver_communications, body='somebinarydata', chat_id=chat_id,
    )

    assert response.status_code == expected_code
