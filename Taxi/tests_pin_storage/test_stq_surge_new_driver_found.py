import pytest

TIME_NOW = '2019-03-08T00:00:00Z'
TIMESTAMP_NOW = '1552003200'


@pytest.mark.parametrize(
    'offer_id,application,point_b,tariff_zone',
    (('some0ffer', 'iphone', [40.2, 55.8], 'moscow'), ('', '', None, None)),
)
@pytest.mark.now(TIME_NOW)
@pytest.mark.config(PIN_STORAGE_CREATE_PIN_REQUESTS=True)
async def test_pin_insert(
        stq_runner,
        taxi_pin_storage,
        mockserver,
        offer_id,
        application,
        point_b,
        tariff_zone,
        testpoint,
):
    surger_requests = []

    @mockserver.json_handler('/surger/create_pin')
    def _create_pin(request):
        surger_requests.append(request.json)
        return {'created': TIME_NOW}

    @testpoint('surger_create_pin')
    def surger_create_pin(data):
        pass

    await taxi_pin_storage.enable_testpoints()

    stq_params = {
        'order_id': 'usual_hexadecimal_mess',
        'offer_id': offer_id,
        'tariff_class': 'uberkids',
        'clid_uuid': 'clid_uuid',
        'personal_phone_id': '123456789012345678901234',
        'user_id': 'pro_customer',
        'point_a': [30.1, 55.2],
        'application': application,
    }
    if point_b is not None:
        stq_params['point_b'] = point_b
    if tariff_zone is not None:
        stq_params['tariff_zone'] = tariff_zone
    await stq_runner.surge_new_driver_found.call(
        task_id='task_id', kwargs=stq_params,
    )

    expected = {
        'driver_id': 'clid_uuid',
        'estimated_waiting': {},
        'order_id': 'usual_hexadecimal_mess',
        'personal_phone_id': '123456789012345678901234',
        'point': [30.1, 55.2],
        'user_id': 'pro_customer',
        'save_to_storage': False,
        'trip_info': {'cost_info': []},
        'selected_class': 'uberkids',
        'offer_id': offer_id,
    }

    if application:
        expected['client'] = {'name': application, 'version': [0, 0, 0]}

    if point_b:
        expected['trip_info']['point'] = point_b

    if tariff_zone:
        expected['tariff_zone'] = tariff_zone

    await surger_create_pin.wait_call()
    assert len(surger_requests) == 1
    assert surger_requests[0] == expected
