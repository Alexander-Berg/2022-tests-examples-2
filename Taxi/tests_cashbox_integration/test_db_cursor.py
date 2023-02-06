import json


def get_external_id_ck(ck_request):
    return ck_request['request'].headers['X-Request-ID']


def check_requests_post_to_cashbox(ck_cashbox_handle, expected_external_ids):
    external_ids = set()
    while ck_cashbox_handle.has_calls:
        request = ck_cashbox_handle.next_call()
        external_ids.add(get_external_id_ck(request))

    assert external_ids == expected_external_ids


def get_uuid_ck(ck_request):
    receipt = json.loads(ck_request['request'].get_data())
    return receipt['Id']


def check_requests_get_status(ck_cashbox_handle, expected_uuids):
    uuids = set()
    while ck_cashbox_handle.has_calls:
        request = ck_cashbox_handle.next_call()
        uuids.add(get_uuid_ck(request))

    assert uuids == expected_uuids


async def test_push_to_cashbox(
        mockserver,
        atol_get_token,
        taxi_cashbox_integration,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    # test doesn't check the right order of database pass
    # test check only that all elements in db was passed
    # and that cursor doesn't loop anywhere

    @mockserver.json_handler('cashbox-cloud-kassir/kkt/receipt')
    def ck_post_receipt(request):
        return mockserver.make_response(status=500)

    taxi_config.set_values(
        {
            'CASHBOX_INTEGRATION_PUSH_TO_CASHBOX': {
                'enable': True,
                'request_count': 1,
            },
        },
    )

    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')
    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')
    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')
    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')

    check_requests_post_to_cashbox(
        ck_post_receipt, set(['key1', 'key2', 'key3']),
    )

    # run again to check that after reaching the end of db
    # cursor wil be reseted and will start pass db again
    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')
    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')
    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')
    await taxi_cashbox_integration.run_periodic_task('ReceiptsPusher0')

    check_requests_post_to_cashbox(
        ck_post_receipt, set(['key1', 'key2', 'key3']),
    )


async def test_wait_status(
        mockserver,
        atol_get_token,
        taxi_cashbox_integration,
        pgsql,
        taxi_config,
        personal_tins_retrieve,
):
    # test doesn't check the right order of database pass
    # test check only that all elements in db was passed
    # and that cursor doesn't loop anywhere

    @mockserver.json_handler('cashbox-cloud-kassir/kkt/receipt/status/get')
    def ck_get_receipt(request):
        return mockserver.make_response(status=500)

    taxi_config.set_values(
        {
            'CASHBOX_INTEGRATION_GET_RECEIPT_STATUS': {
                'enable': True,
                'request_count': 1,
            },
        },
    )

    await taxi_cashbox_integration.run_periodic_task('ReceiptsStatusGetter0')
    await taxi_cashbox_integration.run_periodic_task('ReceiptsStatusGetter0')
    await taxi_cashbox_integration.run_periodic_task('ReceiptsStatusGetter0')
    await taxi_cashbox_integration.run_periodic_task('ReceiptsStatusGetter0')

    check_requests_get_status(
        ck_get_receipt, set(['uuid_4', 'uuid_5', 'uuid_6']),
    )

    # run again to check that after reaching the end of db
    # cursor wil be reseted and will start pass db again
    await taxi_cashbox_integration.run_periodic_task('ReceiptsStatusGetter0')
    await taxi_cashbox_integration.run_periodic_task('ReceiptsStatusGetter0')
    await taxi_cashbox_integration.run_periodic_task('ReceiptsStatusGetter0')
    await taxi_cashbox_integration.run_periodic_task('ReceiptsStatusGetter0')

    check_requests_get_status(
        ck_get_receipt, set(['uuid_4', 'uuid_5', 'uuid_6']),
    )
