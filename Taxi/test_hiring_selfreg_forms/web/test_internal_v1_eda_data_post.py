from test_hiring_selfreg_forms import conftest


@conftest.main_configuration
async def test_internal_v1_eda_data_post(taxi_hiring_selfreg_forms_web):
    request_data = dict(
        form_completion_id='fb4d3282bfbd4893b68ef7e7267ba33e',
        phone_id='aaaaaaaabbbb4cccddddeeeeeeeeeeee',
        citizenship='RU',
        external_id='61fdabf83a0940d0b199768689b3ae31',
        name='name',
        region='region',
        service='service',
        vacancy='vacancy',
        vehicle_type='vehicle_type',
    )
    response = await taxi_hiring_selfreg_forms_web.post(
        '/internal/v1/eda/data', json=request_data,
    )
    assert response.status == 200
    assert await response.json() == {'code': 'ok', 'message': ''}

    response = await taxi_hiring_selfreg_forms_web.get(
        '/v1/eda/form/data',
        params={'form_completion_id': 'fb4d3282bfbd4893b68ef7e7267ba33e'},
    )
    assert response.status == 200
    response_json = await response.json()

    assert response_json['external_id'] == '61fdabf83a0940d0b199768689b3ae31'
    assert (
        response_json['form_completion_id']
        == 'fb4d3282bfbd4893b68ef7e7267ba33e'
    )
    assert response_json['is_finished']
    assert sorted(response_json['data'], key=lambda x: x['id']) == sorted(
        [
            {'id': 'name', 'value': 'name'},
            {'id': 'city', 'value': 'region'},
            {'id': 'service', 'value': 'service'},
            {'id': 'vacancy', 'value': 'vacancy'},
            {'id': 'phone', 'value': '+79210000000'},
            {'id': 'citizenship', 'value': 'RU'},
            {'id': 'external_id', 'value': '61fdabf83a0940d0b199768689b3ae31'},
            {'id': 'courier_transport_type', 'value': 'vehicle_type'},
            {
                'id': 'form_completion_id',
                'value': 'fb4d3282bfbd4893b68ef7e7267ba33e',
            },
        ],
        key=lambda x: x['id'],
    )

    # idempotency
    response = await taxi_hiring_selfreg_forms_web.post(
        '/internal/v1/eda/data', json=request_data,
    )
    assert response.status == 200
    assert await response.json() == {'code': 'ok', 'message': ''}
