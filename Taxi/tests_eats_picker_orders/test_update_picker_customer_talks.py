import pytest

from . import utils


@pytest.mark.parametrize('picker_customer_talks', [None, []])
@utils.update_order_talks_config()
async def test_update_picker_customer_talks_not_completed(
        taxi_eats_picker_orders,
        create_order,
        get_order_talks,
        picker_customer_talks,
):
    eats_id = '123'
    order_id = create_order(
        eats_id=eats_id,
        state='paid',
        picker_customer_talks=picker_customer_talks,
    )

    await taxi_eats_picker_orders.run_distlock_task(
        'update-picker-customer-talks',
    )

    assert get_order_talks(order_id) == []


@pytest.mark.parametrize('state', ['cancelled', 'complete'])
@utils.update_order_talks_config()
async def test_update_picker_customer_talks_completed_with_talks(
        taxi_eats_picker_orders, create_order, get_order_talks, state,
):
    eats_id = '123'
    picker_customer_talks = [('talk_1', 60, None), ('talk_2', 70, 'status')]
    create_order(
        eats_id=eats_id,
        state=state,
        picker_customer_talks=picker_customer_talks,
    )
    order_id = create_order(
        eats_id='456',
        state='paid',
        picker_customer_talks=picker_customer_talks,
    )

    await taxi_eats_picker_orders.run_distlock_task(
        'update-picker-customer-talks',
    )

    assert get_order_talks(order_id) == [
        {
            'order_id': order_id,
            'talk_id': talk[0],
            'length': talk[1],
            'status': talk[2],
        }
        for talk in picker_customer_talks
    ]


@pytest.mark.parametrize('state', ['cancelled', 'complete'])
@pytest.mark.parametrize(
    'order_kwargs', [{'picker_phone_id': None}, {'customer_phone_id': None}],
)
@utils.update_order_talks_config()
async def test_update_picker_customer_talks_completed_missing_phone(
        taxi_eats_picker_orders,
        create_order,
        get_order_talks,
        state,
        order_kwargs,
):
    eats_id = '123'
    create_order(
        eats_id=eats_id,
        state=state,
        picker_customer_talks=None,
        **order_kwargs,
    )

    await taxi_eats_picker_orders.run_distlock_task(
        'update-picker-customer-talks',
    )

    assert get_order_talks(eats_id) == []


@pytest.mark.parametrize('state', ['cancelled', 'complete'])
@pytest.mark.parametrize('order_kwargs', [{'customer_phone_id': '222'}])
@utils.update_order_talks_config()
async def test_update_picker_customer_talks_phones_mismatch(
        taxi_eats_picker_orders,
        mockserver,
        load_json,
        create_order,
        get_order_talks,
        state,
        order_kwargs,
):
    eats_id = '123'
    create_order(
        eats_id=eats_id,
        state=state,
        picker_customer_talks=None,
        picker_phone_id='111',
        **order_kwargs,
    )

    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_forwardings(request):
        assert request.query['external_ref_id'] == eats_id
        return load_json('vgw_api_response.json')

    await taxi_eats_picker_orders.run_distlock_task(
        'update-picker-customer-talks',
    )

    assert mock_forwardings.times_called == 1

    assert get_order_talks(eats_id) == []


@utils.update_order_talks_config()
async def test_update_picker_customer_talks_ok(
        taxi_eats_picker_orders,
        mockserver,
        load_json,
        create_order,
        get_order_talks,
):
    order_talks = {
        'eats_id_1': [
            {'id': '1', 'length': 61, 'status': 'status_1'},
            {'id': '2', 'length': 53, 'status': 'status_2'},
        ],
        'eats_id_2': [
            {'id': '3', 'length': 60, 'status': 'status_3'},
            {'id': '4', 'length': 53, 'status': None},
        ],
        'eats_id_3': [],
    }
    order_id_0 = create_order(
        eats_id='eats_id_1', state='cancelled', customer_phone_id='789',
    )
    order_id_1 = create_order(
        eats_id='eats_id_2', state='complete', customer_phone_id='789',
    )
    order_id_2 = create_order(
        eats_id='eats_id_3', state='complete', customer_phone_id='789',
    )

    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_forwardings(request):
        eats_id = request.query['external_ref_id']
        assert eats_id in order_talks
        response = load_json('vgw_api_response.json')
        talks = response[0]['talks']
        talk_stub = talks[0]
        talks.clear()
        for talk in order_talks[eats_id]:
            talks.append(
                dict(
                    talk_stub,
                    id=talk['id'],
                    length=talk['length'],
                    call_result={'status': talk['status']},
                ),
            )
        return response

    await taxi_eats_picker_orders.run_distlock_task(
        'update-picker-customer-talks',
    )

    assert mock_forwardings.times_called == len(order_talks)
    for talks, order_id in zip(
            order_talks.values(), [order_id_0, order_id_1, order_id_2],
    ):
        assert get_order_talks(order_id) == [
            {
                'order_id': order_id,
                'talk_id': talk['id'],
                'length': talk['length'],
                'status': talk['status'],
            }
            for talk in talks
        ]


@pytest.mark.parametrize('orders_num', [0, 1, 9, 10, 11, 50, 59])
@utils.update_order_talks_config(batch_size=9)
async def test_update_picker_customer_talks_ok_batch(
        taxi_eats_picker_orders,
        mockserver,
        load_json,
        create_order,
        get_order_talks,
        orders_num,
):
    order_talks = [
        {'id': '1', 'length': 61, 'status': 'status_1'},
        {'id': '2', 'length': 53, 'status': 'status_2'},
    ]
    order_ids = []
    for i in range(orders_num):
        order_id = create_order(
            eats_id=f'eats_id_{i}', state='complete', customer_phone_id='789',
        )
        order_ids.append(order_id)

    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def mock_forwardings(request):
        response = load_json('vgw_api_response.json')
        talks = response[0]['talks']
        talk_stub = talks[0]
        talks.clear()
        for talk in order_talks:
            talks.append(
                dict(
                    talk_stub,
                    id=talk['id'],
                    length=talk['length'],
                    call_result={'status': talk['status']},
                ),
            )
        return response

    await taxi_eats_picker_orders.run_distlock_task(
        'update-picker-customer-talks',
    )

    assert mock_forwardings.times_called == orders_num
    for order_id in order_ids:
        assert get_order_talks(order_id) == [
            {
                'order_id': order_id,
                'talk_id': talk['id'],
                'length': talk['length'],
                'status': talk['status'],
            }
            for talk in order_talks
        ]
