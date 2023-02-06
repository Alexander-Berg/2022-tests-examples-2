async def test_change_resource_dev_team(resources):
    fst_dev_team = 'first-team'
    snd_dev_team = 'second-team'
    res_id = '123'

    # create endpoints
    await resources.safely_create_resource(
        resource_id=res_id,
        url='http://url',
        method='post',
        dev_team=fst_dev_team,
    )

    # try to rename dev-team
    await resources.safely_update_resource(
        resource_id=res_id,
        url='http://url',
        method='post',
        dev_team=snd_dev_team,
    )

    res = await resources.fetch_current_stable(res_id)
    assert res['dev_team'] == snd_dev_team
