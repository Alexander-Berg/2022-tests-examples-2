from tests_driver_communications import utils


async def test_channels(
        taxi_driver_communications,
        experiments3,
        load_json,
        taxi_config,
        mockserver,
        mock_fleet_parks_list,
        unique_drivers,
        mock_driver_trackstory,
):
    experiments3.add_experiments_json(
        load_json('chat_settings_channel_test.json'),
    )

    @mockserver.json_handler('/feeds/v1/summary')
    def __summary(request):
        assert [
            '',
            'absent_in_config',
            'taximeter:City:МОСКВА',
            'taximeter:Country:РОССИЯ',
            'taximeter:Driver:db1:uuid1',
            'taximeter:Park:db1',
            'z_channel_2db1uuid1',
            'db1:uuid1',
            'z_channel_4',
        ] == request.json['channels']
        response = {
            'counts': {
                'published': 0,
                'viewed': 0,
                'total': 0,
                'read': 0,
                'removed': 0,
            },
        }
        return mockserver.make_response(json=response, status=200)

    chat = utils.get_chat(last_polling_time='2020-05-01T11:50:15.277047+0000')
    await utils.chats_polling_v2(
        taxi_driver_communications, body=utils.get_chats_request(chats=[chat]),
    )
