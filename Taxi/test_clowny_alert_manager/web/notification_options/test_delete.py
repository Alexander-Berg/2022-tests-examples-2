async def test_delete(
        get_notification_option,
        get_notification_options_list,
        delete_notification_option,
):
    option = await get_notification_option(1)
    assert not option['is_deleted']
    assert (
        len((await get_notification_options_list({}))['notification_options'])
        == 1
    )
    await delete_notification_option(1)
    option = await get_notification_option(1)
    assert option['is_deleted']
    assert not (await get_notification_options_list({}))[
        'notification_options'
    ]
