# pylint: disable=redefined-outer-name


async def test_get_resumes(
        web_app_client,
        superjob_mockserver_buy,
        superjob_mockserver_resumes,
        superjob_mockserver_responds,
        superjob_mockserver_password,
        run_crontask,
):
    handler_password = superjob_mockserver_password()
    handler_resumes = superjob_mockserver_resumes()
    handler_responds = superjob_mockserver_responds()
    handler_buy = superjob_mockserver_buy()

    await run_crontask('resumes_stream')
    await run_crontask('responds_stream')
    await run_crontask('resumes_broker')

    response = await web_app_client.get('/v1/resumes?cursor=0')
    data = await response.json()
    assert response.status == 200
    assert isinstance(data, dict)
    assert len(data['resumes']) == 21
    resumes = data['resumes']
    for resume in resumes:
        fields = [f['field'] for f in resume['fields']]
        assert 'resume_id' in fields
        assert 'phone' in fields
        assert 'first_name' in fields
        assert 'last_name' in fields
        assert 'middle_name' in fields
        # todo: invert city_geo_id asserts after
        #  geobase integration
        assert 'citizenship_geo_id' in fields
        assert 'city_geo_id' not in fields
        assert 'city' in fields
        assert 'citizenship' in fields
        assert 'driver_license_category_b' in fields
        assert 'driver_license_category_c' in fields
        assert 'occupation' in fields
        assert 'salary' in fields
        assert 'children' in fields
        assert 'sex' in fields
        assert 'age' in fields
        assert 'modification_date' in fields
        assert 'resume_type' in fields
    assert handler_buy.has_calls
    assert handler_resumes.has_calls
    assert handler_password.has_calls
    assert handler_responds.has_calls


async def test_cursor(
        web_app_client,
        superjob_mockserver_buy,
        superjob_mockserver_resumes,
        superjob_mockserver_password,
        run_crontask,
):
    handler_password = superjob_mockserver_password()
    handler_resumes = superjob_mockserver_resumes()
    handler_buy = superjob_mockserver_buy()

    await run_crontask('resumes_stream')
    await run_crontask('resumes_broker')

    response = await web_app_client.get('/v1/resumes?cursor=0')
    data = await response.json()
    assert data['cursor'] == '4'
    assert data['resumes']
    response = await web_app_client.get('/v1/resumes?cursor=5')
    data = await response.json()
    assert not data['resumes']
    assert handler_buy.has_calls
    assert handler_resumes.has_calls
    assert handler_password.has_calls
