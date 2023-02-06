import datetime as dt
import json

import dateutil as du
import pytest

QUEUE_NAME = 'eats_nomenclature_edadeal_s3_uploader'
BRAND_PROCESSING_QUEUE = 'eats_nomenclature_brand_processing'
EDADEAL_REACTOR_HANDLER = '/nirvana-reactor-production/api/v1/a/i/instantiate'


def settings(
        max_retries_on_error=3,
        max_retries_on_busy=3,
        max_busy_time_in_ms=100000,
        retry_on_busy_delay_ms=1000,
):
    return {
        '__default__': {
            'max_retries_on_error': max_retries_on_error,
            'max_retries_on_busy': max_retries_on_busy,
            'max_busy_time_in_ms': max_busy_time_in_ms,
            'retry_on_busy_delay_ms': retry_on_busy_delay_ms,
            'insert_batch_size': 1000,
            'lookup_batch_size': 1000,
        },
    }


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'add_brand_for_edadeal.sql',
    ],
)
async def test_stq_trigger(
        task_enqueue_v2,
        stq,
        stq_call_forward,
        mocked_time,
        mds_s3_storage,
        load_json,
        activate_assortment,
        sql_upsert_place,
):
    brand_id = 777
    current_time = dt.datetime.utcnow()

    # Need to freeze time, because it's used in
    # handler when generating upload path
    mocked_time.set(current_time)

    sql_upsert_place(place_id=1, place_slug='lavka_krasina')

    await task_enqueue_v2(BRAND_PROCESSING_QUEUE, task_id='1')

    place_id = 1
    new_availabilities = [
        {'origin_id': 'item_origin_4', 'available': True},
        {'origin_id': 'item_origin_5', 'available': True},
        {'origin_id': 'item_origin_6', 'available': True},
    ]
    new_stocks = [
        {'origin_id': 'item_origin_4', 'stocks': None},
        {'origin_id': 'item_origin_5', 'stocks': None},
        {'origin_id': 'item_origin_6', 'stocks': None},
    ]
    new_prices = [
        {'origin_id': 'item_origin_4', 'price': '1000', 'currency': 'RUB'},
        {'origin_id': 'item_origin_5', 'price': '1000', 'currency': 'RUB'},
        {'origin_id': 'item_origin_6', 'price': '1000', 'currency': 'RUB'},
    ]
    await activate_assortment(
        new_availabilities, new_stocks, new_prices, place_id, '1',
    )

    stq_next_call = (
        stq.eats_nomenclature_assortment_activation_notifier.next_call()
    )
    assert stq_next_call['kwargs']['brand_id'] == brand_id
    await stq_call_forward(stq_next_call)

    stq_next_call = stq.eats_nomenclature_edadeal_s3_uploader.next_call()
    assert stq_next_call['id'] == str(brand_id)
    assert stq_next_call['kwargs']['upload_task_id'] == str(brand_id)
    assert stq_next_call['kwargs']['brand_id'] == brand_id

    await stq_call_forward(stq_next_call)

    place_slug = 'lavka_krasina'
    retailer_name = place_slug.split('_')[0]
    date = current_time.strftime('%Y-%m-%dT%H:%M')
    upload_path = f'{retailer_name}/{date}/products.json'

    dumped_data = mds_s3_storage.get_object(upload_path).data
    assert dumped_data

    result_data = json.loads(dumped_data)
    for item in result_data['items']:
        del item['item_key']
    expected_result = sorted_by_name(load_json('uploaded_data.json'))
    # processed url is not inserted for new pics
    expected_result['items'][2]['images'] = []
    assert sorted_by_name(result_data) == expected_result


@pytest.mark.parametrize(
    'fill_brands_for_edadeal, brand_id_for_edadeal',
    [(True, 777), (True, 888), (False, None)],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_edadeal_stq_should_not_be_called(
        pgsql,
        task_enqueue_v2,
        stq,
        stq_call_forward,
        mocked_time,
        activate_assortment,
        sql_upsert_place,
        # parametrize
        fill_brands_for_edadeal,
        brand_id_for_edadeal,
):
    brand_id = 777

    if fill_brands_for_edadeal:
        sql_add_brand_for_edadeal(
            pgsql, brand_id_for_edadeal, brand_id != brand_id_for_edadeal,
        )
    current_time = dt.datetime.utcnow()

    # Need to freeze time, because it's used in
    # handler when generating upload path
    mocked_time.set(current_time)

    sql_upsert_place(place_id=1, place_slug='lavka_krasina')

    await task_enqueue_v2(BRAND_PROCESSING_QUEUE, task_id='1')

    place_id = 1
    new_availabilities = [
        {'origin_id': 'item_origin_4', 'available': True},
        {'origin_id': 'item_origin_5', 'available': True},
        {'origin_id': 'item_origin_6', 'available': True},
    ]
    new_stocks = [
        {'origin_id': 'item_origin_4', 'stocks': None},
        {'origin_id': 'item_origin_5', 'stocks': None},
        {'origin_id': 'item_origin_6', 'stocks': None},
    ]
    new_prices = [
        {'origin_id': 'item_origin_4', 'price': '1000', 'currency': 'RUB'},
        {'origin_id': 'item_origin_5', 'price': '1000', 'currency': 'RUB'},
        {'origin_id': 'item_origin_6', 'price': '1000', 'currency': 'RUB'},
    ]
    await activate_assortment(
        new_availabilities, new_stocks, new_prices, place_id, '1',
    )

    stq_next_call = (
        stq.eats_nomenclature_assortment_activation_notifier.next_call()
    )
    assert stq_next_call['kwargs']['brand_id'] == brand_id
    await stq_call_forward(stq_next_call)

    assert stq.eats_nomenclature_edadeal_s3_uploader.has_calls == (
        fill_brands_for_edadeal and brand_id_for_edadeal == brand_id
    )


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_stq_trigger_with_disabled_brand(task_enqueue_v2, stq):
    await task_enqueue_v2(BRAND_PROCESSING_QUEUE, task_id='1')
    assert stq.eats_nomenclature_edadeal_s3_uploader.has_calls is False


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'add_brand_for_edadeal.sql',
    ],
)
async def test_edadeal_reactor_trigger(
        task_enqueue_v2,
        stq,
        stq_call_forward,
        stq_runner,
        mockserver,
        testsuite_build_dir,
        load_yaml,
        activate_assortment,
        sql_upsert_place,
):
    sql_upsert_place(place_id=1, place_slug='lavka_krasina')

    place_slug = 'lavka_krasina'
    retailer_name = place_slug.split('_')[0]
    date = dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M')
    upload_path = f'{retailer_name}/{date}/products.json'

    @mockserver.json_handler(EDADEAL_REACTOR_HANDLER)
    def _mock_reactor(request):
        config_path = testsuite_build_dir.joinpath('configs/service.yaml')
        config = load_yaml(config_path)
        config_vars = load_yaml(config['config_vars'])
        artifact_id_var_name = config['components_manager']['components'][
            'nmn-service-settings'
        ]['reactor_edadeal_notify_artifact_id']
        artifact_id = config_vars[artifact_id_var_name[1:]]

        data = request.json
        data.pop('userTimestamp')
        metadata_value = json.loads(data['metadata'].pop('value'))
        metadata_value.pop('timestamp')

        expected_data = {
            'artifactIdentifier': {'artifactId': artifact_id},
            'metadata': {
                '@type': '/yandex.reactor.artifact.StringArtifactValueProto',
            },
            'createIfNotExist': True,
        }
        expected_metadata_value = {
            'feed_name': retailer_name,
            'source_name': '',
            'source_type': 'eda.nomenclature',
            'source_id': 0,
            'source_path': upload_path,
            'options': {},
            'retailer_id': 0,
            'source_md5': '',
        }
        assert data == expected_data
        assert metadata_value == expected_metadata_value
        return mockserver.make_response(
            json.dumps(
                {
                    'artifactInstanceId': 'dummy_instance_id',
                    'creationTimestamp': 'dummy_timestamp',
                },
            ),
            200,
        )

    await task_enqueue_v2(BRAND_PROCESSING_QUEUE, task_id='1')

    place_id = 1
    new_availabilities = [
        {'origin_id': 'item_origin_4', 'available': True},
        {'origin_id': 'item_origin_5', 'available': True},
        {'origin_id': 'item_origin_6', 'available': True},
    ]
    new_stocks = [
        {'origin_id': 'item_origin_4', 'stocks': None},
        {'origin_id': 'item_origin_5', 'stocks': None},
        {'origin_id': 'item_origin_6', 'stocks': None},
    ]
    new_prices = [
        {'origin_id': 'item_origin_4', 'price': '1000', 'currency': 'RUB'},
        {'origin_id': 'item_origin_5', 'price': '1000', 'currency': 'RUB'},
        {'origin_id': 'item_origin_6', 'price': '1000', 'currency': 'RUB'},
    ]
    await activate_assortment(
        new_availabilities, new_stocks, new_prices, place_id, '1',
    )

    stq_next_call = (
        stq.eats_nomenclature_assortment_activation_notifier.next_call()
    )
    await stq_call_forward(stq_next_call)

    stq_next_call = stq.eats_nomenclature_edadeal_s3_uploader.next_call()
    await stq_call_forward(stq_next_call)


@pytest.mark.config(
    EATS_NOMENCLATURE_PROCESSING=settings(max_retries_on_error=2),
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'add_brand_for_edadeal.sql',
    ],
)
async def test_stq_error_limit(task_enqueue_v2, pgsql, taxi_config):

    max_retries_on_error = taxi_config.get('EATS_NOMENCLATURE_PROCESSING')[
        '__default__'
    ]['max_retries_on_error']
    unknown_brand_id = 99999

    for i in range(max_retries_on_error):
        await task_enqueue_v2(
            QUEUE_NAME,
            kwargs={'brand_id': unknown_brand_id},
            expect_fail=True,
            exec_tries=i,
        )

    # should succeed because of the error limit
    await task_enqueue_v2(
        QUEUE_NAME,
        kwargs={'brand_id': unknown_brand_id},
        expect_fail=False,
        exec_tries=max_retries_on_error,
    )


@pytest.mark.config(
    EATS_NOMENCLATURE_PROCESSING=settings(
        max_retries_on_busy=2, max_busy_time_in_ms=100000,
    ),
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'add_brand_for_edadeal.sql',
    ],
)
async def test_stq_busy_limit(mockserver, task_enqueue_v2, pgsql, taxi_config):
    brand_id = 777

    config = taxi_config.get('EATS_NOMENCLATURE_PROCESSING')['__default__']
    max_retries_on_busy = config['max_retries_on_busy']
    max_busy_time_in_ms = config['max_busy_time_in_ms']
    retry_on_busy_delay_ms = config['retry_on_busy_delay_ms']

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def mock_stq_reschedule(request):
        data = request.json
        assert data['queue_name'] == QUEUE_NAME
        assert data['task_id'] == str(brand_id)

        eta = du.parser.parse(data['eta']).replace(tzinfo=None)
        assert (
            eta - dt.datetime.now()
        ).total_seconds() < retry_on_busy_delay_ms

        return {}

    # initialize data for brand
    await task_enqueue_v2(BRAND_PROCESSING_QUEUE, task_id='1')

    sql_set_brand_busy(pgsql, brand_id)

    assert mock_stq_reschedule.times_called == 0

    for i in range(max_retries_on_busy):
        await task_enqueue_v2(QUEUE_NAME, reschedule_counter=i)
        assert mock_stq_reschedule.times_called == i + 1
        assert sql_is_brand_busy(pgsql, brand_id)

    # Exceed max busy retries
    await task_enqueue_v2(QUEUE_NAME, reschedule_counter=max_retries_on_busy)
    assert mock_stq_reschedule.times_called == max_retries_on_busy
    assert sql_is_brand_busy(pgsql, brand_id)

    # Expire the busy status
    sql_set_brand_busy(pgsql, brand_id, 3 * max_busy_time_in_ms)
    await task_enqueue_v2(QUEUE_NAME, reschedule_counter=0)
    assert mock_stq_reschedule.times_called == max_retries_on_busy
    assert not sql_is_brand_busy(pgsql, brand_id)


def sorted_by_name(data):
    data['items'] = sorted(data['items'], key=lambda item: item['name'])
    return data


def sql_set_brand_busy(pgsql, brand_id, time_difference_in_ms=0):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature.brand_update_statuses
            (
                brand_id,
                edadeal_s3_export_started_at,
                edadeal_s3_export_in_progress
            )
            values (
                {brand_id},
                now() - interval '{int(time_difference_in_ms/1000)} second',
                true
            )
        on conflict (brand_id) do update
        set
          edadeal_s3_export_started_at =
            excluded.edadeal_s3_export_started_at,
          edadeal_s3_export_in_progress =
            excluded.edadeal_s3_export_in_progress
        where eats_nomenclature.brand_update_statuses.brand_id = {brand_id}
        """,
    )


def sql_is_brand_busy(pgsql, brand_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select edadeal_s3_export_in_progress
        from eats_nomenclature.brand_update_statuses
        where brand_id = {brand_id}
        """,
    )
    return list(cursor)[0][0]


def sql_add_brand_for_edadeal(pgsql, brand_id, should_insert_to_brands=True):
    cursor = pgsql['eats_nomenclature'].cursor()
    if should_insert_to_brands:
        cursor.execute(
            f"""
            insert into eats_nomenclature.brands (id)
            values ({brand_id});
            """,
        )
    cursor.execute(
        f"""
        insert into eats_nomenclature.brands_for_edadeal (brand_id)
        values ({brand_id});
        """,
    )
