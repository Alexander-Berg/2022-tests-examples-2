import collections as col
import datetime as dt

import dateutil as du
import pytest

SKU_YT_PATH = '//edadeal_yt/skus'
QUEUE_NAME = 'eats_nomenclature_edadeal_yt_skus_processing'


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


def expected_skus(has_existing_processed_url=False, needs_subscription=True):
    return {
        1: {
            'uuid': 'f4e3f17d-607c-47a3-9235-3e883b048276',
            'alternate_name': (
                'Печенье Fleur Alpine Яблочный мармелад, с 18-ти месяцев'
            ),
            'composition': (
                'Яблочная паста (концентрированный яблочный сок, '
                'концентрированное яблочное  пюре, агент желирующий (пектин), '
                'регулятор кислотности (лимонная кислота)),  цельнозерновая '
                'пшеничная мука, концентрированный яблочный сок,  '
                'негидрогенизированные растительные масла (подсолнечное, '
                'кокосовое),  спельтовая мука, яйцо, молоко сухое '
                'обезжиренное, рисовая мука, натуральный  экстракт ванили, '
                'минералы морских водорослей (кальций, магний), разрыхлители  '
                '(карбонат аммония, гидрокарбонат натрия), витамин в1, '
                'антиокислитель  (токоферол).'
            ),
            'storage_requirements': (
                'Хранить в сухом месте при температуре не более +25°С, '
                'относительной влажности воздуха не более 75%. '
                'Для детского питания печенье из открытого пакетика '
                'употребить в течение суток. '
            ),
            'weight': '150 г',
            'volume': None,
            'сarbohydrates': '65 г',
            'proteins': '6.5 г',
            'fats': '11.8 г',
            'calories': '388 ккал',
            'country': 'Бельгия',
            'package_type': 'Картонная коробка',
            'expiration_info': '300 д',
            'yt_updated_at': '2019-11-16T14:20:16.653015+00:00',
            'pictures': [
                {
                    'retailer_name': 'miratorg',
                    'url': (
                        'https://avatars.mds.yandex.net/get-edadeal/'
                        + '123123/45645645645645/orig'
                    ),
                    'processed_url': None,
                    'needs_subscription': needs_subscription,
                },
                {
                    'retailer_name': None,
                    'url': (
                        'https://avatars.mds.yandex.net/get-edadeal/'
                        + '2421831/de9f1c29a090887d9b22864ddd51021d/orig'
                    ),
                    'processed_url': None,
                    'needs_subscription': needs_subscription,
                },
            ],
            'barcode_values': ['5412916941165'],
            'product_type_value': 'Печенье детское',
            'product_type_value_uuid': '3df0d4be-644f-5a23-b912-5e6f29fe53c2',
            'product_brand_value': 'Fleur Alpine',
            'product_brand_value_uuid': '40a7405a-84f7-5468-99c5-94d91a2e0100',
            'product_processing_type_value': 'замороженный',
            'product_processing_type_value_uuid': (
                '020222a2-e9a9-41ff-a399-9bf15aea8bd2'
            ),
        },
        2: {
            'uuid': '8e11bc3f-37d2-44ae-8479-ae0d700c4ecd',
            'alternate_name': (
                'Печенье Fleur Alpine с яблочным соком, с 6 месяцев'
            ),
            'composition': (
                'Концентрат яблочного сока (32%), цельнозерновая пшеничная '
                'мука, рисовая мука, негидрогенизированные растительные '
                'масла (подсолнечное, кокосовое), молоко сухое '
                'обезжиренное, разрыхлители (гидрокарбонат аммония, '
                'гидрокарбонат натрия), натуральный экстракт ванили, '
                'витамин в1, антиокислитель (токоферол).'
            ),
            'storage_requirements': 'Хранить в сухом месте ',
            'weight': '150 г',
            'volume': None,
            'сarbohydrates': '66.8 г',
            'proteins': '7.2 г',
            'fats': '8.3 г',
            'calories': '374 ккал',
            'country': 'Бельгия',
            'package_type': 'Картонная коробка',
            'expiration_info': '450 д',
            'yt_updated_at': '2019-11-16T14:20:16.653015+00:00',
            'pictures': [
                {
                    'retailer_name': None,
                    'url': (
                        'https://avatars.mds.yandex.net/get-edadeal/'
                        + '403310/723772bffc977ab631c11e23969fdbed/orig'
                    ),
                    'processed_url': None,
                    'needs_subscription': needs_subscription,
                },
                {
                    'retailer_name': 'bystronom',
                    'url': (
                        'https://avatars.mds.yandex.net/get-edadeal/'
                        + '456456456456/123123123/orig'
                    ),
                    'processed_url': (
                        (
                            'https://avatars.mds.yandex.net/get-edadeal/'
                            + '456456456456/123123123/orig'
                        )
                        if has_existing_processed_url
                        else None
                    ),
                    'needs_subscription': needs_subscription,
                },
            ],
            'barcode_values': ['5412916940854'],
            'product_type_value': 'Печенье детское',
            'product_type_value_uuid': '3df0d4be-644f-5a23-b912-5e6f29fe53c2',
            'product_brand_value': 'Fleur Alpine',
            'product_brand_value_uuid': '40a7405a-84f7-5468-99c5-94d91a2e0100',
            'product_processing_type_value': 'замороженный',
            'product_processing_type_value_uuid': (
                '020222a2-e9a9-41ff-a399-9bf15aea8bd2'
            ),
        },
        3: {
            'alternate_name': 'Майонез Махеевъ оливковый 50.5%',
            'barcode_values': ['4604248002657'],
            'calories': '462 ккал',
            'composition': (
                'Масло подсолнечное рафинированное, вода, масло '
                'оливковое рафинированное, яичный желток, крахмал, соль, '
                'кислота уксусная, консервант сорбат калия, ароматизатор '
                'натуральный Горчица, краситель бета-каротин, подсластитель '
                'Сахарин'
            ),
            'country': None,
            'expiration_info': '180 д',
            'fats': '50 г',
            'package_type': 'Дой-пак',
            'pictures': [
                {
                    'retailer_name': None,
                    'url': (
                        'https://avatars.mds.yandex.net/get-edadeal/'
                        '472110/c94cd229efdccde56ae2c52a39912b31/orig'
                    ),
                    'processed_url': None,
                    'needs_subscription': needs_subscription,
                },
            ],
            'product_brand_value': 'Махеевъ',
            'product_brand_value_uuid': '7116a9b1-5759-531a-a3c5-ec1e9a69c863',
            'product_type_value': 'Майонез',
            'product_type_value_uuid': '1d6b32ec-430f-5980-8146-f66e2a679d7c',
            'product_processing_type_value': 'охлаждённый',
            'product_processing_type_value_uuid': (
                '1a8db2fe-03fd-409d-b7df-39c8b76e01eb'
            ),
            'proteins': '0.5 г',
            'storage_requirements': 'Хранить при температуре от 0°C до +14°C',
            'uuid': 'd5030921-d507-43d9-b234-f316fbcf62be',
            'weight': '770 г',
            'volume': '800 мл',
            'yt_updated_at': '2019-11-13T07:16:07.192982+00:00',
            'сarbohydrates': '1.3 г',
        },
    }


@pytest.mark.pgsql('eats_nomenclature', files=['fill_migration_33.sql'])
@pytest.mark.yt(
    schemas=['yt_sku_schema.yaml'], static_table_data=['yt_sku_data.yaml'],
)
async def test_merge_on_empty(pgsql, task_enqueue_v2, yt_apply):
    await task_enqueue_v2(QUEUE_NAME, kwargs={'skus_yt_path': SKU_YT_PATH})

    new_skus = sql_get_skus(pgsql)

    assert set(new_skus.keys()) == set(expected_skus().keys())
    assert sort_by_name(new_skus.values()) == sort_by_name(
        expected_skus().values(),
    )


@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_migration_33.sql', 'fill_sku_same.sql'],
)
@pytest.mark.yt(
    schemas=['yt_sku_schema.yaml'], static_table_data=['yt_sku_data.yaml'],
)
async def test_merge_on_same_data(pgsql, task_enqueue_v2, yt_apply):
    old_skus = sql_get_skus(pgsql)
    old_attributes = sql_get_sku_attributes(pgsql)
    old_pictures = sql_get_sku_pictures_raw(pgsql)
    old_barcodes = sql_get_sku_barcodes_raw(pgsql)

    await task_enqueue_v2(QUEUE_NAME, kwargs={'skus_yt_path': SKU_YT_PATH})

    new_skus = sql_get_skus(pgsql)
    new_attributes = sql_get_sku_attributes(pgsql)
    new_pictures = sql_get_sku_pictures_raw(pgsql)
    new_barcodes = sql_get_sku_barcodes_raw(pgsql)

    assert new_skus == expected_skus(
        has_existing_processed_url=True, needs_subscription=False,
    )
    assert new_skus == old_skus
    assert sort_by_sku_id(new_attributes) == sort_by_sku_id(old_attributes)
    assert sort_by_sku_id(new_pictures) == sort_by_sku_id(old_pictures)
    assert sort_by_sku_id(new_barcodes) == sort_by_sku_id(old_barcodes)


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_migration_33.sql', 'fill_sku_different.sql'],
)
@pytest.mark.yt(
    schemas=['yt_sku_schema.yaml'], static_table_data=['yt_sku_data.yaml'],
)
async def test_merge_on_different_sku_data(pgsql, task_enqueue_v2, yt_apply):
    old_skus = sql_get_skus(pgsql)

    await task_enqueue_v2(QUEUE_NAME, kwargs={'skus_yt_path': SKU_YT_PATH})

    new_skus = sql_get_skus(pgsql)

    assert new_skus == expected_skus()
    assert set(new_skus.keys()) == set(old_skus.keys())


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_migration_33.sql', 'fill_sku_different_same_date.sql'],
)
@pytest.mark.yt(
    schemas=['yt_sku_schema.yaml'], static_table_data=['yt_sku_data.yaml'],
)
async def test_merge_on_different_w_same_date(
        pgsql, task_enqueue_v2, yt_apply,
):
    def filter_sku(data):
        return [
            {'sku_id': i['sku_id'], 'updated_at': i['updated_at']}
            for i in data
        ]

    old_skus = sql_get_skus_raw(pgsql)

    await task_enqueue_v2(QUEUE_NAME, kwargs={'skus_yt_path': SKU_YT_PATH})

    new_skus = sql_get_skus_raw(pgsql)

    assert sort_by_sku_id(filter_sku(old_skus)) == sort_by_sku_id(
        filter_sku(new_skus),
    )


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_migration_33.sql', 'fill_sku_different_same_date.sql'],
)
@pytest.mark.yt(
    schemas=['yt_sku_schema.yaml'], static_table_data=['yt_sku_data.yaml'],
)
async def test_merge_on_different_w_same_date_forced(
        pgsql, task_enqueue_v2, yt_apply,
):

    old_skus = sql_get_skus_raw(pgsql)

    await task_enqueue_v2(
        QUEUE_NAME, kwargs={'skus_yt_path': SKU_YT_PATH, 'force_update': True},
    )

    new_skus = sql_get_skus_raw(pgsql)
    for i in zip(sort_by_sku_id(new_skus), sort_by_sku_id(old_skus)):
        assert i[0]['sku_id'] == i[1]['sku_id']
        assert dt.datetime.fromisoformat(
            i[0]['updated_at'],
        ) > dt.datetime.fromisoformat(i[1]['updated_at'])


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_migration_33.sql', 'fill_sku_different.sql'],
)
@pytest.mark.yt(
    schemas=['yt_sku_schema.yaml'], static_table_data=['yt_sku_data.yaml'],
)
async def test_stq_success(task_enqueue_v2, taxi_config, pgsql, yt_apply):

    await task_enqueue_v2(QUEUE_NAME, kwargs={'skus_yt_path': SKU_YT_PATH})

    assert sql_get_last_skus_path(pgsql) == SKU_YT_PATH


@pytest.mark.config(
    EATS_NOMENCLATURE_PROCESSING=settings(max_retries_on_error=2),
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_migration_33.sql'])
async def test_stq_error_limit(task_enqueue_v2, taxi_config, pgsql, yt_apply):

    max_retries_on_error = taxi_config.get('EATS_NOMENCLATURE_PROCESSING')[
        '__default__'
    ]['max_retries_on_error']
    unknown_yt_path = '//unknown'

    for i in range(max_retries_on_error):
        await task_enqueue_v2(
            QUEUE_NAME,
            kwargs={'skus_yt_path': unknown_yt_path},
            expect_fail=True,
            exec_tries=i,
        )
        assert sql_get_last_skus_path(pgsql) != unknown_yt_path

    # should succeed because of the error limit
    await task_enqueue_v2(
        QUEUE_NAME,
        kwargs={'skus_yt_path': unknown_yt_path},
        expect_fail=False,
        exec_tries=max_retries_on_error,
    )
    assert sql_get_last_skus_path(pgsql) != unknown_yt_path


@pytest.mark.config(
    EATS_NOMENCLATURE_PROCESSING=settings(
        max_retries_on_busy=2, max_busy_time_in_ms=100000,
    ),
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_migration_33.sql'])
@pytest.mark.yt(
    schemas=['yt_sku_schema.yaml'], static_table_data=['yt_sku_data.yaml'],
)
async def test_stq_busy_limit(
        mockserver, task_enqueue_v2, pgsql, taxi_config, yt_apply,
):

    config = taxi_config.get('EATS_NOMENCLATURE_PROCESSING')['__default__']
    max_retries_on_busy = config['max_retries_on_busy']
    max_busy_time_in_ms = config['max_busy_time_in_ms']
    retry_on_busy_delay_ms = config['retry_on_busy_delay_ms']

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    async def mock_stq_reschedule(request):
        data = request.json
        assert data['queue_name'] == QUEUE_NAME
        assert data['task_id'] == SKU_YT_PATH[:20]

        eta = du.parser.parse(data['eta']).replace(tzinfo=None)
        assert (
            eta - dt.datetime.now()
        ).total_seconds() < retry_on_busy_delay_ms

        return {}

    sql_set_skus_busy(pgsql)

    assert mock_stq_reschedule.times_called == 0

    for i in range(max_retries_on_busy):
        await task_enqueue_v2(
            QUEUE_NAME,
            kwargs={'skus_yt_path': SKU_YT_PATH},
            reschedule_counter=i,
        )
        assert mock_stq_reschedule.times_called == i + 1
        assert sql_is_skus_busy(pgsql)
        assert sql_get_last_skus_path(pgsql) != SKU_YT_PATH

    # Exceed max busy retries
    await task_enqueue_v2(
        QUEUE_NAME,
        kwargs={'skus_yt_path': SKU_YT_PATH},
        reschedule_counter=max_retries_on_busy,
    )
    assert mock_stq_reschedule.times_called == max_retries_on_busy
    assert sql_is_skus_busy(pgsql)
    assert sql_get_last_skus_path(pgsql) != SKU_YT_PATH

    # Expire the busy status
    sql_set_skus_busy(pgsql, 3 * max_busy_time_in_ms)
    await task_enqueue_v2(
        QUEUE_NAME, kwargs={'skus_yt_path': SKU_YT_PATH}, reschedule_counter=0,
    )
    assert mock_stq_reschedule.times_called == max_retries_on_busy
    assert not sql_is_skus_busy(pgsql)
    assert sql_get_last_skus_path(pgsql) == SKU_YT_PATH


def sql_get_sku_pictures_raw(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select sku_id, picture_id, retailer_name
        from eats_nomenclature.sku_pictures
        """,
    )
    return [
        {'sku_id': i[0], 'picture_id': i[1], 'retailer_name': i[2]}
        for i in list(cursor)
    ]


def sql_get_sku_pictures(pgsql):
    sku_pictures = sql_get_sku_pictures_raw(pgsql)
    picture_ids = [str(i['picture_id']) for i in sku_pictures]

    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select id, url, processed_url, needs_subscription
        from eats_nomenclature.pictures
        where id = any(array[{','.join(picture_ids)}])
        """,
    )
    id_to_data = {
        p[0]: {'url': p[1], 'processed_url': p[2], 'needs_subscription': p[3]}
        for p in list(cursor)
    }

    return [
        {
            'sku_id': i['sku_id'],
            'url': id_to_data[i['picture_id']]['url'],
            'processed_url': id_to_data[i['picture_id']]['processed_url'],
            'needs_subscription': id_to_data[i['picture_id']][
                'needs_subscription'
            ],
            'retailer_name': i['retailer_name'],
        }
        for i in sku_pictures
    ]


def sql_get_sku_attributes(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select
          sa.sku_id,
          pn.value,
          pn.value_uuid,
          pb.value,
          pb.value_uuid,
          ppt.value,
          ppt.value_uuid
        from eats_nomenclature.sku_attributes sa
          left outer join eats_nomenclature.product_types pn
            on pn.id = sa.product_type_id
          left outer join eats_nomenclature.product_brands pb
            on pb.id = sa.product_brand_id
          left outer join eats_nomenclature.product_processing_types ppt
            on ppt.id = sa.product_processing_type_id
        """,
    )
    return [
        {
            'sku_id': i[0],
            'product_type_value': i[1],
            'product_type_value_uuid': i[2],
            'product_brand_value': i[3],
            'product_brand_value_uuid': i[4],
            'product_processing_type_value': i[5],
            'product_processing_type_value_uuid': i[6],
        }
        for i in list(cursor)
    ]


def sql_get_sku_barcodes_raw(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select sku_id, barcode_id
        from eats_nomenclature.sku_barcodes
        """,
    )
    return [{'sku_id': i[0], 'barcode_id': i[1]} for i in list(cursor)]


def sql_get_sku_barcodes(pgsql):
    sku_barcodes = sql_get_sku_barcodes_raw(pgsql)
    barcode_ids = [str(i['barcode_id']) for i in sku_barcodes]

    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select id, value
        from eats_nomenclature.barcodes
        where id = any(array[{','.join(barcode_ids)}])
        """,
    )
    id_to_value = dict(cursor)

    return [
        {'sku_id': i['sku_id'], 'barcode_value': id_to_value[i['barcode_id']]}
        for i in sku_barcodes
    ]


def sql_get_skus_raw(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select
          id,
          uuid,
          alternate_name,
          composition,
          storage_requirements,
          weight,
          volume,
          сarbohydrates,
          proteins,
          fats,
          calories,
          country,
          package_type,
          expiration_info,
          yt_updated_at,
          updated_at
        from eats_nomenclature.sku
        """,
    )

    return [
        {
            'sku_id': i[0],
            'uuid': i[1],
            'alternate_name': i[2],
            'composition': i[3],
            'storage_requirements': i[4],
            'weight': i[5],
            'volume': i[6],
            'сarbohydrates': i[7],
            'proteins': i[8],
            'fats': i[9],
            'calories': i[10],
            'country': i[11],
            'package_type': i[12],
            'expiration_info': i[13],
            'yt_updated_at': (
                i[14]
                .replace(tzinfo=du.tz.tzlocal())
                .astimezone(du.tz.tzutc())
                .isoformat()
            ),
            'updated_at': (
                i[15]
                .replace(tzinfo=du.tz.tzlocal())
                .astimezone(du.tz.tzutc())
                .isoformat()
            ),
        }
        for i in list(cursor)
    ]


def sql_get_skus(pgsql):
    sku_pictures = sorted(sql_get_sku_pictures(pgsql), key=lambda k: k['url'])
    sku_barcodes = sorted(
        sql_get_sku_barcodes(pgsql), key=lambda k: k['barcode_value'],
    )
    sku_attributes = sql_get_sku_attributes(pgsql)
    sku_data = sql_get_skus_raw(pgsql)

    def sku_dict():
        return {'pictures': [], 'barcode_values': []}

    def remove_sku_id(data):
        data.pop('sku_id')
        return data

    skus = col.defaultdict(sku_dict)
    for i in sku_pictures:
        sku_id = i['sku_id']
        skus[sku_id]['pictures'].append(remove_sku_id(i))
    for i in sku_barcodes:
        sku_id = i['sku_id']
        skus[sku_id]['barcode_values'].append(i['barcode_value'])
    for i in sku_attributes:
        sku_id = i['sku_id']
        cur_sku = skus[sku_id]
        skus[sku_id] = {**cur_sku, **remove_sku_id(i)}
    for i in sku_data:
        sku_id = i['sku_id']
        i.pop('updated_at')
        cur_sku = skus[sku_id]
        skus[sku_id] = {**cur_sku, **remove_sku_id(i)}
    return dict(skus)


def sort_by_name(data):
    return sorted(data, key=lambda k: k['alternate_name'])


def sort_by_sku_id(data):
    return sorted(data, key=lambda k: k['sku_id'])


def sql_set_skus_busy(pgsql, time_difference_in_ms=0):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        update eats_nomenclature.sku_yt_update_statuses
        set
          update_started_at =
            now() - interval '{int(time_difference_in_ms/1000)} second',
          is_in_progress = true;
        """,
    )


def sql_is_skus_busy(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select is_in_progress
        from eats_nomenclature.sku_yt_update_statuses
        """,
    )
    return list(cursor)[0][0]


def sql_get_last_skus_path(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select last_sku_path
        from eats_nomenclature.sku_yt_update_statuses
        """,
    )
    return list(cursor)[0][0]
