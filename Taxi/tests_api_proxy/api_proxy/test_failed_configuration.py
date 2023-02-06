async def test_failed_db_config(taxi_api_proxy, testpoint, get_file_path):
    snapshot_path = get_file_path('dynamic-proxy-snapshot.json')

    @testpoint('ConfigurationComponent/on_worker_message_end')
    def on_worker_message_end(_):
        pass

    await taxi_api_proxy.post('/admin/v1/do-reload-configuration')
    await on_worker_message_end.wait_call()

    @testpoint('ConfigurationComponent/db_load')
    def db_error_tp(_):
        return {'make_error': True}

    @testpoint('ConfigurationComponent/persistent_load')
    def snapshot_load_tp(_):
        return {'store_file': str(snapshot_path)}

    @testpoint('ConfigurationComponent::DoReloadEndpoints')
    def reload_tp(_):
        pass

    await taxi_api_proxy.post('/admin/v1/do-reload-configuration')
    await on_worker_message_end.wait_call()
    assert db_error_tp.times_called == 1
    assert snapshot_load_tp.times_called == 1
    assert reload_tp.times_called == 1

    # check that persistent configuration is loaded
    response = await taxi_api_proxy.get('/hello')
    assert response.status_code == 200
    assert response.json() == 'Hello world!'

    # now spoil persistent snapshot also
    snapshot_path = get_file_path('failed-dynamic-proxy-snapshot.json')
    await taxi_api_proxy.post('/admin/v1/do-reload-configuration')
    await on_worker_message_end.wait_call()

    # last successful state have to be used
    response = await taxi_api_proxy.get('/hello')
    assert response.status_code == 200
    assert response.json() == 'Hello world!'
