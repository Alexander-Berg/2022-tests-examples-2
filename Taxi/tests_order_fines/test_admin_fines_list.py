async def test_fines_taken_from_config(taxi_order_fines, taxi_config):
    # from testsuite/config.json
    fines_list = taxi_config.get('ORDER_FINES_CODES')

    expected = []
    for item in fines_list:
        expected.append(item.copy())
        # "disabled" is required field in api but optional in config
        expected[-1]['disabled'] = expected[-1].get('disabled', False)
        del expected[-1]['driver_notification_params']

    response = await taxi_order_fines.get('/admin/fines/list')
    assert response.status_code == 200
    assert response.json()['fine_list'] == expected
