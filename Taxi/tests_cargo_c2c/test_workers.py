import pytest


@pytest.mark.config(
    CARGO_C2C_FLUSH_POSTCARDS_SETTINGS={
        'enabled': True,
        'pg-timeouts': {'execute_ms': 250, 'statement_ms': 250},
    },
)
async def test_flush_postcards_worker_not_outdated(
        taxi_cargo_c2c, testpoint, default_pa_headers, run_flush_postcards,
):

    headers = default_pa_headers('phone_pd_id_1').copy()
    headers['X-Idempotency-Token'] = '123'

    await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/postcard/generate-upload-link',
        json={'content_type': 'image/jpeg'},
        headers=headers,
    )

    stats = await run_flush_postcards()
    assert stats == {'postcards-to-remove': 0, 'postcards-removed': 0}


@pytest.mark.config(
    CARGO_C2C_FLUSH_POSTCARDS_SETTINGS={
        'enabled': True,
        'pg-timeouts': {'execute_ms': 250, 'statement_ms': 250},
    },
)
async def test_flush_postcards_worker_outdated(
        taxi_cargo_c2c,
        testpoint,
        default_pa_headers,
        pgsql,
        create_cargo_c2c_orders,
        get_default_draft_request,
        run_flush_postcards,
        stq_runner,
):
    headers = default_pa_headers('phone_pd_id_1').copy()
    headers['X-Idempotency-Token'] = '123'

    await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/postcard/generate-upload-link',
        json={'content_type': 'image/jpeg'},
        headers=headers,
    )

    # create another postcard but assign it to a draft
    order_id = await create_cargo_c2c_orders(add_postcard=True)

    await stq_runner.cargo_c2c_postcard_download_url.call(
        task_id='1', args=[order_id, 'phone_pd_id_3'],
    )

    cursor = pgsql['cargo_c2c'].cursor()
    query = (
        'UPDATE cargo_c2c.postcards SET created_ts = '
        'created_ts - interval \'2 hours\''
    )
    cursor.execute(query)

    stats = await run_flush_postcards()
    assert stats == {'postcards-to-remove': 1, 'postcards-removed': 1}

    cursor = pgsql['cargo_c2c'].cursor()
    query = 'select removed_from_s3 from cargo_c2c.postcards'
    cursor.execute(query)
    rows = list(cursor)
    assert rows == [(False,), (True,)]


@pytest.mark.config(
    CARGO_C2C_UPDATE_DELIVERY_RESOLUTION_SETTINGS={
        'enabled': True,
        'period_ms': 120,
        'params_by_provider': {
            'cargo-claims': {'termination_period_seconds': 1, 'limit': 10},
        },
    },
)
@pytest.mark.experiments3(filename='experiment.json')
async def test_update_resolution(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        run_update_delivery_resolution,
        pgsql,
):
    cursor = pgsql['cargo_c2c'].cursor()
    query = (
        'UPDATE cargo_c2c.clients_orders SET created_ts = '
        'created_ts - interval \'2 hours\''
    )
    cursor.execute(query)

    stats = await run_update_delivery_resolution()
    assert stats == {'cargo-claims': 3}
