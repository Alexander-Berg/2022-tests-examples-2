ENDPOINTS_LIST = 'admin/v2/endpoints/list'


async def test_change_endpoint_dev_team(endpoints, load_yaml):
    handler_def = load_yaml('simple_post_handler.yaml')
    fst_dev_team = 'first-team'
    snd_dev_team = 'second-team'
    end_id = '123'
    path = '/path'

    # create endpoints
    await endpoints.safely_create_endpoint(
        endpoint_id=end_id,
        path=path,
        post_handler=handler_def,
        dev_team=fst_dev_team,
    )

    # off, then try to rename tesla to spacex
    await endpoints.safely_update_endpoint(
        endpoint_id=end_id,
        path=path,
        enabled=False,
        dev_team=snd_dev_team,
        post_handler=handler_def,
    )

    res = await endpoints.fetch_current_stable(end_id)
    assert res['dev_team'] == snd_dev_team
